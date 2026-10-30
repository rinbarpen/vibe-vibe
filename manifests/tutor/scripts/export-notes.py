#!/usr/bin/env python3
"""Export one selected Markdown note to an offline, illustrated PDF.

Requires local pandoc and Chrome/Chromium. No packages are downloaded. Input
Markdown and image files are never rewritten; PDFs are published atomically.
"""

from __future__ import annotations

import argparse
import base64
import html
from html.parser import HTMLParser
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


class ExportError(Exception):
    """A useful, user-facing export failure."""


TIMEOUT = 90
FONT_STACK = '"Noto Sans CJK SC", "Noto Sans CJK JP", "Microsoft YaHei", "PingFang SC", sans-serif'
PRINT_CSS = """
@page { size: A4; margin: 18mm 16mm 20mm; }
html { font-size: 10.5pt; }
body { max-width: none; margin: 0; color: #202834; line-height: 1.7; FONT_DECL }
h1, h2, h3, h4 { line-height: 1.35; break-after: avoid-page; color: #17324d; }
h1 { font-size: 23pt; } h2 { font-size: 17pt; border-bottom: 1px solid #d5e1eb; padding-bottom: .2em; }
p, li { orphans: 3; widows: 3; overflow-wrap: anywhere; }
a { color: #215e87; text-decoration: underline; overflow-wrap: anywhere; }
figure, .svg-figure { display: block; margin: 1.1em 0; break-inside: avoid; text-align: center; }
img, svg { max-width: 100%; max-height: 235mm; height: auto; object-fit: contain; }
svg text, svg tspan { FONT_DECL }
figcaption, .caption { font-size: 9pt; color: #526375; text-align: center; }
pre, code { font-family: "Noto Sans Mono CJK SC", "DejaVu Sans Mono", monospace; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; overflow: visible; padding: .7em; background: #f3f6f9; border: 1px solid #dae3eb; }
pre code { white-space: inherit; }
table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
th, td { border: 1px solid #cbd7e2; padding: .4em .55em; overflow-wrap: anywhere; }
thead { display: table-header-group; background: #eaf0f6; }
tr { break-inside: avoid; }
blockquote { border-left: 3px solid #7b9cb9; margin-left: 0; padding-left: 1em; color: #43556a; }
math { max-width: 100%; overflow-wrap: anywhere; }
@media print { * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
"""
FORBIDDEN_TAGS = {
    'script', 'iframe', 'object', 'embed', 'link', 'base', 'form', 'input',
    'button', 'audio', 'video', 'source', 'track', 'foreignobject',
}
IMAGE_MIMES = {
    'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/bmp',
    'image/avif', 'image/svg+xml',
}


def run(command, *, stdin=None, cwd=None):
    try:
        result = subprocess.run(
            command, input=stdin, cwd=cwd, capture_output=True, text=True,
            encoding='utf-8', errors='replace', timeout=TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ExportError(f"Tool execution failed: {command[0]}: {error}") from error
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()[-3000:]
        raise ExportError(f"{Path(command[0]).name} exited {result.returncode}: {detail}")
    return result.stdout


def executable(explicit, candidates, label):
    for candidate in ([explicit] if explicit else candidates):
        found = shutil.which(candidate)
        if found:
            return found
    raise ExportError(f"{label} is required; install it locally or specify its executable path.")


def css_is_local(value):
    # CSS escapes and imports can hide external requests from a simple URL scan.
    if '\\' in value or re.search(r'@import\b', value, re.I):
        raise ExportError('CSS imports/escapes are not supported in offline notes.')
    cleaned = re.sub(r'/\*.*?\*/', '', value, flags=re.S)
    for match in re.finditer(r'url\s*\((.*?)\)', cleaned, re.I | re.S):
        target = match.group(1).strip().strip('\"\'')
        if not target.startswith('#'):
            raise ExportError(f"External or file CSS resource is not supported: {target}")


def local_path(value, base):
    parsed = urlsplit(value)
    if parsed.scheme not in ('', 'file') or parsed.netloc:
        raise ExportError(f"Remote embedded resource is not allowed: {value}")
    path = Path(unquote(parsed.path))
    if not path.is_absolute():
        path = base / path
    try:
        path = path.resolve(strict=True)
    except OSError as error:
        raise ExportError(f"Image resource is missing: {value}") from error
    if not path.is_file():
        raise ExportError(f"Image resource is not a file: {value}")
    return path


def data_image(value, base):
    if value.lower().startswith('data:'):
        mime = value[5:].split(';', 1)[0].split(',', 1)[0].lower()
        if mime not in IMAGE_MIMES:
            raise ExportError(f"Unsupported embedded image type: {mime}")
        if mime == 'image/svg+xml':
            try:
                header, payload = value.split(',', 1)
                raw = base64.b64decode(payload, validate=True) if ';base64' in header.lower() else unquote(payload).encode()
                return svg_markup(raw, base)
            except (ValueError, UnicodeError) as error:
                raise ExportError(f"Invalid SVG data image: {error}") from error
        return value
    path = local_path(value, base)
    mime = mimetypes.guess_type(path.name)[0]
    if mime not in IMAGE_MIMES:
        raise ExportError(f"Unsupported image type: {path.name}")
    raw = path.read_bytes()
    if mime == 'image/svg+xml':
        return svg_markup(raw, path.parent)
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def svg_markup(raw, base):
    try:
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper() or b'<?xml-stylesheet' in raw.lower():
            raise ExportError('SVG DTD/entities and external stylesheets are not supported.')
        root = ET.fromstring(raw)
        if root.tag.rsplit('}', 1)[-1].lower() != 'svg':
            raise ExportError('An SVG image must have an svg root element.')
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
        value = ET.tostring(root, encoding='unicode')
        return OfflineHTML(base).render(value)
    except ET.ParseError as error:
        raise ExportError(f"Invalid SVG image: {error}") from error


class OfflineHTML(HTMLParser):
    """Embed local images, preserve ordinary links, reject active resources."""

    def __init__(self, base):
        super().__init__(convert_charrefs=False)
        self.base = base
        self.parts = []
        self.in_style = False

    def render(self, value):
        self.feed(value)
        self.close()
        return ''.join(self.parts)

    def handle_decl(self, declaration):
        if declaration.lower() != 'doctype html':
            raise ExportError('Only an HTML doctype is supported.')
        self.parts.append('<!DOCTYPE html>')

    def unknown_decl(self, data):
        raise ExportError('Unsupported HTML declaration.')

    def handle_pi(self, data):
        raise ExportError('Processing instructions are not supported.')

    def handle_comment(self, data):
        # Comments are irrelevant in print, including legacy conditional markup.
        pass

    def handle_starttag(self, tag, attrs):
        if tag in FORBIDDEN_TAGS:
            raise ExportError(f"Active or external HTML element is not supported: <{tag}>")
        values = dict(attrs)
        if len(values) != len(attrs):
            raise ExportError(f"Duplicate HTML attributes in <{tag}>.")
        changed = False
        for name, value in attrs:
            if name.startswith('on') or name in ('srcdoc', 'srcset', 'action', 'formaction', 'ping', 'background'):
                raise ExportError(f"Active HTML attribute is not supported: {name}")
            if name == 'http-equiv':
                raise ExportError('HTML http-equiv metadata is not supported.')
            if name == 'style' or (value and 'url' in value.lower()):
                css_is_local(value or '')
            if name in ('href', 'xlink:href') and value:
                if tag == 'a':
                    if urlsplit(value).scheme.lower() not in ('', 'https', 'http', 'mailto', 'file'):
                        raise ExportError(f"Unsupported link scheme: {value}")
                elif tag == 'image':
                    image = data_image(value, self.base)
                    if image.startswith('<'):
                        # Nested SVG images remain inert data images in SVG.
                        image = 'data:image/svg+xml;base64,' + base64.b64encode(image.encode()).decode()
                    values[name] = image
                    changed = True
                elif not value.startswith('#'):
                    raise ExportError(f"Non-local SVG reference is not supported: {value}")
            if name == 'src':
                if tag != 'img':
                    raise ExportError(f"Unsupported resource attribute in <{tag}>.")
                values[name] = data_image(value or '', self.base)
                changed = True
        if tag == 'img' and values.get('src', '').startswith('<'):
            label = html.escape(values.get('alt') or '', quote=True)
            self.parts.append(f'<span class="svg-figure" role="img" aria-label="{label}">{values["src"]}</span>')
        elif changed:
            attributes = ''.join(f' {name}="{html.escape(value or "", quote=True)}"' for name, value in values.items())
            self.parts.append(f'<{tag}{attributes}>')
        else:
            # Preserve SVG viewBox and other case-sensitive attribute spelling.
            self.parts.append(self.get_starttag_text())
        if tag == 'style':
            self.in_style = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ('img', 'meta', 'br', 'hr', 'wbr', 'area', 'col'):
            # Rewritten SVG <image> tags need their original closing semantics.
            if not self.parts[-1].rstrip().endswith('/>'):
                self.parts.append(f'</{tag}>')

    def handle_endtag(self, tag):
        if tag in FORBIDDEN_TAGS:
            raise ExportError(f"Unsupported closing HTML element: {tag}")
        self.parts.append(f'</{tag}>')
        if tag == 'style':
            self.in_style = False

    def handle_data(self, value):
        if self.in_style:
            css_is_local(value)
        self.parts.append(value)

    def handle_entityref(self, name):
        self.parts.append(f'&{name};')

    def handle_charref(self, name):
        self.parts.append(f'&#{name};')


def render_mermaid(document, directory, explicit):
    counter = 0
    cli = None

    def visit(node):
        nonlocal counter, cli
        if isinstance(node, dict):
            if node.get('t') == 'CodeBlock' and 'mermaid' in node['c'][0][1]:
                if cli is None:
                    cli = executable(explicit, ['mmdc'], 'Mermaid CLI (mmdc; use --mermaid-cli)')
                counter += 1
                source = directory / f'diagram-{counter}.mmd'
                target = directory / f'diagram-{counter}.svg'
                config = directory / 'mermaid-config.json'
                # Avoid HTML foreignObject labels and external script execution.
                config.write_text(json.dumps({'securityLevel': 'strict', 'flowchart': {'htmlLabels': False}}), encoding='utf-8')
                source.write_text(node['c'][1], encoding='utf-8')
                run([cli, '-i', str(source), '-o', str(target), '-c', str(config)], cwd=directory)
                if not target.is_file():
                    raise ExportError('Mermaid CLI completed without creating its SVG image.')
                svg_markup(target.read_bytes(), target.parent)
                return {'t': 'Para', 'c': [{'t': 'Image', 'c': [node['c'][0], [{'t': 'Str', 'c': 'Diagram'}], [str(target), '']]}]}
            return {key: visit(value) for key, value in node.items()}
        if isinstance(node, list):
            return [visit(value) for value in node]
        return node

    return visit(document)


def font_styles(path):
    stack = FONT_STACK
    face = ''
    if path:
        font = Path(path).expanduser().resolve(strict=True)
        formats = {'.ttf': ('font/ttf', 'truetype'), '.otf': ('font/otf', 'opentype'), '.woff': ('font/woff', 'woff'), '.woff2': ('font/woff2', 'woff2'), '.ttc': ('font/collection', 'collection')}
        if font.suffix.lower() not in formats or not font.is_file():
            raise ExportError('--font must name a local .ttf, .otf, .ttc, .woff or .woff2 file.')
        mime, kind = formats[font.suffix.lower()]
        payload = base64.b64encode(font.read_bytes()).decode('ascii')
        face = f'@font-face {{ font-family: NotesFont; src: url("data:{mime};base64,{payload}") format("{kind}"); font-display: block; }}\n'
        stack = 'NotesFont, ' + stack
    return face + PRINT_CSS.replace('FONT_DECL', f'font-family: {stack} !important;')


def export(args):
    source = Path(args.input).expanduser().resolve(strict=True)
    output = Path(args.output).expanduser().absolute()
    if not source.is_file():
        raise ExportError(f'Markdown input is not a file: {source}')
    if source == output.resolve() or (output.exists() and os.path.samefile(source, output)):
        raise ExportError('Input Markdown and output PDF must be different files.')
    if output.suffix.lower() != '.pdf':
        raise ExportError('Output must use a .pdf extension; Markdown and source images are preserved.')
    if output.exists() or output.is_symlink():
        if output.is_dir():
            raise ExportError(f'Output path is a directory: {output}')
        if not args.force:
            raise ExportError(f'Output already exists: {output}; use --force to replace it.')
    # Preflight the tools, font and Markdown before creating output directories.
    pandoc = executable(None, ['pandoc'], 'pandoc')
    browser = executable(args.browser, ['google-chrome', 'chromium', 'chromium-browser', 'google-chrome-stable'], 'Chrome/Chromium (use --browser)')
    css = font_styles(args.font)
    source.read_text(encoding='utf-8')
    ast_text = run([pandoc, '--from', 'markdown+raw_html+tex_math_dollars', '--to', 'json', str(source)], cwd=source.parent)
    try:
        document = json.loads(ast_text)
        if not isinstance(document, dict) or not isinstance(document.get('blocks'), list):
            raise ValueError('missing blocks')
    except (ValueError, TypeError) as error:
        raise ExportError(f'pandoc returned invalid document JSON: {error}') from error
    heading = next((block for block in document['blocks']
                    if block.get('t') == 'Header' and block['c'][0] == 1), None)
    metadata = document.setdefault('meta', {})
    if not metadata.get('title'):
        metadata['title'] = ({'t': 'MetaInlines', 'c': heading['c'][2]} if heading
                             else {'t': 'MetaString', 'c': source.stem})
    if heading:
        # Keep PDF/browser metadata without printing YAML title and H1 twice.
        metadata.setdefault('pagetitle', metadata['title'])
        del metadata['title']
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.notes-export-', dir=output.parent) as temporary:
        directory = Path(temporary)
        document = render_mermaid(document, directory, args.mermaid_cli)
        raw_html = directory / 'raw.html'
        run([pandoc, '--from', 'json', '--to', 'html5', '--standalone', '--mathml', '--output', str(raw_html)], stdin=json.dumps(document), cwd=source.parent)
        if not raw_html.is_file():
            raise ExportError('pandoc completed without creating HTML.')
        page = OfflineHTML(source.parent).render(raw_html.read_text(encoding='utf-8'))
        policy = '<meta http-equiv="Content-Security-Policy" content="default-src &apos;none&apos;; img-src data:; style-src &apos;unsafe-inline&apos;; font-src data:; base-uri &apos;none&apos;; form-action &apos;none&apos;">'
        if '</head>' not in page:
            raise ExportError('pandoc did not produce a standalone HTML document.')
        # CSP is first in head, before any resource; no remote fetches or JS.
        page = page.replace('<head>', '<head>' + policy, 1).replace('</head>', '<style>' + css + '</style></head>', 1)
        ready_html = directory / 'note.html'
        ready_html.write_text(page, encoding='utf-8')
        pdf = directory / 'note.pdf'
        run([
            browser, '--headless', '--disable-gpu', '--disable-background-networking',
            '--disable-component-update', '--disable-sync', '--disable-extensions',
            '--disable-default-apps', '--no-first-run', '--no-default-browser-check',
            '--disable-features=Translate,MediaRouter,OptimizationHints',
            '--host-resolver-rules=MAP * ~NOTFOUND', '--no-pdf-header-footer',
            '--run-all-compositor-stages-before-draw', '--virtual-time-budget=10000',
            f'--user-data-dir={directory / "browser-profile"}',
            f'--print-to-pdf={pdf}', ready_html.as_uri(),
        ])
        if not pdf.is_file():
            raise ExportError('Browser completed without creating a PDF.')
        payload = pdf.read_bytes()
        if len(payload) < 32 or not payload.startswith(b'%PDF-') or b'%%EOF' not in payload[-1024:]:
            raise ExportError('Browser output is not a complete PDF; previous output was preserved.')
        if (output.exists() or output.is_symlink()) and not args.force:
            raise ExportError(f'Output appeared during export and was preserved: {output}')
        os.replace(pdf, output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Selected Markdown file; only this note is exported')
    parser.add_argument('--output', required=True, help='Destination PDF (existing files are preserved by default)')
    parser.add_argument('--force', action='store_true', help='Atomically replace an existing output after successful validation')
    parser.add_argument('--font', help='Optional local CJK font to embed in text and inline SVG diagrams')
    parser.add_argument('--browser', help='Local Chrome/Chromium executable or command name')
    parser.add_argument('--mermaid-cli', help='Local mmdc executable for Mermaid fences; never downloads packages')
    args = parser.parse_args(argv)
    try:
        output = export(args)
    except (ExportError, OSError, UnicodeError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    print(f'PDF exported: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

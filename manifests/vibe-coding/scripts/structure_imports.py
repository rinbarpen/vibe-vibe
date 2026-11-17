"""Bounded static import extraction; not a compiler or runtime call-graph proof."""
from __future__ import annotations

import ast
import re
from pathlib import PurePosixPath

from structure_contract import ContractError, owner, within

# Comments are discarded before import matching; quoted strings remain tokens.
TOKEN = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|::|[^\s]')
SUFFIXES = ('', '.py', '/__init__.py', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs',
            '/index.ts', '/index.tsx', '/index.js', '.rs', '/mod.rs', '.java')


def quoted(token):
    return len(token) >= 2 and token[0] in "\"'`" and token[-1] == token[0]


def literal(token):
    if not quoted(token) or '\\' in token or '${' in token:
        raise ContractError('Escaped/computed import needs native dependency evidence')
    return token[1:-1]


def use_tree(tokens, prefix=''):
    """Flatten Rust use trees (including nested braces and aliases)."""
    result, current, i = [], prefix, 0
    while i < len(tokens):
        token = tokens[i]
        if token == '{':
            depth, end = 1, i + 1
            while end < len(tokens) and depth:
                depth += (tokens[end] == '{') - (tokens[end] == '}'); end += 1
            if depth:
                raise ContractError('Unbalanced Rust use tree')
            result += use_tree(tokens[i + 1:end - 1], current)
            current = prefix; i = end; continue
        if token == ',':
            if current != prefix:
                result.append(current.rstrip(':'))
            current = prefix
        elif token == 'as':
            i += 1
        elif token != '*':
            current += token
        i += 1
    if current != prefix:
        result.append(current.rstrip(':'))
    return result


def references(path, text):
    """Return (kind, specifier) pairs for the documented declaration subset."""
    suffix = PurePosixPath(path).suffix
    if suffix == '.py':
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError as exc:
            raise ContractError(f'{path}:{exc.lineno}: {exc.msg}') from exc
        refs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                refs += [('python', alias.name) for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = '.' * node.level + (node.module or '')
                refs += [('python', base + ('.' if node.module else '') + a.name) for a in node.names]
            elif isinstance(node, ast.Call) and (getattr(node.func, 'id', '') == '__import__'
                    or getattr(node.func, 'attr', '') == 'import_module'):
                raise ContractError(f'{path}: dynamic Python import needs native dependency evidence')
        return refs
    tokens = [t for t in TOKEN.findall(text) if not t.startswith(('//', '/*'))]
    refs = []
    if suffix in {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}:
        for i, token in enumerate(tokens):
            if token in {'require', 'import'} and i + 1 < len(tokens) and tokens[i + 1] == '(':
                if i + 3 >= len(tokens) or not quoted(tokens[i + 2]) or tokens[i + 3] != ')':
                    raise ContractError(f'{path}: computed import/require needs native dependency evidence')
                refs.append(('path', literal(tokens[i + 2])))
            elif token == 'import' and i + 1 < len(tokens) and quoted(tokens[i + 1]):
                refs.append(('path', literal(tokens[i + 1])))
            elif token == 'from' and i + 1 < len(tokens) and quoted(tokens[i + 1]):
                refs.append(('path', literal(tokens[i + 1])))
        return refs
    if suffix == '.go':
        i = 0
        while i < len(tokens):
            if tokens[i] == 'import':
                i += 1
                if i < len(tokens) and tokens[i] == '(':
                    i += 1
                    while i < len(tokens) and tokens[i] != ')':
                        if quoted(tokens[i]): refs.append(('slash', literal(tokens[i])))
                        i += 1
                else:
                    while i < len(tokens) and not quoted(tokens[i]): i += 1
                    if i < len(tokens): refs.append(('slash', literal(tokens[i])))
            i += 1
        return refs
    if suffix == '.java':
        for i, token in enumerate(tokens):
            if token == 'import':
                end = tokens.index(';', i) if ';' in tokens[i:] else len(tokens)
                refs.append(('java', ''.join(t for t in tokens[i + 1:end] if t != 'static').rstrip('.*')))
        return refs
    if suffix == '.rs':
        if any(tokens[i:i + 4] == ['#', '[', 'path', '=']
               or tokens[i:i + 2] == ['include', '!'] for i in range(len(tokens))):
            raise ContractError(f'{path}: Rust path/include needs native dependency evidence')
        for i, token in enumerate(tokens):
            if token == 'use':
                end = tokens.index(';', i) if ';' in tokens[i:] else len(tokens)
                refs += [('rust', s) for s in use_tree(tokens[i + 1:end])]
            if token == 'mod' and i + 2 < len(tokens) and tokens[i + 2] == ';':
                parent = PurePosixPath(path).parent
                if PurePosixPath(path).stem not in {'main', 'lib', 'mod'}:
                    parent /= PurePosixPath(path).stem
                refs.append(('file', str(parent / tokens[i + 1])))
        return refs
    raise ContractError(f'{path}: no built-in extractor for {suffix}; supply hash-bound native dependency evidence')


def candidate(root, base):
    # Symbol suffixes (Python/Java/Rust) may extend beyond the target file.
    for suffix in SUFFIXES:
        name = base + suffix
        path = within(root, name)
        if path.is_file():
            return name
    if within(root, base).is_dir():
        return base
    return None


def normalize(path):
    parts = []
    for part in path.split('/'):
        if part == '..':
            if not parts: raise ContractError('Relative import leaves project root')
            parts.pop()
        elif part and part != '.': parts.append(part)
    return '/'.join(parts)


def resolve(root, source, kind, spec, contract):
    if kind == 'file':
        result = candidate(root, spec)
        if result is None: raise ContractError(f'{source}: unresolved local module {spec}')
        return result
    if (kind == 'path' and spec.startswith('.')) or (kind == 'python' and spec.startswith('.')):
        if kind == 'python':
            count = len(spec) - len(spec.lstrip('.'))
            base = str(PurePosixPath(source).parent) + '/' + '../' * (count - 1)
            tail = spec[count:].replace('.', '/')
        else:
            base, tail = str(PurePosixPath(source).parent) + '/', spec
        local = normalize(base + tail)
        # Python from-import can end in an attribute, not a file.
        while local:
            result = candidate(root, local)
            if result: return result
            if kind != 'python' or '/' not in local: break
            local = local.rsplit('/', 1)[0]
        raise ContractError(f'{source}: unresolved relative import {spec}')
    if kind == 'rust' and spec.startswith(('self::', 'super::')):
        parent = PurePosixPath(source).parent
        if PurePosixPath(source).stem not in {'main', 'lib', 'mod'}: parent /= PurePosixPath(source).stem
        while spec.startswith('super::'): parent = parent.parent; spec = spec[7:]
        spec = spec.removeprefix('self::')
        base = str(parent / spec.replace('::', '/'))
        while base:
            result = candidate(root, base)
            if result: return result
            base = base.rsplit('/', 1)[0] if '/' in base else ''
        raise ContractError(f'{source}: unresolved Rust relative use')
    separator = '::' if kind == 'rust' else '.' if kind in {'python', 'java'} else '/'
    choices = [(p, m) for m in contract['modules'] for p in m['import_prefixes']
               if spec == p or spec.startswith(p + separator)]
    if not choices:
        if any(spec == p or spec.startswith(p + separator) for p in contract.get('external_prefixes', [])):
            return None  # Explicit external prefix; native dependency/security checks remain separate.
        raise ContractError(f'{source}: unmapped import {spec}; declare local import_prefixes or external_prefixes, or supply native evidence')
    prefix, module = max(choices, key=lambda item: len(item[0]))
    tail = spec[len(prefix):].lstrip(separator).replace(separator, '/')
    base = module['paths'][0] + ('/' + tail if tail else '')
    if kind == 'slash':
        if within(root, base).is_dir(): return base
        raise ContractError(f'{source}: unresolved Go package {spec}')
    while base:
        result = candidate(root, base)
        if result: return result
        if kind not in {'python', 'java', 'rust'} or base == module['paths'][0]: break
        base = base.rsplit('/', 1)[0] if '/' in base else ''
        if not base.startswith(module['paths'][0]): break
    raise ContractError(f'{source}: unresolved managed import {spec}')

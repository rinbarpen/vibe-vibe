#!/usr/bin/env python3
"""Render a token-driven concept map and responsive reader, using the standard library.

python3 .planning/auto-research-wiki-concept/render.py
python3 .planning/auto-research-wiki-concept/render.py --check
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
DATA = json.loads((BASE / 'concept-map.json').read_text(encoding='utf-8'))
P = DATA['presentation']
T = P['tokens']
C = T['light']
W, H = 1440, 1280


def e(value):
    return html.escape(str(value), quote=True)


def scope(domain):
    for prefix in ('ARIS 专项：', 'ARIS 可选扩展'):
        if domain['status'].startswith(prefix):
            return domain['status'].removeprefix(prefix) or '可选扩展'
    return domain['status']


def wrap(value, units):
    """Wrap CJK/Latin labels without deleting or abbreviating their content."""
    lines, line, width = [], '', 0
    for char in value:
        advance = 1 if unicodedata.east_asian_width(char) in ('W', 'F') else 0.56
        if width + advance > units and line:
            lines.append(line)
            line, width = '', 0
        line += char
        width += advance
    if line:
        lines.append(line)
    return lines


def render_svg():
    out = []
    def text(x, y, value, size=20, role='text', weight=400, anchor='start'):
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{C[role]}" font-weight="{weight}" text-anchor="{anchor}">{e(value)}</text>')
    def line(x1, y1, x2, y2, dash=False, arrow=False, role='line'):
        out.append(f'<path d="M {x1} {y1} H {x2}" fill="none" stroke="{C[role]}" stroke-width="1.5"' + (' stroke-dasharray="6 5"' if dash else '') + (' marker-end="url(#arrow)"' if arrow else '') + '/>' if y1 == y2 else f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{C[role]}" stroke-width="1.5"' + (' stroke-dasharray="6 5"' if dash else '') + (' marker-end="url(#arrow)"' if arrow else '') + '/>')
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
    out.append(f'<title id="title">{e(P["title"])}</title>')
    out.append('<desc id="desc">四阶段能力递进、四类实体反馈、默认主线与可选领域、四项补强方向；保留当前状态、证据限制及默认安装边界。</desc>')
    out.append(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 Z" fill="{C["muted"]}"/></marker></defs>')
    out.append(f'<style>text{{font-family:{e(T["font"])}}}</style>')
    out.append(f'<rect width="{W}" height="{H}" fill="{C["surface"]}"/>')
    text(56, 49, P['context'], 20, 'muted')
    text(56, 112, P['title'], T['type']['display'], weight=600)
    text(56, 153, P['boundary'], 18, 'muted')
    line(56, 182, 1384, 182)

    for i, stage in enumerate(DATA['stages']):
        x = 56 + i * 340
        # State is explicit text. Line treatment is supplementary, not a color-only key.
        line(x, 221, x + 308, 221, dash=i >= 2, role='accent' if i < 2 else 'line')
        text(x, 212, stage['number'], 18, 'accent', 500)
        text(x + 45, 212, stage['status'], 18, 'muted')
        text(x, 271, stage['title'], 28, weight=600)
        for j, item in enumerate(stage['items']):
            text(x, 316 + 33 * j, item, 20)
        for j, note in enumerate(wrap(stage['gap'], 16)):
            text(x, 392 + 26 * j, note, 18, 'muted')
        if i < 3:
            line(x + 312, 263, x + 334, 263, arrow=True, role='muted')

    line(56, 454, 1384, 454)
    text(56, 495, '研究反馈', 26, weight=600)
    xs = [150, 530, 910, 1290]
    for i, node in enumerate(DATA['loop']):
        label = node['label'].split(' / ')[0]
        if node['id'] == 'claim':
            label += '（Claim）'
        text(xs[i], 548, label, 26, weight=500, anchor='middle')
        if i < 3:
            line(xs[i] + 100, 539, xs[i + 1] - 100, 539, arrow=True, role='muted')
            text((xs[i] + xs[i + 1]) / 2, 522, ['启发', '检验', '支持 / 反驳'][i], 18, 'muted', anchor='middle')
    out.append(f'<path d="M 1290 563 V 594 H 150 V 564" fill="none" stroke="{C["muted"]}" stroke-width="1.5" stroke-dasharray="6 5" marker-end="url(#arrow)"/>')
    out.append(f'<rect x="466" y="578" width="508" height="31" fill="{C["surface"]}"/>')
    text(720, 600, '新问题 / 限定范围的失败启发 → 再研究', 20, 'muted', anchor='middle')

    line(56, 634, 1384, 634)
    text(56, 675, '支持领域', 26, weight=600)
    text(56, 720, '默认研究主线', 18, 'accent', 500)
    core = DATA['domains'][0]
    text(56, 764, core['title'], 28, weight=600)
    for j, value in enumerate(wrap(core['detail'], 16)):
        text(56, 809 + 28 * j, value, 20, 'muted')
    text(448, 720, 'ARIS 专项 · 按需安装', 18, 'muted', 500)
    for i, domain in enumerate(DATA['domains'][1:]):
        y = 762 + i * 62
        text(448, y, domain['title'], 21, weight=500)
        text(1384, y, scope(domain), 18, 'muted', anchor='end')
        text(448, y + 32, domain['detail'], 18, 'muted')
        if i < 4:
            line(448, y + 44, 1384, y + 44)
    text(56, 1084, '专项技能不等于默认安装或端到端实测；其他学科可迁移通用文献与写作能力。', 18, 'muted')

    line(56, 1108, 1384, 1108)
    text(56, 1150, '补强顺序', 26, weight=600)
    for i, priority in enumerate(DATA['priorities']):
        x = 56 + i * 340
        text(x, 1200, priority['number'], 22, 'accent', 500)
        text(x + 32, 1200, priority['title'], 22, weight=500)
    text(56, 1245, '证明状态与实验证据分开；方法或部分实验失败，不自动否定整个想法。', 18, 'muted')
    out.append('</svg>')
    svg = '\n'.join(out) + '\n'
    ET.fromstring(svg)
    return svg


def render_html():
    light = ''.join(f'--color-{key}:{value};' for key, value in T['light'].items())
    dark = ''.join(f'--color-{key}:{value};' for key, value in T['dark'].items())
    tokens = (f':root{{color-scheme:light dark;{light}--font-body:{T["font"]};'
              '--space-page:clamp(20px,4vw,56px);--space-section:36px;--space-group:24px;'
              '--text-body:16px;--text-secondary:14px;--text-heading:22px;--text-display:clamp(28px,4vw,44px);}'
              f'@media(prefers-color-scheme:dark){{:root{{{dark}}}}}')
    style = tokens + '''
*{box-sizing:border-box}html,body{margin:0;background:var(--color-surface);color:var(--color-text)}
body{font-family:var(--font-body);font-size:var(--text-body);line-height:1.6}
main{max-width:1440px;margin-inline:auto;padding:28px var(--space-page) 24px}
h1,h2,h3,p,ol,dl{margin:0}h1{font-size:var(--text-display);line-height:1.25;font-weight:600;letter-spacing:-.03em;margin:12px 0 20px}
h2{font-size:var(--text-heading);font-weight:600;line-height:1.4}h3{font-size:18px;font-weight:500}
.context,.boundary,.scope,.stage-gap,.group-title,.return,.coverage-note,.detail-meta{color:var(--color-muted)}
.boundary,.state,.scope,.group-title,.coverage-note,.detail-meta{font-size:var(--text-secondary)}
header{padding-bottom:var(--space-group)}
.stages{list-style:none;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:28px;border-top:1px solid var(--color-line);padding:28px 0 30px}
.stage{position:relative;padding-top:14px;border-top:2px solid var(--color-accent);min-width:0}
.stage:nth-child(n+3){border-top:2px dashed var(--color-line)}
.stage:not(:last-child)::after{content:'→';position:absolute;right:-23px;top:63px;color:var(--color-muted)}
.state-row{display:flex;align-items:baseline;gap:12px;margin-bottom:20px}.stage-number{color:var(--color-accent);font-variant-numeric:tabular-nums}
.state{color:var(--color-muted)}.stage h2{font-size:24px;margin-bottom:18px}
.stage-copy{line-height:1.9}.stage-gap{margin-top:24px;font-size:var(--text-secondary)}
.feedback,.coverage,.priorities{border-top:1px solid var(--color-line);padding-block:24px}
.loop{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));list-style:none;padding:22px 0 0;gap:32px}
.loop li{position:relative;font-size:22px;font-weight:500;text-align:center}
.loop li:not(:last-child)::after{content:'→';position:absolute;right:-24px;top:0;color:var(--color-muted);font-weight:400}
.loop-edge{position:absolute;left:calc(100% + 16px);top:28px;transform:translateX(-50%);width:110px;font-size:var(--text-secondary);font-weight:400;color:var(--color-muted)}
.return{border-bottom:1px dashed var(--color-muted);text-align:center;margin-top:18px;padding-bottom:9px;font-size:var(--text-secondary)}
.coverage-grid{display:grid;grid-template-columns:1fr 2.5fr;gap:48px;margin-top:20px}
.group-title{margin-bottom:12px}.core .group-title{color:var(--color-accent)}.core h3{font-size:25px;font-weight:600;margin-bottom:14px}.core p:last-child{color:var(--color-muted)}
.domain{display:grid;grid-template-columns:minmax(170px,1fr) minmax(0,2fr);gap:4px 18px;padding:8px 0;border-bottom:1px solid var(--color-line)}
.domain:last-child{border-bottom:0}.domain dt{font-weight:500}.domain dd{margin:0;min-width:0}.domain .scope{grid-column:2;margin-top:-3px}
.coverage-note{margin-top:16px}.priorities ol{list-style:none;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;padding:18px 0 0}
.priority{display:flex;gap:12px;align-items:baseline}.priority span{color:var(--color-accent)}
.appendix{border-top:1px solid var(--color-line);padding-top:16px}.appendix summary{cursor:pointer;color:var(--color-muted);width:fit-content}
.appendix summary:hover{color:var(--color-accent)}.appendix summary:focus-visible{outline:2px solid var(--color-accent);outline-offset:5px}
.detail-content{padding-top:18px;display:grid;gap:14px}.detail-content ul{margin:0;padding-left:20px}.source-list code{overflow-wrap:anywhere;font-size:var(--text-secondary);font-family:var(--font-body)}
.detail-entities{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 24px}.detail-entities dd{margin:0;color:var(--color-muted)}
@media(max-width:1023px){.coverage-grid{grid-template-columns:1fr 2fr;gap:28px}.domain{grid-template-columns:1fr}.domain .scope{grid-column:1;margin-top:0}.stage h2{font-size:21px}.stage-copy{line-height:1.7}}
@media(max-width:767px){.stages{grid-template-columns:1fr;gap:0;padding-bottom:8px}.stage,.stage:nth-child(n+3){border-top:0;border-left:2px solid var(--color-line);margin-left:9px;padding:0 0 28px 25px}.stage:nth-child(n+3){border-left-style:dashed}.stage:last-child{border-left-color:transparent}.stage::before{content:'';position:absolute;width:12px;height:12px;left:-7px;top:8px;border:2px solid var(--color-accent);background:var(--color-surface)}.stage:nth-child(-n+2)::before{background:var(--color-accent)}.stage:not(:last-child)::after{display:none}.state-row{margin-bottom:6px}.stage h2{font-size:24px;margin-bottom:10px}.stage-gap{margin-top:10px}.loop{grid-template-columns:1fr;gap:20px;padding-top:20px}.loop li{text-align:left;padding-left:18px;font-size:22px}.loop li:not(:last-child)::after{content:'↓';right:auto;left:0;top:24px;font-size:18px}.loop-edge{position:static;display:inline;transform:none;width:auto;margin-left:14px}.return{text-align:left}.coverage-grid{grid-template-columns:1fr;gap:24px}.core h3{margin-bottom:8px}.domain{padding-block:12px;gap:5px}.priorities ol{grid-template-columns:1fr;gap:12px}.detail-entities{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media print{main{max-width:none}.appendix{display:none}}
'''
    stages = []
    for stage in DATA['stages']:
        items = '<br>'.join(e(item) for item in stage['items'])
        stages.append(f'''<li class="stage" data-stage="{e(stage['id'])}"><div class="state-row"><span class="stage-number">{e(stage['number'])}</span><span class="state">{e(stage['status'])}</span></div><h2>{e(stage['title'])}</h2><p class="stage-copy">{items}</p><p class="stage-gap">{e(stage['gap'])}</p></li>''')
    nodes = []
    for i, node in enumerate(DATA['loop']):
        name = node['label'].split(' / ')[0] + ('（Claim）' if node['id'] == 'claim' else '')
        edge = f'<span class="loop-edge">{["启发", "检验", "支持 / 反驳"][i]}</span>' if i < 3 else ''
        nodes.append(f'<li>{e(name)}{edge}</li>')
    domains = ''.join(f'<div class="domain"><dt>{e(d["title"])}</dt><dd>{e(d["detail"])}</dd><dd class="scope">{e(scope(d))}</dd></div>' for d in DATA['domains'][1:])
    priorities = ''.join(f'<li class="priority"><span>{e(item["number"])}</span>{e(item["title"])}</li>' for item in DATA['priorities'])
    notes = ''.join(f'<li>{e(note)}</li>' for note in DATA['notes'])
    entities = ''.join(f'<div><dt>{e(n["label"])}</dt><dd>{e(n["detail"])}</dd></div>' for n in DATA['loop'])
    priority_details = ''.join(f'<li>{e(item["title"])}：{e(item["detail"])}</li>' for item in DATA['priorities'])
    sources = ''.join(f'<li><code>{e(value)}</code></li>' for value in DATA['sources'] + P['rules'])
    core = DATA['domains'][0]
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(P['title'])}</title><style>{style}</style></head>
<body><main id="ar-wiki-concept"><header><p class="context">{e(P['context'])}</p><h1>{e(P['title'])}</h1><p class="boundary">{e(P['boundary'])}</p></header>
<section aria-label="概念发展主线"><ol class="stages">{''.join(stages)}</ol></section>
<section class="feedback" aria-labelledby="feedback-title"><h2 id="feedback-title">研究反馈</h2><ol class="loop">{''.join(nodes)}</ol><p class="return">新问题 / 限定范围的失败启发 → 再研究</p></section>
<section class="coverage" aria-labelledby="coverage-title"><h2 id="coverage-title">支持领域</h2><div class="coverage-grid"><div class="core"><p class="group-title">默认研究主线</p><h3>{e(core['title'])}</h3><p>{e(core['detail'])}</p></div><div class="optional"><p class="group-title">ARIS 专项 · 按需安装</p><dl>{domains}</dl></div></div><p class="coverage-note">专项技能不等于默认安装或端到端实测；其他学科可迁移通用文献与写作能力。</p></section>
<section class="priorities" aria-labelledby="priorities-title"><h2 id="priorities-title">补强顺序</h2><ol>{priorities}</ol></section>
<details class="appendix"><summary>来源与完整说明</summary><div class="detail-content"><p class="detail-meta">{e(DATA['snapshot'])}</p><dl class="detail-entities">{entities}</dl><ul>{priority_details}</ul><ul>{notes}</ul><ul class="source-list">{sources}</ul></div></details>
</main></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, content in {'concept-map.svg': render_svg(), 'concept-map.html': render_html()}.items():
        path = BASE / name
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                print(f'DRIFT {path}')
                return 1
        else:
            temp = path.with_suffix(path.suffix + '.tmp')
            temp.write_text(content, encoding='utf-8')
            os.replace(temp, path)
        print(f'{"CHECK" if args.check else "WROTE"} {path} sha256={hashlib.sha256(content.encode()).hexdigest()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

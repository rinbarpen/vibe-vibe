#!/usr/bin/env python3
"""Deterministic concept-map renderer. Python standard library only.
Run: python3 .planning/auto-research-wiki-concept/render.py [--check]
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
DATA = json.loads((BASE/'concept-map.json').read_text(encoding='utf-8'))
W, H = 1600, 1430
COL = {
 'ink':'#172B3A','muted':'#526675','border':'#D6DFE3','bg':'#F7F9FA',
 'green':('#E9F4EF','#247251'),'amber':('#FFF1DB','#93600D'),
 'blue':('#EAF0FA','#315E9C')
}
parts=[]
def add(s): parts.append(s)
def esc(s): return html.escape(str(s))
def rect(x,y,w,h,fill='#FFFFFF',stroke=None,r=16,dash=False):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="1.5"' if stroke else '')+(' stroke-dasharray="7 5"' if dash else '')+'/>')
def text(x,y,s,size=22,fill=None,weight=400,anchor='start'):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or COL["ink"]}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')
def line(x1,y1,x2,y2,color='#A4B3BD',width=2,dash=False,arrow=False):
    add(f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="7 6"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
def pill(x,y,label,tone='green',width=None):
    bg,fg=COL[tone]
    width=width or (len(label)*17+24)
    rect(x,y,width,30,bg,r=15)
    text(x+width/2,y+21,label,17,fg,500,'middle')
def section(y,n,title,aside):
    text(48,y,n,18,COL['muted'],500)
    text(88,y,title,26,weight=600)
    text(1552,y,aside,18,COL['muted'],anchor='end')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
add(f'<title id="title">{esc(DATA["title"])}</title>')
add('<desc id="desc">文献积累、关系化知识、证据化研究、持续研究记忆四层递进；包含论文、想法、实验、主张的研究反馈环，六类领域支持范围，以及四项补强方向。当前能力与目标能力分别标注。</desc>')
add('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#8B9CA7"/></marker></defs>')
add('<style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",sans-serif}</style>')
rect(0,0,W,H,COL['bg'],r=0)
text(48,49,'RESEARCH KNOWLEDGE  /  CONCEPT DEVELOPMENT',17,COL['muted'],500)
text(48,106,DATA['title'],39,weight=600)
text(48,147,DATA['subtitle'],25,COL['muted'])
pill(1114,33,'已实现基础',tone='green',width=132)
pill(1261,33,'部分接通',tone='amber',width=122)
pill(1398,33,'目标 / 待补强',tone='blue',width=154)
text(1552,147,DATA['snapshot'],17,COL['muted'],anchor='end')
line(48,176,1552,176,COL['border'],1)
section(217,'A','概念如何发展','由“保存材料”走向“累积研究判断”')

cw,gap,x0,y0=352,32,48,242
for i,s in enumerate(DATA['stages']):
    x=x0+i*(cw+gap)
    bg,fg=COL[s['tone']]
    rect(x,y0,cw,298,'#FFFFFF',COL['border'],18,dash=i==3)
    rect(x,y0,cw,8,fg,r=4)
    text(x+22,y0+48,s['number'],19,fg,500)
    pill(x+cw-194,y0+23,s['status'],s['tone'],width=174)
    text(x+22,y0+96,s['title'],29,weight=600)
    text(x+22,y0+134,s['question'],21,COL['muted'])
    for j,item in enumerate(s['items']): text(x+22,y0+180+j*33,item,20)
    line(x+22,y0+235,x+cw-22,y0+235,COL['border'],1)
    # Split long status notes into two exact lines rather than tiny type.
    words = {
      'collect':['内容补全需另行调用','wiki-enrich'],
      'connect':['关系识别与一致性','仍需维护'],
      'evidence':['默认生命周期回写','尚未接全'],
      'memory':['需补问题检索、失败范围','与保留策略']
    }[s['id']]
    for j,note in enumerate(words): text(x+22,y0+262+j*24,note,18,COL['muted'])
    if i<3:
        line(x+cw+4,y0+107,x+cw+gap-4,y0+107,arrow=True)
        text(x+cw+gap/2,575,s['edge'],18,COL['muted'],anchor='middle')

section(631,'B','四类实体组成反馈环','关系结构已具备；默认自动回写尚待接全')
# A shared strip makes the evidence loop one visual unit.
rect(48,654,1504,171,'#EFF3F5',r=18)
node_x=[72,452,832,1212]
for i,n in enumerate(DATA['loop']):
    x=node_x[i]
    rect(x,678,292,86,'#FFFFFF',COL['border'],12)
    text(x+146,713,n['label'],23,weight=600,anchor='middle')
    text(x+146,744,n['detail'],17,COL['muted'],anchor='middle')
    if i<3:
        labels=['启发','检验','支持 / 反驳']
        line(x+298,719,node_x[i+1]-6,719,arrow=True)
        text(x+336,699,labels[i],15,COL['muted'],anchor='middle')
# Dashed feedback: only an intended connection, not a claim of automatic scheduling.
add('<path d="M 1358 768 V 797 H 218 V 770" fill="none" stroke="#8B9CA7" stroke-width="2" stroke-dasharray="7 6" marker-end="url(#arrow)"/>')
rect(602,778,396,32,'#EFF3F5',r=4)
text(800,801,'新问题 / 限定范围的失败启发 → 再研究',18,COL['muted'],anchor='middle')

section(881,'C','当前可以落在哪些领域','Wiki 骨架领域无关；专项能力分层接入')
for i,d in enumerate(DATA['domains']):
    col,row=i%3,i//3
    x,y=48+col*509,905+row*131
    rect(x,y,486,112,'#FFFFFF',COL['border'],14)
    _,fg=COL[d['tone']]
    rect(x+17,y+21,4,25,fg,r=2)
    text(x+33,y+42,d['title'],24,weight=600)
    text(x+22,y+73,d['detail'],18,COL['muted'])
    text(x+22,y+98,d['status'],17,fg,500)

section(1199,'D','下一步：让“能存”变成“可依赖”','补强方向，不表示已实现')
for i,p in enumerate(DATA['priorities']):
    x,y=48+i*384,1225
    text(x,y+26,p['number'],24,COL['blue'][1],500)
    text(x+30,y+26,p['title'],22,weight=600)
    text(x+30,y+58,p['detail'],17,COL['muted'])
line(48,1311,1552,1311,COL['border'],1)
for i,note in enumerate(DATA['notes']):text(48,1344+i*27,note,17,COL['muted'])
add('</svg>')
svg='\n'.join(parts)+'\n'
ET.fromstring(svg)
html_page='''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ARIS Wiki 概念发展图</title><style>
*{box-sizing:border-box}html,body{margin:0;padding:0;background:transparent}main{max-width:1600px;margin:auto}svg{display:block;width:100%;height:auto}a:focus-visible{outline:3px solid #315E9C}
</style></head><body><main>'''+svg+'</main></body></html>\n'
outputs={'concept-map.svg':svg,'concept-map.html':html_page}
parser=argparse.ArgumentParser()
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
for name,content in outputs.items():
    path=BASE/name
    if args.check:
        assert path.read_text(encoding='utf-8')==content,f'Drift: {name}'
    else:
        temp=path.with_suffix(path.suffix+'.tmp')
        temp.write_text(content,encoding='utf-8')
        os.replace(temp,path)
    print(f'{"CHECK" if args.check else "WROTE"} {path} sha256={hashlib.sha256(content.encode()).hexdigest()}')

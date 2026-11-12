#!/usr/bin/env python3
"""Actual browser checks for the original and redrawn concept map."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parent
EVIDENCE=BASE/'ui-redraw'
ORIGINAL=EVIDENCE/'originals/.planning/auto-research-wiki-concept'
DATA=json.loads((BASE/'concept-map.json').read_text(encoding='utf-8'))

def contrast(foreground,background):
    def lum(h):
        c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
        a=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
        return sum(v*w for v,w in zip(a,[.2126,.7152,.0722]))
    hi,lo=sorted((lum(foreground),lum(background)),reverse=True)
    return (hi+.05)/(lo+.05)

MEASURE='''() => {
 const texts=[...document.querySelectorAll('body *')].filter(e=>e.children.length===0&&e.textContent.trim()&&e.checkVisibility());
 const fontSizes=texts.filter(e=>!['STYLE','TITLE','DESC','PATH'].includes(e.tagName.toUpperCase())).map(e=>{const size=parseFloat(getComputedStyle(e).fontSize);const svg=e.closest('svg');return size*(svg?svg.getBoundingClientRect().width/svg.viewBox.baseVal.width:1)});
 return {viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,smallestVisibleFontPx:Math.min(...fontSizes),stageTops:[...document.querySelectorAll('.stage')].map(e=>Math.round(e.getBoundingClientRect().top)),detailsCount:document.querySelectorAll('details').length};
}'''

def run(mode):
    rows=[]
    screenshot_dir=EVIDENCE/'screenshots'
    screenshot_dir.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/snap/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        if mode=='baseline':
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.goto((ORIGINAL/'concept-map.html').as_uri(),wait_until='load')
            page.evaluate('document.fonts.ready')
            for width in [320,768,1024,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                item=page.evaluate(MEASURE)
                item['small_screen_task_readability']='FAIL' if item['smallestVisibleFontPx']<12 else 'PASS'
                item['screenshot']=str(screenshot_dir/f'before-light-{width}.png')
                page.screenshot(path=item['screenshot'],full_page=True)
                rows.append(item)
            result={'mode':mode,'observations':rows,'notes':['Original reader scales the entire desktop SVG instead of reflowing. No user timing or success-rate claim.']}
        else:
            original=json.loads((ORIGINAL/'concept-map.json').read_text(encoding='utf-8'))
            retained={k:v for k,v in DATA.items() if k!='presentation'}
            assert retained==original,'Original scientific/domain content changed'
            ratios={}
            for theme,palette in DATA['presentation']['tokens'].items():
                if theme not in ('light','dark'):continue
                ratios[theme]={role:round(contrast(palette[role],palette['surface']),2) for role in ['text','muted','accent']}
                assert min(ratios[theme].values())>=4.5,ratios
                page=browser.new_page(viewport={'width':1440,'height':1000},color_scheme=theme,reduced_motion='reduce')
                page.goto((BASE/'concept-map.html').as_uri(),wait_until='load')
                page.evaluate('document.fonts.ready')
                for width in [320,768,1024,1440]:
                    page.set_viewport_size({'width':width,'height':1000})
                    item=page.evaluate(MEASURE)
                    assert item['pageWidth']==width,item
                    assert item['smallestVisibleFontPx']>=14,item
                    assert len(item['stageTops'])==4,item
                    if width==320:
                        assert len(set(item['stageTops']))==4,item
                    else:
                        assert len(set(item['stageTops']))==1,item
                    visible=page.locator('main').inner_text()
                    for stage in DATA['stages']:
                        for value in [stage['title'],stage['status'],stage['gap'],*stage['items']]:
                            assert value in visible,value
                    for domain in DATA['domains']:
                        assert domain['title'] in visible,domain['title']
                        assert domain['detail'] in visible,domain['detail']
                    summary=page.locator('summary')
                    summary.focus()
                    page.keyboard.press('Enter')
                    assert page.locator('details').get_attribute('open') is not None
                    assert page.locator('.source-list').is_visible()
                    assert 'manifests/vibe-coding/rules/vibe-coding-ui-design.mdc' in page.locator('.source-list').inner_text()
                    page.keyboard.press('Enter')
                    assert page.locator('details').get_attribute('open') is None
                    item.update({'theme':theme,'keyboard_disclosure':'PASS','content_and_boundaries':'PASS','screenshot':str(screenshot_dir/f'after-{theme}-{width}.png')})
                    page.screenshot(path=item['screenshot'],full_page=True)
                    rows.append(item)
                page.close()
            page=browser.new_page(viewport={'width':1440,'height':1280})
            page.set_content('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>html,body{margin:0}svg{display:block}</style></head><body>'+ (BASE/'concept-map.svg').read_text(encoding='utf-8') +'</body></html>',wait_until='load')
            page.evaluate('document.fonts.ready')
            svg_check=page.evaluate('''()=>{const svg=document.querySelector('svg'),v=svg.viewBox.baseVal;const items=[...svg.querySelectorAll('text')].map(t=>({label:t.textContent,b:t.getBBox()}));return {viewBox:[v.width,v.height],texts:items.length,outside:items.filter(({b})=>b.x<0||b.y<0||b.x+b.width>v.width||b.y+b.height>v.height).map(t=>t.label),overlaps:items.flatMap((a,i)=>items.slice(i+1).filter(c=>a.b.x<c.b.x+c.b.width-1&&a.b.x+a.b.width>c.b.x+1&&a.b.y<c.b.y+c.b.height-1&&a.b.y+a.b.height>c.b.y+1).map(c=>[a.label,c.label]))}}''')
            assert not svg_check['outside'],svg_check
            assert not svg_check['overlaps'],svg_check
            page.screenshot(path=str(BASE/'concept-map.png'),timeout=15000)
            result={'mode':mode,'source_semantics_unchanged':'PASS','contrast_ratios':ratios,'observations':rows,'svg_geometry':svg_check,'static_output':'1440 × 1280 px, light fixed theme','not_applicable':['Static SVG hover/loading/save states','Backend persistence: no data-writing UI','User research: browser assertions are AI checks only']}
        browser.close()
    out=EVIDENCE/f'{mode}-behavior.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['baseline','modified'],required=True)
    args=parser.parse_args()
    run(args.mode)

"""Render two-panel comparative error chart from synthetic CSV."""
from pathlib import Path
import csv
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
O=Path(__file__).resolve().parent
D=defaultdict(lambda: {'Baseline':[],'Corrected':[]})
with (O/'data.csv').open(newline='') as f:
    for r in csv.DictReader(f):
        ref=float(r['reference_NTU']); g=r['condition']
        for method,col in [('Baseline','baseline_NTU'),('Corrected','corrected_NTU')]:
            D[g][method].append(float(r[col])-ref)
groups=['Clear','Moderate','High']; methods=['Baseline','Corrected']; colors={'Baseline':'#557D91','Corrected':'#D0814D'}
assert set(D)==set(groups) and all(len(D[g][m])==12 for g in groups for m in methods)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.5,'pdf.fonttype':42})
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(8.5,4.1),gridspec_kw={'width_ratios':[1,1]})
fig.subplots_adjust(left=.09,right=.98,top=.76,bottom=.2,wspace=.36)
fig.suptitle('Turbidity estimation under three conditions',x=.09,y=.96,ha='left',fontsize=13.5,weight='bold')
fig.text(.09,.87,'Synthetic example  ·  12 paired cases per condition  ·  descriptive only',fontsize=9,color='#555')
for i,g in enumerate(groups):
    for m,off in [('Baseline',-.16),('Corrected',.16)]:
        err=np.array(D[g][m]); y=i+1+off
        ax1.scatter(np.abs(err),np.full(len(err),y)+np.linspace(-.065,.065,len(err)),s=13,
                    color=colors[m],alpha=.45,edgecolors='none')
        ax1.errorbar([np.abs(err).mean()],[y],xerr=[np.abs(err).std(ddof=1)],fmt='D',markersize=6,
                     color=colors[m],capsize=3,lw=1.3,zorder=5)
        bp=ax2.boxplot([err],positions=[y],widths=.24,vert=False,patch_artist=True,showfliers=False,
            manage_ticks=False,medianprops={'color':'#202B31','lw':1.1},
            boxprops={'color':colors[m],'lw':1.0},whiskerprops={'color':colors[m],'lw':.9},
            capprops={'color':colors[m],'lw':.9})
        bp['boxes'][0].set_facecolor(colors[m]);bp['boxes'][0].set_alpha(.25)
        ax2.scatter(err,np.full(len(err),y)+np.linspace(-.05,.05,len(err)),s=11,color=colors[m],alpha=.65,zorder=3)
for ax in (ax1,ax2):
    ax.set_yticks(range(1,4),groups);ax.set_ylim(3.5,.5)
    ax.grid(axis='x',color='#DEE4E7',lw=.7);ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
ax1.set_title('A  Absolute error',loc='left',weight='bold',pad=8)
ax1.set_xlabel('Absolute error (NTU)');ax1.set_xlim(-.3,17)
ax2.set_title('B  Signed error',loc='left',weight='bold',pad=8)
ax2.set_xlabel('Estimate − reference (NTU)');ax2.set_xlim(-17,17)
ax2.axvline(0,ls='--',color='#787F84',lw=.9)
fig.legend(handles=[Line2D([0],[0],marker='o',ls='',color=colors[m],label=m) for m in methods],
           loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,.035))
# Plot grammar documented in brief.md and review.md; no footer overprint.
for ext in ('png','pdf'):fig.savefig(O/f'stat_multi.{ext}',dpi=300,facecolor='white')
plt.close(fig)
for g in groups:
    for m in methods:
        e=np.array(D[g][m]);print(f'{g} {m}: n={len(e)}, MAE={np.abs(e).mean():.3f} NTU, bias={e.mean():.3f} NTU')

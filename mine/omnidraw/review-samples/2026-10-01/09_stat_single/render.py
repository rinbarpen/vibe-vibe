"""Render single-panel statistical chart from explicitly simulated CSV."""
from pathlib import Path
import csv
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
D=defaultdict(list)
with (O/'data.csv').open(newline='') as f:
    for r in csv.DictReader(f):
        D[float(r['nominal_turbidity_NTU'])].append(float(r['normalized_transmission']))
x=np.array(sorted(D)); y=np.array([np.mean(D[k]) for k in x]); sd=np.array([np.std(D[k],ddof=1) for k in x])
assert all(len(D[k])==5 for k in x) and np.all((y>=0)&(y<=1))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(6.2,4.2)); fig.subplots_adjust(left=.15,right=.96,top=.78,bottom=.22)
fig.suptitle('Optical response to turbidity standards',x=.15,y=.96,ha='left',fontsize=13,weight='bold')
fig.text(.15,.87,'Synthetic example  ·  5 simulated replicates per level',fontsize=9,color='#555')
for i,k in enumerate(x):
    jitter=np.linspace(-1.5,1.5,len(D[k]))
    ax.scatter(np.full(len(D[k]),k)+jitter,D[k],color='#8CB0BF',s=20,edgecolor='white',lw=.4,zorder=3)
ax.errorbar(x,y,yerr=sd,fmt='o-',color='#17617A',mfc='white',mec='#17617A',markersize=7,
            lw=1.6,capsize=4,elinewidth=1.2,zorder=4,label='Mean ± SD')
ax.set(xlabel='Nominal turbidity standard (NTU)',ylabel='Normalized transmitted intensity (a.u.)',xlim=(-6,106),ylim=(.3,1.02))
ax.set_xticks(x);ax.grid(axis='y',color='#DDE3E6',lw=.7);ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
ax.legend(frameon=False,loc='upper right')
fig.text(.15,.035,'Error bars = sample SD; not a confidence interval.',fontsize=8,color='#555')
for ext in ('png','pdf'):
    fig.savefig(O/f'stat_single.{ext}',dpi=300,facecolor='white')
plt.close(fig)
for k,m,s in zip(x,y,sd): print(f'{k:g} NTU: n=5, mean={m:.4f}, SD={s:.4f}')

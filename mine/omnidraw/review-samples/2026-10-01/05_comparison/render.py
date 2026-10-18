"""Schematic qualitative comparison; not a photograph or measured data."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
from matplotlib.lines import Line2D

O=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
fig,axs=plt.subplots(1,2,figsize=(10,4.3))
fig.subplots_adjust(left=.055,right=.98,top=.74,bottom=.19,wspace=.18)
fig.suptitle('Portable river-water turbidity: optical response',x=.055,y=.96,ha='left',fontsize=15,weight='bold')
fig.text(.055,.89,'Conceptual comparison — drawn schematic, not a photograph or measured detector output',fontsize=9,color='#555')

def arrow(ax, start,end,color,width=2,ms=13,alpha=1):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=ms,lw=width,color=color,alpha=alpha))
def draw(ax, title, turbid):
    ax.set_xlim(0,10); ax.set_ylim(0,6.5); ax.axis('off')
    ax.set_title(title,loc='left',weight='bold',fontsize=12,pad=8)
    ax.add_patch(Rectangle((3.0,1.4),4.0,3.5,facecolor='#E8F7FA' if not turbid else '#D8C9A8',edgecolor='#516575',lw=1.6))
    ax.add_patch(Rectangle((.45,2.7),1.25,.85,facecolor='#173952',edgecolor='none'))
    ax.text(1.07,3.125,'LED',ha='center',va='center',color='white',weight='bold')
    ax.add_patch(Rectangle((8.18,2.7),1.45,.85,facecolor='#253C50',edgecolor='none'))
    ax.text(8.9,3.125,'T',ha='center',va='center',color='white',weight='bold')
    ax.add_patch(Rectangle((4.35,5.42),1.3,.68,facecolor='#253C50',edgecolor='none'))
    ax.text(5,5.76,'S',ha='center',va='center',color='white',weight='bold')
    ax.text(1.08,2.43,'850 nm',ha='center',fontsize=8)
    ax.text(8.92,2.34,'transmitted',ha='center',fontsize=8)
    ax.text(5,6.2,'90° scatter',ha='center',fontsize=8)
    arrow(ax,(1.75,3.12),(3,3.12),'#DBA643',2.3)
    if turbid:
        for x,y in [(3.55,3.4),(3.9,2.4),(4.2,4.15),(4.45,3.05),(4.9,2.8),(5.15,3.58),(5.6,2.2),(5.85,4.2),(6.35,3.1),(6.7,3.8)]:
            ax.add_patch(Circle((x,y),.10,facecolor='#927856',edgecolor='#6D5E48',lw=.35))
        arrow(ax,(3.03,3.12),(5.02,3.12),'#DBA643',2.1)
        arrow(ax,(5.02,3.12),(7,3.12),'#DBA643',1.2,alpha=.42)
        arrow(ax,(7.02,3.12),(8.16,3.12),'#DBA643',.9,alpha=.42)
        for p in [(4.2,3.1),(5.1,3.1),(6,3.1)]:
            arrow(ax,p,(p[0],5.35),'#3B8B9E',1.3,ms=10,alpha=.75)
        ax.text(5,.82,'lower T  ·  higher S',ha='center',weight='bold',color='#594A37',fontsize=11)
        ax.text(5,.36,'Illustrative: T = 0.40, S = 0.60 a.u.',ha='center',color='#594A37',fontsize=8.5)
    else:
        arrow(ax,(3.03,3.12),(7,3.12),'#DBA643',2.8)
        arrow(ax,(7.02,3.12),(8.16,3.12),'#DBA643',2.8)
        arrow(ax,(5,3.1),(5,5.35),'#3B8B9E',.8,ms=9,alpha=.35)
        ax.text(5,.82,'higher T  ·  lower S',ha='center',weight='bold',color='#345B6A',fontsize=11)
        ax.text(5,.36,'Illustrative: T = 0.90, S = 0.10 a.u.',ha='center',color='#345B6A',fontsize=8.5)

draw(axs[0],'A  Clear water',False)
draw(axs[1],'B  Turbid water',True)
fig.text(.055,.055,'T = transmission detector; S = side-scatter detector. Relative trends only; particle count and positions are illustrative.',fontsize=8.4,color='#555')
for ext in ('svg','png','pdf'):
    fig.savefig(O/f'comparison.{ext}',dpi=300,facecolor='white')
plt.close(fig)

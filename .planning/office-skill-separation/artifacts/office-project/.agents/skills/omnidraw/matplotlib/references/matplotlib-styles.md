# Matplotlib Style Reference

## Built-in Styles

```python
plt.style.use('default')       # Matplotlib default
plt.style.use('seaborn-v0_8')  # Seaborn style
plt.style.use('ggplot')        # R ggplot style
plt.style.use('fivethirtyeight') # Data journalism
plt.style.use('grayscale')     # Black and white
plt.style.use('dark_background') # Dark theme
plt.style.use('bmh')           # Bayesian Methods
```

List all: `print(plt.style.available)`

## Publication Style Presets

### IEEE / ACM Style
```python
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.8,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'lines.linewidth': 1.2,
    'lines.markersize': 4,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})
```

### Presentation Style
```python
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 16,
    'axes.labelsize': 18,
    'axes.titlesize': 20,
    'legend.fontsize': 14,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'axes.linewidth': 2.0,
    'lines.linewidth': 3.0,
    'lines.markersize': 10,
    'grid.alpha': 0.2,
    'figure.facecolor': 'white',
})
```

### Chinese Journal Style (中文期刊)
```python
plt.rcParams.update({
    'font.sans-serif': ['SimHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'axes.unicode_minus': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})
```

### Minimal Clean
```python
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.2,
    'axes.axisbelow': True,
})
```

## Color Palettes

### Distinguishable (Up to 8)
```python
colors = ['#6c8ebf', '#82b366', '#d6b656', '#b85450',
          '#9673a6', '#d79b00', '#6c8ebf', '#b3b3b3']
```

### Seaborn Qualitative
```python
import seaborn as sns
colors = sns.color_palette('husl', 8)
colors = sns.color_palette('Set2', 8)
colors = sns.color_palette('tab10', 10)
```

### Grayscale (Print)
```python
colors = ['#333333', '#666666', '#999999', '#bbbbbb',
          '#444444', '#777777', '#aaaaaa', '#dddddd']
```

### Colormap Selection
| Data Type | Colormap | Notes |
|-----------|----------|-------|
| Sequential | `Blues`, `Greens`, `viridis`, `plasma` | Low→High values |
| Diverging | `RdBu`, `coolwarm`, `PuOr`, `BrBG` | Centered data, ± change |
| Qualitative | `Set2`, `tab10`, `Pastel1` | Distinct categories |
| Heatmap | `coolwarm`, `RdBu_r`, `YlOrRd` | Common choice |

## Figure Sizing

| Format | Size (inches) | Use |
|--------|--------------|-----|
| Single column (IEEE) | 3.5 × 2.5 | Column-width figure |
| Double column (IEEE) | 7.0 × 4.0 | Full-width figure |
| CVPR/ICCV (single) | 6.0 × 3.5 | Single column |
| Presentation (16:9) | 10.0 × 5.625 | Full slide |
| Presentation (4:3) | 8.0 × 6.0 | Full slide |
| Poster portrait | 8.0 × 10.0 | Poster figure |
| A4 portrait | 8.27 × 11.69 | Full page |
| Square | 6.0 × 6.0 | Social media |

## Common Plot Functions Quick Reference

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(8, 6))

# Bar
ax.bar(x, height, width=0.6, color='#dae8fc', edgecolor='#6c8ebf', linewidth=1)
ax.barh(y, width)  # horizontal

# Line
ax.plot(x, y, color='#6c8ebf', linewidth=2, linestyle='-', marker='o', markersize=5, label='Series')

# Scatter
ax.scatter(x, y, s=50, c=values, cmap='viridis', alpha=0.7, edgecolors='white')

# Fill Between
ax.fill_between(x, y-std, y+std, color='#dae8fc', alpha=0.3)

# Heatmap
import seaborn as sns
sns.heatmap(data, annot=True, fmt='.2f', cmap='coolwarm', square=True, ax=ax)

# Histogram
ax.hist(data, bins=30, color='#dae8fc', edgecolor='#6c8ebf', alpha=0.7)

# Box plot
ax.boxplot(data, patch_artist=True, boxprops=dict(facecolor='#dae8fc'))

# Horizontal line
ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

# Labels and grid
ax.set_xlabel('X Label', fontsize=12)
ax.set_ylabel('Y Label', fontsize=12)
ax.set_title('Title', fontsize=14, fontweight='bold')
ax.legend(loc='best', frameon=True, fancybox=True)
ax.grid(True, alpha=0.3, linestyle='--')

# Save
plt.tight_layout()
plt.savefig('output.pdf', dpi=300, bbox_inches='tight')
plt.savefig('output.png', dpi=300, bbox_inches='tight')
plt.close()
```

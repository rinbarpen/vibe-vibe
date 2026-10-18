---
name: matplotlib
description: Programmatic data visualization with Python matplotlib. Bar charts, line charts, scatter plots, heatmaps, error bars, subplots. Publication-quality figures with precise control. Best for data-driven charts and statistical visualizations.
---

# Matplotlib

Programmatic data visualization in Python. Publication-quality charts with precise control over every element.

## When to Use

- Data charts from code (bar, line, scatter, heatmap)
- Publication-quality figures (IEEE/ACM/journal requirements)
- Statistical visualizations (error bars, confidence intervals, box plots)
- Custom chart types not available in Mermaid
- When you need pixel-level control

**Not for**: quick inline charts (use [mermaid](../mermaid/SKILL.md) pie), architecture diagrams (use [mermaid](../mermaid/SKILL.md)).

For a supplied scientific panel image that needs reproducible code reconstruction, consult [NaturePanelForge](https://github.com/littlepeachs/NaturePanelForge) and its `codex-panel-reproduce` workflow. For a new chart, retain the user's actual data as the source of values; use the reference panel only for chart type, visual encoding, layout, and styling.

## Quick Start

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, label='sin(x)', color='#dae8fc', linewidth=2)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sine Wave')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('chart.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Chart Types

| Type | Function | Use |
|------|----------|-----|
| Line | `plt.plot()` | Trends, time series |
| Bar | `plt.bar()`, `plt.barh()` | Comparisons |
| Scatter | `plt.scatter()` | Correlations |
| Heatmap | `plt.imshow()`, `sns.heatmap()` | Matrices, attention |
| Histogram | `plt.hist()` | Distributions |
| Box plot | `plt.boxplot()` | Statistical spread |
| Pie | `plt.pie()` | Proportions (use sparingly) |
| Error bars | `plt.errorbar()` | Uncertainties |
| Stacked area | `plt.stackplot()` | Cumulative trends |
| Subplots | `plt.subplots()` | Multi-panel figures |

## Publication Settings

```python
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.family': 'serif',
})
```

### Chinese Font Support
```python
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False
```

## Templates

```
Bar chart:
  Plot a grouped bar chart comparing [metric] across [N groups]. [Group A], [Group B], [Group C] for each. Error bars from std. Grayscale for print, seaborn palette for slides. Save as PDF 300 DPI.

Line chart:
  Plot [metric] over [x-axis range]. [N] series: [series names]. Dashed lines for baselines, solid for ours. Markers at data points. Legend, grid, tight layout.

Scatter:
  Scatter plot of [x] vs [y], color-coded by [category]. Add trend line (linear regression). Annotate outliers. Square aspect ratio if comparing same-scale metrics.

Heatmap:
  Heatmap of [matrix/data]. Annotate values in cells. Diverging colormap (coolwarm/RdBu). Colorbar label. Square cells.

Multi-panel:
  [N] subplots in [layout]. Each showing [content]. Shared axes where applicable. Single figure caption. Combined PDF 300 DPI.
```

## Tool Selection

| Need | Tool |
|------|------|
| Precise data from code | matplotlib |
| Quick chart in markdown | [mermaid](../mermaid/SKILL.md) |
| Stylized custom diagram | [mermaid](../mermaid/SKILL.md) |
| IEEE publication figure | matplotlib (data), drawio (architecture) |
| Chinese journal | matplotlib + SimHei font |

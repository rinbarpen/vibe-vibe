# Matplotlib Prompt Templates

---

## Bar Chart

### Grouped Bar
```
Generate a matplotlib grouped bar chart:
Data: [Group1] = [values], [Group2] = [values], [Group3] = [values].
X-axis: [label1], [label2], [label3]. Y-axis: "[metric]".
Groups: [series names]. Error bars from std across [N] runs.
Colors: ['#dae8fc', '#d5e8d4', '#fff2cc'] or grayscale for print.
Font: serif 12pt. Grid: y-axis, alpha 0.3. Legend top-right.
Save as PDF 300 DPI. Tight layout.
```

### Horizontal Bar
```
Generate a matplotlib horizontal bar chart:
Categories: [list]. Values: [list]. Sort descending.
Single color #dae8fc. Value labels at bar tips.
Minimal grid. Clean sans-serif font. Save PNG 300 DPI.
```

---

## Line Chart

### Single/Multi Series
```
Generate a matplotlib line chart:
X-axis: [range]. Series: [name1] = [values], [name2] = [values].
Line styles: solid, dashed, dotted. Markers: o, s, ^ (every 5th point).
Colors: distinguishable palette. Legend: [position].
Grid: major + minor, alpha 0.3. Annotate key points.
Font: serif 12pt. Save PDF 300 DPI + PNG for slides.
```

### With Confidence Interval
```
Generate a matplotlib line chart with CI:
X-axis: [range]. Y-mean: [values]. Y-std: [values].
Plot line in solid #6c8ebf. Fill between ±1 std in light #dae8fc alpha 0.3.
Legend: mean, ±1 std. Grid on. PubMed-quality, serif 12pt. PDF 300 DPI.
```

---

## Scatter Plot

### Basic Scatter
```
Generate a matplotlib scatter plot:
X: [values], Y: [values]. Point color coded by [category column].
Colormap: viridis/coolwarm/RdBu. Alpha 0.7. Point size proportional to [z column].
Add trend line (linear regression, dashed). Annotate [N] outliers.
Colorbar label. Square aspect ratio. Save PDF 300 DPI.
```

---

## Heatmap

### Matrix / Correlation
```
Generate a matplotlib heatmap:
Data: [N]×[M] matrix of [description].
Colormap: coolwarm (diverging). Annotate values in cells (fmt='.2f').
Row labels: [list]. Column labels: [list].
Colorbar with label "[units]". Square cells, tight layout.
Save PDF 300 DPI.
```

### Confusion Matrix
```
Generate a confusion matrix:
Data: [matrix values]. Row labels: [predicted classes]. Col labels: [true classes].
Annotate counts + percentages. Blues colormap (sequential).
X-label: Predicted, Y-label: Actual. Save PDF 300 DPI.
```

---

## Statistical

### Box Plot
```
Generate a matplotlib box plot:
Data: [list of arrays for each group]. Labels: [group names].
Show outliers as dots. Fill light #dae8fc. Median line red.
Grid y-axis. Font: 12pt. Save PDF 300 DPI.
```

### Error Bar
```
Generate a matplotlib error bar chart:
X: [categories]. Y: [means]. Yerr: [std or CI].
fmt='o' markers, capsize=5, capthick=1. Line #6c8ebf.
Add horizontal reference line at [value] (dashed, gray).
Save PDF 300 DPI.
```

---

## Multi-Panel

### Subplot Grid
```
Generate [N]×[M] matplotlib subplots:
Figsize: [width]×[height] inches.
[Describe each subplot content].
Shared X-axis on column, shared Y-axis on row.
Single figure title. Combined legend.
Save PDF 300 DPI. Tight layout with hspace/wspace.
```

---

## Publication Settings

```
matplotlib rcParams for [journal]:
font.family: serif (English) / SimHei (Chinese)
font.size: 12 (labels), 14 (title)
figure.dpi: 300
savefig.dpi: 300
savefig.bbox: tight
axes.linewidth: 1.0
axes.grid: True, alpha 0.3
```

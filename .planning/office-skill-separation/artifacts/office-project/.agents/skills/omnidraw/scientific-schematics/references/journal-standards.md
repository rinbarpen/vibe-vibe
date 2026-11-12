# Journal Standards for Scientific Schematics

## Journal-Specific Requirements

| Journal | Style | Color | Font | Format | Notes |
|---------|-------|-------|------|--------|-------|
| Nature | Minimal, clean | Limited palette, color-OK | Sans-serif, consistent sizing | Vector (PDF/EPS) | No figure number in image |
| Science | Clean, high-contrast | Color-OK | Bold labels | Vector | 1-column or 2-column width |
| Cell | Refined, controlled | Color-OK, restrained | Clear, readable | Vector | Graphical abstract style |
| PNAS | Professional, clear | Color-OK, grayscale-compatible | Sans-serif | Vector | Accessible to broad audience |
| eLife | Modern, clean | Color-OK | Sans-serif | Vector | Figure + figure supplement |
| PLOS | Accessible | Color-blind safe | Sans-serif | Vector (PDF) | CC-BY license |
| IEEE | Traditional | Grayscale preferred | Serif or sans-serif | EPS/PDF | LaTeX integration |
| ACM | Clean, digital | Color-OK | Sans-serif | PDF/PNG | Single column |
| Elsevier | Journal-specific | Usually color-OK | Journal-specific | TIFF/EPS/PDF | Check guide for authors |

## Chinese Journals

| Journal | Style | Font | Format | Notes |
|---------|-------|------|--------|-------|
| 中国科学 | 学术规范 | 宋体 | EPS/PDF | 中英双语标注 |
| 计算机学报 | 清晰专业 | 宋体 | EPS/PDF | 双语图题 |
| 电子学报 | 学术规范 | 宋体 | EPS/PDF | — |
| 软件学报 | 现代清晰 | 宋体 | PDF/SVG | — |
| 自动化学报 | 学术规范 | 宋体 | EPS/PDF | — |

## Resolution & Export

| Use | Minimum DPI | Format | Color Space |
|-----|------------|--------|-------------|
| Print publication | 300 DPI | PDF/EPS/TIFF | CMYK |
| Online publication | 150 DPI | PNG/JPEG | RGB |
| Figure supplement | 300 DPI | PDF | RGB/CMYK |
| Peer review | 150 DPI | PDF/PNG | RGB |
| Presentation | 150 DPI | PNG | RGB |

## General Best Practices

### Color
- Use color-blind safe palettes (Okabe-Ito, Viridis)
- Ensure grayscale compatibility (test in B&W)
- Limit to 4-6 distinct colors per figure
- Consistent palette across all figures in paper

### Typography
- Sans-serif for schematics (Arial, Helvetica, DejaVu Sans)
- Serif for data charts (matching journal body font)
- Minimum 8pt after scaling to print size
- Consistent font sizing within and across figures

### Labeling
- Use panel letters (A, B, C...) for multi-panel figures
- Keep labels outside the figure area
- Use arrows/callouts for pointing to specific features
- Consistent abbreviation usage

### Export Checklist
- [ ] Minimum resolution met
- [ ] Fonts embedded (for PDF/EPS)
- [ ] Colors converted to correct space (CMYK for print)
- [ ] Figure dimensions match journal requirements
- [ ] All labels readable at print size
- [ ] No raster artifacts in vector figures

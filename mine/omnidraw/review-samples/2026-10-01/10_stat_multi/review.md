# Review — 10_stat_multi

- Execution: `python generate_data.py` deterministically writes `data.csv`; `python render.py` derives errors and emits `stat_multi.png` / `stat_multi.pdf` at 300 DPI for raster output.
- Data: 3 water conditions × 12 paired synthetic cases, with reference, baseline, and corrected estimate columns. Panel A is absolute error, points and diamond mean ± sample SD. Panel B is signed error, points and Tukey box (median, IQR, whiskers to 1.5×IQR). No statistical significance claim.
- Visual inspection: panel lettering, units, zero reference line, condition labels, and method legend are readable. Initial review found a footer colliding with the x-axis title; removed that footer and documented chart grammar here; final PNG is clear.
- Limitations: simulated cases were drawn from deliberately different noise scales, so the displayed improvement is built into the example rather than evidence of a real method. Clear-condition estimates can be clamped to zero by the generator. NaturePanelForge panel-to-code was not used because no target panel image was supplied.

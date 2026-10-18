# Review — 09_stat_single

- Execution: `python render.py` reads `data.csv` and emits `stat_single.png` / `stat_single.pdf` at 300 DPI for raster output.
- Data: 7 nominal turbidity levels × 5 synthetic replicates. Error bars are sample SD (ddof=1), calculated directly from CSV; raw points are overlaid. No fitted calibration equation, p-values, or confidence intervals.
- Visual inspection: monotonic simulated response visible, axis labels and units readable, error bars present. Initial footer approached the x-axis title; increased bottom margin and shortened footer; final PNG has clear spacing.
- Limitations: nominal NTU level is a turbidity standard, not a mass concentration; the diagram does not establish a validated calibration curve or detection limit. NaturePanelForge panel-to-code was not used because there was no input panel image.

"""Deterministic synthetic data generator; no physical measurements."""
from pathlib import Path
import csv
import numpy as np
O=Path(__file__).resolve().parent
rng=np.random.default_rng(20261001)
conditions=[('Clear',2.0,0.85,0.42),('Moderate',30.0,2.7,1.25),('High',90.0,7.2,3.6)]
with (O/'data.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['condition','replicate','reference_NTU','baseline_NTU','corrected_NTU'])
    for name,center,base_sd,new_sd in conditions:
        for rep in range(1,13):
            reference=max(0,center+rng.normal(0,center*.025))
            base=max(0,reference+rng.normal(.45*base_sd,base_sd))
            corrected=max(0,reference+rng.normal(.15*new_sd,new_sd))
            w.writerow([name,rep,*[f'{v:.3f}' for v in (reference,base,corrected)]])

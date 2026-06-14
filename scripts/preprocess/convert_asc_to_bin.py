#!/usr/bin/env python3
# =============================================================================
# Author: M. El Aabaribaoune (@UM6P)
# Date:   2026-06-07
# =============================================================================
import numpy as np

# Read the ASCII file
with open('data/land_params/GMIA/gmia_v5_aei_pct.asc', 'r') as f:
    lines = f.readlines()

header = {}
data = []
for line in lines:
    parts = line.strip().split()
    if len(parts) == 2 and not parts[0].replace('.','',1).isdigit() and not parts[0].startswith('-'):
        header[parts[0].lower()] = float(parts[1])
    else:
        data.extend([float(x) for x in parts])

data = np.array(data, dtype=np.float32)

# Save to binary
data.tofile('data/land_params/GMIA/gmia_v5_aei_pct.bin')
print(f"Header: {header}")
print(f"Data shape: {data.shape}")

#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Script: download_gmia.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# =============================================================================
# Date:   2026-06-07
# =============================================================================
import os
import urllib.request
import zipfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
DEST_DIR = os.path.join(BASE_DIR, 'data/land_params/GMIA')
os.makedirs(DEST_DIR, exist_ok=True)

urls = [
    ("gmia_v5_aei_pct_asc.zip", "https://firebasestorage.googleapis.com/v0/b/fao-aquastat.appspot.com/o/GIS%2Fgmia_v5_aei_pct_asc.zip?alt=media&token=c81b6711-bc6e-44cb-acb2-297eb09cebc1"),
    ("gmia_v5_aei_ha_asc.zip", "https://firebasestorage.googleapis.com/v0/b/fao-aquastat.appspot.com/o/GIS%2Fgmia_v5_aei_ha_asc.zip?alt=media&token=b9000dbd-efd9-432a-bc9f-9cd26eb2a865")
]

for filename, url in urls:
    filepath = os.path.join(DEST_DIR, filename)
    print(f"Downloading {filename} ...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Extracting {filename} ...")
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(DEST_DIR)
        print(f"Successfully processed {filename}")
    except Exception as e:
        print(f"Failed to process {filename}: {e}")

print("Done.")

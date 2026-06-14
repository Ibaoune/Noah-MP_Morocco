#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
preprocess_smap_qc_regrid.py

Extracts soil moisture, applies QC flags, regrids to 0.01°, and prepares files
for CDF matching / bias correction.
"""

import os
import glob
import logging

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/observations/SMAP_SPL3SMP_E/raw')
QC_DIR = os.path.join(BASE_DIR, 'data/observations/SMAP_SPL3SMP_E/qc')
REGRID_DIR = os.path.join(BASE_DIR, 'data/observations/SMAP_SPL3SMP_E/regridded')
BIAS_CORRECT_DIR = os.path.join(BASE_DIR, 'data/observations/SMAP_SPL3SMP_E/bias_corrected')

os.makedirs(QC_DIR, exist_ok=True)
os.makedirs(REGRID_DIR, exist_ok=True)
os.makedirs(BIAS_CORRECT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/preprocess/preprocess_smap.log')),
        logging.StreamHandler()
    ]
)

def apply_qc(raw_file, qc_path):
    # TODO: Implement SMAP HDF5 QC extraction
    # e.g., Filter out frozen ground, VWC > 5 kg/m2, surface water fraction
    with open(qc_path, 'w') as f:
        f.write("DUMMY QC DATA")

def regrid_smap(qc_path, regrid_path):
    # TODO: Implement regridding to 0.01 degree using nearest neighbor or bilinear
    with open(regrid_path, 'w') as f:
        f.write("DUMMY REGRID DATA")

def placeholder_bias_correction(regrid_path, bias_path):
    # TODO: Implement CDF matching or anomaly rescaling
    with open(bias_path, 'w') as f:
        f.write("DUMMY BIAS CORRECTED DATA")

def main():
    logging.info("Starting SMAP preprocessing...")
    
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, '*.h5')))
    if not raw_files:
        logging.warning("No raw SMAP files found.")
        return
        
    for rf in raw_files:
        basename = os.path.basename(rf)
        date_str = basename.split('_')[5] # e.g. 20150401
        
        qc_path = os.path.join(QC_DIR, f"SMAP_QC_{date_str}.nc")
        regrid_path = os.path.join(REGRID_DIR, f"SMAP_REGRID_0.01_{date_str}.nc")
        bias_path = os.path.join(BIAS_CORRECT_DIR, f"SMAP_BC_{date_str}.nc")
        
        if not os.path.exists(qc_path):
            logging.info(f"Applying QC to {basename}")
            apply_qc(rf, qc_path)
            
        if not os.path.exists(regrid_path):
            logging.info(f"Regridding {basename}")
            regrid_smap(qc_path, regrid_path)
            
        if not os.path.exists(bias_path):
            logging.info(f"Bias Correcting {basename}")
            placeholder_bias_correction(regrid_path, bias_path)
            
    logging.info("SMAP preprocessing completed.")

if __name__ == "__main__":
    main()

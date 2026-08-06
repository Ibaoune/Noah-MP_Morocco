#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

"""
===============================================================================
Script Name   : download_gdas.py
Description   : Downloads GDAS meteorological forcings (excluding precipitation)
                for the Sebou-Saïss basin (Morocco). Used as an alternative 
                to MERRA-2.
Data Downloaded: GDAS/FNL Global Tropospheric Analyses (.sg files)
Data Version  : GDAS1 (NCAR RDA ds083.3)
Frequency     : 6-hourly with 3-hour forecasts (cycles 00Z, 06Z, 12Z, 18Z)
Resolution    : 0.25° x 0.25°
Source / Site : NASA NCCS Portal / NCAR RDA
Target Period : 2015-01-01 to 2020-12-31 (Customizable)
Author        : M. El Aabaribaoune (@um6p)
Date Updated  : 2026-06-11
===============================================================================
"""

import os
import sys
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2020, 12, 31)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/forcing/GDAS')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_gdas.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_gdas.log')),
        logging.StreamHandler()
    ]
)

def download_gdas_file(date_obj, cycle, output_dir, credentials=None):
    """
    Download GDAS forcing files from NASA NCCS portal.
    NASA hosts these as .sg (simple GRIB) files which LIS natively reads.
    We download f00 (instantaneous), f03 (3-hour average), and f06 (6-hour average).
    """
    date_str = date_obj.strftime("%Y%m%d")
    month_str = date_obj.strftime("%Y%m")
    
    # GDAS T1534 plugin expects data/forcing/GDAS/gdas.YYYYMMDD/
    gdas_folder = f"gdas.{date_str}"
    output_dir_day = os.path.join(output_dir, gdas_folder)
    os.makedirs(output_dir_day, exist_ok=True)
    
    forecast_hours = [0, 3, 6]
    overall_status = "Success"
    total_size = 0
    
    for fhr in forecast_hours:
        filename = f"{date_str}{cycle:02d}.gdas1.sfluxgrbf{fhr:02d}.sg"
        url = f"https://portal.nccs.nasa.gov/lisdata_pub/data/MET_FORCING/GDAS/{month_str}/{filename}"
        
        output_filename = f"gdas1.t{cycle:02d}z.sfluxgrbf{fhr:02d}"
        output_path = os.path.join(output_dir_day, output_filename)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            total_size += os.path.getsize(output_path)
            continue
        
        try:
            logging.info(f"Downloading {filename} as {output_filename}...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            total_size += os.path.getsize(output_path)
        except Exception as e:
            logging.error(f"Failed to download {url}: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            overall_status = "Failed"
            
    return f"gdas1.t{cycle:02d}z (00,03,06)", overall_status, total_size

def main():
    logging.info("Starting GDAS download workflow.")
    logging.warning("This script requires NCAR RDA authentication to download actual data.")
    
    current_date = START_DATE
    cycles = [0, 6, 12, 18]
    inventory_data = []
    
    while current_date <= END_DATE:
        for cycle in cycles:
            fname, status, size = download_gdas_file(current_date, cycle, RAW_DIR)
            
            inventory_data.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'cycle': f"{cycle:02d}Z",
                'file_name': fname,
                'file_size_mb': round(size / (1024 * 1024), 2),
                'status': status
            })
            
        current_date += timedelta(days=1)
        
    # Save inventory
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("GDAS workflow completed.")

if __name__ == "__main__":
    main()

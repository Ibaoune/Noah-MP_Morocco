#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
check_data_inventory.py

Scans all downloaded datasets and produces a data completeness report.
Outputs:
- reports/data_inventory_2015_2020.csv
- reports/data_completeness_2015_2020.md
"""

import os
import glob
import pandas as pd
from datetime import datetime, timedelta

# Configuration
START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2020, 12, 31)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')

CSV_OUT = os.path.join(REPORT_DIR, 'data_inventory_2015_2020.csv')
MD_OUT = os.path.join(REPORT_DIR, 'data_completeness_2015_2020.md')

def count_expected_daily():
    return (END_DATE - START_DATE).days + 1

def scan_directory(path, extension):
    files = glob.glob(os.path.join(path, f'*{extension}'))
    total_size_mb = sum(os.path.getsize(f) for f in files) / (1024*1024)
    return len(files), total_size_mb

def main():
    expected_daily = count_expected_daily()
    
    datasets = [
        {
            "name": "IMERG Precipitation",
            "path": os.path.join(DATA_DIR, 'forcing/IMERG/raw'),
            "ext": ".nc4",
            "expected": expected_daily,
            "version": "V07"
        },
        {
            "name": "GDAS Meteorological",
            "path": os.path.join(DATA_DIR, 'forcing/GDAS/raw'),
            "ext": ".grib2",
            "expected": expected_daily * 4, # 4 cycles per day
            "version": "Historical"
        },
        {
            "name": "SMAP SPL3SMP_E",
            "path": os.path.join(DATA_DIR, 'observations/SMAP_SPL3SMP_E/raw'),
            "ext": ".h5",
            "expected": expected_daily,
            "version": "V6"
        },
        {
            "name": "MODIS MCD15A2H",
            "path": os.path.join(DATA_DIR, 'observations/MODIS_MCD15A2H/raw'),
            "ext": ".hdf",
            "expected": expected_daily // 8, # 8-day product approx
            "version": "6.1"
        },
        {
            "name": "MODIS MOD16A2GF (Gap-Filled ET)",
            "path": os.path.join(DATA_DIR, 'validation/evapotranspiration/MOD16/raw'),
            "ext": ".hdf",
            "expected": expected_daily // 8, # 8-day product approx
            "version": "061"
        },
        {
            "name": "MODIS MOD17A2HGF (Gap-Filled GPP)",
            "path": os.path.join(DATA_DIR, 'validation/vegetation/GPP/raw'),
            "ext": ".hdf",
            "expected": expected_daily // 8, # 8-day product approx
            "version": "061"
        },
        {
            "name": "GRACE/GRACE-FO Mascon",
            "path": os.path.join(DATA_DIR, 'validation/water_storage/GRACE_GRACEFO/raw'),
            "ext": ".nc",
            "expected": 72, # Approx 1 file per month for 6 years
            "version": "RL06.1_v3"
        },
        {
            "name": "CGLS ASCAT Soil Moisture",
            "path": os.path.join(DATA_DIR, 'validation/soil_moisture/ASCAT/raw'),
            "ext": "_nc",
            "expected": expected_daily,
            "version": "v3.1.1"
        },
        {
            "name": "Copernicus LAI 300m",
            "path": os.path.join(DATA_DIR, 'validation/vegetation/Copernicus_LAI/raw'),
            "ext": "_nc",
            "expected": expected_daily // 10, # 10-day product approx
            "version": "v1.0.1/v2.0.1"
        }
    ]
    
    report_data = []
    
    for ds in datasets:
        count, size = scan_directory(ds['path'], ds['ext'])
        status = "Complete" if count >= ds['expected'] else "Incomplete"
        if count == 0:
            status = "Missing"
            
        report_data.append({
            "Dataset": ds['name'],
            "Version": ds['version'],
            "Expected Files": ds['expected'],
            "Downloaded Files": count,
            "Size (MB)": round(size, 2),
            "Status": status
        })
        
    df = pd.DataFrame(report_data)
    df.to_csv(CSV_OUT, index=False)
    
    # Write Markdown
    with open(MD_OUT, 'w') as f:
        f.write("# Data Completeness Report (2015-2020)\n\n")
        f.write("This report summarizes the status of the required datasets for the Sebou-Saïss Noah-MP experiments.\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n**Note**: The expected file count for MODIS is approximate due to its 8-day temporal resolution.\n")
        
    print(f"Inventory reports generated at:\n- {CSV_OUT}\n- {MD_OUT}")

if __name__ == "__main__":
    main()

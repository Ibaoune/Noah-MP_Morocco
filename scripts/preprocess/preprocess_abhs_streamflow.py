#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
preprocess_abhs_streamflow.py

Standardizes ABHS streamflow data from the provided metadata template and raw CSVs
into validation-ready daily/monthly files for LIS.
"""

import os
import logging
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
ABHS_DIR = os.path.join(BASE_DIR, 'data/validation/streamflow/ABHS')
META_TEMPLATE = os.path.join(ABHS_DIR, 'abhs_station_metadata_template.csv')

os.makedirs(ABHS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/preprocess/preprocess_abhs.log')),
        logging.StreamHandler()
    ]
)

def create_metadata_template():
    if not os.path.exists(META_TEMPLATE):
        df = pd.DataFrame({
            'station_name': [],
            'station_id': [],
            'latitude': [],
            'longitude': [],
            'drainage_area_km2': [],
            'river_name': [],
            'period_available': [],
            'temporal_resolution': [],
            'units': [],
            'quality_flag': [],
            'notes_dams_irrigation': []
        })
        df.to_csv(META_TEMPLATE, index=False)
        logging.info(f"Created metadata template at {META_TEMPLATE}")

def main():
    logging.info("Starting ABHS Streamflow preprocessing...")
    
    create_metadata_template()
    
    # Process actual data if available
    raw_files = [f for f in os.listdir(ABHS_DIR) if f.endswith('.csv') and 'metadata' not in f]
    
    for rf in raw_files:
        logging.info(f"Processing raw streamflow file {rf}")
        # TODO: Implement generic reading logic that standardizes Date and Streamflow(m3/s) columns
        # TODO: Output to a NetCDF or standardized CSV for validation metrics calculation.
        pass
        
    logging.info("ABHS preprocessing completed.")

if __name__ == "__main__":
    main()

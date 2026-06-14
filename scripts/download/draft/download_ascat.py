#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

import os
import requests
import json
import logging
import pandas as pd
from datetime import datetime
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import argparse

parser = argparse.ArgumentParser(description="Download ASCAT data")
parser.add_argument('--start_date', type=str, default="2015-01-01", help='Start date YYYY-MM-DD')
parser.add_argument('--end_date', type=str, default="2020-12-31", help='End date YYYY-MM-DD')
args = parser.parse_args()

START_DATE = args.start_date
END_DATE = args.end_date
USERNAME = "mohammad.trop1@gmail.com"
PASSWORD = "pip123@ZOHMKA"

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
TARGET_DIR = os.path.join(DATA_DIR, 'validation/soil_moisture/ASCAT/raw')
REPORT_DIR = os.path.join(DATA_DIR, 'reports')

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def get_token():
    token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    data = {
        "client_id": "cdse-public",
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def download_file(url, token, target_path):
    headers = {"Authorization": f"Bearer {token}"}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(target_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

def main():
    logging.info("Starting Copernicus ASCAT Soil Moisture download workflow.")
    
    try:
        logging.info("Authenticating with CDSE...")
        token = get_token()
        logging.info("Successfully authenticated with CDSE.")
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return

    # OData API Query
    start_dt = f"{START_DATE}T00:00:00.000Z"
    end_dt = f"{END_DATE}T23:59:59.000Z"
    
    base_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    filter_query = f"?$filter=contains(Name,'c_gls_SWI_') and contains(Name,'_nc') and ContentDate/Start ge {start_dt} and ContentDate/Start le {end_dt}&$top=1000"
    search_url = base_url + filter_query
    
    logging.info(f"Searching for ASCAT SWI from {START_DATE} to {END_DATE}...")
    
    products = []
    while search_url:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        products.extend(data.get('value', []))
        search_url = data.get('@odata.nextLink', None)
        
    logging.info(f"Found {len(products)} granules.")
    
    if not products:
        return
        
    inventory_data = []
    
    logging.info(f"Downloading to {TARGET_DIR}...")
    
    for p in tqdm(products, desc="Downloading ASCAT"):
        uuid = p['Id']
        fname = p['Name']
        date_str = p['ContentDate']['Start']
        target_path = os.path.join(TARGET_DIR, fname)
        
        status = "Success"
        if os.path.exists(target_path):
            logging.info(f"File {fname} already downloaded")
        else:
            download_url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({uuid})/$value"
            try:
                # Refresh token periodically if downloading many files to prevent expiry
                token = get_token() 
                download_file(download_url, token, target_path)
            except Exception as e:
                logging.error(f"Failed to download {fname}: {e}")
                status = f"Failed: {e}"
                
        size = os.path.getsize(target_path) / (1024 * 1024) if os.path.exists(target_path) else 0
        
        inventory_data.append({
            'date': date_str,
            'file_name': fname,
            'product': 'ASCAT_SWI',
            'file_size_mb': round(size, 2),
            'status': status
        })

    logging.info("Building inventory...")
    df = pd.DataFrame(inventory_data)
    inventory_file = os.path.join(REPORT_DIR, 'inventory_ascat.csv')
    df.to_csv(inventory_file, index=False)
    logging.info(f"Inventory saved to {inventory_file}")
    logging.info("ASCAT workflow completed.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)
#
# Download MODIS LAI MOD15A2H tile h17v05 from Earthdata for Morocco domain

import os
import requests
import sys
from datetime import datetime, timedelta

# Configurations
START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2020, 12, 31)
OUT_DIR = "data/observations/MODIS_LAI"
TILE = "h17v05"


# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# NASA CMR API URL
CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

# Session with Earthdata Login
session = requests.Session()
session.auth = ("el.aabaribaoune@gmail.com", "mohkaj111@ZO")

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        try:
            r = session.head(url, verify=True, allow_redirects=True)
            remote_size = int(r.headers.get('content-length', 0))
            local_size = os.path.getsize(dest_path)
            if remote_size == local_size and local_size > 0:
                print(f"[SKIP] Already downloaded: {os.path.basename(dest_path)}")
                return
        except Exception:
            pass

    print(f"[DOWNLOADING] {url} -> {dest_path}")
    response = session.get(url, stream=True, verify=True)
    if response.status_code == 401:
        print("[ERROR] Unauthorized. Check Earthdata credentials.", file=sys.stderr)
        return
    response.raise_for_status()
    
    total_length = int(response.headers.get('content-length', 0))
    dl = 0
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                dl += len(chunk)
                if total_length > 0 and dl % (65536*10) == 0:
                    percent = 100 * dl / total_length
                    sys.stdout.write(f"\rProgress: {percent:.1f}% ({dl/(1024*1024):.1f} MB / {total_length/(1024*1024):.1f} MB)")
                    sys.stdout.flush()
    sys.stdout.write("\n")
    print(f"[COMPLETE] {os.path.basename(dest_path)}")

if __name__ == "__main__":
    print(f"Querying CMR for MODIS LAI granules (MOD15A2H version 061) tile {TILE} from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}...")
    
    # Query all granules in the date range for the specified tile
    t_start = START_DATE.strftime("%Y-%m-%dT%H:%M:%SZ")
    t_end = END_DATE.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # MODIS LAI granules are grouped by date. We query in pages.
    page_num = 1
    granules_found = []
    
    while True:
        params = {
            "short_name": "MOD15A2H",
            "version": "061",
            "temporal": f"{t_start},{t_end}",
            "readable_granule_name[]": f"*{TILE}*",
            "options[readable_granule_name][pattern]": "true",
            "page_size": 200,
            "page_num": page_num
        }

        
        try:
            r = requests.get(CMR_URL, params=params).json()
            entries = r.get("feed", {}).get("entry", [])
            if not entries:
                break
            granules_found.extend(entries)
            page_num += 1
            if len(entries) < 200:
                break
        except Exception as e:
            print(f"[ERROR] Failed to query CMR on page {page_num}: {e}", file=sys.stderr)
            break
            
    print(f"Found {len(granules_found)} granules for tile {TILE}.")
    
    for idx, entry in enumerate(granules_found):
        granule_name = entry.get("title", "")
        # Find the HDF file link
        hdf_url = None
        for link in entry.get("links", []):
            href = link.get("href", "")
            if "http" in href and href.endswith(".hdf") and "protected" in href:
                hdf_url = href
                break
        
        if hdf_url:
            dest_file = os.path.join(OUT_DIR, os.path.basename(hdf_url))
            try:
                print(f"\n[Granule {idx+1}/{len(granules_found)}] {granule_name}")
                download_file(hdf_url, dest_file)
            except Exception as e:
                print(f"[ERROR] Failed downloading {granule_name}: {e}", file=sys.stderr)
        else:
            print(f"[WARN] No HDF link found for granule: {granule_name}")
            
    print("\nMODIS LAI download process complete.")

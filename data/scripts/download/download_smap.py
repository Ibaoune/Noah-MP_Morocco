#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

import os
import requests
import sys
from datetime import datetime, timedelta

# Configurations
START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2020, 12, 31)
OUT_DIR = "data/observations/SMAP/SPL3SMP.009"


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
    print(f"Querying CMR for SMAP L3 Soil Moisture granules (SPL3SMP version 009) from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}...")
    
    current_date = START_DATE
    while current_date <= END_DATE:
        yr = current_date.strftime("%Y")
        mo = current_date.strftime("%m")
        day = current_date.strftime("%d")
        date_str = f"{yr}-{mo}-{day}"
        
        # Format temporal range for this single day
        t_start = f"{date_str}T00:00:00Z"
        t_end = f"{date_str}T23:59:59Z"
        
        params = {
            "short_name": "SPL3SMP",
            "version": "009",
            "temporal": f"{t_start},{t_end}",
            "page_size": 5
        }
        
        try:
            r = requests.get(CMR_URL, params=params).json()
            entries = r.get("feed", {}).get("entry", [])
            
            if not entries:
                print(f"[WARN] No SMAP granule found for date {date_str}")
            else:
                # Find the H5 file link
                h5_url = None
                for entry in entries:
                    for link in entry.get("links", []):
                        href = link.get("href", "")
                        if "http" in href and href.endswith(".h5") and "protected" in href:
                            h5_url = href
                            break
                    if h5_url:
                        break
                        
                if h5_url:
                    # Create daily subdirectory YYYY.MM.DD
                    day_dir = f"{OUT_DIR}/{yr}.{mo}.{day}"
                    os.makedirs(day_dir, exist_ok=True)
                    
                    # Target filename expected by LIS
                    dest_file = f"{day_dir}/SMAP_L3_SM_P_{yr}{mo}{day}.h5"
                    download_file(h5_url, dest_file)
                else:
                    print(f"[WARN] No H5 download link found for date {date_str}")
        except Exception as e:
            print(f"[ERROR] Failed on date {date_str}: {e}", file=sys.stderr)
            
        current_date += timedelta(days=1)
        
    print("SMAP observations download complete.")

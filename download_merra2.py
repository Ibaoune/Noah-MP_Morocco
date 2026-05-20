#!/usr/bin/env python3
import os
import requests
import sys
from datetime import datetime, timedelta

# Configurations
START_DATE = datetime(2020, 6, 1)
END_DATE = datetime(2020, 8, 31)
OUT_DIR = "input/MET_FORCING/MERRA2"

# Ensure directories exist
os.makedirs(f"{OUT_DIR}/M2T1NXFLX", exist_ok=True)
os.makedirs(f"{OUT_DIR}/M2T1NXSLV", exist_ok=True)

# NASA GES DISC URLs
BASE_FLX_URL = "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2T1NXFLX.5.12.4"
BASE_SLV_URL = "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2T1NXSLV.5.12.4"

# User credentials from netrc will be used automatically by requests,
# but we can also set up a session to handle redirects correctly.
session = requests.Session()
session.auth = ("el.aabaribaoune@gmail.com", "mohkaj111@ZO")

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        # Quick size check
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
    # Earthdata redirect dance
    response = session.get(url, stream=True, verify=True)
    if response.status_code == 401:
        print("[ERROR] Unauthorized. Check your Earthdata credentials in download_merra2.py or .netrc.", file=sys.stderr)
        return
        
    response.raise_for_status()
    total_length = int(response.headers.get('content-length', 0))
    dl = 0
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                dl += len(chunk)
                if total_length > 0 and dl % (65536*100) == 0:
                    percent = 100 * dl / total_length
                    sys.stdout.write(f"\rProgress: {percent:.1f}% ({dl/(1024*1024):.1f} MB / {total_length/(1024*1024):.1f} MB)")
                    sys.stdout.flush()
    sys.stdout.write("\n")
    print(f"[COMPLETE] {os.path.basename(dest_path)}")

if __name__ == "__main__":
    print(f"Starting MERRA-2 download from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}...")
    
    current_date = START_DATE
    while current_date <= END_DATE:
        yr = current_date.strftime("%Y")
        mo = current_date.strftime("%m")
        day = current_date.strftime("%d")
        date_str = f"{yr}{mo}{day}"
        
        # 1. Surface Fluxes (M2T1NXFLX)
        flx_filename = f"MERRA2_400.tavg1_2d_flx_Nx.{date_str}.nc4"
        flx_url = f"{BASE_FLX_URL}/{yr}/{mo}/{flx_filename}"
        flx_dest = f"{OUT_DIR}/M2T1NXFLX/{flx_filename}"
        
        try:
            download_file(flx_url, flx_dest)
        except Exception as e:
            print(f"[ERROR] Failed to download FLX for {date_str}: {e}", file=sys.stderr)
            
        # 2. Single-level Met (M2T1NXSLV)
        slv_filename = f"MERRA2_400.tavg1_2d_slv_Nx.{date_str}.nc4"
        slv_url = f"{BASE_SLV_URL}/{yr}/{mo}/{slv_filename}"
        slv_dest = f"{OUT_DIR}/M2T1NXSLV/{slv_filename}"
        
        try:
            download_file(slv_url, slv_dest)
        except Exception as e:
            print(f"[ERROR] Failed to download SLV for {date_str}: {e}", file=sys.stderr)
            
        current_date += timedelta(days=1)
        
    print("MERRA-2 forcing download complete.")

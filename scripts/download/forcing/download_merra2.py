#!/usr/bin/env python3
"""
===============================================================================
Script Name   : download_merra2.py
Description   : 
  Part 1: Iterates over the requested time period day by day.
  Part 2: Constructs direct HTTP URLs for three MERRA-2 global collections:
          M2T1NXFLX (Fluxes), M2T1NXSLV (Met), and M2T1NXRAD (Radiation).
  Part 3: Authenticates via NASA GES DISC and downloads the global NetCDF files.
  Note on Subsetting: No spatial subsetting is performed in this script. 
                      The downloaded files are global. LIS natively reads these 
                      global files and automatically performs internal spatial 
                      subsetting and interpolation for the configured domain at runtime.
Data Downloaded: M2T1NXFLX, M2T1NXSLV, M2T1NXRAD
Data Version  : 5.12.4
Frequency     : Hourly (1 hour)
Resolution    : 0.5° x 0.625°
Source / Site : NASA GES DISC (via `requests` API)
Target Period : 2000-01-01 to 2023-12-31
Author        : M. El Aabaribaoune (@um6p)
Date Updated  : 2026-06-11
===============================================================================
"""

import os
import requests
import sys
from datetime import datetime, timedelta

import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Download MERRA-2 data")
parser.add_argument('--start', type=str, default="2000-01-01", help="Start date (YYYY-MM-DD)")
parser.add_argument('--end', type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")
args = parser.parse_args()

# Configurations
START_DATE = datetime.strptime(args.start, "%Y-%m-%d")
END_DATE = datetime.strptime(args.end, "%Y-%m-%d")

# Define root paths based on script location so it can be run from anywhere
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
OUT_DIR = os.path.join(BASE_DIR, "data/forcing/MERRA2")


# Ensure the output directories for each variable exist
os.makedirs(f"{OUT_DIR}/M2T1NXFLX", exist_ok=True)
os.makedirs(f"{OUT_DIR}/M2T1NXSLV", exist_ok=True)
os.makedirs(f"{OUT_DIR}/M2T1NXRAD", exist_ok=True)

# NASA GES DISC Base URLs for the different collections
BASE_FLX_URL = "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2T1NXFLX.5.12.4"
BASE_SLV_URL = "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2T1NXSLV.5.12.4"
BASE_RAD_URL = "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2T1NXRAD.5.12.4"

# Set up an HTTP session with Earthdata credentials to handle redirects
session = requests.Session()
session.auth = ("el.aabaribaoune@gmail.com", "mohkaj111@ZO")

def download_file(url, dest_path):
    """
    Downloads a single file from the given URL and saves it to dest_path.
    It checks the remote file size against the local file size to skip 
    already downloaded files.
    """
    if os.path.exists(dest_path):
        # Quick size check to avoid re-downloading
        try:
            r = session.head(url, verify=True, allow_redirects=True)
            remote_size = int(r.headers.get('content-length', 0))
            local_size = os.path.getsize(dest_path)
            if remote_size == local_size and local_size > 0:
                print(f"[SKIP] Already downloaded: {os.path.basename(dest_path)}")
                return True
        except Exception:
            pass

    print(f"[DOWNLOADING] {url} -> {dest_path}")
    # Perform the GET request (handles Earthdata redirect dance)
    response = session.get(url, stream=True, verify=True)
    if response.status_code == 401:
        print("[ERROR] Unauthorized. Check your Earthdata credentials in download_merra2.py or .netrc.", file=sys.stderr)
        return False
    response.raise_for_status()
    
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        print(f"[ERROR] NASA returned an HTML page (auth or 404 issue) instead of data for {url}", file=sys.stderr)
        return False

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
    return True

if __name__ == "__main__":
    print(f"Starting MERRA-2 download from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}...")
    
    current_date = START_DATE
    failures = 0
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
            if not download_file(flx_url, flx_dest): failures += 1
        except Exception as e:
            print(f"[ERROR] Failed to download FLX for {date_str}: {e}", file=sys.stderr)
            failures += 1
            
        # 2. Single-level Met (M2T1NXSLV)
        slv_filename = f"MERRA2_400.tavg1_2d_slv_Nx.{date_str}.nc4"
        slv_url = f"{BASE_SLV_URL}/{yr}/{mo}/{slv_filename}"
        slv_dest = f"{OUT_DIR}/M2T1NXSLV/{slv_filename}"
        
        try:
            if not download_file(slv_url, slv_dest): failures += 1
        except Exception as e:
            print(f"[ERROR] Failed to download SLV for {date_str}: {e}", file=sys.stderr)
            failures += 1

        # 3. Radiation (M2T1NXRAD) — required by LIS MERRA2 reader
        rad_filename = f"MERRA2_400.tavg1_2d_rad_Nx.{date_str}.nc4"
        rad_url = f"{BASE_RAD_URL}/{yr}/{mo}/{rad_filename}"
        rad_dest = f"{OUT_DIR}/M2T1NXRAD/{rad_filename}"
        
        try:
            if not download_file(rad_url, rad_dest): failures += 1
        except Exception as e:
            print(f"[ERROR] Failed to download RAD for {date_str}: {e}", file=sys.stderr)
            failures += 1
            
        current_date += timedelta(days=1)
        
    print("MERRA-2 forcing download complete.")
    if failures > 0:
        print(f"[CRITICAL] {failures} downloads failed! Exiting with status 1.", file=sys.stderr)
        sys.exit(1)

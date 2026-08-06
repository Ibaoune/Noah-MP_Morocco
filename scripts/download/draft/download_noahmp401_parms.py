#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)

import os
import requests
import sys

BASE_URL = "https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS/noahmp401_parms"
OUT_DIR = "data/land_params/noahmp401_parms"

os.makedirs(OUT_DIR, exist_ok=True)

files_to_download = [
    "SOILPARM.TBL",
    "GENPARM.TBL",
    "MPTABLE.TBL",
    "VEGPARM.TBL"
]

def download_file(filename):
    url = f"{BASE_URL}/{filename}"
    dest_path = f"{OUT_DIR}/{filename}"
    
    if os.path.exists(dest_path):
        try:
            r = requests.head(url, verify=True)
            remote_size = int(r.headers.get('content-length', 0))
            local_size = os.path.getsize(dest_path)
            if remote_size == local_size and local_size > 0:
                print(f"[SKIP] Already downloaded: {filename}")
                return
        except Exception:
            pass
            
    print(f"[DOWNLOADING] {url} -> {dest_path}")
    with requests.get(url, stream=True, verify=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get('content-length', 0))
        dl = 0
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    dl += len(chunk)
                    if total_length > 0 and dl % (8192*100) == 0:
                        percent = 100 * dl / total_length
                        sys.stdout.write(f"\rProgress: {percent:.1f}%")
                        sys.stdout.flush()
    sys.stdout.write("\n")
    print(f"[COMPLETE] {filename}")

if __name__ == "__main__":
    print("Starting Noah-MP 4.0.1 parameters download...")
    for filename in files_to_download:
        try:
            download_file(filename)
        except Exception as e:
            print(f"[ERROR] Failed to download {filename}: {e}", file=sys.stderr)
    print("Download script complete.")

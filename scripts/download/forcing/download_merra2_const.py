#!/usr/bin/env python3
"""
===============================================================================
Script Name   : download_merra2_const.py
Description   : Downloads the static MERRA-2 geopotential terrain height 
                constants file. This is required for LIS/LDT topographic 
                'lapse-rate' correction.
Data Downloaded: MERRA2_101.const_2d_asm_Nx.00000000.nc4 (M2C0NXASM)
Data Version  : 5.12.4
Frequency     : Static (Time-invariant file)
Resolution    : 0.5° x 0.625°
Source / Site : NASA GES DISC (via `requests` API)
Author        : M. El Aabaribaoune (@um6p)
Date Updated  : 2026-06-11
Usage         : python3 download_merra2_const.py
===============================================================================
"""

import os
import sys
import requests

# -----------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
OUT_DIR   = os.path.join(BASE_DIR, "data/forcing/MERRA2/M2C0NXASM")
FILENAME  = "MERRA2_101.const_2d_asm_Nx.00000000.nc4"
BASE_URL  = "https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2_MONTHLY/M2C0NXASM.5.12.4/1980"

# Earthdata credentials  (same as download_merra2.py)
EARTHDATA_USER = "e" + "x"*20 + "@gmail.com"
EARTHDATA_PASS = "m" + "x"*8 + "O"

import netrc
try:
    netrc_info = netrc.netrc()
    EARTHDATA_USER, _, EARTHDATA_PASS = netrc_info.authenticators('urs.earthdata.nasa.gov')
except Exception as e:
    print(f"[ERROR] Could not read credentials from ~/.netrc: {e}", file=sys.stderr)
    print("Please ensure ~/.netrc exists with machine urs.earthdata.nasa.gov", file=sys.stderr)
    sys.exit(1)

# -----------------------------------------------------------------------

def download_file(url: str, dest_path: str) -> None:
    """Download a single file with Earthdata authentication and resume check."""
    session = requests.Session()
    session.auth = (EARTHDATA_USER, EARTHDATA_PASS)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Skip if already downloaded and size matches
    if os.path.exists(dest_path):
        try:
            r = session.head(url, verify=True, allow_redirects=True)
            remote_size = int(r.headers.get("content-length", 0))
            local_size  = os.path.getsize(dest_path)
            if remote_size > 0 and remote_size == local_size:
                print(f"[SKIP] Already downloaded: {os.path.basename(dest_path)} ({local_size/(1024*1024):.1f} MB)")
                return
            else:
                print(f"[REDOWNLOAD] Size mismatch (local={local_size}, remote={remote_size}). Re-downloading.")
        except Exception as e:
            print(f"[WARN] Could not verify remote size: {e}. Proceeding with download.")

    print(f"[DOWNLOADING] {url}")
    print(f"         --> {dest_path}")

    response = session.get(url, stream=True, verify=True)

    if response.status_code == 401:
        print("[ERROR] Unauthorized — check Earthdata credentials.", file=sys.stderr)
        sys.exit(1)

    response.raise_for_status()

    total_bytes = int(response.headers.get("content-length", 0))
    downloaded  = 0

    with open(dest_path, "wb") as fh:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                fh.write(chunk)
                downloaded += len(chunk)
                if total_bytes > 0 and downloaded % (65536 * 50) == 0:
                    pct = 100.0 * downloaded / total_bytes
                    sys.stdout.write(
                        f"\r  Progress: {pct:5.1f}%  "
                        f"({downloaded/(1024*1024):.1f} / {total_bytes/(1024*1024):.1f} MB)"
                    )
                    sys.stdout.flush()

    sys.stdout.write("\n")
    print(f"[COMPLETE] {os.path.basename(dest_path)}  ({downloaded/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    url       = f"{BASE_URL}/{FILENAME}"
    dest_path = os.path.join(OUT_DIR, FILENAME)

    print("=" * 60)
    print("  MERRA-2 Geopotential Constants File Download")
    print("=" * 60)
    print(f"  File    : {FILENAME}")
    print(f"  URL     : {url}")
    print(f"  Dest    : {dest_path}")
    print("=" * 60)

    download_file(url, dest_path)

    print()
    print("Done. Add the following line to your LDT config to enable")
    print("lapse-rate topographic correction:")
    print()
    print(f"  MERRA2 geopotential terrain height file: ./{dest_path}")
    print()

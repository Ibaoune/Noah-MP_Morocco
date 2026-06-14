#!/usr/bin/env python3
# =============================================================================
# download_fluxsat_gpp.py
#
# Author: M. El Aabaribaoune (@um6p)
# Created: 2026-06-11
#
# Download FLUXSAT v2 monthly Gross Primary Production (GPP) global dataset
# for validation against Noah-MP GPP outputs (postproc_02 Figures 2, 3, Supp).
#
# Dataset:  FLUXSAT v2 (monthly, 0.05°, global, NetCDF)
# Variable: GPP (gC/m²/day)
# Period:   2001–2020 (fully covers validation period 2015–2020)
# Source:   Zenodo — https://doi.org/10.5281/zenodo.7761881
# Reference: Joiner & Yoshida (2020), Geoscientific Model Development
# Storage:  data/validation/vegetation/FLUXSAT_GPP/
#
# Note: Files are global NetCDF4 monthly composites (~50–100 MB each).
#       Spatial subsetting to the Sebou domain is done during post-processing.
# =============================================================================

import os
import sys
import logging
import argparse
import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Import shared configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from config_validation import (
    START_YEAR, END_YEAR, DIR_FLUXSAT,
    FLUXSAT_ZENODO_RECID, FLUXSAT_VERSION,
    REPORT_DIR, LOG_DIR
)

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Download FLUXSAT v2 GPP from Zenodo")
parser.add_argument("--start_year", type=int, default=START_YEAR, help="Start year (default: 2015)")
parser.add_argument("--end_year",   type=int, default=END_YEAR,   help="End year   (default: 2020)")
parser.add_argument(
    "--all_years",
    action="store_true",
    help="Download the full record (2001–2020), useful for climatology"
)
args = parser.parse_args()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log_file = os.path.join(LOG_DIR, "download_fluxsat.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Zenodo API helper
# ---------------------------------------------------------------------------
ZENODO_API_URL = f"https://zenodo.org/api/records/{FLUXSAT_ZENODO_RECID}"

def list_zenodo_files(record_id: str) -> list:
    """Return list of {filename, size, url} for a Zenodo record."""
    url = f"https://zenodo.org/api/records/{record_id}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    record = resp.json()
    files = []
    for f in record.get("files", []):
        files.append({
            "filename": f["key"],
            "size":     f["size"],
            "url":      f["links"]["self"],
        })
    return files

def download_file(url: str, local_path: str, chunk_size: int = 8192) -> bool:
    """Stream-download a file. Returns True on success."""
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(local_path, "wb") as f, tqdm(
                total=total, unit="B", unit_scale=True,
                desc=os.path.basename(local_path), leave=False
            ) as pbar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    pbar.update(len(chunk))
        return True
    except Exception as e:
        logger.error(f"Download failed for {os.path.basename(local_path)}: {e}")
        if os.path.exists(local_path):
            os.remove(local_path)
        return False

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import pandas as pd

    logger.info("==============================================")
    logger.info(" FLUXSAT v2 GPP Download — postproc_02     ")
    logger.info("==============================================")

    # Year range to download
    if args.all_years:
        years_target = set(range(2001, 2021))
        logger.info("Mode: full record (2001–2020)")
    else:
        years_target = set(range(args.start_year, args.end_year + 1))
        logger.info(f"Mode: targeted years {args.start_year}–{args.end_year}")

    os.makedirs(DIR_FLUXSAT, exist_ok=True)
    logger.info(f"Output dir : {DIR_FLUXSAT}")

    # Query Zenodo record for file list
    logger.info(f"Querying Zenodo record {FLUXSAT_ZENODO_RECID} …")
    try:
        all_files = list_zenodo_files(FLUXSAT_ZENODO_RECID)
    except Exception as e:
        logger.error(f"Failed to query Zenodo: {e}")
        logger.error("Check the record ID or network connectivity.")
        logger.error(f"Direct URL: https://zenodo.org/record/{FLUXSAT_ZENODO_RECID}")
        sys.exit(1)

    logger.info(f"Found {len(all_files)} files in the Zenodo record.")

    # Filter to NetCDF files matching target years
    # FLUXSAT filename pattern: FLUXSAT_v2_GPP_YYYY_MM.nc  or similar
    import re
    target_files = []
    for f in all_files:
        name = f["filename"]
        if not name.endswith(".nc"):
            continue
        # Extract year from filename
        m = re.search(r"(\d{4})", name)
        if m:
            year = int(m.group(1))
            if year in years_target:
                target_files.append(f)

    if not target_files:
        logger.warning("No matching NetCDF files found for the requested years.")
        logger.warning(f"All files in record: {[x['filename'] for x in all_files]}")
        sys.exit(1)

    logger.info(f"Files to download: {len(target_files)}")

    inventory = []
    
    # Download in parallel using ThreadPoolExecutor
    import concurrent.futures

    def process_file(fmeta):
        fname  = fmeta["filename"]
        url    = fmeta["url"]
        fsize  = fmeta["size"]
        local  = os.path.join(DIR_FLUXSAT, fname)

        if os.path.exists(local) and os.path.getsize(local) == fsize:
            logger.info(f"  ✓ Already complete: {fname}")
            status = "Already_Downloaded"
        else:
            logger.info(f"  ↓ Downloading: {fname}  ({fsize/1048576:.1f} MB)")
            ok = download_file(url, local)
            status = "Downloaded" if ok else "Failed"
            
        return {
            "file_name":    fname,
            "url":          url,
            "size_mb":      round(fsize / 1048576, 2),
            "local_path":   local,
            "status":       status,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_meta = {executor.submit(process_file, fmeta): fmeta for fmeta in target_files}
        for future in concurrent.futures.as_completed(future_to_meta):
            try:
                result = future.result()
                inventory.append(result)
            except Exception as exc:
                logger.error(f"File generated an exception: {exc}")

    # Save inventory
    inv_file = os.path.join(REPORT_DIR, "inventory_fluxsat.csv")
    df = pd.DataFrame(inventory)
    df.to_csv(inv_file, index=False)
    n_ok = df["status"].isin(["Downloaded", "Already_Downloaded"]).sum()
    logger.info(f"Inventory saved → {inv_file}  ({n_ok}/{len(df)} succeeded)")
    logger.info("FLUXSAT download workflow complete.")


if __name__ == "__main__":
    main()

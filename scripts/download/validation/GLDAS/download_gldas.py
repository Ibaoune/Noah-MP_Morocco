#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Script: download_gldas.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# =============================================================================
# download_gldas.py
#
# Created: 2026-06-11
#
# Download GLDAS land surface model outputs for multi-model intercomparison
# (postproc_01 Figures 6–9).
#
# Products:
#   - GLDAS_NOAH025_3H  v2.1  (3-hourly, 0.25°)
#   - GLDAS_VIC10_3H    v2.1  (3-hourly, 1.0°)
#   - GLDAS_CLSM10_3H   v2.1  (3-hourly, 1.0°)
#   - GLDAS_CLSM025_DA1_D v2.2 (daily, 0.25°, GRACE-DA1)
#
# Period: 2015-01-01 to 2020-12-31
# Domain: Sebou-Saïss basin, Morocco (-7.5, 32.0, -3.0, 36.0)
# Source: NASA GES DISC via earthaccess
# =============================================================================

import os
import sys
import logging
import argparse
import pandas as pd
import earthaccess

# ---------------------------------------------------------------------------
# Import shared configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from config_validation import (
    START_DATE, END_DATE, BBOX,
    GLDAS_PRODUCTS, REPORT_DIR, LOG_DIR
)

# ---------------------------------------------------------------------------
# Argument parsing — allows overriding product / dates at the CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Download GLDAS products from NASA GES DISC")
parser.add_argument(
    "--product",
    type=str,
    default="all",
    choices=["all"] + list(GLDAS_PRODUCTS.keys()),
    help="Which GLDAS product to download (default: all)"
)
parser.add_argument("--start_date", type=str, default=START_DATE, help="Start date YYYY-MM-DD")
parser.add_argument("--end_date",   type=str, default=END_DATE,   help="End date YYYY-MM-DD")
args = parser.parse_args()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log_file = os.path.join(os.path.dirname(__file__), "logs", "download_gldas.log")
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
# Helper: download one GLDAS product
# ---------------------------------------------------------------------------
def download_product(product_key: str, start: str, end: str) -> list:
    """Search and download one GLDAS product; returns list of inventory dicts."""
    cfg = GLDAS_PRODUCTS[product_key]
    short_name  = cfg["short_name"]
    version     = cfg["version"]
    output_dir  = cfg["output_dir"]

    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"--- Processing {product_key} v{version} ---")
    logger.info(f"    Output dir : {output_dir}")
    logger.info(f"    Period     : {start} → {end}")

    # Search granules
    results = earthaccess.search_data(
        short_name=short_name,
        version=version,
        bounding_box=BBOX,
        temporal=(start, end)
    )
    logger.info(f"    Found {len(results)} granules.")

    if not results:
        logger.warning(f"    No granules found for {product_key}. Check short_name / version.")
        return []

    # Download
    logger.info(f"    Downloading {len(results)} files using 10 threads …")
    earthaccess.download(results, local_path=output_dir, threads=10)

    # Build inventory
    inventory = []
    for r in results:
        try:
            fname = r.data_links(access="external")[0].split("/")[-1]
        except (IndexError, TypeError):
            fname = "unknown"
        output_path = os.path.join(output_dir, fname)
        status  = "Downloaded" if os.path.exists(output_path) else "Failed"
        size_mb = os.path.getsize(output_path) / 1048576 if os.path.exists(output_path) else 0.0

        inventory.append({
            "product":       product_key,
            "version":       version,
            "file_name":     fname,
            "file_size_mb":  round(size_mb, 2),
            "status":        status,
        })

    n_ok  = sum(1 for x in inventory if x["status"] == "Downloaded")
    n_fail = len(inventory) - n_ok
    logger.info(f"    Downloaded: {n_ok}  Failed: {n_fail}")
    return inventory


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("========================================")
    logger.info(" GLDAS Download Workflow — postproc_01 ")
    logger.info("========================================")
    logger.info(f"Period : {args.start_date} → {args.end_date}")
    logger.info(f"BBox   : {BBOX}")

    # Authenticate with NASA Earthdata
    logger.info("Authenticating with NASA Earthdata …")
    try:
        # Use credentials from environment variables set in the SLURM script
        earthaccess.login(strategy="environment")
    except Exception as e:
        logger.warning(f"Environment login failed ({e}). Attempting netrc login.")
        earthaccess.login(strategy="netrc")

    # Select products to process
    products_to_run = list(GLDAS_PRODUCTS.keys()) if args.product == "all" else [args.product]
    logger.info(f"Products to download: {products_to_run}")

    all_inventory = []
    for pkey in products_to_run:
        inv = download_product(pkey, args.start_date, args.end_date)
        all_inventory.extend(inv)

    # Save merged inventory
    if all_inventory:
        inv_file = os.path.join(REPORT_DIR, "inventory_gldas.csv")
        df = pd.DataFrame(all_inventory)
        df.to_csv(inv_file, index=False)
        logger.info(f"Inventory saved → {inv_file}  ({len(df)} rows)")

    logger.info("GLDAS download workflow complete.")


if __name__ == "__main__":
    main()

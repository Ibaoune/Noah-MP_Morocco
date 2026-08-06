#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Script: config_validation.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

# =============================================================================
# config_validation.py
#
# Created: 2026-06-11
#
# Central configuration for the validation data download workflow.
# All scripts in scripts/download/validation/ import from this file.
#
# Validation period: 2015-01-01 to 2020-12-31
# Study domain:     Sebou-Saïss basin, Morocco
# =============================================================================

import os

# ---------------------------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"

# Download script directory
SCRIPT_DIR = os.path.join(PROJECT_ROOT, "scripts/download/validation")

# Log directory
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Reports / inventory directory
REPORT_DIR = os.path.join(PROJECT_ROOT, "data/reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 2. VALIDATION PERIOD
# ---------------------------------------------------------------------------
START_DATE = "2015-01-01"
END_DATE   = "2020-12-31"
START_YEAR = 2015
END_YEAR   = 2020

# ---------------------------------------------------------------------------
# 3. STUDY DOMAIN (Sebou-Saïss basin bounding box)
#    Format: (lon_min, lat_min, lon_max, lat_max)  — used by earthaccess
# ---------------------------------------------------------------------------
BBOX = (-7.5, 32.0, -3.0, 36.0)

# Explicit bounds for wapordl / WaPOR API (W, S, E, N)
BBOX_WAPOR = {
    "west":  -7.5,
    "south": 32.0,
    "east":  -3.0,
    "north": 36.0,
}

# ---------------------------------------------------------------------------
# 4. DATASET STORAGE PATHS
# ---------------------------------------------------------------------------

# --- Already available (2015–2020) ---
DIR_GMIA = os.path.join(PROJECT_ROOT, "data/land_params/GMIA")
DIR_MODIS_MCD15A2H_RAW = os.path.join(PROJECT_ROOT, "data/observations_archive/MODIS_LAI/raw")

# --- Need download ---
DIR_WAPOR    = os.path.join(PROJECT_ROOT, "data/validation/evapotranspiration/WaPOR")
DIR_FLUXSAT  = os.path.join(PROJECT_ROOT, "data/validation/vegetation/FLUXSAT_GPP")

# GLDAS products (one sub-dir per product)
DIR_GLDAS_ROOT    = os.path.join(PROJECT_ROOT, "data/validation/lsm/GLDAS")
DIR_GLDAS_NOAH    = os.path.join(DIR_GLDAS_ROOT, "GLDAS_NOAH025_3H")
DIR_GLDAS_VIC     = os.path.join(DIR_GLDAS_ROOT, "GLDAS_VIC10_3H")
DIR_GLDAS_CLSM3H  = os.path.join(DIR_GLDAS_ROOT, "GLDAS_CLSM10_3H")
DIR_GLDAS_CLSMD   = os.path.join(DIR_GLDAS_ROOT, "GLDAS_CLSM025_DA1_D")

for d in [DIR_WAPOR, DIR_FLUXSAT,
          DIR_GLDAS_NOAH, DIR_GLDAS_VIC, DIR_GLDAS_CLSM3H, DIR_GLDAS_CLSMD]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# 5. GLDAS PRODUCT DEFINITIONS (earthaccess Concept IDs from NASA GES DISC)
# ---------------------------------------------------------------------------
GLDAS_PRODUCTS = {
    "GLDAS_NOAH025_3H": {
        "short_name":  "GLDAS_NOAH025_3H",
        "version":     "2.1",
        "description": "GLDAS Noah Land Surface Model L4 3 hourly 0.25 x 0.25 degree V2.1",
        "output_dir":  DIR_GLDAS_NOAH,
        "variables":   ["SoilMoi0_10cm_inst", "Rainf_tavg", "Evap_tavg", "Qs_acc", "Qsb_acc"],
    },
    "GLDAS_VIC10_3H": {
        "short_name":  "GLDAS_VIC10_3H",
        "version":     "2.1",
        "description": "GLDAS VIC Land Surface Model L4 3 hourly 1.0 x 1.0 degree V2.1",
        "output_dir":  DIR_GLDAS_VIC,
        "variables":   ["SoilMoi0_10cm_inst", "Rainf_tavg", "Evap_tavg", "Qs_acc", "Qsb_acc"],
    },
    "GLDAS_CLSM10_3H": {
        "short_name":  "GLDAS_CLSM10_3H",
        "version":     "2.1",
        "description": "GLDAS Catchment Land Surface Model L4 3 hourly 1.0 x 1.0 degree V2.1",
        "output_dir":  DIR_GLDAS_CLSM3H,
        "variables":   ["SoilMoist_RZ_tavg", "Rainf_tavg", "Evap_tavg", "Qs_acc", "Qsb_acc"],
    },
    "GLDAS_CLSM025_DA1_D": {
        "short_name":  "GLDAS_CLSM025_DA1_D",
        "version":     "2.2",
        "description": "GLDAS Catchment Land Surface Model L4 Daily 0.25 x 0.25 degree GRACE-DA1 V2.2",
        "output_dir":  DIR_GLDAS_CLSMD,
        "variables":   ["SoilMoist_RZ_tavg", "Evap_tavg", "TWS_tavg"],
    },
}

# ---------------------------------------------------------------------------
# 6. FLUXSAT CONFIGURATION
# ---------------------------------------------------------------------------
# FLUXSAT v2: monthly global GPP, 0.05° resolution
# Zenodo DOI: https://doi.org/10.5281/zenodo.7761881
# Coverage: 2001–2020 — fully covers validation period 2015–2020
FLUXSAT_ZENODO_DOI   = "10.5281/zenodo.7761881"
FLUXSAT_ZENODO_RECID = "7761881"
FLUXSAT_VERSION      = "v2"

# ---------------------------------------------------------------------------
# 7. WAPOR CONFIGURATION
# ---------------------------------------------------------------------------
# WaPOR v3 products (via wapordl library)
# AETI = Actual Evapotranspiration and Interception
# T    = Transpiration
# E    = Evaporation
# NPP  = Net Primary Production
WAPOR_LEVEL      = "L2"      # Level 2: country/regional (250m)
WAPOR_COMPONENTS = ["AETI", "T", "E", "NPP"]
WAPOR_PERIOD     = "DEKADAL"  # 10-day composites

if __name__ == "__main__":
    print("=== Validation Data Configuration ===")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Period       : {START_DATE} → {END_DATE}")
    print(f"Bounding box : {BBOX}")
    print(f"GLDAS products: {list(GLDAS_PRODUCTS.keys())}")
    print(f"WaPOR components: {WAPOR_COMPONENTS}")
    print(f"FLUXSAT DOI  : {FLUXSAT_ZENODO_DOI}")
    print("All output directories created OK.")

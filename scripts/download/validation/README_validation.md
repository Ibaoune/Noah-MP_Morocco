# README — Validation Datasets for Noah-MP SMAP DA Experiments
**Author:** M. EL Aabaribaoune (@um6p)

**Project**: Noah-MP SMAP Data Assimilation — Sebou-Saïss Basin, Morocco  
**Contact**: M. El Aabaribaoune, UM6P  
**Last updated**: 2026-06-11  

---

## Overview

This directory (`scripts/download/validation/`) centralizes the complete validation data download
workflow for the two post-processing experiments:

| Experiment | Scope |
|------------|-------|
| **postproc_01** | Water balance, runoff, multi-model lsm (GLDAS), streamflow validation |
| **postproc_02** | SSM-DA impact on fluxes (ET, GPP, NPP), vegetation dynamics (LAI), drought detection |

**Validation period**: **2015-01-01 to 2020-12-31**  
**Study domain**: Sebou-Saïss basin, Morocco  
**Bounding box**: West=-7.5°, South=32.0°, East=-3.0°, North=36.0°  

---

## Dataset Summary Table

| # | Dataset | Used In | Status (2015–2020) | Download Script |
|---|---------|---------|-------------------|-----------------|
| 1 | [FAO GMIA v5](#1-fao-gmia-v5---irrigation-maps) | pp01, pp02 |  Available | `download_gmia.py` (moved) |
| 2 | [GLDAS Products](#2-gldas-land-surface-model-lsm) | pp01 (Figs 6–9) |  Available | `download_gldas.py` |
| 3 | [MODIS MCD12Q1](#3-modis-mcd12q1---land-cover) | pp02 (Fig 1, 3) |  Available (LIS input) | Static — no script needed |
| 4 | [MODIS MCD15A2H v6.1](#4-modis-mcd15a2h-v61---leaf-area-index-lai) | pp02 (Figs 4, 6, Supp) |  Available — 276 HDF files | `download_modis_mcd15a2h.py` (moved) |
| 5 | [FAO WaPOR v3](#5-fao-wapor-v3---evapotranspiration--npp) | pp02 (Figs 2, 3, Supp) |  **Pending** — requires Google Earth Engine `set_project` | `download_wapor.py` |
| 6 | [FLUXSAT v2](#6-fluxsat-v2---gross-primary-production-gpp) | pp02 (Figs 2, 3, Supp) |  Available | `download_fluxsat_gpp.py` |

| 7 | ESA CCI Soil Moisture (COMBINED v8.1) | pp01, pp02 | Available | `download_esa_cci_sm.py` |
| 8 | Copernicus ASCAT SWI | pp01, pp02 | Available | `download_ascat.py` |
| 9 | Copernicus LAI 300m | pp02 | **Running** | `download_copernicus_lai.py` |
| 10 | GLEAM v3.8a ET | pp01, pp02 | **Running** | `download_gleam.py` |
| 11 | GRACE / GRACE-FO | pp01 | Available | `download_grace.py` |

> **Excluded** (produced by simulation workflow or provided by local agencies):  
> LIS Noah-MP OPL outputs · LIS Noah-MP DA outputs · HyMAP routed streamflow · In-situ gauging discharge

---

## Directory Contents

```
scripts/download/validation/
├── README_validation.md              ← This file
├── config_validation.py              ← Shared configuration (paths, bbox, dates)
│
├── download_gmia.py                  ← MOVED from scripts/download/ (GMIA — static, complete)
├── download_modis_mcd15a2h.py        ← MOVED from scripts/download/ (MODIS LAI — complete 2015–2020)
├── download_wapor.py                 ← MOVED + REWRITTEN (WaPOR v3 via wapordl — needs run)
├── download_fluxsat_gpp.py           ← NEW (FLUXSAT GPP v2 from Zenodo — needs run)
├── download_gldas.py                 ← NEW (GLDAS 4 products — needs run)
│
├── submit_download_wapor.sh          ← SLURM job for WaPOR
├── submit_download_fluxsat.sh        ← SLURM job for FLUXSAT
├── submit_download_gldas.sh          ← SLURM array job for GLDAS (4 tasks)
│
└── logs/                             ← Job log files
```

---

## Dataset Details

---

### 1. FAO GMIA v5 — Irrigation Maps

| Field | Value |
|-------|-------|
| **Dataset name** | Global Map of Irrigation Areas (GMIA) v5 |
| **Provider / Source** | Food and Agriculture Organization of the United Nations (FAO) |
| **Official website** | https://www.fao.org/aquastat/en/geospatial-information/global-maps-irrigated-areas |
| **Version** | v5.0 |
| **Spatial resolution** | 5 arc-minutes (~10 km) |
| **Temporal resolution** | Static (single epoch ~2005) |
| **Variables used** | `gmia_v5_aei_pct.asc` — Area Equipped for Irrigation (% of grid cell) |
| **Temporal coverage** | Static |
| **Period used** | Static (applied over full 2015–2020 simulation) |
| **File format** | ASC (ESRI ASCII raster) |
| **Download method** | Manual download from FAO AQUASTAT portal |
| **Download script** | `download_gmia.py` |
| **Storage location** | `data/land_params/GMIA/gmia_v5_aei_pct.asc` |
| **Preprocessing** | None required; used directly as a spatial mask |
| **Notes** | Used for Figures 4, 13–14 in postproc_01 and Figures 1, 2 in postproc_02. No newer version is needed for the 2015–2020 period. |

**Status**:  Available and complete.

---

### 2. GLDAS Land Surface Model Intercomparison

| Field | Value |
|-------|-------|
| **Dataset name** | Global Land Data Assimilation System (GLDAS) — multiple products |
| **Provider / Source** | NASA GES DISC (Goddard Earth Sciences Data and Information Services Center) |
| **Official website** | https://disc.gsfc.nasa.gov/datasets?keywords=GLDAS |
| **Versions** | v2.1 (NOAH, VIC, CLSM), v2.2 (CLSM DA1) |
| **Spatial resolution** | 0.25° (NOAH, CLSM DA1), 1.0° (VIC, CLSM) |
| **Temporal resolution** | 3-hourly (NOAH, VIC, CLSM); Daily (CLSM DA1) |
| **Variables used** | Soil moisture (top layer), Evapotranspiration, Runoff (surface + baseflow) |
| **Temporal coverage** | 2000–present (NOAH v2.1); varies by product |
| **Period used** | 2015-01-01 to 2020-12-31 |
| **File format** | NetCDF-4 |
| **Download method** | `earthaccess` Python library (NASA Earthdata login required) |
| **Download script** | `download_gldas.py` |
| **Storage location** | `data/validation/lsm/GLDAS/<product>/` |
| **Preprocessing** | Spatial subsetting to Sebou domain; temporal aggregation (3H → daily/monthly) |
| **Notes** | Used for postproc_01 Figures 6–9 (multi-model lsm). NASA Earthdata account required; store credentials in `~/.netrc`. |

**Sub-products:**

| Product | Version | Resolution | Temporal | Short Name |
|---------|---------|-----------|----------|-----------|
| GLDAS Noah LSM | v2.1 | 0.25° / 3H | 3-hourly | `GLDAS_NOAH025_3H` |
| GLDAS VIC LSM | v2.1 | 1.0° / 3H | 3-hourly | `GLDAS_VIC10_3H` |
| GLDAS CLSM | v2.1 | 1.0° / 3H | 3-hourly | `GLDAS_CLSM10_3H` |
| GLDAS CLSM GRACE-DA1 | v2.2 | 0.25° / Daily | Daily | `GLDAS_CLSM025_DA1_D` |

**Status**:  Not yet downloaded. **Action**: Run `sbatch submit_download_gldas.sh`

---

### 3. MODIS MCD12Q1 — Land Cover

| Field | Value |
|-------|-------|
| **Dataset name** | MODIS Terra+Aqua Land Cover Type Yearly L3 Global 500m (MCD12Q1) |
| **Provider / Source** | NASA LP DAAC (Land Processes Distributed Active Archive Center) |
| **Official website** | https://lpdaac.usgs.gov/products/mcd12q1v061/ |
| **Version** | Collection 6.1 (v061) |
| **Spatial resolution** | 500 m |
| **Temporal resolution** | Annual |
| **Variables used** | `LC_Type1` — IGBP land cover classification (17 classes) |
| **Temporal coverage** | 2001–present |
| **Period used** | 2015–2020 (yearly maps) |
| **File format** | HDF4 (MODIS standard) |
| **Download method** | Already embedded in LIS input files |
| **Download script** | N/A — static LIS input |
| **Storage location** | `data/lis_input/lis_input.d01.nc` (embedded) |
| **Preprocessing** | Pre-processed by LDT into LIS input file |
| **Notes** | Used for ecosystem stratification in postproc_02 Figures 1, 3. Accessed from `lis_input.d01.nc` land cover index variable. |

**Status**:  Available and complete.

---

### 4. MODIS MCD15A2H v6.1 — Leaf Area Index (LAI)

| Field | Value |
|-------|-------|
| **Dataset name** | MODIS Terra+Aqua Leaf Area Index/FPAR 8-Day L4 Global 500m (MCD15A2H) |
| **Provider / Source** | NASA LP DAAC (Land Processes Distributed Active Archive Center) |
| **Official website** | https://lpdaac.usgs.gov/products/mcd15a2hv061/ |
| **Version** | Collection 6.1 (v061) |
| **Spatial resolution** | 500 m (MODIS sinusoidal grid, tile h17v05 for Morocco) |
| **Temporal resolution** | 8-day composites |
| **Variables used** | `Lai_500m` (LAI, m²/m²), `FparLai_QC` (quality flag) |
| **Temporal coverage** | 2002–present |
| **Period used** | 2015-01-01 to 2020-12-31 |
| **File format** | HDF4 (MODIS standard) |
| **Download method** | `earthaccess` Python library (NASA Earthdata login required) |
| **Download script** | `download_modis_mcd15a2h.py` |
| **Storage location** | `data/observations_archive/MODIS_LAI/raw/` (raw HDF files) |
| **Preprocessing** | HDF4 → NetCDF conversion, reprojection to lat/lon, spatial clip to Sebou domain |
| **Notes** | 276 HDF files available for 2015–2020 (tile h17v05, ~46 composites/year × 6 years). Processed files in `data/observations_archive/MODIS_LAI/processed/`. Used for postproc_02 Figures 4, 6, and Supplementary statistics. |

**Status**:  Available and complete for 2015–2020.

---

### 5. FAO WaPOR v3 — Evapotranspiration & NPP

| Field | Value |
|-------|-------|
| **Dataset name** | Water Productivity Open-access portal (WaPOR) — Level 2 Regional Products |
| **Provider / Source** | Food and Agriculture Organization of the United Nations (FAO) |
| **Official website** | https://wapor.apps.fao.org/ |
| **Version** | v3 (released 2023; improved algorithms over v2) |
| **Spatial resolution** | 100 m (Level 2 regional) |
| **Temporal resolution** | Dekadal (10-day composites) → aggregatable to monthly |
| **Variables used** | `AETI` (Actual ET & Interception, mm/day), `T` (Transpiration), `E` (Evaporation), `NPP` (Net Primary Production, gDM/ha/day) |
| **Temporal coverage** | 2009–present |
| **Period used** | 2015-01-01 to 2020-12-31 |
| **File format** | GeoTIFF (.tif), one file per 10-day composite per variable |
| **Download method** | `wapordl` Python library with FAO WaPOR API token |
| **Download script** | `download_wapor.py` |
| **Storage location** | `data/validation/evapotranspiration/WaPOR/<component>/` |
| **Preprocessing** | Spatial clip to Sebou domain; temporal aggregation (dekadal → monthly/seasonal) |
| **Notes** | **Requires WaPOR API token** — register at https://wapor.apps.fao.org/ and set `WAPOR_API_TOKEN` environment variable or store in `~/.wapor_token`. Install library: `pip install wapordl`. Dummy files currently exist in `data/validation/evapotranspiration/WaPOR/` and must be replaced. Used for postproc_02 Figures 2, 3, and Supplementary statistics. |

**Status**:  Dummy placeholder files only. **Action**: Run `sbatch submit_download_wapor.sh`

**WaPOR layer codes (wapordl)**:
```
L2-AETI-D  →  Actual Evapotranspiration and Interception (dekadal)
L2-T-D     →  Transpiration (dekadal)
L2-E-D     →  Evaporation (dekadal)
L2-NPP-D   →  Net Primary Production (dekadal)
```

---

### 6. FLUXSAT v2 — Gross Primary Production (GPP)

| Field | Value |
|-------|-------|
| **Dataset name** | FLUXSAT v2 — Global Monthly Gross Primary Production |
| **Provider / Source** | Joiner & Yoshida (NASA GSFC) / Berkeley GIF |
| **Official website** | https://doi.org/10.5281/zenodo.7761881 |
| **Version** | v2 |
| **Spatial resolution** | 0.05° (~5 km), global |
| **Temporal resolution** | Monthly |
| **Variables used** | `GPP` (Gross Primary Production, gC/m²/day) |
| **Temporal coverage** | 2001–2020 |
| **Period used** | 2015-01-01 to 2020-12-31 (72 monthly files) |
| **File format** | NetCDF-4 (.nc), one file per month, global extent |
| **Download method** | Zenodo REST API (no registration required) |
| **Download script** | `download_fluxsat_gpp.py` |
| **Storage location** | `data/validation/vegetation/FLUXSAT_GPP/` |
| **Preprocessing** | Spatial clip to Sebou domain; temporal aggregation to seasonal/annual means |
| **Notes** | FLUXSAT v2 is derived from MODIS reflectance and SIF data scaled to FLUXNET tower GPP. Coverage ends at 2020 — fully covers the 2015–2020 validation period. Used for postproc_02 Figures 2, 3, and Supplementary statistics. Compare with LIS `GPP_tavg` output. |

**Status**:  Not yet downloaded. **Action**: Run `sbatch submit_download_fluxsat.sh`

---

## Data Storage Map

```
data/
├── land_params/GMIA/
│   └── gmia_v5_aei_pct.asc                     Available
│
├── observations_archive/
│   └── MODIS_LAI/
│       ├── raw/        (276 HDF files, 2015–2020)     Available
│       └── processed/  (NetCDF, clipped)                Available
│
└── validation/
    ├── evapotranspiration/
    │   ├── WaPOR/
    │   │   ├── AETI/   (dekadal GeoTIFF 2015–2020)    NEEDS DOWNLOAD
    │   │   ├── T/                                       NEEDS DOWNLOAD
    │   │   ├── E/                                       NEEDS DOWNLOAD
    │   │   └── NPP/                                     NEEDS DOWNLOAD
    │   └── MOD16/      (existing archive, 2015–2020)   Available (archive)
    │
    ├── lsm/
    │   └── GLDAS/
    │       ├── GLDAS_NOAH025_3H/                        NEEDS DOWNLOAD
    │       ├── GLDAS_VIC10_3H/                          NEEDS DOWNLOAD
    │       ├── GLDAS_CLSM10_3H/                         NEEDS DOWNLOAD
    │       └── GLDAS_CLSM025_DA1_D/                     NEEDS DOWNLOAD
    │
    └── vegetation/
        ├── MODIS_MCD15A2H/    (link to observations_archive)   Available
        └── FLUXSAT_GPP/       (monthly NetCDF 2015–2020)        NEEDS DOWNLOAD
```

---

## Quick-Start: Downloading Missing Datasets

### Step 1 — Prerequisites

```bash
# Activate the post-processing environment
conda activate postproc_env

# Install required libraries
pip install earthaccess wapordl tqdm

# Configure NASA Earthdata credentials (for GLDAS + MODIS)
# Edit ~/.netrc:
echo "machine urs.earthdata.nasa.gov login <your_user> password <your_pass>" >> ~/.netrc
chmod 600 ~/.netrc

# Configure WaPOR API token
# Register at https://wapor.apps.fao.org/ then:
echo "<your_wapor_token>" > ~/.wapor_token
chmod 600 ~/.wapor_token
```

### Step 2 — Submit download jobs

```bash
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation

# GLDAS (4 products in parallel, ~8h per product)
sbatch submit_download_gldas.sh

# WaPOR v3 (AETI, T, E, NPP, ~4h total)
sbatch submit_download_wapor.sh

# FLUXSAT v2 GPP (72 monthly NetCDF files, ~2h)
sbatch submit_download_fluxsat.sh
```

### Step 3 — Monitor and verify

```bash
# Check job status
squeue -u $USER

# Check logs
tail -f logs/gldas_*.out
tail -f logs/wapor_*.out
tail -f logs/fluxsat_*.out

# Check downloaded inventories
ls ../../data/reports/inventory_*.csv

# Other submission scripts available:
# sbatch submit_ascat.sh
# sbatch submit_cop_lai.sh
# sbatch submit_esacci.sh
# sbatch submit_gleam.sh

```

### Step 4 — Run interactively (if needed)

```bash
# GLDAS — one product at a time
python3 download_gldas.py --product GLDAS_NOAH025_3H

# WaPOR
python3 download_wapor.py

# FLUXSAT
python3 download_fluxsat_gpp.py --start_year 2015 --end_year 2020

# MODIS LAI (already downloaded — use script to re-download if needed)
python3 download_modis_mcd15a2h.py --start_date 2015-01-01 --end_date 2020-12-31
```

---

## References

1. **GMIA**: Siebert, S., Döll, P., et al. (2013). *Global Map of Irrigation Areas version 5*. FAO-AQUASTAT.
2. **GLDAS**: Rodell, M., et al. (2004). *The Global Land Data Assimilation System*. BAMS, 85(3), 381–394. DOI: 10.1175/BAMS-85-3-381
3. **GLDAS v2.2 DA1**: Li, B., et al. (2019). *Global GRACE data assimilation for groundwater and drought monitoring*. Water Resources Research.
4. **MODIS MCD12Q1**: Friedl, M.A., et al. (2010). *MODIS Collection 5 global land cover*. Remote Sensing of Environment, 114(1), 168–182.
5. **MODIS MCD15A2H**: Myneni, R., et al. (2015). *MODIS/Terra+Aqua Leaf Area Index/FPAR 8-Day L4 Global 500m SIN Grid*. LP DAAC.
6. **WaPOR**: FAO (2020). *WaPOR, the FAO portal to monitor water productivity through open access of remotely sensed derived data*. FAO, Rome.
7. **FLUXSAT**: Joiner, J. & Yoshida, Y. (2020). *Satellite-based reflectances capture large fraction of variability in global gross primary production (GPP) at weekly time scales*. Agricultural and Forest Meteorology. DOI: 10.5281/zenodo.7761881

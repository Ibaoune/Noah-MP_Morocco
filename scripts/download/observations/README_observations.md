# Observation Datasets Preparation
**Author:** M. EL Aabaribaoune (@um6p)

**Author:** M. El Aabaribaoune (@um6p)  
**Last Updated:** 2026-06-14

---

## Overview
This directory (`scripts/download/observations/`) is dedicated to preparing and downloading the **Observation datasets** used for Data Assimilation in the Noah-MP experiments (e.g., the 3-day tests and the 2015–2020 validation periods).

> [!NOTE]
> For validation and intercomparison datasets (like GLDAS, WaPOR, FLUXSAT, and MODIS LAI), please refer to the `scripts/download/validation/` directory.

## SMAP Soil Moisture (Assimilation)
- **Dataset Name**: SMAP Enhanced L3 Radiometer Global Daily 9 km EASE-Grid Soil Moisture
- **Provider/Source**: NASA NSIDC
- **Version**: 006
- **Spatial Resolution**: 9 km
- **Temporal Resolution**: Daily
- **Variables Used**: Soil Moisture (SPL3SMP_E)
- **Temporal Coverage**: 2015-03-31 to Present
- **Period Used**: 2015–2020 (Validation period)
- **File Format**: HDF5
- **Download Method**: `download_smap_spl3smp_e.py` (submitted via `submit_download_smap.sh`)
- **Storage Location**: `data/observations/SMAP_SPL3SMP_E/raw`
- **Preprocessing/Notes**: Earthdata login credentials are required (`.netrc` or env). Assimilated via LIS using EnKF with CDF matching bias correction.

## Execution
To ensure maximum stability when interacting with NASA's servers, the download process is designed to be executed **one year at a time** using monthly job arrays (1-12).

To run the automated parallel download for SMAP data for a specific year:
```bash
sbatch --export=ALL,YEAR=2020 submit_download_smap.sh
```
This job array will spawn 12 independent tasks (one for each month), fetching the daily granules and avoiding network timeouts.

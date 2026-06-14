# Observation Datasets Preparation

This directory (`scripts/download/observations/`) is dedicated to preparing and downloading the **Observation datasets** used for Data Assimilation in the Noah-MP experiments (e.g., the 3-day tests and the 2015–2020 validation periods).

> [!NOTE]
> For validation and intercomparison datasets (like GLDAS, WaPOR, FLUXSAT, and MODIS LAI), please refer to the `scripts/download/validation/` directory.

## SMAP Soil Moisture (Assimilation)
- **Dataset Name**: SMAP L3 Radiometer Global Daily 36 km EASE-Grid Soil Moisture
- **Provider/Source**: NASA NSIDC
- **Version**: 009
- **Spatial Resolution**: 36 km
- **Temporal Resolution**: Daily
- **Variables Used**: Soil Moisture (SPL3SMP)
- **Temporal Coverage**: 2015-03-31 to Present
- **Period Used**: 2015–2020 (Validation period)
- **File Format**: HDF5
- **Download Method**: `download_smap.py` (submitted via `submit_download_smap.sh`)
- **Storage Location**: `data/observations/SMAP/SPL3SMP.009`
- **Preprocessing/Notes**: Earthdata login credentials are required. Assimilated via LIS using EnKF with CDF matching bias correction.

## Execution
To run the automated multi-year parallel download for SMAP data on the cluster:
```bash
sbatch submit_download_smap.sh
```
This job array runs one task per year (from 2015 to 2020), fetching the daily granules and avoiding network timeouts.

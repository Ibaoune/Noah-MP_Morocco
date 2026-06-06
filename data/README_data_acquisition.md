# Data Acquisition and Preprocessing Workflow

**Author:** M. El Aabaribaoune (@um6p)

This document outlines the end-to-end workflow for acquiring and preprocessing all necessary forcing, assimilation, and validation datasets for the LIS/Noah-MP simulations over the Sebou-Saïss basin (Morocco) for the 2015-2020 period. This setup strictly follows the configuration detailed in Nie et al. (2022).

## 1. Datasets Overview

| Dataset | Type | Version | Spatial Res | Temporal Res | Source/Platform | Authentication |
|---------|------|---------|-------------|--------------|-----------------|----------------|
| **IMERG** | Forcing (Precipitation) | Final Run V07 | 0.1° | Daily / Sub-daily | NASA Earthdata | `earthaccess` (.netrc) |
| **GDAS** | Forcing (Meteorological) | NCEP FNL | 0.25° | 6-hourly | NCAR RDA (ds083.3) | RDA API Token |
| **SMAP** | Assimilation (Soil Moisture) | SPL3SMP_E V6 | 9 km | Daily | NASA Earthdata | `earthaccess` (.netrc) |
| **MODIS** | Assimilation (LAI/FPAR) | MCD15A2H 6.1 | 500 m | 8-day | NASA Earthdata | `earthaccess` (.netrc) |
| **GLEAM** | Validation (ET) | v3.7a | 0.25° | Daily | ftp.gleam.eu | FTP credentials |
| **WaPOR** | Validation (AETI) | v2/v3 | 250 m | Dekadal | FAO API | WaPOR API Token |
| **ESA CCI**| Validation (Soil Moisture)| COMBINED | 0.25° | Daily | CEDA / CDS API | CEDA/CDS Account |
| **MOD16A2GF** | Validation (ET) | 6.1 (Gap-Filled) | 500 m | 8-day | NASA Earthdata | `earthaccess` (.netrc) |
| **MOD17A2HGF**| Validation (GPP) | 6.1 (Gap-Filled) | 500 m | 8-day | NASA Earthdata | `earthaccess` (.netrc) |
| **GRACE** | Validation (TWS) | Mascon CRI v04 | 3° (0.5° grid) | Monthly | NASA Earthdata | `earthaccess` (.netrc) |
| **ASCAT** | Validation (Soil Moisture) | SWI v3.1.1 | 0.1° | Daily | CDSE API | OAuth2 Token |
| **Copernicus LAI** | Validation (LAI) | LAI300 v1/v2 | 300 m | 10-day | CDSE API | OAuth2 Token |
| **ABHS** | Validation (Streamflow) | In-situ | Point | Daily/Monthly | Local Agency | None (Local files)|

## 2. Preprocessing Steps and Expected Output Format

The LIS framework requires forcing and observational data to be in specific formats (typically NetCDF, occasionally GRIB/HDF depending on the exact reader compiled) and remapped to the target domain.

- **IMERG**: Sub-setted to the domain bounding box (`-7.0W, 32.5N` to `-3.5W, 35.5N`) and stored as `.nc4` files. Handled directly during the download phase.
- **GDAS**: Extracted from GRIB2, sub-setted to the bounding box, longitudes shifted to -180/180 if required, and output as NetCDF.
- **SMAP SPL3SMP_E**: Extracted from HDF5, quality-controlled (filtering frozen soil and high vegetation water content), regridded to 0.01° using nearest-neighbor or bilinear interpolation, and stored as NetCDF. Bias correction (CDF matching/anomaly rescaling) files are generated from these regridded datasets.
- **MODIS LAI**: Extracted from HDF-EOS (Sinusoidal projection), quality-controlled, reprojected to geographic coordinates (EPSG:4326), regridded to 0.01°, and stored as NetCDF.
- **Streamflow (ABHS)**: Standardized into daily/monthly CSV or NetCDF format using the provided metadata template.

## 3. Workflow Execution Order

All workflow components (scripts, logs, reports, and raw data) are strictly localized within the `data/` directory. All commands below should be executed from within the `data/` directory.

1. **Setup Environment**: The SLURM job scripts are pre-configured to use the Conda environment at `/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13`.
2. **Download Forcing**: Submit `sbatch scripts/jobs/job_download_forcing.sh`
3. **Download Observations**: Submit `sbatch scripts/jobs/job_download_observations.sh`
4. **Download Validation**: Submit `sbatch scripts/jobs/job_download_validation.sh`
5. **Preprocess Forcing**: Submit `sbatch scripts/jobs/job_preprocess_forcing.sh`
6. **Preprocess Observations**: Submit `sbatch scripts/jobs/job_preprocess_observations.sh`
7. **Verify Completeness**: Run `./scripts/survey_downloads.sh` and review the auto-generated summaries in `reports/`.

---

## 4. Draft Methods Paragraph for Publication

**Data Acquisition and Preparation**
The meteorological forcing for the Land Information System (LIS) Noah-MP configuration was constructed by combining the Integrated Multi-satellitE Retrievals for GPM (IMERG) Final Run Version 07 for precipitation and the Global Data Assimilation System (GDAS) for near-surface air temperature, specific humidity, wind speed, surface pressure, and downward shortwave and longwave radiation (Nie et al., 2022). All forcing fields were downscaled to the 0.01° target grid covering the Sebou-Saïss basin for the 2015–2020 period. For data assimilation, the Soil Moisture Active Passive (SMAP) Enhanced L3 Radiometer Global Daily 9 km soil moisture product (SPL3SMP_E V6) and the MODIS Terra+Aqua Leaf Area Index product (MCD15A2H Collection 6.1) were utilized. Prior to assimilation, SMAP retrievals were subjected to rigorous quality control to mask frozen soils and dense vegetation, followed by regridding and bias correction via Cumulative Distribution Function (CDF) matching. Independent validation of the simulated water cycle was performed using the Global Land Evaporation Amsterdam Model (GLEAM v3.7), FAO WaPOR actual evapotranspiration, ESA CCI soil moisture, and daily in-situ streamflow observations provided by the Sebou Hydraulic Basin Agency (ABHS).

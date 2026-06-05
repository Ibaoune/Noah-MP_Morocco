# Troubleshooting Data Acquisition

**Author:** M. El Aabaribaoune (@um6p)

This document provides solutions to common issues encountered during the data download and preprocessing workflow.

## 1. Earthdata Authentication Failures (IMERG, SMAP, MODIS)

**Error**: `earthaccess` fails to authenticate, or the script crashes with `ModuleNotFoundError: No module named 'earthaccess'`.
**Solution**: 
- The module error occurs if the SLURM job uses the system default python instead of your conda environment. Ensure the SLURM script explicitly calls the python executable from your active conda environment (e.g., `/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python`).
- Ensure your `~/.netrc` file is correctly formatted:
  ```text
  machine urs.earthdata.nasa.gov
  login YOUR_USERNAME
  password YOUR_PASSWORD
  ```
- Make sure the file permissions are strict: `chmod 600 ~/.netrc`.
- Alternatively, export environment variables before running the job: `export EARTHDATA_USERNAME="user"`, `export EARTHDATA_PASSWORD="pwd"`.

**Error**: `earthaccess` search fails with `RuntimeError: {"errors":["An Internal Error has occurred."]}`.
**Solution**: This is a temporary server outage on NASA's Common Metadata Repository (CMR) side. Wait a few minutes or hours and resubmit the download job. `earthaccess` will safely skip already-downloaded files and resume exactly where it left off.

## 2. GDAS Download Errors

**Error**: HTTP 401 Unauthorized or script fails to download actual GRIB files.
**Solution**:
- NCAR RDA (ds083.3) requires active authentication. You cannot download via simple anonymous requests.
- Generate an API token from the RDA dashboard.
- If using python `requests`, ensure you are passing the auth token in the headers as described in the RDA documentation, or use their provided `rdams-client` python package.

## 3. Preprocessing Memory Errors (OOM)

**Error**: SLURM kills the preprocessing job with `OOM-kill` (Out of Memory).
**Solution**:
- Xarray can consume significant memory if processing large HDF/NetCDF datasets in memory.
- In the preprocessing SLURM script (`job_preprocess_observations.sh`), increase the `--mem` allocation (e.g., from `32G` to `64G`).
- Modify the python scripts to process chunks of data or use `dask` via `xarray.open_mfdataset(..., chunks={})`.

## 4. Incomplete Files or Corrupt HDF/NetCDF

**Error**: Python scripts throw `OSError: [Errno -101] NetCDF: HDF error` or `File format not recognized`.
**Solution**:
- This usually occurs if a download was interrupted.
- Run `./scripts/survey_downloads.sh`. Check the file sizes in the generated CSV in `reports/`. If a file is significantly smaller than others of the same product, delete it and re-run the download script. The download scripts are designed to skip existing files but will not automatically resume partially downloaded files.

## 5. GLEAM FTP Connection Timeout

**Error**: `ftplib.error_temp: 421 Timeout` or connection refused.
**Solution**:
- Institutional firewalls or cluster login nodes sometimes block outbound FTP traffic on port 21.
- Try downloading the data manually from a local machine and uploading via `scp`/`rsync`, or request a direct HTTP download link from the GLEAM administrators.

## 6. MODIS Reprojection Issues (pyresample / rasterio)

**Error**: Sinusoidal grid conversion fails or coordinates are misaligned.
**Solution**:
- Ensure your environment has the correct PROJ definitions. A common issue is a missing `PROJ_LIB` path.
- Export `PROJ_LIB` to your conda environment's proj directory before running the script: `export PROJ_LIB=/path/to/conda/envs/lis_env/share/proj`.

## 7. MODIS Collection 6.1 Historical Data Missing (0 Granules)

**Error**: `earthaccess` search for `MOD16A2` or `MOD17A2H` returns `0` granules for historical dates (e.g., 2015-2020), causing `ValueError: List of URLs or DataGranule instances expected` during the download phase.
**Solution**:
- NASA LP DAAC's standard Collection 6.1 datasets for MOD16 and MOD17 are currently missing indexing for data prior to 2021 on the CMR catalog.
- To download historical data for the 2015-2020 period, you must query the **Gap-Filled** (GF) versions of these datasets (`MOD16A2GF` and `MOD17A2HGF`). Gap-filled data is highly recommended for model validation as it mitigates cloud cover issues.
- Explicitly pass the NASA Concept IDs for the Gap-Filled versions to `earthaccess.search_data()`. For example, use `concept_id="C2565791021-LPCLOUD"` for MOD16A2GF and `concept_id="C2565791029-LPCLOUD"` for MOD17A2HGF.

## 8. CDSE OData API Failures (ASCAT, Copernicus LAI)

**Error**: `requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url`
**Solution**:
- This means the CDSE OAuth2 token has expired or the credentials are invalid.
- Ensure your `USERNAME` and `PASSWORD` in `download_ascat.py` and `download_copernicus_lai.py` are correct.
- If downloading a large batch of files (e.g., thousands of ASCAT granules), the script will automatically refresh the token periodically. If it still fails, the CDSE authentication server might be temporarily down.

**Error**: `requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
**Solution**:
- Copernicus Data Space Ecosystem limits the number of concurrent connections and data streams. 
- The Python script downloads files sequentially to avoid rate limiting. If the connection drops mid-download, the script will crash. Simply re-run the SLURM job. The scripts are designed to skip already downloaded files, so it will resume exactly where it left off.

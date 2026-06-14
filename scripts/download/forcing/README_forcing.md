# Noah-MP Forcing Data Infrastructure
**Author:** M. El Aabaribaoune (@um6p)  
**Last Updated:** 2026-06-14

---

## Overview
This directory contains the infrastructure for downloading the meteorological forcing datasets required to run LIS / Noah-MP simulations over the Sebou-Saïss basin (Morocco). 

To ensure maximum stability when interacting with NASA's GES DISC servers (which frequently drop long-lived connections), the architecture is highly modular. The download process is **decoupled** into separate IMERG and MERRA-2 SLURM scripts, and is designed to be executed **one year at a time** using monthly job arrays (1-12).

---

## How to Run

To download the forcing datasets, submit the provided SLURM job array scripts manually for a specific year:

```bash
cd scripts/download/forcing/

# 1. Download MERRA-2 for a specific year (e.g. 2010)
sbatch --export=ALL,YEAR=2010 --array=1-12 job_download_merra2.sh

# 2. Download IMERG for a specific year
sbatch --export=ALL,YEAR=2010 --array=1-12 job_download_imerg.sh
```

**What happens under the hood?**
- `sbatch --array=1-12` launches exactly **12 parallel tasks**, one for each month of the specified `YEAR`.
- This granularity isolates NASA server timeouts. If a single month fails due to network issues, it does not corrupt the rest of the year.
- The Python scripts have **strict data validation**: if a downloaded file is corrupted or times out, the script will forcefully fail (`sys.exit(1)`), ensuring you are instantly notified.
- You can easily retry a failed month simply by re-running the command; the scripts are smart and will instantly **[SKIP]** already downloaded files, picking up exactly where they left off.

---

## Scripts Description

### 1. `job_download_merra2.sh` & `job_download_imerg.sh`
- **Role:** The SLURM orchestrator scripts for their respective datasets.
- **Functionality:** Sets up the HPC environment (`arch_toubkal.env` + Python `venv`), calculates the start and end dates for the specific array month, and launches the Python download logic.

### 2. `download_merra2.py`
- **Role:** Fetches global meteorological state variables and surface fluxes.
- **Data Downloaded:** 
  - `M2T1NXFLX` (Surface Fluxes)
  - `M2T1NXSLV` (Single-level Meteorology)
  - `M2T1NXRAD` (Radiation)
- **Version:** 5.12.4
- **Frequency:** Hourly (1-hour)
- **Source API:** NASA GES DISC (using Python `requests` with strict `Content-Type` validation).
- **Subsetting:** **None (Global)**. LIS reads these global NetCDF (`.nc4`) files natively and handles spatial subsetting dynamically at runtime.

### 3. `download_imerg.py`
- **Role:** Fetches high-resolution satellite precipitation data.
- **Data Downloaded:** `GPM_3IMERGHH` (Precipitation Final Run)
- **Version:** V07B
- **Frequency:** Half-hourly (30 mins)
- **Source API:** NASA GES DISC (using `earthaccess` library).
- **Subsetting:** The script searches for granules intersecting the Moroccan bounding box and downloads them natively to the `raw/` directory structure.

### 4. `download_merra2_const.py`
- **Role:** Fetches the static topographic constants needed by LIS/LDT for altitude-based corrections.
- **Data Downloaded:** `MERRA2_101.const_2d_asm_Nx.00000000.nc4` (Geopotential terrain height `PHIS`).
- **Why it's needed:** Crucial for the `lapse-rate` topographic correction algorithm. *Note: `job_download_merra2.sh` automatically calls this script when YEAR=2000 and Month=1.*

---

## Dependencies
- Python 3.x
- `requests` (for MERRA-2 API)
- `earthaccess` (for IMERG API & Earthdata authentication)
- `pandas` (for IMERG inventory generation)

> **Note:** Authentication requires a valid `.netrc` file configured with NASA Earthdata credentials in your home directory.

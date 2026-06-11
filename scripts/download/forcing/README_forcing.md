# Noah-MP Forcing Data Infrastructure
**Author:** M. El Aabaribaoune (@um6p)  
**Last Updated:** 2026-06-11

---

## Overview
This directory contains the automated, parallelized infrastructure for downloading the meteorological forcing datasets required to run LIS / Noah-MP simulations over the Sebou-Saïss basin (Morocco). 

The infrastructure is designed with scalability in mind, using **SLURM Job Arrays** to parallelize decadal downloads (2000–2023) and prevent HPC wall-time timeouts.

---

## How to Run

To download the full forcing dataset (2000-2023), simply submit the provided SLURM job array script from this directory:

```bash
cd scripts/download/forcing/
sbatch job_download_forcing.sh
```

**What happens under the hood?**
- SLURM launches **24 simultaneous jobs** (one for each year).
- Each job dynamically computes its `START_DATE` and `END_DATE`.
- `IMERG` and `MERRA-2` downloads run concurrently in the background for each specific year.
- Topographic constants are automatically downloaded once (tied to the year 2000 task).
- Output logs are stored cleanly in the `logs/` directory (`dl_<jobid>_<arrayid>.out`).

---

## Scripts Description

### 1. `job_download_forcing.sh`
- **Role:** The main orchestrator (SLURM Job Array).
- **Functionality:** Sets up the HPC environment (`arch_toubkal.env` + Python `venv`), handles year-by-year array indexing, and launches the Python download scripts in parallel.

### 2. `download_merra2.py`
- **Role:** Fetches global meteorological state variables and surface fluxes.
- **Data Downloaded:** 
  - `M2T1NXFLX` (Surface Fluxes)
  - `M2T1NXSLV` (Single-level Meteorology)
  - `M2T1NXRAD` (Radiation)
- **Version:** 5.12.4
- **Resolution:** 0.5° x 0.625°
- **Frequency:** Hourly (1-hour)
- **Source API:** NASA GES DISC (using Python `requests`)
- **Subsetting:** **None (Global)**. LIS reads these global NetCDF (`.nc4`) files natively and handles spatial subsetting & interpolation dynamically at runtime.

### 3. `download_imerg.py`
- **Role:** Fetches high-resolution satellite precipitation data.
- **Data Downloaded:** `GPM_3IMERGHH` (Precipitation Final Run)
- **Version:** V07B
- **Resolution:** 0.1° x 0.1°
- **Frequency:** Half-hourly (30 mins)
- **Source API:** NASA GES DISC (using `earthaccess` library)
- **Subsetting:** The script searches for granules intersecting the Moroccan bounding box. An optional `PERFORM_SUBSET` flag is provided in the code to allow local spatial subsetting (post-download) using `xarray` to save storage space.

### 4. `download_merra2_const.py`
- **Role:** Fetches the static topographic constants needed by LIS/LDT for altitude-based corrections.
- **Data Downloaded:** `MERRA2_101.const_2d_asm_Nx.00000000.nc4` (Geopotential terrain height `PHIS`).
- **Version:** 5.12.4
- **Resolution:** 0.5° x 0.625°
- **Frequency:** Static (Time-invariant)
- **Source API:** NASA GES DISC
- **Why it's needed:** Crucial for the `lapse-rate` topographic correction algorithm when running LIS with MERRA-2 forcings.

---

## Dependencies
- Python 3.x
- `requests` (for MERRA-2 API)
- `earthaccess` (for IMERG API & Earthdata authentication)
- `pandas` (for IMERG inventory generation)

> **Note:** Authentication requires a valid `.netrc` file configured with NASA Earthdata credentials in your home directory.

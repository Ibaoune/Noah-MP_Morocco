# Noah-MP Forcing Data Infrastructure
**Author:** M. El Aabaribaoune (@um6p)  
**Last Updated:** 2026-06-18

---

## Overview
This directory contains the infrastructure for downloading and verifying the meteorological forcing datasets required to run LIS / Noah-MP simulations over the Sebou-Saïss basin (Morocco). 

To ensure maximum stability when interacting with NASA's GES DISC servers (which frequently drop long-lived connections), the architecture is highly modular and **fully automated via a central orchestrator**. The download process is **decoupled** into separate IMERG and MERRA-2 SLURM scripts, and is designed to be executed **one year at a time**.

---

## How to Run

To launch the fully automated forcing data download workflow, you only need to submit the **Orchestrator** script for the starting year (e.g., 2015):

```bash
cd scripts/download/forcing/

# Start the continuous download loop for the decade
sbatch --export=ALL,YEAR=2015 job_orchestrator.sh
```

**What happens under the hood?**
1. **Orchestration:** `job_orchestrator.sh` manages the workflow. It concurrently submits `job_download_imerg.sh` and `job_download_merra2.sh` as job arrays (12 tasks, one for each month).
2. **Resilience:** If the network drops or a file fails to download, the Python scripts force a strict failure (`sys.exit(1)`). 
3. **Verification:** Once both downloads finish for the year, the orchestrator submits `job_check_single_year.sh`. This script rigorously verifies every NetCDF/HDF5 file using `h5py`. Any corrupted files are immediately deleted.
4. **Auto-Retry & Progression:** If files are missing or corrupted, the orchestrator loops back and retries downloading the year. Existing files are safely `[SKIP]`ped. If the year is 100% verified, it creates a `status_YYYY.success` file and automatically submits the job for `YEAR + 1`, chaining all the way to 2020.

---

## Scripts Description

### 1. `job_orchestrator.sh`
- **Role:** The master SLURM job.
- **Functionality:** Dispatches the monthly download arrays for both datasets, waits for their completion, dispatches the verification job, and handles infinite retries until the year is completely verified. Once a year is done, it triggers the next.

### 2. `job_download_merra2.sh` & `job_download_imerg.sh`
- **Role:** The SLURM job arrays for downloading the datasets.
- **Functionality:** Configured as `--array=1-12`. Each task handles exactly one month. Loads the `Anaconda3/2020.11` module (which provides Python 3.8 and native access to your `~/.local` packages like `earthaccess`), calculates the start and end dates, and launches the python download logic.

### 3. `job_check_single_year.sh` & `check_single_year.py`
- **Role:** Strict verification pipeline.
- **Functionality:** After a year's downloads are finished, it attempts to open every downloaded IMERG and MERRA-2 file using the `h5py` library. Any file that fails to open (network corruption/truncated download) is deleted instantly so the orchestrator can re-download it.

### 4. `download_merra2.py`
- **Role:** Fetches global meteorological state variables and surface fluxes.
- **Data Downloaded:** 
  - `M2T1NXFLX` (Surface Fluxes)
  - `M2T1NXSLV` (Single-level Meteorology)
  - `M2T1NXRAD` (Radiation)
- **Subsetting:** **None (Global)**. LIS reads these global NetCDF (`.nc4`) files natively and handles spatial subsetting dynamically at runtime.

### 5. `download_imerg.py`
- **Role:** Fetches high-resolution satellite precipitation data.
- **Data Downloaded:** `GPM_3IMERGHH` (Precipitation Final Run V07B)
- **Source API:** NASA GES DISC (using the `earthaccess` library).
- **Subsetting:** The script searches for granules intersecting the Moroccan bounding box and downloads them natively to the `raw/` directory structure.

### 6. `download_merra2_const.py`
- **Role:** Fetches the static topographic constants needed by LIS/LDT for altitude-based corrections.
- **Data Downloaded:** `MERRA2_101.const_2d_asm_Nx.00000000.nc4` (Geopotential terrain height `PHIS`).
- *Note: `job_download_merra2.sh` automatically calls this script when YEAR=2000 and Month=1.*

---

## Directory Structure & Outputs

The downloaded files are automatically organized into the `data/forcing/` directory located at the root of the project:

- **MERRA-2** : `data/forcing/MERRA2/`
  - Subdirectories : `M2T1NXFLX/`, `M2T1NXSLV/`, `M2T1NXRAD/`
  - Format : Global NetCDF (`.nc4`)
- **IMERG** : `data/forcing/IMERG/raw/`
  - Subdirectories : Organized by month (`YYYYMM/`)
  - Format : Global HDF5

## Monitoring & Troubleshooting

If you need to verify the status or resume a broken download (for instance, if years like 2008-2010 are missing days):

1. **Check the `.success` files**: When a year is successfully downloaded and 100% verified, a file named `status_YYYY.success` is created in `scripts/download/forcing/`. If this file is missing, the year is incomplete.
2. **Check the logs**: Detailed SLURM outputs and error logs are stored in `scripts/download/forcing/logs/` (e.g., `chk_yr_*.out`, `chk_yr_*.err`).
3. **Resuming a download**: Simply run the orchestrator again for the failed year. The Python scripts are designed to check file sizes and will `[SKIP]` files that are already successfully downloaded, picking up exactly where they left off:
   ```bash
   sbatch --export=ALL,YEAR=2008 job_orchestrator.sh
   ```

---

## Environment & Dependencies
The scripts rely on the official Toubkal **`Anaconda3/2020.11`** module, which loads a stable Python 3.8 environment. This environment successfully resolves to your `~/.local` directory for the `earthaccess` library.
- `requests` (for MERRA-2 API)
- `earthaccess` (for IMERG API & Earthdata authentication)
- `pandas` (for IMERG inventory generation)
- `h5py` (for file corruption verification)

> **Note:** Authentication requires a valid `.netrc` file configured with NASA Earthdata credentials in your home directory.

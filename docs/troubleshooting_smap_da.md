# SMAP Data Assimilation Troubleshooting Guide

This document tracks the implementation and troubleshooting of the SMAP Data Assimilation framework within the LIS/Noah-MP setup over the Sebou basin. It is meant to be updated progressively as issues are encountered and resolved during implementation.

## Current Setup & Progress
We have implemented the following components based on the theoretical Data Assimilation framework for the initial 3-day test (`experiments/3days/assim_tests/lis_da_smap.config`):

1. **Focus on SMAP only:** 
   - Deleted LAI configurations (`lis_da_lai.config`, `lis_da_joint.config`) to focus purely on SMAP retrieval assimilation.
2. **EnKF Perturbation Strategy:**
   - **Forcings:** Adjusted `forcing_attribs.txt` and `forcing_pertattribs.txt` to apply multiplicative perturbations exclusively to IMERG precipitation (`std=0.50`) and MERRA-2 downward shortwave radiation (`std=0.30`). Longwave perturbations were disabled.
   - **Soil Moisture State (SMC):** Maintained additive perturbations (`ptype=0`) as defined in `noahmp_sm_pertattribs.txt` (`std=0.004` on layer 1).
3. **Observation Errors:**
   - Updated the SMAP observation error standard deviation to `0.04 m³/m³` in `smap_pertattribs.txt`.
4. **Bias Correction (CDF-Matching):**
   - Configured `Data assimilation scaling strategy: "CDF matching"` in the SMAP DA configuration.
   - Pointed the CDF files to `./data/cdf/smap_model_cdf.nc` and `./data/cdf/smap_obs_cdf.nc`.

---

## Known Issues and Troubleshooting Steps

### 1. Missing CDF Files for Scaling
**Issue:** 
The LIS scaling strategy expects CDF files for both the Open-Loop model climatology and the SMAP observations (`./data/cdf/smap_model_cdf.nc`, `./data/cdf/smap_obs_cdf.nc`). However, these files have not been generated yet. If you run LIS right now, it will crash trying to open these non-existent paths.

**Resolution / Next Steps:**
- **Option A (Generate CDFs):** You need to configure and run the Land Data Toolkit (LDT) to generate these CDF files. This requires having a multi-year historical Open-Loop run (to establish climatology) and a multi-year SMAP observation record.
- **Option B (Temporary Bypass for 3-day test):** If you just want to verify that the DA algorithm initializes correctly for the 3-day window, you could temporarily set `Data assimilation scaling strategy: "anomaly"` (which only removes the mean) or `"none"`, until the actual CDF files are ready. 
- *Current Status:* Waiting for CDF files to be generated. Paths are configured as placeholders in the config.

### 2. MPI / Resource Allocation Limits (Potential)
**Issue:** 
Data assimilation uses ensemble runs (`Number of ensembles per tile: 20`), increasing memory and computational overhead significantly compared to an open-loop run.
**Resolution:** Ensure that `job_da.sh` requests sufficient nodes/tasks and that the `Number of processors along x` and `y` in the LIS config logically matches the `srun/mpirun` allocation.

### 3. State Vector / Perturbation Range Limits
**Issue:** 
If the DA state vector exceeds physical bounds (e.g., soil moisture going below residual or above porosity), Noah-MP might crash or yield NaNs.
**Resolution:** The `varmin` and `varmax` in `noahmp_sm_attribs.txt` and `smap_attribs.txt` help control this, restricting the standard deviation multiplier to avoid unphysical states. If crashes occur, review these bounds relative to soil parameter tables.

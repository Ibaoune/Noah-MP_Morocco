# Spin-Up Troubleshooting Guide
# Author: M. EL Aabaribaoune (@um6p)
This file acts as a living document to track issues, errors, and resolutions encountered during the implementation and execution of the Noah-MP cycled spin-up over the Sebou-Saïss basin. Please update this document as new issues arise.

## 1. Missing Forcing Data
**Symptom**: `check_spinup_stability.py` reports WARNINGs about missing files, or LIS crashes citing missing forcing records in `lislog`.
**Cause**: The 2015-2020 MERRA2 data might not have been fully downloaded, or the required `MERRA2_400/Y{YYYY}/M{MM}/` hierarchy has not been created from the downloaded `M2T1NXFLX` (and RAD/SLV) paths.
**Resolution**: Ensure you have run `bash spinup/scripts/reorganize_spinup_merra2.sh` after downloading the raw forcing data. This script creates the exact directory structure LIS requires and resolves missing interpolation days.

## 2. Cycle 2 or 3 Fails on Startup
**Symptom**: `job_spinup_cycle2.sh` stops immediately and reports `ERROR: Could not find Cycle 1 restart file`.
**Cause**: 
- Cycle 1 did not finish writing the final restart file.
- The `Restart output interval` in the config is set incorrectly so it didn't generate at the end of the year.
**Resolution**: Check the logs of Cycle 1 (`spinup/SPINUP_sebou/logs/lis_spinup_c1_run.log`) to ensure it finished successfully. Ensure LIS is correctly generating netcdf restart output. Check the `spinup/SPINUP_sebou/cycle1/` dir directly.

## 3. Spin-Up Stability Not Reached
**Symptom**: Running `check_spinup_stability.py` shows large differences between Cycle 2 and Cycle 3 in Deep Soil Moisture (Layer 4) or LAI.
**Cause**: The deep layers (especially groundwater or 1m soil layer) are very slow to respond to the initial cold start conditions.
**Resolution**: A 4th or 5th cycle may be required. Copy `job_spinup_cycle3.sh` to a `cycle4` script, adjust the restart inputs to point to Cycle 3, and re-run.

## 4. MPI or Slurm Allocation Errors
**Symptom**: "OOM (Out Of Memory)", segmentation faults, or `srun: error: Task launch failed` messages in the slurm error logs.
**Cause**: Currently configured for 128 tasks on 4 nodes. Sometimes node failure or excessive disk I/O causes LIS to stall.
**Resolution**: Rerun using the same configuration on a fresh queue, or if disk I/O is saturated (creating history outputs too frequently), check `MODEL_OUTPUT_LIST.TBL` to ensure diagnostic frequency is `1mo` or `1da` and not hourly unless absolutely needed.

## 5. LDT/LIS Parameter Mismatch
**Symptom**: Fatal errors indicating domain dimensions do not match the restart file.
**Cause**: The parameter file (`lis_input.d01_sebou.nc`) was regenerated with different bounds, or LIS config has wrong row/col count.
**Resolution**: Ensure no changes have been made to the core LDT Sebou config. The spin-up config should be an identical twin to the `OPL` run minus assimilation lines.

## 6. Cycle 1 Fails Immediately on Startup (MPI_ABORT / endrun)
**Symptom**: `job_spinup_cycle1.sh` crashes almost instantly. The slurm log shows `MPI_ABORT was invoked` and `lislog.0000` inside `spinup/SPINUP_sebou/cycle1/` contains `[ERR] ./data/met_forcing/MERRA2//MERRA2_400/Y2014/M12/MERRA2_400.tavg1_2d_slv_Nx.20141231.nc4 does not exist`.
**Cause**: Because LIS interpolates the hourly MERRA-2 data to the 15-minute timestep, starting the simulation precisely at `2015-01-01 00:00:00` requires reading the forcing data from the previous day (`2014-12-31`). Furthermore, LIS expects the data to be organized in the `MERRA2_400/Y{YYYY}/M{MM}/` hierarchy.
**Resolution**: Run `bash spinup/scripts/reorganize_spinup_merra2.sh`. This script reorganizes all downloaded files into the correct folder hierarchy and programmatically creates a symlink for `2014-12-31` pointing to `2015-01-01` to serve as a stable interpolation placeholder.

---
*Document Last Updated: 2026-06-03*

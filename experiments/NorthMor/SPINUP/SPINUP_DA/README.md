# SPINUP_DA: Data Assimilation Spin-up Workflow

**Author:** M. El Aabaribaoune (@um6p)

## Overview & Objectives

This directory contains the 1-year Data Assimilation spin-up experiment for the year 2015.

The goal of this experiment is to run the Ensemble Kalman Filter (EnKF) for a full year to generate statistically mature ensemble perturbations before the actual `matrix_2016` experiments begin. 

## Importance to the 2016 Matrix
Unlike the deterministic Open Loop runs, the Data Assimilation experiments in `matrix_2016` (`DA_cdf_noirr_2016` and `DA_nocdf_noirr_2016`) require two sets of initial conditions:
1. **Surface Model States** (`restarts/surf/LIS_RST_*.nc`): The physical state of the land surface.
2. **Perturbation States** (`restarts/pert/LIS_DAPERT_*.bin`): The mathematical spread of the ensemble members.

This directory successfully generated these final equilibrated states at the end of 2015, which are directly read by the 2016 experiments.

## Execution Workflow
This experiment utilizes a daisy-chaining approach (similar to `SPINUP_OPL`) orchestrated via `scripts/chain_da.py` and `job.sh`. It automatically processes month-by-month configurations to advance the assimilation filter stably.

# ENS_OPL_2015: Ensemble Open Loop Generation

**Author:** M. El Aabaribaoune (@um6p)

## Overview & Objectives

This directory is responsible for transforming a deterministic state into an ensemble state. 

Before starting the Data Assimilation spin-up in 2015 (`SPINUP_DA`), we need an ensemble of initial conditions. Since `SPINUP_OPL` only produces a single deterministic state (1 member), this directory bridges the gap by running an Ensemble Open Loop experiment.

## The Script: `expand_restart.py`
This directory contains `scripts/expand_restart.py` which takes a single deterministic restart file from the end of 2014/start of 2015 (from `SPINUP_OPL`) and duplicates its spatial fields across `N` tiles (e.g., 20 ensemble members).

## Execution Workflow
1. The script expands the deterministic restart.
2. The `chain_ens_opl.py` script orchestrates the generation of ensemble trajectories.
3. The resulting states form the necessary starting points for the Data Assimilation perturbation spin-up in `SPINUP_DA`.

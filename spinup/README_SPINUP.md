# Sebou-Saïss Basin Spin-Up Setup
# Author: M. EL Aabaribaoune (@um6p)

This directory contains the completely isolated framework for performing a cycled Noah-MP spin-up over the Sebou-Saïss basin.

## Objective
The primary objective is to prepare a stable and common initial land surface state for all subsequent production experiments (OPL, DA-SM, DA-LAI, DA-Joint) covering the 2015–2020 period. 

## Methods
*To prepare a stable and common initial land surface state for all data assimilation and open-loop experiments, a cycled spin-up strategy was conducted following the logic of Nie et al. (2022). The spin-up was performed over the 2015–2020 period using exactly the same land surface parameters, Noah-MP physics options, and meteorological forcing as the main production runs, but without any data assimilation. To ensure deep soil moisture and prognostic vegetation states reached equilibrium, the 2015–2020 forcing was repeated for three consecutive cycles. Cycle 1 was initialized from cold-start default states, while Cycles 2 and 3 were initialized from the final restart files of the preceding cycles. Diagnostics for hydrological components were generated to verify spin-up stability (Ahmad et al., 2024). The restart file generated at the end of Cycle 3 serves as the common initial condition for all 2015–2020 production experiments.*

## Directory Structure
- `configs/` : Contains the isolated LIS configuration for the spin-up, mirroring the production setup but strictly without DA.
- `jobs/` : SLURM scripts to run the three cycles.
- `scripts/` : Python scripts for diagnostics and verification (e.g., `check_spinup_stability.py`).
- `SPINUP_sebou/` : The dedicated output tree for all spin-up data, avoiding conflict with the main `experiments/` directory.

## Configuration Checklist
Before running the cycles, ensure the following match exactly with your target production experiments:
- [x] **Domain and grid**: Same as production (Sebou-Saïss)
- [x] **Land surface parameters**: Same LDT-generated files
- [x] **Noah-MP version**: 3.6
- [x] **Noah-MP physics options**: Matches exactly
- [x] **Dynamic vegetation**: Option 2 (enabled)
- [x] **Soil layer configuration**: 4 layers (0.1, 0.3, 0.6, 1.0 m)
- [x] **Timestep**: 15 mn
- [x] **Meteorological forcing**: MERRA2 2015-2020 (same variables and format)
- [x] **Data Assimilation**: DISABLED (no EnKF, no observation operators)

## Execution Sequence
1. Submit Cycle 1: `sbatch spinup/jobs/job_spinup_cycle1.sh`
2. Wait for Cycle 1 to finish successfully.
3. Submit Cycle 2: `sbatch spinup/jobs/job_spinup_cycle2.sh`
4. Wait for Cycle 2 to finish successfully.
5. Submit Cycle 3: `sbatch spinup/jobs/job_spinup_cycle3.sh`
6. Verify stability: `python spinup/scripts/check_spinup_stability.py`

Once completed, the final restart file located at `spinup/SPINUP_sebou/final_restart/restart_spinup_cycle3_2020_common_initial_state.nc` should be referenced in the main production configuration files for OPL, DA-SM, DA-LAI, and DA-Joint.

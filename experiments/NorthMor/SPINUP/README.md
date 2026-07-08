# Centralized Spin-up Directory (`SPINUP`)

**Author:** M. El Aabaribaoune (@um6p)

This repository serves as the central hub for all initial conditions and spin-up experiments required by the core matrix (`matrix_2016`) and other downstream simulations for the NorthMor domain. 

To ensure reproducibility and clean organization, the spin-up data is divided into three distinct sub-directories based on their specific roles in the experimental workflow:

## 1. `SPINUP_OPL`
* **Purpose:** Contains the baseline 10-year open-loop spin-up (2005 - 2015).
* **Role:** Generates the highly stable surface and soil initial conditions (restart files) required to launch the 2016 Open Loop (`OPL_noirr_2016`) experiment without any cold-start shocks.
* **See also:** `SPINUP_OPL/README.md` for detailed daisy-chaining execution instructions.

## 2. `SPINUP_DA`
* **Purpose:** Contains the 1-year Data Assimilation spin-up (2015).
* **Role:** Generates both the surface model initial conditions AND the **ensemble perturbation states** (`LIS_DAPERT_*.bin`) required to launch the 2016 Data Assimilation EnKF experiments (`DA_cdf_noirr_2016`, `DA_nocdf_noirr_2016`).

## 3. `ENS_OPL_2015`
* **Purpose:** Contains the open-loop ensemble generation scripts for 2015.
* **Role:** Expands the deterministic state from `SPINUP_OPL` into a multi-member ensemble, generating the initial spread required to kick off the `SPINUP_DA` EnKF assimilation in 2015.

# NorthMor Noah-MP SPINUP_OPL Workflow

**Last Updated:** 2026-06-25
# Author:  M. El Aabaribaoune(@um6p)
## Overview & Objectives

This repository contains the standalone infrastructure necessary to execute the **Noah-MP Land Surface Model spin-up** over the NorthMor domain. 

The primary objective of a spin-up experiment is to run sequential simulations, using the final hydrological and thermal states (soil moisture, temperature, snow depth) of the previous period as the initial condition (restart file) for the current period. This ensures that the model reaches a state of physical equilibrium before conducting the actual analysis.

### The Daisy-Chaining Architecture
To efficiently simulate long, multi-year periods on High-Performance Computing (HPC) clusters, this workflow uses an automated **daisy-chaining** architecture:
1. A Python script generates the configuration and SLURM job for a single simulation period (e.g., 1 year).
2. The SLURM job executes the Noah-MP simulation.
3. Upon successful completion, the SLURM job extracts the generated restart file and automatically re-invokes the Python script from the compute node to submit the job for the *next* chronological period.

This methodology eliminates wasteful idle wait-times that occur when an orchestrator script continually polls the cluster queue. It ensures the workflow runs sequentially and resiliently.

---

##  Completed Spin-Up Run (2005 - 2015)

A full 10-year spin-up has already been successfully executed on this domain to achieve a stable equilibrium state for the land surface variables.

**Run Details:**
- **Start Date:** `2005-01-01` (Coldstart)
- **End Date:** `2016-01-01`
- **Period Length:** 1 Year (`1Y`)
- **Status:**  Successfully completed. 
- **Final Output:** The final robust restart file generated from this 10-year spin-up is available at:
  `restarts/LIS_RST_NOAHMP401_201601010000.d01.nc`

This restart file serves as the perfect, fully-equilibrated initial condition for any subsequent Assimilation (DA) or Open Loop (OL) experiments starting from January 1st, 2016.

---

## Repository Structure

The workflow is completely self-contained within this directory:

- **`config/`**: Contains `experiment.ini`, the central configuration file defining dates, periods, and simulation modes.
- **`scripts/`**: Contains `chain_spinup.py`, the core Python script that implements the daisy-chaining logic (generating configurations and submitting SLURM jobs).
- **`templates/`**: Contains the baseline LIS configuration template (`lis_spinup.config.template`) with placeholders (e.g., `__START_YEAR__`).
- **`generated/`**: A working directory where the Python script automatically outputs the compiled LIS configurations (`configs/`) and SLURM batch scripts (`jobs/`).
- **`output/`**: Directory where raw LIS NetCDF output files are stored, organized by period (e.g., `output/2008/`).
- **`restarts/`**: Centralized storage for the `.d01.nc` restart files. These files are linked sequentially to connect the periods.
- **`logs/`**: Directory containing SLURM standard error (`.err`) and output (`.log`) files for debugging and monitoring.
- **`job.sh`**: A master batch script used to securely kick off the daisy-chain workflow.

---

## Installation & Requirements

1. **Python Environment:** Requires `python3` with standard libraries. Ensure `python3-dateutil` is installed if running in a virtual environment.
2. **Computing Environment:** Relies on the SLURM workload manager. Ensure `sbatch`, `squeue`, and `mpirun` are available.
3. **LIS Executable:** The workflow assumes the LIS executable is compiled and available at `../../../src/lisf/lis/LIS` relative to this directory.
4. **Environment Setup:** The job script loads the necessary environment via `../../../arch/arch_toubkal.env`. Verify this path matches your HPC setup.

---

## Configuration Steps

All parameters for the spin-up experiment are centralized in `config/experiment.ini`. Before running, review this file:

```ini
[Experiment]
# Simulation start date (Format: YYYY-MM-DD)
StartDate = 2008-01-01

# Simulation end date (Format: YYYY-MM-DD). The chain will stop here.
EndDate   = 2016-01-01

# Length of a single simulation chunk (1Y, 1M, or 1D)
PeriodLength = 1Y

# Initialization mode for the VERY FIRST period. 
# Options: 'coldstart' or 'restart'.
InitMode = restart

# Experiment identifier
ExperimentName = spinup

# Path to the base LIS configuration template
TemplateFile = templates/lis_spinup.config.template
```
*Note: If `InitMode = restart`, ensure the appropriate restart file from the previous date exists in the `restarts/` directory before starting.*

---

## Execution Workflow: Batch Job Submission

To avoid executing continuous scripts interactively on the login node, the workflow should be initiated via a dedicated SLURM batch job.

Submit the `job.sh` script to kick off the chain:

```bash
sbatch job.sh
```

**What happens next?**
1. `job.sh` runs as a short SLURM task, sets up the environment, and triggers `chain_spinup.py`.
2. `chain_spinup.py` reads `experiment.ini`, verifies inputs, generates the configuration for the first year (e.g., 2008), and submits it to SLURM as a new job (e.g., `spinup_2008`).
3. The initial `job.sh` exits cleanly.
4. The compute job `spinup_2008` runs for up to 12 hours. Upon completion, it copies its output restart file to `restarts/` and invokes `chain_spinup.py` again to submit the job for 2009.
5. This cycle continues autonomously until `EndDate` is reached.

### Monitoring
Check the SLURM queue to see the active job:
```bash
squeue -u $USER
```
Check the generated `.log` and `.err` files inside the `logs/` directory for live output.

---

## Troubleshooting Guidance

- **The chain stopped prematurely:**
  Check the latest `.err` file in the `logs/` directory. The job likely aborted because:
  - LIS encountered an error (e.g., `MPI_ABORT`, missing meteorological forcing data).
  - The expected restart file was not generated or couldn't be copied.

- **Resuming after a failure:**
  If a specific year fails (e.g., 2010), fix the underlying issue (e.g., download missing data). Then, resume the chain from that exact year by manually running the Python script or temporarily editing `job.sh`:
  
  ```bash
  python3 scripts/chain_spinup.py --current-date 2010-01-01 --submit
  ```
  Since the restart file from 2009 is already in `restarts/`, the chain will cleanly resume from 2010 and continue to the end.

---

## 6. Log Management and Directory Structure

The logging system automatically routes all SLURM standard output/error files and LIS diagnostic logs into period-specific subdirectories under `logs/`. This prevents the `logs/` directory from becoming cluttered during long simulations.

The directory structure dynamically reflects the actual execution period based on `PeriodLength`:

**For yearly runs (`PeriodLength = 1Y`):**
```text
logs/
├── 2008/
├── 2009/
├── 2010/
└── ...
```

**For monthly runs (`PeriodLength = 1M`):**
```text
logs/
├── 012008/
├── 022008/
├── 032008/
└── ...
```

**For daily runs (`PeriodLength = 1D`):**
```text
logs/
├── 20080101/
├── 20080102/
├── 20080103/
└── ...
```

*Note: The initial kickoff batch job (`job.sh`) writes its output directly to the root `logs/` folder (e.g., `logs/kickoff_%j.log`) as it applies to the entire chain launch.*

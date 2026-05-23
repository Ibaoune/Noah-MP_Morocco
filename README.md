# NoahMP-LIS Morocco — Soil Moisture Data Assimilation

Land surface modeling and soil moisture data assimilation over Morocco
using NASA's **Land Information System (LIS)** with **NoahMP 3.6** and
**SMAP** satellite observations via Ensemble Kalman Filter (EnKF).

**Author:** M. EL Aabaribaoune (@um6p)  
**HPC:** Toubkal cluster, UM6P  
**Project:** EMPOWERMED

---

## Directory Structure

```
NoahMP_Morocco/
│
├── arch/                     # HPC environment setup
│   ├── arch_toubkal.env      #   Toubkal module loads (source this)
│   └── README.md             #   Compilation notes
│
├── src/                      # Source code
│   └── lisf/                 #   NASA LISF framework
│       ├── ldt/              #     Land Data Toolkit (preprocessing)
│       ├── lis/              #     Land Information System (model)
│       └── lvt/              #     Land Verification Toolkit
│
├── configs/                  # Configuration files
│   ├── ldt.config            #   LDT config (generate lis_input.d01.nc)
│   ├── lis.config.opl        #   LIS Open-Loop experiment
│   ├── lis.config.da         #   LIS Data Assimilation (EnKF + SMAP)
│   ├── MODEL_OUTPUT_LIST.TBL #   Output variable selection
│   └── forcing_variables.txt #   Forcing variable definitions
│
├── scripts/                  # All executable scripts
│   ├── jobs/                 #   SLURM job scripts
│   │   ├── job_1_ldt.sh      #     Step 1: Run LDT
│   │   ├── job_2_lis_opl.sh  #     Step 2: Open-Loop simulation
│   │   ├── job_3_lis_da.sh   #     Step 3: Data Assimilation
│   │   └── job_scalability.sh#     Scalability testing
│   ├── download/             #   Data download scripts
│   │   ├── download_smap.py
│   │   ├── download_merra2.py
│   │   ├── download_parameters.py
│   │   └── reorganize_merra2.sh
│   ├── fix/                  #   Data fix/correction scripts
│   │   ├── fix_gtopo.py
│   │   └── fix_mptable.py
│   ├── submit_all.sh         #   Submit scalability tests
│   └── generate_configs.sh   #   Generate scalability configs
│
├── data/                     # Input data
│   ├── met_forcing/MERRA2/   #   MERRA-2 meteorological forcing
│   ├── land_params/          #   Land surface parameters
│   │   ├── noah_2dparms/     #     NoahMP tables (VEGPARM, SOILPARM, etc.)
│   │   └── topo_parms/       #     Topography (GTOPO30)
│   ├── observations/SMAP/    #   SMAP soil moisture (SPL3SMP v009)
│   ├── pert_package/         #   Perturbation attributes (DA)
│   └── lis_input.d01.nc      #   Domain/parameter file (LDT output)
│
├── experiments/              # Model outputs (by experiment)
│   ├── OPL/                  #   Open-Loop results
│   ├── DA/                   #   Data Assimilation results
│   └── scalability/          #   Scalability test results
│
├── postproc/                 # Post-processing & visualization
│   ├── scripts/              #   Analysis scripts
│   └── figures/              #   Generated figures
│
├── logs/                     # Centralized logs
│   ├── slurm/                #   SLURM job logs
│   └── *.log                 #   Download & run logs
│
└── docs/                     # Documentation
    ├── TROUBLESHOOTING_LOG.md
    └── COMPILATION_AND_STATUS_SUMMARY.txt
```

## Quick Start

### 1. Setup environment

```bash
source arch/arch_toubkal.env
```

### 2. Generate domain parameters (LDT)

```bash
sbatch scripts/jobs/job_1_ldt.sh
```

### 3. Run Open-Loop simulation

```bash
sbatch --nodes=1 --ntasks=32 scripts/jobs/job_2_lis_opl.sh
```

### 4. Run Data Assimilation (EnKF + SMAP)

```bash
sbatch --nodes=2 --ntasks=64 scripts/jobs/job_3_lis_da.sh
```

## Domain

| Parameter | Value |
|-----------|-------|
| Region | Morocco (central) |
| Latitude | 33.00°N — 34.50°N |
| Longitude | 5.50°W — 3.50°W |
| Resolution | 0.01° (~1 km) |
| Grid size | 200 × 150 = 30,000 cells |
| Period | Jun — Aug 2020 |
| Timestep | 15 min |

## Experiments

| Experiment | Description | Config |
|------------|-------------|--------|
| **OPL** | Open-Loop (no data assimilation) | `configs/lis.config.opl` |
| **DA** | EnKF with SMAP soil moisture (12 ensembles) | `configs/lis.config.da` |

## Forcing & Observations

- **Meteorological forcing:** MERRA-2 (NASA, hourly)
- **Observations:** SMAP L3 soil moisture (SPL3SMP v009, daily)
- **Land surface model:** NoahMP v3.6
- **Data assimilation:** Ensemble Kalman Filter (EnKF, 12 members)

## Dependencies

Compiled with the **foss/2024a** toolchain on Toubkal:
- GCC 13.3.0, OpenMPI 5.0.3
- NetCDF 4.9.2 + Fortran 4.6.1
- ESMF 8.7.0, HDF5 1.14.5
- JasPer 4.2.4, ecCodes 2.38.3

## Scalability Analysis

A comprehensive scalability analysis was conducted on the Toubkal cluster to optimize the LIS NoahMP simulation runtimes for Morocco (200x150 grid size).

### Setup details
- **Period:** 3-day simulation (Jun 01 - Jun 04 2020)
- **MPI Task Allocation:** Tested with 4, 16, 32, 64, 128, 256, 512, and 896 tasks
- **Node Configurations:** Sourced from 1 to 28 compute nodes (max 32 tasks per node to prevent memory saturation)
- **Experiments:** Open-Loop (OPL) vs. Data Assimilation (DA, 12 ensemble members)
- **Launch Command:** `mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS`

### Performance Results

| Run Configuration | Nodes | MPI Tasks | OPL Time | OPL Speedup | DA Time | DA Speedup |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Baseline** | 1 | 4 | 3m 59s | 1.00x | 47m 07s | 1.00x |
| **1 Node (16t)** | 1 | 16 | 1m 06s | 3.58x | 12m 04s | 3.90x |
| **1 Node (32t)** | 1 | 32 | 38.8s | 6.18x | 6m 10s | 7.63x |
| **2 Nodes** | 2 | 64 | 32.0s | 7.48x | 3m 21s | 14.00x |
| **4 Nodes** | 4 | 128 | 21.8s | 11.01x | 1m 57s | 24.01x |
| **8 Nodes** | 8 | 256 | 44.8s | 5.35x | 1m 27s | 32.31x |
| **16 Nodes** | 16 | 512 | 43.8s | 5.47x | 1m 12s | 39.16x |
| **28 Nodes** | 28 | 896 | 42.8s | 5.59x | 41.5s | 67.98x |

### Key Findings & Recommendations
1. **Open-Loop (OPL):**
   - Runtimes scale well up to **128 tasks (4 nodes)**, reaching a speedup of **11.0x**.
   - Beyond 128 tasks, performance **degrades** (~44s) due to communication overhead dominating the small grid computation (each task processes < 100 grid cells).
   - **Recommendation:** Use **128 tasks (4 nodes with 32 tasks/node)** for OPL production runs.

2. **Data Assimilation (DA):**
   - DA is highly compute-intensive (12 ensembles). It scales exceptionally well up to **896 tasks (28 nodes)**, achieving a **68.0x speedup** (runtime drops from 47 minutes to 41.5 seconds!).
   - **Recommendation:** Use **896 tasks (28 nodes with 32 tasks/node)** for DA production runs to maximize cluster throughput and reduce simulation time.

### Scalability Performance Plot
The scalability curves are plotted below:
![Scalability Performance](postproc/figures/lis_scalability_performance.png)


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

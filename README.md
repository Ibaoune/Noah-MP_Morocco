# NoahMP-LIS Morocco — Soil Moisture Data Assimilation

Land surface modeling and soil moisture data assimilation over Morocco
using NASA's **Land Information System (LIS)** with **NoahMP 4.0.1** and
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
│   ├── ldt.config            #   LDT config (original Morocco domain)
│   ├── ldt.config.sebou      #   LDT config (Sebou basin domain)
│   ├── lis.config.opl        #   Open-Loop experiment (original domain)
│   ├── lis.config.opl_sebou  #   Open-Loop experiment (Sebou basin)
│   ├── lis.config.da         #   DA: SMAP SM only (original domain)
│   ├── lis.config.da_sm_sebou   #   DA: SMAP SM only (Sebou basin)
│   ├── lis.config.da_lai_sebou  #   DA: MODIS LAI only (Sebou basin)
│   ├── lis.config.da_sebou   #   DA: SMAP SM + MCD15A2H LAI — joint test (Sebou)
│   ├── lis.config.da_joint   #   DA: joint long-run config (2015-2020)
│   ├── MODEL_OUTPUT_LIST.TBL #   Output variable selection
│   └── forcing_variables.txt #   Forcing variable definitions
│
├── scripts/                  # All executable scripts
│   ├── jobs/                 #   SLURM job scripts
│   │   ├── job_1_ldt.sh               #     Step 1: LDT (original domain)
│   │   ├── job_1_ldt_sebou.sh         #     Step 1: LDT (Sebou basin)
│   │   ├── job_2_lis_opl.sh           #     Step 2: Open-Loop
│   │   ├── job_2_lis_opl_sebou.sh     #     Step 2: Open-Loop (Sebou)
│   │   ├── job_3a_lis_da_sm_sebou.sh  #     Step 3a: DA — SMAP SM only
│   │   ├── job_3b_lis_da_lai_sebou.sh #     Step 3b: DA — MODIS LAI only
│   │   ├── job_3c_lis_da_joint_sebou.sh #   Step 3c: DA — Joint (SM + LAI)
│   │   ├── job_preprocess_modis_lai.sh#     Preprocess HDF → NetCDF4
│   │   └── job_scalability.sh         #     Scalability testing
│   ├── fix/                  #   Data fix/correction scripts
│   │   ├── fix_gtopo.py
│   │   ├── fix_mptable.py
│   │   └── preprocess_modis_lai.py    #     HDF tile → global NetCDF4
│   └── utils/                #   Utility and setup scripts
│       ├── create_test_config.py
│       ├── migrate.sh
│       ├── update_param_paths.py
│       └── upgrade_configs.py
│
├── data/                     # Centralized Data Acquisition & Preprocessing
│   ├── scripts/              #   Data acquisition and preprocessing scripts
│   ├── logs/                 #   Data acquisition SLURM logs
│   ├── reports/              #   Automated inventory CSVs
│   ├── forcing/              #   Meteorological forcing (IMERG, GDAS)
│   ├── assimilation/         #   Assimilation datasets (SMAP, MODIS)
│   ├── validation/           #   Validation datasets (ASCAT, LAI, GRACE)
│   ├── land_params/          #   NoahMP parameters & Topography
│   ├── pert_package/         #   Perturbation attributes (DA)
│   ├── lis_input.d01_sebou.nc#   Sebou domain/parameter file (LDT output)
│   └── README_data_acquisition.md # Detailed data workflow documentation
│
├── experiments/              # Model outputs (by experiment)
│   ├── OPL_sebou/            #   Open-Loop results
│   ├── DA_SM_sebou/          #   SMAP SM assimilation results
│   ├── DA_LAI_sebou/         #   MODIS LAI assimilation results
│   ├── DA_Joint_sebou/       #   Joint SM+LAI assimilation results
│   └── scalability/          #   Scalability test results
│
├── postproc/                 # Post-processing & visualization
│   ├── scripts/              #   Analysis scripts
│   └── figures/              #   Generated figures
│
├── logs/                     # Centralized logs
│   ├── slurm/                #   SLURM job logs
│   ├── slurm_archive/        #   Archived generic execution logs
│   └── *.log                 #   Download & run logs
│
└── docs/                     # Documentation
    ├── TROUBLESHOOTING_LOG.md
    ├── COMPILATION_AND_STATUS_SUMMARY.txt
    └── EXPERIMENT_SETUP.md
```

## Quick Start

### 1. Setup environment

```bash
source arch/arch_toubkal.env
```

### 2. Generate domain parameters (LDT — Sebou Basin)

```bash
sbatch scripts/jobs/job_1_ldt_sebou.sh
```

### 3. Run Open-Loop simulation

```bash
sbatch scripts/jobs/job_2_lis_opl_sebou.sh
```

### 4. Preprocess MODIS LAI observations

Required before running DA-LAI or DA-Joint experiments:
```bash
sbatch scripts/jobs/job_preprocess_modis_lai.sh
```

### 5. Run Data Assimilation experiments

```bash
# 3a — SMAP Soil Moisture assimilation only
sbatch scripts/jobs/job_3a_lis_da_sm_sebou.sh

# 3b — MODIS LAI assimilation only (needs preprocessing step above)
sbatch scripts/jobs/job_3b_lis_da_lai_sebou.sh

# 3c — Joint assimilation: SMAP SM + MODIS LAI
sbatch scripts/jobs/job_3c_lis_da_joint_sebou.sh
```

## Domain

| Parameter | Value |
|-----------|-------|
| Region | Sebou River basin & Saïss plain |
| Latitude | 32.50°N — 35.50°N |
| Longitude | 7.00°W — 3.50°W |
| Resolution | 0.01° (~1 km) |
| Grid size | 300 × 350 = 105,000 cells |
| Period | Jun — Aug 2020 |
| Timestep | 15 min |

## Experiments

| # | Experiment | Description | Config | Output Dir |
|---|------------|-------------|--------|------------|
| **OPL** | Open-Loop | No assimilation (ensemble mean) | `lis.config.opl_sebou` | `experiments/OPL_sebou/` |
| **DA-SM** | SM Assimilation | EnKF + SMAP soil moisture (20 ens.) | `lis.config.da_sm_sebou` | `experiments/DA_SM_sebou/` |
| **DA-LAI** | LAI Assimilation | EnKF + MODIS MCD15A2H LAI (20 ens.) | `lis.config.da_lai_sebou` | `experiments/DA_LAI_sebou/` |
| **DA-Joint** | Joint Assimilation | EnKF + SMAP SM **+** MODIS LAI (20 ens.) | `lis.config.da_joint` | `experiments/DA_Joint_sebou/` |

## Forcing & Observations

- **Meteorological forcing:** GDAS (NASA, 2015–2020) and GPM IMERG Final V07
- **Soil Moisture Observations:** SMAP L3 SPL3SMP v009 (daily, 2015–2020)
- **LAI Observations:** MODIS MOD15A2H v061, tile `h17v05` (8-day, 2015–2020), preprocessed to global NetCDF4
- **Land surface model:** NoahMP v4.0.1 with dynamic vegetation (`option=2`)
- **Data assimilation:** Ensemble Kalman Filter (EnKF, 20 members)
- **Perturbations:** GMAO scheme — precipitation, radiation, soil moisture state, LAI state

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

## Sebou Basin Joint DA Experiment

An expanded multi-year experiment has been designed over the entire upstream Sebou River basin (`32.5° N — 35.5° N` and `7.0° W — 3.5° W` at 1 km resolution) for the period 2015–2020, matching the study period in Nie et al. (2022).

### Current Status
*   **Domain parameters (LDT):** Successfully processed. Generated the NetCDF parameter file `data/lis_input.d01_sebou.nc`.
*   **Domain parameter maps:** Visualizations for [Topography](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_topography.png), [Land Cover](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_landcover.png), and [Soil Texture](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_soil_texture.png) have been plotted and saved to `postproc/figures/`.
*   **Forcings & Observations downloads:** Staged and running on Toubkal.

### Main Research Axes
*   **Hydrology Focus (Paper 1):** Assimilation of SMAP soil moisture and MODIS LAI into Noah-MP to improve root-zone soil moisture, evapotranspiration (ET), baseflow, and streamflow routing (using HYMAP).
*   **Agriculture Focus (Paper 2):** Ingesting observations to assess dynamic crop water stress, GPP, and dynamic sprinkler/drip irrigation allocation volumes.

For detailed configurations, datasets, and job launch instructions, please refer to the dedicated guide:
*   [docs/EXPERIMENT_SETUP.md](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/docs/EXPERIMENT_SETUP.md)

## Evaluation and Post-Processing

A dedicated Python module is provided to extract variables, compute spatial averages, and visualize spatial/temporal impacts across Data Assimilation setups. 
*   **DA Analysis script:** `scripts/plot_da_comparison.py` extracts Surface/Root-Zone Soil Moisture, Evapotranspiration, Runoff, and LAI to generate spatial difference maps (`Δ DA - OPL`) and basin-averaged temporal comparisons.
*   **DA Increments script:** `scripts/plot_da_increments.py` parses EnKF assimilation diagnostics (`*_incr.*.nc`) to visualize temporal adjustments applied by the filter (aligning with Nie et al. 2022).
*   **Result Plots:** Are deposited into `experiments/plots/` upon successful execution.




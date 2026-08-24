# NoahMP-LIS Morocco — Soil Moisture Data Assimilation

Land surface modeling and soil moisture data assimilation over Morocco
using NASA's **Land Information System (LIS)** with **NoahMP 4.0.1** and
**SMAP** satellite observations via Ensemble Kalman Filter (EnKF).

**Author:** M. EL Aabaribaoune (@um6p)  
**HPC:** Toubkal cluster, UM6P  

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
│   ├── NorthMor/
│   │   ├── matrix_2016/      #   Core SMAP DA matrix (5 baseline experiments)
│   │   ├── step3_da_2015/    #   Long-run DA experiments
│   │   └── 1Yr_2016/         #   One-year evaluation configurations
│   ├── OPL_sebou/            #   Legacy Open-Loop results
│   ├── DA_SM_sebou/          #   Legacy SMAP SM assimilation results
│   ├── scalability/          #   Scalability test results
│   └── 3days/                #   3-day Validation & DA Tests
│       ├── opl/              #     Open Loop run
│       ├── assim_tests/      #     SMAP, LAI, and Joint DA runs
│       └── README_exps.md    #     Detailed guide for 3-day tests
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
├── docs/                     # Documentation
│   ├── TROUBLESHOOTING_LOG.md
│   ├── COMPILATION_AND_STATUS_SUMMARY.txt
│   └── EXPERIMENT_SETUP.md
│
└── assim_AI/                 # AI component for explaining assimilation behavior
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

## Forcing, Observations & Validation

- **Meteorological forcing:** GDAS (NASA, 2015–2020) and GPM IMERG Final V07
- **Assimilation:**
  - SMAP L3 SPL3SMP v009 (daily, 2015–2020)
  - MODIS MOD15A2H v061, tile `h17v05` (8-day, 2015–2020)
- **Validation Datasets:**
  - ASCAT (Soil Moisture)
  - Copernicus LAI (Vegetation)
  - GRACE (Terrestrial Water Storage anomalies)
  - GLEAM (Evapotranspiration)
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

## 3-Day Validation & Data Assimilation Tests

Before running the multi-year joint assimilation, a complete test environment is set up over a **3-day window (2020-02-01 to 2020-02-04)** to validate the EnKF configuration, forcing perturbations, and observation processing (following the methodology in Nie et al., 2022).

These tests are isolated in `experiments/3days/`:
- **Open Loop (OPL)**: A fast baseline reference simulation using 32 tasks (`experiments/3days/opl`).
- **Data Assimilation (DA)**: Three separate configurations testing 1D EnKF with 20 ensemble members (`experiments/3days/assim_tests`):
  - SMAP Soil Moisture assimilation
  - MODIS LAI assimilation
  - Joint (SMAP + LAI) assimilation

Please refer to `experiments/3days/README_exps.md` for detailed configuration settings and launch instructions for these test cases.

## Sebou Basin Joint DA Experiment

An expanded multi-year experiment has been designed over the entire upstream Sebou River basin (`32.5° N — 35.5° N` and `7.0° W — 3.5° W` at 1 km resolution) for the period 2015–2020, matching the study period in Nie et al. (2022).

### 2016 Core SMAP DA Matrix
Before executing the full 2015-2020 runs, a highly controlled 1-year validation matrix has been established in `experiments/NorthMor/matrix_2016/`. 
This matrix strictly focuses on isolating the impact of **SMAP Assimilation** without the noise of irrigation models or dynamic LAI. It includes 5 fundamental experiments:
1. `OPL_noirr_2016`: Baseline open-loop without irrigation.
2. `DA_nocdf_noirr_2016`: SMAP EnKF without CDF matching.
3. `DA_cdf_noirr_2016`: SMAP EnKF with CDF matching.
4. `DA_SMAP_inflation_sensitivity_2016`: EnKF spread/inflation tests.
5. `DA_SMAP_obs_error_sensitivity_2016`: Observation error parameter tests.

Please refer to `experiments/NorthMor/matrix_2016/README.md` for launch instructions.

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

A modern, highly modular, YAML-driven post-processing pipeline has been established to visualize hydrology states and fluxes, strictly separating scientific data loading from visual styling.

*   **YAML Configurations:** Located in `configs/postproc/hydrology_visuals/`. Each hydrological variable (e.g., `baseflow.yaml`, `total_runoff.yaml`) has its own configuration specifying NetCDF variable names, multipliers, fallback calculation logic (e.g. weighted mean for RZSM), colormaps, bounds, and layout preferences.
*   **Universal Runner:** The core script `scripts/postproc/scripts/run_hydrology_postproc.py` dynamically ingests these YAML files to generate standardized multi-panel figures:
    - `01_<variable>_annual_mean_<year>`
    - `02_<variable>_differences_<year>` (e.g. DA-CDF minus OPL)
    - `03_<variable>_domain_mean_timeseries_<year>`
*   **Reproducibility:** Every execution produces a `processing_log.yaml` detailing exact NetCDF files read, aliases used, calculated percentiles, and statistical metrics, along with a `resolved_config.yaml`.
*   **Execution Launchers:** Available in `jobs/postproc_hydrology/`:
    - `run_all_local.sh`: Processes all variables locally in sequence.
    - `submit_all_hydrology.sh`: Submits one SLURM job per variable for parallel HPC execution.
    - `run_one_hydro_variable.sh`: Core wrapper script for a single variable configuration.

*Note: Older hardcoded Python scripts (e.g., `plot_runoff.py`, `plot_da_comparison.py`) remain in `scripts/postproc/src/` as legacy reference materials.*

## AI-Based Assimilation Diagnostics (`assim_AI`)

A dedicated AI/Machine Learning component is included in the `assim_AI/` directory. This project uses machine learning techniques (such as Random Forests and Explainable AI) to diagnose and explain the behavior of the data assimilation experiments.
* Evaluates the hydrological response and sensitivity of assimilation increments.
* Helps interpret the impact of assimilating observations on the core model variables.
* Includes its own independent documentation, scripts, and environment configurations.

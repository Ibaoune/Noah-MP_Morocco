# DA_nocdf_noirr_2016_2020 — Historical SMAP-EnKF Data Assimilation Simulation (2016–2020)

**Author:** Mohammad El Aabaribaoune

---

## 1. Scientific Overview, Objectives & Domain Definition

The `DA_nocdf_noirr_2016_2020` experiment constitutes the **unscaled satellite data assimilation (NoCDF) component** of the 5-year experimental matrix ($2016\text{--}2020$) for Northern Morocco. It integrates NASA SMAP L3 enhanced surface soil moisture retrievals into the Noah-MP land surface model using a 1D Ensemble Kalman Filter (EnKF) across 20 ensemble members, without statistical bias correction (CDF matching) and with anthropogenic irrigation deactivated.

```
                             [ Master Spin-up Hierarchy ]
  Stage 1: SPINUP_OPL (2005–2016) ──► 11-Year Deterministic Climatological Equilibrium (1 member)
                                           │
                                           │ [2015-01-01 Checkpoint: 10 completed years (2005–2014)]
                                           ▼ scripts/expand_restart.py (20x tile replication)
  Stage 2: ENS_OPL_2015 (Jan–Apr 2015) ──► 3-Month Ensemble Perturbation Spin-up (GMAO noise, No DA)
                                           │
                                           ▼ 2015-03-31 Checkpoint (staged to 2015-04-01)
  Stage 3: SPINUP_DA (Apr–Dec 2015)   ──► 9-Month SMAP EnKF Assimilation Spin-up
                                           │
                                           ▼ 2016-01-01 Checkpoints (surf: 21 MB, pert: 137 MB)
  ┌────────────────────────────────────────┴────────────────────────────────────────┐
  ▼                                                                                 ▼
DA_nocdf_noirr_2016_2020                                                 DA_cdf_noirr_2016_2020
(Raw SMAP Assimilation, NoCDF)                                           (CDF-Scaled SMAP Assimilation)
```

### 1.1 Scientific Objectives
1. **Unscaled Satellite Assimilation Benchmark:** Quantify the hydrological response when satellite surface soil moisture retrievals are assimilated in their raw volumetric state space ($\text{m}^3/\text{m}^3$) without adjusting for systematic mean and dynamic range differences between the satellite retrieval algorithm and the land surface model.
2. **CDF Sensitivity Comparison:** Serve as the unscaled counterfactual to evaluate the impact of Cumulative Distribution Function (CDF) matching in `DA_cdf_noirr_2016_2020`. Comparing NoCDF against CDF assimilation provides empirical evidence on the structural effects of mean-state shifts versus transient innovation updates (noting that DA-CDF scaling calibration is investigated independently).
3. **Multi-Year Ensemble Land Surface Reanalysis:** Produce a continuous 5-year, 20-member ensemble reanalysis of root-zone soil moisture, evapotranspiration, runoff partitioning, and water table dynamics across Northern Morocco under active Kalman updating.

### 1.2 Domain Specification
* **Domain Name:** Northern Morocco (`NorthMor`)
* **Spatial Extent:** $30.00^\circ\text{N}$ to $36.00^\circ\text{N}$ Latitude; $-10.00^\circ\text{E}$ to $-1.00^\circ\text{E}$ Longitude.
* **Grid Resolution:** $0.05^\circ$ regular lat/lon grid spacing (~$5\text{ km}$ nominal resolution; $121 \times 181$ grid points).
* **Active Land Grid:** $16,030$ active land tiles over Morocco extracted from [`data/lis_input/lis_input_NorthMor_5km.nc`](../../../../data/lis_input/lis_input_NorthMor_5km.nc).
* **Ensemble Dimension:** 20 members per land tile, yielding $16,030 \times 20 = 320,600$ computational tiles.

---

## 2. Model Framework, Physics & Meteorological Forcing

The simulation physics are defined in [`templates/lis_da.config.template`](templates/lis_da.config.template) and executed using the Land Information System Framework (LISF).

### 2.1 Model Discretization and Architecture
* **Land Surface Model:** Noah-MP version 4.0.1.
* **Simulation Timestep:** 15 minutes (`15mn`).
* **Parallel Layout:** 1 node, 32 MPI tasks ($4 \times 8$ 2D spatial decomposition).
* **Soil Discretization:** 4 vertical layers with layer node thicknesses of $0.1\text{ m}$ (Layer 1: $0\text{--}10\text{ cm}$), $0.3\text{ m}$ (Layer 2: $10\text{--}40\text{ cm}$), $0.6\text{ m}$ (Layer 3: $40\text{--}100\text{ cm}$), and $1.0\text{ m}$ (Layer 4: $100\text{--}200\text{ cm}$), totaling $2.0\text{ m}$ total soil depth.
* **Snowpack Discretization:** Up to 3 physics-based prognostic snow layers.

### 2.2 Noah-MP Physical Parameterizations
* **Runoff and Groundwater:** Option `1` (SIMGM - Simple Groundwater Model; explicit unconfined dynamic aquifer model with prognostic water table depth).
* **Dynamic Vegetation:** Option `2` (Dynamic phenology / on-line carbon allocation; prognostic Leaf Area Index).
* **Canopy Stomatal Resistance:** Option `1` (Ball-Berry formulation).
* **Radiation Transfer:** Option `1` (Modified two-stream scheme).
* **Surface Layer Drag Coefficient:** Option `1` (Monin-Obukhov similarity theory).
* **Snow Surface Albedo:** Option `1` (BATS scheme).
* **Precipitation Partitioning:** Option `1` (Jordan91 scheme).
* **Soil Temperature Lower Boundary:** Option `2` (Thermal diffusion).
* **Crop Model / Irrigation:** Option `0` (`Irrigation scheme: "none"`, irrigation OFF).

### 2.3 Meteorological Forcing Architecture
The experiment couples two meteorological forcing datasets via the LIS multi-forcing architecture (`LIS_rc%nmetforc = 2`):
1. **Base Forcing (Source 1):** NASA MERRA-2 reanalysis (`data/forcing/MERRA2/`), providing 3D lowest-model-level atmospheric states (temperature, humidity, pressure, surface wind) and downward shortwave/longwave radiation, with MERRA-2 corrected precipitation.
2. **Precipitation Overlay (Source 2):** NASA GPM IMERG Final Run V07B (`data/forcing/IMERG/raw/`), providing half-hourly, $0.1^\circ$ calibrated satellite precipitation overlaying the base atmospheric fields.
3. **Ensemble Forcing Allocation:** In [`src/lisf/lis/core/LIS_metforcingMod.F90:1279-1296`](../../../../src/lisf/lis/core/LIS_metforcingMod.F90#L1279-L1296), `ensembleForcings` divides the 20 ensemble members across the 2 forcing sources:
   - **Cohort 1 (Members 1–10):** Driven by MERRA-2 meteorological forcing.
   - **Cohort 2 (Members 11–20):** Driven by MERRA-2 base fields overlaid with GPM IMERG precipitation.

---

## 3. SMAP Observation Ingestion & EnKF Configuration

### 3.1 Observation Dataset Specifications
* **Observation Product:** NASA SMAP Level-3 Enhanced Radiometer Global Daily 9 km EASE-Grid Soil Moisture (`SPL3SMP_E`).
* **Data Directory:** `./data/observations/SMAP_SPL3SMP_E`
* **Retrieval Characteristic:** Volumetric soil moisture ($\text{m}^3/\text{m}^3$) representing the top $0\text{--}5\text{ cm}$ of the soil column.
* **Product Version & Release:** ECS Version ID `006`, Composite Release ID `R19240` (specified as `"R19"` in LIS configuration).
* **Quality Control Architecture:**
  - **Retrieval Quality Control:** `SMAP(NASA) soil moisture apply SMAP QC flags: 1`. Ingests the quality control bit flags from the SMAP HDF5 product files to exclude retrievals affected by frozen ground, heavy vegetation biomass, complex topography, snow cover, or open water bodies.
  - **Noah-MP Model Quality Control:** Applied within LIS prior to filter updates. Screens observations against physical bounds ($0.01 \le \theta_{\text{obs}} \le 1.0\text{ m}^3/\text{m}^3$ defined in `data/pert_package/smap_attribs.txt`), enforces model soil moisture limits ($0.01 \le \theta_{\text{model}} \le 0.55\text{ m}^3/\text{m}^3$ defined in `data/pert_package/noahmp_sm_attribs.txt`), and deactivates updates if the model surface soil temperature is at or below freezing ($T \le 273.15\text{ K}$) or if snow cover is present on the grid cell.

### 3.2 Assimilation Algorithm & Scaling Strategy
* **Data Assimilation Algorithm:** 1-Dimensional Ensemble Kalman Filter (`1D EnKF`, `Number of data assimilation instances: 1`).
* **Ensemble Size:** 20 members (`Number of ensembles per tile: 20`).
* **Scaling Strategy:** `Data assimilation scaling strategy: "none"` (**NoCDF**). SMAP observations are ingested directly in their native volumetric space without CDF matching or variance adjustment.
* **State Update Vector:** `Number of state variables: 4`. Volumetric soil moisture across all 4 vertical layers is registered in the Kalman state vector, with increments distributed vertically based on ensemble background error cross-correlations.
* **Observation Perturbation Scheme:** GMAO perturbation scheme (`data/pert_package/smap_pertattribs.txt`), additive Gaussian noise (`perttype = 0`), standard deviation $\sigma_v = 0.04\text{ m}^3/\text{m}^3$ (consistent with SMAP mission target accuracy), truncation limit `std_max = 2.5` ($\pm 0.10\text{ m}^3/\text{m}^3$), zero mean (`zeromean = 1`), temporal decorrelation timescale $43,200\text{ s}$ (12 hours), spatial correlation length $0.0$, and cross-variable correlation $1.0$.

---

## 4. Ensemble Initialization & Restart Provenance

The 20-member ensemble for `DA_nocdf_noirr_2016_2020` was initialized from historical checkpoints generated by the upstream spin-up hierarchy:

### 4.1 Upstream Spin-up Lineage
1. **Stage 1 — `SPINUP_OPL` ($2005\text{--}2016$):** 11-year deterministic simulation producing climatological equilibrium. After 10 completed years ($2005\text{--}2014$), the intermediate checkpoint `LIS_RST_NOAHMP401_201501010000.d01.nc` (1 member, 16,030 tiles, 1.6 MB) was extracted to initialize ensemble generation. The final checkpoint at 2016-01-01 (`LIS_RST_NOAHMP401_201601010000.d01.nc`) concluded the full 11-year deterministic spin-up and initialized deterministic experiments (such as `OPL_noirr_2016_2020`), NOT `ENS_OPL_2015`.
2. **Expansion — `scripts/expand_restart.py`:** Replicated each deterministic tile from the 2015-01-01 checkpoint 20 times into contiguous 20-member blocks, creating `LIS_RST_NOAHMP401_201501010000_ens20.d01.nc` (320,600 tiles, 90 MB) with zero initial cross-member variance.
3. **Stage 2 — `ENS_OPL_2015` ($2015-01-01\text{ to }2015-04-01$):** 3-month unassimilated ensemble spin-up generating initial perturbation covariance structures under GMAO forcing and state noise.
4. **Stage 3 — `SPINUP_DA` ($2015-04-01\text{ to }2016-01-01$):** 9-month active SMAP assimilation spin-up establishing dynamic background error covariance before launching 2016 production runs.

### 4.2 Consumed Checkpoints at 2016-01-01
On January 1, 2016, `chain_da.py` initialized `DA_nocdf_noirr_2016_2020` directly from the final restarts of `SPINUP_DA`:
* **Surface Model Restart:**  
  `experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc` (21,451,770 bytes).
* **Perturbation State Restart:**  
  `experiments/NorthMor/SPINUP/SPINUP_DA/restarts/pert/LIS_DAPERT_201601010000.d01.bin` (137,219,692 bytes).

---

## 5. Execution Chronology & 60-Month Chaining Workflow

The 5-year simulation was divided into 60 sequential monthly segments ($2016-01\text{ to }2020-12$) orchestrated by [`scripts/chain_da.py`](scripts/chain_da.py).

### 5.1 Orchestration Mechanism
For each month $M$:
1. `chain_da.py` generated `generated/configs/lis_DA_SMAP_nocdf_noirr_{YYYY-MM}.config` by substituting dates, paths, and restart pointers into `templates/lis_da.config.template`.
2. Generated the corresponding SLURM batch script `generated/jobs/job_DA_SMAP_nocdf_noirr_{YYYY-MM}.sh`.
3. Executed `./src/lisf/lis/LIS` across 32 MPI tasks on 1 node.
4. Upon successful completion (`set -e`), the job script copied the end-of-month restarts stamped `${next_date}0000` to `restarts/surf/` and `restarts/pert/`.
5. Triggered the next monthly segment via `python3 scripts/chain_da.py --current-date {next_date} --submit`.

### 5.2 Historical Execution Timeline
The 60 monthly jobs executed between July 24, 2026 and July 28, 2026 on HPC Toubkal under the SLURM account `empowermed-ahl6xm8o7mg-DEFAULT-CPU`:
* **Launch Date:** July 24, 2026 at 11:28 (Job `7344623`, period 2016-01).
* **Completion Date:** July 28, 2026 at 07:49 (Job `7372247`, period 2020-12).
* **Chaining Status:** All 60 monthly SLURM tasks ran sequentially without human interruption or segmentation faults.

---

## 6. Output Organization, Restarts & Data Assimilation Diagnostics

### 6.1 Directory Layout
```
DA_nocdf_noirr_2016_2020/
├── config/                      # Experiment parameters & date bounds (planned for Git tracking)
│   └── experiment.ini
├── templates/                   # Base LISF/Noah-MP configuration template (planned for Git tracking)
│   └── lis_da.config.template
├── scripts/                     # Chaining and restart automation script (planned for Git tracking)
│   └── chain_da.py
├── generated/                   # 60 monthly generated configs and SLURM scripts (preserved in later commits)
│   ├── configs/                 # 60 monthly lis.config files
│   └── jobs/                    # 60 monthly SLURM job scripts
├── restarts/                    # Checkpoint archive (Lustre-only, untracked)
│   ├── surf/                    # 60 monthly surface restarts (LIS_RST_NOAHMP401_*.nc, ~21 MB each)
│   └── pert/                    # 60 monthly perturbation restarts (LIS_DAPERT_*.bin, ~137 MB each)
├── logs/                        # Historical execution logs (Lustre-only, untracked)
│   └── <MMYYYY>/                # Monthly SLURM logs (*.log, *.err) and 32 MPI task logs (lislog_*.0000-0031)
└── output/                      # Primary simulation outputs (Lustre-only, untracked)
    └── <YYYY-MM>/               # Monthly output root
        ├── SURFACEMODEL/<YYYYMM>/ # Daily LIS_HIST_*.nc history files (ensemble mean states/fluxes)
        ├── EnKF/<YYYYMM>/         # Instantaneous EnKF analysis increments and innovations at update steps
        ├── DAOBS/<YYYYMM>/        # Gridded observation files at assimilation timesteps (LISDAOBS_*.1gs4r)
        └── DAPERT/<YYYYMM>/       # Monthly LIS_DAPERT_*.bin perturbation state checkpoints
```

*Note on Repository Tracking & Preservation Strategy:*
* **Core Experiment Definitions:** The primary configuration, template, chaining script, and this documentation ([`config/experiment.ini`](config/experiment.ini), [`templates/lis_da.config.template`](templates/lis_da.config.template), [`scripts/chain_da.py`](scripts/chain_da.py), and `README.md`) define the experimental setup and will be tracked directly in Git.
* **Generated Run Configurations:** The 60 historical monthly generated LIS configuration files (`generated/configs/`) and 60 SLURM job scripts (`generated/jobs/`) record exact historical execution parameters and will be preserved later in separate dedicated Git commits.
* **Excluded Simulation Products:** High-volume binary restarts (`restarts/`), primary simulation outputs (`output/`), and detailed raw MPI logs (`logs/`) remain excluded from version control in accordance with [`.gitignore`](../../../../.gitignore) to maintain repository efficiency.

### 6.2 Data Assimilation Diagnostic Variables
Data assimilation diagnostics are stored across two distinct output streams:

1. **Instantaneous EnKF Diagnostic Files (`output/<YYYY-MM>/EnKF/<YYYYMM>/`):**  
   At each observation assimilation timestep, LIS archives instantaneous 2D fields:
   * **`LIS_DA_EnKF_YYYYMMDDHHMM_innov.a01.d01.nc`:**
     - **`ninnov_01` (`Normalized_innovations_for_DA_instance_01`):** Normalized innovation $(y - H \bar{x}^f) / \sqrt{H P^f H^T + R}$ (dimensionless). Unobserved or rejected grid cells contain missing-value `-9999.0`. Non-missing innovations indicate that an observation was paired with a background tile and passed initial retrieval screening, but they are not automatically proof of accepted EnKF updates (subsequent filter checks or local conditions can prevent state updates).
     - **`innov_01` (`Innovations_for_DA_instance_01`):** Raw observation innovation $d = y - H \bar{x}^f$ in volumetric units ($\text{m}^3/\text{m}^3$). Unobserved grid cells contain missing-value `-9999.0`. Non-missing innovations confirm observation pairing, but do not guarantee that the filter accepted or applied a Kalman update.
     - **`analysis_residual_01` (`Analysis_residuals_for_DA_instance_01`):** Analysis residual $y - H x^a$ in volumetric units ($\text{m}^3/\text{m}^3$).
     - **`forecast_sigma_01` (`Forecast_variance_for_DA_instance_01`):** Total forecast innovation variance $H P^f H^T + R$ in $(\text{m}^3/\text{m}^3)^2$.
   * **`LIS_DA_EnKF_YYYYMMDDHHMM_incr.a01.d01.nc`:**
     - **`anlys_incr_Soil Moisture Layer [1-4]_01`:** Kalman analysis increment ($x^a - x^f$) applied to each of the 4 soil moisture layers in volumetric units ($\text{m}^3/\text{m}^3$). Inactive mask points and ocean cells evaluate to `-9999.0`, while active land cells receive numerical `0.0` whenever no non-zero update was applied. Zero increments alone cannot distinguish missing observations, rejected observations, zero innovations, zero Kalman gain, or other filter update conditions.

2. **Daily History Files (`output/<YYYY-MM>/SURFACEMODEL/<YYYYMM>/`):**  
   Daily history files (`LIS_HIST_YYYYMMDD0000.d01.nc`) contain 24-hour ensemble-mean prognostic states and surface fluxes, including 4-layer soil moisture (`SoilMoist_tavg`), soil temperature (`SoilTemp_tavg`), water table depth (`WaterTableD_tavg`), terrestrial water storage (`TWS_tavg`), groundwater storage (`GWS_tavg`), and surface energy/water fluxes (`Qle_tavg`, `Qh_tavg`, `Evap_tavg`, `Qs_tavg`, `Qsb_tavg`).

---

## 7. Verified Implementation Characteristics & Technical Limitations

Detailed source code inspections in `src/lisf/` and statistical evaluations across historical restarts established the following technical facts:

### 7.1 Interleaved 20-Member NetCDF Restart Indexing
In surface restart NetCDF files (`LIS_RST_NOAHMP401_*.d01.nc`), dimensions are `ntiles = 320600` and `dim2 = 4`. The 20 ensemble members are stored consecutively cell-by-cell in an interleaved structure:
$$\text{SMC}[\text{layer}, \text{tile}] \equiv \text{SMC}[\text{layer}, \text{cell}, \text{member}]$$
where $\text{tile} = (\text{cell}-1) \times 20 + \text{member}$ ($1 \le \text{cell} \le 16,030$; $1 \le \text{member} \le 20$).

### 7.2 Deterministic State Perturbation Exclusion for Members 10 and 20
In [`src/lisf/lis/core/LIS_lsmMod.F90:1181-1205`](../../../../src/lisf/lis/core/LIS_lsmMod.F90#L1181-L1205), LIS implements the Ryu et al. (2009) perturbation bias-correction scheme by partitioning the ensemble into sub-groups according to `nmetforc = 2`:
$$\text{nxx} = \frac{\text{LIS\_rc\%nensem}}{\text{LIS\_rc\%nmetforc}} = \frac{20}{2} = 10$$
* **Cohort 1 ($f=1$, MERRA-2):** Sub-indices $m = 1 \dots 10$. Terminal member $m = \text{nxx} = 10 \implies$ **Member 10**.
* **Cohort 2 ($f=2$, IMERG):** Sub-indices $m = 1 \dots 10$. Terminal member $m = \text{nxx} = 10 \implies$ **Member 20**.
* **Exclusion Logic:** Lines 1190 and 1198 apply perturbations only `if (m .ne. nxx)`. When $m = 10$, this condition evaluates to **FALSE**.
* **Direct Result:** **Members 10 and 20 receive ZERO prognostic state perturbations (`stvar = stvar + pert`).**
* Because `data/pert_package/noahmp_sm_pertattribs.txt` specifies state perturbations exclusively for Layer 1 ($\sigma = 0.004\text{ m}^3/\text{m}^3$) and zero for Layers 2–4, Members 10 and 20 exhibit $\sim 35\%\text{--}45\%$ lower spatial standard deviation in Layer 1 than the other 18 members ($0.036\text{--}0.042$ vs $0.065\text{ m}^3/\text{m}^3$ at 2016-01-01), while deeper layers have near-unity variance ratios ($0.93\text{--}0.99$).
* *Analytical Scope:* This behavior is established directly from workspace source-code analysis; no quantitative claims are made regarding its specific net impact on Kalman gain weighting or overall assimilation skill.

### 7.3 Configuration Bias-Correction Flag Overridden in Source Code
In all configuration files, `Apply perturbation bias correction: 0` was specified. However, in [`src/lisf/lis/core/LIS_readConfig.F90:793-798`](../../../../src/lisf/lis/core/LIS_readConfig.F90#L793-L798), reading this attribute is commented out and `LIS_rc%pert_bias_corr = 1` is **unconditionally hardcoded**. The user configuration was overridden by the compiled code.

### 7.4 Forcing Perturbation Indexing Inconsistency (`k` vs `f`)
In [`src/lisf/lis/core/LIS_metforcingMod.F90:1450-1470`](../../../../src/lisf/lis/core/LIS_metforcingMod.F90#L1450-L1470), forcing bias correction contains an indexing inconsistency:
* **Initial Perturbation Application (lines 1428–1447):** Checks `if (m .ne. LIS_rc%nensem(n))`. Only Member 20 is bypassed from initial forcing noise; Member 10 is perturbed.
* **Offset Accumulation Loop (line 1459):** Indexes tile $t = (j-1) \times 20 + \mathbf{(k-1) \times 10} + m$. Because $k=1$ (constant domain nest index), this evaluates to $(1-1) \times 10 = 0$ for both forcing cohorts ($f=1$ and $f=2$).
* **Cross-Forcing Offset:** For Cohort 2 ($f=2$, IMERG), the offset $\delta$ is computed by subtracting Member 20 (IMERG) from Cohort 1 members (MERRA-2) rather than Cohort 2 members (IMERG). This offset is then subtracted from Cohort 2 members (11–19).

### 7.5 Demonstrated Physical Forcing Cohorts
The parameter `LIS_rc%nmetforc = 2` mathematically partitions the 20 members into two 10-member cohorts. In [`LIS_metforcingMod.F90:1287-1296`](../../../../src/lisf/lis/core/LIS_metforcingMod.F90#L1287-L1296), Members 1–10 retain MERRA-2 precipitation, while Members 11–20 receive GPM IMERG precipitation where valid data exists.

### 7.6 LISF 7.5 Source Identification & Historical Binary Provenance
* Source notices across `LIS_readConfig.F90`, `LIS_lsmMod.F90`, `LIS_metforcingMod.F90`, and `build_version.sh` are stamped `Land Information System Framework (LISF) Version 7.5 (2024)`.
* Job logs from Job 7260790 match line 2490 in `gmaopert_Mod.F90` exactly, establishing direct line correspondence between the workspace source code and the execution environment.
* Binary `./src/lisf/lis/LIS` (16,666,992 bytes) resides outside version control without archived build flags or commit-stamped version manifests. Behaviors documented here represent deductions from the current workspace source code.

### 7.7 Downstream Postprocessing Directory-Path Mismatch
In [`scripts/postproc/`](../../../../scripts/postproc/), several postprocessing and validation routines failed to locate outputs because they expected history files at `output/SURFACEMODEL/` or referenced `matrix_2016/DA_nocdf_noirr_2016/output`, whereas the production chaining script wrote outputs to monthly nested folders (`output/<YYYY-MM>/SURFACEMODEL/<YYYYMM>/LIS_HIST_*.nc`).

### 7.8 Execution Success vs. Scientific Validation
The complete 60-month execution of `DA_nocdf_noirr_2016_2020` without software crashes confirms technical and numerical stability of the chained workflow. Logged outputs show steady execution across all periods. However, operational completion does not inherently establish the physical validity, filter optimality, or accuracy of the resulting soil moisture reanalysis; formal scientific validation against independent in-situ hydrometeorological observations across Morocco (e.g., local soil moisture probe stations, agricultural lysimeters, or eddy covariance towers) remains required. Furthermore, claims of complete absence of NaNs across all uninspected model state arrays require exhaustive multi-variable verification before being asserted as proven.

---

## 8. Reproducibility Limitations & Core Definition Files

Independent reproducibility is constrained by the following documented repository conditions:

1. **Git Tracking Status & Preservation Strategy:**
   * Line 5 of [`.gitignore`](../../../../.gitignore#L5) specifies `experiments/`.
   * **Core Experiment Definitions:** [`README.md`](README.md), [`config/experiment.ini`](config/experiment.ini), [`scripts/chain_da.py`](scripts/chain_da.py), and [`templates/lis_da.config.template`](templates/lis_da.config.template) define the mathematical and numerical setup and will be tracked in Git.
   * **Generated Run Configurations:** The 60 historical monthly generated LIS configuration files (`generated/configs/`) and 60 SLURM job scripts (`generated/jobs/`) record exact historical execution parameters and will be preserved later in separate dedicated Git commits.
   * **Excluded Simulation Products:** High-volume binary restarts (`restarts/`), primary simulation outputs (`output/`), and detailed raw MPI logs (`logs/`) remain excluded from version control in accordance with [`.gitignore`](../../../../.gitignore) to maintain repository efficiency.
2. **Hardcoded Absolute Paths:**
   [`scripts/chain_da.py`](scripts/chain_da.py) contains hardcoded Lustre paths:
   * Line 58: `base_dir = "/home/mohammad.elaabaribao/lustre/.../experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"`
   * Lines 105, 110: Points to `/home/mohammad.elaabaribao/.../experiments/NorthMor/SPINUP/SPINUP_DA/restarts/`
3. **External Dataset Dependencies:**
   The simulation ingested external forcing datasets (MERRA-2, IMERG) and SMAP observation files (`./data/observations/SMAP_SPL3SMP_E`) stored without cryptographic checksum manifests.
4. **Core Definition Files:**
   * [`config/experiment.ini`](config/experiment.ini): Prescribes the master simulation date bounds and template linkage.
   * [`templates/lis_da.config.template`](templates/lis_da.config.template): Parametric specification of Noah-MP physics, SMAP observation ingestion, and EnKF options.
   * [`scripts/chain_da.py`](scripts/chain_da.py): Encapsulates monthly chunking, template substitution, restart copying, and SLURM chaining.
   * [`README.md`](README.md): Scientific documentation, verified implementation mechanisms, and reproducibility assessment.

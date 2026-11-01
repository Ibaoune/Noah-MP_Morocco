# OPL_noirr_2016_2020 — Noah-MP Open-Loop Simulation

**Author:** Mohammad El Aabaribaoune

---

## 1. Scientific Overview & Role in Project Matrix

The `OPL_noirr_2016_2020` experiment represents the baseline **Open Loop (OL) reference simulation** of the 5-year experimental matrix for Northern Morocco. It simulates natural land surface hydrology under historical meteorological forcing without data assimilation and with anthropogenic irrigation deactivated.

### Experiment Metadata & Technical Scope
* **Experiment Identifier:** `OPL_noirr_2016_2020`
* **Domain:** Northern Morocco (`data/lis_input/lis_input_NorthMor_5km.nc`, regular lat/lon 0.05° resolution, ~5 km, $121 \times 181$ grid points)
* **Simulation Period:** 2016-01-01 00:00:00 to 2021-01-01 00:00:00 (5 calendar years / 60 monthly simulation segments)
* **Model Framework:** NASA Land Information System (LIS) v7.4 / Noah-MP LSM v4.0.1
* **Repository Path:** `experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/` (Branch: `main`)

### Core Roles in the Research Framework
1. **Unperturbed Climatological Baseline:** Provides the natural, unperturbed hydrological benchmark against which all Data Assimilation (DA) experiments (`DA_nocdf_noirr_2016_2020`, `DA_cdf_noirr_2016_2020`, `DA_anomaly_noirr_2016_2020`) are evaluated.
2. **Model Reference for NASA SMAP CDF Generation:** The 60 months of simulated surface soil moisture (layer 1, 0–10 cm) serve as the model reference climatology. In [`experiments/NorthMor/matrix_2016_2020/CDF/`](../CDF/), LDT ingests these outputs to generate empirical Cumulative Distribution Functions (`smap_model_cdf.nc`) for observation bias correction and scaling. *(Note: Downstream CDF generation and observation scaling are independent post-processing steps and are not evaluated or validated by this open-loop documentation).*
3. **Hydrological Routing Base Fluxes:** Modeled surface runoff (`Qs`) and subsurface baseflow (`Qsb`) time series provide unperturbed lateral flux inputs for the offline HyMAP river routing model (developed in [`experiments/NorthMor/routing/`](../../routing/)). *(Note: Downstream HyMAP discharge simulations are conducted separately and are not validated by this document).*
4. **Benchmark for Independent Evaluation:** Serves as the primary reference run for the evaluation framework in [`scripts/postproc/`](../../../../scripts/postproc/) (in-situ streamflow, FluxSat GPP, GLEAM/WaPOR evapotranspiration, and satellite soil moisture).

---

## 2. Model & Physics Configuration

The simulation physics are parameterized in [`templates/lis_opl.config.template`](templates/lis_opl.config.template) and executed via LIS 7.4.

* **Land Surface Model:** Noah-MP version 4.0.1
* **Simulation Timestep:** 15 minutes (`15mn`)
* **Parallel Execution Layout:** 1 node, 32 MPI tasks ($4 \times 8$ 2D spatial decomposition).
* **Ensemble Size:** 1 member (`Number of ensembles per tile: 1`). Deterministic open-loop run without perturbation (`Forcing perturbation algorithm: "none"`, `State perturbation algorithm: "none"`).
* **Data Assimilation:** Completely disabled (`Number of data assimilation instances: 0`, algorithm: `"none"`, scaling: `"none"`).
* **Output Intervals & Format:**
  * Surface Model History: Daily (`1da`), NetCDF format, 3-level hierarchy (`output/<YYYY-MM>/SURFACEMODEL/<YYYYMM>/LIS_HIST_*.nc`).
  * Model Restarts: Monthly (`1mo`), NetCDF format.
* **Vertical Discretization:**
  * Soil Layers (4): Layer thicknesses 0.1 m, 0.3 m, 0.6 m, 1.0 m (total soil column depth: 2.0 m).
  * Snow Layers (3): Up to 3 physics-based snow layers.
* **Physics Options:**
  * **Runoff and Groundwater:** Option `1` (SIMGM - Simple Groundwater Model; dynamic unconfined aquifer with explicit prognostic water table depth).
  * **Dynamic Vegetation:** Option `2` (Dynamic phenology / on-line carbon allocation; prognostic Leaf Area Index).
  * **Canopy Stomatal Resistance:** Option `1` (Ball-Berry formulation).
  * **Radiation Transfer:** Option `1` (Modified two-stream scheme).
  * **Surface Layer Drag Coefficient:** Option `1` (Monin-Obukhov similarity theory).
  * **Snow Surface Albedo:** Option `1` (BATS scheme).
  * **Precipitation Partitioning:** Option `1` (Jordan91 scheme).
  * **Soil Temperature Lower Boundary:** Option `2` (Thermal diffusion).
  * **Irrigation Scheme:** `none` (`crop model option: 0`, irrigation OFF).
* **Static Parameter Tables & Spatial Inputs:**
  * Domain & Spatial Parameters: [`./data/lis_input/lis_input_NorthMor_5km.nc`](../../../../data/lis_input/lis_input_NorthMor_5km.nc) (elevation, soil texture, landmask, greenness from LDT).
  * Vegetation Parameters: `./data/land_params/noahmp401_parms/VEGPARM.TBL`
  * Soil Parameters: `./data/land_params/noahmp401_parms/SOILPARM.TBL`
  * General Parameters: `./data/land_params/noahmp401_parms/GENPARM.TBL`
  * Noah-MP Table: `./data/land_params/noahmp401_parms/MPTABLE.TBL`
  * Model Output Variable Registry: [`./shared/MODEL_OUTPUT_LIST.TBL`](../../../../shared/MODEL_OUTPUT_LIST.TBL)
  * Forcing Variable Registry: [`./shared/forcing_variables.txt`](../../../../shared/forcing_variables.txt)

---

## 3. Meteorological Forcing Configuration

The meteorological forcing blends high-resolution satellite precipitation with reanalysis atmospheric fields:

1. **Atmospheric State & Energy Forcing:** NASA MERRA-2 ([`./data/forcing/MERRA2`](../../../../data/forcing/MERRA2))
   * Variables: 2m air temperature, specific humidity, surface pressure, 10m wind components, downward shortwave and longwave radiation fluxes.
   * Settings: Lowest model level (`1`), corrected total precipitation (`1`), topographic lapse-rate elevation correction enabled.
2. **Precipitation Forcing:** NASA GPM IMERG Final Run V07B ([`./data/forcing/IMERG/raw/`](../../../../data/forcing/IMERG/raw/))
   * Settings: Product `final`, half-hourly satellite precipitation calibrated against monthly rain gauges.
3. **Blending Method:** `overlay`
   * IMERG satellite precipitation overrides MERRA-2 precipitation across the domain.
4. **Spatial & Temporal Interpolation:**
   * Spatial: Bilinear interpolation from native forcing grids to the 0.05° model grid.
   * Temporal: Linear interpolation to the 15-minute LSM timestep.

---

## 4. Spin-up & Initialization Provenance

* **Initialization Mode:** `restart` mode (configured in [`config/experiment.ini`](config/experiment.ini) and rendered into LIS configuration).
* **Initial State Source (Month 1, 2016-01-01 00:00):**
  * File: [`experiments/NorthMor/SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201601010000.d01.nc`](../../SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201601010000.d01.nc)
  * Properties: Size `1,517,650 bytes` (~1.5 MB), timestamp `2026-06-26 12:46:40`.
  * **SHA-256 Checksum:** `422f8d3e79a9d2f9779c87bd5283de15d189b41990973e93bf8b43200c8f584e`
  * Provenance: Generated as the terminal restart of the 11-year spin-up simulation (2005–2015 inclusive) in [`experiments/NorthMor/SPINUP/SPINUP_OPL/`](../../SPINUP/SPINUP_OPL/).
  * Staging Note: In [`scripts/chain_opl.py`](scripts/chain_opl.py#L100), month 1 initialization directly targets the spin-up restart directory. The local `restarts/` directory therefore begins with `LIS_RST_NOAHMP401_201602010000.d01.nc`.
* **Aquifer Initialization & Equilibrium Status:**
  * The parameter value `4900.0 mm` in `lis.config` represents the coldstart default value for initial unconfined aquifer storage (`Noah-MP.4.0.1 initial water in the aquifer: 4900.0`), applied only during initial coldstart runs.
  * In restart mode, dynamic aquifer storage is ingested directly from state variable `WA` in the restart NetCDF (domain mean: $4787.84\,\text{mm}$ in the 2016-01-01 spin-up restart; $4780.71\,\text{mm}$ in the subsequent 2017-01-01 boundary restart).
  * *Hydrological Convergence Note:* The 11-year deterministic spin-up provides modeled initial conditions for the simulation, while formal hydrological equilibrium and deep groundwater convergence remain unverified.

---

## 5. Experiment Structure & Daisy-Chaining Architecture

The simulation was orchestrated via an automated SLURM daisy-chaining Python script ([`scripts/chain_opl.py`](scripts/chain_opl.py)) designed to execute monthly simulation chunks sequentially on HPC compute nodes.

### Directory Inventory

| Directory | Content | Role |
| :--- | :--- | :--- |
| [`config/`](config/) | [`experiment.ini`](config/experiment.ini) | Master parameters: `StartDate=2016-01-01`, `EndDate=2021-01-01`, `PeriodLength=1M`, `InitMode=restart`. |
| [`scripts/`](scripts/) | [`chain_opl.py`](scripts/chain_opl.py) | Python orchestrator: date calculations, template substitutions, job generation, restart propagation. |
| [`templates/`](templates/) | [`lis_opl.config.template`](templates/lis_opl.config.template) | Master LIS configuration template containing domain and physics definitions with placeholder tokens. |
| [`generated/configs/`](generated/configs/) | 60 `.config` files | Rendered monthly LIS configs (`lis_opl_noirr_YYYY-MM.config`). |
| [`generated/jobs/`](generated/jobs/) | 60 `.sh` scripts | Rendered monthly SLURM batch scripts (`job_opl_noirr_YYYY-MM.sh`). |
| [`restarts/`](restarts/) | 60 NetCDF files | Staged monthly boundary restart files (`LIS_RST_NOAHMP401_YYYYMM010000.d01.nc`). |
| [`logs/`](logs/) | 60 folders (`MMYYYY/`) | 32 MPI diagnostic rank logs (`lislog_*.0000`..`.0031`), plus SLURM `.log` and `.err` files. |
| [`output/`](output/) | 60 folders (`YYYY-MM/`) | Daily history NetCDFs (`SURFACEMODEL/YYYYMM/LIS_HIST_*.nc`) and month-end boundary restarts. |

### Execution Mechanism & Directory Navigation

1. **Invocation:** `python3 scripts/chain_opl.py --current-date <YYYY-MM-01> --submit`  
   *(The script calls `os.chdir(base_dir)` to ensure execution within the experiment directory).*
2. **Configuration Rendering:** `chain_opl.py` writes `generated/configs/lis_opl_noirr_<YYYY-MM>.config` and `generated/jobs/job_opl_noirr_<YYYY-MM>.sh`.
3. **Execution Environment:** When the SLURM batch script launches on the compute node, it navigates to the repository root:
   ```bash
   cd /home/mohammad.elaabaribao/lustre/.../NoahMP_Morocco/
   source arch/arch_toubkal.env
   time mpirun -n 32 ./src/lisf/lis/LIS -f /home/.../OPL_noirr_2016_2020/generated/configs/lis_opl_noirr_<YYYY-MM>.config
   ```
4. **Restart Staging & Chaining:** The batch script locates the newly produced boundary restart from the monthly output folder, copies it into `restarts/`, returns to `base_dir`, and executes:
   ```bash
   cd /home/.../OPL_noirr_2016_2020/
   python3 scripts/chain_opl.py --current-date <next_date> --submit
   ```
5. **Termination:** When `next_date >= EndDate`, the job prints `echo "Chain complete!"` and exits cleanly.

---

## 6. Execution History & Physical Dataset Verification

A systematic verification of SLURM execution logs, MPI diagnostic outputs, and cryptographic hashes established the complete historical execution record across all 60 months:

### Complete Chronology of Historical Execution

The 5-year simulation was executed in **three distinct historical phases**:

```
[Phase 1: 2017-01 to 2020-07] -------> [2020-08 Abort]
     (July 18, 2026: Jobs 7318092 - 7319137)     (Job 7319141)
                                                      |
[Phase 2: 2020-08 Recovery to 2020-12] <-------------+
     (July 21, 2026: Jobs 7328453 - 7328801)
                                                      
[Phase 3: 2016-01 to 2016-12]
     (July 31, 2026: Jobs 7390805 - 7391303)  <-- Consolidated after Phase 1 & 2
```

* **Phase 1 (2017–2020 Initial Segment):** Executed on **July 18, 2026 between 11:46:56 and 20:15:32**.
  * Chained months 13 to 55 (`2017-01` to `2020-07`, 43 months) continuously via SLURM Job IDs `7318092` through `7319137`.
  * **August 2020 Failure:** Month 56 (`2020-08`) initially failed on July 18 under Job `7319141` (`MPI_ABORT` logged after 10m36s in [`logs/082020/opl_noirr_2020-08_7319141.err`](logs/082020/opl_noirr_2020-08_7319141.err)), halting the chain.
* **Phase 2 (2020-08 Recovery & Completion):** Executed on **July 21, 2026 between 13:33:02 and 14:34:38**.
  * Resubmitted month 56 (`2020-08`) under Job `7328453` using the intact staged restart `restarts/LIS_RST_NOAHMP401_202008010000.d01.nc`.
  * Completed successfully in 12m08s and chained through month 60 (`2020-12`) via Jobs `7328581`, `7328602`, `7328622`, and `7328801`.
* **Phase 3 (2016 Consolidation Segment):** Executed on **July 31, 2026 between 21:38:30 and 23:59:58**.
  * Chained months 1 to 12 (`2016-01` to `2016-12`, 12 months) via SLURM Job IDs **`7390805` through `7391303`** (averaging 11–12 minutes walltime per month).
  * Executed with `EndDate = 2017-01-01` in `config/experiment.ini`, concluding with `echo "Chain complete!"` at month 12 under Job `7391303`. `config/experiment.ini` was subsequently updated to `EndDate = 2021-01-01` on August 1 at 00:37.

### Physical Dataset Integrity & Coverage

| Metric | Target (2016–2020) | Verified on Disk | Status |
| :--- | :---: | :---: | :---: |
| Monthly Output Subdirectories | 60 | 60 (`output/2016-01` to `output/2020-12`) | **VERIFIED** |
| Monthly Boundary Restarts | 60 | 60 (`restarts/LIS_RST_...20160201` to `20210101`) | **VERIFIED** |
| Daily History NetCDF Files | 1,827 days | 1,827 files (`20160102` to `20210101`) | **VERIFIED** |
| Missing Calendar Days | 0 | 0 | **VERIFIED** |
| Duplicate Daily Timestamps | 0 | 0 | **VERIFIED** |
| Restart SHA-256 (Output vs Staged) | 60 matches | 60 matches / 0 mismatches | **VERIFIED** |

*Note on Daily Timestamps:* In LIS daily accumulation mode (`1da`), the history file timestamped `YYYYMMDD0000.d01.nc` represents the 24-hour accumulation from day $N-1$ 00:00 to day $N$ 00:00. The initial file is `LIS_HIST_201601020000.d01.nc` (covering Jan 1, 2016) and the final file is `LIS_HIST_202101010000.d01.nc` (covering Dec 31, 2020). The last day of month $M$ resides in the subfolder for month $M+1$. No gaps or timestamp collisions exist.

*Storage Footprint:* `output/`: 3.7 GB | `logs/`: 1.8 GB | `restarts/`: 89 MB | `generated/`: 972 KB | **Total: 5.5 GB**.

---

## 7. Author-Confirmed 2016–2017 Sequence & Provenance

### Confirmed Historical Workflow
The experiment author confirmed the following historical execution sequence:

1. **Independent 2016 Precursor Simulation:** The year 2016 was initially simulated independently in the precursor experiment directory `experiments/NorthMor/matrix_2016/OPL_noirr_2016/` (active in Git between commits `7d0c039` and `f230640`).
2. **Restart Re-use for 2017–2020:** The resulting boundary restart (`LIS_RST_NOAHMP401_201701010000.d01.nc`) was used to initialize the subsequent 2017–2020 simulation (staged in `matrix_2016_2020/OPL_noirr_2016_2020/restarts/` on July 18 at 11:18, and consumed by Job `7318092`).
3. **2016 Consolidation Rerun:** The year 2016 was later rerun on July 31 within `matrix_2016_2020/OPL_noirr_2016_2020` to consolidate all five years of daily history outputs into a single experiment directory.

> [!NOTE]
> **Workflow Context:** The non-chronological execution dates (January 2017 executed on July 18; 2016 executed on July 31) reflect an **intentional consolidation workflow**. The historical sequence is confirmed, but bitwise equivalence between the two 2016 final restarts remains unverified.

### Staging Overwrite & Reproducibility Limitation
* **The Overwrite Mechanism:** When the consolidated December 2016 execution (Job `7391303`) concluded on July 31 at 23:59:58, its post-processing script copied its newly generated boundary restart (`output/2016-12/SURFACEMODEL/201701/LIS_RST_NOAHMP401_201701010000.d01.nc`) into `restarts/`, overwriting the pre-existing July 18 file in place.
* **Retrospective Hash Limitation:** Because the original restart consumed on July 18 was overwritten and LIS execution logs (`lislog_2017-01.0000`) record input file paths rather than cryptographic hashes, bitwise equivalence between the two 2016 final restarts cannot be verified retrospectively.
* **Template vs. Execution Reproducibility:** Programmatic verification confirms that `matrix_2016/OPL_noirr_2016` used the identical LIS configuration template (SHA-256 `2e13bc96...`), the same spin-up initial conditions (`422f8d3e...`), and the same meteorological forcing datasets (MERRA-2 + IMERG). However, identical configuration templates do not establish complete bitwise reproducibility in the absence of verified binary hashes or identical execution logs.

### Physical Boundary Transition Diagnostics
Inspection of domain-mean prognostic state variables across December 31, 2016, the boundary restart, and January 1, 2017 indicates plausible bulk consistency across the transition:

| Diagnostic Variable | Dec 31, 2016 Domain Mean (`LIS_HIST_201701010000`) | Instantaneous Boundary Restart (`LIS_RST_...201701010000`) | Jan 01, 2017 Domain Mean (`LIS_HIST_201701020000`) | Bulk Transition Assessment |
| :--- | :---: | :---: | :---: | :--- |
| **Soil Moisture (`SoilMoist`)** | `0.2378 m³/m³` | `0.2373 m³/m³` (`SMC`) | `0.2370 m³/m³` | Consistent winter desaturation |
| **Soil Moisture Range (Min / Max)** | `[0.0735, 0.4048]` | `[0.0734, 0.4041]` | `[0.0733, 0.4034]` | Preserved bulk range |
| **Soil Temperature (`SoilTemp`)** | `282.75 K` | Instantaneous state | `282.44 K` | Continuous winter cooling ($\Delta T = -0.31\,\text{K}$) |
| **Water Table Depth (`WaterTableD`)** | `3.0966 m` | Parameterized in `WA`/`WT` | `3.0963 m` | Gradual evolution ($\Delta = -0.0003\,\text{m}$) |
| **Total Water Storage (`TWS`)** | `5264.41 mm` | `WA` mean: `4780.71 mm` | `5263.72 mm` | Daily storage depletion ($\Delta = -0.69\,\text{mm}$) |
| **Surface Precipitation (`TotalPrecip`)** | `0.0000 kg/m²s`* | N/A (Flux) | `0.0000 kg/m²s`* | Diagnostic output (precision limit; see note) |
| **Evapotranspiration (`Evap`)** | `0.0000 kg/m²s`* | N/A (Flux) | `0.0000 kg/m²s`* | Diagnostic output (precision limit; see note) |

*\*Note on Flux Values and Spatial Continuity:*
1. **Flux Numerical Precision:** Diagnostic values reported as `0.0000 kg/m²s` reflect standard rounding in summary model output diagnostics and do not indicate zero physical flux. Higher numerical precision is required to determine actual flux magnitudes across individual grid cells.
2. **Spatial Scope:** Domain-mean diagnostics suggest plausible bulk consistency without catastrophic shocks or coldstart jumps; however, domain-averaged metrics do not prove cell-by-cell spatial continuity across the full domain grid.

---

## 8. Potential Future Reproducibility Test: Isolated January 2017 Replay

To empirically assess whether numerical divergence exists between the two states, an isolated replay of January 2017 could serve as a possible future reproducibility test (not an approved or scheduled simulation):

### Illustrative Replay Protocol (Testing Concept)
1. **Isolated Output Target:** Direct all outputs to an isolated test directory (e.g., `_validation/replay_201701/`) to prevent any risk of modifying or overwriting historical production data.
2. **Initial Condition:** Initialize exclusively from the current preserved December 2016 boundary restart:  
   [`restarts/LIS_RST_NOAHMP401_201701010000.d01.nc`](restarts/LIS_RST_NOAHMP401_201701010000.d01.nc) (SHA-256 `6603f937...`).
3. **Execution Fidelity:** Use the identical parameter configuration ([`generated/configs/lis_opl_noirr_2017-01.config`](generated/configs/lis_opl_noirr_2017-01.config)), forcing inputs (MERRA-2 + IMERG for Jan 2017), and the compiled `./src/lisf/lis/LIS` binary under `arch/arch_toubkal.env`.
4. **Diagnostic Metrics:**
   * Compute grid-cell-by-grid-cell differences between test history files and historical outputs in [`output/2017-01/SURFACEMODEL/201701/`](output/2017-01/SURFACEMODEL/201701/).
   * Compare the produced end-of-month restart against [`output/2017-01/SURFACEMODEL/201702/LIS_RST_NOAHMP401_201702010000.d01.nc`](output/2017-01/SURFACEMODEL/201702/LIS_RST_NOAHMP401_201702010000.d01.nc).
5. **Evidentiary Scope:** If executed in the future, an exact bitwise match between test outputs and historical outputs would demonstrate dynamic consistency with the July 31 restart. However, because the historical July 18 restart was overwritten without an archived checksum, a replay cannot resurrect the original file metadata.

---

## 9. Reproducibility Limitations & Core Definition Files

Full independent reproducibility remains subject to the following documented constraints:

1. **Git Tracking Status:**
   * Line 5 of [`.gitignore`](../../../../.gitignore#L5) specifies `experiments/`.
   * Consequently, all files within this experiment directory (including scripts, configurations, templates, logs, and restarts) are currently untracked in Git.
2. **Hard-Coded Absolute Paths:**
   [`scripts/chain_opl.py`](scripts/chain_opl.py) contains hardcoded paths on Lustre:
   * Line 58: `base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"`
   * Line 100: `spinup_restart = "/home/mohammad.elaabaribao/lustre/.../experiments/NorthMor/SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201601010000.d01.nc"`
   * Line 156: `cd {base_dir}/../../../../`
3. **Binary Executable Provenance:**
   The simulation executable `./src/lisf/lis/LIS` is an unversioned compiled binary located outside version control. While environment modules are preserved in [`arch/arch_toubkal.env`](../../../../arch/arch_toubkal.env) (GCC 13.3.0, OpenMPI 5.0.3, ESMF 8.7.0, NetCDF-Fortran 4.6.1), compiler optimization flags and make configurations are not archived locally.
4. **External Dataset Manifests:**
   Forcing datasets ([`./data/forcing/MERRA2`](../../../../data/forcing/MERRA2), [`./data/forcing/IMERG/raw/`](../../../../data/forcing/IMERG/raw/)) and spatial inputs ([`./data/lis_input/lis_input_NorthMor_5km.nc`](../../../../data/lis_input/lis_input_NorthMor_5km.nc)) reside on Lustre without cryptographic checksum manifests.
5. **Core Definition Files:**
   Four primary source and documentation files define the operational setup of the Open Loop experiment, though independent reproducibility remains constrained by the executable and forcing provenance limitations noted above:
   * [`config/experiment.ini`](config/experiment.ini): Prescribes the master simulation date bounds and template linkage.
   * [`templates/lis_opl.config.template`](templates/lis_opl.config.template): Parametric LIS/Noah-MP physical, numerical, and forcing specification.
   * [`scripts/chain_opl.py`](scripts/chain_opl.py): Encapsulates monthly chunking, template substitution, and execution orchestration.
   * [`README.md`](README.md): Scientific description, confirmed execution history, and documented technical limitations.

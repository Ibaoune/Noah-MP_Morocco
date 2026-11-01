# Deterministic Open-Loop Spin-up (SPINUP_OPL) Documentation

**Author:** Mohammad El Aabaribaoune

---

## 1. Scientific Purpose

`SPINUP_OPL` is the **11-year baseline deterministic open-loop spin-up** for the Northern Morocco (`NorthMor`) modeling domain.

Its scientific roles in the project are:
1. **Model Initialization:** Provide an extended continuous multi-year integration to allow land surface hydrological states (soil moisture across 4 layers, deep soil temperature, and unconfined aquifer groundwater) to evolve away from idealized uniform cold-start assumptions.
2. **Restart Provider for Downstream Chains:**
   * Supply the `2015-01-01 00:00:00` restart file used as the physical base for ensemble expansion in `ENS_OPL_2015`.
   * Supply the `2016-01-01 00:00:00` restart file used to initialize the deterministic Open-Loop simulation (`matrix_2016_2020/OPL_noirr_2016_2020`).
3. **Data Availability for Climatology Analyses:** Provide 11 years (2005–2015) of continuous daily outputs. While available on disk, their **scientific suitability as a climatological reference baseline has not yet been demonstrated**, as early spin-up years may contain initial adjustment transients.

---

## 2. Historical Simulation Period & Phasing

* **Simulated Period:** `2005-01-01 00:00:00` to `2016-01-01 00:00:00` (11 calendar years, 4,017 continuous simulation days).
* **Execution Phasing (Verified from SLURM and Orchestrator Logs):**
  * **Phase 1 (2005–2007) [Executed June 22–24, 2026]:**
    * Conducted via an external polling orchestrator script (`orchestrator_main.log`).
    * **2005 (Coldstart):** Executed as Job `7231029` on 2026-06-22 (walltime 2h 14m 40s across 32 MPI tasks).
    * **2006:** Initial attempt (`7236891`) cancelled; successfully re-run as Job `7236905` on 2026-06-24 (2h 14m).
    * **2007:** Executed as Job `7237101` on 2026-06-24 (2h 17m).
    * **2008 (Failed Attempt):** Job `7237275` aborted on 2026-06-24 at 04:14 due to relative path resolution and missing restart lookup.
  * **Phase 2 (2008–2015) [Executed June 25–26, 2026]:**
    * Following the 2008 failure, the orchestrator was redesigned into a self-submitting compute-node daisy chain (`scripts/chain_spinup.py`).
    * Configuration `config/experiment.ini` was updated to `StartDate = 2008-01-01` and `InitMode = restart` to resume directly from the validated 2007 restart.
    * Master batch job `job.sh` (Job `7247895`) was launched on June 25 at 20:55, triggering Job `7247896` (2008).
    * The chain sequentially completed 2008 through 2015 without intervention, terminating cleanly at Job `7251030` on 2026-06-26 at 16:53 (`Chain complete`SPINUP_OPL` is the **11-year baseline deterministic open-loop spin-up** for the Northern Morocco (`NorthMor`) modeling domain.).

---

## 3. Model Configuration & Physical Schemes

Verified against `templates/lis_spinup.config.template` and all compiled configurations in `generated/configs/`:

* **Domain & Resolution:** NorthMor lat/lon domain at 5 km resolution (`./data/lis_input/lis_input_NorthMor_5km.nc`, 16,030 active land tiles).
* **Atmospheric Forcing:** Blended `MERRA2` (lowest model level, bias-corrected total precipitation, lapse-rate topographic correction) + `GPM IMERG` V07B Final (overlay mode, linear temporal and bilinear spatial interpolation).
* **Timestep & Output Interval:** Noah-MP timestep = 15 minutes (`15mn`); history output interval = daily (`1da`).
* **Noah-MP Physical Schemes:**
  * Runoff and Groundwater: `1` (SIMGM - Simple Groundwater Model).
  * Dynamic Vegetation: `2` (Dynamic phenology / on-line leaf area index).
  * Stomatal Resistance: `1` (Ball-Berry formulation).
  * Canopy Radiation: `1` (Modified two-stream canopy radiation).
  * Surface Layer Drag: `1` (Monin-Obukhov similarity).
  * Snow Surface Albedo: `1` (BATS scheme).
  * Precipitation Partitioning: `1` (Jordan 1991).
  * Lower Soil Thermal Boundary: `2` (Thermal diffusion).
  * Supercooled Liquid Water: `1` (Enabled).
  * Frozen Soil Permeability: `1` (Enabled).
  * Soil Moisture Factor for Stomatal Resistance: `1` (Noah type).
  * Crop Model / Irrigation: `0` (**Irrigation completely OFF**; natural rainfed hydrology).
* **Ensemble & Perturbation Settings:**
  * `Number of ensembles per tile: 1` (Deterministic).
  * `Forcing / State / Observation perturbation algorithm: "none"`.

---

## 4. Initialization & Chaining Architecture

### Initialization Modes
1. **Year 2005 (Coldstart):**
   * `Start mode: coldstart`
   * `Noah-MP.4.0.1 restart file: none`
   * Default uniform initialization: Soil moisture = 0.20 m³/m³ (layers 1–4), soil temperatures = 288.0 K, canopy water = 0.0 mm, snow depth = 0.0 m, initial water table depth = 2.5 m, aquifer storage = 4900.0 mm.
2. **Years 2006–2015 (Restart):**
   * `Start mode: restart`
   * Restart file: `restarts/LIS_RST_NOAHMP401_<YYYY>01010000.d01.nc`.

### Daisy-Chaining Architecture
* Managed by `scripts/chain_spinup.py`.
* Each annual job compiles the LIS configuration for year `N`, executes LIS across 32 MPI tasks, locates the newly generated restart file at `output/<N>/SURFACEMODEL/<N+1>01/LIS_RST_NOAHMP401_<N+1>01010000.d01.nc`, copies it to `restarts/`, and submits year `N+1` via SLURM from the compute node.

---

## 5. Annual Restarts & Integrity Verification

All 11 boundary restart files exist intact in `restarts/` (17 MB total). Bit-for-bit identity between simulation outputs and staged restarts was verified using SHA-256 checksums:

| Simulated Year | Boundary Timestamp | Output File Location (`output/<Year>/...`) | Staged Restart (`restarts/`) | SHA-256 Checksum (Output & Staged) | Integrity Status |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **2005** | `2006-01-01 00:00` | `output/2005/.../LIS_RST_...200601010000.d01.nc` | `LIS_RST_NOAHMP401_200601010000.d01.nc` | `3f0940a1bf72db0d037b314583a18c3e0493f62607e1105038562b6c843c5f23` | **MATCH** |
| **2006** | `2007-01-01 00:00` | `output/2006/.../LIS_RST_...200701010000.d01.nc` | `LIS_RST_NOAHMP401_200701010000.d01.nc` | `a77ebc281a533543a5343d27851cde42d21beb7bee174a3d205d28174f938c20` | **MATCH** |
| **2007** | `2008-01-01 00:00` | `output/2007/.../LIS_RST_...200801010000.d01.nc` | `LIS_RST_NOAHMP401_200801010000.d01.nc` | `20b328e61130b3e2d08574a195ff3a88da7e505b16c5f05a5d5dd6e8bb6e9435` | **MATCH** |
| **2008** | `2009-01-01 00:00` | `output/2008/.../LIS_RST_...200901010000.d01.nc` | `LIS_RST_NOAHMP401_200901010000.d01.nc` | `56a4146c14f6e95d20dd06c03437574b69c68bac3bc8b767ba0cbaa8152d0d9b` | **MATCH** |
| **2009** | `2010-01-01 00:00` | `output/2009/.../LIS_RST_...201001010000.d01.nc` | `LIS_RST_NOAHMP401_201001010000.d01.nc` | `e85d76e085c420f3aadd01299111d23fc86a2840d1df8e635f5b6314fbd693b7` | **MATCH** |
| **2010** | `2011-01-01 00:00` | `output/2010/.../LIS_RST_...201101010000.d01.nc` | `LIS_RST_NOAHMP401_201101010000.d01.nc` | `5f26b8d9cad813ecc990c711efe937768caff60c7896242678ac3e11057396ac` | **MATCH** |
| **2011** | `2012-01-01 00:00` | `output/2011/.../LIS_RST_...201201010000.d01.nc` | `LIS_RST_NOAHMP401_201201010000.d01.nc` | `7b9767a90447507e5a9853d5fe4f957d2a2ceb76abda2426e4d7b4672e3168a6` | **MATCH** |
| **2012** | `2013-01-01 00:00` | `output/2012/.../LIS_RST_...201301010000.d01.nc` | `LIS_RST_NOAHMP401_201301010000.d01.nc` | `0ba3d54e6dc422afec2264b66a349c2b560c9b56ffaf610fd637bf4b04519cb7` | **MATCH** |
| **2013** | `2014-01-01 00:00` | `output/2013/.../LIS_RST_...201401010000.d01.nc` | `LIS_RST_NOAHMP401_201401010000.d01.nc` | `3dcbe36fe92e138316ac14ada6c59b3cc13a94706e7c9ebb805f58f438217c44` | **MATCH** |
| **2014** | `2015-01-01 00:00` | `output/2014/.../LIS_RST_...201501010000.d01.nc` | `LIS_RST_NOAHMP401_201501010000.d01.nc` | `dac6ad19f8981d47488abdefc4bb572859c7ec77f847d3eaf4de37a962d08bab` | **MATCH** |
| **2015** | `2016-01-01 00:00` | `output/2015/.../LIS_RST_...201601010000.d01.nc` | `LIS_RST_NOAHMP401_201601010000.d01.nc` | `422f8d3e79a9d2f9779c87bd5283de15d189b41990973e93bf8b43200c8f584e` | **MATCH** |

> **Note on Verification Methodology:** Checksum equality proves that the files currently residing in `restarts/` are identical to the simulation outputs. Historical consumption by subsequent jobs is independently verified through LIS execution logs, which report reading each specific restart path at run initialization.

### Downstream Dependencies & Trajectory Distinctions
1. **Ensemble Expansion (`2015-01-01`):**
   * Staged restart `restarts/LIS_RST_NOAHMP401_201501010000.d01.nc` is the documented source for ensemble expansion via `ENS_OPL_2015/scripts/expand_restart.py`.
2. **Deterministic Continuation vs Ensemble Branch:**
   * At `2015-01-01 00:00:00`, two distinct physical trajectories diverge:
     * **Deterministic Continuation (`SPINUP_OPL`):** Continued running 2015 deterministically (1 member, no perturbations) to reach `2016-01-01` for Open-Loop simulations.
     * **Ensemble Generation (`ENS_OPL_2015`):** Replicated the state into 20 members and applied stochastic GMAO perturbations to develop ensemble spread.
3. **Open-Loop 2016–2020 Initialization (`2016-01-01`):**
   * Staged restart `restarts/LIS_RST_NOAHMP401_201601010000.d01.nc` is explicitly referenced by `experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/scripts/chain_opl.py:100` and its initial configuration.
4. **Disambiguation from Data Assimilation:**
   * The 2016 deterministic restart was **NOT** used to initialize Data Assimilation (`DA_NoCDF`, `DA_CDF`, `DA_anomaly`). All DA experiments require surface and perturbation restart files originating exclusively from `experiments/NorthMor/SPINUP/SPINUP_DA/`.

---

## 6. Output Temporal Coverage & Climatological Availability

* **Output Directory:** `output/` (total footprint: 14 GB).
* **Daily History Coverage:**
  * File pattern: `LIS_HIST_YYYYMMDD0000.d01.nc`.
  * Total files: Exactly **4,017 continuous daily history files**.
  * Period covered: `2005-01-02 00:00:00` through `2016-01-01 00:00:00`.
  * Missing dates: **0**.
  * Duplicate timestamps: **0**.
  * Boundary consistency: Verified. Each year `N` contains its final day at `<N+1>01010000`, and year `N+1` begins output at `<N+1>01020000`.
* **Note on Total File Count:** The total NetCDF file count in early output folders (730 / 732 per year) reflects both daily history files and daily checkpoint restart files (`LIS_RST_NOAHMP401_*`) written during early execution phases.
* **Climatological Availability Caveat:**
  * While 2005–2015 daily outputs are physically intact and available on disk, **their scientific validity as a reference climatology for drought diagnostics has not yet been demonstrated**.
  * Early spin-up years (especially 2005–2007) are subject to initialization transients from the uniform cold start and should not be used as an equilibrium baseline without formal trend and sensitivity evaluations.

---

## 7. Known Inconsistencies & Reproducibility Limitations

1. **Config StartDate Mismatch:**
   * Preserved `config/experiment.ini` shows `StartDate = 2008-01-01` and `InitMode = restart`.
   * *Origin:* Preserves the Phase 2 resumption point after the June 25 refactoring, rather than the initial 2005 coldstart.
2. **Hardcoded Stale Paths (Path Rot):**
   * `scripts/chain_spinup.py` (line 59) and `job.sh` (line 22) contain the hardcoded path:
     `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup`
   * *Status:* That directory was moved on July 9, 2026 to `experiments/NorthMor/SPINUP/SPINUP_OPL/`. Attempting to run `job.sh` today will immediately abort with `No such file or directory`.
3. **Git Tracking Status:**
   * Due to `experiments/` being ignored in the root `.gitignore`, the source files (`config/experiment.ini`, `scripts/chain_spinup.py`, `templates/lis_spinup.config.template`, `job.sh`) are **untracked** in Git. Only this `README.md` is currently tracked.

---

## 8. Hydrological Convergence Status

**Status: HYDROLOGICAL CONVERGENCE: NOT VERIFIED**

To ensure scientific rigor, four distinct dimensions of the experiment are separated:
1. **Successful Numerical Execution: VERIFIED.** LIS completed all 11 years of integration on 32 MPI tasks without numerical instability, floating-point exceptions, or model crashes.
2. **Temporal Completeness: VERIFIED.** Exactly 4,017 continuous daily history outputs exist from `2005-01-02` to `2016-01-01` without temporal gaps or missing dates.
3. **Restart Integrity: VERIFIED.** All 11 annual boundary restarts exist, match simulation outputs bit-for-bit (SHA-256 verified), and were sequentially chained.
4. **Physical Spin-Up Convergence: NOT VERIFIED.** No empirical convergence diagnostics (such as layer-4 deep soil moisture trend analysis, unconfined aquifer storage stabilization, or inter-annual difference criteria < 1%) were computed or preserved. Neither an operational steady state nor the complete dissipation of cold-start effects can be asserted scientifically without empirical post-processing diagnostic verification.

---

## 9. Cleanup & Maintenance Candidates

> **IMPORTANT NOTICE:**  
> The items below are **PROPOSALS ONLY**.  
> **NOT APPROVED FOR DELETION.** No files may be moved, renamed, archived, or deleted without explicit review and approval.

1. **Misplaced Nested Directory (`experiments/` - 144 KB):**
   * Path: `experiments/NorthMor/SPINUP/SPINUP_OPL/experiments/NorthMor/spinup/logs/`
   * *Origin:* Created during the early 2008 test run when relative paths were invoked. Contains redundant `lislog_2008.0000`–`.0031` files from June 25, 20:32.
   * *Recommendation:* Candidate for future cleanup once path fixes are authorized.
2. **High-Volume MPI Diagnostic Logs (`logs/` - 3.9 GB):**
   * Contains hundreds of raw rank logs (`lislog_<YYYY>.<rank>`) for 32 MPI tasks across 11 years.
   * *Recommendation:* Propose compressing into an archival tarball (`logs_2005_2015.tar.xz`) to recover filesystem inodes while preserving full provenance.
3. **Generated Configs & Jobs (`generated/` - 188 KB):**
   * Keep intact as historical evidence of the exact command-line arguments and LIS parameters governing each year.

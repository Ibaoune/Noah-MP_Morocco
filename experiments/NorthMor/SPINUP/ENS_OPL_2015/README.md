# Ensemble Open-Loop Spin-up (ENS_OPL_2015) Documentation

**Author:** Mohammad El Aabaribaoune

---

## 1. Purpose and Experimental Design

`ENS_OPL_2015` fulfills the critical intermediate role (Stage 2) connecting the multi-year deterministic spin-up (`SPINUP_OPL`, Stage 1) to the Ensemble Kalman Filter data assimilation spin-up (`SPINUP_DA`, Stage 3).

```
[ Stage 1: SPINUP_OPL ]
  2005-01-01 to 2015-01-01 (Deterministic, 1 member, no perturbations)
         │
         ▼ Final physical restart: LIS_RST_NOAHMP401_201501010000.d01.nc (1.6 MB)
[ scripts/expand_restart.py ]
  Exact 20x tile-space replication (ntiles: 16,030 -> 320,600)
         │
         ▼ Expanded restart: restarts/LIS_RST_NOAHMP401_201501010000_ens20.d01.nc (93.8 MB)
[ Stage 2: ENS_OPL_2015 ]
  2015-01-01 00:00:00 (Zero initial physical spread; GMAO perturbation spin-up begins)
         │
         ▼ 3-month perturbation spin-up (January – March 2015)
  2015-03-31 23:45:00 Checkpoints:
  - Surface restart:      output/2015/SURFACEMODEL/201503/LIS_RST_NOAHMP401_201503312345.d01.nc
  - Perturbation restart: output/2015/DAPERT/201503/LIS_DAPERT_201503312345.d01.bin
         │
         ▼ Staged into SPINUP_DA as 2015-04-01 00:00:00 initial conditions
[ Stage 3: SPINUP_DA ]
  2015-04-01 to 2016-01-01 (SMAP Radiometer EnKF Assimilation)
```

### Scientific Objectives:
1. **Initialize 20 ensemble members** with the equilibrium hydrological states reached by `SPINUP_OPL` at the end of 2014.
2. **Spin up ensemble spread and error covariances** over a 3-month lead-in period (January 1 – March 31, 2015) under GMAO stochastic forcing and state perturbations prior to the start of SMAP satellite observations in April 2015.
3. **Generate coupled initial restarts** (physical land-surface state NetCDF and perturbation state binary) to initialize `SPINUP_DA` at 2015-04-01 00:00:00.

---

## 2. Initialization from SPINUP_OPL

* **Source File:** `experiments/NorthMor/SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201501010000.d01.nc` (1.6 MB; 1,602,434 bytes; 16,030 land tiles).
* **Physical State:** Represents the 10-year deterministic spin-up state at 2015-01-01 00:00:00 UTC.
* **Trajectory Divergence:** At 2015-01-01 00:00:00, the trajectory forks:
  - `SPINUP_OPL` continued deterministically through 2015 as a 1-member unperturbed simulation.
  - `ENS_OPL_2015` branched into a 20-member ensemble under GMAO stochastic forcing and state perturbations.

---

## 3. Expansion to 20 Members (`expand_restart.py`)

### The `nf90_get_var` Dimensionality Bottleneck
During initial deployment, LIS execution aborted immediately with:
```
[ERR] Error in nf90_get_var in LIS_readvar_restart Stopping
```
**Root Cause:** LIS configures the NetCDF restart dimension `ntiles` as the total active tile space across all ensemble members:
$$\text{ntiles} = N_{\text{cells}} \times N_{\text{ensembles}} = 16,030 \times 20 = 320,600$$
Because the deterministic restart from `SPINUP_OPL` contained only 16,030 tiles ($N_{\text{ensembles}} = 1$), the NetCDF library rejected the read request due to an array dimension mismatch.

### Solution and Implementation
The pre-processing script [`scripts/expand_restart.py`](scripts/expand_restart.py) reads the deterministic restart and replicates every variable along the `ntiles` dimension:
```python
expanded_data = np.repeat(data, num_ensembles, axis=axis)
```

### Tile-Space Layout & Geographic Preservation
In LIS Fortran core (`LIS_domainMod.F90`), domain patches are constructed by nested loops over rows, columns, and ensemble members:
```fortran
do r = 1, LIS_rc%lnr(n)
   do c = 1, LIS_rc%lnc(n)
      do m = 1, LIS_rc%nensem(n)
         if (LIS_LMLC(n)%dommask(c,r) > 0) then
            kk = kk + 1
            LIS_domain(n)%tile(kk)%ensem = m
```
Because the ensemble index `m` is innermost within each spatial cell `(c, r)`, tiles are ordered contiguous in ensemble space: `[cell_0_ens1..20, cell_1_ens1..20, ...]`. The use of `np.repeat(data, 20)` replicates each spatial grid cell 20 consecutive times, perfectly preserving the 1-to-1 geographic mapping of every ensemble member.

### Numerical Array Verification
Verification of the generated file [`restarts/LIS_RST_NOAHMP401_201501010000_ens20.d01.nc`](restarts/LIS_RST_NOAHMP401_201501010000_ens20.d01.nc) (93.8 MB; 93,781,388 bytes):
- All 50 prognostic and diagnostic variables exhibit **exact numerical array-value equality** (`np.array_equal == True`) across all 20 members compared to the deterministic source array values.
- *Distinction:* `np.array_equal` confirms exact array value replication across all variables, not byte-for-byte NetCDF container identity (NetCDF file headers, chunking tables, and dimension structures naturally differ between the 1-member 1.6 MB file and the 20-member 93.8 MB file).
- Initial ensemble standard deviation across all 20 members is physically zero. Calculated standard deviations show exact $0.000000\text{ m}^3/\text{m}^3$ for all soil moisture layers; minuscule non-zero values in soil temperature ($\sim 2.5 \times 10^{-5}\text{ K}$) and aquifer water ($\sim 3.9 \times 10^{-4}\text{ mm}$) represent numerical 32-bit single-precision floating-point rounding artifacts of NetCDF/NumPy computations rather than genuine initial ensemble variance.

---

## 4. Perturbation Architecture

Ensemble spread is generated using the GMAO stochastic perturbation scheme configured in [`templates/lis_ens_opl.config.template`](templates/lis_ens_opl.config.template) and [`config/experiment.ini`](config/experiment.ini).

### Perturbation Attributes

| Target | Attribute File | Method | Standard Deviation ($\sigma$) | Temporal Decorrelation ($	au$) | Cross-Correlation | Update Frequency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Downward Shortwave** | `forcing_pertattribs.txt` | Multiplicative | $0.30$ | $86,400\text{ s}$ (24 h) | $-0.80$ (with Rain) | $3,600\text{ s}$ (1 h) | **ACTIVE** |
| **Rainfall Rate** | `forcing_pertattribs.txt` | Multiplicative | $0.50$ | $86,400\text{ s}$ (24 h) | $-0.80$ (with SW) | $3,600\text{ s}$ (1 h) | **ACTIVE** |
| **Soil Moisture Layer 1** | `noahmp_sm_pertattribs.txt` | Additive | $0.004\text{ m}^3/\text{m}^3$ | $43,200\text{ s}$ (12 h) | None | $10,800\text{ s}$ (3 h) | **ACTIVE** |
| **Soil Moisture Layers 2–4** | `noahmp_sm_pertattribs.txt` | None | $0.000$ | — | — | — | **Dynamic only** |
| **SMAP Radiometer Obs** | `smap_pertattribs.txt` | Additive | $0.040\text{ m}^3/\text{m}^3$ | — | — | — | **DORMANT** ($N_{\text{DA}}=0$) |

### Atmospheric Forcing Verification
Verification of `generated/configs/lis_ens_opl_2015_2015.config` and `generated/configs/lis_ens_opl_2015_resume.config`:
- **Primary Source:** MERRA-2 reanalysis (`./data/forcing/MERRA2/`) with lowest model level forcing (`MERRA2 use lowest model level forcing: 1`) and lapse-rate topographic correction.
- **Precipitation Source:** GPM IMERG raw precipitation (`./data/forcing/IMERG/raw/`) blended via `overlay`.
- **Interpolation:** Bilinear spatial interpolation and linear temporal interpolation to the 15-minute Noah-MP timestep.

### Perturbation Coldstart Rationale
- Configured setting: `Perturbations restart filename: "none"` (`coldstart`).
- Scientific basis: The deterministic `SPINUP_OPL` simulation produced no `LIS_DAPERT` perturbation restart file. Therefore, the perturbation state vectors (first-order autoregressive noise memory) were initialized from coldstart at 2015-01-01 00:00:00.
- Checkpoint output frequency: `Perturbations restart output interval: "1mo"`. Checkpoint files are saved as monthly unformatted binary files (`LIS_DAPERT_*.bin`).

---

## 5. Historical Execution and Outputs

All runs executed on the UM6P Toubkal HPC cluster under SLURM partition `nodes` using 32 MPI tasks.

### Execution Chronology
1. **Initial Aborted Attempts (2026-06-26 to 2026-06-27):**
   - Jobs `7253409`, `7255666`, `7255704`, `7255705` failed within 6–8 seconds (`MPI_ABORT`).
   - Root causes: The `nf90_get_var` dimension bug, missing `shared/MODEL_OUTPUT_LIST.TBL`, and misconfigured `lis_input` domain paths.
2. **Successful Segment 1 (Job `7255708`):**
   - Ran from 2026-06-27 12:37:42 to 2026-06-28 00:37:35 (walltime: 12:00:06). Reached SLURM walltime limit.
   - Completed simulation months **2015-01 through 2015-08**.
   - Generated the crucial March 31 23:45 handoff checkpoint at 17:01 UTC on June 27.
3. **Successful Segment 2 (Job `7262240`):**
   - Resumed on 2026-06-28 14:23:00 using `generated/configs/lis_ens_opl_2015_resume.config`.
   - Initialized surface and perturbation states from the 2015-08-31 23:45 checkpoints.
   - Completed months **2015-09 through 2015-12**, reaching 2016-01-01 00:00:00 in ~6 hours.

### Generated Products Available on Disk
- **Ensemble History Files:** 365 daily NetCDF files (`output/2015/SURFACEMODEL/2015??/LIS_HIST_*.d01.nc`, 2.2 GB total).
- **Monthly Surface Restarts:** 12 monthly NetCDF files (`output/2015/SURFACEMODEL/2015??/LIS_RST_NOAHMP401_*.d01.nc`) plus annual boundary restart (`201601/LIS_RST_NOAHMP401_201601010000.d01.nc`).
- **Monthly Perturbation Restarts:** 12 monthly binary files (`output/2015/DAPERT/2015??/LIS_DAPERT_*.bin`) plus annual boundary restart (`201601/LIS_DAPERT_201601010000.d01.bin`).
- **Execution Logs:** SLURM standard output/error files and 32 MPI lislog files (`logs/`, 120 MB total).

---

## 6. Reassessment of the March 31 to April 1 Handoff

The checkpoint files transferred to `SPINUP_DA` have nominal timestamps of `201503312345` (in `ENS_OPL_2015`) and `201504010000` (in `SPINUP_DA`). A rigorous assessment distinguishes three levels of verification:

### A. Verified Binary File Equality (Bit-for-Bit Identity)
Byte-level verification (`cmp` / `filecmp.cmp`) proves that the files staged for `SPINUP_DA` are exact binary clones of the `ENS_OPL_2015` March 31 checkpoints:
```bash
# Surface model state (exact 100% byte-for-byte identity):
cmp experiments/NorthMor/SPINUP/ENS_OPL_2015/output/2015/SURFACEMODEL/201503/LIS_RST_NOAHMP401_201503312345.d01.nc \
    experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201504010000.d01.nc

# Perturbation state (exact 100% byte-for-byte identity):
cmp experiments/NorthMor/SPINUP/ENS_OPL_2015/output/2015/DAPERT/201503/LIS_DAPERT_201503312345.d01.bin \
    experiments/NorthMor/SPINUP/SPINUP_DA/restarts/pert/LIS_DAPERT_201504010000.d01.bin
```

### B. Evidence Supporting a Valid Operational Restart Transition
- In LIS retrospective runs with monthly alarm interval (`1mo`), LIS writes monthly checkpoint files at the end of each calendar month.
- Every monthly checkpoint throughout 2015 in `ENS_OPL_2015` follows this exact timestamping convention: `201501312345`, `201502282345`, `201503312345`, ..., `201511302345`, `201512312345`.
- In `ENS_OPL_2015` Job `7262240`, the simulation resumed at `2015-09-01 00:00:00` by directly pointing to `LIS_RST_NOAHMP401_201508312345.d01.nc` and `LIS_DAPERT_201508312345.d01.bin`. LIS parsed and integrated forward from this checkpoint without error.
- `SPINUP_DA` initialized at `2015-04-01 00:00:00` using the `201503312345` files (staged under `201504010000`), executing without numerical instability.

### C. Remaining Physical Timing Uncertainty (15-Minute Ambiguity)
- In `src/lisf/lis/runmodes/retrospective/retrospective_runMod.F90`, `LIS_ticktime` advances the ESMF clock at the beginning of each step (`00:00 -> 00:15`, ..., `23:30 -> 23:45`).
- The monthly alarm (`isMonthlyAlarmRinging` in `LIS_timeMgrMod.F90`) evaluates whether the clock time has reached the monthly interval threshold.
- The resulting restart file is stamped with the clock time active when `create_restart_filename` is called (`23:45`).
- *Uncertainty:* Without cycle-level internal state telemetry, it cannot be definitively proved whether the stored state represents the completion of the 23:30–23:45 step, or whether the final step (23:45–00:00) was integrated before the checkpoint dump. If the file represents the 23:45 state, a 15-minute gap or slight phase shift exists relative to the nominal `2015-04-01 00:00:00` start time of `SPINUP_DA`.
- *Status:*
  - **RESTART FILE INTEGRITY: VERIFIED** (exact byte equality).
  - **OPERATIONAL CHAIN TRANSITION: VERIFIED** (proven by execution of `SPINUP_DA` and `ENS_OPL_2015_resume`).
  - **SUB-HOURLY PHYSICAL CONTINUITY: QUALIFIED / UNRESOLVED** (15-minute timestamp offset reflects LIS alarm conventions, but exact physical boundary closure remains unverified at the sub-timestep level).

---

## 7. Verified Diagnostics

Lightweight read-only diagnostics evaluated over all 16,030 land grid cells and 20 ensemble members:

### Initial State vs 3-Month Checkpoint Spread

| Variable | Metric / Depth | Initial State (2015-01-01 00:00) | Checkpoint State (2015-03-31 23:45) | Units |
| :--- | :--- | :--- | :--- | :--- |
| **SMC Layer 1** | Domain-mean ensemble mean | $0.23533$ | $0.19902$ | $\text{m}^3/\text{m}^3$ |
| | Domain-mean ensemble spread ($\sigma_{\text{ens}}$) | **$0.000000$** | **$0.055952$** | $\text{m}^3/\text{m}^3$ |
| | Min / Max spread across domain | $[0.000000, 0.000000]$ | $[0.002693, 0.116740]$ | $\text{m}^3/\text{m}^3$ |
| | Spread percentiles [p5, p25, p50, p75, p95] | $[0, 0, 0, 0, 0]$ | $[0.0311, 0.0485, 0.0573, 0.0649, 0.0754]$ | $\text{m}^3/\text{m}^3$ |
| **SMC Layer 2** | Domain-mean ensemble spread ($\sigma_{\text{ens}}$) | **$0.000000$** | **$0.020481$** | $\text{m}^3/\text{m}^3$ |
| | Spread percentiles [p5, p25, p50, p75, p95] | $[0, 0, 0, 0, 0]$ | $[0.0077, 0.0157, 0.0206, 0.0252, 0.0327]$ | $\text{m}^3/\text{m}^3$ |
| **SMC Layer 3** | Domain-mean ensemble spread ($\sigma_{\text{ens}}$) | **$0.000000$** | **$0.014811$** | $\text{m}^3/\text{m}^3$ |
| | Spread percentiles [p5, p25, p50, p75, p95] | $[0, 0, 0, 0, 0]$ | $[0.0043, 0.0095, 0.0140, 0.0196, 0.0275]$ | $\text{m}^3/\text{m}^3$ |
| **SMC Layer 4** | Domain-mean ensemble spread ($\sigma_{\text{ens}}$) | **$0.000000$** | **$0.008555$** | $\text{m}^3/\text{m}^3$ |
| | Spread percentiles [p5, p25, p50, p75, p95] | $[0, 0, 0, 0, 0]$ | $[0.0016, 0.0046, 0.0079, 0.0117, 0.0180]$ | $\text{m}^3/\text{m}^3$ |
| **TSLB Layer 1** | Soil temperature spread ($\sigma_{\text{ens}}$) | $0.000025$* | **$1.009478$** (max $2.578$) | $\text{K}$ |
| **ZWT** | Water table depth spread ($\sigma_{\text{ens}}$) | $0.000000$ | **$0.028296$** (max $0.243$) | $\text{m}$ |
| **WA** | Aquifer storage spread ($\sigma_{\text{ens}}$) | $0.000387$* | **$5.659192$** (max $48.65$) | $\text{mm}$ |

*\*Note: Initial non-zero standard deviations in TSLB and WA reflect numerical single-precision floating-point rounding artifacts, not physical ensemble spread.*

### Physical Interpretation & Scientific Qualification
1. **Coupled Physical Propagation:** Direct additive state perturbations were configured only for Layer 1 ($\sigma = 0.004\text{ m}^3/\text{m}^3$). Spread in deeper soil layers (Layers 2–4, where direct perturbations are $0.0$) arises through coupled soil-vegetation-atmosphere physics:
   - Infiltration fronts driven by perturbed precipitation and shortwave radiation.
   - Soil moisture diffusion and unsaturated hydraulic fluxes (Richards equation; vertical drainage and capillary rise).
   - Vegetation root water uptake and evapotranspiration drawdown across layers 1–4.
   This coupled interaction results in smooth attenuation of ensemble spread with depth ($0.056 \rightarrow 0.020 \rightarrow 0.015 \rightarrow 0.0086\text{ m}^3/\text{m}^3$).
2. **Scientific Status on Spread Adequacy:**
   - **ENSEMBLE DIVERGENCE: VERIFIED.** (Initial identical states successfully diverged under stochastic forcing/physics).
   - **COVARIANCE ADEQUACY FOR EnKF: NOT VERIFIED.** The existence of non-zero spread confirms active perturbation dynamics, but does not prove statistical optimality or consistency with true model and forcing error covariances. Calibration must be evaluated against observation-minus-forecast residuals in downstream data assimilation diagnostics.

---

## 8. Uncertainties and Reproducibility Limitations

1. **Path Configurations & Obsolete References:**
   - **Genuinely Obsolete:** In `scripts/chain_ens_opl.py` (line 27), `base_dir` hardcodes the pre-migration directory path:
     `base_dir = "/home/.../experiments/NorthMor/1Yr_2016/ens_opl_2015"`
     This directory no longer exists on disk, so running `python3 scripts/chain_ens_opl.py` directly from the current directory will fail unless `base_dir` is updated.
   - **Genuinely Obsolete:** `generated/configs/lis_ens_opl_2015_2015.config` and `generated/configs/lis_ens_opl_2015_resume.config` contain historical absolute paths to `1Yr_2016/ens_opl_2015` and `step2_ens_opl_2015`.
   - **Valid Relative Path:** In `job.sh` (line 19), `source ../../../../arch/arch_toubkal.env` is **VALID** relative to `$SLURM_SUBMIT_DIR` because `experiments/NorthMor/SPINUP/ENS_OPL_2015/` is exactly 4 directory levels below the repository root (`NoahMP_Morocco/`), where `arch/arch_toubkal.env` actually resides.
2. **Dual Scientific Role vs Redundant Simulation:**
   - `ENS_OPL_2015` was executed for the full calendar year 2015 (365 days).
   - However, only months **2015-01 through 2015-03** served as the spin-up handoff into `SPINUP_DA`.
   - Months **2015-04 through 2015-12** represent open-loop ensemble trajectory output that duplicates the time period assimilated in `SPINUP_DA`.
3. **Stochastic Repeatability:**
   - Because perturbation sequences rely on pseudo-random seeds initialized at coldstart, exact bitwise regeneration of daily histories requires identical MPI rank topology and compiler runtime libraries.

---

## 9. Potential Cleanup Candidates (NOT APPROVED FOR DELETION)

| File / Directory | Size | Proposed Classification | Scientific Rationale |
| :--- | :--- | :--- | :--- |
| `restarts/LIS_RST_NOAHMP401_201501010000_ens20.d01.nc` | 93.8 MB | **KEEP AS PROVENANCE** | Primary expanded initial condition (320,600 tiles) connecting Stage 1 to Stage 2. (Source deterministic restart: 1.6 MB). |
| `output/2015/SURFACEMODEL/201501..201503/` | ~560 MB | **KEEP** | Daily histories and monthly restarts documenting the 3-month perturbation spin-up. |
| `output/2015/DAPERT/201501..201503/` | ~30 MB | **KEEP** | Monthly perturbation restarts, specifically the critical March 31 23:45 handoff binary. |
| `output/2015/SURFACEMODEL/201504..201512/` | ~1.6 GB | **ARCHIVE CANDIDATE** | Daily histories post-dating the handoff to `SPINUP_DA`. Useful only as open-loop baseline for 2015. |
| `output/2015/DAPERT/201504..201512/` | ~90 MB | **ARCHIVE CANDIDATE** | Perturbation binary restarts post-dating the handoff. |
| `logs/` (all 32 MPI lislogs and SLURM logs) | 120 MB | **KEEP AS PROVENANCE** | Indispensable execution telemetry and provenance trail of jobs `7255708` and `7262240`. |
| `Readme` (original French documentation) | 3.5 KB | **KEEP AS PROVENANCE** | Primary historical source document written during original execution. |

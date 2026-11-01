# SPINUP_DA: Data Assimilation Spin-up & 2016 Initialization Audit

**Scope:** Stage 3 of the Northern Morocco Land Information System (LIS) Spin-up Hierarchy  
**Experiment Directory:** `experiments/NorthMor/SPINUP/SPINUP_DA/`  
**Model & Domain:** Noah-MP 4.0.1 on Northern Morocco 5-km Grid (16,030 active land tiles; 320,600 ensemble tiles)  
**Atmospheric Forcing:** MERRA-2 meteorological forcing overlaid with GPM IMERG precipitation  
**Ensemble Configuration:** 20 members (`Number of ensembles per tile: 20`)  
**Data Assimilation Algorithm:** Ensemble Kalman Filter (`EnKF`), 1 instance  
**Assimilation Target:** NASA SMAP Level-3 Enhanced Radiometer Soil Moisture (`SPL3SMP_E`, Release R19)  
**Scaling Strategy:** **NoCDF** (`Data assimilation scaling strategy: "none"`)  
**Execution Interval:** 2015-04-01 00:00:00 to 2016-01-01 00:00:00 (9 monthly simulation chunks)  
**Historical Status:** Completed (Jobs `7260791` through `7262178`, 13h 45m walltime)  
**Audit Status:** Fully verified (reconstructed execution chronology, restart integrity, source code verification of EnKF diagnostics, and corrected scientific interpretations)

---

## 1. Purpose and Experimental Design

`SPINUP_DA` serves as **Stage 3** in the Northern Morocco initialization hierarchy, bridging the 3-month unassimilated ensemble perturbation spin-up (`ENS_OPL_2015`, Stage 2) to the multi-year production data assimilation runs (`matrix_2016_2020`).

```
[ Stage 1: SPINUP_OPL ]  2005-01-01 to 2015-01-01 (1 member, deterministic, unperturbed)
         │
         ▼ Deterministic restart: LIS_RST_NOAHMP401_201501010000.d01.nc (1.6 MB)
[ scripts/expand_restart.py ] Exact 20x tile replication (ntiles: 16,030 -> 320,600)
         │
         ▼ Expanded restart: restarts/LIS_RST_NOAHMP401_201501010000_ens20.d01.nc (93.8 MB)
[ Stage 2: ENS_OPL_2015 ] 2015-01-01 to 2015-04-01 (20 members, GMAO perturbations, NO DA)
         │
         ▼ 2015-03-31 23:45 Checkpoints (staged as 2015-04-01 00:00:00)
[ Stage 3: SPINUP_DA ]   2015-04-01 to 2016-01-01 (20 members, SMAP EnKF Assimilation, NoCDF)
         │
         ▼ 2016-01-01 00:00:00 Checkpoints (surf: 21 MB, pert: 137 MB)
[ Downstream: matrix_2016_2020 ]
  ├── DA_nocdf_noirr_2016_2020    (Initialized directly from SPINUP_DA)
  ├── DA_cdf_noirr_2016_2020      (Initialized directly from SPINUP_DA)
  └── DA_anomaly_noirr_2016_2020  (Initialized directly from SPINUP_DA)
```

### Scientific Objectives:
1. **Initialize EnKF Data Assimilation:** Begin assimilating satellite soil moisture when NASA SMAP observations became operational in April 2015.
2. **Spin up Ensemble Covariances:** Execute 9 months of active observation-update cycles so that background error covariances and spatial/vertical cross-correlations develop under coupled forcing perturbations and Kalman updating before launching 2016–2020 experiments. *(Note: Statistical filter optimality is not formally calibrated; see Section 7).*
3. **Generate Downstream Initial Conditions:** Deliver coupled land-surface physical restart states (`LIS_RST_NOAHMP401_201601010000.d01.nc`) and perturbation binary states (`LIS_DAPERT_201601010000.d01.bin`) to initialize downstream 2016 DA matrix simulations.

---

## 2. Initialization from ENS_OPL_2015

### Staged Restart Verification:
- **Surface Restart:** `experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201504010000.d01.nc`
  - Source: `ENS_OPL_2015/output/2015/SURFACEMODEL/201503/LIS_RST_NOAHMP401_201503312345.d01.nc` (21 MB).
  - Verification: **100% exact bitwise identity** (`cmp` exit code 0).
  - Loading: Successfully read by LIS at initialization via `Start mode: restart` (confirmed by `lislog_2015-04.0000`, line 211).
- **Perturbation File:** `experiments/NorthMor/SPINUP/SPINUP_DA/restarts/pert/LIS_DAPERT_201504010000.d01.bin`
  - Source: `ENS_OPL_2015/output/2015/DAPERT/201503/LIS_DAPERT_201503312345.d01.bin` (93 MB).
  - Verification: **100% exact bitwise identity** (`cmp` exit code 0).
  - Loading: **BYPASSED / NOT READ**. April 2015 was executed with `Perturbations start mode: "coldstart"`.

### Physical-State vs Perturbation-Memory Continuity:
A critical distinction must be made between physical land-surface state continuity and perturbation auto-regressive memory continuity:
1. **Physical-State Continuity: FULLY PRESERVED.**
   - All 20 ensemble members retained the prognostic land-surface physical states (soil moisture in 4 layers, soil temperature, canopy water, snowpack, aquifer storage) developed during the 3-month unassimilated spin-up (`ENS_OPL_2015`).
   - The ensemble entered April 2015 with realistic spread ($\sigma pprox 0.051\text{ m}^3/\text{m}^3$ in Layer 1).
2. **Perturbation-Memory Continuity: VERIFIED BYPASS vs UNVERIFIED COLDSTART INTERNALS.**
   - **Verified Perturbation-Restart Bypass:** LIS source code (`LIS_perturbMod.F90:120`, `rstFlag = .false.`) and execution logs prove conclusively that `readpertrestart` was never invoked during April 2015. The staged perturbation file `LIS_DAPERT_201504010000.d01.bin` (93 MB) was **completely bypassed and unread**.
   - **Reset AR(1) Temporal Memory:** Setting `Perturbations start mode: "coldstart"` ensured that serial auto-regressive AR(1) noise correlations from the unassimilated March run were severed across atmospheric forcing (radiation, precipitation), prognostic state (SMC Layer 1), and observation perturbations (SMAP).
   - **Unverified Stochastic Coldstart Details:** While the restart bypass and AR(1) memory severing are verified, the precise internal initialization mechanics (e.g., initial pseudo-random number generator seeds, internal noise array zeroing vs initial drawing, or memory buffering across MPI ranks) remain unverified internal model behaviors without instrumented runtime tracing.

### Reassessment of the 15-Minute Nominal Difference:
1. **File Equality (VERIFIED):** The checkpoint files staged into `SPINUP_DA` are exact binary clones of the `ENS_OPL_2015` March 31 23:45 outputs.
2. **Operational Restart Transition (VERIFIED):** LIS consistently names monthly checkpoint files using the last completed 15-minute step of the calendar month (`23:45`). Staging this file under `00:00` for the subsequent month is standard in LIS chaining and executes cleanly without runtime errors.
3. **Sub-hourly Physical Timing Continuity (QUALIFIED / UNRESOLVED):** While operational continuity is demonstrated, whether the restart file contains the state integrated up to 23:45 or through 00:00 cannot be proven without cycle-level diagnostic telemetry. The nominal 15-minute label offset represents a standard LIS naming convention rather than an established physical discontinuity.

---

## 3. SMAP Observation and EnKF Configuration

Verified settings from `generated/configs/lis_assim_2015-04.config` through `lis_assim_2015-12.config`:

```ini
# Data Assimilation Core
Number of data assimilation instances:                1
Data assimilation algorithm:                          "EnKF"
Data assimilation set:                                "SMAP(NASA) soil moisture"
Data assimilation number of observation types:        1
Data assimilation exclude analysis increments:        0
Data assimilation output interval for diagnostics:    "1da"
Data assimilation output ensemble spread:             1
Data assimilation output innovations:                 1
Data assimilation output processed observations:      1

# Scaling & Bias Strategy: NoCDF
Data assimilation scaling strategy:                   "none"
Bias estimation algorithm:                            "none"
Apply perturbation bias correction:                   0

# SMAP Dataset Specifications
SMAP(NASA) soil moisture data designation:            SPL3SMP_E
SMAP(NASA) soil moisture data directory:              ./data/observations/SMAP_SPL3SMP_E
SMAP(NASA) soil moisture apply SMAP QC flags:         1
SMAP(NASA) soil moisture Composite Release ID:        "R19"
```

### Critical Configuration Findings:
- **NoCDF Assimilation:** Although CDF paths (`./data/cdf/smap_model_cdf.nc` and `./data/cdf/smap_obs_cdf.nc`) were defined in the config template, `Data assimilation scaling strategy: "none"` was active. SMAP volumetric soil moisture was assimilated directly without CDF matching.
- **State Updating:** `Data assimilation exclude analysis increments: 0` ensured that calculated Kalman analysis increments were directly applied to prognostic soil moisture states (Layer 1 directly, Layers 2–4 via covariance propagation and drainage).

---

## 4. Perturbation and Ensemble Settings

```ini
# Ensemble Configuration
Number of ensembles per tile:                         20

# Stochastic Perturbations (GMAO Scheme)
Forcing perturbation algorithm:                       "GMAO scheme"
Forcing perturbation frequency:                       "1hr"
Forcing perturbation attributes file:                 ./data/pert_package/forcing_pertattribs.txt

State perturbation algorithm:                         "GMAO scheme"
State perturbation frequency:                         "3hr"
State perturbation attributes file:                   ./data/pert_package/noahmp_sm_pertattribs.txt

Observation perturbation algorithm:                   "GMAO scheme"
Observation perturbation frequency:                   "6hr"
Observation attributes file:                          ./data/pert_package/smap_attribs.txt
Observation perturbation attributes file:             ./data/pert_package/smap_pertattribs.txt
```

### The Perturbation Coldstart Discovery for April 2015:
- In `scripts/chain_da.py`, the initialization logic specifies:
  ```python
  if current_date == global_start_date:
      pert_start_mode = "coldstart"
  else:
      pert_start_mode = "restart"
  ```
- **Root Cause:** In Job `7260790`, `SPINUP_DA` initially attempted to run April 2015 with `Perturbations start mode: "restart"`, loading the staged file `LIS_DAPERT_201504010000.d01.bin` (93 MB from `ENS_OPL_2015`).
- The job crashed after 7.8 seconds with:
  ```
  At line 2490 of file ../dataassim/perturb/gmaopert/gmaopert_Mod.F90
  Fortran runtime error: End of file
  ```
  Because `ENS_OPL_2015` had `Number of data assimilation instances: 0`, its perturbation restart file lacked observation perturbation records. When `gmaopert_Mod.F90` attempted to read observation perturbation arrays (`read(ftn) gtmp`), it hit EOF immediately.
- **Resolution:** Setting `pert_start_mode = "coldstart"` for April 2015 allowed LIS to initialize observation perturbations from scratch while retaining the 20-member physical land-surface state from `ENS_OPL_2015`.
- **Subsequent Months:** From May through December 2015, `pert_start_mode = "restart"` was active. The perturbation restart size expanded from 93 MB to **137 MB** to accommodate observation perturbation states, propagating continuously.

---

## 5. Historical Execution Chronology

All jobs executed on the UM6P Toubkal HPC cluster under SLURM partition `nodes` (32 MPI tasks).

| Job ID | Period | Start Time (UTC) | End Time (UTC) | Walltime | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `7260789` | 2015-04 | 2026-06-27 23:25 | 2026-06-27 23:25 | 0m 01s | **FAILED** | Path error: `arch/arch_toubkal.env` not found. |
| `7260790` | 2015-04 | 2026-06-27 23:36 | 2026-06-27 23:36 | 0m 08s | **FAILED** | Fortran EOF at line 2490 in `gmaopert_Mod.F90`. |
| `7260791` | 2015-04 | 2026-06-28 01:10 | 2026-06-28 02:45 | 95m 25s | **SUCCESS** | April completed with `pert_start_mode = "coldstart"`. |
| `7261425` | 2015-05 | 2026-06-28 02:46 | 2026-06-28 04:21 | 95m 14s | **SUCCESS** | Resumed with `pert_start_mode = "restart"`. |
| `7261855` | 2015-06 | 2026-06-28 04:21 | 2026-06-28 05:51 | 90m 30s | **SUCCESS** | Chained automatically. |
| `7262045` | 2015-07 | 2026-06-28 05:51 | 2026-06-28 07:25 | 93m 59s | **SUCCESS** | Chained automatically. |
| `7262088` | 2015-08 | 2026-06-28 07:25 | 2026-06-28 08:58 | 92m 47s | **SUCCESS** | Chained automatically. |
| `7262104` | 2015-09 | 2026-06-28 08:58 | 2026-06-28 10:28 | 89m 32s | **SUCCESS** | Chained automatically. |
| `7262124` | 2015-10 | 2026-06-28 10:28 | 2026-06-28 12:00 | 92m 26s | **SUCCESS** | Chained automatically. |
| `7262144` | 2015-11 | 2026-06-28 12:00 | 2026-06-28 13:31 | 91m 02s | **SUCCESS** | Chained automatically. |
| `7262178` | 2015-12 | 2026-06-28 13:31 | 2026-06-28 15:05 | 94m 12s | **SUCCESS** | Reached 2016-01-01 00:00:00 UTC. Chain completed! |

**Total Production Walltime:** 13 hours 45 minutes of continuous automated SLURM chaining.

---

## 6. Monthly Chaining and Restart Integrity

Every month generated an end-of-simulation restart stamped `${next_date}0000` which was copied to `restarts/surf/` and `restarts/pert/` by `chain_da.py`.

### SHA-256 Checksum Audit:

| Monthly Segment | Target Restart Stamp | Surface NetCDF SHA-256 (Prefix) | Staged Match | Perturbation Binary SHA-256 (Prefix) | Staged Match |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2015-04** | `201505010000` | `e3a50290722e...` | **EXACT MATCH** | `8c87fb0c42fc...` | **EXACT MATCH** |
| **2015-05** | `201506010000` | `8bbb0e7a3973...` | **EXACT MATCH** | `012d3cccfc90...` | **EXACT MATCH** |
| **2015-06** | `201507010000` | `53d7ed46678c...` | **EXACT MATCH** | `b29e652d8551...` | **EXACT MATCH** |
| **2015-07** | `201508010000` | `18c8a98db973...` | **EXACT MATCH** | `28977ad6db11...` | **EXACT MATCH** |
| **2015-08** | `201509010000` | `648d6bf92caa...` | **EXACT MATCH** | `c5df4c994beb...` | **EXACT MATCH** |
| **2015-09** | `201510010000` | `e18ec06fbdff...` | **EXACT MATCH** | `156e389b32f1...` | **EXACT MATCH** |
| **2015-10** | `201511010000` | `15f0f223ee9e...` | **EXACT MATCH** | `0331ad682854...` | **EXACT MATCH** |
| **2015-11** | `201512010000` | `7315f40868f1...` | **EXACT MATCH** | `467de350cedf...` | **EXACT MATCH** |
| **2015-12** | `201601010000` | `46de5914372a...` | **EXACT MATCH** | `39db9fe4ce24...` | **EXACT MATCH** |

**Restart Integrity Status: VERIFIED.** Zero corrupted, missing, or mismatched restart files across all nine monthly transitions.

---

## 7. Verified Assimilation Diagnostics & Statistical Evaluation

### NetCDF Variable Definitions and Source Code Verification:
Source code analysis in `src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90`, `LIS_DAobservationsMod.F90`, and `LIS_historyMod.F90` established the exact definitions of all EnKF diagnostic variables:
- **`ninnov_01` (`Normalized_innovations_for_DA_instance_01`):**
  - **Definition:** Float variable computing $(y - H \bar{x}^f) / \sqrt{H P^f H^T + R}$.
  - **Correction:** It is **NOT** an integer observation count. Unobserved and QC-rejected pixels are assigned `-9999.0`. A valid assimilated observation is identified by `innov_01 > -9000.0`.
- **`innov_01` (`Innovations_for_DA_instance_01`):**
  - **Definition:** Raw innovation $d = y - H \bar{x}^f$ in volumetric units [$\text{m}^3/\text{m}^3$]. Populated only for assimilated observations (`Observations(i)%assim == .true.`). Unobserved/rejected pixels are `-9999.0`.
- **`anlys_incr_Soil Moisture Layer 1_01`:**
  - **Definition:** Kalman analysis increment $x^a - x^f$ applied to prognostic soil moisture Layer 1. On land cells without observation updates, increment is `0.0`; ocean cells are `-9999.0`.
- **`ensspread_Soil Moisture Layer 1_01` & `Layer 2_01`:**
  - **Definition:** In `src/lisf/lis/core/LIS_historyMod.F90:7973-7985`, the standard deviation calculation is commented out (`#if 0`), and the executed routine computes:
    $$gtmp(c, r) = \max_{t}(gtmp1) - \min_{t}(gtmp1)$$
  - **Correction:** The NetCDF `ensspread_*` variable stores the **Ensemble Range** (peak-to-peak difference $\max - \min$), **NOT** the ensemble standard deviation!
  - For $N = 20$ normally distributed members, the expected sample range is related to standard deviation by Tippett's factor $d_2 \approx 3.735$ (i.e. $\text{Range} \approx 3.735 \times \sigma$).
  - The true standard deviation across the 20 members is $\sigma_1 \approx 0.040 - 0.051\text{ m}^3/\text{m}^3$ (Layer 1) and $\sigma_2 \approx 0.010 - 0.025\text{ m}^3/\text{m}^3$ (Layer 2).

### Monthly Verified Diagnostic Statistics:
Computed from all 668 innovation NetCDF files, 668 increment NetCDF files, and 275 daily spread files across valid assimilated observation samples (`innov_01 > -9000.0`):

| Month | EnKF Cycles | Valid Grid-Time Innovation Records | Mean Innov ($y - Hx$) [$\text{m}^3/\text{m}^3$] | RMS Innov | Mean `ninnov` | Std `ninnov` | Mean Incr L1 ($x_a - x_f$) [$\text{m}^3/\text{m}^3$] | RMS Incr L1 | Mean Range L1 ($\max - \min$) | Mean Range L2 ($\max - \min$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2015-04** | 79 | 121,617 | $-0.02063$ | $0.04383$ | $-0.3108$ | $0.6099$ | $-0.01296$ | $0.02740$ | $0.1894$ | $0.0589$ |
| **2015-05** | 72 | 98,007 | $+0.00053$ | $0.03719$ | $+0.0288$ | $0.6529$ | $-0.00085$ | $0.01973$ | $0.1632$ | $0.0404$ |
| **2015-06** | 64 | 97,012 | $-0.00570$ | $0.03370$ | $-0.0795$ | $0.5570$ | $-0.00401$ | $0.01937$ | $0.1663$ | $0.0505$ |
| **2015-07** | 80 | 119,649 | $+0.00770$ | $0.02323$ | $+0.1457$ | $0.3764$ | $+0.00319$ | $0.01265$ | $0.1500$ | $0.0359$ |
| **2015-08** | 82 | 136,545 | $+0.00365$ | $0.03286$ | $+0.0742$ | $0.5377$ | $+0.00122$ | $0.01909$ | $0.1646$ | $0.0426$ |
| **2015-09** | 79 | 130,507 | $-0.01012$ | $0.03722$ | $-0.1717$ | $0.6226$ | $-0.00532$ | $0.02013$ | $0.1740$ | $0.0563$ |
| **2015-10** | 64 | 130,855 | $-0.01764$ | $0.04764$ | $-0.2822$ | $0.7349$ | $-0.01028$ | $0.02766$ | $0.1787$ | $0.0909$ |
| **2015-11** | 79 | 147,098 | $-0.00773$ | $0.03266$ | $-0.1190$ | $0.5026$ | $-0.00473$ | $0.01996$ | $0.1827$ | $0.0877$ |
| **2015-12** | 69 | 99,191 | $-0.00863$ | $0.02502$ | $-0.1264$ | $0.3700$ | $-0.00559$ | $0.01559$ | $0.1882$ | $0.0720$ |
| **TOTAL** | **668** | **1,080,481** | — | — | — | — | — | — | — | — |

*(Note on true standard deviation: In the end-of-year restart `restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc`, sample standard deviation across the 20 ensemble members is $\bar{\sigma}_1 = 0.05084\text{ m}^3/\text{m}^3$ and $\bar{\sigma}_2 = 0.01535\text{ m}^3/\text{m}^3$, with corresponding mean ranges of $0.18542$ and $0.06537\text{ m}^3/\text{m}^3$. Ratio Range/Std $\approx 3.65–4.26$, confirming theoretical Gaussian sample statistics).*

### Correction of Scientific Interpretations:

1. **Innovation Signs and Inferred Land Moisture State:**
   - *Previous Unsupported Claim:* "Unscaled SMAP retrievals were systematically wetter than the Noah-MP background model forecast across all months (mean innovations $+0.013$ to $+0.035$)."
   - *Correction:* This was an artifact of an earlier post-processing script that erroneously filtered `ninnov > 0`, discarding all negative innovations. When all valid observations are evaluated, **mean innovations are negative in 7 out of 9 months** ($-0.0206$ in April, $-0.0176$ in October). SMAP retrievals were frequently drier than the unscaled Noah-MP model background during spring, autumn, and winter.
   - *Scientific Qualification:* Positive or negative innovations cannot be used to declare an absolute physical "wet" or "dry" ground truth without independent in-situ validation. Satellite microwave retrievals reflect sensor calibration, vegetation attenuation corrections, and roughness assumptions; differences from Noah-MP indicate systematic discrepancies between unscaled satellite retrievals and the land-surface model climatology.

2. **Physical Consistency of Innovations and Increments:**
   - On identical observation pixels, Kalman analysis increments correlate strongly with innovations ($r = +0.9687$). Negative innovations consistently generated negative Layer 1 increments (e.g. April mean increment $-0.0130\text{ m}^3/\text{m}^3$), pulling the model state toward drier satellite retrievals.

3. **Statistical Filter Optimality and Spread Retention:**
   - *Previous Unsupported Claim:* "Filter reached mature, statistically optimal background error covariance with zero filter collapse."
   - *Correction & Remaining Uncertainties:*
     - The ensemble maintained non-zero spread throughout all 9 months (mean Layer 1 range bounded between $0.150$ and $0.189\text{ m}^3/\text{m}^3$, corresponding to $\sigma_1 \approx 0.040–0.051\text{ m}^3/\text{m}^3$). Catastrophic ensemble collapse did not occur.
     - However, **statistical optimality is NOT demonstrated.** In a statistically calibrated Kalman filter, the normalized innovation variance should equal 1.0 ($	ext{std}(ninnov) = 1.0$). Across all 9 months, the sample standard deviation of `ninnov` is substantially below 1.0 (mean $\approx 0.55$, monthly range $0.37–0.73$).
     - The sample standard deviation of normalized innovations (`std(ninnov) ~ 0.55`) suggests a **possible consistency/calibration issue** in the filter configuration.
     - However, this diagnostic alone is **insufficient by itself to establish filter non-optimality or specifically over-estimated error covariance**. Alternative mechanisms—such as unresolved spatial observation error cross-correlations, forward operator approximations, observation preprocessing, or geographic sample selection—can also depress the empirical innovation variance.
     - Definitive attribution requires formal calibration diagnostics (e.g. Desroziers consistency relations or objective covariance tuning). Claims asserting either proven filter optimality or proven covariance over-estimation remain scientifically unsupported.
4. **Observation Record Counts vs Acceptance/Rejection Audits:**
   - The 9-month archive contains **1,080,481 valid grid-time innovation records** (`innov_01 > -9000.0`).
   - While LIS populates `innov_01` during active EnKF processing cycles, calling every record an accepted physical state update is unverified without independent tile-by-tile acceptance logs or explicit Kalman weight telemetry. These records are rigorously designated as **valid grid-time innovation records** rather than proven unique physical update events.
   - Rejection counts by QC flags or unobserved cell ratios cannot be proven without examining raw SMAP HDF5 orbital footprints or dedicated diagnostic log files.

---

## 8. Final 2016 Restart Dependencies & Downstream Implications

The final restart files produced at `2016-01-01 00:00:00`:
- **Surface NetCDF:** `restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc` (21 MB, SHA-256: `46de5914372a...`)
- **Perturbation Binary:** `restarts/pert/LIS_DAPERT_201601010000.d01.bin` (137 MB, SHA-256: `39db9fe4ce24...`)

### Downstream Experiments Dependent on these Restarts:
1. [`experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020`](../matrix_2016_2020/DA_nocdf_noirr_2016_2020): Configured to read both files directly.
2. [`experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020`](../matrix_2016_2020/DA_cdf_noirr_2016_2020): Configured to read both files directly.
3. [`experiments/NorthMor/matrix_2016_2020/DA_anomaly_noirr_2016_2020`](../matrix_2016_2020/DA_anomaly_noirr_2016_2020): Configured to read both files directly.

### Methodological Assessment & Remaining Uncertainties:
- **For `DA_nocdf`:** Fully methodologically consistent. Both the 2015 spin-up and the 2016–2020 run assimilate unscaled SMAP observations under identical stochastic perturbation settings.
- **For `DA_cdf`:** `SPINUP_DA` assimilated unscaled SMAP observations. When `DA_cdf` begins in January 2016, it scales SMAP observations to match Noah-MP open-loop climatology.
  - *Theoretical Adjustment Hypothesis:* It is hypothesized that `DA_cdf` undergoes a physical transition or relaxation period as the model state adjusts from the NoCDF-spun-up regime toward the CDF-scaled regime.
  - *Correction of Previous Claim:* A "demonstrated 1–3 month DA-CDF adjustment period" has **NOT** been empirically demonstrated. Quantifying the actual relaxation timescale requires analyzing the 2016 `DA_cdf` outputs directly, rather than asserting it from 2015 spin-up files.
  - *Operational Pragmatism:* Reusing `SPINUP_DA` restarts avoided a separate 9-month DA-CDF spin-up execution, providing an active 20-member perturbation state. However, downstream analyses comparing early 2016 `DA_cdf` to `DA_nocdf` must treat the first few months with caution.

---

## 9. Known Issues and Reproducibility Limitations

1. **Hardcoded Obsolete Paths:**
   - In `scripts/chain_da.py` (line 49): `base_dir = ".../experiments/NorthMor/step3_da_2015"`. This path was relocated to `SPINUP_DA` on July 9, 2026. Running the script directly will fail unless `base_dir` is updated.
   - Generated configuration files (`generated/configs/*.config`) and job scripts (`generated/jobs/*.sh`) contain absolute paths referencing `step3_da_2015`.
2. **Kickoff Relative Path:**
   - In `job.sh`, `source ../../../../arch/arch_toubkal.env` is valid relative to `$SLURM_SUBMIT_DIR` (4 directory levels up reaches repository root `NoahMP_Morocco/`).

---

## 10. Potential Cleanup Candidates (NOT APPROVED FOR DELETION)

| Item | Size | Proposed Classification | Scientific Rationale |
| :--- | :--- | :--- | :--- |
| `restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc` | 21 MB | **CRITICAL KEEP** | Active initial condition for all 2016–2020 DA matrix experiments. |
| `restarts/pert/LIS_DAPERT_201601010000.d01.bin` | 137 MB | **CRITICAL KEEP** | Active initial perturbation state for all 2016–2020 DA matrix experiments. |
| `restarts/surf/` (months 04–11, 8 files) | 168 MB | **KEEP AS PROVENANCE** | Intermediate monthly surface checkpoints documenting restart chaining. |
| `restarts/pert/` (months 04–11, 8 files) | 1.05 GB | **KEEP AS PROVENANCE** | Intermediate monthly perturbation checkpoints documenting covariance spin-up. |
| `output/` (9 monthly directories) | 3.6 GB | **KEEP** | Daily histories, innovations, increments, and spread files supporting all EnKF diagnostics. |
| `logs/` (9 monthly directories) | 278 MB | **KEEP AS PROVENANCE** | Indispensable execution audit trail of jobs `7260791` through `7262178`. |\n
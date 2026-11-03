# DA_cdf_noirr_2016_2020 — Historical SMAP-EnKF Data Assimilation Simulation with CDF Matching (2016–2020)

**Author:** Mohammad El Aabaribaoune

---

## 1. Scientific Overview, Objectives & Domain Definition

The `DA_cdf_noirr_2016_2020` experiment constitutes the **bias-corrected satellite data assimilation (CDF-matching) component** of the 5-year experimental matrix ($2016\text{--}2020$) for Northern Morocco. It integrates NASA SMAP L3 enhanced surface soil moisture retrievals into the Noah-MP land surface model using a 1-dimensional Ensemble Kalman Filter (EnKF) across 20 ensemble members, with Cumulative Distribution Function (CDF) matching calibrated on Northern Morocco, and with anthropogenic irrigation deactivated.

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
1. **Bias-Corrected Satellite Assimilation:** Ingest SMAP surface soil moisture into Noah-MP after correcting systematic differences in climatological mean and dynamic range between the satellite retrieval algorithm and the land surface model via piecewise linear CDF matching.
2. **CDF vs. NoCDF Experimental Counterpart:** Provide the scaled assimilation counterpart to [`DA_nocdf_noirr_2016_2020`](../DA_nocdf_noirr_2016_2020/README.md). Juxtaposing CDF-scaled assimilation against raw NoCDF assimilation enables isolating the structural impact of climatological quantile alignment versus transient innovation updating on root-zone soil moisture states, runoff partitioning, and evapotranspiration.
3. **Multi-Year Ensemble Land Surface Reanalysis:** Produce a continuous 5-year, 20-member ensemble reanalysis of root-zone soil moisture, surface energy fluxes, runoff components, and water table dynamics across Northern Morocco under active Kalman updating.

### 1.2 Domain Specification
* **Domain Name:** Northern Morocco (`NorthMor`)
* **Spatial Extent:** $30.00^\circ\text{N}$ to $36.00^\circ\text{N}$ Latitude; $-10.00^\circ\text{E}$ to $-1.00^\circ\text{E}$ Longitude.
* **Grid Resolution:** $0.05^\circ$ regular lat/lon grid spacing (~$5\text{ km}$ nominal resolution; $121 \times 181$ grid points).
* **Active Land Grid:** $16,030$ active land tiles over Morocco extracted from [`data/lis_input/lis_input_NorthMor_5km.nc`](../../../../data/lis_input/lis_input_NorthMor_5km.nc).
* **Ensemble Dimension:** 20 members per land tile, yielding $16,030 \times 20 = 320,600$ computational tiles.

---

## 2. Model Framework, Physics & Meteorological Forcing

The simulation physics are parameterized in [`templates/lis_da.config.template`](templates/lis_da.config.template) and executed using the Land Information System Framework (LISF).

### 2.1 Model Discretization and Architecture
* **Land Surface Model:** Noah-MP version 4.0.1.
* **Simulation Timestep:** 15 minutes (`15mn`).
* **Parallel Layout:** 1 node, 32 MPI tasks ($4 \times 8$ 2D spatial domain decomposition).
* **Soil Discretization:** 4 soil layers with node thicknesses of $0.10\text{ m}$ (Layer 1, $0\text{--}10\text{ cm}$), $0.30\text{ m}$ (Layer 2, $10\text{--}40\text{ cm}$), $0.60\text{ m}$ (Layer 3, $40\text{--}100\text{ cm}$), and $1.00\text{ m}$ (Layer 4, $100\text{--}200\text{ cm}$), totaling a $2.0\text{ m}$ active soil column.
* **Snow Discretization:** Up to 3 physical snow layers (`Number of snow layers: 3`).

### 2.2 Noah-MP Physical Parameterizations
* **Groundwater and Runoff Option:** Option 1 (`SIMGM`), Simple groundwater model with unconfined aquifer dynamics, equilibrium water table depth (`ZWT`), and groundwater reservoir storage (`WA`).
* **Dynamic Vegetation:** Option 2 (`Dynamic phenology`), dynamic leaf area index (LAI) and stem area index (SAI) prognostically calculated based on carbon allocation.
* **Stomatal Resistance:** Option 1 (`Ball-Berry`), coupled stomatal conductance and photosynthesis.
* **Radiation Transfer:** Option 1 (`Modified two-stream`), accounting for 3D canopy structure and gap fraction.
* **Surface Layer Drag Coefficient:** Option 1 (`Monin-Obukhov similarity theory`).
* **Snow Surface Albedo:** Option 1 (`BATS`), accounting for snow aging and grain growth.
* **Rainfall & Snowfall Partitioning:** Option 1 (`Jordan 1991`), temperature-dependent precipitation phase separation.
* **Supercooled Soil Water & Frozen Soil Permeability:** Options 1 (`Niu and Yang 2006`).
* **Lower Boundary of Soil Temperature:** Option 2 (`Thermal diffusion`), zero net flux condition at $8.0\text{ m}$ bedrock depth.
* **Crop Model & Irrigation:** Option 0 (`Crop model option: 0`), anthropogenic irrigation strictly deactivated.

### 2.3 Meteorological Forcing Ingestion
1. **Primary Forcing:** NASA MERRA-2 reanalysis (`MERRA2`), ingested at hourly frequency, providing 2m air temperature, specific humidity, surface pressure, 10m zonal/meridional wind, surface incoming shortwave and longwave radiation, and background precipitation. Topographic lapse-rate elevation correction is applied (`lapse-rate`).
2. **Secondary Precipitation Overlay:** NASA GPM IMERG Final Precipitation (`GPM IMERG`), ingested at 30-minute frequency without downscaling (`overlay` blending method).
3. **Ensemble Forcing Allocation:** In [`src/lisf/lis/core/LIS_metforcingMod.F90:1279-1296`](../../../../src/lisf/lis/core/LIS_metforcingMod.F90#L1279-L1296), `ensembleForcings` partitions the 20 members across the 2 forcing sources:
   - **Cohort 1 (Members 1–10):** Driven by MERRA-2 meteorological forcing.
   - **Cohort 2 (Members 11–20):** Driven by MERRA-2 base fields overlaid with GPM IMERG precipitation.

### 2.4 Ensemble Perturbation Scheme
Ensemble dispersion is driven by the GMAO perturbation framework:
* **Meteorological Forcing Perturbations ([`data/pert_package/forcing_pertattribs.txt`](../../../../data/pert_package/forcing_pertattribs.txt)):**
  - *Precipitation:* Multiplicative log-normal noise, standard deviation $\sigma = 0.5$, cross-member bounds $[0.1, 8.0]$, temporal decorrelation timescale $86,400\text{ s}$ (24 hours).
  - *Downwelling Shortwave Radiation:* Multiplicative log-normal noise, $\sigma = 0.3$, bounds $[0.2, 2.5]$, timescale $86,400\text{ s}$.
  - *Downwelling Longwave Radiation:* Additive Gaussian noise, $\sigma = 20.0\text{ W}/\text{m}^2$, bounds $[-50, +50]\text{ W}/\text{m}^2$, timescale $86,400\text{ s}$.
  - *Near-Surface Air Temperature:* Additive Gaussian noise, $\sigma = 1.0\text{ K}$, bounds $[-3.0, +3.0]\text{ K}$, timescale $86,400\text{ s}$.
  - *Near-Surface Wind Speed:* Multiplicative log-normal noise, $\sigma = 0.25$, bounds $[0.1, 5.0]$, timescale $86,400\text{ s}$.
* **Prognostic State Perturbations ([`data/pert_package/noahmp_sm_pertattribs.txt`](../../../../data/pert_package/noahmp_sm_pertattribs.txt)):**
  - *Layer 1 Soil Moisture ($0\text{--}10\text{ cm}$):* Additive Gaussian noise, $\sigma = 0.004\text{ m}^3/\text{m}^3$, truncation limit $\pm 0.010\text{ m}^3/\text{m}^3$, timescale $21,600\text{ s}$ (6 hours).
  - *Layers 2–4 Soil Moisture ($10\text{--}200\text{ cm}$):* Zero prognostic perturbation applied ($\sigma = 0.0$); ensemble spread in root-zone layers develops dynamically via vertical infiltration, root water uptake, and Kalman cross-layer gain coupling.

---

## 3. SMAP Observations, EnKF & CDF-Matching Configuration

### 3.1 Observation Dataset Specifications
* **Observation Product:** NASA SMAP Level-3 Enhanced Radiometer Global Daily 9 km EASE-Grid Soil Moisture (`SPL3SMP_E`).
* **Data Directory:** `./data/observations/SMAP_SPL3SMP_E`
* **Retrieval Characteristic:** Volumetric soil moisture ($\text{m}^3/\text{m}^3$) representing the top $0\text{--}5\text{ cm}$ of the soil column.
* **Product Version & Release:** ECS Version ID `006`, Composite Release ID `R19240` (specified as `"R19"` in LIS configuration).
* **Observation Screening Pipeline:**  
  The data assimilation pipeline implements a multi-stage screening structure distinguishing satellite retrieval screening, land surface model screening, and state/observation boundary definitions:
  - **SMAP Retrieval Quality Screening ([`read_NASASMAPsm.F90`](../../../../src/lisf/lis/dataassim/obs/NASA_SMAPsm/read_NASASMAPsm.F90#L1145-L1165)):**
    - *Configuration Key Status:* The configuration line `SMAP(NASA) soil moisture apply SMAP QC flags: 1` in [`templates/lis_da.config.template`](templates/lis_da.config.template) is obsolete and unparsed by the LISF 7.5 SMAP reader; source-code comments in [`NASASMAPsm_Mod.F90:23-24`](../../../../src/lisf/lis/dataassim/obs/NASA_SMAPsm/NASASMAPsm_Mod.F90#L23-L24) confirm this toggle was eliminated in July 2020 and retrieval QC is permanently hardcoded ON.
    - *Retrieval Quality Bitmask:* LIS reads the HDF5 variable `retrieval_qual_flag` (or `retrieval_qual_flag_pm`) and inspects bit 0 (`ibits(sm_qa, 0, 1) == 0`). Bit 0 indicates composite recommended retrieval quality; if bit 0 is set (or data is invalid), the observation is rejected and set to `-9999.0`. LIS does not parse individual environmental condition sub-bits (e.g., surface water fraction or steep terrain flags) directly, relying entirely on NASA's composite recommended quality indicator.
    - *Vegetation Water Content (VWC) Screening:* LIS evaluates the HDF5 field `vegetation_water_content` (or `vegetation_water_content_pm`) and rejects retrievals where $\text{VWC} > 5.0\text{ kg}/\text{m}^2$, setting the value to missing (`LIS_rc%udef`).
  - **Noah-MP Model-Side Observation Screening ([`noahmp401_qc_soilmobs.F90:226-276`](../../../../src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90#L226-L276)):**  
    Interpolated observations undergo comprehensive model-state screening in subroutine `NoahMP401_qc_soilmobs` prior to EnKF analysis update calculation:
    - *Precipitation:* Rejected if model precipitation rate exceeds threshold (`rainf_obs > 3E-6` $\text{kg}/\text{m}^2/\text{s}$).
    - *Frozen Soil:* Rejected if soil ice is detected in any layer ($|\theta_{\text{total}} - \theta_{\text{liquid}}| > 0.0001\text{ m}^3/\text{m}^3$ across Layers 1–4).
    - *Freezing Temperatures:* Rejected if model soil temperature in any layer ($T_{\text{soil}, 1\dots 4} \le 273.15\text{ K}$) or ground surface skin temperature ($T_{\text{skin}} \le 273.15\text{ K}$) is at or below freezing (`LIS_CONST_TKFRZ`).
    - *Dense Forest Cover:* Rejected over dense forest landcover categories (`vegt <= 4`).
    - *Snow Cover:* Rejected if snow water equivalent $\text{SWE} > 0.001\text{ m}$ (`sneqv_obs > 0.001`) or snow cover area fraction $\text{SCA} > 0.0001$ (`sca_obs > 0.0001`).
    - *High Green Vegetation Fraction:* Rejected if shading greenness fraction exceeds threshold (`shdfac_obs > 0.9`).
    - *Physical Boundary Proximity (Tails Rejection):* Rejected if the observation falls within $0.02\text{ m}^3/\text{m}^3$ of soil saturation ($\theta_{\text{sat}} - \theta_{\text{obs}} < 0.02$) or wilting point ($\theta_{\text{obs}} - \theta_{\text{wilt}} < 0.02$) to avoid numerical filter instability near asymptotic bounds.
  - **Observation & State Bounds Defined in Attribute Files:**
    - *Observation Attribute Bounds:* [`data/pert_package/smap_attribs.txt`](../../../../data/pert_package/smap_attribs.txt) prescribes generic observation validity bounds ($0.01 \le \theta_{\text{obs}} \le 1.0\text{ m}^3/\text{m}^3$) checked during generic LIS observation initialization.
    - *Prognostic State Bounds:* [`data/pert_package/noahmp_sm_attribs.txt`](../../../../data/pert_package/noahmp_sm_attribs.txt) prescribes model state limits ($0.01 \le \theta_{\text{model}} \le 0.55\text{ m}^3/\text{m}^3$) for Layers 1–4. These bounds govern state perturbation truncation and model state clamping; they do not function as the model-side observation screening routine.

### 3.2 Assimilation Algorithm & CDF-Matching Parameterization
* **Assimilation Algorithm:** 1-Dimensional Ensemble Kalman Filter (`1D EnKF`, `Number of data assimilation instances: 1`).
* **Ensemble Size:** 20 members (`Number of ensembles per tile: 20`).
* **Scaling Strategy:** `Data assimilation scaling strategy: "CDF matching"` (Cumulative Distribution Function matching).
* **State Vector Dimension:** `Number of state variables: 4`. Volumetric soil moisture across all 4 vertical layers is registered in the Kalman state vector, with increments distributed vertically based on ensemble background error cross-correlations.
* **CDF Quantile Resolution:** `SMAP(NASA) soil moisture number of bins in the CDF: 100` (100 discrete probability bins dimensioned in `SoilMoist_CDF`). In [`src/lisf/lis/core/LIS_dataAssimMod.F90:745-770`](../../../../src/lisf/lis/core/LIS_dataAssimMod.F90#L745-L770) (`LIS_rescale_with_CDF_matching`), LIS maps each observation to its discrete quantile bin index along `obs_xrange` and assigns the corresponding quantile value along `model_xrange` without continuous polynomial or spline fitting.
* **CDF Scaling Model:** `SMAP(NASA) soil moisture use scaled standard deviation model: 0` (standard piecewise linear quantile-quantile mapping without variance post-scaling; option 1 is disabled in LIS).
* **CDF File Ingestion Option:** `SMAP(NASA) CDF read option: 1` (reads multi-month climatological NetCDF CDF files).
* **Observation Perturbation Scheme:** GMAO perturbation scheme (`data/pert_package/smap_pertattribs.txt`), additive Gaussian noise (`perttype = 0`), standard deviation $\sigma_v = 0.04\text{ m}^3/\text{m}^3$ (consistent with SMAP mission target accuracy), truncation limit `std_max = 2.5` ($\pm 0.10\text{ m}^3/\text{m}^3$), zero mean (`zeromean = 1`), temporal decorrelation timescale $43,200\text{ s}$ (12 hours), spatial correlation length $0.0$, and cross-variable correlation $1.0$.

---

## 4. CDF Generation, Provenance & Spatial Validation

### 4.1 Production CDF Files for Northern Morocco
The CDF matching transfer functions applied during the simulation were pre-computed using the Land Data Toolkit (LDT) under `LDT running mode: "DA preprocessing"`.

* **Observation CDF File (SMAP SPL3SMP_E):**
  * Path on Lustre: [`experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc`](../CDF/OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc)
  * Cryptographic Hash (MD5): `98c56b7ae1e27ac752a5b6b8172c12b6`
  * Associated Domain Checkpoint: `smap_obs_cdf_NorthMor_domain.nc`
  * File Size: $53,928,133\text{ bytes}$ (~$53.9\text{ MB}$)
  * Dimensions: `ngrid: 16030`, `ntimes: 12` (monthly climatology), `nbins: 100`, `SoilMoist_levels: 1`
  * Variables: `SoilMoist_xrange`, `SoilMoist_mu`, `SoilMoist_sigma`, `SoilMoist_CDF`
* **Model CDF File (Noah-MP 4.0.1 Open Loop):**
  * Path on Lustre: [`experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc`](../CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc)
  * Cryptographic Hash (MD5): `5b28260743b52d2a958b7adaf05ac2c6`
  * Associated Domain Checkpoint: `noahmp_model_cdf_NorthMor_domain.nc`
  * File Size: $93,504,433\text{ bytes}$ (~$93.5\text{ MB}$)
  * Dimensions: `ngrid: 16030`, `ntimes: 12`, `nbins: 100`, `SoilMoist_levels: 1`
  * Variables: `SoilMoist_xrange`, `SoilMoist_mu`, `SoilMoist_sigma`, `SoilMoist_CDF`

### 4.2 LDT Configuration and Climatological Provenance
* **Observation LDT Configuration:** [`experiments/NorthMor/matrix_2016_2020/CDF/ldt.config.cdf.obs.NorthMor`](../CDF/ldt.config.cdf.obs.NorthMor)
  * Period: 2016-01-01 to 2021-01-01 (60 months, 5 years).
  * Observation Directory: `../../../../data/observations/SMAP_SPL3SMP_E`
  * Ingestion list: Preserved in `SMAP_filelist.dat`.
* **Model LDT Configuration:** [`experiments/NorthMor/matrix_2016_2020/CDF/ldt.config.cdf.model.NorthMor`](../CDF/ldt.config.cdf.model.NorthMor)
  * Period: 2016-01-01 to 2021-01-01 (60 months, 5 years).
  * Ingestion Directory: `combined_OPL_noirr/SURFACEMODEL/`, containing 60 monthly symlinks pointing directly to the verified open-loop history outputs of [`OPL_noirr_2016_2020`](../OPL_noirr_2016_2020/).
* **Version Control Policy:** The binary NetCDF CDF files remain on Lustre storage and are excluded from Git tracking in accordance with repository data policy; their provenance, MD5 hashes, and generation configurations are preserved in version control.

### 4.3 Spatial Domain Alignment and Pre-Flight Validation
In LISF, CDF arrays are dimensioned linearly as a 1D vector `ngrid`. During execution, LIS reads the CDF data sequentially by tile index without dynamic latitude/longitude coordinate lookups. Consequently, absolute numerical and spatial concordance between the LDT CDF domain and the LIS landmask is an essential requirement.

Spatial consistency was verified via [`scripts/check_cdf_domain.py`](scripts/check_cdf_domain.py):
1. **1D Point Equality:** $\text{ngrid}_{\text{CDF}} = 16,030 \equiv \sum(\text{LANDMASK} == 1)_{\text{lis\_input}} = 16,030$.
2. **2D Grid Concordance:** Landmask differences between `*_domain.nc` and `lis_input_NorthMor_5km.nc` equal exactly **0 pixels** ($121 \times 181$ grid).
3. **Coordinate Equality:** Maximum absolute difference on latitude and longitude coordinates is strictly **$0.000000\text{e}+00$**.

### 4.4 Historical Context: Invalid National CDF Domain
Prior to October 2026, an earlier assimilation run utilized CDF files (`smap_cdf.nc`) generated over a national Morocco grid containing **$66,391$ grid points**:
* **Mechanism of Incompatibility:** When LIS executed the Northern Morocco domain ($16,030$ active land points), it read the first $16,030$ entries of the $66,391$-point CDF array sequentially. Because the national grid ordered points from south to north, LIS mapped CDF transfer functions calculated over southern and Saharan Morocco onto agricultural and mountainous catchments in Northern Morocco (Rif, Gharb, Saïss).
* **Demonstrated Impact:** This spatial misallocation inverted seasonal soil moisture dynamics, induced spurious negative innovations, and distorted water balance closure.
* **Archive Location:** All data, outputs, and downstream models associated with the invalid 66,391-point CDF domain were completely isolated on 2026-11-02 into [`experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/`](../_ARCHIVE_WRONG_CDF_DOMAIN/) ($38\text{ GB}$). The invalid simulation is not a valid scientific baseline and must not be used for hydrometeorological analysis.
* **Scope of Attribution:** The dimensional mismatch ($66,391$ vs $16,030$) is the sole established technical cause of the historical invalidation; no speculative secondary causes are asserted.

### 4.5 Sensitivity Tests: `DA_cdf_TEST` and `DA_cdf_TEST_1619`
Prior to production execution, two distinct short-period exploratory sensitivity tests were conducted over two representative months (January 2018 and August 2018):
1. **`DA_cdf_TEST` ($884\text{ MB}$):** Evaluated numerical stability and innovation magnitude using the 5-year NorthMor CDF ($2016\text{--}2020$).
2. **`DA_cdf_TEST_1619` ($884\text{ MB}$):** Evaluated sensitivity to climatological sample length using a 4-year NorthMor CDF ($2016\text{--}2019$, generated via `OUTPUT_*_NorthMor_2016_2019/`).
* *Distinction:* These tests served solely as internal sensitivity benchmarks and are strictly distinguished from the 60-month production simulation.

---

## 5. Ensemble Initialization & Restart Provenance

The 20-member ensemble for `DA_cdf_noirr_2016_2020` was initialized from identical historical checkpoints as `DA_nocdf_noirr_2016_2020`, originating from the upstream spin-up hierarchy:

### 5.1 Upstream Spin-up Lineage
1. **Stage 1 — `SPINUP_OPL` ($2005\text{--}2016$):** 11-year deterministic simulation producing climatological equilibrium. After 10 completed years ($2005\text{--}2014$), the intermediate checkpoint `LIS_RST_NOAHMP401_201501010000.d01.nc` (1 member, 16,030 tiles, 1.6 MB) was extracted to initialize ensemble generation. The final checkpoint at 2016-01-01 (`LIS_RST_NOAHMP401_201601010000.d01.nc`) concluded the full 11-year deterministic spin-up and initialized deterministic experiments (such as `OPL_noirr_2016_2020`), NOT `ENS_OPL_2015`.
2. **Expansion — `scripts/expand_restart.py`:** Replicated each deterministic tile from the 2015-01-01 checkpoint 20 times into contiguous 20-member blocks, creating `LIS_RST_NOAHMP401_201501010000_ens20.d01.nc` (320,600 tiles, 90 MB) with zero initial cross-member variance.
3. **Stage 2 — `ENS_OPL_2015` ($2015-01-01\text{ to }2015-04-01$):** 3-month unassimilated ensemble spin-up generating initial perturbation covariance structures under GMAO forcing and state noise.
4. **Stage 3 — `SPINUP_DA` ($2015-04-01\text{ to }2016-01-01$):** 9-month active SMAP assimilation spin-up establishing dynamic background error covariance before launching 2016 production runs.

### 5.2 Initial Restarts for Production
* **Surface Model Restart File:**
  * Path: [`experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc`](../../SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc)
  * File Size: $21,173,636\text{ bytes}$ (~$21\text{ MB}$)
  * Cryptographic Hash (MD5): `3a469aca9bf8115d7f56395e49727a2a`
  * Tile Structure: $320,600$ interleaved tiles ($16,030\text{ land cells} \times 20\text{ ensemble members}$).
* **Ensemble Perturbation Restart File:**
  * Path: [`experiments/NorthMor/SPINUP/SPINUP_DA/restarts/pert/LIS_DAPERT_201601010000.d01.bin`](../../SPINUP/SPINUP_DA/restarts/pert/LIS_DAPERT_201601010000.d01.bin)
  * File Size: $137,345,188\text{ bytes}$ (~$137\text{ MB}$)
  * Cryptographic Hash (MD5): `21afc5f46cbc63c06cc1c4f6510f5a87`

---

## 6. Historical Execution Chronology & Monthly Chaining

### 6.1 Execution Workflow and Spatial Guard
Execution was orchestrated via [`scripts/chain_da.py`](scripts/chain_da.py), implementing an automated sequential pipeline:
1. **Configuration Generation:** Reads [`templates/lis_da.config.template`](templates/lis_da.config.template), dynamically updates monthly simulation timestamps, restart file pointers, output paths, and generates monthly configuration files in `generated/configs/`.
2. **Pre-Execution Guard Check:** Prior to invoking the LIS executable, each SLURM job script automatically executes:
   ```bash
   /home/mohammad.elaabaribao/.conda/envs/smap-xai-audit/bin/python scripts/check_cdf_domain.py \
       --config generated/configs/lis_DA_SMAP_cdf_noirr_<YYYY-MM>.config \
       --run-dir $(pwd)
   ```
   If spatial or dimensional mismatch is detected, execution aborts immediately before MPI launch.
3. **SLURM Chaining:** Upon successful completion of month $M$ (`COMPLETED`, ExitCode `0:0`), `chain_da.py` verifies the generation of end-of-month restart files (`LIS_RST_NOAHMP401_<YYYYMM010000>.d01.nc` and `LIS_DAPERT_<YYYYMM010000>.d01.bin`), stages them as initial conditions for month $M+1$, generates the next configuration, and submits the next job.

### 6.2 Execution Timeline
The complete 60-month production simulation was executed from **2026-10-27T21:34:37** to **2026-10-31T18:37:01** (total wallclock duration: ~3.8 days).
* **SLURM JobIDs:** 60 consecutive jobs from **8188120** (2016-01) to **8215966** (2020-12).
* **Job Execution Status:** 100% of jobs completed successfully with SLURM status `COMPLETED` and exit code `0:0`.
* **Execution Duration:** Monthly wallclock execution times averaged ~1 hour 33 minutes per month.
* Complete per-month timestamps, JobIDs, and durations are documented in [`MANIFEST.md`](MANIFEST.md).

### 6.3 Configuration Comparison: CDF vs. NoCDF
A line-by-line comparison between [`DA_cdf_noirr_2016_2020/templates/lis_da.config.template`](templates/lis_da.config.template) and [`DA_nocdf_noirr_2016_2020/templates/lis_da.config.template`](../DA_nocdf_noirr_2016_2020/templates/lis_da.config.template) confirms:
* **Identical Parameters:** Physical parameterizations, vertical soil layer thicknesses, meteorological forcing sources, perturbation parameters, time steps, output diagnostics, and EnKF algorithm settings are strictly identical.
* **Sole Configured Differences:**
  1. `Data assimilation scaling strategy`: `"CDF matching"` (CDF) vs. `"none"` (NoCDF).
  2. `SMAP(NASA) model CDF file`: `./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc` (CDF) vs. `./data/cdf/smap_model_cdf.nc` (NoCDF).
  3. `SMAP(NASA) observation CDF file`: `./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc` (CDF) vs. `./data/cdf/smap_obs_cdf.nc` (NoCDF).

---

## 7. Output Structure & Data Assimilation Diagnostics

### 7.1 Monthly Output Organization
Outputs are archived on Lustre in monthly directories `output/<YYYY-MM>/`:
* **Land Surface History Files (`SURFACEMODEL/<YYYYMM>/LIS_HIST_*.d01.nc`):** Daily averaged 2D grids ($121 \times 181$) containing ensemble-mean hydrological states and fluxes (`SoilMoist_tavg` for Layers 1–4, `TotalPrecip_tavg`, `Evap_tavg`, `Qs_tavg`, `Qsb_tavg`, `TVeg_tavg`, `ESoil_tavg`, `ECanop_tavg`).
* **Ensemble Kalman Filter Outputs (`EnKF/<YYYYMM>/`):**
  * `LIS_DA_EnKF_<YYYYMMDDHHMM>_incr.a01.d01.nc`: Analysis increments $\Delta \theta = \theta_{\text{analysis}} - \theta_{\text{forecast}}$ for Layers 1–4.
  * `LIS_DA_EnKF_<YYYYMMDDHHMM>_spread.a01.d01.nc`: Ensemble dispersion diagnostic files.
  * `LIS_DA_EnKF_<YYYYMMDDHHMM>_innov.a01.d01.nc`: Innovations $y - H(x)$ and observation error covariance.
* **Processed Observations (`DAOBS/<YYYYMM>/LIS_DAOBS_*.d01.nc`):** Quality-controlled, scaled SMAP observations mapped to the model grid.
* **Restart Checkpoints (`restarts/`):** 60 surface restart files in `restarts/surf/` and 60 perturbation binary files in `restarts/pert/`.

### 7.2 Data Assimilation Diagnostic Caveats
1. **Innovations vs. Accepted Updates:** In LIS NetCDF diagnostic files, the presence of non-missing values in `_innov.nc` indicates that satellite observations passed quality screening and innovation calculation. However, this does not imply that an analysis increment was applied to the prognostic state. In [`noahmp401_setsoilm.F90`](../../../../src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90), if fewer than 50% of ensemble members remain within physical bounds ($[0.02, \theta_{\text{sat}}-0.02]$), the update is rejected for the entire grid cell.
2. **Analysis Increments Written Prior to Boundary Adjustments:** In [`src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90:414,1009-1130`](../../../../src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90#L414), analysis increments stored in `_incr.nc` are assigned directly from the unconstrained Kalman update equation (`enkf_struc(n,k)%anlys_incr`) and written via subroutine `writeAnalysisIncr`. This occurs **before** [`noahmp401_setsoilm.F90:79-210`](../../../../src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90#L79-L210) performs physical validity checks ($sh2o \in [0.02, \theta_{\text{sat}}-0.02]$), midrange substitution for out-of-bounds members, or full grid-cell update rejection when $<50\%$ of members are valid. Because `noahmp401_setsoilm.F90` does not update `enkf_struc%anlys_incr`, the NetCDF increment fields record the raw mathematical Kalman increments rather than the post-clamping state adjustment actually applied to the model.
3. **Ensemble Spread Defined as Range:** In [`src/lisf/lis/core/LIS_historyMod.F90:7949-7984`](../../../../src/lisf/lis/core/LIS_historyMod.F90#L7949-L7984) (subroutine `LIS_writevar_spread`, called from [`enkf_Mod.F90:988`](../../../../src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90#L988)), standard deviation calculation is deactivated in the source code (`#if 0 ... #endif`), and LIS explicitly evaluates `gtmp(c,r) = max_v - min_v`. Consequently, the diagnostic field `ensspread_*` in `_spread.nc` represents the **ensemble range** ($\max - \min$) across members, and not the sample standard deviation ($\sigma$) or variance.

---

## 8. Implementation Characteristics & Technical Limitations

Analysis of the compiled LISF 7.5 codebase reveals specific algorithmic characteristics governing ensemble behavior:

### 8.1 Interleaved 20-Member NetCDF Restart Indexing
In surface restart NetCDF files (`LIS_RST_NOAHMP401_*.d01.nc`), dimensions are `ntiles = 320600` and `dim2 = 4`. The 20 ensemble members are stored consecutively cell-by-cell in an interleaved structure:
$$\text{SMC}[\text{layer}, \text{tile}] \equiv \text{SMC}[\text{layer}, \text{cell}, \text{member}]$$
where $\text{tile} = (\text{cell}-1) \times 20 + \text{member}$ ($1 \le \text{cell} \le 16,030$; $1 \le \text{member} \le 20$).

### 8.2 Deterministic State Perturbation Exclusion for Members 10 and 20
In [`src/lisf/lis/core/LIS_lsmMod.F90:1181-1205`](../../../../src/lisf/lis/core/LIS_lsmMod.F90#L1181-L1205), LIS implements the Ryu et al. (2009) perturbation bias-correction scheme by partitioning the ensemble into sub-groups according to `nmetforc = 2`:
$$\text{nxx} = \frac{\text{LIS\_rc\%nensem}}{\text{LIS\_rc\%nmetforc}} = \frac{20}{2} = 10$$
* **Cohort 1 ($f=1$, MERRA-2):** Sub-indices $m = 1 \dots 10$. Terminal member $m = \text{nxx} = 10 \implies$ **Member 10**.
* **Cohort 2 ($f=2$, IMERG):** Sub-indices $m = 1 \dots 10$. Terminal member $m = \text{nxx} = 10 \implies$ **Member 20**.
* **Exclusion Logic:** Lines 1190 and 1198 apply state perturbations only `if (m .ne. nxx)`. When $m = 10$, this condition evaluates to **FALSE**.
* **Direct Result:** **Members 10 and 20 receive ZERO prognostic state perturbations (`stvar = stvar + pert`).**
* In Layer 1 ($\sigma = 0.004\text{ m}^3/\text{m}^3$), Members 10 and 20 exhibit $\sim 35\%\text{--}45\%$ lower spatial standard deviation than the other 18 members, while deeper unperturbed layers maintain near-unity variance ratios ($0.93\text{--}0.99$).

### 8.3 Configuration Bias-Correction Flag Overridden in Source Code
In all configuration files, `Apply perturbation bias correction: 0` was specified. However, in [`src/lisf/lis/core/LIS_readConfig.F90:793-798`](../../../../src/lisf/lis/core/LIS_readConfig.F90#L793-L798), reading this attribute is commented out and `LIS_rc%pert_bias_corr = 1` is **unconditionally hardcoded**.

### 8.4 Forcing Perturbation Indexing Inconsistency (`k` vs `f`)
In [`src/lisf/lis/core/LIS_metforcingMod.F90:1450-1470`](../../../../src/lisf/lis/core/LIS_metforcingMod.F90#L1450-L1470), forcing bias correction contains an indexing inconsistency:
* **Initial Perturbation Application (lines 1428–1447):** Checks `if (m .ne. LIS_rc%nensem(n))`. Only Member 20 is bypassed from initial forcing noise; Member 10 is perturbed.
* **Offset Accumulation Loop (line 1459):** Indexes tile $t = (j-1) \times 20 + \mathbf{(k-1) \times 10} + m$. Because $k=1$ (constant domain nest index), this evaluates to $(1-1) \times 10 = 0$ for both forcing cohorts ($f=1$ and $f=2$).
* **Cross-Forcing Offset:** For Cohort 2 ($f=2$, IMERG), the offset $\delta$ is computed by subtracting Member 20 (IMERG) from Cohort 1 members (MERRA-2) rather than Cohort 2 members (IMERG).

### 8.5 Physical Forcing Cohorts
The parameter `LIS_rc%nmetforc = 2` partitions the 20 members into two 10-member forcing cohorts. In [`LIS_metforcingMod.F90:1287-1296`](../../../../src/lisf/lis/core/LIS_metforcingMod.F90#L1287-L1296), Members 1–10 receive MERRA-2 precipitation, while Members 11–20 receive GPM IMERG precipitation where valid data exists.

### 8.6 LISF 7.5 Source Identification & Historical Binary Provenance
* Source notices across core routines are stamped `Land Information System Framework (LISF) Version 7.5 (2024)`.
* Binary `./src/lisf/lis/LIS` (16,666,992 bytes, MD5: `04150c14d7bcee2f83567688254b5a95`) resides on Lustre outside version control without recorded compiler toolchain specifications or build flags.

---

## 9. Reproducibility & Scientific Validation Limitations

Independent reproducibility and scientific interpretation are subject to specific documented constraints:

### 9.1 Climatological Calibration Period Overlap
The model CDF transfer function ([`noahmp_model_cdf_NorthMor.nc`](../CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc)) was derived from the 5-year open-loop simulation `OPL_noirr_2016_2020` spanning the exact same chronological period ($2016\text{--}2020$) as the assimilation experiment.
* **Analytical Scope:** Because calibration period and evaluation period overlap completely, the CDF parameters reflect the specific 2016–2020 climatological sample rather than an independent historical baseline.
* **Sensitivity Analysis vs. Out-of-Sample Validation:** The 4-year CDF test (`DA_cdf_TEST_1619`, calibrated on 2016–2019) confirms model sensitivity to calibration sample length, but does not constitute a fully independent out-of-sample temporal validation.

### 9.2 Execution Success vs. Independent Scientific Validation
The complete 60-month execution of `DA_cdf_noirr_2016_2020` without software aborts confirms numerical stability of the chained workflow under CDF matching. However:
* **Hydrological Accuracy:** Operational completion does not demonstrate whether CDF-scaled assimilation improves physical fidelity relative to unscaled NoCDF assimilation or open-loop simulations.
* **Independent Ground Truth:** Verification of root-zone soil moisture improvements, evapotranspiration realism, and water balance partitioning requires rigorous evaluation against independent in-situ hydrometeorological observations across Morocco (e.g., agricultural soil moisture networks, flux towers, or groundwater monitoring wells).

### 9.3 Numerical and Binary Reproducibility
Bit-for-bit reproducibility of historical runs cannot be guaranteed on differing HPC architectures or toolchains due to:
* Untracked MPI/compiler toolchains for historical executable `src/lisf/lis/LIS`.
* Asynchronous parallel pseudo-random number generator sequencing across 32 MPI tasks.

### 9.4 Git Tracking Status and Core Definition Files
* **Repository Policy:** Line 5 of [`.gitignore`](../../../../.gitignore#L5) excludes `experiments/`.
* **Core Definition Files Versioned in Git:**
  - [`config/experiment.ini`](config/experiment.ini): Master simulation date bounds and template linkage.
  - [`templates/lis_da.config.template`](templates/lis_da.config.template): Parametric specification of Noah-MP physics, SMAP ingestion, and CDF matching options.
  - [`scripts/chain_da.py`](scripts/chain_da.py): Monthly chunking, restart staging, guard check, and SLURM chaining.
  - [`scripts/check_cdf_domain.py`](scripts/check_cdf_domain.py): Standalone spatial and dimensional integrity guard.
  - [`MANIFEST.md`](MANIFEST.md): Cryptographic file hashes and 60-month SLURM JobID execution audit.
  - [`README.md`](README.md): Scientific documentation, verified implementation mechanisms, and reproducibility assessment.
* **Generated Run Configurations:** The 60 monthly configuration files (`generated/configs/`) and 60 SLURM job scripts (`generated/jobs/`) record exact historical execution parameters.
* **Excluded Primary Products:** High-volume binary restarts (`restarts/`), primary simulation outputs (`output/`), and MPI logs (`logs/`) remain on Lustre storage to maintain Git repository efficiency.

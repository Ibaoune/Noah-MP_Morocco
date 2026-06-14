# Sebou Basin Experiment Setup Guide
**Author:** M. EL Aabaribaoune (@um6p)

This document describes the scientific setup, datasets, and step-by-step workflow for running land surface model experiments (Open-Loop and three data assimilation variants) using Noah-MP/LIS over the Sebou River basin, Morocco.

---

## 1. Domain Configuration

| Parameter | Value |
|-----------|-------|
| Region | Upstream Sebou River basin + Saïss plain |
| South-West corner | `32.5° N, 7.0° W` |
| North-East corner | `35.5° N, 3.5° W` |
| Resolution | `0.05°` (~5 km) |
| Grid size | 60 × 70 = 4,200 grid points |
| Simulation period | January 1, 2015 — December 31, 2020 (6 years, matching Nie et al., 2022) |
| Timestep | 15 minutes |

---

## 2. Scientific Objectives

The experiments address two key research questions for Q1 publications:
1. **Hydrology (Paper 1):** *Can joint soil moisture and LAI assimilation improve streamflow, AET estimation, and root-zone soil moisture representation?*
2. **Agriculture (Paper 2):** *Does assimilation reduce irrigation water allocation uncertainties and crop stress detection times?*

---

## 3. Experiment Design

Four experiments are defined, all on the same Sebou basin domain, to allow controlled comparison:

| Label | Name | DA Instances | Config | Output |
|-------|------|-------------|--------|--------|
| **OPL** | Open-Loop | None | `lis.config.opl_sebou` | `experiments/OPL_sebou/` |
| **DA-SM** | SMAP SM assimilation | 1: SMAP(NASA) soil moisture | `lis.config.da_sm_sebou` | `experiments/DA_SM_sebou/` |
| **DA-LAI** | MODIS LAI assimilation | 1: MCD15A2H LAI | `lis.config.da_lai_sebou` | `experiments/DA_LAI_sebou/` |
| **DA-Joint** | Joint SM + LAI assimilation | 2: SMAP SM + MCD15A2H LAI | `lis.config.da_joint` | `experiments/DA_Joint_sebou/` |

All DA experiments use **EnKF with 20 ensemble members** and GMAO-scheme perturbations on forcing (precipitation, radiation) and state variables (soil moisture layers, LAI).

---

## 4. Data Download Instructions

Three Python scripts in `scripts/download/` query NASA's Common Metadata Repository (CMR):

| Dataset | Script | SLURM job |
|---------|--------|-----------|
| MERRA-2 forcing | `download_merra2.py` | `job_download_data.sh` |
| SMAP SPL3SMP v009 | `download_smap.py` | `job_download_data.sh` |
| MODIS MOD15A2H v061 tile h17v05 | `download_modis_lai.py` | `job_download_data.sh` |

```bash
sbatch scripts/jobs/job_download_data.sh
```
*All scripts are configured for the target period (2015-01-01 to 2020-12-31).*

---

## 5. Parameter Processing (LDT)

```bash
sbatch scripts/jobs/job_1_ldt_sebou.sh
```

**Status: ✅ Completed** — generated `data/lis_input.d01_sebou.nc`.

Domain parameter maps (saved in `postproc/figures/`):
- **Topography:** [sebou_topography.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_topography.png)
- **Land Cover (MODIS IGBP):** [sebou_landcover.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_landcover.png)
- **Soil Texture (STATSGO):** [sebou_soil_texture.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_soil_texture.png)

---

## 6. MODIS LAI Preprocessing (Required for DA-LAI and DA-Joint)

The LIS `"MCD15A2H LAI"` plugin reads global NetCDF4 files (`86400 × 43200` grid, EPSG:4326, 500 m resolution), not raw MODIS HDF tile files. A preprocessing step is required:

```bash
sbatch scripts/jobs/job_preprocess_modis_lai.sh
```

This runs `scripts/fix/preprocess_modis_lai.py` which:
- Warps each HDF tile from Sinusoidal to EPSG:4326 using GDAL
- Stamps the tile into a global grid (filled with `255` outside the tile)
- Saves compressed NetCDF4 files to `data/observations/MODIS_LAI/processed/YYYY/MCD15A2H.006_LAI_YYYYDOY.nc4`
- Renames variables from `Band1/Band2` to `Lai_500m/FparLai_QC` using `ncrename`

**Status: 🔄 Running** — SLURM job 7053114 submitted.

---

## 7. Running the Experiments

### Step 1 — Open-Loop (no assimilation)
```bash
sbatch scripts/jobs/job_2_lis_opl_sebou.sh
# Output → experiments/OPL_sebou/
```

### Step 2a — DA-SM (SMAP Soil Moisture only)
```bash
sbatch scripts/jobs/job_3a_lis_da_sm_sebou.sh
# Output → experiments/DA_SM_sebou/
```

### Step 2b — DA-LAI (MODIS LAI only, requires preprocessing)
```bash
# Wait for job_preprocess_modis_lai.sh to complete, then:
sbatch scripts/jobs/job_3b_lis_da_lai_sebou.sh
# Output → experiments/DA_LAI_sebou/
```

### Step 2c — DA-Joint (SMAP SM + MODIS LAI, requires preprocessing)
```bash
# Wait for job_preprocess_modis_lai.sh to complete, then:
sbatch scripts/jobs/job_3c_lis_da_joint_sebou.sh
# Output → experiments/DA_Joint_sebou/
```

> **Tip:** For the 3-day test run (2020-06-01 to 2020-06-04), the configs are already set. For the full 2015-2020 production run, update the `Ending year/month/day` fields in the config files.

---

## 8. Perturbation Attributes

| File | Used in |
|------|---------|
| `data/pert_package/forcing_attribs.txt` | All DA experiments |
| `data/pert_package/forcing_pertattribs.txt` | All DA experiments |
| `data/pert_package/noahmp_sm_attribs.txt` | DA-SM |
| `data/pert_package/noahmp_sm_pertattribs.txt` | DA-SM |
| `data/pert_package/smap_attribs.txt` | DA-SM, DA-Joint |
| `data/pert_package/smap_pertattribs.txt` | DA-SM, DA-Joint |
| `data/pert_package/noahmp_lai_attribs.txt` | DA-LAI, DA-Joint |
| `data/pert_package/noahmp_lai_pertattribs.txt` | DA-LAI, DA-Joint |
| `data/pert_package/modis_lai_attribs.txt` | DA-LAI, DA-Joint |
| `data/pert_package/modis_lai_pertattribs.txt` | DA-LAI, DA-Joint |

---

## 9. Verification & Validation Strategy

### Hydrology Focus (Paper 1)
- **River Discharge:** Route runoff via HYMAP; compare with ABHS gauge records.
- **Evapotranspiration (ET):** Compare against FAO WaPOR (250 m) or GLEAM v3.
- **Terrestrial Water Storage:** Validate against GRACE/GRACE-FO monthly anomalies.

### Agriculture Focus (Paper 2)
- **Irrigation Volumes:** Compare with ABHS regional water withdrawal estimates.
- **Crop Productivity:** Correlate simulated GPP anomalies with provincial wheat/barley yield statistics (Ministry of Agriculture of Morocco).


---

## 1. Domain Configuration

The domain is expanded to cover the entire upstream Sebou River basin feeding the reservoir, as well as adjacent agricultural perimeters in the Saïss plain:
*   **Bounding Box coordinates:**
    *   South-West Corner: `32.5° N, 7.0° W`
    *   North-East Corner: `35.5° N, 3.5° W`
*   **Resolution:** `0.05°` (~5 km spatial grid)
*   **Grid Dimensions:** $60 \times 70$ grid points (4,200 total cells)
*   **Simulation Period:** January 1, 2015 — December 31, 2020 (6-year study period matching Nie et al., 2022).

---

## 2. Scientific Objective

The simulation aims to address key research questions for Q1 publications in hydrology and agriculture:
1.  **Hydrology (Paper 1):** *Can joint soil moisture and LAI assimilation improve streamflow prediction, AET estimation, and root-zone soil moisture representation?*
2.  **Agriculture (Paper 2):** *Does assimilation reduce irrigation water allocation uncertainties and crop stress detection times under severe droughts?*

---

## 3. Data Download Instructions

We have provided three python download scripts in `scripts/download/` to query NASA's Common Metadata Repository (CMR) and download the datasets using your Earthdata credentials:
1.  **Meteorological Forcing (MERRA-2):** `scripts/download/download_merra2.py`
2.  **Soil Moisture Observations (SMAP):** `scripts/download/download_smap.py`
3.  **Leaf Area Index (MODIS LAI):** `scripts/download/download_modis_lai.py`

### Downloading using SLURM:
To submit the downloading process to the Toubkal cluster:
```bash
sbatch scripts/jobs/job_download_data.sh
```
*Note: The download scripts have been configured for the target study period (2015-01-01 to 2020-12-31).*

---

## 4. Parameter Processing (LDT)

We have configured `configs/ldt.config.sebou` with the expanded Sebou basin coordinates.
To process the elevation (DEM), soil textures, and land cover types:
```bash
sbatch scripts/jobs/job_1_ldt_sebou.sh
```

### Status: Completed
This step was successfully run on Toubkal and generated the central parameter file:
*   `data/lis_input.d01_sebou.nc`

Visualizations of the domain parameters are saved under `postproc/figures/` and can be viewed directly:
- **Topography Map:** [sebou_topography.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_topography.png)
- **Land Cover Map (MODIS IGBP):** [sebou_landcover.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_landcover.png)
- **Soil Texture Map (STATSGO):** [sebou_soil_texture.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/postproc/figures/sebou_soil_texture.png)

---

## 5. Model and Assimilation Configurations

The model config file `configs/lis.config.da_joint` is configured for joint EnKF assimilation:
*   **Ensemble Size:** 20 members (`Number of ensembles per tile: 20`)
*   **Dynamic Vegetation:** Enabled (`Noah-MP.3.6 dynamic vegetation option: 2`), allowing LIS to simulate prognostic phenology and calculate dynamic LAI.
*   **Data Assimilation Instances:** 2 instances:
    *   *Instance 1:* SMAP L3 Soil Moisture (`SMAP(NASA) soil moisture`)
    *   *Instance 2:* MODIS LAI (`MODIS LAI`, tile `h17v05`)
*   **Perturbation Attributes:** Configured to perturb precipitation/radiation forcing fields and model state variables (soil layers and Leaf Area Index) using the GMAO scheme. Perturbation parameters are defined in:
    *   `data/pert_package/modis_lai_attribs.txt`
    *   `data/pert_package/modis_lai_pertattribs.txt`
    *   `data/pert_package/noahmp_lai_attribs.txt`
    *   `data/pert_package/noahmp_lai_pertattribs.txt`

---

## 6. Verification & Validation Strategy

To publish in Q1 journals, you will validate the outputs (`experiments/DA_joint/`) against independent datasets:

### Hydrology Focus
*   **River Discharge:** Route LIS runoff outputs using the built-in **HYMAP** routing module and compare simulated daily/monthly streamflow against gauge records from the **Sebou Basin Agency (ABHS)**.
*   **Evapotranspiration (ET):** Compare simulated actual evapotranspiration against **FAO WaPOR** (250 m) or **GLEAM v3** products.
*   **Terrestrial Water Storage:** Validate basin-scale water changes against monthly **GRACE/GRACE-FO** anomalies.

### Agriculture Focus
*   **Irrigation Volumes:** Enable the Noah-MP sprinkler irrigation module and compare simulated seasonal water applications against ABHS regional water withdrawal estimates.
*   **Crop Productivity:** Correlate simulated GPP (Gross Primary Productivity) anomalies during the growing season with provincial wheat/barley crop yield statistics from the **Ministry of Agriculture of Morocco**.

### Evaluation Tooling
A custom Python visualization module (`scripts/plot_da_comparison.py`) has been provided to automatically parse the LIS NetCDF outputs across the four experiments (OPL, DA SMAP, DA LAI, DA Joint).
*   **Time Series:** Computes and plots the daily basin-averaged response of key hydrological variables (SSM, RZSM, Evapotranspiration, Runoff, LAI).
*   **Spatial Maps:** Generates detailed `Δ DA Joint - OPL` difference maps to visually inspect the exact spatial impact of the assimilated satellite retrievals.
*   **Note on LAI:** LAI plotting requires the `LAI` parameter in `configs/MODEL_OUTPUT_LIST.TBL` to be enabled (set to `1`) prior to running the simulations.

---

## 7. Pre-Production Workflow (2015-2020)

Before running the final 5-year Data Assimilation experiments, the following sequence of scripts must be executed to prepare the forcings and initialize the model states correctly (Spin-up).

1.  **Download Forcing:** Run `sbatch scripts/jobs/job_4a_download_merra2.sh` to download the remaining MERRA-2 data for 2015-2020.
2.  **Spin-up:** Run `sbatch scripts/jobs/job_4c_lis_spinup.sh` to execute an Open-Loop simulation for the 5-year period. This equilibrates the deep soil moisture and groundwater states. The `lis.config.spinup_sebou` is configured to save a restart file (`LIS_RST_NOAHMP36...`) at the end of the run.
3.  **CDF Matching (SMAP):** Run `sbatch scripts/jobs/job_4b_ldt_cdf.sh`. *(Note: You must first configure `ldt.config.cdf` to point to the output history of the Spin-up run. This computes the bias correction scaling factors for SMAP).*
4.  **Production DA Initialization:** Once the Spin-up is complete, modify your Data Assimilation configs (`lis.config.da_*`) as follows:
    *   Change `Start mode: coldstart` to `Start mode: restart`
    *   Set `Noah-MP.3.6 restart file:` to point to the file generated in step 2.

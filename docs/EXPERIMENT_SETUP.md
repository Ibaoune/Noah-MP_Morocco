# Sebou Basin Experiment Setup Guide

This document describes the detailed scientific setup, datasets, and configuration variables for running a joint data assimilation experiment (SMAP Soil Moisture + MODIS LAI) using the Noah-MP land surface model in NASA LIS over the expanded upstream Sebou Basin, Morocco.

---

## 1. Domain Configuration

The domain is expanded to cover the entire upstream Sebou River basin feeding the reservoir, as well as adjacent agricultural perimeters in the Saïss plain:
*   **Bounding Box coordinates:**
    *   South-West Corner: `33.0° N, 7.0° W`
    *   North-East Corner: `35.0° N, 4.0° W`
*   **Resolution:** `0.01°` (~1 km spatial grid)
*   **Grid Dimensions:** $200 \times 300$ grid points (~60,000 active cells)
*   **Simulation Period:** January 1, 2015 — December 31, 2025 (10-year multi-year analysis).

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
*Note: Before submitting, open the download scripts and verify the `START_DATE` and `END_DATE` configurations to match your desired target period.*

---

## 4. Parameter Processing (LDT)

We have configured `configs/ldt.config.sebou` with the expanded Sebou basin coordinates.
To process the elevation (DEM), soil textures, and land cover types:
```bash
sbatch scripts/jobs/job_1_ldt_sebou.sh
```
This job generates the central parameter file:
*   `data/lis_input.d01_sebou.nc`

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

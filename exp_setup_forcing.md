# Experimental Setup: Meteorological Forcing and Static Parameters

**Author:** M. El Aabaribaoune (@um6p)


This document details the configuration of meteorological forcings, static land surface parameters, and model configuration for the LIS/Noah-MP simulations over the Sebou-Saïss basin, strictly following the methodology established by Nie et al. (2022) and Ahmad et al. (2024).

The simulations have been successfully upgraded to utilize **Noah-MP 4.0.1** and are configured to support the **HyMAP streamflow routing** module.

## 1. Meteorological Forcing Configuration

The simulations are driven by a combination of two surface meteorology datasets, blended using an overlay method within the Land Information System (LIS):

*   **Precipitation (Primary Forcing):** Provided by the Integrated Multi-satellitE Retrievals for Global Precipitation Measurement (IMERG) Final Run V07 dataset.
*   **Other Meteorological Fields:** Provided by the National Oceanic and Atmospheric Administration (NOAA) Global Data Assimilation System (GDAS) FNL dataset (0.25° resolution). This dataset supplies the 2m air temperature, 2m specific humidity, 10m wind speed, surface pressure, and downward shortwave and longwave radiation.

### 1.1. Topographical Corrections (Lapse Rate)

To account for the coarse resolution of the GDAS dataset (~25 km) over the highly variable terrain of the Sebou basin, topographic corrections are dynamically applied to the input meteorology during the LIS simulation. 

Specifically, a **lapse-rate** correction adjusts the GDAS 2m air temperature and surface pressure based on the elevation difference between:
1.  The coarse "native" elevation of the GDAS grid cell.
2.  The high-resolution (0.01°) true terrain elevation of the specific LIS model sub-grid.

To facilitate this calculation, the LIS `lis.config` requires the native GDAS elevation map. 

**LIS Configuration File Updates:**
```text
Topographic correction method (met forcing):  "lapse-rate" "none"

#--------------------------------FORCINGS----------------------------------
GDAS forcing directory:   ./data/forcing/GDAS/
GDAS T574 elevation map:  ./data/forcing/GDAS/global_orography.t574.grb
IMERG forcing directory:  ./data/forcing/IMERG/raw/
...
```

*Note: A script `scripts/download_gdas_orography.sh` has been provided to download the required `global_orography.t574.grb` file.*

---

## 2. Static Land Surface Parameters

While forcing datasets provide the dynamic weather inputs, static land surface parameters define the physical characteristics of the land surface domain. LIS utilizes the Land Information System Data Toolkit (LDT) to process these raw global parameter datasets and resample them onto the target 0.01° grid.

The following parameter datasets are used to define the Sebou domain:

*   **Land Cover Classification (MODIS-IGBP):** The Moderate Resolution Imaging Spectroradiometer International Geosphere Biosphere Program (MODIS-IGBP) dataset provides the vegetation type (e.g., cropland, forest) at 1 km resolution. This dictates physiological parameters like stomatal resistance and root depth.
*   **Soil Properties (ISRIC):** The International Soil Reference and Information Centre (ISRIC) dataset provides soil texture mapping (e.g., sand and clay fractions).
*   **Elevation and Topography (MERIT DEM / GTOPO30):** Shuttle Radar Topography Mission (SRTM) or GTOPO30 elevation data provides the base topography. Additionally, high-resolution MERIT DEM data has been downloaded for the domain to support HyMAP hydrography parameter generation.
*   **Noah-MP 4.0.1 Parameters:** The legacy 3.6 parameter tables have been replaced with the official Noah-MP 4.0.1 parameter tables (`SOILPARM.TBL`, `GENPARM.TBL`, `MPTABLE.TBL`) downloaded from the NASA NCCS portal to ensure stable initialization.

### 2.1. Parameter Preprocessing (LDT)

Before any simulations (Spin-up, Open-Loop, or Data Assimilation) can be run, LDT processes the MODIS, ISRIC, and Elevation datasets. LDT interpolates these varied datasets using specific spatial transform methods (e.g., bilinear interpolation, tile, or mode) onto the exact 0.01° spatial resolution required by the model. 

The resulting processed parameters are saved into a single NetCDF file (`lis_input.d01_sebou.nc`), which serves as the static domain foundation for all subsequent LIS runs.

```text
# Excerpt from lis.config
LIS domain and parameter data file:     ./data/lis_input.d01_sebou.nc
Landmask data source:                   LDT
Landcover data source:                  LDT
Soil texture data source:               LDT
Elevation data source:                  LDT
...
```

## Summary for Configuration Deployment

When transitioning from the initialization/spin-up state to the production configurations (Open-Loop (OL) and Data Assimilation (DA)):

1.  **Ensure Consistency:** Verify that `lis.config.opl_sebou` and `lis.config.da_sebou` are using `GDAS` and `GPM IMERG` as the `Met forcing sources`.
2.  **Enable Lapse Rate:** Ensure the `lapse-rate` setting and the `GDAS T574 elevation map` are defined in all target configuration files to ensure the entire experiment perfectly replicates the methodology.
3.  **Noah-MP 4.0.1 Options:** Ensure all LIS configuration files utilize the 4.0.1 parameter prefixes and correct parameter table paths (`data/land_params/noahmp401_parms/`).
4.  **HyMAP Routing:** HyMAP is currently set to `"none"` in the config files to facilitate standalone DA testing. It can be re-enabled (`"HYMAP router"`) once the `.bin` routing parameters are generated from the MERIT DEM.

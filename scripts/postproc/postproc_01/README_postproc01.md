# Documentation for Noah-MP SMAP DA Evaluation Framework

This directory (`/scripts/postproc/postproc_01`) contains the analytical scripts to generate a set of 14 scientific figures evaluating the impact of Soil Moisture Active Passive (SMAP) Data Assimilation (DA) on the Noah-MP land surface model over the Sebou basin.

Below is the detailed description of each figure, including its scientific objective, the required datasets, their sources, and their **current availability** in the workspace.

---

## Figure 1: Study Domain and Land Cover
- **Objective / Message**: Contextualize the physiographic and hydroclimatic characteristics of the Sebou basin.
- **Data Used**:
  - **Relief**: SRTM DEM 30m (Source: NASA, Static) - *Assumed Available (LIS Input)*
  - **Land Cover**: MODIS IGBP (Source: NASA, Static) - *Assumed Available (LIS Input)*
  - **Basin & River Network**: HydroSHEDS / MERIT (Source: WWF / Yamazaki et al., Static) - *Assumed Available*
  - **In Situ Stations**: GPS Coordinates (Source: Local Agencies, Static) - *Assumed Available*
- **Status**: Ready.

## Figure 2: Conceptual Modeling Framework
- **Objective / Message**: Clearly describe the experimental protocol (Forcings -> LIS-Noah-MP -> OL vs DA -> HyMAP).
- **Data Used**: None (Schematic generation using Python `graphviz` or `matplotlib` patches).
- **Status**: Ready.

## Figure 3: Impact of Assimilation on Soil Moisture
- **Objective / Message**: Identify corrections brought by DA according to seasons (winter vs summer).
- **Data Used**:
  - **Noah-MP Output**: Soil moisture layer 1 (0-5cm) from OL and DA. (Temporal Freq: Daily/3-Hourly, Source: Local LIS Simulations).
- **Status**: Partially Ready. The script is functional using the `3days` test dataset (`experiments/3days/`), but full seasonal analysis requires the multi-year spin-up/assimilation runs to be completed.

## Figure 4: Impact on Total Runoff and Link with Irrigation
- **Objective / Message**: Demonstrate if assimilation indirectly captures the effect of irrigation and modifies the runoff.
- **Data Used**:
  - **Noah-MP Output**: Total Runoff (Qs + Qsb) from OL and DA. (Temporal Freq: Daily/3-Hourly, Source: Local Simulations).
  - **Irrigation Map**: Global Map of Irrigation Areas (GMIA) v5. (Temporal Freq: Static, Source: FAO).
- **Status**: Ready. GMIA data found at `/data/land_params/GMIA/gmia_v5_aei_pct.asc`.

## Figure 5: Runoff Decomposition
- **Objective / Message**: Determine which hydrological component (surface runoff vs baseflow) is most sensitive to assimilation.
- **Data Used**:
  - **Noah-MP Output**: Surface runoff (`Qs`), Baseflow (`Qsb`), Soil Moisture from OL and DA.
  - **Forcing**: IMERG Precipitation.
- **Status**: Partially Ready (Requires full simulation for meaningful correlation).

## Figures 6 to 9: Multi-Model Intercomparison (GLDAS)
- **Objective / Message**: Position the local LIS simulation results relative to global reference models (GLDAS NOAH, VIC, CLSM).
- **Data Used**:
  - **Noah-MP Output**: Soil Moisture, Runoff, Evapotranspiration.
  - **GLDAS Products**: GLDAS_NOAH025_3H v2.1, GLDAS_VIC10_3H v2.1, GLDAS_CLSM10_3H v2.1, GLDAS_CLSM025_DA1_D v2.2. (Temporal Freq: 3-Hourly/Daily, Source: GES DISC).
- **Status**: **MISSING**. GLDAS files are not yet downloaded in the `/data` directory. The scripts (`fig06_09_gldas_intercomparison.py`) are provided as skeletons that will process the files once they are downloaded.

## Figures 10 to 12: Validation of Routed Streamflow
- **Objective / Message**: Quantify the improvement brought by DA on streamflow dynamics (hydrographs, KGE, NSE).
- **Data Used**:
  - **HyMAP Output**: Routed discharge from OL and DA. (Temporal Freq: Daily, Source: Local HyMAP offline runs).
  - **In Situ Observations**: Gauging station discharge. (Temporal Freq: Daily, Source: Local Agencies).
- **Status**: **MISSING**. Both HyMAP routing outputs and in-situ streamflow observations are not yet available for the `3days` test. The scripts are provided as skeletons.

## Figures 13 and 14: Spatial Analysis of the Impact of Assimilation
- **Objective / Message**: Identify factors controlling the hydrological response to DA (basin size, precipitation, irrigation).
- **Data Used**:
  - **HyMAP / Noah-MP Output**: Relative streamflow/runoff changes.
  - **IMERG Precipitation**: Total precipitation.
  - **GMIA Irrigation**: Irrigation percentage.
- **Status**: **MISSING**. Depends on routed discharge (HyMAP), which is not yet available. Scripts provided as skeletons.

## Summary Table

| Figure | message | data used from simulation (variables) if any | data used from observation (if any) |
|---|---|---|---|
| Figure 1 | Contextualize the physiographic and hydroclimatic characteristics of the Sebou basin. | None | Relief (SRTM DEM 30m), Land Cover (MODIS IGBP), Basin & River Network, In Situ Stations |
| Figure 2 | Clearly describe the experimental protocol (Forcings -> LIS-Noah-MP -> OL vs DA -> HyMAP). | None | None |
| Figure 3 | Identify corrections brought by DA according to seasons (winter vs summer). | Soil moisture layer 1 (0-5cm) from OL and DA | None |
| Figure 4 | Demonstrate if assimilation indirectly captures the effect of irrigation and modifies the runoff. | Total Runoff (Qs + Qsb) from OL and DA | Irrigation Map (FAO GMIA v5) |
| Figure 5 | Determine which hydrological component (surface runoff vs baseflow) is most sensitive to assimilation. | Surface runoff (Qs), Baseflow (Qsb), Soil Moisture from OL and DA | IMERG Precipitation |
| Figures 6-9 | Position the local LIS simulation results relative to global reference models. | Soil Moisture, Runoff, Evapotranspiration | GLDAS Products (NOAH, VIC, CLSM) |
| Figures 10-12 | Quantify the improvement brought by DA on streamflow dynamics (hydrographs, KGE, NSE). | Routed discharge from OL and DA (HyMAP) | Gauging station discharge (In Situ) |
| Figures 13-14 | Identify factors controlling the hydrological response to DA (basin size, precipitation, irrigation). | Relative streamflow/runoff changes (HyMAP / Noah-MP) | IMERG Precipitation, GMIA Irrigation |

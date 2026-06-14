# Documentation for Noah-MP SSM-DA Evaluation Framework (postproc_02)

This directory (`/scripts/postproc/postproc_02`) contains the analytical scripts to generate a set of scientific figures and statistics evaluating the impact of Soil Moisture Data Assimilation (SSM-DA) on the Noah-MP land surface model over the Sebou-Saïss basin, focusing on fluxes, vegetation dynamics, and droughts.

Below is the detailed description of each figure, its scientific objective, and the required datasets and their **current availability**.

---

## Figure 1: Spatial Context of the Study Area
- **Objective**: Establish the spatial context by identifying regions where vegetation-soil-irrigation interactions are likely to influence water balances.
- **Data Used**:
  - **Land Cover**: MODIS MCD12Q1 (IGBP, 1km) - *Assumed Available (LIS Input)*
  - **Irrigation Intensity**: FAO GMIA (or GRIPC/GIAM) - *Available*
- **Status**: Ready for the 3-day test layout, though maps are static.

## Figure 2: Spatial Impact of DA on Surface Fluxes
- **Objective**: Map differences ($\Delta$ and $\Delta$ Anomaly) between SSM-DA and OL for E, T, ET, GPP, and NPP.
- **Data Used**:
  - **Noah-MP Output**: Evap_tavg, TVeg_tavg, GPP_tavg, NPP_tavg from OL and DA.
  - **Validation**: FAO WaPOR (ET, E, T, NPP) and FLUXSAT (GPP).
- **Status**: **MISSING VALIDATION DATA**. WaPOR and FLUXSAT need to be downloaded to `/data/observations/`. The script is a skeleton.

## Figure 3: Statistical Evaluation by Ecosystem Type
- **Objective**: Identify ecosystems where assimilation significantly improves or degrades model performance using correlation (R) boxplots.
- **Data Used**:
  - **Noah-MP Output**: E, T, ET, NPP, GPP.
  - **Land Cover**: MODIS MCD12Q1.
  - **Validation**: FAO WaPOR, FLUXSAT.
- **Status**: **MISSING VALIDATION DATA**. Script is a skeleton.

## Figure 4: Simulated Vegetation Dynamics
- **Objective**: Compare monthly LAI time series (OL vs SSM-DA) to assess phenology and drought response improvements.
- **Data Used**:
  - **Noah-MP Output**: LAI_tavg.
- **Status**: Ready. Can run on LIS outputs (though requires longer runs than 3 days for meaningful seasonal cycles).

## Figure 5: Drought Categorization
- **Objective**: Quantify the effect of assimilation on spatial drought detection.
- **Data Used**:
  - **Noah-MP Output**: Root zone soil moisture (SoilMoist_tavg for layers).
- **Status**: Ready. Computes percentiles based on OL climatology. Requires multi-year simulations to establish robust climatologies.

## Figure 6: Spatial Response to an Extreme Event
- **Objective**: Evaluate the capability of SSM-DA to reproduce spatial impacts of water stress on vegetation during a major drought.
- **Data Used**:
  - **Noah-MP Output**: LAI_tavg anomalies.
  - **Validation**: MODIS LAI MCD15A2H v6.
- **Status**: **PARTIALLY READY**. MODIS LAI is available, but detecting a major drought event requires multi-year LIS simulations.

## Supplementary Statistical Analysis
- **Objective**: Comprehensive statistical validation (R, Anomaly R, Bias, RMSE, ubRMSE, NSE, KGE) for SM, ET, T, E, GPP, NPP, LAI.
- **Data Used**: All aforementioned LIS outputs and validation datasets.
- **Status**: **MISSING VALIDATION DATA**. Script is a skeleton.

---

## Summary Table

| Figure | Message | Data used from simulation (variables) if any | Data used from observation (if any) |
| --- | --- | --- | --- |
| Figure 1 | Establish spatial context (vegetation-soil-irrigation) | None | MODIS MCD12Q1 (Land Cover), FAO GMIA/GRIPC (Irrigation) |
| Figure 2 | Map spatial impact of DA on surface fluxes ($\Delta$ and $\Delta$ Anomaly) | Evap_tavg, TVeg_tavg, GPP_tavg, NPP_tavg | FAO WaPOR (ET, E, T, NPP), FLUXSAT (GPP) |
| Figure 3 | Identify ecosystems where DA improves/degrades performance | E, T, ET, NPP, GPP | MODIS MCD12Q1, FAO WaPOR, FLUXSAT |
| Figure 4 | Compare LAI dynamics to assess phenology and drought response | LAI_tavg | MODIS LAI MCD15A2H v6 |
| Figure 5 | Quantify effect of assimilation on spatial drought detection | Root zone soil moisture (SoilMoist_tavg) | None |
| Figure 6 | Evaluate spatial vegetation response to a major drought event | LAI_tavg anomalies | MODIS LAI MCD15A2H v6 |
| Supp Stats | Comprehensive statistical validation (R, RMSE, KGE, NSE, etc.) | SM, ET, T, E, GPP, NPP, LAI | All validation datasets |

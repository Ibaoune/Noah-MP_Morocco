# Drought Diagnostics Methodology (V0)

## A. Scientific objective
The objective is to evaluate how SMAP assimilation (DA-NoCDF and DA-CDF) modifies the drought diagnostics derived from hydrological states, specifically Surface Soil Moisture (SSM) and Root-Zone Soil Moisture (RZSM).

## B. Relation to Nie et al. (2022)
Nie et al. (2022) established a drought monitoring framework for the MENA region using Noah-MP within LIS. They analyzed the spatial and temporal evolution of drought area percentages during the SMAP era based on model-derived percentiles. This methodology adapts their framework to assess the diagnostic sensitivity of these metrics to different SMAP data assimilation techniques.

## C. Input data
- Monthly pixel-level datasets covering 2016–2020.
- State variables: SSM and RZSM.
- Experiments: OPL, DA-NoCDF, DA-CDF.
- Ancillary data: Static land cover.

## D. Reference strategy

### opl_pooled_2016_2020 (Main Mode)
- OPL 2016–2020 by pixel as common reference.
- Ensures comparability among OPL, DA-NoCDF, and DA-CDF.
- Does not remove the seasonal cycle.
- Supports relative low-soil-moisture diagnostics, not climatological drought assessment.

### opl_calendar_month_2016_2020
- Would remove the seasonal cycle.
- But only 5 samples per calendar month and pixel.
- Too short for stable percentile thresholds.
- Not recommended as the main result.

### opl_calendar_month_long_reference
- Preferred if a longer OPL reference (e.g., 2005–2020) is available.
- Would be the most defensible option for drought-like percentile classes.
- Currently blocked pending processing of raw daily SPINUP outputs.

**Conclusion:** The main reference mode used for this diagnostic is `opl_pooled_2016_2020` because it provides 60 samples per pixel, which is the minimum required for extracting stable relative shifts in D1/D2 without requiring full reprocessing of historical spin-up runs.

## E. Drought classes
Percentile ranks are converted into hierarchical drought classes:
- **D0 (Abnormally Dry):** percentile <= 30
- **D1 (Moderate):** percentile <= 20
- **D2 (Severe):** percentile <= 10
- **D3 (Extreme):** percentile <= 5
- **D4 (Exceptional):** percentile <= 2

## F. Drought area percentage
The temporal evolution of drought is quantified by computing the percentage of the domain area (number of pixels) experiencing drought (e.g., D1 or worse) for each month and comparing the OPL, DA-NoCDF, and DA-CDF experiments.

## G. Drought frequency maps
The spatial frequency of drought conditions (percentage of months a pixel is classified as D1 or worse) is mapped to illustrate where assimilation most strongly shifts the drought classification.

## H. Transition analysis
To assess the DA-induced shift in drought classification, a discrete transition matrix is computed comparing the OPL reference to the DA states month-by-month. Transitions are classified heuristically (e.g., alleviated, intensified, introduced_drought, removed_drought).

## I. Land-cover stratification
When land cover data is available, the mean drought area percentage is stratified to identify vegetation types that exhibit high diagnostic sensitivity to the assimilation updates.

## J. Limitations
- **SMAP-only assimilation:** Vegetation states are not directly constrained (no LAI assimilation yet).
- **Missing human components:** There is no explicit representation of irrigation or reservoir management in the current Noah-MP setup.
- **No routed streamflow:** The analysis is restricted to grid-based fluxes and states, as HyMAP routed streamflow is not yet integrated.
- **Short reference period:** The 2016–2020 window is short for computing true climatological percentiles.
- **Diagnostic nature:** The drought classes are relative, model-derived diagnostics. Changes should be viewed as diagnostic sensitivity and do not necessarily represent a DA-induced shift in true drought classification.


## Terminology and Metric Definitions
- **Drought Area Percent (`drought_area_percent`)**: The monthly fraction of valid grid cells in the domain that fall below the specific diagnostic threshold (e.g., D1).
- **Mean Drought Area Percent (`mean_drought_area_percent`)**: The temporal mean of these monthly spatial fractions over the 2016-2020 period.
- **Transition Percentages**: The percentage of evaluated pixel-month cases that transition between categorical states relative to the total number of valid pixel-months.


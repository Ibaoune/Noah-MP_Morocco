# Planned Drought Diagnostics

## A. Objective
To evaluate how SMAP assimilation modifies drought diagnostics derived from Soil Moisture (SSM/RZSM) and potentially Evapotranspiration (ET).

## B. Link with Nie et al. (2022)
Nie et al. (2022) use Noah-MP/LIS for drought monitoring across Morocco/MENA, analyzing the percentage of area under drought based on percentile categories during the SMAP period. This planned extension adapts that methodology to our OPL / DA-NoCDF / DA-CDF experiments over the 2016–2020 period.

## C. Inputs
- Monthly SSM (OPL / DA-NoCDF / DA-CDF)
- Monthly RZSM (OPL / DA-NoCDF / DA-CDF)
- ET (Optional)
- Static land cover
- Basin/domain mask
- Climatology or reference distribution

## D. Important climatology issue
We must verify if the 2016–2020 period is sufficient to compute a robust climatology. If a longer OPL baseline is available, it should be utilized. Otherwise, 2016–2020 will only serve as a relative diagnostic sensitivity tool, without claiming to represent a robust long-term climatological drought index.

## E. Drought metrics to compute
- Monthly percentile rank of SSM
- Monthly percentile rank of RZSM
- **Drought classes:**
  - D0: percentile < 30
  - D1: percentile < 20
  - D2: percentile < 10
  - D3: percentile < 5
  - D4: percentile < 2
- Drought area percentage by month
- Drought frequency maps
- Drought class transition maps: OPL → DA-NoCDF and OPL → DA-CDF
- Seasonal drought-area time series
- Land-cover stratified drought-area percentage

## F. Figures to produce later
- `manuscript_drought_frequency_SSM_OPL_DA_NoCDF_DA_CDF_2016_2020.png`
- `manuscript_drought_frequency_RZSM_OPL_DA_NoCDF_DA_CDF_2016_2020.png`
- `manuscript_drought_area_timeseries_SSM_2016_2020.png`
- `manuscript_drought_area_timeseries_RZSM_2016_2020.png`
- `manuscript_drought_transition_OPL_to_DA_NoCDF_2016_2020.png`
- `manuscript_drought_transition_OPL_to_DA_CDF_2016_2020.png`
- `manuscript_drought_by_landcover_2016_2020.png`

## G. Tables to produce later
- `drought_area_monthly_summary_2016_2020.csv`
- `drought_frequency_summary_2016_2020.csv`
- `drought_transition_summary_2016_2020.csv`
- `drought_by_landcover_summary_2016_2020.csv`

## H. Cautions
- SMAP-only assimilation does not constrain vegetation directly (unlike LAI assimilation).
- 2016–2020 may be too short to establish robust climatological drought percentiles.
- Differences between CDF and NoCDF must be strictly interpreted as diagnostic sensitivity, not a definitive "true" drought correction.
- Drought diagnostics are model-derived and do not constitute direct validation of meteorological drought truth.
- There is currently no explicit representation of irrigation or reservoir management.

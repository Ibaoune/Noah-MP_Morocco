# Multi-experiment Hydrological Diagnostics — `opl_multiple_da`
**Author:** M. EL Aabaribaoune (@um6p)

This directory contains the full set of publication-ready diagnostic figures produced for the comparative analysis of multiple SMAP data assimilation configurations against the open-loop (OPL) baseline for the year **2016**.

Experiments compared: **OPL** (no assimilation), **DA-noCDF-noIRR** (EnKF without CDF-matching), and **DA-CDF-noIRR** (EnKF with CDF-matching).

Each figure follows a consistent naming scheme: `NN_topic_experiments_year.png`.

---

## 1. Assimilation Diagnostics — `assimilation/`

These figures evaluate the internal behaviour of the EnKF assimilation system. They focus on the quality of the observation-model fusion and do not yet reflect any impact on simulated hydrological variables.

| # | Filename | Description |
|---|----------|-------------|
| 01 | `01_assimilated_observations_coverage_2016.png` | Spatial map of total assimilated SMAP observations (obs count per cell). Identifies the assimilation footprint and coverage gaps (e.g., dense vegetation, frozen soils). |
| 02 | `02_monthly_assimilated_observations_2016.png` | Domain-integrated monthly count of assimilated observations. Highlights seasonal variations in satellite data availability. |
| 03 | `03_mean_innovation_nocdf_vs_cdf_2016.png` | Spatial comparison of time-averaged innovations $y - H(x^f)$ between noCDF and CDF experiments. A positive value indicates SMAP is wetter than the model prior. |
| 04 | `04_mean_increment_nocdf_vs_cdf_2016.png` | Spatial comparison of mean soil moisture increments $x^a - x^f$ between experiments. Shows the net correction systematically applied to the model state. |
| 05 | `05_increment_histogram_nocdf_vs_cdf_2016.png` | Distribution of all daily increment values across the domain. Characterises the symmetry (or systematic bias) of the EnKF updates. |
| 06 | `06_monthly_increment_boxplots_nocdf_vs_cdf_2016.png` | Monthly box plots of increments per experiment. Reveals seasonal patterns in the model correction behaviour. |
| 07 | `07_seasonal_increment_wet_dry_nocdf_vs_cdf_2016.png` | Spatial maps of mean increments during wet (Nov–Apr) and dry (May–Oct) seasons. Diagnoses seasonal biases in the land surface model. |
| 08 | `08_prior_ensemble_spread_nocdf_vs_cdf_2016.png` | Spatial map of forecast ensemble spread (prior uncertainty in observation space). Reflects the initial ensemble uncertainty before the analysis step. |
| 09 | `09_posterior_ensemble_spread_nocdf_vs_cdf_2016.png` | Spatial map of posterior ensemble spread (analysis uncertainty after the assimilation update). |
| 10 | `10_spread_reduction_nocdf_vs_cdf_2016.png` | Relative spread reduction between prior and posterior. A positive value indicates the observations added information to the ensemble. |
| 11 | `11_normalized_innovation_nocdf_vs_cdf_2016.png` | Normalised innovations (innovation divided by innovation standard deviation). Should be close to a standard normal distribution if the ensemble is consistent. |
| 12 | `12_innovation_increment_scatter_nocdf_vs_cdf_2016.png` | Scatter plot between innovations and increments. A positive correlation confirms that the DA system physically responds to the observed signal. |

---

## 2. Soil Moisture — `soil_moisture/`

These figures quantify the direct impact of SMAP assimilation on modelled soil moisture at different depths.

| # | Filename | Description |
|---|----------|-------------|
| 13 | `13_surface_soil_moisture_mean_opl_nocdf_cdf_2016.png` | Annual mean surface soil moisture (Layer 1, 0–10 cm) maps for OPL, DA-noCDF, and DA-CDF. |
| 14 | `14_surface_soil_moisture_differences_nocdf_cdf_2016.png` | Spatial difference maps (DA − OPL) for surface soil moisture. Red/blue indicates drying/wetting induced by assimilation. |
| 15 | `15_surface_soil_moisture_timeseries_2016.png` | Domain-averaged daily surface soil moisture time series for all experiments. |
| 16 | `16_soil_moisture_layer_timeseries_2016.png` | Daily time series across all four soil layers (0–10, 10–40, 40–100, 100–200 cm) for all experiments. |
| 17 | `17_soil_moisture_layer_differences_2016.png` | Seasonal mean differences by soil layer. Shows the vertical propagation of the surface DA signal through the soil column. |
| 18 | `18_rootzone_soil_moisture_mean_opl_nocdf_cdf_2016.png` | Annual mean root-zone soil moisture (0–100 cm) maps for all experiments. |
| 19 | `19_rootzone_soil_moisture_differences_2016.png` | Spatial difference maps for root-zone soil moisture. |
| 20 | `20_rootzone_soil_moisture_timeseries_2016.png` | Domain-averaged daily root-zone soil moisture time series. |
| 21 | `21_vertical_profile_sm_increment_wet_dry_2016.png` | Mean vertical profile of the increment signal across all 4 layers, split by wet and dry season. |
| 22 | `22_soil_moisture_variability_violinplots_2016.png` | Violin plots comparing the spatial distribution of soil moisture values across experiments and seasons. |

---

## 3. Surface Fluxes — `fluxes/`

These figures evaluate the propagation of the DA signal into surface energy and water balance components.

| # | Filename | Description |
|---|----------|-------------|
| 23 | `23_evapotranspiration_mean_opl_nocdf_cdf_2016.png` | Annual mean total ET (mm d⁻¹) maps for OPL, DA-noCDF, and DA-CDF. |
| 24 | `24_evapotranspiration_differences_2016.png` | Spatial DA − OPL differences in total ET. |
| 25 | `25_evapotranspiration_timeseries_2016.png` | Domain-averaged daily ET time series. |
| 26 | `26_transpiration_mean_and_differences_2016.png` | Mean maps and DA − OPL differences for plant transpiration. |
| 27 | `27_soil_evaporation_mean_and_differences_2016.png` | Mean maps and DA − OPL differences for soil evaporation. |
| 28 | `28_transpiration_fraction_t_over_et_2016.png` | Transpiration fraction (T/ET) maps. A higher T/ET indicates more vegetation-controlled water use. |
| 29 | `29_latent_heat_sensible_heat_response_2016.png` | Response of latent heat (LE) and sensible heat (H) to assimilation. Shows the Bowen ratio adjustment. |
| 30 | `30_water_energy_flux_timeseries_2016.png` | Combined time series of LE, H, and ET for all experiments. |

---

## 4. Groundwater — `groundwater/`

These figures characterise the deeper propagation of the DA signal into groundwater storage.

| # | Filename | Description |
|---|----------|-------------|
| 31 | `31_groundwater_storage_mean_opl_nocdf_cdf_2016.png` | Annual mean groundwater storage anomaly maps for all experiments. |
| 32 | `32_groundwater_storage_differences_2016.png` | Spatial DA − OPL differences in groundwater storage. |
| 33 | `33_groundwater_storage_timeseries_2016.png` | Domain-averaged daily groundwater storage time series. |
| 34 | `34_water_table_depth_response_2016.png` | Response of simulated water table depth to SMAP assimilation. |
| 35 | `35_rzsm_vs_groundwater_storage_scatter_2016.png` | Scatter between root-zone soil moisture and groundwater storage across experiments. Tests the hydraulic connectivity in the model. |

---

## 5. Runoff — `runoff/`

These figures examine how surface runoff, baseflow, and total runoff respond to the assimilation-induced changes in soil moisture.

| # | Filename | Description |
|---|----------|-------------|
| 36 | `36_total_runoff_mean_opl_nocdf_cdf_2016.png` | Annual mean total runoff maps for all experiments. |
| 37 | `37_total_runoff_differences_2016.png` | DA − OPL spatial differences in total runoff. |
| 38 | `38_surface_runoff_mean_opl_nocdf_cdf_2016.png` | Annual mean surface runoff (Hortonian + saturation excess) maps. |
| 39 | `39_surface_runoff_differences_2016.png` | DA − OPL spatial differences in surface runoff. |
| 40 | `40_baseflow_mean_opl_nocdf_cdf_2016.png` | Annual mean baseflow (subsurface drainage) maps. |
| 41 | `41_baseflow_differences_2016.png` | DA − OPL spatial differences in baseflow. |
| 42 | `42_total_runoff_timeseries_2016.png` | Domain-averaged daily total runoff time series. |
| 43 | `43_surface_runoff_timeseries_2016.png` | Domain-averaged daily surface runoff time series. |
| 44 | `44_baseflow_timeseries_2016.png` | Domain-averaged daily baseflow time series. |
| 45 | `45_baseflow_fraction_2016.png` | Baseflow fraction (Qb / Qtotal) maps and time series. |
| 46 | `46_monthly_runoff_partitioning_2016.png` | Monthly bar charts showing runoff partitioning (surface vs. base) for each experiment. |
| 47 | `47_cumulative_runoff_components_2016.png` | Cumulative runoff components (annual accumulation) for all experiments. |
| 48 | `48_delta_baseflow_vs_delta_surface_runoff_2016.png` | Scatter plot of DA − OPL baseflow change vs. surface runoff change. Tests whether DA shifts the runoff generation mechanism. |

---

## 6. Streamflow — `streamflow/`

These figures evaluate the impact of assimilation on streamflow at gauged stations, providing an indirect validation of the DA approach.

| # | Filename | Description |
|---|----------|-------------|
| 49 | `49_selected_station_daily_hydrographs_2016.png` | Daily simulated vs. observed hydrographs at selected gauging stations. |
| 50 | `50_selected_station_monthly_hydrographs_2016.png` | Monthly simulated vs. observed hydrographs. |
| 51 | `51_flow_duration_curves_selected_stations_2016.png` | Flow duration curves (FDC) for OPL and DA simulations vs. observations. |
| 52 | `52_streamflow_scatter_obs_vs_sim_2016.png` | Scatter plot of simulated vs. observed streamflow (all stations, all days). |
| 53 | `53_streamflow_skill_metrics_by_station_2016.png` | Bar charts of NSE, KGE, PBIAS per station and per experiment. |
| 54 | `54_station_map_streamflow_skill_improvement_2016.png` | Map of stations coloured by the change in NSE or KGE from OPL to DA. |
| 55 | `55_low_flow_high_flow_bias_2016.png` | Bias decomposition by flow regime (low-flow vs. high-flow events). |
| 56 | `56_cumulative_streamflow_volume_2016.png` | Cumulative annual streamflow volume at each station for all experiments. |
| 57 | `57_hydrographs_by_station_typology_2016.png` | Hydrographs grouped by station typology (e.g., snowmelt, rainfall-driven, regulated). |

---

## 7. External Validation — `validation/`

These figures compare simulated outputs against independent observational products to assess DA performance beyond the SMAP observations themselves.

| # | Filename | Description |
|---|----------|-------------|
| 58 | `58_et_validation_against_wapor_2016.png` | Comparison of simulated total ET against WaPOR remote sensing ET. |
| 59 | `59_transpiration_validation_against_wapor_2016.png` | Transpiration validation against WaPOR. |
| 60 | `60_evaporation_validation_against_wapor_2016.png` | Soil evaporation validation against WaPOR. |
| 61 | `61_soil_moisture_validation_against_ascat_esa_cci_2016.png` | Validation of surface soil moisture against ASCAT and ESA-CCI satellite products. |
| 62 | `62_gws_validation_against_grace_2016.png` | Groundwater storage anomaly validation against GRACE TWS. |
| 63 | `63_gldas_runoff_intercomparison_2016.png` | Runoff intercomparison with GLDAS as an alternative model benchmark. |
| 64 | `64_skill_improvement_maps_against_external_products_2016.png` | Spatial maps of skill improvement (DA vs. OPL) relative to WaPOR, ASCAT/ESA-CCI, and GRACE. |

---

## 8. Spatial & Stratified Analysis — `spatial_analysis/`

These figures investigate how the DA impact varies with land cover type, elevation, and sub-basin characteristics.

| # | Filename | Description |
|---|----------|-------------|
| 65 | `65_increment_by_landcover_class_2016.png` | Box plots of soil moisture increments stratified by land cover class (cropland, forest, shrubland, bare soil, etc.). |
| 66 | `66_hydrological_response_by_landcover_class_2016.png` | DA-induced changes in ET and runoff per land cover class. |
| 67 | `67_increment_by_elevation_band_2016.png` | Mean increments stratified by elevation bands (e.g., <500 m, 500–1000 m, >1000 m). |
| 68 | `68_runoff_response_by_elevation_band_2016.png` | Runoff changes induced by assimilation, stratified by elevation. |
| 69 | `69_response_by_cultivated_and_non_cultivated_areas_2016.png` | Contrast of hydrological response between cultivated and non-cultivated areas. |
| 70 | `70_subbasin_average_hydrological_response_2016.png` | Catchment-aggregated response maps showing DA impact per sub-basin. |

---

## Notes

- **Experiment labels**:
  - `OPL` = Open-loop (no data assimilation baseline)
  - `DA-noCDF` = EnKF with SMAP direct insertion (no CDF-matching bias correction)
  - `DA-CDF` = EnKF with SMAP after CDF-matching rescaling
- **Year**: All figures cover the January–December 2016 period.
- **Grid**: Morocco domain, 0.01° resolution.
- **Figure format**: PNG, 300 DPI, `bbox_inches=tight`.

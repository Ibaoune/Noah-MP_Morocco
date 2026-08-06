# OPL Multiple DA Module
**Author:** M. EL Aabaribaoune (@um6p)

This module compares Open Loop (OPL) against multiple Data Assimilation (DA) experiments (e.g. CDF and no-CDF).

Run via:
```bash
bash job_opl_multiple_da.sh
```

## Catalogue des Figures Générées (OPL vs DA-NoCDF vs DA-CDF pour 2016)

Voici la liste organisée des figures générées par les différents scripts de ce module, réparties par répertoire thématique.

### 1. `assimilation/`

- **01** - `01_assimilated_observations_coverage_2016.png` : Spatial coverage and frequency of assimilated SMAP observations in 2016
- **02** - `02_monthly_assimilated_observations_2016.png` : Monthly number of assimilated SMAP observations in 2016
- **03** - `03_mean_innovation_nocdf_vs_cdf_2016.png` : Mean SMAP innovation for No-CDF and CDF assimilation experiments in 2016
- **04** - `04_mean_increment_nocdf_vs_cdf_2016.png` : Mean soil moisture analysis increments for No-CDF and CDF assimilation experiments in 2016
- **05** - `05_increment_histogram_nocdf_vs_cdf_2016.png` : Distribution of soil moisture analysis increments under No-CDF and CDF assimilation
- **06** - `06_monthly_increment_boxplots_nocdf_vs_cdf_2016.png` : Monthly variability of SMAP-induced soil moisture increments under No-CDF and CDF assimilation
- **07** - `07_seasonal_increment_wet_dry_nocdf_vs_cdf_2016.png` : Wet- and dry-season soil moisture increments under No-CDF and CDF assimilation
- **08** - `08_prior_ensemble_spread_nocdf_vs_cdf_2016.png` : Prior ensemble spread for No-CDF and CDF assimilation experiments
- **09** - `09_posterior_ensemble_spread_nocdf_vs_cdf_2016.png` : Posterior ensemble spread after SMAP assimilation under No-CDF and CDF configurations
- **10** - `10_spread_reduction_nocdf_vs_cdf_2016.png` : Reduction of ensemble spread after SMAP assimilation under No-CDF and CDF configurations
- **11** - `11_normalized_innovation_nocdf_vs_cdf_2016.png` : Normalized innovation statistics for No-CDF and CDF SMAP assimilation
- **12** - `12_innovation_increment_scatter_nocdf_vs_cdf_2016.png` : Relationship between SMAP innovations and analysis increments under No-CDF and CDF assimilation

### 2. `soil_moisture/`

- **13** - `13_surface_soil_moisture_mean_opl_nocdf_cdf_2016.png` : Mean surface soil moisture in OPL, DA-NoCDF and DA-CDF experiments
- **14** - `14_surface_soil_moisture_differences_nocdf_cdf_2016.png` : Impact of No-CDF and CDF assimilation on surface soil moisture
- **15** - `15_surface_soil_moisture_timeseries_2016.png` : Basin-averaged surface soil moisture time series for OPL, DA-NoCDF and DA-CDF
- **16** - `16_soil_moisture_layer_timeseries_2016.png` : Vertical propagation of SMAP assimilation increments across Noah-MP soil layers
- **17** - `17_soil_moisture_layer_differences_2016.png` : Layer-wise soil moisture differences induced by No-CDF and CDF assimilation
- **18** - `18_rootzone_soil_moisture_mean_opl_nocdf_cdf_2016.png` : Mean root-zone soil moisture in OPL, DA-NoCDF and DA-CDF experiments
- **19** - `19_rootzone_soil_moisture_differences_2016.png` : Root-zone soil moisture response to No-CDF and CDF SMAP assimilation
- **20** - `20_rootzone_soil_moisture_timeseries_2016.png` : Basin-averaged root-zone soil moisture response to SMAP assimilation
- **21** - `21_vertical_profile_sm_increment_wet_dry_2016.png` : Seasonal vertical profile of soil moisture increments under No-CDF and CDF assimilation
- **22** - `22_soil_moisture_variability_violinplots_2016.png` : Seasonal distribution of soil moisture states in OPL, DA-NoCDF and DA-CDF experiments

### 3. `fluxes/`

- **23** - `23_evapotranspiration_mean_opl_nocdf_cdf_2016.png` : Mean evapotranspiration in OPL, DA-NoCDF and DA-CDF experiments
- **24** - `24_evapotranspiration_differences_2016.png` : Impact of No-CDF and CDF SMAP assimilation on evapotranspiration
- **25** - `25_evapotranspiration_timeseries_2016.png` : Basin-averaged evapotranspiration response to SMAP assimilation
- **26** - `26_transpiration_mean_and_differences_2016.png` : Transpiration response to No-CDF and CDF SMAP assimilation
- **27** - `27_soil_evaporation_mean_and_differences_2016.png` : Soil evaporation response to No-CDF and CDF SMAP assimilation
- **28** - `28_transpiration_fraction_t_over_et_2016.png` : Impact of SMAP assimilation on the transpiration fraction T/ET
- **29** - `29_latent_heat_sensible_heat_response_2016.png` : Energy flux response to No-CDF and CDF SMAP assimilation
- **30** - `30_water_energy_flux_timeseries_2016.png` : Basin-averaged water and energy fluxes under OPL, DA-NoCDF and DA-CDF experiments

### 4. `groundwater/`

- **31** - `31_groundwater_storage_mean_opl_nocdf_cdf_2016.png` : Mean groundwater storage in OPL, DA-NoCDF and DA-CDF experiments
- **32** - `32_groundwater_storage_differences_2016.png` : Groundwater storage response to No-CDF and CDF SMAP assimilation
- **33** - `33_groundwater_storage_timeseries_2016.png` : Basin-averaged groundwater storage response to SMAP assimilation
- **34** - `34_water_table_depth_response_2016.png` : Water table depth response to No-CDF and CDF SMAP assimilation
- **35** - `35_rzsm_vs_groundwater_storage_scatter_2016.png` : Relationship between root-zone soil moisture changes and groundwater storage response

### 5. `runoff/`

- **36** - `36_total_runoff_mean_opl_nocdf_cdf_2016.png` : Mean total runoff in OPL, DA-NoCDF and DA-CDF experiments
- **37** - `37_total_runoff_differences_2016.png` : Impact of No-CDF and CDF SMAP assimilation on total runoff
- **38** - `38_surface_runoff_mean_opl_nocdf_cdf_2016.png` : Mean surface runoff in OPL, DA-NoCDF and DA-CDF experiments
- **39** - `39_surface_runoff_differences_2016.png` : Surface runoff response to No-CDF and CDF SMAP assimilation
- **40** - `40_baseflow_mean_opl_nocdf_cdf_2016.png` : Mean baseflow in OPL, DA-NoCDF and DA-CDF experiments
- **41** - `41_baseflow_differences_2016.png` : Baseflow response to No-CDF and CDF SMAP assimilation
- **42** - `42_total_runoff_timeseries_2016.png` : Basin-averaged total runoff time series for OPL, DA-NoCDF and DA-CDF
- **43** - `43_surface_runoff_timeseries_2016.png` : Basin-averaged surface runoff time series for OPL, DA-NoCDF and DA-CDF
- **44** - `44_baseflow_timeseries_2016.png` : Basin-averaged baseflow time series for OPL, DA-NoCDF and DA-CDF
- **45** - `45_baseflow_fraction_2016.png` : Baseflow fraction response to No-CDF and CDF SMAP assimilation
- **46** - `46_monthly_runoff_partitioning_2016.png` : Monthly partitioning of total runoff into surface runoff and baseflow
- **47** - `47_cumulative_runoff_components_2016.png` : Cumulative surface runoff, baseflow and total runoff under OPL, DA-NoCDF and DA-CDF
- **48** - `48_delta_baseflow_vs_delta_surface_runoff_2016.png` : Relative sensitivity of baseflow and surface runoff to SMAP assimilation

### 6. `streamflow/`

- **49** - `49_selected_station_daily_hydrographs_2016.png` : Daily HyMAP-routed streamflow at selected gauges: observations, OPL, DA-NoCDF and DA-CDF
- **50** - `50_selected_station_monthly_hydrographs_2016.png` : Monthly HyMAP-routed streamflow at selected gauges under OPL and SMAP assimilation experiments
- **51** - `51_flow_duration_curves_selected_stations_2016.png` : Flow duration curves for observed and simulated streamflow at selected gauges
- **52** - `52_streamflow_scatter_obs_vs_sim_2016.png` : Observed versus simulated daily streamflow for OPL, DA-NoCDF and DA-CDF
- **53** - `53_streamflow_skill_metrics_by_station_2016.png` : Streamflow skill metrics by station for OPL, DA-NoCDF and DA-CDF
- **54** - `54_station_map_streamflow_skill_improvement_2016.png` : Spatial distribution of streamflow skill changes induced by SMAP assimilation
- **55** - `55_low_flow_high_flow_bias_2016.png` : Low-flow and high-flow bias diagnostics for HyMAP-routed streamflow
- **56** - `56_cumulative_streamflow_volume_2016.png` : Cumulative streamflow volume at selected gauges under OPL, DA-NoCDF and DA-CDF
- **57** - `57_hydrographs_by_station_typology_2016.png` : Streamflow response to SMAP assimilation across station typologies

### 7. `validation/`

- **58** - `58_et_validation_against_wapor_2016.png` : Evaluation of OPL, DA-NoCDF and DA-CDF evapotranspiration against WaPOR
- **59** - `59_transpiration_validation_against_wapor_2016.png` : Evaluation of simulated transpiration against WaPOR under OPL and SMAP assimilation experiments
- **60** - `60_evaporation_validation_against_wapor_2016.png` : Evaluation of simulated soil evaporation against WaPOR under OPL and SMAP assimilation experiments
- **61** - `61_soil_moisture_validation_against_ascat_esa_cci_2016.png` : Independent soil moisture evaluation against ASCAT and ESA CCI products
- **62** - `62_gws_validation_against_grace_2016.png` : Comparison of simulated groundwater storage anomalies with GRACE/GRACE-FO terrestrial water storage
- **63** - `63_gldas_runoff_intercomparison_2016.png` : Intercomparison of Noah-MP runoff components with GLDAS land surface model products
- **64** - `64_skill_improvement_maps_against_external_products_2016.png` : Spatial skill improvement of DA-NoCDF and DA-CDF against independent remote sensing products

### 8. `spatial_analysis/`

- **65** - `65_increment_by_landcover_class_2016.png` : SMAP assimilation increments stratified by land cover class
- **66** - `66_hydrological_response_by_landcover_class_2016.png` : Hydrological response to SMAP assimilation across land cover classes
- **67** - `67_increment_by_elevation_band_2016.png` : SMAP assimilation increments along the elevation gradient
- **68** - `68_runoff_response_by_elevation_band_2016.png` : Runoff and baseflow response to SMAP assimilation along the elevation gradient
- **69** - `69_response_by_cultivated_and_non_cultivated_areas_2016.png` : SMAP assimilation response over cultivated and non-cultivated areas
- **70** - `70_subbasin_average_hydrological_response_2016.png` : Sub-basin averaged hydrological response to No-CDF and CDF SMAP assimilation

### 9. `synthesis/`

- **71** - `71_summary_matrix_hydrological_impacts_2016.png` : Summary matrix of SMAP assimilation impacts across hydrological variables
- **72** - `72_cdf_vs_nocdf_decision_heatmap_2016.png` : Decision heatmap comparing No-CDF and CDF assimilation performance
- **73** - `73_water_balance_summary_opl_nocdf_cdf_2016.png` : Water balance summary for OPL, DA-NoCDF and DA-CDF experiments
- **74** - `74_hydrological_consistency_score_2016.png` : Hydrological consistency score of No-CDF and CDF SMAP assimilation
- **75** - `75_smap_assimilation_pathway_summary_2016.png` : Pathway of SMAP assimilation impacts from surface soil moisture to routed streamflow
- **76** - `76_recommended_figures_for_ahmad_pdf_2016.png` : Recommended figure set for expert feedback on the 2016 SMAP assimilation pilot

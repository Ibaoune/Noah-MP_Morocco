# Evaluating the Impact of SMAP Soil Moisture Assimilation on Hydrological Dynamics and Streamflow Routing in the Semi-Arid Sebou Basin, Morocco

## 1. Introduction
Accurate estimation of hydrological states, including soil moisture and streamflow, is imperative for water resource management, particularly in regions vulnerable to severe climate stress. The Sebou River basin in Northern Morocco, a critical agricultural hub within the Mediterranean and North African (MENA) region, is experiencing amplified water scarcity driven by recurrent droughts and intensive, unmonitored groundwater extraction for irrigation (Driouech et al., 2020; Arjdal et al., 2023). Land surface models (LSMs) serve as vital tools for monitoring these dynamics; however, they inherently suffer from atmospheric forcing errors and physical parameterization uncertainties, particularly regarding unrepresented anthropogenic water use. 

Data assimilation (DA) mitigates these deficiencies by optimally merging model predictions with satellite observations. Recent advancements have successfully utilized Earth Observation data in the region. Most notably, Nie et al. (2022) demonstrated the assimilation of Soil Moisture Active Passive (SMAP) soil moisture and MODIS Leaf Area Index (LAI) to accurately estimate land states over Northern Morocco. Building on this foundation, it is critical to evaluate how such assimilation frameworks propagate improvements to downstream hydrological processes. Following the methodologies of Ahmad et al. (2024), who investigated the influence of SMAP soil moisture assimilation on runoff and baseflow across South Asia, this study employs the NASA Land Information System (LIS) framework integrating the Noah-MP land surface model and HyMAP routing scheme. Our objective is to evaluate whether the assimilation of SMAP surface soil moisture retrievals systematically improves surface and subsurface runoff, partitioned baseflow, and hydraulically routed streamflow within the Sebou Basin.

## 2. Materials and Methods

### 2.1. Study Region
The study focuses on the upstream Sebou River basin and the Saïss plain in northern Morocco (32.5° N–35.5° N; 7.0° W–3.5° W; Table 1). The region features a strong topoclimatic gradient, transitioning from the snow-capped Middle Atlas Mountains to the semi-arid, highly cultivated Saïss plain (Jarlan et al., 2015; Nie et al., 2022). Known as Morocco’s primary agricultural hub, the basin is subject to extreme water stress. Recent climate projections highlight North Africa, and specifically Morocco, as a severe hotspot for future hydrological drying, with significant projected declines in surface water availability (Arjdal et al., 2023). This imminent climatic pressure, compounded by intense, often unmonitored groundwater extraction for irrigation (Driouech et al., 2020), underscores the critical need for improved hydrological monitoring tools in the region. 

This domain presents an optimal testbed for evaluating joint data assimilation coupled with streamflow routing. While anthropogenic water withdrawals introduce major uncertainties in baseline land surface simulations (Lawston et al., 2017; Brocca et al., 2018), the Sebou basin provides a rare and robust network of in-situ streamflow gauges managed by the Sebou Hydraulic Basin Agency (ABHS). The availability of continuous daily discharge records from key sub-catchments (e.g., Ouergha, Inaouene) allows for the rigorous evaluation of how satellite-driven updates to soil moisture and phenology propagate through the drainage network via streamflow routing schemes (Kumar et al., 2019; Ahmad et al., 2024).

**Table 1. Domain Configuration**

| Parameter | Value |
| :--- | :--- |
| Region | Upstream Sebou River basin & Saïss plain |
| Spatial Resolution | 0.05° × 0.05° |
| South-West Corner | 32.5° N, 7.0° W |
| North-East Corner | 35.5° N, 3.5° W |

### 2.2. Model Configuration
**2.2.1. Land Surface Modeling Strategy (Noah-MP)**
In this study, the Noah-MP (Multiparameterization) land surface model (v4.0.1; Niu et al., 2011) was implemented within the NASA Land Information System (LIS; Kumar et al., 2006) framework at a spatial resolution of 0.05° over the Sebou basin. Noah-MP is configured with a multilayer soil profile comprising four discrete layers with thicknesses of 0.1, 0.3, 0.6, and 1.0 m from the surface down to the bottom, totaling a 2 m soil column (Nie et al., 2022). Water movement in these soil layers is simulated using the Richards equation.

To represent baseflow generation and groundwater–surface water interactions—critical for semi-arid streamflow routing—the Simple Groundwater Model (SIMGM; Niu et al., 2007) was activated. This specific parameterization was selected because recent data assimilation studies (e.g., Ahmad et al., 2024) have demonstrated its suitability for coupling soil moisture updates with subsurface runoff dynamics. Following this parameterization, surface runoff and baseflow are both modeled as exponential functions of the depth to the water table. Surface runoff is simulated using the saturation-excess (Dunne) runoff technique, where the fractional saturated area determines the proportion of incident water categorized as surface runoff. This formulation explicitly links soil moisture profile updates to water table depth fluctuations, which subsequently influence the partitioned surface runoff and subsurface baseflow components. Furthermore, the BATS snow albedo and Jordan91 rain/snow partitioning schemes were adopted to accurately capture the timing of snowmelt contributions from the Middle Atlas mountains (Ma et al., 2017). 

To preserve the vegetation–soil moisture feedbacks essential for land surface data assimilation, the model incorporates a prognostic vegetation phenology scheme combined with a Ball–Berry photosynthesis-based stomatal resistance scheme (Nie et al., 2022; Kumar et al., 2019). This configuration allows the vegetation photosynthesis rate to be constrained by water stress, dynamically predicting seasonal leaf area growth and vegetation greenness fraction. Consequently, canopy conditions dynamically interact with the partitioning of water and energy fluxes, such as evaporation and transpiration. The modified two-stream radiation transfer model was also selected to properly account for canopy gap fractions as vegetation grows. 

Crucially, explicit anthropogenic irrigation modules were intentionally deactivated in the baseline configuration. Agricultural water use in the Sebou-Saïss basin relies heavily on unrecorded groundwater pumping, making forward modeling of irrigation highly uncertain. Instead, this study adopts the premise that the assimilation of satellite-derived soil moisture can implicitly capture unmodeled anthropogenic water applications (Lawston et al., 2017; Brocca et al., 2018). By omitting the irrigation module, this experimental design isolates and evaluates the capacity of soil moisture data assimilation to correct human-induced hydrological biases and propagate these corrections into the simulated streamflow.

**2.2.2. Meteorological Forcings and Topographic Correction**
Precipitation forcing was prescribed using the Integrated Multi-satellitE Retrievals for GPM (IMERG) Final Run product (V07B). IMERG provides half-hourly precipitation estimates at a 0.1° spatial resolution, combining passive microwave and infrared satellite data, which are subsequently gauge-calibrated. All other required near-surface meteorological fields were derived from the Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2; Gelaro et al., 2017). Within the LIS framework, the MERRA-2 atmospheric fields (~0.50° × 0.625°) and IMERG precipitation (0.1°) were spatially interpolated to the target 0.05° LSM grid and temporally disaggregated to the model integration time step using bilinear interpolation and topographic lapse-rate adjustments. 

To mitigate discrepancies over the substantial elevation gradients of the Middle Atlas, a terrain-based correction was applied to the MERRA-2 forcing fields. Near-surface air temperature was corrected using a standard environmental lapse rate of −6.5 K km⁻¹, while surface pressure and specific humidity were adjusted using physically consistent hypsometric scaling relationships implemented within LIS. Downward longwave radiation was subsequently recalculated to account for the corrected near-surface conditions (Nie et al., 2022; Kumar et al., 2006).

**2.2.3. Initialization and Spin-up Protocol**
Proper model initialization is critical to remove the influence of arbitrary initial conditions. A rigorous two-stage spin-up strategy was implemented, mirroring established data assimilation protocols within the NASA LIS framework (Kumar et al., 2019):
*   **Stage 1: Deterministic Spin-up.** A long-term deterministic (single-member) open-loop simulation was conducted over a 14-year period (2000–2013) using continuous MERRA-2 and IMERG forcings. This ensures that the root-zone soil moisture and the unconfined groundwater storage reach full thermodynamic and hydrological equilibrium (Ahmad et al., 2024).
*   **Stage 2: Ensemble Spin-up.** A 15-month ensemble spin-up was executed from January 2014 to March 2015 prior to the start of the assimilation period (April 2015). This transition optimally generates ensemble spread while minimizing unnecessary computational costs (Nie et al., 2022; Kumar et al., 2014).

### 2.3. SMAP Data Assimilation Framework (EnKF)

The assimilation of SMAP surface soil moisture retrievals was executed using a one-dimensional Ensemble Kalman Filter (1D-EnKF) implemented within the NASA Land Information System (LIS) framework, utilizing a 20-member ensemble. Crucially, raw SMAP retrievals were assimilated directly (no-preprocessing scaling) rather than applying the standard Cumulative Distribution Function (CDF) matching. While CDF-matching is traditionally used to remove systematic model-observation biases (Reichle & Koster, 2004), recent studies in heavily managed agricultural domains have demonstrated that such statistical rescaling inadvertently erases anthropogenic irrigation signals captured by satellites (Kumar et al., 2015; Ahmad et al., 2022). Because the baseline Noah-MP physics lacks parameterization for the widespread unrecorded groundwater pumping in the Sebou basin, the model's unconstrained climatology is inherently dry-biased during the growing season. Rescaling the "wetter" SMAP observations to match this dry model climatology would artificially neutralize the very irrigation signal this study aims to propagate into the hydrological routing. Therefore, direct assimilation was prioritized to implicitly capture these human-induced water applications (Ahmad et al., 2024). To ensure data reliability, only SMAP retrievals that passed the highest baseline quality assessment flags were assimilated. To generate the necessary ensemble spread, the Goddard Earth Observing System Model (GMAO) perturbation scheme was employed. Meteorological forcings were perturbed hourly using multiplicative Gaussian noise with standard deviations of 0.50 for precipitation and 0.30 for incident shortwave radiation, alongside a cross-correlation of -0.8 and a 24-hour temporal correlation. State variables were perturbed every three hours via an additive zero-mean noise (standard deviation of 0.004 m³ m⁻³) applied to the topmost soil moisture layer, constrained by a 12-hour temporal correlation. Finally, a temporally invariant observation error standard deviation of 0.04 m³ m⁻³ was assigned to the SMAP retrievals, representing the unbiased Root Mean Square Error (ubRMSE) mission requirement, with a 12-hour temporal correlation (Nie et al., 2022).

### 2.4. Streamflow Routing (HyMAP)
To simulate the lateral transport of surface and subsurface runoff generated by Noah-MP, the Hydrological Modeling and Analysis Platform (HyMAP; Getirana et al., 2012) was implemented in offline mode. HyMAP represents river floodplain dynamics and handles the kinematic wave routing of total runoff across the high-resolution DEM network. This offline configuration allowed for the isolated evaluation of both the Open-Loop (OPL) and Data Assimilation (DA) runoff outputs without internal model feedback loops, ensuring direct comparability of the resulting daily streamflow hydrographs.

### 2.5. Datasets

**2.5.1. Satellite Soil Moisture (SMAP)**
The core assimilation dataset comprises the SMAP Enhanced L3 Radiometer Global Daily 9 km EASE-Grid Soil Moisture (SPL3SMP_E) product. This L-band passive microwave radiometer retrieval provides robust top-layer (~5 cm depth) volumetric soil moisture estimates, well-suited for penetrating moderate vegetation canopies characteristic of the Mediterranean climate. The spatial mismatch between the native SMAP footprint (9 km) and the high-resolution Noah-MP routing grid (0.05°) was seamlessly handled by the LIS observation operator, which regrids the retrievals to the model space using bilinear interpolation.

**2.5.2. FAO WaPOR Evapotranspiration and Productivity**
To independently validate the water-energy budget closure, the FAO Water Productivity through Open access of Remotely sensed derived data (WaPOR) dataset was utilized. WaPOR provides spatially explicit, 250m-resolution decadal and monthly grids for Gross Evaporation (E), Transpiration (T), Evapotranspiration (ET), and Net Primary Productivity (NPP). This facilitates the assessment of whether soil moisture corrections positively propagate to surface fluxes.

**2.5.3. Surface Runoff and Baseflow Intercomparison**
Given the lack of continuous, distributed subsurface groundwater observations, simulated surface runoff ($Qs$) and subsurface baseflow ($Qsb$) partitioning were inter-compared against macro-scale outputs from the Global Land Data Assimilation System (GLDAS-2.1 NOAH, VIC, CLSM). These datasets provide baseline references for validating regional runoff generation behaviors. Additionally, Terrestrial Water Storage Anomalies (TWSA) were corroborated using GRACE/GRACE-FO mascon grids.

**2.5.4. In-Situ Streamflow Observations**
Continuous daily river discharge records, maintained by the Sebou Hydraulic Basin Agency (ABHS), were acquired for key validation gauges within the basin (e.g., the Ouergha and Inaouene sub-catchments). These historical time-series act as the primary ground-truth benchmark to rigorously evaluate the integrated impact of data assimilation on downstream water availability and unmodeled anthropogenic withdrawals.

## 3. Results

*This section outlines the planned sequence of figures, their intended titles, the core message to discuss, and placeholders for the generated visualizations.*

### 3.1. Spatial and Temporal Impact of SMAP Assimilation

**Figure 1: Spatial Context and Domain Characteristics**
* **Title:** Topoclimatic and Land Cover Characteristics of the Sebou Basin.
* **Message to Discuss:** Introduce the strong gradients in the basin (Middle Atlas snow vs. Saïss plain agriculture). Highlight the regions with the highest fractional irrigation where DA is expected to have the most significant unmodeled impact.
* **Placeholder:** *[Insert Figure 1 here - Generated via fig01_study_domain.py and fig01_spatial_context.py]*

**Figure 2: Soil Moisture Assimilation Increments and Temporal Innovations**
* **Title:** Spatial Distribution and Temporal Evolution of Soil Moisture Increments (DA - OPL).
* **Message to Discuss:** Demonstrate that EnKF successfully corrects soil moisture trajectories. Highlight how increments spatially align with human-managed agricultural areas (positive increments indicating unmodeled irrigation) versus natural forested/mountainous areas (correcting structural model biases).
* **Placeholder:** *[Insert Figure 2 here - Generated via fig03_sm_assim_impact.py]*

### 3.2. Surface Fluxes and Internal Water Budget Closure

**Figure 3: Spatial Impact on Vertical Fluxes and Evapotranspiration**
* **Title:** Impact of SMAP Assimilation on Simulated Evapotranspiration and Transpiration Dynamics.
* **Message to Discuss:** Validate that soil moisture updates correctly propagate into the water-energy cycle. Compare the DA-adjusted ET against independent FAO WaPOR and GLEAM products, demonstrating bias reduction during extreme dry spells, particularly in heavily vegetated/irrigated zones.
* **Placeholder:** *[Insert Figure 3 here - Generated via fig02_spatial_impact_fluxes.py]*

**Figure 4: Terrestrial Water Storage Anomalies (TWSA) Validation**
* **Title:** Evaluation of Simulated Terrestrial Water Storage Anomalies against GRACE/GRACE-FO.
* **Message to Discuss:** Prove that improvements in surface routing are supported by physically consistent internal water budget dynamics (i.e., we are not getting the right answer for the wrong reasons). Show how SMAP DA alongside SIMGM improves the interannual aquifer storage trends compared to GRACE mascons.
* **Placeholder:** *[Insert Figure 4 here - Generated via suggested_water_budget_analysis.py]*

### 3.3. Runoff Decomposition and Hydrometeorological Response

**Figure 5: Runoff Partitioning and Subsurface Dynamics**
* **Title:** Decomposition of Runoff: Surface vs. Baseflow Response to SMAP Assimilation.
* **Message to Discuss:** Analyze how sustained soil moisture corrections alter the partitioning of total runoff. Show that DA strongly controls rapid surface runoff during intense precipitation, while modifying the delayed baseflow response crucial for the Sebou basin's dry-season streamflow.
* **Placeholder:** *[Insert Figure 5 here - Generated via fig05_runoff_decomposition.py]*

### 3.4. Streamflow Validation and Anthropogenic Signatures

**Figure 6: Hydraulically Routed Streamflow Validation**
* **Title:** Validation of Routed Streamflow (HyMAP) against In-Situ Gauges.
* **Message to Discuss:** This is the capstone result. Demonstrate the enhanced skill (NSE, RMSE) of the assimilation run in capturing hydrograph peaks in natural sub-catchments. 
* **Placeholder:** *[Insert Figure 6 here - Generated via fig10_12_streamflow_validation.py]*

**Figure 7: Detection of Irrigation Signatures via Streamflow**
* **Title:** Bridging the Anthropogenic Gap: Streamflow Corrections in Highly Managed Sub-catchments.
* **Message to Discuss:** Emphasize that by disabling the explicit irrigation module, the DA process intrinsically recovers agricultural water use signatures. Show that soil moisture increments correctly translate into realistic streamflow depletions that match gauge observations in human-modified catchments.
* **Placeholder:** *[Insert Figure 7 here - Generated via fig04_runoff_irrigation.py]*

### 3.5. Responses to Extreme Events and Drought Categorization

**Figure 8: Vegetation Response and Drought Categorization**
* **Title:** Vegetation Dynamics (LAI) and Agricultural Drought Monitoring.
* **Message to Discuss:** Assess the model's performance during categorized extremes (severe droughts vs. wet winters). Show how DA accelerates the model's response to drought onset (removing artificial "memory effects") and translates into a reliable tool for real-time agricultural drought monitoring in the MENA region.
* **Placeholder:** *[Insert Figure 8 here - Generated via fig04_lai_dynamics.py and fig05_drought_categorization.py]*

## References

Ahmad, J. A., Forman, B. A., & Kumar, S. V. (2022). Soil moisture estimation in South Asia via assimilation of SMAP retrievals. Hydrology and Earth System Sciences, 26(8), 2221-2243.

Ahmad, J. A., Forman, B. A., Getirana, A., & Kumar, S. V. (2024). Influence of SMAP soil moisture retrieval assimilation on runoff estimation across South Asia. Journal of Hydrology, 630, 130635.

Arjdal, K., Driouech, F., Vrac, M., et al. (2023). Future of land surface water availability over the Mediterranean basin and North Africa: Analysis and synthesis from the CMIP6 exercise. Atmospheric Science Letters, 24(7), e1167.

Brocca, L., Tarpanelli, A., Filippucci, P., et al. (2018). How much water is used for irrigation? A new approach exploiting coarse resolution satellite soil moisture products. International Journal of Applied Earth Observation and Geoinformation, 73, 752-766.

Crow, W. T., van den Berg, M. J., Huffman, G. J., & Pellarin, T. (2011). Correcting satellite-based precipitation products via the assimilation of satellite surface soil moisture retrievals. Journal of Hydrometeorology, 12(1), 70-85.

Driouech, F., El Rhaz, K., Tramblay, Y., et al. (2020). Observed and simulated changes in extreme temperature and precipitation indices in Morocco. Global and Planetary Change, 192, 103280.

Gelaro, R., McCarty, W., Suárez, M. J., et al. (2017). The modern-era retrospective analysis for research and applications, version 2 (MERRA-2). Journal of Climate, 30(14), 5419-5454.

Getirana, A. C., Boone, A., Yamazaki, D., et al. (2012). The Hydrological Modeling and Analysis Platform (HyMAP): Evaluation in the Amazon Basin. Journal of Hydrometeorology, 13(6), 1641-1665.

Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009). Decomposition of the mean squared error and NSE performance criteria: Implications for improving hydrological modelling. Journal of Hydrology, 377(1-2), 80-91.

Jarlan, L., Khabba, S., Er-Raki, S., et al. (2015). Remote sensing of water resources in semi-arid Mediterranean areas: the joint international laboratory TREMA. International Journal of Applied Earth Observation and Geoinformation, 43, 118-134.

Kumar, S. V., Peters-Lidard, C. D., Tian, Y., et al. (2006). Land information system: An interoperable framework for high resolution land surface modeling. Environmental Modelling & Software, 21(10), 1402-1415.

Kumar, S. V., Reichle, R. H., Harrison, K. W., et al. (2008). A comparison of methods for a priori bias correction in soil moisture data assimilation. Water Resources Research, 44(10).

Kumar, S. V., Peters-Lidard, C. D., Mocko, D., Reichle, R., Liu, Y., Arsenault, K. R., ... & Xia, Y. (2014). Assimilation of remotely sensed soil moisture and snow depth retrievals for drought estimation. Journal of Hydrometeorology, 15(6), 2446-2469.

Kumar, S. V., Holmes, T., Andreadis, K., et al. (2019). Assimilation of remotely sensed soil moisture and leaf area index in an ensemble land surface framework. Water Resources Research, 55(5), 4316-4332.

Lawston, P. M., Santanello, J. A., Kumar, S. V., et al. (2017). Assessment of irrigation physics in a land surface modeling framework using SMAP and SMOS satellite observations. Journal of Geophysical Research: Atmospheres, 122(14), 7279-7297.

Ma, N., Niu, G. Y., Xia, Y., et al. (2017). Observation-based evaluation of Noah-MP land surface model skill in simulating cold processes over the Tibetan Plateau. Journal of Geophysical Research: Atmospheres, 122(9), 4781-4795.

Martens, B., Miralles, D. G., Lievens, H., et al. (2017). GLEAM v3: Satellite-based land evaporation on a global scale. Geoscientific Model Development, 10(5), 1903-1925.

Nie, W., Zaitchik, B. F., Bounoua, L., et al. (2022). Assimilation of Earth observation data to estimate soil moisture and leaf area index over Northern Morocco. Remote Sensing, 14(10), 2433.

Niu, G.-Y., Yang, Z.-L., Dickinson, R. E., et al. (2007). Development of a simple groundwater model for use in climate models and evaluation with Gravity Recovery and Climate Experiment data. Journal of Geophysical Research: Atmospheres, 112(D7).

Niu, G.-Y., Yang, Z.-L., Mitchell, K. E., et al. (2011). The community Noah land surface model with multiparameterization options (Noah-MP): 1. Model description and evaluation with local-scale measurements. Journal of Geophysical Research: Atmospheres, 116(D12).

Peters-Lidard, C. D., Houser, P. R., Tian, Y., et al. (2007). High-performance Earth system modeling with NASA/Software Integration framework. Innovations in Systems and Software Engineering, 3(3), 157-165.

Reichle, R. H., & Koster, R. D. (2004). Bias reduction in short science records of satellite soil moisture. Geophysical Research Letters, 31(19).

Tapley, B. D., Bettadpur, S., Watkins, M., & Reigber, C. (2004). Gravity recovery and climate experiment: Mission status and early results. Geophysical Research Letters, 31(9).

Tramblay, Y., Jarlan, L., Hanich, L., et al. (2020). Impacts of climate change on extreme events in the Mediterranean basin. Earth-Science Reviews, 210, 103385.

Yang, Z.-L., Niu, G.-Y., Mitchell, K. E., et al. (2011). The community Noah land surface model with multiparameterization options (Noah-MP): 2. Evaluation over global river basins. Journal of Geophysical Research: Atmospheres, 116(D12).

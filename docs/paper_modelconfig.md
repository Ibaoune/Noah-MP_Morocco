> **Author:** M. El Aabaribaoune (@UM6P)  
> **Date:** 2026-06-07

---

# Model Configuration

In this study, the Noah-MP (Multiparameterization) land surface model (version 4.0.1) was implemented within the NASA Land Information System (LIS) framework at a spatial resolution of 0.01° (~1 km) over the Sebou-Saïss basin (32.5°N–35.5°N, 7.0°W–3.5°W), corresponding to a 301 × 351 grid. The model was driven by the Modern-Era Retrospective analysis for Research and Applications version 2 (MERRA-2) meteorological forcing, using the lowest model level fields and the corrected total precipitation product. The model was run in cold-start mode for a retrospective simulation beginning on 1 January 2015, with a model time step of 15 minutes and daily output.

The dynamic vegetation option (option 2) was activated to enable prognostic phenology, allowing the Leaf Area Index (LAI) and Green Vegetation Fraction (GVF) to evolve freely throughout the simulation — a key prerequisite for the dynamic irrigation scheduling. Canopy stomatal resistance was represented using the Ball-Berry scheme (option 1), soil moisture stress on stomatal resistance followed the Noah parameterization (option 1), and runoff and groundwater interactions were handled through the SIMGM scheme (option 1). Radiation transfer was parameterized using option 3 (gap = 1 − Fveg), and snow surface albedo followed the CLASS scheme (option 2). The soil column was discretized into four layers with thicknesses of 0.1, 0.3, 0.6, and 1.0 m.

To explicitly account for human-managed water use, the demand-driven sprinkler irrigation scheme (Ozdogan et al., 2010; Nie et al., 2018) was enabled. The spatial distribution of irrigated areas was defined using the FAO Global Map of Irrigated Areas (GMIA v5.0), integrated over agricultural land cover pixels classified by the MODIS IGBP dataset. Rather than relying on static crop calendars or highly uncertain local crop-specific distribution maps, this study adopted a generic cropland representation to minimize parameterization uncertainties. Consequently, a uniform maximum effective root depth of 1.0 m was assigned to all irrigated agricultural areas to calculate the root zone soil moisture deficit consistently. Furthermore, following the methodology of Nie et al. (2022), the irrigation scheduling was dynamically coupled with Noah-MP's prognostic phenology module. Irrigation is automatically triggered when the dynamically simulated vegetation growth (i.e., Leaf Area Index) indicates an active growing season (GVF > 0.40) and the root-zone soil moisture drops below a predefined threshold of 50% of the field capacity. When triggered, the scheme computes and applies the exact volume of water required to replenish the root zone to field capacity, allowing crops to transpire without water stress.

---

### Table 1: Summary of the Noah-MP 4.0.1 Model Configuration

| Component / Parameter | Setting / Value | Reference / Note |
| :--- | :--- | :--- |
| **Modeling Framework** | NASA Land Information System (LIS) | Kumar et al. (2006) |
| **Land Surface Model** | Noah-MP v4.0.1 | Niu et al. (2011) |
| **Spatial Domain** | Sebou-Saïss basin (32.5°N–35.5°N, 7.0°W–3.5°W) | 301 × 351 grid cells |
| **Spatial Resolution** | 0.01° × 0.01° (~1.1 km) | — |
| **Model Time Step** | 15 minutes | — |
| **Simulation Period** | January 2015 onwards | Cold-start |
| **Meteorological Forcing** | MERRA-2 (lowest model level + corrected precipitation) | GMAO (2015) |
| **Land Cover / Vegetation** | MODIS IGBP | Friedl et al. (2010) |
| **Soil Column Layers** | 4 layers: 0.1 / 0.3 / 0.6 / 1.0 m | — |
| **Dynamic Vegetation** | Option 2 — Prognostic phenology (LAI/GVF simulated) | Niu et al. (2011) |
| **Stomatal Resistance** | Ball-Berry scheme (Option 1) | Ball et al. (1987) |
| **Runoff & Groundwater** | SIMGM (Option 1) | Niu et al. (2007) |
| **Radiation Transfer** | Gap = 1 − Fveg (Option 3) | — |
| **Snow Albedo** | CLASS scheme (Option 2) | Verseghy (1991) |
| **Irrigation Scheme** | Demand-driven Sprinkler | Ozdogan et al. (2010) |
| **Irrigated Area Extent** | FAO GMIA v5.0 | Siebert et al. (2013) |
| **Crop Representation** | Generic (no crop-specific map) | — |
| **Effective Root Depth** | Uniform 1.0 m | — |
| **Irrigation Trigger** | Prognostic GVF > 0.40 AND SM < 50% Field Capacity | Nie et al. (2022) |
| **GVF Threshold (param 1)** | 0.40 | — |
| **Soil Moisture Threshold** | 50% of Field Capacity | — |
| **Irrigation Source** | Surface water (no groundwater abstraction) | — |

> **Author:** M. El Aabaribaoune (@UM6P)  
> **Date:** 2026-06-07

---

## 2.X Meteorological and Precipitation Forcing Data

Accurate meteorological forcing is critical for simulating the hydrological cycle, particularly in topographically complex regions like the Sebou-Saïss basin. Following the methodology outlined by Nie et al. (2022), the Noah-MP (v4.0.1) land surface model was driven by a combination of global meteorological reanalysis and satellite-based precipitation datasets. 

**Meteorological Forcing (GDAS):**
Near-surface meteorological forcing variables—including downward shortwave and longwave radiation, air temperature, specific humidity, wind speed, and surface pressure—were derived from the National Centers for Environmental Prediction (NCEP) Global Data Assimilation System (GDAS). The GDAS data, provided at a 0.25° spatial resolution and 6-hourly temporal resolution, were temporally interpolated to the 15-minute model integration time step using linear interpolation. Spatially, the fields were downscaled to the 1 km Noah-MP grid using bilinear interpolation.

**Topographic Correction:**
Given the significant elevation gradients within the Sebou basin (ranging from the low-lying Saïss plain to the high-altitude Middle Atlas mountains), a topographic correction was applied to the coarse-resolution GDAS forcing fields to mitigate representation errors. Following Nie et al. (2022), a lapse-rate correction method was employed within the Land Information System (LIS) framework. Near-surface air temperature, surface pressure, specific humidity, and downward longwave radiation were dynamically adjusted based on the elevation difference between the native GDAS topography (extracted from the T574 global orography) and the high-resolution 1 km model grid. A standard environmental lapse rate of -6.5 K/km was applied for the temperature adjustments, and the corresponding state variables were physically scaled accordingly.

**Precipitation Forcing (GPM IMERG):**
Precipitation forcing was provided by the Integrated Multi-satellitE Retrievals for GPM (IMERG) Final Run product (V07B). Compared to the IMERG Early Run used in operational forecasts (Nie et al., 2022), the Final Run incorporates monthly gauge adjustments, providing higher accuracy suitable for retrospective hydrological modeling and spin-up. The IMERG precipitation fields (native 0.1° spatial resolution) were spatially downscaled to the 1 km model grid using bilinear interpolation. To prevent inconsistencies between the precipitation and other meteorological variables, the LIS forcing blending configuration was set to overlay the IMERG precipitation directly onto the GDAS atmospheric forcing background.

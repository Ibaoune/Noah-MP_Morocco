# Drought Diagnostics Results (V0)

## 3.X Relative drought-area diagnostics

To evaluate the diagnostic sensitivity of drought indicators to SMAP data assimilation, a relative model-derived drought classification was computed based on the Open Loop (OPL) pooled 2016–2020 reference distribution. This approach allows the states from the DA-NoCDF and DA-CDF experiments to be mapped onto a common baseline, isolating the assimilation-induced structural shifts.

The surface soil moisture (SSM) drought classification exhibits minimal sensitivity to the assimilation updates. The mean area classified as moderate drought (D1, percentile ≤ 20%) slightly decreases from the 20.0% reference baseline to 18.5% in both the DA-NoCDF and DA-CDF experiments. This stability reflects the strong control of high-frequency precipitation forcing on the surface layer, which rapidly dissipates the transient assimilation increments.

In stark contrast, root-zone soil moisture (RZSM) displays a massive diagnostic sensitivity. Because RZSM integrates the assimilation updates vertically and drives deeper hydrological responses like evapotranspiration, it serves as the preferred indicator for sustained agricultural drought. The DA-NoCDF experiment shifts the mean D1 drought area from 20.0% up to 48.9%. The DA-CDF experiment similarly dries the profile but dampens the magnitude of the shift to 39.5%. Because these diagnostics rely on a short 5-year OPL-based reference period, these dramatic expansions do not denote absolute climatological drought events; rather, they demonstrate that the SMAP-constrained states are systematically drier than the model's internal baseline, thereby triggering widespread relative drought classifications.

## 3.Y DA-induced shifts in model-derived drought classes

A pixel-level discrete transition analysis further quantifies how often the assimilation explicitly alters the categorical drought classification. For SSM, the transitions are balanced, resulting in a slight net alleviation of the drought classes. 

However, for RZSM, the DA-NoCDF experiment introduces a new categorical drought classification (relative to the OPL state) across 31.0% of the domain on average, while removing drought conditions in only 5.0% of the area. This net intensification of the drought classification is perfectly consistent with the systemic reduction in root-zone water and evapotranspiration observed in the hydrological fluxes. The spatial robustness of this RZSM response is also corroborated by the Random Forest attribution analysis, which found deep-layer moisture to be highly predictive. While the DA-CDF approach mitigates the severity of these structural shifts (21.5% introduced drought), the systematic drying trend remains robust, underscoring the profound sensitivity of model-derived drought monitoring frameworks to both the observational constraint and the chosen assimilation scaling methodology.

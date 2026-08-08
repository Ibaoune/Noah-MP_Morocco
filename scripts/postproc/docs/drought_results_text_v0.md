# Drought Diagnostics Results (V0)

## 3.X Relative low-soil-moisture diagnostics

To evaluate the diagnostic sensitivity of drought indicators to SMAP data assimilation, a relative model-derived low-soil-moisture classification was computed based on the Open Loop (OPL) pooled 2016–2020 reference distribution. This approach maps the states from the DA-NoCDF and DA-CDF experiments onto a common baseline, isolating the assimilation-induced structural shifts. Because these diagnostics rely on a short 5-year OPL-based reference period, they are strictly relative low-soil-moisture diagnostics and do not represent a robust climatological drought index. Consequently, only the D1 (≤20%) and D2 (≤10%) thresholds are emphasized, as extreme classes lack statistical stability in a 5-year sample.

The surface soil moisture (SSM) drought classification exhibits minimal sensitivity to the assimilation updates. The mean area classified as D1 slightly decreases from the 20.0% reference baseline to 18.5% and 18.6% in the DA-NoCDF and DA-CDF experiments, respectively. This stability reflects the strong control of high-frequency precipitation forcing on the surface layer, which rapidly dissipates the transient assimilation increments without inducing a structural shift.

In stark contrast, root-zone soil moisture (RZSM) displays a high diagnostic sensitivity. RZSM is preferred for this analysis because it integrates the assimilation updates vertically and drives deeper hydrological responses like evapotranspiration. The DA-NoCDF experiment shifts the mean D1 area from 20.0% up to 48.9%, which represents a substantial increase of +28.9 percentage points. The DA-CDF experiment similarly dries the profile but dampens the magnitude of the shift, resulting in a mean D1 area of 39.5% (+19.5 percentage points). 

These DA-induced shifts relative to the OPL reference are perfectly consistent with the water balance analysis, which showed that DA-NoCDF produces an average drying of RZSM while modifying ET and runoff components. Furthermore, the Random Forest attribution analysis identified RZSM and ET as the most spatially robust responses to assimilation, supporting the focus on RZSM for drought monitoring. It is critical to note that this substantial expansion of the relative low-soil-moisture area serves as a diagnostic sensitivity check on the model's internal states, not a validation of true meteorological drought.

## 3.Y DA-induced shifts in model-derived drought classes

A pixel-level discrete transition analysis quantifies how often the assimilation explicitly alters the categorical classification. For SSM, the transitions are balanced, resulting in a slight net alleviation of the classes. 

However, for RZSM, the DA-NoCDF experiment introduces a low-RZSM classification for approximately 31.0% of evaluated pixel-month cases relative to OPL, while removing the condition in only 5.0% of cases. This net intensification of the drought classification aligns with the systemic reduction in root-zone water. While the DA-CDF approach mitigates the severity of these structural shifts (21.5% introduced drought), the systematic drying trend remains robust. This underscores the high diagnostic sensitivity of model-derived low-soil-moisture monitoring frameworks to both the observational constraint and the chosen assimilation scaling methodology.

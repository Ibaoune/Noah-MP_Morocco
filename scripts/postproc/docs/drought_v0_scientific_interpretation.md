# Drought Diagnostics V0 Scientific Interpretation

## A. Main message RZSM
The root-zone soil moisture (RZSM) shows a massive diagnostic sensitivity to SMAP assimilation. The DA-NoCDF experiment shifts the mean D1 drought area from 20.0% (OPL reference) up to 48.9% (a +28.9% shift). This means that relative to the model's unassimilated baseline, the updated states are substantially drier, triggering a model-derived drought classification across much larger areas.

## B. Main message SSM
In contrast to RZSM, the surface soil moisture (SSM) drought classification remains relatively stable, with the mean D1 area slightly decreasing from 20.0% to 18.5%. The surface layer is strongly constrained by high-frequency precipitation forcing, so the SMAP updates introduce only transient, highly variable shifts that result in a slight net alleviation of drought classes.

## C. DA-NoCDF vs OPL
DA-NoCDF produces the strongest structural shifts. For RZSM, the discrete transition matrix shows that 31.0% of the domain area experiences an "introduced drought" classification relative to the OPL, while only 5.0% experiences a "removed drought." This confirms a strong systemic drying of the deeper profile by the unscaled increments.

## D. DA-CDF vs OPL
DA-CDF also systematically dries the root zone, but the magnitude of the shift is damped. The mean D1 area increases by +19.5% (compared to +28.9% for NoCDF). The CDF-matching explicitly scales the increments to respect the OPL climatology, thereby mitigating the severity of the diagnostic drought-class transitions while still propagating the drying trend.

## E. DA-NoCDF vs DA-CDF
The difference between DA-NoCDF and DA-CDF highlights the critical role of the observation operator. While both indicate that the baseline OPL is too wet relative to SMAP observations, DA-NoCDF aggressively alters the categorical drought threshold, whereas DA-CDF produces a more conservative diagnostic shift.

## F. Link with hydrological response
These results are perfectly consistent with the water balance analysis (Section 3.4), which demonstrated that assimilation systematically reduces RZSM and ET while slightly increasing pre-routing baseflow. The drying of the root zone directly manifests here as a drastic expansion of the model-derived drought area.

## G. Link with RF/XAI
The Random Forest diagnostics (Section 3.Y) established that RZSM and ET exhibit the highest predictability and strongest spatial coherence among the DA-induced responses. Consequently, the RZSM drought indicators are more stable and represent a more robust diagnostic metric for agricultural/ecological drought monitoring than the transient SSM responses.

## H. Cautions
These diagnostics rely on an `opl_pooled_2016_2020` reference distribution. Therefore, the +28.9% expansion of drought area does not mean that a "true historical drought" occurred. It indicates that the DA-updated states are systematically drier than the model's 5-year internal climatology. The shifts must be interpreted purely as relative diagnostic sensitivities.

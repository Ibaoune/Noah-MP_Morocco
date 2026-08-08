# Drought Diagnostics Results (V0)

## 3.X Relative drought-area response to SMAP assimilation

To evaluate the diagnostic sensitivity of drought indicators to SMAP data assimilation, a relative model-derived drought classification was computed based on the 2016–2020 distributions of Surface Soil Moisture (SSM) and Root-Zone Soil Moisture (RZSM). The analysis compares the temporal evolution of the drought area percentage (pixels classified as D1 or worse, representing a percentile rank ≤ 20%) across the Open Loop (OPL), DA-NoCDF, and DA-CDF experiments.

The assimilation of SMAP observations introduces notable shifts in the estimated area under drought. While the interannual variability follows the primary hydroclimatic forcing, the magnitude of the drought peaks is frequently modulated by the assimilation updates. Because these diagnostics rely on a relatively short 2016–2020 reference period, the DA-induced changes are interpreted strictly as relative diagnostic sensitivities rather than absolute climatological drought corrections. The results are consistent with the hypothesis that directly updating soil moisture states alters the thresholds governing the onset and severity of model-derived drought events.

## 3.Y Drought transition diagnostics

A pixel-level discrete transition analysis was conducted to quantify how often the assimilation explicitly alters the drought category relative to the OPL baseline. When transitioning from the OPL to the DA-NoCDF states, a substantial fraction of pixels experience an alleviated or intensified drought class. The DA-CDF approach similarly induces transitions, though the rescaling process can dampen the magnitude of the structural shifts observed in the unscaled increments.

These DA-induced shifts in drought classification suggest that land-surface states are highly sensitive to the observational constraints, particularly in semi-arid domains. However, without a dense, long-term in-situ validation network, these transitions reflect model-derived diagnostic sensitivities and do not imply an improvement in true observed drought conditions. The differences underscore the critical role that assimilation methodology plays in operational drought monitoring frameworks.

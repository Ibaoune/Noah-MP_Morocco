# Sprint 2: First-Order Water-Balance Diagnostic

## Objective
The goal is to compute a first-order water balance to verify the interpretability of the hydrological fluxes resulting from SMAP data assimilation. 

## Variables Used
- **P**: Precipitation (IMERG)
- **ET**: Total Evapotranspiration
- **Qs**: Surface Runoff
- **Qsb**: Baseflow
- **Qtotal**: Total Runoff (Qs + Qsb)
- **Flux-only Residual**: P − ET − Qtotal

All fluxes were converted from mm/month to **mm/day** for intuitive seasonal comparisons.

## Assumptions and Limitations
1. **No Storage Change (dS) Included**: Because the dataset provides temporally aggregated mean states rather than start-of-month and end-of-month snapshots, calculating an exact Δsoil_storage (dS) and Δgroundwater_storage is mathematically complex and prone to errors. Therefore, a *flux-only* balance is used.
2. **Interpretability over Closure**: The flux-only balance provides a first-order interpretability check, but does not demonstrate water-balance closure because storage changes are not explicitly included.
3. **No Routing**: The baseflow represents deep drainage at the pixel level, not measured streamflow, as no routing model (HyMAP) is used here.

## Differences: OPL vs DA-NoCDF vs DA-CDF
- **DA-NoCDF**: Introduces significant shifts in the residual term compared to OPL, particularly in winter (DJF), consistent with the addition or removal of water through data assimilation increments. The runoff and ET changes track these unclosed moisture injections.
- **DA-CDF**: The fluxes (ET and Qtotal) and the residual remain almost perfectly identical to the OPL experiment. The CDF matching effectively neutralizes the hydrological response, acting as a strong dampening filter.

## Conclusion
The DA-NoCDF experiment produces changes in runoff and ET that are consistent with the unmodeled water additions/removals suggested by SMAP, even if it creates an artificial imbalance in the model's native closed loop. NoCDF remains a powerful diagnostic tool rather than a strictly mass-conservative hydrological configuration.

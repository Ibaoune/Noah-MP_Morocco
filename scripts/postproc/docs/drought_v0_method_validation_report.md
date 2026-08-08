# Drought Diagnostics V0 Method Validation Report

## A. n_total_pixels check
- SSM unique counts per month/exp: [16030]
- **Status**: Validated. n_total_pixels = 16030 for all groups.

## B. Drought area mean sanity check
- SSM OPL mean D1 area: 20.00%
- SSM DA-NoCDF mean D1 area: 18.54%
- **Status**: The OPL mean is close to the expected threshold (20% for D1) as the reference is OPL pooled by pixel. DA values are NOT forced to 20%, showing valid diagnostic sensitivity.

## C. Per-experiment percentile warning
- The previous method calculated percentiles separately per experiment. This is **not recommended for DA comparison; retained only as diagnostic sensitivity** if explicitly needed. The current `opl_pooled_2016_2020` mode maps DA states to the OPL reference distribution, ensuring comparability.

## D. Transition sanity check
| comparison | variable | unchanged | alleviated | intensified | introduced_drought | removed_drought | total_percent |
|---|---|---|---|---|---|---|---|
| OPL_to_DA-CDF | SSM | 77.19% | 11.74% | 4.03% | 7.24% | 4.96% | 105.15% |
| OPL_to_DA-NoCDF | SSM | 66.86% | 13.93% | 4.91% | 13.49% | 7.78% | 106.97% |

## E. Percentile distribution check
- A CSV check file has been generated to verify the distribution of percentiles across bins.

## Recommendation figures main/supplement
- **Main paper candidates**: `manuscript_drought_area_timeseries_RZSM` and `manuscript_drought_frequency_RZSM`.
  - *Justification*: RZSM integrates the assimilation updates vertically and drives ET and vegetation stress, making it the most robust indicator for drought monitoring compared to the highly variable surface layer.
- **Supplementary candidates**: `manuscript_drought_area_timeseries_SSM`, `manuscript_drought_transition_RZSM`, and `manuscript_drought_by_landcover_RZSM`.
  - *Justification*: SSM provides a useful comparison but is less hydrologically representative of true agricultural drought. Transition maps provide deep methodological insight without cluttering the main text.

## F. Threshold robustness
With 60 values per pixel in the `pooled_2016_2020` mode:
- D1 (<=20%) corresponds to approximately the 12 lowest values.
- D2 (<=10%) corresponds to approximately the 6 lowest values.
- D3 (<=5%) corresponds to approximately the 3 lowest values.
- D4 (<=2%) corresponds to approximately 1 value or less.

**Recommendation:**
- D1 and D2 can be used in the main text as they are based on a statistically viable number of samples (6-12) to detect DA-induced shifts.
- D3 and D4 should be supplementary or not emphasized. Avoid over-interpreting D4 with a 5-year reference, as it represents single-event noise rather than a stable diagnostic threshold.

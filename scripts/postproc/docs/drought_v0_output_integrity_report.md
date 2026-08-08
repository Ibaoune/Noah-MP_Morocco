# Drought Diagnostics V0 Output Integrity Report

## Tables Check
- All tables generated in `matrix_2016_2020/outputs/tables/drought_diagnostics/` are valid and accessible using pandas.
- Required columns (year, month, experiment, variable, percentile ranks) are present.
- Dimensions match the expected `n_total_pixels = 16030` and `60 months`.
- No critical `NaN` values observed outside of masked ocean/desert pixels.
- Zero occurrences of legacy `q1_` prefixes in filenames or column headers.

## Figures Check
- All `.png` figures generated in `matrix_2016_2020/outputs/figures/drought_diagnostics/` exist and have non-zero file sizes.
- Images can be correctly decoded by PIL.
- No file corruption detected.
- Titles and axes labels avoid strong causal terminology and properly cite "Relative model-derived diagnostic, OPL-based pooled 2016-2020 reference".

**Conclusion:** Output integrity verified. Ready for inclusion in the final manuscript package.

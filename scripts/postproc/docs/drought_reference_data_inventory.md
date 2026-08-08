# Drought Reference Data Inventory

## 1. Availability of long OPL reference
- **available_long_reference**: partial
- **years available**: 2005–2015 (SPINUP_OPL) + 2016–2020 (matrix_2016_2020/OPL).
- **variables available**: `SoilMoist` (layers 1-4) in daily `LIS_HIST` NetCDF outputs.
- **whether files are directly usable**: No. The data exists as raw daily LIS outputs. It has not been aggregated to monthly averages, masked, or flattened into the unified pixel-level parquet format used for the 2016-2020 analysis.

## 2. Recommended reference strategy
Since the long reference is not directly usable and requires significant post-processing (spatial extraction, monthly aggregation, parquet conversion), we will not construct it in this sprint. 

The recommended reference strategy for the current drought diagnostics remains **`opl_pooled_2016_2020`**. This mode pools the 60 available months per pixel to evaluate the relative drought class. While it does not remove seasonality, it provides a stable diagnostic baseline for comparing DA-NoCDF and DA-CDF shifts against OPL.

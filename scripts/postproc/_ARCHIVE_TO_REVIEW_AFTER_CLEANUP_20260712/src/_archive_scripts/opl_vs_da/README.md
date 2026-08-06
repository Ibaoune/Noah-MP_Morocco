# OPL vs DA Modular Plotting Framework
**Author:** M. EL Aabaribaoune (@um6p)

**Author:** M. El Aabaribaoune (@um6p)

This directory contains a data-driven, modular Python framework designed to automatically generate high-quality 1x3 Cartesian grid maps comparing **Noah-MP Open Loop (OL)** against **Data Assimilation (DA)**.

## Architecture

The framework is decoupled into 4 main files:

1. **`config_opl_da.yaml`**: The central configuration. Defines variable names (`ESoil_tavg`, `SoilMoist_tavg`), plotting bounds (`vmin`/`vmax`), units, and unit multipliers. It also controls the temporal aggregation (`all-period` vs `seasonal`).
2. **`main.py`**: The orchestrator script. Run this to parse the YAML and launch the plotting jobs.
3. **`core.py`**: The processing engine. Computes differences, temporal means, spatial statistics, and generates the layout.
4. **`utils.py`**: Geospatial and NetCDF utilities (Cartopy definitions, date parsing).

## How to Run

1. Ensure your conda environment is activated:
   ```bash
   conda activate postproc_env
   ```
2. Execute the main script:
   ```bash
   python main.py
   ```

The script will iterate over all variables defined in `config_opl_da.yaml` and save the output figures in the configured `dir_figures` directory.

## Adding a New Variable

To plot a new variable from the LIS NetCDF outputs, you **do not need to write any Python code**. Simply add a block to `config_opl_da.yaml`:

```yaml
  SWE_tavg:
    title_name: "Snow Water Equivalent"
    unit: "mm"
    layer_index: null
    cmap: "Blues"
    vmin: 0.0
    vmax: 50.0
    diff_cmap: "RdBu"
    diff_vmax: 10.0
    multiplier: 1.0
```

## Note on External Validation
Scripts that rely on **external observational datasets** (like WaPOR, FLUXSAT, or MODIS LAI) to compute RMSE, Bias, or Correlation (R) have been migrated to the `../opl_vs_da_vs_obs/` directory to maintain a strict "Model vs Model" focus in this folder.

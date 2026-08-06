# Assimilation Diagnostics Post-Processing
**Author:** M. EL Aabaribaoune (@um6p)

This module generates publication-ready diagnostic figures for the 2016 SMAP assimilation experiment. It systematically extracts, computes, and plots several metrics to evaluate the performance and physical impact of the Data Assimilation (DA) system.

## Diagnostic Metrics & Interpretation

### 1. Assimilation Coverage & Frequency (`Fig02`)
- **Files used**: `*innov.a01.d01.nc`
- **Variables**: `obs_01` (SMAP observations)
- **Metrics computed**:
  - **Spatial Assimilation Frequency**: The ratio of days where a valid observation was assimilated at a given grid cell, relative to the total number of days in the period (expressed in `obs d⁻¹`).
  - **Monthly Total Observations**: The domain-integrated count of assimilated observations for each month.
- **Interpretation**: Identifies the spatial distribution of the SMAP satellite swaths and highlights potential observational gaps (e.g., due to dense vegetation, freezing, or orbital patterns). The monthly totals highlight temporal variations in data availability across the year.

### 2. Innovations and Increments (`Fig04`)
- **Files used**: `*innov.a01.d01.nc` and `*EnKF_incr*.nc`
- **Variables**: `innov_01` (observation-space innovations) and `SoilMoist_inst` at Layer 1 (model-state increments).
- **Metrics computed**:
  - **Mean Innovation**: Time-averaged difference between the observation and the model forecast prior ($y - H(x^f)$). A positive value indicates the satellite observation is systematically wetter than the model forecast.
  - **Mean Increment**: Time-averaged update applied to the model state ($x^a - x^f$). A positive value indicates the assimilation systematically adds water to the model soil moisture.
  - **Increment Distribution**: Histogram of all daily increment values across the domain.
- **Interpretation**: Evaluates the systematic biases being corrected by the assimilation. It reveals regional patterns where the land surface model is consistently too dry (requiring positive increments) or too wet (requiring negative increments) compared to the SMAP baseline.

### 3. Seasonal Increments (`Fig05`)
- **Files used**: `*EnKF_incr*.nc`
- **Variables**: `SoilMoist_inst` at Layer 1.
- **Metrics computed**:
  - **Wet Season Increment**: Mean increment during the hydrologically wet months (November–April).
  - **Dry Season Increment**: Mean increment during the hydrologically dry months (May–October).
- **Interpretation**: Investigates seasonal biases in the land surface model. It reveals if the model dries out too quickly in summer or drains too slowly in winter, and demonstrates how the DA system compensates for these seasonal dynamics.

### 4. Spread & Uncertainty Diagnostics (`Fig06` & `Fig07`)
- **Files used**: `*innov.a01.d01.nc` and `*EnKF_spread*.nc`
- **Variables**: `forecast_sigma_01` (forecast uncertainty) and `ensspread_Soil Moisture Layer 1_01` (model-state ensemble spread).
- **Metrics computed**:
  - **Valid Mask Consistency**: Compares the spatial coverage of both diagnostics.
  - **Forecast Uncertainty (obs space)**: Uncertainty mapped specifically at assimilated observation locations.
  - **Model-State Spread (state space)**: Ensemble spread snapshot at daily output times over the entire LIS land mask.
- **Important Interpretation Note**: These two variables **are not directly comparable** and must not be interpreted as a prior/posterior spread reduction pair. They differ in physical space (observation vs. model-state), spatial support (satellite footprint vs. full mask), and timing (assimilation times vs. daily snapshots). The diagnostics simply verify their spatial coverage consistency and their independent statistical distributions.

---

## Configuration Architecture

The module uses a robust **3-level configuration architecture** to ensure reproducibility, allow easy tuning, and avoid parameter duplication:

1. **`configs/global.yaml`**: Contains common paths, default plotting options (e.g., DPI, fonts, margins), and map styling (coastlines, borders).
2. **`configs/experiments/*.yaml`**: Contains experiment-specific parameters such as the experiment name, analysis period, and input directories.
3. **`configs/diagnostics/*.yaml`**: Each file (`coverage.yaml`, `innovations.yaml`, etc.) contains purely diagnostic-specific parameters like panel layout, colorbars, bounds, titles, and target output filenames.

At execution, `main.py` automatically merges the global config, the selected experiment config, and the specific diagnostic configs.

## Execution

You can execute all diagnostics for an experiment simultaneously, or just a specific module.

**Run all diagnostics:**
```bash
python main.py --experiment configs/experiments/DA-noCDF-noIRR_2016.yaml --all
```

**Run a single diagnostic (e.g., coverage):**
```bash
python main.py --experiment configs/experiments/DA-noCDF-noIRR_2016.yaml --diagnostic coverage
```

Alternatively, you can submit the job via SLURM on the cluster:
```bash
sbatch job_assimilation_diagnostics.sh
```

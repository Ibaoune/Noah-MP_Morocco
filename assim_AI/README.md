# Assimilation Diagnostic Package (assim_AI)

**Author:** M. EL Aabaribaoune (@um6p)

This directory contains the **Random Forest diagnostic analysis pipeline** for the Noah-MP/LIS SMAP assimilation study. It has been integrated directly into the `NoahMP_Morocco` project structure to evaluate and diagnose soil moisture data assimilation.

---

## Directory Structure

### Code & Execution
- **`src/`**: Main Python source code, organized by pipeline steps:
  - **`preproc/`**: Scripts for data preparation, feature engineering, and validation.
  - **`main/`**: Scripts for model configuration and Random Forest training.
  - **`postproc/`**: Scripts for result visualization, plotting, and report generation.
  - **`utils/`**: Shared library code and helper functions.
- **`jobs/`**: Scripts for submitting jobs to the computing cluster.
- **`scratch/`**: Temporary scratch scripts used for quick tests, computations, and debugging.
- **`run_full_v0.sh`**: Main executable shell script to run the end-to-end diagnostic workflow.

### Data & Results
- **`data/`**: Input datasets, observations, and preprocessed feature files.
- **`outputs/`**: Model outputs, generated predictions, and intermediate processing files.
- **`logs/`**: Generated reports, visualization plots, and comprehensive analysis summaries.
- **`archive/`**: Archived experiments and legacy data/code.

### Configuration & Environment
- **`config.yaml`**: Main configuration file governing the parameters of the diagnostic pipeline.
- **`requirements.txt`**: Standard Python dependencies required for the project.
- **`environment.yml`**: Conda environment definition for reproducing the exact project setup.

---

## Quick Start

1. **Set up the environment:**
   You can create the environment using Conda:
   ```bash
   conda env create -f environment.yml
   conda activate <env_name> # Check environment.yml for the exact name
   ```
   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Pipeline:**
   Adjust the parameters in `config.yaml` to match your specific experiment settings, file paths, and model hyperparameters.

3. **Run the Analysis Pipeline:**
   Execute the full end-to-end diagnostic workflow using the provided bash script:
   ```bash
   ./run_full_v0.sh
   ```

---

## Pipeline Overview & Execution Details

The assimilation AI diagnostic pipeline is structured into three main phases:

### 1. Preprocessing (`src/preproc/`)
- **Scripts:** `01_build_dataset.py`, `05_validate_full_dataset.py`
- **Data Used:** Noah-MP and LIS SMAP historical data (OPL, DA_NoCDF, DA_CDF) and observational increments.
- **Output:** A cleaned and consolidated dataset saved at `data/processed/monthly_pixel_dataset.parquet`.

### 2. Main Training (`src/main/`)
- **Scripts:** `00_check_config.py`, `02_train_rf.py`
- **Action:** Trains Random Forest models for various targets (e.g., `increment_SSM_DA_NoCDF`, `delta_DA_NoCDF_minus_OPL_ET`).
- **Output Models:** The `.joblib` models are saved in the `models/` directory.

### 3. Post-Processing (`src/postproc/`)
- **Scripts:** `03_plot_results.py`, `04_export_summary.py`
- **Outputs Produced:**
  - **Metrics:** `results/metrics/rf_metrics.csv` (R², RMSE, Pearson scores) and `rf_feature_importance.csv`.
  - **Figures:** Saved in `results/figures/` (e.g., `rf_model_skill.png`, `rf_feature_importance.png`, `rf_increment_feature_importance.png`).
  - **Logs:** Markdown summaries exported to the `logs/` directory.

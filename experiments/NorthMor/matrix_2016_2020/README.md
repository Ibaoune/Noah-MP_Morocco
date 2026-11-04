# LIS/Noah-MP Data Assimilation (2016-2020)

This repository directory `matrix_2016_2020` contains a comprehensive 5-year experimental matrix for assimilating NASA SMAP soil moisture observations into the Noah-MP land surface model using LIS, targeting the period 2016 to 2020. 

## Scientific Justification
The transition from a 1-year analysis (2016) to a 5-year analysis (2016-2020) provides a much more robust framework for evaluating data assimilation performance:
* **Interannual Variability**: Encompasses both dry and wet climatological years, avoiding bias toward the specific meteorological conditions of a single year.
* **Robust CDF Matching**: By deriving the Cumulative Distribution Functions over 60 months instead of 12, the scaling of SMAP observations against the Open Loop (OPL) model climatology becomes significantly more robust and climatologically representative.

## Directory Organization

* **`OPL_noirr_2016_2020/`**: Open Loop (OPL) configuration. Runs the base model without irrigation or data assimilation to capture the model's unperturbed climatology.
* **`CDF/`**: LDT (Land Data Toolkit) scripts and configurations used to compute the Cumulative Distribution Functions for scaling SMAP observations to the OPL climatology.
* **`DA_nocdf_noirr_2016_2020/`**: Ensemble Kalman Filter (EnKF) assimilation of raw SMAP observations (no CDF matching, `CDF read option: 0`).
* **`DA_cdf_noirr_2016_2020/`**: EnKF assimilation of SMAP observations scaled via the computed 5-year CDF matching (`CDF read option: 1`).
* **`DA_anomaly_noirr_2016_2020/`**: EnKF assimilation using the anomaly scaling method proposed by Kwon et al. (2022) to directly assimilate SMAP anomalies, which preserves irrigation signals (`scaling strategy: "anomaly"`).

## Execution Workflow

To ensure a scientifically correct pipeline, these experiments **must** be executed sequentially.

### 1. Open Loop (OPL)
You must first generate the unperturbed states for the entire 2016-2020 period.
```bash
cd OPL_noirr_2016_2020
python3 scripts/chain_opl.py --current-date 2016-01-01 --submit
```
Wait for all 60 jobs (months) to finish successfully.

### 2. CDF Generation
Once the OPL is completed, navigate to the `CDF` directory to symlink the 60 months of outputs and run LDT to compute the observation scaling parameters.
```bash
cd CDF
sbatch run_cdf.sh
```
Wait for the CDF generation job to complete and confirm `smap_model_cdf.nc` and `smap_obs_cdf.nc` are generated in the corresponding output folders.

### 3. Data Assimilation (DA)
Finally, you can launch the DA experiments. These can run in parallel since they are independent.
```bash
cd DA_nocdf_noirr_2016_2020
python3 scripts/chain_da.py --current-date 2016-01-01 --submit

cd ../DA_cdf_noirr_2016_2020
python3 scripts/chain_da.py --current-date 2016-01-01 --submit

cd ../DA_anomaly_noirr_2016_2020
python3 scripts/chain_da.py --current-date 2016-01-01 --submit
```

## Important Notes & Pitfalls

> [!WARNING]
> **Disk Space:** A 5-year run of 20 ensemble members generates a massive amount of data. Ensure your Lustre quota is sufficient before starting.

> [!NOTE]
> **Spin-Up Consistency:** The 5-year period still starts at `2016-01-01`, meaning the restart files obtained from the previous long-term spin-up remain completely valid and are correctly pointed to by the daisy-chain scripts.

> [!IMPORTANT]
> **Cluster Wall-Time:** The daisy-chaining script (`chain_*.py`) submits the experiment month-by-month. This is an intentional design choice to bypass cluster maximum wall-time limits (e.g., 12 hours) and ensure the 5-year pipeline executes without premature termination.

#!/bin/bash
set -e

BASE_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
CDF_DIR="${BASE_DIR}/experiments/NorthMor/matrix_2016_2020/CDF"

cd "${CDF_DIR}"
mkdir -p OUTPUT_obs_NorthMor_2016_2019
mkdir -p OUTPUT_model_NorthMor_2016_2019

source "${BASE_DIR}/arch/arch_toubkal.env"

LDT_BIN="${BASE_DIR}/src/lisf/ldt/LDT"

echo "=== [$(date)] 1/2: Starting LDT for Observations (2016-2019) ==="
"${LDT_BIN}" ldt.config.cdf.obs.NorthMor.2016_2019
echo "=== [$(date)] 1/2: LDT Observation CDF Complete ==="

echo "=== [$(date)] 2/2: Starting LDT for Model (2016-2019) ==="
"${LDT_BIN}" ldt.config.cdf.model.NorthMor.2016_2019
echo "=== [$(date)] 2/2: LDT Model CDF Complete ==="
echo "=== [$(date)] ALL LDT CDF GENERATION 2016-2019 FINISHED SUCCESSFULLY ==="

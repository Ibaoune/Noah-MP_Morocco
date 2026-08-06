#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
MODULE_DIR="$PROJECT_ROOT/scripts/postproc/src/runoff_partitioning"

cd "$MODULE_DIR"

python main.py \
  --matrix matrix_2016 \
  --experiments OPL_noirr_2016 DA_nocdf_noirr_2016 \
  --year 2016 \
  --config config_runoff_partitioning.yaml \
  --output-root "$PROJECT_ROOT/scripts/postproc/figures" \
  --table-root "$PROJECT_ROOT/scripts/postproc/tables" \
  --log-root "$PROJECT_ROOT/scripts/postproc/logs"

#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

set -euo pipefail

# ======================================================
# Job: Domain plots
# Matrix: matrix_2016
# Year: 2016
# ======================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
MODULE_DIR="$PROJECT_ROOT/scripts/postproc/src/domain"

cd "$MODULE_DIR"

python main.py \
  --matrix matrix_2016 \
  --year 2016 \
  --config config_domain.yaml \
  --output-root "$PROJECT_ROOT/scripts/postproc/figures" \
  --table-root "$PROJECT_ROOT/scripts/postproc/tables" \
  --log-root "$PROJECT_ROOT/scripts/postproc/logs"

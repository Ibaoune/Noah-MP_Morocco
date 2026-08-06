#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
MODULE_DIR="$PROJECT_ROOT/scripts/postproc/src/figure_export"

cd "$MODULE_DIR"

python main.py \
  --matrix matrix_2016 \
  --figure-set ahmad_2016 \
  --year 2016 \
  --manifest ahmad_2016_manifest.yaml \
  --figures-root "$PROJECT_ROOT/scripts/postproc/figures" \
  --export-root "$PROJECT_ROOT/scripts/postproc/exports"

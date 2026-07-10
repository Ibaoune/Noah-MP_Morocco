#!/bin/bash
# run_all_local.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname $(dirname $SCRIPT_DIR))"
CONFIGS_DIR="$PROJECT_ROOT/configs/postproc/hydrology_visuals"

for config in "$CONFIGS_DIR"/*.yaml; do
    if [ -f "$config" ]; then
        echo "======================================"
        echo "Processing $config"
        echo "======================================"
        bash "$SCRIPT_DIR/run_one_hydro_variable.sh" "$config"
    fi
done

echo "All variables processed locally."

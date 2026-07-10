#!/bin/bash
# run_one_hydro_variable.sh
# Usage: ./run_one_hydro_variable.sh <path_to_yaml_config>

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_yaml_config>"
    exit 1
fi

CONFIG_FILE=$1
echo "Running post-processing for $CONFIG_FILE"

# Make sure we use the right python environment (if applicable, e.g. conda activate myenv)
# For now, just run python
python scripts/postproc/scripts/run_hydrology_postproc.py --config "$CONFIG_FILE"

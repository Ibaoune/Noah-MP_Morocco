#!/bin/bash
# submit_all_hydrology.sh
# Example SLURM submission loop. Adjust #SBATCH params as needed.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname $(dirname $SCRIPT_DIR))"
CONFIGS_DIR="$PROJECT_ROOT/configs/postproc/hydrology_visuals"

for config in "$CONFIGS_DIR"/*.yaml; do
    if [ -f "$config" ]; then
        var_name=$(basename "$config" .yaml)
        echo "Submitting job for $var_name"
        
        # We wrap run_one_hydro_variable.sh in a sbatch call, e.g.:
        # sbatch -J "hydro_$var_name" -o "logs/${var_name}_%j.out" -e "logs/${var_name}_%j.err" \
        #   "$SCRIPT_DIR/run_one_hydro_variable.sh" "$config"
        
        # As a placeholder if not using slurm, we just run sequentially or in background
        # bash "$SCRIPT_DIR/run_one_hydro_variable.sh" "$config" &
        
        # Here we just output what would be run:
        cat <<EOF | sbatch
#!/bin/bash
#SBATCH --job-name=hydro_${var_name}
#SBATCH --output=${SCRIPT_DIR}/logs/hydro_${var_name}_%j.out
#SBATCH --error=${SCRIPT_DIR}/logs/hydro_${var_name}_%j.err
#SBATCH --time=01:00:00
#SBATCH --mem=4G

cd $PROJECT_ROOT
bash "$SCRIPT_DIR/run_one_hydro_variable.sh" "$config"
EOF
    fi
done

echo "All jobs submitted."

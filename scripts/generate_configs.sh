#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Generate LIS configs for 3-day scalability tests
# Each config is a copy of the original but with:
#   - End date = Jun 04 2020 (3 days)
#   - Different processor layouts (up to 32 tasks per node, max 28 nodes)
#   - Max 32 procs per node (avoid memory/system saturation)

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$BASEDIR/configs/scalability"
OUTPUT_DIR="$BASEDIR/experiments/scalability"

mkdir -p "$CONFIG_DIR"
mkdir -p "$OUTPUT_DIR"

# ============================================================
# Processor layouts to test (npx × npy = total MPI tasks)
# Max 32 procs per node to leave headroom for memory & OS
# Grid size is 200x150, so npx <= 200 and npy <= 150
# ============================================================
# Format: "npx npy nodes label"
LAYOUTS=(
    "2 2 1 4tasks_1node"
    "4 4 1 16tasks_1node"
    "4 8 1 32tasks_1node"
    "8 8 2 64tasks_2nodes"
    "8 16 4 128tasks_4nodes"
    "16 16 8 256tasks_8nodes"
    "16 32 16 512tasks_16nodes"
    "32 28 28 896tasks_28nodes"
)

echo "============================================="
echo "Generating scalability test configs"
echo "============================================="

# ---- OPL configs ----
for layout in "${LAYOUTS[@]}"; do
    read -r npx npy nodes label <<< "$layout"
    total=$((npx * npy))
    
    outname="lis.config.opl.${label}"
    echo "  OPL: $outname (${npx}x${npy} = ${total} tasks on ${nodes} node(s))"
    
    sed -e "s/^Ending month:.*/Ending month:                           06/" \
        -e "s/^Ending day:.*/Ending day:                             04/" \
        -e "s/^Ending hour:.*/Ending hour:                            00/" \
        -e "s/^Ending minute:.*/Ending minute:                          00/" \
        -e "s/^Number of processors along x:.*/Number of processors along x:           ${npx}/" \
        -e "s/^Number of processors along y:.*/Number of processors along y:           ${npy}/" \
        -e "s|^Output directory:.*|Output directory:                       \"$OUTPUT_DIR/OPL_${label}\"|" \
        -e "s|^Diagnostic output file:.*|Diagnostic output file:                 \"$OUTPUT_DIR/OPL_${label}/lislog\"|" \
        -e 's|./input/forcing_variables.txt|./configs/forcing_variables.txt|' \
        -e 's|./input/noah_2dparms/|./data/land_params/noah_2dparms/|g' \
        -e 's|./lis_input.d01.nc|./data/lis_input.d01.nc|g' \
        -e 's|./input/MET_FORCING/MERRA2/|./data/met_forcing/MERRA2/|' \
        -e "s|'./MODEL_OUTPUT_LIST.TBL'|'./configs/MODEL_OUTPUT_LIST.TBL'|" \
        -e 's|./input/LS_PARAMETERS/noahmp_parms/|./data/land_params/noah_2dparms/|g' \
        "$BASEDIR/configs/lis.config.opl" > "$CONFIG_DIR/$outname"
done

# ---- DA configs ----
for layout in "${LAYOUTS[@]}"; do
    read -r npx npy nodes label <<< "$layout"
    total=$((npx * npy))
    
    outname="lis.config.da.${label}"
    echo "  DA:  $outname (${npx}x${npy} = ${total} tasks on ${nodes} node(s))"
    
    sed -e "s/^Ending month:.*/Ending month:                           06/" \
        -e "s/^Ending day:.*/Ending day:                             04/" \
        -e "s/^Ending hour:.*/Ending hour:                            00/" \
        -e "s/^Ending minute:.*/Ending minute:                          00/" \
        -e "s/^Number of processors along x:.*/Number of processors along x:           ${npx}/" \
        -e "s/^Number of processors along y:.*/Number of processors along y:           ${npy}/" \
        -e "s|^Output directory:.*|Output directory:                       \"$OUTPUT_DIR/DA_${label}\"|" \
        -e "s|^Diagnostic output file:.*|Diagnostic output file:                 \"$OUTPUT_DIR/DA_${label}/lislog\"|" \
        -e 's|./input/forcing_variables.txt|./configs/forcing_variables.txt|' \
        -e 's|./input/noah_2dparms/|./data/land_params/noah_2dparms/|g' \
        -e 's|./lis_input.d01.nc|./data/lis_input.d01.nc|g' \
        -e 's|./input/MET_FORCING/MERRA2/|./data/met_forcing/MERRA2/|' \
        -e 's|./input/pert_package/|./data/pert_package/|g' \
        -e 's|./input/RS_DATA/SMAP/SPL3SMP.009|./data/observations/SMAP/SPL3SMP.009|' \
        -e "s|'./MODEL_OUTPUT_LIST.TBL'|'./configs/MODEL_OUTPUT_LIST.TBL'|" \
        -e 's|./input/LS_PARAMETERS/noahmp_parms/|./data/land_params/noah_2dparms/|g' \
        "$BASEDIR/configs/lis.config.da" > "$CONFIG_DIR/$outname"
done

echo ""
echo "Done! Configs generated in: $CONFIG_DIR/"
echo "Output will go to: $OUTPUT_DIR/"

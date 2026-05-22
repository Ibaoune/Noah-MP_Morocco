#!/bin/bash
# Generate LIS configs for 3-day scalability tests
# Each config is a copy of the original but with:
#   - End date = Jun 04 2020 (3 days)
#   - Different processor layouts
#   - Max 32 procs per node (avoid memory/system saturation)

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
TESTDIR="$BASEDIR/scalability_test"

mkdir -p "$TESTDIR/configs"
mkdir -p "$TESTDIR/output"

# ============================================================
# Processor layouts to test (npx × npy = total MPI tasks)
# Max 32 procs per node to leave headroom for memory & OS
# ============================================================
# Format: "npx npy nodes label"
LAYOUTS=(
    "2 2 1 4tasks_1node"
    "4 4 1 16tasks_1node"
    "4 8 1 32tasks_1node"
    "8 8 2 64tasks_2nodes"
    "8 16 4 128tasks_4nodes"
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
        -e "s|^Output directory:.*|Output directory:                       \"$TESTDIR/output/OPL_${label}\"|" \
        -e "s|^Diagnostic output file:.*|Diagnostic output file:                 \"$TESTDIR/output/OPL_${label}/lislog\"|" \
        "$BASEDIR/lis.config.opl" > "$TESTDIR/configs/$outname"
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
        -e "s|^Output directory:.*|Output directory:                       \"$TESTDIR/output/DA_${label}\"|" \
        -e "s|^Diagnostic output file:.*|Diagnostic output file:                 \"$TESTDIR/output/DA_${label}/lislog\"|" \
        "$BASEDIR/lis.config.da" > "$TESTDIR/configs/$outname"
done

echo ""
echo "Done! Configs generated in: $TESTDIR/configs/"
echo "Output will go to: $TESTDIR/output/"

#!/bin/bash
#SBATCH --job-name=chk_yr
#SBATCH --output=logs/chk_yr_%A_%a.out
#SBATCH --error=logs/chk_yr_%A_%a.err
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32

YEAR=$1

if [ -z "$YEAR" ]; then
    echo "ERROR: YEAR argument not provided."
    exit 1
fi

echo "Starting verification for year $YEAR..."
module load Anaconda3/2020.11
export PYTHONNOUSERSITE=1

python3 check_single_year.py $YEAR
STATUS=$?

if [ $STATUS -eq 0 ]; then
    echo "Verification for $YEAR passed!"
    touch status_${YEAR}.success
else
    echo "Verification for $YEAR failed."
    rm -f status_${YEAR}.success
    exit 1
fi

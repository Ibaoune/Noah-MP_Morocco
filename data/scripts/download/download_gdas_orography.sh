#!/bin/bash
# ==============================================================================
# Script to download GDAS orography file for LIS lapse-rate topographic correction
# ==============================================================================

set -e

# Get the script's current directory and resolve the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Assuming script is in data/scripts/download
TARGET_DIR="${SCRIPT_DIR}/../../forcing/GDAS"
mkdir -p "$TARGET_DIR"

# NCCS NASA LIS parameter download URL for GDAS T574 global orography
# This file is required when 'lapse-rate' correction is enabled for GDAS forcing in LIS.
URL="https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS/NCEP_Native/GDAS/global_orography.t574.grb"

FILE_PATH="${TARGET_DIR}/global_orography.t574.grb"

echo "Downloading GDAS T574 global orography..."
echo "Source: $URL"
echo "Destination: $FILE_PATH"

# Download the file
wget -c "$URL" -O "$FILE_PATH"

echo "Download complete."
echo "Please ensure your lis.config has the following lines under FORCINGS:"
echo "GDAS T574 elevation map:  ./data/forcing/GDAS/global_orography.t574.grb"
echo "Topographic correction method (met forcing):  \"lapse-rate\" \"none\""

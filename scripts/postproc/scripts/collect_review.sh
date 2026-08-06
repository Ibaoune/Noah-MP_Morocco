#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
set -e

# Move to the postproc root directory
cd "$(dirname "$0")/.."

SOURCE_ROOT="outputs/matrix_2016/figures/smap_cdf_sensitivity/independent_obs_validation"
REVIEW_DIR="outputs/matrix_2016/figures/smap_cdf_sensitivity/independent_obs_validation_review"
MANIFEST="${REVIEW_DIR}/manifest.txt"
PDF_FILE="outputs/matrix_2016/figures/smap_cdf_sensitivity/smap_cdf_sensitivity_2016_report_v2.pdf"

mkdir -p "${REVIEW_DIR}"
echo "Manifest for Independent Observation Validation Review" > "${MANIFEST}"
echo "======================================================" >> "${MANIFEST}"

# Helper function to copy and log a file
copy_and_log() {
    local fname=$1
    local src_dir=$2
    local obs_type=$3
    local var_type=$4

    local src_file="${SOURCE_ROOT}/${src_dir}/${fname}"
    local dest_file="${REVIEW_DIR}/${fname}"
    local json_file="${SOURCE_ROOT}/${src_dir}/${fname%.png}.json"
    
    if [ -f "${src_file}" ]; then
        cp "${src_file}" "${dest_file}"
        local file_size=$(stat -c%s "${src_file}")
        local file_date=$(stat -c%y "${src_file}")
        local has_json="No"
        
        if [ -f "${json_file}" ]; then
            cp "${json_file}" "${REVIEW_DIR}/"
            has_json="Yes"
        fi
        
        echo -e "\nFile: ${fname}" >> "${MANIFEST}"
        echo "Source: ${src_file}" >> "${MANIFEST}"
        echo "Size: ${file_size} bytes" >> "${MANIFEST}"
        echo "Date Modified: ${file_date}" >> "${MANIFEST}"
        echo "Has JSON: ${has_json}" >> "${MANIFEST}"
        echo "Observation Type: ${obs_type}" >> "${MANIFEST}"
        echo "Variable: ${var_type}" >> "${MANIFEST}"
    else
        echo "WARNING: Expected file not found: ${src_file}"
        echo "${fname}" >> missing_files.txt
    fi
}

rm -f missing_files.txt

# Soil Moisture
copy_and_log "SM-01_Data_Coverage.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"
copy_and_log "SM-02_Annual_Mean_and_Bias.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"
copy_and_log "SM_timeseries_corrected.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"
copy_and_log "SM-04_Pooled_Scatterplots.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"
copy_and_log "SM-05_Spatial_Bias.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"
copy_and_log "SM-05_Spatial_RMSE.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"
copy_and_log "SM-06_Assimilation_Skill.png" "soil_moisture/esa_cci_combined/NorthMor" "ESA CCI Combined" "Soil Moisture"

# Evapotranspiration
copy_and_log "ET_mean_maps_corrected.png" "evapotranspiration/gleam" "GLEAM" "Evapotranspiration"
copy_and_log "ET_timeseries_corrected.png" "evapotranspiration/gleam" "GLEAM" "Evapotranspiration"

# Vegetation
copy_and_log "VG-02_Mean_Vegetation_corrected.png" "vegetation/fluxsat_gpp" "FluxSat GPP" "Vegetation"
copy_and_log "VG-03_Time_Series_corrected.png" "vegetation/fluxsat_gpp" "FluxSat GPP" "Vegetation"

# Water Storage
copy_and_log "TWS_mean_maps_corrected.png" "water_storage/grace" "GRACE" "Water Storage"
copy_and_log "TWS_timeseries_corrected.png" "water_storage/grace" "GRACE" "Water Storage"

# Copy PDF
if [ -f "${PDF_FILE}" ]; then
    cp "${PDF_FILE}" "${REVIEW_DIR}/"
    echo -e "\nFile: $(basename ${PDF_FILE})" >> "${MANIFEST}"
    echo "Source: ${PDF_FILE}" >> "${MANIFEST}"
    echo "Size: $(stat -c%s ${PDF_FILE}) bytes" >> "${MANIFEST}"
    echo "Date Modified: $(stat -c%y ${PDF_FILE})" >> "${MANIFEST}"
else
    echo "WARNING: PDF not found: ${PDF_FILE}"
    echo "$(basename ${PDF_FILE})" >> missing_files.txt
fi

# Create archive
cd "outputs/matrix_2016/figures/smap_cdf_sensitivity"
tar -czf independent_obs_validation_review.tar.gz independent_obs_validation_review
cd - > /dev/null

echo "Archive created successfully."

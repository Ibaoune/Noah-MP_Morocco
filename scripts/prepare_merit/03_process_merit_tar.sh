#!/bin/bash
# Script: 03_process_merit_tar.sh
# Description: Extrait les tuiles 5x5 depuis les archives .tar, les fusionne et les convertit.

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/merit_hydro
mkdir -p extracted

# Chargement des modules requis
module load foss/2024a GDAL NCO netCDF/4.9.2-gompi-2024a
source /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/arch/arch_toubkal.env

echo "1. Extraction des archives .tar..."
for tarfile in *.tar; do
    echo "Extraction de $tarfile..."
    tar -xf "$tarfile" -C extracted/
done

cd extracted
# Déplacer tous les tif à la racine de extracted/
mv */*.tif . 2>/dev/null || true

mkdir -p merged
echo "2. Fusion des tuiles avec gdal_merge.py..."

# Variables et suffixes correspondants dans les noms de fichiers extraits
declare -A vars=(
    ["dir"]="_dir.tif"
    ["elev"]="_elv.tif"
    ["uparea"]="_upa.tif"
    ["width"]="_wth.tif"
)

for var_name in "${!vars[@]}"; do
    suffix=${vars[$var_name]}
    
    # Chercher les 4 tuiles pour cette variable
    # ex: n30w010_dir.tif, n30w005_dir.tif, etc.
    # Dans les archives, le nom est parfois n30w010_dir.tif
    files_to_merge=""
    for tile in "n30w010" "n30w005" "n35w010" "n35w005"; do
        if [ -f "${tile}${suffix}" ]; then
            files_to_merge="$files_to_merge ${tile}${suffix}"
        else
            echo "Attention: tuile ${tile}${suffix} manquante !"
        fi
    done
    
    if [ ! -z "$files_to_merge" ]; then
        echo "Fusion pour $var_name..."
        gdal_merge.py -o "merged/merged_${var_name}.tif" -n -9999 -a_nodata -9999 $files_to_merge
        
        echo "Conversion en NetCDF pour $var_name..."
        gdal_translate -of NetCDF "merged/merged_${var_name}.tif" "merged/${var_name}_tmp.nc"
        ncrename -v Band1,"$var_name" "merged/${var_name}_tmp.nc" "merged/${var_name}.nc"
        rm "merged/${var_name}_tmp.nc"
    fi
done

# 3. Calcul de la longueur de flux avec le script python
echo "3. Exécution du calcul de longueur de canal..."
cp ../../../scripts/prepare_merit/02_calc_flow_length.py merged/
cd merged
python 02_calc_flow_length.py

# 4. Déplacement vers le répertoire final
echo "4. Déplacement vers data/land_params/topo_parms/MERIT..."
MERIT_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/land_params/topo_parms/MERIT"
mkdir -p $MERIT_DIR
cp dir.nc uparea.nc elev.nc width.nc flw_len.nc $MERIT_DIR/

echo "Opération terminée avec succès !"

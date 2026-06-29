#!/bin/bash
# Script: 01_convert_merit_to_nc.sh
# Description: Convertit les fichiers MERIT GeoTIFF en NetCDF et renomme les variables internes.
# Prérequis: gdal, nco

# Assurez-vous que les modules nécessaires sont chargés, ex:
# module load GDAL NCO

# Liste des fichiers et de leurs variables correspondantes pour LDT
declare -A files=(
    ["w030n30_dir.tif"]="dir"
    ["w030n30_uparea.tif"]="uparea"
    ["w030n30_elev.tif"]="elev"
    ["w030n30_width.tif"]="width"
)

echo "Début de la conversion des GeoTIFF en NetCDF..."

for tif in "${!files[@]}"; do
    var_name=${files[$tif]}
    out_nc="${var_name}.nc"
    tmp_nc="tmp_${out_nc}"

    if [ -f "$tif" ]; then
        echo "Traitement de $tif -> $out_nc (variable: $var_name)"
        
        # 1. Convertir TIFF en NetCDF avec GDAL
        gdal_translate -of NetCDF "$tif" "$tmp_nc" > /dev/null
        
        # 2. Renommer la variable Band1 par défaut en nom de variable LDT
        ncrename -v Band1,"$var_name" "$tmp_nc" "$out_nc"
        
        # Nettoyage
        rm "$tmp_nc"
    else
        echo "Attention: Fichier $tif non trouvé dans le répertoire courant."
    fi
done

echo "Conversion terminée."

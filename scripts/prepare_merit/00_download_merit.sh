#!/bin/bash
# Script: 00_download_merit.sh
# Description: Télécharge les tuiles MERIT Hydro (dir, uparea, elev, width)
# Note: Remplacez USERNAME et PASSWORD par vos identifiants MERIT Hydro.

USERNAME="VOTRE_NOM_UTILISATEUR"
PASSWORD="VOTRE_MOT_DE_PASSE"

# Tuile correspondant au Maroc (Nord-Ouest) - Vérifiez le nom exact sur la carte MERIT
TILE="n30w030" 
VERSION="v1.0.1"

BASE_URL="http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/${VERSION}"

echo "Téléchargement des fichiers GeoTIFF MERIT Hydro pour la tuile ${TILE}..."

for var in dir uparea elev width; do
    # L'URL typique est: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/v1.0.1/dir/n30w030_dir.tif
    FILE="${TILE}_${var}.tif"
    URL="${BASE_URL}/${var}/${FILE}"
    
    echo "Téléchargement de $FILE..."
    wget --user="$USERNAME" --password="$PASSWORD" "$URL"
    
    if [ $? -eq 0 ]; then
        echo "✅ $FILE téléchargé avec succès."
    else
        echo "❌ Échec du téléchargement de $FILE."
    fi
done

echo "Opération terminée."

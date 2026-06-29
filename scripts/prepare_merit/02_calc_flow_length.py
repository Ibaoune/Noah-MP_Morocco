#!/usr/bin/env python3
# Script: 02_calc_flow_length.py
# Description: Calcule la longueur du flux (flw_len) à partir de la direction (dir.nc).
# Prérequis: xarray, numpy, netCDF4

import xarray as xr
import numpy as np
import os

print("Calcul de la longueur du canal (flw_len.nc)...")

if not os.path.exists("dir.nc"):
    raise FileNotFoundError("Le fichier dir.nc est introuvable. Veuillez exécuter le script bash de conversion d'abord.")

# Charger la direction de flux
ds_dir = xr.open_dataset("dir.nc")

# MERIT utilise souvent x et y, ou lon et lat. On suppose x=lon, y=lat venant de GDAL
lon = ds_dir.lon if 'lon' in ds_dir.coords else ds_dir.x
lat = ds_dir.lat if 'lat' in ds_dir.coords else ds_dir.y
direction = ds_dir['dir'].values

# Constantes pour la Terre
R_EARTH = 6371000.0  # Rayon de la terre en mètres

# Résolution spatiale de MERIT Hydro (3 arc-seconds = ~0.0008333 degrés)
dlon = np.abs(lon.values[1] - lon.values[0])
dlat = np.abs(lat.values[1] - lat.values[0])

# Convertir les différences de degrés en radians
dlon_rad = np.radians(dlon)
dlat_rad = np.radians(dlat)

# Calculer les distances dx et dy pour chaque pixel (dx dépend de la latitude)
# Broadcasting de la latitude sur toute la grille 2D
lat_rad = np.radians(lat.values)
lat_2d = lat_rad[:, np.newaxis] # Forme (Y, 1) pour un broadcast sur (Y, X)

# Distance orthogonale
dx = R_EARTH * np.cos(lat_2d) * dlon_rad  # Longueur E-W (dépend de la latitude)
dy = R_EARTH * dlat_rad                   # Longueur N-S (constante)

# Distance diagonale
diag_dist = np.sqrt(dx**2 + dy**2)

# Convention des directions D8 pour MERIT (ESRI)
# 1: Est, 2: Sud-Est, 4: Sud, 8: Sud-Ouest, 16: Ouest, 32: Nord-Ouest, 64: Nord, 128: Nord-Est
# On initialise un tableau pour la longueur de flux avec des NaN ou des 0
flw_len = np.zeros_like(direction, dtype=np.float32)

# Appliquer les distances orthogonales
flw_len = np.where(np.isin(direction, [1, 16]), dx, flw_len)
flw_len = np.where(np.isin(direction, [4, 64]), dy, flw_len)

# Appliquer les distances diagonales
flw_len = np.where(np.isin(direction, [2, 8, 32, 128]), diag_dist, flw_len)

# Gérer les pixels sans flux (NoData ou océan)
# Dans MERIT, NoData est souvent 0 ou une valeur négative.
flw_len = np.where(direction <= 0, np.nan, flw_len)

# Créer un Dataset xarray pour flw_len
ds_flw_len = xr.Dataset(
    {
        "flw_len": (ds_dir['dir'].dims, flw_len)
    },
    coords=ds_dir.coords
)

# Ajouter des attributs
ds_flw_len["flw_len"].attrs = {
    "units": "meters",
    "long_name": "Flow routing length",
    "description": "Calculated based on MERIT Hydro D8 direction and geospatial resolution"
}

# Sauvegarder en NetCDF
ds_flw_len.to_netcdf("flw_len.nc")
print("Fichier flw_len.nc généré avec succès !")

# Inventaire et Provenance des Données d'Entrée — Projet NoahMP_Morocco

Ce document recense l'ensemble des données d'entrée (forçages météorologiques, observations satellitaires, paramètres de surface, définitions spatiales et tables CDF) utilisées par les simulations de production de **NoahMP_Morocco**.

Toutes les informations ci-dessous sont extraites directement des configurations LIS/LDT et des fichiers NetCDF de production du dépôt. Pour chaque jeu de données, le fichier de configuration source est explicitement cité.

---

## 1. Forçages Météorologiques

Le modèle fonctionne en forçage couplé bimoteur, combinant les réanalyses horaires atmosphériques de la NASA avec les précipitations satellitaires calibrées de la mission GPM :
* **Nombre de sources** : 2 (`Number of met forcing sources: 2`, `Met forcing sources: "MERRA2" "GPM IMERG"`)
  *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, lignes 17-18)*

### a. MERRA-2 (NASA GMAO)
* **Description** : Modern-Era Retrospective analysis for Research and Applications, Version 2.
* **Emplacement** : `./data/forcing/MERRA2/`
* **Options de configuration LIS** :
  - `MERRA2 use lowest model level forcing: 1`
  - `MERRA2 use corrected total precipitation: 1`
* *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, lignes 72-76)*

### b. GPM IMERG (NASA / JAXA)
* **Description** : Integrated Multi-satellitE Retrievals for GPM.
* **Emplacement** : `./data/forcing/IMERG/raw/`
* **Version du produit** : `'V07B'`
* **Type de traitement** : `'final'` (IMERG Final Run calibré avec jauges)
* *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, lignes 78-80)*

---

## 2. Observations Satellitaires d'Assimilation (SMAP)

* **Mission & Capteur** : Soil Moisture Active Passive (SMAP) radiomètre bande L.
* **Produit** : Niveau 3 Enhanced Soil Moisture (L3_SM_P_E / SPL3SMP_E) grillage 9 km EASE-2.
* **Emplacement local** : `./data/observations/SMAP_SPL3SMP_E/`
* **Fichier de liste d'observation dynamique** : `SMAP_filelist.dat` (généré et actualisé par LIS au cours du run).
* *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, ligne 116)*

---

## 3. Domaine Spatial et Fichier `lis_input`

* **Fichier domaine de référence** : `data/lis_input/lis_input_NorthMor_5km.nc`
  *(Variante irrigation : `data/lis_input/lis_input_NorthMor_5km_irr.nc`)*
* **Type de projection cartographique** : Cylindrique équidistante régulière (`MAP_PROJECTION: EQUIDISTANT CYLINDRICAL`)
* **Bornes géographiques** :
  - Coin Sud-Ouest : Latitude `30.0° N`, Longitude `-10.0° W` (`SOUTH_WEST_CORNER_LAT: 30.0`, `SOUTH_WEST_CORNER_LON: -10.0`)
  - Coin Nord-Est : Latitude `36.0° N`, Longitude `-1.0° W`
* **Résolution spatiale de maille** : `0.05°` × `0.05°` (~5 km) (`DX: 0.05`, `DY: 0.05`)
* **Dimensions de grille** : 181 colonnes (longitude) × 121 lignes (latitude) = 181 × 121 = 21 901 points.
* **Points continentaux actifs** : **16 030 points terre** (`LANDMASK == 1`, points océaniques exclus `INC_WATER_PTS: false`).
* *(Source : `data/lis_input/lis_input_NorthMor_5km.nc`, attributs globaux NetCDF)*

---

## 4. Propriétés du Sol et de la Végétation

* **Classification d'occupation du sol** : IGBP-NCEP à 20 classes (`LANDCOVER_SCHEME: IGBPNCEP`, bare soil class = 16, urban = 13, water = 17).
* **Source du masque terre/mer** : MODIS Native (`LANDMASK_SOURCE: MODIS_Native`).
* **Texture et caractéristiques du sol** : STATSGO à 19 classes (`SOILTEXT_SCHEME: STATSGO`, `NUMBER_SOILTYPES: 19`).
* *(Source : `data/lis_input/lis_input_NorthMor_5km.nc`, attributs globaux NetCDF)*
* **Tables de paramètres physiques Noah-MP 4.0.1** :
  - Paramètres de végétation : `./data/land_params/noahmp401_parms/VEGPARM.TBL`
  - Paramètres de sol : `./data/land_params/noahmp401_parms/SOILPARM.TBL`
  - Paramètres généraux : `./data/land_params/noahmp401_parms/GENPARM.TBL`
  - Options multiphysiques Noah-MP : `./data/land_params/noahmp401_parms/MPTABLE.TBL`
  - Épaisseur des 4 couches de sol : `0.1`, `0.3`, `0.6`, `1.0` m (profil total 2.0 m).
  - Couches de neige : 3 couches.
* *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, lignes 48-55)*

---

## 5. Schéma de Perturbation d'Ensemble

* **Nombre de membres d'ensemble** : 20 membres (`Number of ensembles per tile: 20`, soit $16\,030 \times 20 = 320\,600$ tuiles actives).
* **Algorithme de perturbation** : Schéma GMAO pour forçages, états et observations :
  - `Forcing perturbation algorithm: "GMAO scheme"` (Fréquence : `1hr`)
  - `State perturbation algorithm: "GMAO scheme"` (Fréquence : `3hr`)
  - `Observation perturbation algorithm: "GMAO scheme"` (Fréquence : `6hr`)
* **Tables d'attributs de perturbation** :
  - Forçages : `./data/pert_package/forcing_attribs.txt`, `./data/pert_package/forcing_pertattribs.txt`
  - États d'humidité du sol : `./data/pert_package/noahmp_sm_attribs.txt`, `./data/pert_package/noahmp_sm_pertattribs.txt`
  - Observations SMAP : `./data/pert_package/smap_attribs.txt`, `./data/pert_package/smap_pertattribs.txt`
* *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, lignes 86-105)*

---

## 6. Fichiers de Scaling CDF Matching

* **Algorithme d'assimilation** : Ensemble Kalman Filter (`Data assimilation algorithm: "EnKF"`)
* **Stratégie de mise à l'échelle** : CDF matching (`Data assimilation scaling strategy: "CDF matching"`)
* **Fichiers NetCDF de CDF** :
  - CDF Modèle : `./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc`
  - CDF Observation : `./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc`
  - Fichiers de domaine LDT associés : `noahmp_model_cdf_NorthMor_domain.nc`, `smap_obs_cdf_NorthMor_domain.nc`
* **Paramétrage des quantiles** :
  - `SMAP(NASA) soil moisture number of bins in the CDF: 100`
  - `SMAP(NASA) CDF read option: 1`
* *(Source : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/templates/lis_da.config.template`, lignes 112-120)*

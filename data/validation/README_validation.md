# Suivi du Téléchargement des Données de Validation

Ce document a pour objectif de documenter les données requises pour la validation du modèle Noah-MP sur la période **2015-2020**, et de suivre l'avancement des téléchargements au fur et à mesure.

## Objectif des données à télécharger
Les données de validation couvrent plusieurs composantes du cycle hydrologique et de la végétation. L'objectif est de comparer les résultats du modèle (simulations Open-Loop et avec Assimilation de Données) avec des observations satellitaires, in situ, et d'autres modèles (produits d'intercomparaison comme GLDAS).

Période d'étude requise : **2015-01-01 au 2020-12-31**.

---

## État d'avancement des téléchargements

*Cochez les cases `[x]` une fois que le téléchargement est confirmé complet pour la période 2015-2020.*

### 1. Données Complètes 
Ces données sont déjà téléchargées et couvrent l'intégralité de la période requise.
- [x] **GRACE / GRACE-FO TWSA** (`data/validation/water_storage/`) : Anomalies de stockage d'eau (TWSA).
- [x] **MODIS GPP MOD17A2HGF** (`data/validation/vegetation/GPP/`) : GPP 8-jours.
- [x] **MODIS LAI/FPAR** (`data/observations_archive/MODIS_LAI/raw`) : LAI 8-jours.
- [x] **GLDAS CLSM 1.0 3H** (`data/validation/lsm/GLDAS/GLDAS_CLSM10_3H`) : Modèle d'intercomparaison.
- [x] **GMIA** (`data/land_params/GMIA/`) : Carte des zones irriguées (donnée statique).

### 2. Données Partielles 
Ces données sont en cours de téléchargement ou ont été interrompues.
- [ ] **GLDAS NOAH 0.25 3H** (`data/validation/lsm/GLDAS/GLDAS_NOAH025_3H`) : S'arrête en juin 2018. 
  - *Action* : Relancer `submit_download_gldas.sh`.
- [ ] **FLUXSAT GPP v2** (`data/validation/vegetation/FLUXSAT_GPP/`) : Seulement 16 mois téléchargés sur les 72 requis. 
  - *Action* : Relancer `submit_download_fluxsat.sh`.

### 3. Données Manquantes 
Ces données n'ont pas encore été téléchargées ou nécessitent un nouveau script/traitement manuel.
- [ ] **WaPOR L2** (`data/validation/evapotranspiration/WaPOR/`) : ET, E, T, NPP. 
  - *Action* : Lancer `submit_download_wapor.sh`.
- [ ] **GLDAS VIC 1.0 & CLSM-DA1** (`data/validation/lsm/GLDAS/`) : Modèles d'intercomparaison.
  - *Action* : Lancer via `submit_download_gldas.sh`.
- [ ] **Streamflow ABHS** (`data/validation/streamflow/ABHS/`) : Débit in situ (journalier). 
  - *Action* : Uploader et formater les fichiers CSV/Excel manuellement.
- [ ] **Soil Moisture** (`data/validation/soil_moisture/`) : ESA CCI, ASCAT ou in situ. 
  - *Action* : Créer un script de téléchargement ou uploader les données in situ.
- [ ] **MODIS Land Cover MCD12Q1** : Couverture terrestre.
  - *Action* : Créer un script de téléchargement ou le télécharger manuellement.
- [ ] **IMERG Precipitation** : Produit de précipitation (si requis en plus du forçage MERRA-2).
  - *Action* : Vérifier la nécessité et créer le script le cas échéant.
- [ ] **Shapefiles Bassins/Stations** : Polylignes et polygones géospatiaux.
  - *Action* : Créer le dossier `data/shapefiles` et y uploader les fichiers `.shp`.

---

## Tableau de Synthèse des Produits

| Dossier | Dataset détecté | Variable(s) | Format | Résol. spatiale | Période dispo | Statut | Script associé |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `water_storage` | GRACE / GRACE-FO | TWSA | `.nc` | 0.5° | 2002-2026 |  Complet | Aucun (manuel) |
| `streamflow` | ABHS (in situ) | Débit | CSV/XLS | Stations | N/A |  Manquant | Aucun (manuel) |
| `soil_moisture` | ESA_CCI / SMAP | Humidité | N/A | N/A | N/A |  Manquant | À créer |
| `evapotranspiration`| WaPOR L2 | ET, E, T, NPP | `.tif`/`.nc`| 250m | N/A |  Manquant | `download_wapor.py` |
| `vegetation` | MODIS GPP | GPP | `.hdf` | 500m | 2015-2020 |  Complet | Aucun (manuel) |
| `vegetation` | FLUXSAT v2 | GPP | `.nc` | 0.05° | 2015-2019 (16 mois)|  Partiel | `download_fluxsat_gpp.py` |
| `vegetation` | MODIS LAI/FPAR | LAI, FPAR | `.hdf` | 500m | 2015-2020 |  Complet | `download_modis_mcd15a2h.py` |
| `lsm` | GLDAS CLSM 1.0 | SM, Q, ET | `.nc4` | 1.0° | 2015-2020 |  Complet | `download_gldas.py` |
| `lsm` | GLDAS NOAH 0.25 | SM, Q, ET | `.nc4` | 0.25° | 2015-2018 |  Partiel | `download_gldas.py` |
| `lsm` | GLDAS VIC / CLSM-DA| SM, Q, ET, TWSA| N/A | 1.0°/0.25° | N/A |  Manquant | `download_gldas.py` |
| Autres | GMIA | Zones irriguées | N/A | Statique | Statique |  Complet | `download_gmia.py` |
| Autres | MODIS Land Cover | Land cover | N/A | 500m | N/A |  Manquant | À créer |
| Autres | Shapefiles | Bassins | `.shp` | Statique | N/A |  Manquant | Manuel |

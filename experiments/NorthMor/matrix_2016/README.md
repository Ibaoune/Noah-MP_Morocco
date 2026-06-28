# Matrice d'Expériences 2016 (Validation Phase)

Ce répertoire (`matrix_2016`) est dédié à la validation de la configuration du modèle LIS/Noah-MP pour le domaine du Nord du Maroc, en se limitant strictement à l'année **2016**. 

L'objectif principal de cette étape est de valider le comportement du module d'irrigation, de calculer un CDF robuste et isolé sur une année pour l'assimilation de données SMAP, et de tester l'intégration de l'assimilation du LAI (MODIS MCD15A2H) avant de lancer la simulation finale couvrant la période 2016-2020.

## Structure et Expériences

Les expériences sont décomposées selon la logique suivante :

### 1. Open-Loop (OPL) - Les baselines
- **OPL_noirr** : Open-loop sans irrigation. L'irrigation est explicitement désactivée. Cette expérience sert de point de contrôle principal.
- **OPL_irr** : Open-loop avec irrigation activée via le schéma `Sprinkler`. 
  - **Détails Techniques** : Le module `Sprinkler` exige la présence de métadonnées spécifiques pour fonctionner. Nous avons dû :
    - Configurer des paramètres stricts (ex: `maxrootdepth32.txt`, `GVF1=0.40`, `GVF2=0.00`).
    - Injecter proprement la variable manquante `CROPTYPE` (via `ncap2 -A`) directement dans une copie du fichier de paramètres d'entrée (`lis_input_NorthMor_5km_irr.nc`). Sans cela, le run crashait systématiquement.
  - Ces deux OPL sont exécutés exclusivement sur l'année 2016. La date de fin de tous les `experiment.ini` est configurée sur `2017-01-01`.

### 2. Génération du CDF (Calculs de la climatologie SMAP)
Pour procéder à l'assimilation de données (DA) du produit SMAP `SPL3SMP_E`, nous avons besoin de calculer les fonctions de répartition empiriques (CDF) du modèle afin de réduire les biais par rapport à l'observation.
- **Chemin** : `CDF/`
- Les fichiers LIS history étant générés mois par mois (`2016-01`, `2016-02`, etc.), le logiciel LDT a besoin d'un répertoire regroupé pour le calcul du CDF.
- Le script `run_cdf.sh` a été écrit pour automatiser deux choses :
  1. Créer des liens symboliques consolidant les historiques mensuels dans `combined_OPL_irr` et `combined_OPL_noirr`.
  2. Exécuter l'outil `LDT` avec deux configurations distinctes :
     - `ldt.config.cdf.noirr` : Génère `smap_cdf_noirr.nc`
     - `ldt.config.cdf.irr` : Génère `smap_cdf_irr.nc`
- **Attention** : Ces CDFs doivent être générés manuellement via `sbatch run_cdf.sh` *uniquement après* la fin complète des runs OPL 2016.

### 3. Data Assimilation (DA)
Une fois les OPL validés et les CDF générés, le dossier contiendra les expériences d'assimilation de données (préparées via le script `setup_da.sh`) :
- **DA_nocdf_noirr** : Assimilation SMAP EnKF, sans CDF matching, sans irrigation.
- **DA_cdf_noirr** : Assimilation SMAP EnKF, avec CDF matching, sans irrigation.
- **DA_nocdf_irr** : Assimilation SMAP EnKF, sans CDF matching, avec irrigation.
- **DA_cdf_irr** : Assimilation SMAP EnKF, avec CDF matching, avec irrigation.

### 4. Assimilation LAI (MCD15A2H) - À venir
Un test d'assimilation des données LAI MODIS (produit `MCD15A2H` version 6) sera également intégré.
- **Analyse technique** : Nous avons identifié la configuration native requise dans LIS 7.4. L'assimilation se déclarera ainsi dans le `lis.config` :
  ```ini
  Data assimilation set:                 "MCD15A2H LAI"
  MCD15A2H LAI data directory:           ../../../../data/observations_archive/MODIS_MCD15A2H/raw/
  MCD15A2H LAI data version:             "006"
  MCD15A2H LAI apply temporal smoother between 8-day intervals: 1
  MCD15A2H LAI apply climatological fill values:                0
  MCD15A2H LAI apply QC flags:                                  1
  ```
  *(La valeur `climatological fill values` est réglée à 0 dans un premier temps afin d'éviter les erreurs liées à l'absence d'un fichier de climatologie manuel).*

## Résumé de la chaine d'exécution
1. Attendre que `OPL_irr` et `OPL_noirr` finissent 2016.
2. Aller dans `CDF/` et lancer `sbatch run_cdf.sh`.
3. Préparer les répertoires DA_LAI via un script de setup mis à jour.
4. Lancer les chaînes DA (`chain_da.py`).

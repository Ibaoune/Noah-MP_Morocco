# LIS Noah-MP 3-Day Tests: Troubleshooting & Bug Fixes

Ce document répertorie tous les blocages rencontrés lors de la configuration et de l'exécution des tests Open-Loop (OPL) et d'assimilation de données (EnKF) pour Noah-MP 4.0.1 sur le cluster Toubkal, ainsi que les solutions apportées.

## 1. Erreur de Forçages MERRA2 Introuvables (Liens Symboliques Brisés)

**Symptôme :**
Le modèle s'arrête avec l'erreur : `[ERR] ./data/forcing/MERRA2//MERRA2_400/Y2020/M02/MERRA2_400.tavg1_2d_slv_Nx.20200201.nc4 does not exist`

**Cause :**
Le dossier racine des forçages avait été renommé de `data/met_forcing` à `data/forcing`. Tous les fichiers à l'intérieur de `MERRA2_400` étaient des liens symboliques pointant vers l'ancien chemin (désormais inexistant).

**Solution :**
Une commande a été exécutée pour mettre à jour en masse tous les liens symboliques afin qu'ils pointent vers le nouveau chemin `data/forcing/MERRA2/M2T1NXSLV/`.

---

## 2. Erreurs d'Attributs de Sortie (Variables non supportées par Noah-MP 4.0.1)

**Symptôme :**
Crash lors de la tentative d'écriture du premier fichier NetCDF avec le message d'erreur :
`[ERR] RootMoist field is not defined for diagnostic output... Please exclude it from the model output attributes table`
(Même erreur pour d'autres variables comme `total_living_biomass_carbon_content`).

**Cause :**
Le fichier `./experiments/reference/configs/MODEL_OUTPUT_LIST.TBL` demandait au modèle de sortir des variables (comme `RootMoist`, `GPP`, `NPP`, `TotLivBiom`) qui n'existent pas ou ne sont pas calculées par défaut dans cette version spécifique de Noah-MP au sein de LIS.

**Solution :**
Ces variables ont été désactivées (passées de `1` à `0`) dans le fichier `MODEL_OUTPUT_LIST.TBL`.

---

## 3. Segmentation Fault Immédiat (Erreur d'Algorithme DA)

**Symptôme :**
Le run Data Assimilation (DA) crashe immédiatement (signal 11) après l'affichage de la configuration physique de Noah-MP (`urban physics: 0`).

**Cause :**
Dans les fichiers de configuration, la variable `Data assimilation algorithm:` était réglée sur `"1D EnKF"`. Or, les plugins internes de LIS s'attendent strictement à la chaîne de caractères `"EnKF"`. Cette divergence empêchait l'initialisation du module d'assimilation et provoquait un crash mémoire (Null pointer dereference) lorsqu'il essayait de lire le pointeur de l'algorithme.

**Solution :**
Remplacement de `"1D EnKF"` par `"EnKF"` dans les fichiers `lis_da_smap.config`, `lis_da_lai.config` et `lis_da_joint.config`.

---

## 4. Crashs de Plugins d'Observation (Noms d'Ensembles Erronés)

**Symptôme :**
Un crash silencieux (ou MPI Abort) se produit lors du paramétrage des observations après avoir passé l'étape précédente.

**Cause :**
Tout comme pour l'algorithme, les noms donnés aux jeux de données d'assimilation doivent correspondre exactement aux identifiants préprogrammés dans le code source de LIS (`LIS_pluginIndices.F90`).
*   `"SMAP(NRT) Soil Moisture"` n'était pas le bon nom pour le dataset utilisé (SPL3SMP).
*   `"MODIS LAI"` n'est pas un identifiant reconnu par LIS.

**Solution :**
*   Changement vers `"SMAP(NASA) soil moisture"` pour le SMAP.
*   Changement vers `"MCD15A2H LAI"` pour le LAI.
*   Les préfixes dans la configuration ont dû être modifiés en conséquence (ex: `MCD15A2H LAI data directory: ...`).

---

## 5. Paramètres Obligatoires Manquants pour le LAI (MPI Abort)

**Symptôme :**
Le test LAI crashe proprement avec `MPI_ABORT` en affichant l'erreur :
`[ERR] MCD15A2H LAI data version: is missing Stopping.`
`[ERR] MCD15A2H LAI apply temporal smoother between 8-day intervals: is missing Stopping.`
`[ERR] MCD15A2H LAI apply climatological fill values: is missing Stopping.`
`[ERR] MCD15A2H LAI apply QC flags: is missing Stopping.`

**Cause :**
Le module d'assimilation `MCD15A2H LAI` exige explicitement d'activer ou désactiver de nombreux drapeaux internes de gestion des observations dans `lis.config`.

**Solution :**
Ajout de l'ensemble des paramètres obligatoires dans `lis_da_lai.config` et `lis_da_joint.config` :
```text
MCD15A2H LAI data version: "006"
MCD15A2H LAI apply temporal smoother between 8-day intervals: 0
MCD15A2H LAI apply climatological fill values: 0
MCD15A2H LAI apply QC flags: 0
```

---

## 5b. Paramètres Tableaux (Arrays) Incomplets pour le Run Conjoint (Joint DA)

**Symptôme :**
L'expérience `lis_da_joint.config` crashe avec des erreurs d'algorithmes manquants comme :
`[ERR] Observation perturbation algorithm: not defined Stopping.`
Ou encore `Bias estimation algorithm: not defined Stopping.`

**Cause :**
Pour un run conjoint avec `Number of data assimilation instances: 2`, tous les paramètres liés aux perturbations et aux observations doivent obligatoirement être des listes contenant exactement 2 valeurs séparées par des espaces (une pour SMAP, une pour LAI). Une seule valeur (ex: `"GMAO scheme"`) entraîne un crash car le code n'arrive pas à parser la suite de la configuration pour l'instance 2.

**Solution :**
Correction des paramètres clés sous forme de vecteurs dans `lis_da_joint.config` :
```text
State perturbation algorithm:             "GMAO scheme" "GMAO scheme"
Observation perturbation algorithm:       "GMAO scheme" "GMAO scheme"
Apply perturbation bias correction:        0 0
Bias estimation algorithm:                "none" "none"
```

---

## 6. Problèmes de Lecture des Attributs de Perturbation (Caractères Invisibles)

**Symptôme :**
Crash inexpliqué pendant la lecture du fichier `noahmp_sm_pertattribs.txt`. LIS lit les trois premières lignes (Soil Moisture Layer 1 à 3) et crashe avant de lire la 4ème.

**Cause :**
Les fichiers textes générés sous Windows ou modifiés incorrectement contiennent des caractères de retour chariot `\r` ou des tabulations `\t`. La fonction Fortran `read()` utilisée par LIS pour lire ces tables formatées crashe souvent lorsqu'elle rencontre ce type de caractères.

**Solution :**
Nettoyage des fichiers textes du répertoire `data/pert_package/` avec `sed` :
```bash
sed -i 's/\r$//' data/pert_package/*.txt
sed -i 's/\t/ /g' data/pert_package/*.txt
```

---

## 7. Mismatch de la Décomposition MPI (Processor Layout)

**Symptôme :**
Lorsqu'il est exécuté avec `mpirun -n 32`, le modèle DA crashe ou s'arrête en erreur (`Layout does not match the number of processors`).

**Cause :**
Dans les configurations DA (`lis_da_*.config`), le découpage du domaine (`Number of processors along x` et `y`) était configuré en 4x8 (soit 32 processeurs). Pour un domaine local aussi petit (18x8) et avec des paramètres d'assimilation, attribuer 32 processus fait que certains nœuds MPI n'ont aucune cellule terrestre à traiter. Le filtre de Kalman calcule alors des matrices de covariance vides, ce qui induit une instabilité.

**Solution :**
Changement de la décomposition à **2x2** (soit 4 processeurs) dans tous les `lis_da_*.config`, et lancement des tests avec `mpirun -n 4` dans le script SLURM `job_da.sh`.

---

## Conclusion
Après résolution de tous ces points de configuration interdépendants, l'Open-Loop et les différentes expériences EnKF 1D s'exécutent de façon stable, lisent bien les matrices de perturbation, ingèrent les données et produisent correctement les sorties dans `/output_smap`, `/output_lai`, etc.

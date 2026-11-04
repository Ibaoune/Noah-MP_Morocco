# Historique des Décisions Techniques et Journal des Modifications (CHANGELOG)

Ce document retrace l'historique chronologique des arbitrages scientifiques, des corrections d'anomalies et des évolutions d'infrastructure du projet **NoahMP_Morocco**.

---

## Chronologie des Jalons et Décisions

### 1. Correction de l'erreur de domaine CDF et archivage (Fin Octobre 2026)
* **Contexte** : La première simulation d'assimilation avec CDF matching (`DA_cdf`) montrait des incohérences d'assimilation et des ajustements anormaux.
* **Diagnostic** : Les fichiers NetCDF de CDF matching (`smap_cdf.nc`) avaient été générés par LDT sur une grille nationale couvrant l'ensemble du territoire marocain, au lieu d'être restreints au domaine effectif de modélisation **NorthMor** (181 × 121 = 21 901 points, longitude [-10.0, -1.0], latitude [30.0, 36.0]). Cette divergence de domaine faussait la correspondance d'indice 1D `ngrid` des points continentaux entre LDT et LIS.
* **Actions correctives** :
  1. *Archivage strict* : Le run complet de 60 mois affecté ainsi que ses tables dérivées ont été déplacés et sanctuarisés dans `experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/` afin de garantir une traçabilité expérimentale totale.
  2. *Génération de la CDF NorthMor* : Recalcul propre des CDF d'observations SMAP (`smap_obs_cdf_NorthMor.nc`) et de modèle Open Loop (`noahmp_model_cdf_NorthMor.nc`) sur la grille stricte NorthMor (16 030 points de terre).
  3. *Mise en place d'un garde-fou spatial* : Création du script bloquant `check_cdf_domain.py`, intégré dans le script de soumission SLURM de chaque job mensuel de `chain_da.py`. Ce script vérifie avant le lancement de LIS que `ngrid == 16030`, que les dimensions sont strictement identiques, et que le `LANDMASK` ne présente aucun pixel divergent.

### 2. Recalcul et complétion de la simulation de production `DA_cdf_noirr_2016_2020` (Novembre 2026)
* Exécution complète de la chaîne daisy-chain mois par mois couvrant les 60 mois de la période 2016-01 à 2020-12 (20 membres d'ensemble).
* Validation spatiale réussie avec 0 pixel d'écart sur le masque terre et une reproductibilité numérique contrôlée.

### 3. Mesure de l'effet du seuil de flétrissement du QC (`lisf_nowilt`) (Fin Octobre 2026)
* Une version modifiée du code source de LIS (`src/lisf_nowilt`, patch [`patches/lisf_nowilt_qc_wilting.patch`](../patches/lisf_nowilt_qc_wilting.patch)) a été compilée afin de **mesurer l'effet du seuil de flétrissement du QC** dans le module de contrôle qualité des observations SMAP (`noahmp401_qc_soilmobs.F90`).
* Une simulation de test sur 2 mois (`DA_nocdf_TEST_nowilt`, juillet–août 2018) a été exécutée.

### 4. Structuration, assainissement et documentation du workspace (Novembre 2026)
* Sanctuarisation des runs de production (`SPINUP`, `OPL_noirr_2016_2020`, `DA_nocdf_noirr_2016_2020`, `DA_cdf_noirr_2016_2020`, `CDF/`).
* Regroupement propre des expériences de test dans `matrix_2016_2020/tests/` et des expériences futures dans `matrix_2016_2020/planned/`.
* Rangement des journaux de batch épars dans `CDF/logs/` et des fichiers de travail `.bak` dans `_bak/`.
* Écriture d'une suite documentaire complète (`README.md`, `docs/RUNS.md`, `docs/DATA.md`, `docs/CHANGELOG.md`).
* Suspension formelle des tâches relatives au binaire instrumenté et à l'open loop d'ensemble 2018.

---

## Notes Techniques

Cette section rassemble les spécificités factuelles du code LISF et du modèle Noah-MP identifiées au cours des audits :

1. **Définition de la variable `spread` dans les fichiers EnKF `*_spread.nc`** :
   Dans les fichiers EnKF `*_spread.nc` générés par LIS, la variable nommée `spread` correspond factuellement à l'**étendue d'ensemble** (valeur maximale moins valeur minimale : $\text{max} - \text{min}$), et **non à l'écart-type** ($\sigma$) des membres de l'ensemble.

2. **Calcul des incréments d'analyse (`*_incr.nc`)** :
   Les champs d'incréments d'assimilation enregistrés dans les fichiers `*_incr.nc` sont calculés immédiatement à la sortie du filtre EnKF, **avant** l'application des contrôles de validité physique et de saturation/flétrissement effectués dans la routine `noahmp401_setsoilm.F90`. En conséquence, un incrément mathématiquement calculé peut être tronqué ou corrigé par le modèle terrestre lors de la mise à jour effective des profils d'humidité du sol.

3. **Condition de rejet par le contrôle qualité (QC) au point de flétrissement** :
   Dans la routine `noahmp401_qc_soilmobs.F90`, le test de rejet des observations d'humidité du sol s'appuie sur la condition `(smobs(t) - smcwlt_obs(t) < 0.02)`. La valeur de `smcwlt_obs` (teneur en eau au point de flétrissement) n'est pas constante spatialement : elle **dépend directement de la classe de texture du sol** (STATSGO) définie pour chaque point de grille.

# ARCHIVE — Simulation DA-CDF avec Domaine CDF Erroné (66 391 points)

> [!CAUTION]
> **NE PAS RÉUTILISER**
> L'ensemble des données, modèles, sorties SHAP, tableaux et figures regroupés dans cette archive est strictement invalide pour l'analyse scientifique. Ne pas réutiliser ces fichiers ni les réintégrer dans les chaînes de traitement actives.

---

## 1. Raison de l'invalidation

- **Cause technique** : La correction de biais par CDF matching pour SMAP et le modèle Noah-MP avait été initialement générée par LDT sur l'ensemble de la grille nationale Maroc (contenant **66 391 points** de grille 1D `ngrid`).
- **Comportement du modèle LIS** : Lors de l'exécution de la simulation sur le domaine d'étude `NorthMor` (**16 030 points** de grille), LIS lit le fichier CDF séquentiellement selon la dimension `ngrid` ($i = 1, \dots, 16\,030$) sans effectuer de ré-échantillonnage ni de vérification des coordonnées spatiales (latitude/longitude). En conséquence, les quantiles et statistiques de biais associées aux pixels du sud du Maroc (Sahara / désert) ont été appliqués aux pixels du nord du Maroc (Rif, Gharb, Moyen-Atlas).
- **Date de découverte** : **2026-10-27**
- **Date d'archivage** : **2026-11-02**
- **Statut de remplacement** : Une nouvelle simulation rigoureusement corrigée `DA_cdf_noirr_2016_2020` a été relancée avec des fichiers CDF calculés strictement sur le domaine NorthMor (**16 030 points**) :
  - `experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc` (ngrid: 16 030)
  - `experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc` (ngrid: 16 030)

---

## 2. Inventaire des dossiers et fichiers archivés

Espace disque total occupé par l'archive : **38 Go**.

### A. Ancienne simulation LIS DA-CDF complète (35 Go)
- **Ancien chemin** : `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/_archive_oldCDF_20261027/`
- **Nouveau chemin** : `experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/old_DA_cdf_run/`
- **Contenu** : 60 mois de sorties LIS historiques (`SURFACEMODEL`), incréments et spreads EnKF (`EnKF`), observations assimilées (`DAOBS`), restarts mensuels (`restarts/surf`, `restarts/pert`), journaux d'exécution (`logs/`) et fichiers de configuration générés (`generated/`).

### B. Anciens fichiers CDF nationaux à 66 391 points (387 Mo)
- **Anciens chemins** :
  - `experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_noirr/` (`smap_cdf.nc` [ngrid: 66 391] et `smap_cdf_domain.nc`)
  - `experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_irr/` (`smap_cdf.nc` [ngrid: 66 391] et `smap_cdf_domain.nc`)
- **Nouveau chemin** : `experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/old_cdf_files/`

### C. Produits dérivés dans `smap-xai-audit` (2,8 Go, 236 éléments)
- **Nouveau chemin racine** : `experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/old_derived_products/smap-xai-audit/` (arborescence d'origine préservée)
- **Composants déplacés** :
  1. **Données intermédiaires EnKF et Noah-MP** :
     - `data/interim/enkf/da_cdf/`
     - `data/interim/noahmp/da_cdf/`
  2. **Données journalières agrégées** :
     - `data/processed/daily_enkf/da_cdf/`
     - `data/processed/daily_model/da_cdf/`
     - `data/processed/transfer/da_cdf/`
  3. **Modèles Random Forest (RF)** :
     - `artifacts/modeling/random_forest/SOURCE_da_cdf_*` (ensemble des modèles A, B, C, D et folds spatiaux)
     - `artifacts/modeling/random_forest/*_matched_support` (modèles entraînés sur l'échantillon commun de support avec l'ancienne run CDF)
  4. **Données de modélisation et sorties SHAP (XAI)** :
     - `data/processed/modeling/source/*da_cdf*`
     - `data/processed/modeling/splits/*da_cdf*`
     - `data/processed/modeling/transfer/*da_cdf*`
     - `data/processed/modeling/value/*da_cdf*`
     - `data/processed/modeling/xai/*da_cdf*` et `*matched_support*`
  5. **Métriques, rapports QC et figures** :
     - `reports/modeling/baselines/*da_cdf*` et `*matched_support*`
     - `reports/qc/*/*da_cdf*`
     - `figures/water_balance/Figure_S8.png` et `Figure_S8.pdf`
     - `analysis_water_accounting_pixel_cumulative_cdf.nc`
     - `analysis_water_accounting_*.csv`

La liste exhaustive des 236 fichiers et répertoires déplacés est répertoriée dans [moved_items.log](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/moved_items.log).

---

## 3. Intégrité des simulations valides
Aucun fichier appartenant aux simulations valides (`OPL_noirr_2016_2020`, `DA_nocdf_noirr_2016_2020`, nouvelle `DA_cdf_noirr_2016_2020`) n'a été altéré ou déplacé. Les produits propres à DA-NoCDF (`data/*/da_nocdf`, modèles `SOURCE_da_nocdf_*_native_support`, etc.) restent inchangés à leur emplacement d'origine.

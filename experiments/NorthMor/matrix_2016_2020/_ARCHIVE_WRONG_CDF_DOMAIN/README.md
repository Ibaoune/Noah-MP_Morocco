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

### D. Produits dérivés de post-traitement archivés (`old_derived_products/postproc/`, 181 fichiers)
- **Origine** : Sorties NetCDF de climatologies, figures de diagnostic et de manuscrit, tables et chiffres clés générés avant le 31 octobre 2026 à partir de l'ancienne simulation `DA-CDF`.
- **Nouveau chemin racine** : `experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/old_derived_products/postproc/`
- **Contenu déplacé** :
  1. **Climatologies NetCDF DA-CDF (5 ans, 22 fichiers)** : `total_runoff_DA_CDF_M01..M12`, `DJF`, `JJA`, `surface_runoff_DA_CDF`, `baseflow_DA_CDF`, `precipitation_DA_CDF`, `surface_soil_moisture_DA_CDF`.
  2. **Figures candidates du manuscrit (11 fichiers)** : `Fig3_SMAP_coverage_increment_distributions_v2/v3/v4`, `Fig4_annual_DJF_JJA_SMAP_increment_patterns_Q1`, `FigS1_mean_innovations_Q1`.
  3. **Tables et chiffres clés (8 fichiers)** : `Fig3_Fig4_SMAP_assimilation_key_numbers.txt`, etc.
  4. **Diagnostics d'assimilation DA-CDF (21 fichiers)** : sous-dossier `assimilation/DA_CDF/` et `Fig_MultiYear_Assimilation`.
  5. **Hydrologie & bilans (60 fichiers)** : sous-dossiers `hydrology/` pour `baseflow`, `baseflow_fraction`, `evapotranspiration`, `rootzone_soil_moisture`, `surface_runoff`, `surface_soil_moisture`, `total_runoff`.
  6. **Impact saisonnier OPL vs DA-CDF (6 fichiers)** : `fig_runoff_seasonal_OPL_vs_DA_CDF`, etc.
  7. **Validation observations indépendantes (23 fichiers)** : comparaison DA-CDF face à ESA CCI.
  8. **Réponse hydrologique & sécheresse (30 fichiers)**.
- **Régénération avec la nouvelle run DA_cdf_noirr_2016_2020** :
  Ces sorties sont **entièrement régénérables** à partir de la nouvelle run valide `DA_cdf_noirr_2016_2020` et des runs `OPL_noirr_2016_2020` et `DA_nocdf_noirr_2016_2020`, via les recettes existantes du pipeline :
  - `configs/recipes/smap_cdf_sensitivity_2016_2020.yaml` (diagnostics d'assimilation, bilans hydrologiques, cartes de différences et climatologies saisonnières).
  - `configs/recipes/paper_manuscript_figures.yaml` (génération des figures consolidées du manuscrit).
  - `configs/recipes/smap_cdf_independent_validation_2016_2020.yaml` (évaluation indépendante face à ESA CCI, GLEAM, etc.).
  - `configs/recipes/paper_core_diagnostics.yaml`.
  Les sorties spécifiques à OPL seule et à DA-NoCDF seule restent intactes à leur emplacement d'origine dans `scripts/postproc/matrix_2016_2020/`.

La liste exhaustive de tous les fichiers et répertoires déplacés (dont les 181 sorties postproc) est répertoriée dans [moved_items.log](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN/moved_items.log).

---

## 3. Intégrité des simulations valides
Aucun fichier appartenant aux simulations valides (`OPL_noirr_2016_2020`, `DA_nocdf_noirr_2016_2020`, nouvelle `DA_cdf_noirr_2016_2020`) n'a été altéré ou déplacé. Les produits propres à DA-NoCDF (`data/*/da_nocdf`, modèles `SOURCE_da_nocdf_*_native_support`, etc.) restent inchangés à leur emplacement d'origine.

---

## 4. Purge définitive des données volumineuses invalidées (Lot 2B)

- **Date effective de la purge** : Novembre 2026
- **Volume net récupéré** : **40,64 GB** (37,85 GiB, 19 840 fichiers supprimés)
- **Groupes de données supprimés** :
  1. `old_DA_cdf_run/output/` : 60 mois de sorties LIS historiques (`SURFACEMODEL`, incréments et spreads `EnKF`, observations `DAOBS`) — **25,29 GB** (17 127 fichiers).
  2. `old_DA_cdf_run/restarts/` : Restarts mensuels LIS invalides (`restarts/surf`, `restarts/pert`) — **9,95 GB** (120 fichiers).
  3. `old_DA_cdf_run/logs/` : Journaux d'exécution LIS de l'ancienne simulation — **1,93 GB** (2 042 fichiers).
  4. `old_derived_products/` : Anciens produits dérivés `smap-xai-audit` (modèles RF, tables SHAP, data processed) et `postproc` (climatologies et figures obsolètes) — **3,07 GB** (549 fichiers).
  5. `old_cdf_files/*/smap_cdf.nc` : Tables CDF erronées à 66 391 points (versions irriguée et non-irriguée) — **0,40 GB** (2 fichiers).
- **Reliques préservées pour traçabilité scientifique (~1,4 Mo, 125 fichiers)** :
  - `README.md` : justification méthodologique de l'invalidation spatiale et journal de purge.
  - `PROOF_WRONG_CDF_GRID_66391_PTS.txt` : signature dimensionnelle ($331 \times 305$, 66 391 points 1D) et spatiale ($[20.8^\circ\text{N}, 36.0^\circ\text{N}] \times [-17.3^\circ\text{E}, -0.8^\circ\text{E}]$) attestant de l'incompatibilité avec `NorthMor`.
  - `moved_items.log` : manifeste exhaustif des fichiers déplacés.
  - `old_DA_cdf_run/generated/` : 120 fichiers de configuration `lis_DA_SMAP_cdf_noirr_*.config` et 60 scripts de soumission `job_DA_cdf_*.slurm` d'origine.
  - `old_cdf_files/*/smap_cdf_domain.nc` : grilles NetCDF 2D de domaine LDT (514 Ko au total).

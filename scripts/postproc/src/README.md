# LIS/Noah-MP Post-Processing — `src/`

Ce dossier contient l'ensemble des modules Python du framework de post-traitement LIS/Noah-MP/HyMAP.

> [!IMPORTANT]
> **Depuis juillet 2026, le framework est piloté par la nouvelle architecture YAML-driven.**
> Le point d'entrée principal est désormais `scripts/run_postproc.py` (situé dans `scripts/postproc/scripts/`).
> Les anciens modules conservés dans ce dossier restent fonctionnels en mode **archive**.
> Consultez le [README principal](../README.md) pour l'utilisation du nouveau framework.

---

## Nouveau Framework (à utiliser)

```bash
# Depuis scripts/postproc/
python scripts/run_postproc.py --list-experiments
python scripts/run_postproc.py --list-recipes
python scripts/run_postproc.py --check-configs
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --dry-run
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures
```

---

## Architecture de `src/`

```
src/
├── lis_postproc/                   ← Package principal (nouveau)
│   ├── cli.py                      # Interface CLI
│   ├── runner.py                   # Orchestrateur RecipeRunner
│   ├── core/                       # Chargement + validation YAML
│   │   ├── config.py               # load_global_config, load_recipe, check_all_configs
│   │   ├── experiments.py          # Dataclass Experiment
│   │   ├── variables.py            # Dataclass Variable
│   │   ├── recipes.py              # Dataclass Recipe
│   │   ├── scanner.py              # Scanner dynamique des variables NetCDF
│   │   └── quality.py              # Module QC (Quality Control) hydrologique
│   ├── io/                         # Lecture LIS/HyMAP NetCDF
│   │   ├── lis.py                  # Wrapper autour de utils/io_lis.py
│   │   ├── hymap.py                # Stub (à implémenter)
│   │   └── observations.py         # Stub (SMAP, WaPOR, ASCAT)
│   ├── diagnostics/
│   │   ├── assimilation/
│   │   │   └── adapter.py          # Pont vers assimilation_diagnostics/ (préservé intact)
│   │   └── hydrology/              # Diagnostics hydrologiques (Phase 2 - complété)
│   │       ├── maps.py             # Cartes moyennes et de différences
│   │       ├── timeseries.py       # Séries temporelles moyennes
│   │       └── runoff_partitioning.py # Partitionnement Qs/Qsb
│   ├── plotting/
│   │   ├── maps.py                 # Cartographie générique (Cartopy)
│   │   ├── timeseries.py           # Séries temporelles multi-expériences
│   │   ├── distributions.py        # Histogrammes et boxplots
│   │   └── styles.py               # Palettes de couleurs + styles matplotlib
│   └── utils/
│       └── helpers.py              # Wrappers utils/masking, metrics, spatial_stats
│
├── assimilation_diagnostics/       ← Module de référence (PRÉSERVÉ INTACT)
│   ├── main.py
│   ├── utils.py
│   ├── diagnostics/
│   │   ├── diag_coverage.py
│   │   ├── diag_innovations.py
│   │   ├── diag_seasonal_increments.py
│   │   └── diag_spread.py
│   └── configs/
│       ├── global.yaml
│       ├── experiments/
│       │   ├── DA-noCDF-noIRR_2016.yaml
│       │   └── DA-CDF-noIRR_2016.yaml
│       └── diagnostics/
│           ├── coverage.yaml
│           ├── innovations.yaml
│           ├── seasonal_increments.yaml
│           └── spread.yaml
│
├── opl_multiple_da/                ← Archive (remplacé par configs/recipes/) + Modules génériques
├── opl_vs_da/                      ← Archive (remplacé par configs/recipes/)
├── runoff_partitioning/            ← À migrer (Phase 2)
├── hymap_validation/               ← À migrer (Phase 2)
├── external_validation/            ← À migrer (Phase 2) + Modules génériques
├── figure_export/                  ← À migrer (Phase 2)
│
├── paper_reproductions/            ← NOUVEAU : Scripts de reproduction des articles
│   └── nie2022/                    # Figures de l'article Nie et al. (2022)
│
├── utils/                          ← Utilitaires partagés (réutilisés par lis_postproc/)
│   ├── io_lis.py                   # Lecture des fichiers LIS NetCDF
│   ├── io_da.py                    # Lecture des fichiers DA
│   ├── masking.py                  # Masques terrestres
│   ├── metrics.py                  # RMSE, biais, corrélation
│   └── spatial_stats.py            # Moyennes spatiales et statistiques
│
└── configs/                        ← Configs legacy (remplacées par configs/ à la racine)
    ├── matrix_2016.yaml            # → remplacé par configs/experiments.yaml
    ├── paths.yaml                  # → remplacé par configs/global.yaml
    ├── figure_sets.yaml
    └── variables_lis.yaml          # → remplacé par configs/variables/*.yaml
```

---

## Modules en Détail

### `lis_postproc/` — Nouveau package principal

Package YAML-driven créé en juillet 2026. Il orchestre l'ensemble du pipeline via des objets `Recipe`, `Experiment` et `Variable` chargés depuis `configs/`.

**Interface d'entrée :**
```python
from lis_postproc.core import load_global_config, load_experiments_catalog, load_recipe, Recipe
from lis_postproc.runner import RecipeRunner
```

---

### `assimilation_diagnostics/` — Module de référence ⭐

> [!IMPORTANT]
> **Ce module est préservé intact.** Aucune ligne de `diag_*.py` ou `utils.py` n'a été modifiée.
> Il reste exécutable de manière autonome ET intégré dans le nouveau framework via un adaptateur.

**Exécution autonome (inchangée) :**
```bash
cd src/assimilation_diagnostics
python main.py --experiment configs/experiments/DA-noCDF-noIRR_2016.yaml --all
python main.py --experiment configs/experiments/DA-CDF-noIRR_2016.yaml --diagnostic coverage
```

**Intégration dans le nouveau framework :**
La recette `smap_cdf_sensitivity_2016.yaml` active automatiquement les 4 diagnostics via `lis_postproc/diagnostics/assimilation/adapter.py`, qui injecte les chemins et appelle directement `run_coverage()`, `run_innovations()`, `run_seasonal_increments()`, `run_spread()`.

| Diagnostic | Description | Figures |
|---|---|---|
| `coverage` | Couverture spatiale des observations assimilées | Fig 1, Fig 2 |
| `innovations` | Innovations et incréments moyens + histogramme | Fig 4a, 4b, 4c |
| `seasonal_increments` | Incréments saisonniers (sec/humide) | Fig 5 |
| `spread` | Cohérence spread / RMSE | Fig 6, Fig 7 |

---

### `opl_multiple_da/` — Archive

> [!NOTE]
> Ce module est en mode **archive**. Sa logique a été migrée dans `configs/recipes/smap_cdf_sensitivity_2016.yaml`.
> Les 9 blocs thématiques (`assimilation`, `soil_moisture`, `fluxes`, `groundwater`, `runoff`, `streamflow`, `validation`, `spatial_analysis`, `synthesis`) correspondent maintenant aux clés `diagnostics:` dans les recettes YAML.

---

### `opl_vs_da/` — Archive

> [!NOTE]
> Ce module est en mode **archive**. Le script `plot_basin_timeseries.py` sera migré dans `lis_postproc/diagnostics/` lors de la Phase 2.

---

### `runoff_partitioning/` — Archive (Phase 2 complétée)

Module historique dédié au partitionnement du ruissellement. **Complètement migré** dans `lis_postproc/diagnostics/hydrology/runoff_partitioning.py`.

---

### `hymap_validation/` — À migrer (Phase 2)

Validation des débits HyMAP contre les stations de jaugeage. Sera migré dans `lis_postproc/io/hymap.py` + `lis_postproc/diagnostics/streamflow/`.

---

### `external_validation/` — À migrer (Phase 2) + Modules Génériques

Validation externe (ASCAT, ESA-CCI, GLEAM, WaPOR, GRACE, MODIS LAI). Sera migré dans `lis_postproc/diagnostics/validation/`.
Contient également les nouveaux modules de calcul génériques pour la reproduction de papiers (e.g., `correlations.py`, `lai_anomalies.py`, `landcover_statistics.py`).

---

### `paper_reproductions/` — Reproduction d'Articles Scientifiques (NOUVEAU)

Ce répertoire contient les scripts de haut niveau dédiés exclusivement à la **reproduction exacte des figures d'articles publiés**. 

**Principe d'architecture :**
- **Aucun calcul scientifique lourd** ne doit être codé ici. 
- Les scripts importent les fonctions depuis les modules de calcul (`external_validation/`, `opl_multiple_da/`, `assimilation_diagnostics/`, etc.).
- Le rôle de ces scripts se limite à l'assemblage des données, la mise en page (subplots), les palettes de couleurs, et l'export des figures finales (PDF/PNG).

**Sous-module `nie2022/` :**
Reproduit les figures de l'article *Nie et al. (2022)* relatives à l'assimilation SMAP.
- `fig02_flux_correlation_maps.py` : Utilise `external_validation/correlations.py`
- `fig03_landcover_correlation_boxplots.py` : Utilise `external_validation/landcover_statistics.py`
- `fig04_lai_seasonality_comparison.py` : Utilise `opl_multiple_da/lai_timeseries.py`
- `fig08_drought_area_timeseries.py` : Utilise `opl_multiple_da/drought_indices.py`
- `fig09_drought_area_scatterplots.py` : Utilise `opl_multiple_da/drought_scatter.py`
- `fig10_lai_anomaly_maps.py` : Utilise `external_validation/lai_anomalies.py`

**Utilisation :**
```bash
python src/paper_reproductions/nie2022/fig02_flux_correlation_maps.py
```

---

### `utils/` — Utilitaires partagés (réutilisés)

> [!TIP]
> Ces fichiers sont directement réutilisés par le nouveau package `lis_postproc/io/lis.py` et `lis_postproc/utils/helpers.py` via des imports. Ils ne sont pas dupliqués.

| Fichier | Contenu |
|---|---|
| `io_lis.py` | `get_lis_files()`, `load_lis_variable()` |
| `io_da.py` | Lecture des fichiers d'assimilation (innovations, spread) |
| `masking.py` | `get_land_mask()` |
| `metrics.py` | `compute_bias()`, `compute_rmse()`, `compute_corr()` |
| `spatial_stats.py` | `compute_domain_mean()`, `compute_basin_average()` |

---

## Règles de Développement

1. **Ne jamais modifier** `assimilation_diagnostics/diagnostics/diag_*.py` directement — passer par l'adaptateur
2. **Ne jamais coder en dur** un nom d'expérience dans le code Python — le déclarer dans `configs/experiments.yaml`
3. **Ne pas ajouter** de nouveau code dans `opl_multiple_da/` ou `opl_vs_da/` — les modules cibles sont dans `lis_postproc/diagnostics/`
4. Tout nouveau diagnostic → créer dans `lis_postproc/diagnostics/` + enregistrer dans `runner.py`
5. Toute nouvelle variable → créer `configs/variables/{id}.yaml`
6. Toute nouvelle expérience → ajouter dans `configs/experiments.yaml`

---

## Feuille de Route (Phase 2)

| Module source | Cible dans `lis_postproc/` | Statut / Priorité |
|---|---|---|
| `runoff_partitioning/` | `diagnostics/hydrology/runoff_partitioning.py` | ✅ **Terminé** |
| `opl_vs_da/plot_basin_timeseries.py` | `diagnostics/hydrology/timeseries.py` | ✅ **Terminé** |
| `figure_export/` | Intégré dans `runner.py` et `plotting/pdf_generator.py` | ✅ **Terminé** |
| `hymap_validation/` | `diagnostics/streamflow/` + `io/hymap.py` | À faire (Haute) |
| `external_validation/` | `diagnostics/validation/` | À faire (Moyenne) |
| `domain/` | `plotting/maps.py` (étendu) | À faire (Basse) |

# Framework de Post-Processing LIS/Noah-MP/HyMAP

Framework modulaire et scalable pour le post-traitement des expériences d'assimilation de données LIS/Noah-MP. L'architecture est entièrement pilotée par des fichiers YAML — **aucun nom d'expérience n'est codé en dur dans le code Python**.

---

## Architecture Générale

```
scripts/postproc/
├── _ARCHIVE_OBSOLETE/              # Composants obsolètes archivés pour traçabilité
├── configs/                        # ← Fichiers YAML de configuration
│   ├── global.yaml                 # Chemins globaux, options de plotting
│   ├── experiments.yaml            # Catalogue de toutes les expériences
│   ├── baselines/                  # Configurations des baselines figées (read-only)
│   ├── observations/               # Configurations des jeux d'observations (ex: WaPOR)
│   ├── domains/                    # Configurations de domaine spatial
│   │   └── morocco_001deg.yaml
│   ├── variables/                  # Une variable = un YAML
│   │   ├── surface_soil_moisture.yaml
│   │   ├── total_runoff.yaml
│   │   └── ...  (15 variables)
│   └── recipes/                    # Recettes de comparaison scientifiques
│       ├── only_opl_2016.yaml
│       ├── smap_cdf_sensitivity_2016.yaml
│       ├── opl_vs_smap_da_scientific_2016.yaml
│       └── ...
│
├── scripts/                        # Point d'entrée
│   ├── run_postproc.py             # ← SCRIPT PRINCIPAL (baseline existante)
│   ├── run_scientific_postproc.py  # ← NOUVEAU RUNNER scientifique (additive)
│   └── job_postproc_2016.sh        # Script SLURM pour le cluster
│
├── src/                            # Code Python
│   ├── lis_postproc/               # ← Package principal
│   │   ├── cli.py                  # Interface CLI
│   │   ├── runner.py               # Orchestrateur RecipeRunner
│   │   ├── core/                   # Chargement YAML, capabilities, registry, provenance
│   │   ├── io/                     # Lecture LIS/HyMAP NetCDF
│   │   ├── diagnostics/
│   │   │   ├── assimilation/       # Pont vers assimilation_diagnostics/
│   │   │   ├── domain/             # Diagnostic de cartographie du domaine
│   │   │   ├── quality_control/    # QC temporel, coords, valeurs manquantes
│   │   │   └── water_balance/      # Audit des termes du bilan hydrique
│   │   ├── plotting/               # Fonctions de visualisation génériques
│   │   └── utils/
│   │
│   ├── assimilation_diagnostics/   # ← MODULE DE RÉFÉRENCE (préservé intact)
│   ├── opl_multiple_da/            # Archive (→ déplacé vers _ARCHIVE_OBSOLETE)
│   ├── opl_vs_da/                  # Archive (→ déplacé vers _ARCHIVE_OBSOLETE)
│   └── utils/                      # Utilitaires partagés existants
│
├── tests/                          # Tests unitaires et d'intégration (core, qc, wb, etc.)
│
├── tools/                          # Outils autonomes d'audit et utilitaires
│   ├── audit/                      # Scripts d'inventaire, regression, audit EnKF/DAOBS
│   └── download/                   # Scripts de téléchargement de données (WaPOR, etc.)
│
├── outputs/                        # Sorties générées
│   └── matrix_2016/
│       ├── figures/
│       ├── metrics/
│       ├── tables/
│       ├── pdf/
│       └── opl_vs_smap_da_scientific/ # Nouvelle structure de sortie avec provenance
│
└── logs/                           # Fichiers de logs
```

---

## Concepts Clés

### Expérience
Une expérience est une simulation LIS/Noah-MP identifiée par un **ID unique** dans `configs/experiments.yaml`. Elle contient : label, type, chemin des données, année, et paramètres d'assimilation.

```yaml
# configs/experiments.yaml
DA_smap_cdf_noirr_2016:
  label: "DA-SMAP-CDF"
  type: data_assimilation
  path: "experiments/NorthMor/matrix_2016/DA_cdf_noirr_2016/output"
```

### Variable
Une variable est une quantité hydro-physique définie dans `configs/variables/{id}.yaml`. Elle spécifie les noms de variables LIS, l'unité, les colormaps et les options de plotting.

```yaml
# configs/variables/total_runoff.yaml
variable_id: total_runoff
lis_variable_names: [Qs_tavg, Qsb_tavg]
operation: sum
unit: "mm day⁻¹"
```

### Recette
Une recette est un fichier `configs/recipes/{id}.yaml` qui orchestre une comparaison scientifique complète : quelles expériences, quelles variables, quels diagnostics, où sauvegarder.

```yaml
# configs/recipes/smap_cdf_sensitivity_2016.yaml
experiments: [OPL_noirr_2016, DA_smap_nocdf_noirr_2016, DA_smap_cdf_noirr_2016]
variables: [surface_soil_moisture, total_runoff, ...]
diagnostics:
  assimilation:
    enabled: true
  domain:
    enabled: true
```

---

## Commandes Disponibles

```bash
# Depuis le dossier scripts/postproc/

# Lister toutes les expériences (baseline)
python scripts/run_postproc.py --list-experiments

# Lister toutes les recettes (baseline)
python scripts/run_postproc.py --list-recipes

# Lancer la génération des figures pour une recette baseline
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures --make-pdf

# Lancer le NOUVEAU workflow scientifique additif avec provenance et diagnostiques étendus
python scripts/run_scientific_postproc.py --recipe configs/recipes/opl_vs_smap_da_scientific_2016.yaml

# Lancer la suite de tests (unitaires et d'intégration)
pytest tests/ -v

# Lancer un audit de non-régression de la baseline
python tools/audit/run_baseline_regression.py

# Sur le cluster (SLURM)
sbatch scripts/job_postproc_2016.sh smap_cdf_sensitivity_2016
```

---

## Comment Ajouter une Nouvelle Expérience

1. Copier `configs/experiments.yaml`
2. Ajouter une nouvelle entrée avec un ID unique :
   ```yaml
   DA_smap_irrigation_2016:
     label: "DA-SMAP-IRR"
     type: data_assimilation
     year: 2016
     assimilation: SMAP
     irrigation: true
     path: "experiments/NorthMor/matrix_2016/DA_smap_irr_2016/output"
   ```
3. Référencer l'ID dans une recette existante ou créer une nouvelle recette.
4. **Aucun code Python à modifier.**

---

## Comment Ajouter une Nouvelle Variable

1. Créer `configs/variables/{ma_variable}.yaml` en s'inspirant d'un fichier existant :
   ```yaml
   variable_id: snow_water_equivalent
   long_name: "Snow water equivalent"
   unit: "mm"
   input:
     lis_variable_names: [SWE_inst]
     operation: direct
   plotting:
     cmap: "Blues"
   ```
2. Référencer `snow_water_equivalent` dans la section `variables:` d'une recette.

---

## Comment Créer une Nouvelle Recette

1. Copier `configs/recipes/only_opl_2016.yaml` comme template
2. Renseigner :
   - `recipe_id` : identifiant unique
   - `experiments` : liste des IDs d'expériences (doivent exister dans `experiments.yaml`)
   - `variables` : liste des IDs de variables (doivent avoir leur YAML dans `configs/variables/`)
   - `diagnostics` : activer/désactiver les modules
   - `outputs` : chemins de sortie
3. Lancer avec : `python scripts/run_postproc.py --recipe configs/recipes/ma_recette.yaml --dry-run`

---

## Module `src/assimilation_diagnostics/` — Préservation et Intégration

### Statut
Ce module est le **module de référence** pour tous les diagnostics d'assimilation. Il est **préservé intact** — aucune ligne de code n'a été modifiée dans :
- `diagnostics/diag_coverage.py`
- `diagnostics/diag_innovations.py`
- `diagnostics/diag_seasonal_increments.py`
- `diagnostics/diag_spread.py`
- `utils.py`
- `configs/diagnostics/*.yaml` (4 fichiers de config visuelle)

### Intégration
L'intégration dans la nouvelle architecture se fait via un **adaptateur léger** :

```
configs/recipes/*.yaml
       ↓
scripts/run_postproc.py
       ↓
src/lis_postproc/diagnostics/assimilation/adapter.py
       ↓ (construit un compat_config)
src/assimilation_diagnostics/diagnostics/diag_*.py  ← INCHANGÉ
```

L'adaptateur :
1. Lit les paramètres de la recette (expériences DA, dates, saisons)
2. Construit un `compat_config` compatible avec le format attendu par les `run_*()` fonctions
3. Fusionne les YAMLs de configuration visuelle existants (`configs/diagnostics/*.yaml`)
4. Appelle directement `run_coverage()`, `run_innovations()`, etc.

### Exécution autonome (toujours fonctionnelle)
Le module peut aussi être exécuté directement sans passer par le nouveau framework :
```bash
cd src/assimilation_diagnostics
python main.py --experiment configs/experiments/DA-noCDF-noIRR_2016.yaml --all
python main.py --experiment configs/experiments/DA-CDF-noIRR_2016.yaml --diagnostic coverage
```

### Diagnostics disponibles
| Figure | Diagnostic | Module |
|--------|-----------|--------|
| Fig 1  | Assimilated observation count map | `diag_coverage` |
| Fig 2  | Assimilation frequency + monthly totals | `diag_coverage` |
| Fig 4a | Mean innovation map | `diag_innovations` |
| Fig 4b | Mean increment map | `diag_innovations` |
| Fig 4c | Increment distribution histogram | `diag_innovations` |
| Fig 5  | Wet/dry seasonal increments | `diag_seasonal_increments` |
| Fig 6  | Spread consistency check | `diag_spread` |
| Fig 7  | Prior/posterior spread comparison | `diag_spread` |

---

## Module `src/domain/` — Cartographie Géospatiale

Le module de domaine (`src/domain/`) est entièrement intégré dans le nouveau framework via l'adaptateur `src/lis_postproc/diagnostics/domain/adapter.py`. Il réutilise de manière fidèle la logique de rendu d'origine pour assurer une cohérence parfaite du style visuel (Cartopy, couleurs, résolutions).

### Diagnostics disponibles (`domain`)
| Figure | Description | Module |
|--------|-------------|--------|
| `Fig0_a_landcover` | Dominant Land Cover Types (MODIS IGBP) | `plot_domain_map` |
| `Fig0_b_soil_texture`| Dominant Soil Texture Classes (STATSGOFAO)| `plot_domain_map` |
| `Fig0_c_topography`  | Topography & Elevation (SRTM 30m) | `plot_domain_map` |
| `Fig0_d_basins_and_insitudata` | Hydrological Basins & In-Situ Stations | `plot_domain_map` |

---

## Règles d'Extension

1. **Ne jamais modifier** `src/assimilation_diagnostics/diagnostics/diag_*.py` directement
2. **Ne jamais coder en dur** un nom d'expérience dans le code Python
3. Pour ajouter un diagnostic dans l'assimilation, l'ajouter dans `assimilation_diagnostics/` puis l'enregistrer dans `adapter.py`
4. Pour ajouter un nouveau module de diagnostic (hydrology, validation...), créer un fichier dans `src/lis_postproc/diagnostics/` et l'enregistrer dans `runner.py`
5. Les anciens scripts `opl_multiple_da/` et `opl_vs_da/` ont été déplacés dans **`_ARCHIVE_OBSOLETE/`** — ne pas ajouter de nouveau code.

---

## Recettes Disponibles

| Recette | Expériences | Usage |
|---------|------------|-------|
| `only_opl_2016` | OPL | Vérification de référence |
| `smap_cdf_sensitivity_2016` | OPL, DA-noCDF, DA-CDF | **Recette principale actuelle** |
| `opl_vs_smap_da_2016` | OPL, DA-CDF | Évaluation de l'assimilation SMAP |
| `opl_vs_lai_da_2016` | OPL, DA-LAI | Évaluation de l'assimilation LAI (future) |
| `opl_vs_smap_vs_lai_2016` | OPL, DA-CDF, DA-LAI | Triple comparaison (future) |
| `opl_vs_smap_vs_lai_vs_joint_2016` | OPL, DA-CDF, DA-LAI, DA-joint | Référence Q1 (future) |

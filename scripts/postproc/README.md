# Framework de Post-Processing LIS/Noah-MP/HyMAP

**Author:** M. EL Aabaribaoune (@um6p)

## 1. Objectif du Projet
Ce projet est un framework générique et modulaire conçu pour le post-traitement, l'analyse et la visualisation des résultats de modélisation hydrologique et d'assimilation de données (LIS/Noah-MP). 

Il a été pensé pour ne pas être spécifique à une expérience donnée (comme `matrix_2016_2020`). Il s'appuie intégralement sur des fichiers de configuration YAML afin d'être **réutilisable** pour toute future expérience de modélisation sans aucune modification du code source.

## 2. Architecture des Dossiers

L'arborescence du framework sépare strictement le code métier (sources), la configuration et les résultats (outputs).

```text
scripts/postproc/
├── configs/                        # ← Fichiers YAML de configuration
│   ├── global.yaml                 # Configuration globale (noms de dossiers, paramètres par défaut)
│   ├── experiments.yaml            # Catalogue définissant les chemins des expériences (OL, DA)
│   ├── observations/               # Configurations des jeux de données d'observations
│   ├── variables/                  # Métadonnées des variables NetCDF (unités, limites)
│   └── recipes/                    # "Recettes" d'exécution des diagnostics
│
├── src/                            # ← Code métier (Python)
│   ├── core/                       # Chargement et validation des YAML
│   ├── io/                         # Outils de lecture NetCDF (LIS, HyMAP)
│   ├── diagnostics/                # Modules d'analyse
│   │   ├── assimilation/           # Diagnostics d'assimilation (innovations, spread)
│   │   ├── domain/                 # Cartographie du domaine d'étude
│   │   ├── hydrology/              # Cartes d'impacts hydrologiques
│   │   ├── independent_ob_validation/ # Validation contre observations satellitaires
│   │   └── runoff_partitioning/    # Séparation Ruissellement de surface / Baseflow
│   ├── plotting/                   # Utilitaires de tracé et de style (matplotlib/cartopy)
│   └── runner.py                   # Orchestrateur qui exécute les recettes
│
├── docs/                           # ← Documentation détaillée
│   └── figures/                    # Documentation décrivant la génération de CHAQUE figure
│
├── <nom_exp_principale>/           # ← DOSSIER DE RÉSULTATS (ex: matrix_2016_2020)
│   ├── figures/                    # Toutes les figures générées
│   ├── tables/                     # Fichiers textes/CSV statistiques
│   ├── metrics/                    # Données intermédiaires et NetCDF calculés
│   └── climatology_nc/             # Fichiers de climatologies moyennes
│
└── _ARCHIVE_TO_REVIEW_AFTER_CLEANUP_20260712/ # Anciens codes archivés
```

## 3. Fonctionnement Général

Le framework fonctionne via un système de **"Recettes"** (recipes). 
Une recette (un fichier YAML dans `configs/recipes/`) définit :
- Les expériences à comparer (ex: `OPL`, `DA_NoCDF`).
- La période d'analyse.
- Les variables à traiter.
- Les modules de diagnostic à activer (hydrologie, assimilation, etc.).

Lors de l'exécution, l'orchestrateur `runner.py` :
1. Lit le `global.yaml` et la recette.
2. Résout les chemins des expériences via `experiments.yaml`.
3. Lance séquentiellement les modules de diagnostics demandés.
4. Écrit les résultats dynamiquement dans le dossier de l'expérience (`<nom_exp_principale>/figures/`).

## 4. Prérequis et Installation

### Environnement Python
Le projet nécessite Python 3.8+ et les librairies d'analyse géospatiale standards (`xarray`, `netCDF4`, `cartopy`, `matplotlib`, `numpy`, `pandas`).

L'environnement virtuel (situé typiquement dans `scripts/venv/`) doit être activé avant toute exécution :
```bash
source ../venv/bin/activate
```

## 5. Comment exécuter le pipeline

Le point d'entrée principal est le script d'enrobage :

```bash
# Vérifier la configuration des recettes
python src/cli.py --list-recipes

# Exécuter une recette spécifique
python src/cli.py --recipe configs/recipes/smap_cdf_sensitivity_2016_2020.yaml --make-figures
```

Pour les figures de publication (manuscrit), un script dédié permet de soumettre le calcul via SLURM sur le HPC :
```bash
bash submit_manuscript_plots.sh
```

## 6. Ajouter une nouvelle expérience

Pour traiter une nouvelle simulation LIS, il n'est **jamais** nécessaire de modifier le code Python :

1. Ouvrez `configs/global.yaml` et changez `name_main_dir` par le nom de votre nouveau dossier d'analyse (ex: `my_new_experiment`).
2. Ouvrez `configs/experiments.yaml` et ajoutez un bloc pointant vers le dossier contenant vos sorties NetCDF LIS.
3. Copiez une recette dans `configs/recipes/`, changez son nom et lancez-la !

## 7. Bonnes pratiques de maintenance

1. **Aucun chemin en dur :** Tous les chemins doivent être construits dynamiquement via `global_cfg.get('_project_root')` ou lus depuis un fichier YAML.
2. **Modularité :** Toute nouvelle fonction de tracé doit être ajoutée dans `src/plotting/` et être appelée par un diagnostic dans `src/diagnostics/`.
3. **Documentation :** Chaque fonction doit avoir une docstring. Chaque nouveau diagnostic doit posséder un fichier markdown explicatif dans `docs/figures/`.

# Framework de Post-Processing LIS/Noah-MP/HyMAP

Framework unifié et modulaire pour le post-traitement des expériences d'assimilation de données LIS/Noah-MP. 
Cette architecture a été consolidée pour se concentrer sur l'essentiel : une arborescence propre, reproductible et pilotée par des configurations YAML.

---

## Architecture Générale

```text
scripts/postproc/
├── _ARCHIVE_TO_REVIEW_AFTER_CLEANUP_20260712/ # Anciennes architectures et historiques
├── configs/                        # ← Fichiers YAML de configuration
│   ├── global.yaml                 # Chemins globaux
│   ├── experiments.yaml            # Catalogue de toutes les expériences
│   ├── observations/               # Configurations des jeux d'observations
│   ├── domains/                    # Configurations spatiales
│   ├── variables/                  # Une variable = un YAML
│   └── recipes/                    # Recettes d'exécution
│       └── smap_cdf_sensitivity_2016.yaml  # ← RECETTE PRINCIPALE
│
├── scripts/                        # Point d'entrée
│   └── run_postproc.py             # ← SCRIPT D'EXÉCUTION UNIQUE
│
├── src/                            # Code Python actif
│   ├── assimilation_diagnostics/   # Code historique préservé
│   ├── domain/                     # Logique de génération des cartes
│   └── lis_postproc/               # Coeur de la pipeline modulaire
│       ├── core/                   # Chargement YAML et configuration
│       ├── io/                     # Lecture LIS/HyMAP NetCDF
│       ├── diagnostics/            # Modules d'analyse
│       │   ├── assimilation/       
│       │   ├── domain/             
│       │   ├── hydrology/          # (Inclut le runoff_partitioning)
│       │   └── independent_ob_validation/ # Validation multi-sources
│       ├── plotting/               # Outils graphiques
│       └── utils/
│
├── tests/                          # Tests unitaires du framework
├── tools/                          # Outils autonomes (téléchargement WaPOR, etc.)
│
└── outputs/
    └── matrix_2016/
        └── figures/
            └── smap_cdf_sensitivity/
                ├── assimilation/
                ├── domain/
                ├── hydrology/
                ├── independent_ob_validation/
                └── runoff_partitioning/
```

---

## Utilisation de la Pipeline

Le point d'entrée unique est `scripts/run_postproc.py`.

### Commandes de base

```bash
# Depuis le dossier scripts/postproc/

# Lister les expériences configurées
python scripts/run_postproc.py --list-experiments

# Lister les recettes disponibles
python scripts/run_postproc.py --list-recipes

# Vérifier la validité des configurations sans exécuter
python scripts/run_postproc.py --check-configs

# Simuler l'exécution de la recette principale (Dry-Run)
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --dry-run
```

### Génération des figures

```bash
# Exécuter l'analyse et générer les figures
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures
```

> **Note :** Les dossiers temporaires pour les métriques, PDFs et tables (`.tmp/`) sont utilisés pendant l'exécution pour ne pas polluer l'arborescence permanente de `outputs/`.

---

## Les 5 Diagnostics Actifs

La recette principale (`smap_cdf_sensitivity_2016.yaml`) orchestre la génération de 5 dossiers de sortie distincts :

1. **`assimilation/`** : Diagnostics internes du filtre (innovations, incréments, spread). S'appuie sur le code historique `src/assimilation_diagnostics/`.
2. **`domain/`** : Cartographie géospatiale du domaine d'étude (topographie, sols, bassins).
3. **`hydrology/`** : Séries temporelles et cartes de différences pour les variables hydrologiques (humidité du sol, ET, ruissellement).
4. **`runoff_partitioning/`** : Sous-diagnostic généré par l'hydrologie analysant le ratio ruissellement de surface / débit de base.
5. **`independent_ob_validation/`** : Comparaison avec des jeux de données d'observation indépendants (ESA CCI, ASCAT, WaPOR, In-situ).

---

## Principes d'Extension

- **Aucun nom de variable ou d'expérience n'est codé en dur** dans les scripts Python. Tout se paramètre dans les `configs/`.
- Pour ajouter une observation indépendante, utilisez `configs/observations/` et l'adaptateur de validation.
- Les anciens codes, CLI parallèles et scripts redondants ont été isolés dans `_ARCHIVE_TO_REVIEW_AFTER_CLEANUP_20260712/` pour garantir une architecture saine. En cas de besoin de code ancien, veuillez consulter cette archive.

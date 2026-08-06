# LIS/Noah-MP Post-Processing — `src/`
**Author:** M. EL Aabaribaoune (@um6p)

Ce dossier contient l'ensemble des modules Python du framework de post-traitement LIS/Noah-MP/HyMAP.

> [!IMPORTANT]
> **Le framework est piloté par une architecture YAML-driven.**
> L'architecture historique a été restructurée en juillet 2026 pour fournir une arborescence plate, claire et fonctionnelle.
> Le point d'entrée principal est `scripts/run_postproc.py` (situé dans le répertoire parent `scripts/`).
> Consultez le [README principal](../README.md) pour l'utilisation globale.

---

## Architecture de `src/`

Le code est organisé par responsabilités fonctionnelles :

```text
src/
├── cli.py                      # Interface en ligne de commande (CLI)
├── runner.py                   # Orchestrateur principal (RecipeRunner)
│
├── core/                       # Chargement + validation YAML
│   ├── config.py               # Chargement configs globales
│   ├── experiments.py          # Objets Experiment
│   ├── variables.py            # Objets Variable
│   └── recipes.py              # Objets Recipe
│
├── io/                         # Lecture des données (NetCDF)
│   ├── lis.py                  # Extraction des sorties LIS
│   └── hymap.py                # Extraction des sorties HyMAP
│
├── diagnostics/                # Modules d'analyse métier (le "cœur" scientifique)
│   ├── assimilation/           # Diagnostics d'assimilation (innovations, incréments, spread)
│   ├── domain/                 # Génération de cartes de domaine (topographie, sols, bassins)
│   ├── hydrology/              # Validation hydrologique (séries temporelles, cartes)
│   ├── independent_ob_validation/ # Validation contre observations multi-sources (ESA CCI, GLEAM...)
│   └── runoff_partitioning/    # Partitionnement Qs/Qsb (ruissellement vs débit de base)
│
├── plotting/                   # Moteur de génération des figures (Cartopy/Matplotlib)
│   ├── maps.py                 # Cartographie générique
│   ├── timeseries.py           # Séries temporelles
│   └── distributions.py        # Histogrammes et boxplots
│
└── utils/                      # Fonctions utilitaires partagées
    ├── masking.py              # Masques terrestres et bassins
    ├── metrics.py              # Fonctions statistiques (RMSE, biais, corrélation)
    └── spatial_stats.py        # Agrégeations spatiales
```

---

## Les Diagnostics (`src/diagnostics/`)

Les modules dans `diagnostics/` correspondent directement aux dossiers de sortie qui seront générés dans `outputs/<name_main_dir>/figures/<name_exp>/`. Chaque dossier métier possède un fichier `adapter.py` qui sert de pont entre le `runner.py` générique et la logique métier spécifique.

1. **`assimilation/`** : Analyse les performances du filtre d'assimilation de données.
2. **`domain/`** : Dessine les cartes fixes du domaine (topographie, landcover).
3. **`hydrology/`** : Extrait et compare les variables hydrologiques (humidité, évapotranspiration, débits).
4. **`independent_ob_validation/`** : Géré dynamiquement via `dataset_registry.py` pour valider le modèle contre des jeux de données d'observation configurés dans `configs/observations/`.
5. **`runoff_partitioning/`** : Analyse le comportement de surface vs souterrain.

---

## Règles de Développement

1. **Aucun nom de variable ou d'expérience codé en dur** : Utilisez toujours les fichiers YAML du répertoire `configs/` pour déclarer vos variables et expériences.
2. **Nouveaux Diagnostics** : Pour ajouter un nouveau diagnostic, créez un dossier dans `src/diagnostics/` avec un `adapter.py` et référencez-le dans `runner.py`.
3. **Lazy Loading** : Les librairies lourdes (comme `cartopy` ou `matplotlib.pyplot`) doivent être importées *à l'intérieur* des fonctions qui les utilisent. Cela garantit que les commandes légères (comme `--help` ou `--dry-run`) s'exécutent instantanément et sans erreur, même si l'environnement Python n'est pas complet.

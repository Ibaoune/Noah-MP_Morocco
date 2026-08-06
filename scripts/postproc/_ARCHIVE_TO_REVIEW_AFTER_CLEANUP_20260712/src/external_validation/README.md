# External Validation Module
**Author:** M. EL Aabaribaoune (@um6p)

Ce module orchestre la validation indépendante du modèle (Noah-MP) en comparant ses sorties Open Loop (OL) et avec Assimilation de Données (DA) contre des jeux de données d'observation externes.

## Structure

- `config_external_validation.yaml` : Fichier de configuration principal (chemins, paramètres d'expérience, bascules d'activation des plots).
- `config.py` : Chargeur de configuration (mapping YAML vers variables Python).
- `main.py` : Point d'entrée de l'orchestrateur. Appelle les différents modules selon la configuration.
- `job_external_validation.sh` : Script bash permettant l'exécution (utile pour les environnements HPC).

## Modules d'Analyse

- **`plot_time_series.py`** : Génère les séries temporelles de bassin (TWS via GRACE, SM via ASCAT, ET via GLEAM, dynamique du LAI).
- **`plot_spatial_maps.py`** : Génère les cartes d'impact spatial des flux (E, T, ET, GPP, NPP) et les différences moyennes par saison.
- **`evaluate_ecosystems.py`** : Produit des boxplots de corrélations stratifiés par classes d'écosystèmes (Agricole, Forêts, etc.).
- **`evaluate_extremes.py`** : Analyse de la réponse spatiale du modèle face aux événements extrêmes (ex: sécheresse) et catégorisation des zones touchées.
- **`evaluate_streamflow.py`** : Valide le débit hydrologique routé (HyMAP) avec les données In-Situ (Stations).
- **`evaluate_gldas.py`** : Compare les performances des sorties LIS par rapport aux autres modèles Land Surface Models du catalogue GLDAS (NOAH, VIC, CLSM).

## Exécution

Pour lancer le module de validation, exécutez le script job associé :
```bash
bash job_external_validation.sh
```

Ou exécutez directement le `main.py` :
```bash
python main.py --config config_external_validation.yaml --matrix matrix_2016
```

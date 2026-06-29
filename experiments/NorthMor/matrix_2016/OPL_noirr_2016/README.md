# Expérience : OPL_noirr (2016-2020)
**Auteur : M. El Aabaribaoune (@um6p)**

## Description
Cette expérience représente la ligne de base (baseline) Open-Loop pour la période de 2016 à 2020.
L'irrigation est **désactivée** dans cette simulation. Elle sert de run de contrôle principal pour isoler l'impact de l'irrigation et de l'assimilation de données dans les expériences futures.

## Initialisation et Workflow
- **Initialisation** : La simulation démarre le 1er Janvier 2016 en utilisant le restart déterministe produit par le run de spin-up (`step1_spinup`).
- Fichier de restart initial utilisé : `LIS_RST_NOAHMP401_201601010000.d01.nc`
- **Exécution** : La simulation s'exécute de mois en mois grâce à un mécanisme de daisy-chaining géré par le script Python `scripts/chain_opl.py`. À la fin de chaque mois, le restart produit est copié dans le dossier `restarts/` et utilisé pour initialiser le mois suivant.

## Configuration Spécifique
- **Schéma d'irrigation** : `"none"`
- L'expérience utilise le fichier d'entrée standard LIS : `lis_input_NorthMor_5km.nc`.

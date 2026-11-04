# Calcul de CDF Matching — Domaine NorthMor

**Rôle** : Dépendance critique de production pour la simulation `DA_cdf_noirr_2016_2020`.

Ce répertoire contient l'ensemble des scripts de traitement LDT (Land Data Toolkit) et des fichiers de sortie NetCDF utilisés pour calculer les fonctions de répartition cumulée (CDF) de l'humidité du sol sur le domaine NorthMor ($180 \times 120$, 16 030 points continentaux) sur la période 2016–2020.

## Fichiers de Sortie Clés
* `OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc` : CDF d'humidité du sol du modèle Noah-MP (dérivée de 60 mois d'Open Loop `OPL_noirr_2016_2020`).
* `OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc` : CDF des observations satellitaires SMAP SPL3SMP_E.
* Fichiers de domaine associés : `*_domain.nc` (utilisés par le garde-fou `check_cdf_domain.py`).

## Scripts d'Exécution LDT
* `run_cdf.sh` : Script maître de soumission SLURM.
* `ldt.config.cdf.model.NorthMor` : Configuration LDT pour la CDF modèle.
* `ldt.config.cdf.obs.NorthMor` : Configuration LDT pour la CDF observation.
* `logs/` : Répertoire d'archivage des journaux SLURM et logs LDT d'exécution.

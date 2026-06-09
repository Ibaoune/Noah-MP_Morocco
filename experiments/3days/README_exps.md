# 3-Day Scalability & Assimilation Tests (Nie et al. 2022)

Ce dossier contient l'infrastructure de test permettant de valider les performances (Open Loop) et le fonctionnement des algorithmes d'assimilation de données (EnKF 1D) de LIS/Noah-MP sur une fenêtre temporelle réduite (2020-02-01 au 2020-02-04). 

L'objectif est de s'assurer de la robustesse du modèle (scalabilité, lecture des forçages/observations, perturbations) avant d'engager un long spin-up multi-décennal.

## 📂 Structure des Expériences

### 1. `opl/` (Open Loop)
C'est la simulation de référence sans assimilation. 
- **Configuration** : `lis.config`
- **Exécution** : `sbatch job_opl.sh`
- **Output** : `output/` et `logs/`

### 2. `assim_tests/` (Data Assimilation)
Ces expériences utilisent le filtre de Kalman d'Ensemble 1D (20 membres) en mode "coldstart" pour tester la mécanique d'assimilation de 3 jeux de données. 

Trois configurations sont disponibles :
- **`lis_da_smap.config`** : Assimilation de l'humidité du sol de surface (SMAP L3SMP v009).
- **`lis_da_lai.config`** : Assimilation de la végétation (MODIS LAI / Copernicus LAI).
- **`lis_da_joint.config`** : Assimilation conjointe SMAP + LAI.

**Exécution** (Via un script SLURM unique prenant la configuration en argument) :
```bash
sbatch job_da.sh lis_da_smap.config
sbatch job_da.sh lis_da_lai.config
sbatch job_da.sh lis_da_joint.config
```

## ⚙️ Paramètres Techniques
- **Modèle** : Noah-MP 4.0.1
- **Résolution** : 5km
- **Domaine** : Sebou–Saïss basin (Maroc)
- **Membres de l'Ensemble (DA)** : 20
- **Forçages** : MERRA-2 (Global) + GPM IMERG (Précipitations)
- **Perturbations** : Définies dans `data/pert_package/` (Méthode `GMAO-1D`)

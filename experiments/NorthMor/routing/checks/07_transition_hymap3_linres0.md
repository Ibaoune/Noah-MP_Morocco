# Note Technique : Transition vers HyMAP-3 et Désactivation du Réservoir Linéaire (`linres = 0`)

**Date :** 9 novembre 2026  
**Auteur :** Mohammad Elaabaribao  
**Contexte :** Retour technique et recommandations directes d'Augusto Getirana (NASA GSFC).

---

## 1. Contexte et Retours d'Augusto Getirana (NASA GSFC)

Suite à la transmission des premiers résultats comparatifs de débit à Lalla Chafia (2018) et aux interrogations soulevées sur les unités de `tbasflw`, l'interaction avec le plancher numérique `cntime` et la convergence du spin-up de nappe, Augusto Getirana a formulé trois recommandations directes :

1. **Adoption de HyMAP-3 :** Augusto préconise la bascule vers HyMAP-3 pour une meilleure stabilité numérique et afin d'anticiper la dépréciation définitive de HyMAP-2.
2. **Désactivation du réservoir linéaire (`linear reservoir flag: 0`) :** Le réservoir linéaire conceptuel de nappe et de ruissellement ne doit pas être utilisé conjointement avec un modèle de surface distribué physique comme Noah-MP.
3. **Origine du biais d'étiage estival :** Le maintien de débits trop élevés en été par rapport aux observations provient de la sur-génération de drainage profond/baseflow par Noah-MP. Côté routage, les flux entrants sont conservés et aucune altération artificielle du baseflow ne doit être opérée dans HyMAP.

---

## 2. Analyse Physique et Portée de `linear reservoir flag: 0`

### 2.1 Fonctionnement interne du code source (`HYMAP3_modelMod.F90`)
Lorsque `linres = 0`, la routine appelée à chaque pas de temps est `HYMAP3_no_reservoir_lis` :
```fortran
if (runoff0 /= rmis .and. basflw0 /= rmis) then
   runoff = runoff0 + basflw0
else
   runoff = 0.
endif
roffsto = 0.
basfsto = 0.
```

### 2.2 Résolution immédiate des anomalies antérieures
1. **Paramètre `tbasflw` :** N'est plus ingéré ni utilisé par la dynamique d'écoulement. L'incertitude sur ses unités (secondes vs jours) devient sans objet.
2. **Plancher numérique `cntime` :** La condition de seuillage `tbsflw >= cntime/86400` n'est plus évaluée.
3. **Puits d'accumulation de nappe (`BSFSTO`) :** Le volume d'eau en nappe reste strictement nul (`BaseflowStor = 0.0 m³`).
4. **Protocole de spin-up :** Le spin-up de nappe sur plusieurs cycles (C1/C2) est éliminé. Seul le stockage fluvial (`RiverStor`) nécessite un amorçage hydraulique, dont le temps caractéristique de convergence est de l'ordre de quelques jours (temps de transit fluvial sur les bassins marocains < 2 semaines). Un spin-up d'une année (2016 coldstart) est donc largement sur-conservateur et garantit une initialisation parfaite.

---

## 3. Matrice des Configurations et Scripts HyMAP-3

Six configurations et scripts SLURM ont été déployés pour couvrir les trois expériences de 2016 à 2020 :

| Expérience | Étape | Fichier lis.config | Script SLURM | Répertoire de sortie |
| :--- | :---: | :--- | :--- | :--- |
| **Open-Loop (OPL)** | Spin-up 2016 | `lis_hymap3_opl_spinup_2016.config` | `run_hymap3_opl_spinup_2016.sh` | `output/HYMAP3_OPL_spinup_2016` |
| **Open-Loop (OPL)** | Prod 2016-2020 | `lis_hymap3_opl_2016_2020.config` | `run_hymap3_opl_2016_2020.sh` | `output/HYMAP3_OPL_2016_2020` |
| **DA SMAP sans CDF** | Spin-up 2016 | `lis_hymap3_da_nocdf_spinup_2016.config` | `run_hymap3_da_nocdf_spinup_2016.sh` | `output/HYMAP3_DA_nocdf_spinup_2016` |
| **DA SMAP sans CDF** | Prod 2016-2020 | `lis_hymap3_da_nocdf_2016_2020.config` | `run_hymap3_da_nocdf_2016_2020.sh` | `output/HYMAP3_DA_nocdf_2016_2020` |
| **DA SMAP avec CDF** | Spin-up 2016 | `lis_hymap3_da_cdf_spinup_2016.config` | `run_hymap3_da_cdf_spinup_2016.sh` | `output/HYMAP3_DA_cdf_spinup_2016` |
| **DA SMAP avec CDF** | Prod 2016-2020 | `lis_hymap3_da_cdf_2016_2020.config` | `run_hymap3_da_cdf_2016_2020.sh` | `output/HYMAP3_DA_cdf_2016_2020` |

### Script d'orchestration globale
Le script `launch_all_hymap3_pipeline.sh` gère la soumission automatisée avec dépendance d'exécution (`sbatch --dependency=afterok:$JID_SP`) :
```bash
./experiments/NorthMor/routing/jobs/launch_all_hymap3_pipeline.sh all
```

---

## 4. Validation Expérimentale Préliminaire
Un test numérique d'amorçage sur 1 jour a confirmé :
- La bonne initialisation de `HYMAP3 router` avec `LIS HYMAP3 runoff output`.
- La compatibilité descendante totale avec `ldt_hymap/lis_input_corrigee.d01.nc`.
- La production conforme des fichiers de sortie et de restart NetCDF (`LIS_RST_HYMAP3_router_*.nc`).
- L'invariance de masse et l'annulation stricte de `BaseflowStor` et `RunoffStor`.

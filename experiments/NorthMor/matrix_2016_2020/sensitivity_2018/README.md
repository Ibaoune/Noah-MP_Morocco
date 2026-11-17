# Simulations de Sensibilité 2018 — Domaine NorthMor (LIS/Noah-MP 4.0.1)

**Auteur** : mohammad.elaabaribao  
**Dépôt** : `Noah-MP_Morocco`  
**Date de préparation** : 17 Novembre 2026  
**Statut** : PRÊT POUR VALIDATION UTILISATEUR — AUCUN JOB SOUMIS (POINT D'ARRÊT RESPECTÉ)

---

## 1. Contexte et Objectifs

Cette matrice d'expériences de sensibilité sur l'année 2018 (année hydrologique charnière avec crues de mars-avril et fort séchage estival) vise à tester deux hypothèses complémentaires formulées dans le cadre de l'audit SMAP / Noah-MP :

1. **Hypothèse Physique (Étape B)** : L'option standard de résistance de surface du sol nu de Sakaguchi & Zeng (2009) (`OPT_RSF = 1`) impose une dépendance explicite à $\text{SMCWLT}$ au dénominateur :
   $$D_{\text{RSURF}} = 2.2 \times 10^{-5} \cdot \theta_{\text{sat}}^2 \cdot \left(1 - \frac{\text{SMCWLT}}{\theta_{\text{sat}}}\right)^{2 + 3/b}$$
   Lorsque $\theta \to \text{SMCWLT}$, la résistance $R_{\text{surf}}$ tend vers l'infini, paralysant l'évaporation du sol nu et forçant un plancher artificiel. L'option alternative de Sellers (1992) (`OPT_RSF = 2`) :
   $$R_{\text{surf}} = \exp\left(8.25 - 4.225 \cdot \frac{\theta}{\theta_{\text{sat}}}\right)$$
   est indépendante de $\text{SMCWLT}$ et permet un séchage régulier sous le point de flétrissement.
2. **Hypothèse Assimilation (Étape C)** : Dans `DA_nocdf_noirr`, le filtre de contrôle qualité de LIS (`noahmp401_qc_soilmobs.F90`, condition `smobs - smcwlt < 0.02`) censure 43 % à 78 % des observations SMAP au printemps et 73 % à 100 % en été sur sols fins. En désactivant cette censure via le binaire patché `lisf_nowilt`, SMAP peut enfin corriger l'état d'humidité du modèle vers des valeurs sèches réalistes.

---

## 2. Inventaire des Expériences Préparées

| Répertoire | Expérience | Type | Période | Sortie | Résistance Sol (`OPT_RSF`) | Binaire LIS |
|:-----------|:-----------|:----:|:-------:|:------:|:--------------------------:|:------------|
| `OL_ctrl_hourly_2018/` | **OL_ctrl_hourly_2018** | Open-Loop (déterministe) | 2018-01-01 au 2019-01-01 | **1 heure** (inst + tavg) | 1 (Sakaguchi & Zeng 2009) | `src/lisf/lis/make/LIS` (Production) |
| `OL_rsf2_hourly_2018/` | **OL_rsf2_hourly_2018** | Open-Loop (déterministe) | 2018-01-01 au 2019-01-01 | **1 heure** (inst + tavg) | 2 (Sellers 1992) | `src/lisf/lis/make/LIS` (Production) |
| `DA_nocdf_nowilt_2018/`| **DA_nocdf_nowilt_2018** | Assimilation EnKF (20 membres) | 2018-01-01 au 2019-01-01 | 1 jour (DAOBS, incréments, spread) | 1 (Sakaguchi & Zeng 2009) | `src/lisf_nowilt/lis/LIS` (Patché sans filtre flétrissement) |
| `routing_DA_nocdf_nowilt_2018/` | **HyMAP2_nowilt_2018** | Routage hydrodynamique | 2018-01-01 au 2019-01-01 | 1 jour (débits aux stations) | N/A | `src/lisf/lis/make/LIS` (Production) |

---

## 3. Détail des Fichiers et Diffs de Configuration

### Étape B.1 — OL_ctrl_hourly_2018
- **Configuration** : `config/lis_OL_ctrl_hourly_2018.config`
- **Fichier de Restart** :  
  `experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/restarts/LIS_RST_NOAHMP401_201801010000.d01.nc`
- **Table des sorties** :  
  `shared/MODEL_OUTPUT_LIST_hourly.TBL` (active `timeAvgOpt = 2` pour `SoilMoist` [4 couches], `Evap`, `ECanop`, `TVeg`, `ESoil`, `Qs`, `Qsb`).
- **Diff avec la production OPL_noirr_2016_2020** :
  - `Surface model output interval: 1hr` (au lieu de `1da`)
  - Durée continue de 1 an (au lieu de relances mensuelles par chaîne Python)
  - `Model output attributes file: .../shared/MODEL_OUTPUT_LIST_hourly.TBL`
- **Script Slurm** : `jobs/run_OL_ctrl_hourly_2018.sh`
- **Ressources demandées** : 1 nœud, 32 tâches MPI, partition `DEFAULT-CPU`, walltime `03:30:00`.
- **Estimation temps de calcul** : **~2 h 20 min** (basé sur 11m45s par mois en production).
- **Protocole de validation** : `scripts/verify_reproduce_opl.py` agrège les sorties horaires en moyennes journalières et vérifie l'accord exact ($\Delta < 10^{-6}$) avec `OPL_noirr`.

### Étape B.2 — OL_rsf2_hourly_2018
- **Configuration** : `config/lis_OL_rsf2_hourly_2018.config`
- **Fichier de Restart** : Identique à OL_ctrl (`LIS_RST_NOAHMP401_201801010000.d01.nc`).
- **Diff avec OL_ctrl_hourly_2018** :
  ```diff
  -Noah-MP.4.0.1 surface resistance option:                      1
  +Noah-MP.4.0.1 surface resistance option:                      2  # 2=Sellers (1992)
  ```
- **Script Slurm** : `jobs/run_OL_rsf2_hourly_2018.sh`
- **Ressources demandées** : 1 nœud, 32 tâches MPI, walltime `03:30:00`.
- **Estimation temps de calcul** : **~2 h 20 min**.

---

### Étape C.1 — DA_nocdf_nowilt_2018
- **Configuration** : `config/lis_DA_nocdf_nowilt_2018.config`
- **Binaire** : `src/lisf_nowilt/lis/LIS` (issu du patch `patches/lisf_nowilt_qc_wilting.patch` supprimant la condition `smobs - smcwlt < 0.02`).
- **Fichiers de Restarts utilisés** :
  1. Surface restart :  
     `experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc`
  2. Perturbations restart :  
     `experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201801010000.d01.bin`
- **Diff avec DA_nocdf_noirr_2016_2020 de production** :
  - Utilisation du binaire `lisf_nowilt` au lieu du binaire standard.
  - Exécution continue sur l'année 2018.
  - Toutes les options de diagnostics d'assimilation conservées :
    - `Data assimilation output processed observations: 1` (`DAOBS`)
    - `Data assimilation exclude analysis increments: 0` (incréments sauvegardés)
    - `Data assimilation output ensemble spread: 1`
- **Script Slurm** : `jobs/run_DA_nocdf_nowilt_2018.sh`
- **Ressources demandées** : 1 nœud, 32 tâches MPI, walltime `24:00:00`.
- **Estimation temps de calcul** : **~18 heures** (basé sur 1h33 par mois pour 20 membres en production).

### Étape C.2 — Routage HyMAP2 (routing_DA_nocdf_nowilt_2018)
- **Configuration** : `config/lis_hymap2_da_nocdf_nowilt_2018.config`
- **Fichier de Restart HyMAP** :  
  `experiments/NorthMor/routing/output/DA_nocdf_2016_2020/ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc`
- **Pipeline d'exécution** :
  1. `scripts/remap_runoff_nowilt_2018.py` : remap conservatif du ruissellement journalier ($Q_s, Q_{sb}$) vers la grille 180×120.
  2. Routage HyMAP2 avec le binaire de production.
- **Diff avec le routage DA_nocdf 2016–2020** :
  - Année 2018 uniquement au lieu de 5 ans continus.
  - Entrées de ruissellement pointant vers le dossier remappé de `DA_nocdf_nowilt_2018`.
- **Script Slurm** : `jobs/run_hymap2_da_nocdf_nowilt_2018.sh`
- **Ressources demandées** : 1 nœud, 16 tâches MPI, walltime `00:30:00`.
- **Estimation temps de calcul** : **~15 minutes** (remapping ~2 min + routage ~12 min).

---

## 4. Analyse et Documentation du Comportement de `noahmp401_setsoilm.F90`

L'analyse détaillée du code source `lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90` révèle les règles suivantes de troncature d'état lors de l'application des incréments d'assimilation :

1. **Seuil Minimal de Troncature d'État** :
   ```fortran
   real, parameter :: MIN_THRESHOLD = 0.02  ! 2% volumique
   ```
   **Constat capital** : L'état du modèle n'est **JAMAIS** tronqué par le point de flétrissement $\text{SMCWLT}$ dans la routine de mise à jour EnKF ! La valeur plancher imposée par le code d'assimilation est universellement fixée à `0.02 m³/m³`.
2. **Critère d'acceptation de l'incrément** :
   Pour chaque couche $j \in \{1, 2, 3, 4\}$ :
   ```fortran
   if (sh2o(j) + delta(j) > MIN_THRESHOLD .and. &
       sh2o(j) + delta(j) < sm_threshold .and. &
       tslb(j) > LIS_CONST_TKFRZ) then
   ```
   où `sm_threshold = SMCMAX - 0.02`. L'incrément est donc accepté dès que l'humidité résultante reste dans l'intervalle $[0.02, \theta_{\text{sat}} - 0.02]$.
3. **Implication directe** :
   Le blocage artificiel observé dans `DA_nocdf_noirr` ne provenait donc **pas** de `noahmp401_setsoilm.F90`, mais résultait uniquement du filtre de rejet en amont dans `noahmp401_qc_soilmobs.F90` (`smobs - smcwlt < 0.02`). En levant ce filtre, les incréments EnKF s'appliqueront sans entrave jusqu'à 0.02 m³/m³.

# Rapport Step A0b — Correction des tables de définition (sans nouveau run)

**Date de génération :** 2026-11-23 21:35:57
**Règle absolue :** Aucun chiffre ni libellé tapé à la main ; tout est extrait par script depuis le code source, les configs et les logs, avec citations fichier:ligne dans la colonne `evidence`.

## 1. Tableau final des définitions d'expériences 2018 (`paper1/tables/experiment_definitions_2018.csv`)

| Expérience | Forçages perturbés | État perturbé | Recentrage (`pert_bias_corr`) | Contrôle Wilting | CDF matching | Binaire utilisé | Preuve Recentrage | Preuve Wilting |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OL_DAIC** | none | none | `N/A` | `N/A (pas d'obs)` | none | `./src/lisf/lis/make/LIS` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/config/lis_OL_DAIC_2018.config:156 (State perturbation algorithm: none)` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/config/lis_OL_DAIC_2018.config:70 (Number of data assimilation instances: 0)` |
| **ENS_OPL** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `N/A (pas d'obs)` | none | `./src/lisf/lis/make/LIS` | `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/config/lis_ENS_OPL_2018.config:96 (Apply perturbation bias correction:        0) ignorée` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/config/lis_ENS_OPL_2018.config:70 (Number of data assimilation instances: 0)` |
| **ENS_corr** | GMAO scheme (1hr, forcing_pertattribs.txt) | none | `N/A` | `N/A (pas d'obs)` | none | `./src/lisf_corr/lis/LIS` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/config/lis_ENS_corr_2018.config:168 (State perturbation algorithm: none) ; code src/lisf_corr/lis/core/LIS_readConfig.F90:794 lit config (experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/config/lis_ENS_corr_2018.config:96=0), confirmé experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/logs/lislog_ENS_corr_2018.0000:4` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/config/lis_ENS_corr_2018.config:70 (Number of data assimilation instances: 0)` |
| **DA_nocdf** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `actif` | none | `./src/lisf/lis/LIS` | `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_nocdf_noirr_2018-01.config:96 (Apply perturbation bias correction:        0) ignorée` | `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:272 (ligne active: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |
| **DA_nocdf_nowilt** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `désactivé` | none | `./src/lisf_nowilt/lis/LIS` | `src/lisf_nowilt/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/config/lis_DA_nocdf_nowilt_2018.config:96 (Apply perturbation bias correction:        0) ignorée` | `src/lisf_nowilt/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:273 (ligne commentée: ! elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |
| **DA_corr** | GMAO scheme (1hr, forcing_pertattribs.txt) | none | `N/A` | `désactivé` | none | `./src/lisf_corr/lis/LIS` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/config/lis_DA_corr_2018.config:168 (State perturbation algorithm: none) ; code src/lisf_corr/lis/core/LIS_readConfig.F90:794 lit config (experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/config/lis_DA_corr_2018.config:96=0), confirmé experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/logs/lislog_DA_corr_2018.0000:4` | `src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:273 (ligne commentée: ! elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |
| **DA_cdf** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `actif` | CDF matching (100 bins) | `./src/lisf/lis/LIS` | `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_cdf_noirr_2018-01.config:96 (Apply perturbation bias correction:        0) ignorée` | `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:272 (ligne active: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |

## 2. Tableau des contrastes 2018 régénéré (`paper1/tables/contrasts_definition.csv`)

| Contraste | Run X | Run Y | Objectif | Différences réelles entre runs | Preuve |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ENS_OPL - OL_DAIC** | `ENS_OPL` | `OL_DAIC` | Effet ensemble et perturbations standard | Ensemble 20 membres vs 1 membre ; forçages perturbés (GMAO 1hr) vs none ; état perturbé (GMAO 3hr) vs none ; binaire standard make/LIS dans les deux runs | `lis_ENS_OPL_2018.config:43,167,168 vs lis_OL_DAIC_2018.config:43,155,156 ; run_ENS_OPL_2018.sh:17 vs run_OL_DAIC_2018.sh:18` |
| **ENS_corr - OL_DAIC** | `ENS_corr` | `OL_DAIC` | Effet ensemble (forçages perturbés, sans perturbation d état) | Ensemble 20 membres vs 1 membre ; forçages perturbés (GMAO 1hr) vs none ; état non perturbé (none) dans les deux runs ; binaire lisf_corr vs make/LIS | `lis_ENS_corr_2018.config:43,167,168 vs lis_OL_DAIC_2018.config:43,155,156 ; run_ENS_corr_2018.sh:17 vs run_OL_DAIC_2018.sh:18` |
| **DA_nocdf - ENS_OPL** | `DA_nocdf` | `ENS_OPL` | Effet net de l assimilation SMAP native (production) | Assimilation EnKF SMAP active (1 instance) vs inactive (0 instance) ; mêmes perturbations forçages (GMAO 1hr) et état (GMAO 3hr) ; même binaire standard src/lisf | `lis_DA_SMAP_nocdf_noirr_2018-01.config:70,71 vs lis_ENS_OPL_2018.config:70,71 ; même binaire ./src/lisf/lis/LIS (make/LIS)` |
| **DA_nocdf_nowilt - DA_nocdf** | `DA_nocdf_nowilt` | `DA_nocdf` | Effet spécifique du filtre de flétrissement | Seuil de flétrissement désactivé dans QC SMAP (noahmp401_qc_soilmobs.F90:273 commenté) vs actif (ligne 272) ; binaire lisf_nowilt vs src/lisf ; toutes les autres options et forçages identiques | `src/lisf_nowilt/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:273 vs src/lisf/.../noahmp401_qc_soilmobs.F90:272 ; run_DA_nocdf_nowilt_2018.sh:17` |
| **DA_corr - ENS_corr** | `DA_corr` | `ENS_corr` | Effet net de l assimilation SMAP avec binaire lisf_corr (sans perturbation d état) | Assimilation EnKF SMAP active (1 instance, seuil flétrissement désactivé) vs inactive (0 instance) ; binaire lisf_corr dans les deux runs ; aucune perturbation d état (none) dans les deux runs | `lis_DA_corr_2018.config:70,71,168 vs lis_ENS_corr_2018.config:70,71,168 ; run_DA_corr_2018.sh:17 vs run_ENS_corr_2018.sh:17` |
| **DA_cdf - DA_nocdf** | `DA_cdf` | `DA_nocdf` | Effet de la mise à l échelle climatologique par CDF matching | Stratégie de mise à l échelle: CDF matching (100 bins) vs none (retrievals natifs) ; même binaire standard src/lisf ; mêmes perturbations GMAO | `lis_DA_SMAP_cdf_noirr_2018-01.config:77,89 vs lis_DA_SMAP_nocdf_noirr_2018-01.config:77` |

## 3. Description factuelle et Diff réel de `lisf_corr` vs `src/lisf`

**Phrase factuelle normalisée :**
> Diffère de src/lisf uniquement par deux modifications : la désactivation du seuil de flétrissement dans le contrôle qualité SMAP (noahmp401_qc_soilmobs.F90:273-275) et la lecture effective du paramètre de recentrage des perturbations depuis lis.config (LIS_readConfig.F90:793-796).

**Nombre de fichiers sources modifiés :** 2

- `core/LIS_readConfig.F90`
- `surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90`

### Patchs unifiés complets des fichiers modifiés :

```diff
--- /srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/core/LIS_readConfig.F90	2026-05-19 23:47:00.000000000 +0100
+++ /srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf_corr/lis/core/LIS_readConfig.F90	2026-11-22 03:04:41.000000000 +0100
@@ -791,11 +791,9 @@
   call LIS_parseTimeString(time,LIS_rc%pertrestartInterval)
 
   LIS_rc%pert_bias_corr = 1
-!  if(npert_forc.ne.0.or.npert_state.ne.0) then 
-!     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
-!          label="Apply perturbation bias correction:",rc=rc)
-!     call LIS_verify(rc,'Apply perturbation bias correction: not specified')
-!  endif
+  call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
+       label="Apply perturbation bias correction:",default=1,rc=rc)
+  write(LIS_logunit,*) '[CONFIG] Apply perturbation bias correction: ', LIS_rc%pert_bias_corr
 
 !  if(npert_forc.ne.0.or.npert_state.ne.0.or.npert_obs.ne.0) then 
   call ESMF_ConfigFindLabel(LIS_config,"Perturbations restart filename:",rc=rc)
```

```diff
--- /srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90	2026-05-19 23:47:02.000000000 +0100
+++ /srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90	2026-11-22 02:11:02.000000000 +0100
@@ -269,8 +269,9 @@
 !too close to the tails, could be due to scaling, so reject. 
         elseif(smcmax_obs(t)-smobs(t).lt.0.02) then 
            smobs(t) = LIS_rc%udef
-        elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then 
-           smobs(t) = LIS_rc%udef
+! TEST NOWILT : seuil de fletrissement commente pour audit DA-NoCDF
+!        elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then 
+!           smobs(t) = LIS_rc%udef
         endif
      endif
   enddo
```

## 4. Comparaison des observations assimilées en 2018 (Domaine + 3 bassins)

Vérification chiffrée de la cause des +74 % d'observations entre `DA_nocdf` et `DA_corr` :

| Région / Bassin | Jours DA_nocdf | Obs DA_nocdf | Jours DA_nocdf_nowilt | Obs DA_nocdf_nowilt | Jours DA_corr | Obs DA_corr | Écart nowilt - nocdf | Écart corr - nocdf | Écart corr - nowilt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Domaine complet** | 357 | 1611015 | 357 | 2789143 | 357 | 2806399 | +1178128 (+73.1 %) | +1195384 (+74.2 %) | +17256 (+0.6 %) |
| **Lalla Chafia** | 220 | 30168 | 220 | 36252 | 220 | 36274 | +6084 (+20.2 %) | +6106 (+20.2 %) | +22 (+0.1 %) |
| **Sidi Jabeur** | 217 | 27986 | 220 | 34965 | 220 | 34995 | +6979 (+24.9 %) | +7009 (+25.0 %) | +30 (+0.1 %) |
| **Sebou amont** | 260 | 33175 | 260 | 37405 | 260 | 37570 | +4230 (+12.8 %) | +4395 (+13.2 %) | +165 (+0.4 %) |

**Constat chiffré :**

- Le passage de `DA_nocdf` (wilting actif) à `DA_nocdf_nowilt` (wilting désactivé) fait passer le nombre d'observations de 1 611 015 à 2 789 143 (+73,1 % sur le domaine complet).
- Le passage de `DA_nocdf_nowilt` à `DA_corr` (wilting désactivé dans les deux cas, différence sur la perturbation d'état) n'ajoute que 17 256 observations (+0,6 % sur le domaine complet).
- La différence de configuration expliquant les +74 % d'observations est donc le contrôle de flétrissement (`smobs(t) - smcwlt_obs(t) < 0.02`).

## 5. Sortie brute des grep (preuves directes du code source, configs et logs)

### Preuve `OL_DAIC_recentering` (src/lisf/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 795: !     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
```
- Configuration associée : ligne 84: `Apply perturbation bias correction:        0`

### Preuve `OL_DAIC_wilting` (src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 272: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                0`

### Preuve `ENS_OPL_recentering` (src/lisf/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 795: !     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
```
- Configuration associée : ligne 96: `Apply perturbation bias correction:        0`

### Preuve `ENS_OPL_wilting` (src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 272: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                0`

### Preuve `ENS_corr_recentering` (src/lisf_corr/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 794: call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
 796: write(LIS_logunit,*) '[CONFIG] Apply perturbation bias correction: ', LIS_rc%pert_bias_corr
```
- Configuration associée : ligne 96: `Apply perturbation bias correction:        0`

### Preuve `ENS_corr_wilting` (src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 273: !        elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                0`

### Preuve `DA_nocdf_recentering` (src/lisf/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 795: !     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
```
- Configuration associée : ligne 96: `Apply perturbation bias correction:        0`

### Preuve `DA_nocdf_wilting` (src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 272: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                1`

### Preuve `DA_nocdf_nowilt_recentering` (src/lisf_nowilt/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 795: !     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
```
- Configuration associée : ligne 96: `Apply perturbation bias correction:        0`

### Preuve `DA_nocdf_nowilt_wilting` (src/lisf_nowilt/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 273: !        elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                1`

### Preuve `DA_corr_recentering` (src/lisf_corr/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 794: call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
 796: write(LIS_logunit,*) '[CONFIG] Apply perturbation bias correction: ', LIS_rc%pert_bias_corr
```
- Configuration associée : ligne 96: `Apply perturbation bias correction:        0`

### Preuve `DA_corr_wilting` (src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 273: !        elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                1`

### Preuve `DA_cdf_recentering` (src/lisf/lis/core/LIS_readConfig.F90)
```text
 793: LIS_rc%pert_bias_corr = 1
 795: !     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
```
- Configuration associée : ligne 96: `Apply perturbation bias correction:        0`

### Preuve `DA_cdf_wilting` (src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90)
```text
  84: real                     :: smcwlt_obs(LIS_rc%obs_ngrid(k))
 171: smcwlt_obs)
 272: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then
```
- Instance DA dans config : ligne 70: `Number of data assimilation instances:                1`


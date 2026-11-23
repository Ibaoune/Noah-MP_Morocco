# Rapport Step A0b/A0c — Définition des expériences et audit des contrastes (sans nouveau run)

**Date de mise à jour :** 2026-11-23 21:59:21
**Règle absolue :** Extraction 100 % scriptée depuis code source, configs et logs. Aucune interprétation subjective, colonnes evidence avec citations fichier:ligne.

## 1. Tableau final des définitions d'expériences 2018 (`paper1/tables/experiment_definitions_2018.csv`)

| Expérience | Forçages perturbés | État perturbé | Recentrage (`recentering_bias_corr`) | Contrôle Wilting | CDF matching | Binaire utilisé | Preuve Recentrage (`evidence`) | Preuve Wilting (`evidence`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OL_DAIC** | none | none | `N/A (setsoilm non appelé)` | `N/A (pas d'obs)` | none | `./src/lisf/lis/make/LIS` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/config/lis_OL_DAIC_2018.config:156 (State perturbation algorithm: none) ; experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/config/lis_OL_DAIC_2018.config:70 (Number of data assimilation instances: 0) ; noahmp401_setsoilm.F90 non appelé` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/config/lis_OL_DAIC_2018.config:70 (Number of data assimilation instances: 0)` |
| **ENS_OPL** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `N/A (pas d'obs)` | none | `./src/lisf/lis/make/LIS` | `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/config/lis_ENS_OPL_2018.config:96 (Apply perturbation bias correction:        0) ignorée ; appelé via noahmp401_setsoilm.F90:361,869 (perturbation état)` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/config/lis_ENS_OPL_2018.config:70 (Number of data assimilation instances: 0)` |
| **ENS_corr** | GMAO scheme (1hr, forcing_pertattribs.txt) | none | `N/A (setsoilm non appelé)` | `N/A (pas d'obs)` | none | `./src/lisf_corr/lis/LIS` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/config/lis_ENS_corr_2018.config:168 (State perturbation algorithm: none) ; experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/config/lis_ENS_corr_2018.config:70 (Number of data assimilation instances: 0) ; noahmp401_setsoilm.F90 non appelé` | `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/config/lis_ENS_corr_2018.config:70 (Number of data assimilation instances: 0)` |
| **DA_nocdf** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `actif` | none | `./src/lisf/lis/LIS` | `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_nocdf_noirr_2018-01.config:96 (Apply perturbation bias correction:        0) ignorée ; appelé via noahmp401_setsoilm.F90:361,869 (perturbation état et DA EnKF)` | `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:272 (ligne active: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |
| **DA_nocdf_nowilt** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `désactivé` | none | `./src/lisf_nowilt/lis/LIS` | `src/lisf_nowilt/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/config/lis_DA_nocdf_nowilt_2018.config:96 (Apply perturbation bias correction:        0) ignorée ; appelé via noahmp401_setsoilm.F90:361,869 (perturbation état et DA EnKF)` | `src/lisf_nowilt/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:273 (ligne commentée: ! elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |
| **DA_corr** | GMAO scheme (1hr, forcing_pertattribs.txt) | none | `0 (lu config, confirmé lislog)` | `désactivé` | none | `./src/lisf_corr/lis/LIS` | `src/lisf_corr/lis/core/LIS_readConfig.F90:794 ; experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/config/lis_DA_corr_2018.config:96 (valeur 0) ; experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/logs/lislog_DA_corr_2018.0000:4 ; appelé via noahmp401_setsoilm.F90:361,869 (DA EnKF)` | `src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:273 (ligne commentée: ! elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |
| **DA_cdf** | GMAO scheme (1hr, forcing_pertattribs.txt) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | `forcé=1 (option config ignorée)` | `actif` | CDF matching (100 bins) | `./src/lisf/lis/LIS` | `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_cdf_noirr_2018-01.config:96 (Apply perturbation bias correction:        0) ignorée ; appelé via noahmp401_setsoilm.F90:361,869 (perturbation état et DA EnKF)` | `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:272 (ligne active: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)` |

## 2. Tableau des contrastes 2018 généré par script (`paper1/tables/contrasts_definition.csv`)

| Contraste | Run X | Run Y | Objectif | Binaire md5 | Différences réelles entre runs (générées par script) |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **ENS_OPL - OL_DAIC** | `ENS_OPL` | `OL_DAIC` | Effet ensemble et perturbations standard | `identique` | [Binaire]: identique (md5: 04150c14 vs 04150c14) | [Table]: forcing_perturbation [GMAO scheme (1hr, forcing_pertattribs.txt) vs none]; state_perturbation [GMAO scheme (3hr, noahmp_sm_pertattribs.txt) vs none]; recentering_bias_corr [forcé=1 (option config ignorée) vs N/A (setsoilm non appelé)]; initial_state [/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc vs /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc] | [Config]: 32 clés différentes (Data assimilation algorithm: "EnKF" vs "none"; Data assimilation number of observation types: 1 vs 0; Data assimilation observation domain file: ./data/lis_input/lis_input_NorthMor_5km.nc vs ABSENT; Data assimilation output ensemble spread: 1 vs 0; Data assimilation output innovations: 1 vs 0 ; ... et 27 autres) |
| **ENS_corr - OL_DAIC** | `ENS_corr` | `OL_DAIC` | Effet ensemble (forçages perturbés, sans perturbation d état) | `différent` | [Binaire]: différent (md5: 2f0f2984 vs 04150c14) | [Table]: forcing_perturbation [GMAO scheme (1hr, forcing_pertattribs.txt) vs none]; binary_used [./src/lisf_corr/lis/LIS vs ./src/lisf/lis/make/LIS]; initial_state [/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc vs /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc] | [Config]: 31 clés différentes (Data assimilation algorithm: "EnKF" vs "none"; Data assimilation number of observation types: 1 vs 0; Data assimilation observation domain file: ./data/lis_input/lis_input_NorthMor_5km.nc vs ABSENT; Data assimilation output ensemble spread: 1 vs 0; Data assimilation output innovations: 1 vs 0 ; ... et 26 autres) |
| **DA_nocdf - ENS_OPL** | `DA_nocdf` | `ENS_OPL` | Effet net de l assimilation SMAP native (production) | `identique` | [Binaire]: identique (md5: 04150c14 vs 04150c14) | [Table]: wilting_criterion [actif vs N/A (pas d'obs)]; binary_used [./src/lisf/lis/LIS vs ./src/lisf/lis/make/LIS] | [Config]: 1 clés différentes (Number of data assimilation instances: 1 vs 0) |
| **DA_nocdf_nowilt - DA_nocdf** | `DA_nocdf_nowilt` | `DA_nocdf` | Effet spécifique du filtre de flétrissement | `différent` | [Binaire]: différent (md5: 748798ad vs 04150c14) | [Table]: wilting_criterion [désactivé vs actif]; binary_used [./src/lisf_nowilt/lis/LIS vs ./src/lisf/lis/LIS] | [Config]: 0 clé différente |
| **DA_corr - ENS_corr** | `DA_corr` | `ENS_corr` | Effet net de l assimilation SMAP avec binaire lisf_corr (sans perturbation d état) | `identique` | [Binaire]: identique (md5: 2f0f2984 vs 2f0f2984) | [Table]: recentering_bias_corr [0 (lu config, confirmé lislog) vs N/A (setsoilm non appelé)]; wilting_criterion [désactivé vs N/A (pas d'obs)] | [Config]: 1 clés différentes (Number of data assimilation instances: 1 vs 0) |
| **DA_cdf - DA_nocdf** | `DA_cdf` | `DA_nocdf` | Effet de la mise à l échelle climatologique par CDF matching | `identique` | [Binaire]: identique (md5: 04150c14 vs 04150c14) | [Table]: cdf_matching [CDF matching (100 bins) vs none]; initial_state [/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc vs /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc] | [Config]: 5 clés différentes (Data assimilation scaling strategy: "CDF matching" vs "none"; Noah-MP.4.0.1 restart file: /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc vs /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc; Perturbations restart filename: "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201801010000.d01.bin" vs "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201801010000.d01.bin"; SMAP(NASA) model CDF file: ./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_model_NorthMor/noahmp_model_cdf_NorthMor.nc vs ./data/cdf/smap_model_cdf.nc; SMAP(NASA) observation CDF file: ./experiments/NorthMor/matrix_2016_2020/CDF/OUTPUT_obs_NorthMor/smap_obs_cdf_NorthMor.nc vs ./data/cdf/smap_obs_cdf.nc) |

## 3. Synthèse md5 des binaires et diff factuel `lisf_corr` vs `src/lisf`

### Checksums md5 des exécutables :

```text
./src/lisf/lis/make/LIS        -> 04150c14d7bcee2f83567688254b5a95
./src/lisf/lis/LIS             -> 04150c14d7bcee2f83567688254b5a95
./src/lisf_nowilt/lis/LIS      -> 748798ad2db5ec35fa692dc6bc48633e
./src/lisf_corr/lis/LIS        -> 2f0f29844cabc2e915dfac310391e31d
```

**Description factuelle de `lisf_corr` :**
> Diffère de src/lisf uniquement par deux modifications : la désactivation du seuil de flétrissement dans le contrôle qualité SMAP (noahmp401_qc_soilmobs.F90:273-275) et la lecture effective du paramètre de recentrage des perturbations depuis lis.config (LIS_readConfig.F90:793-796).

**Fichiers sources modifiés :** 2

- `core/LIS_readConfig.F90`
- `surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90`

### Patchs unifiés des fichiers sources modifiés :

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

Tableau calculé directement par script depuis les fichiers NetCDF `*_innov.*.nc` :

| Région / Bassin | Jours DA_nocdf | Obs DA_nocdf | Jours DA_nocdf_nowilt | Obs DA_nocdf_nowilt | Jours DA_corr | Obs DA_corr | Écart nowilt - nocdf | % rejetées par wilting | Écart corr - nocdf | Écart corr - nowilt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Domaine complet** | 357 | 1611015 | 357 | 2789143 | 357 | 2806399 | +1178128 (+73.1 %) | **42.24 %** | +1195384 (+74.2 %) | +17256 (+0.6 %) |
| **Lalla Chafia** | 220 | 30168 | 220 | 36252 | 220 | 36274 | +6084 (+20.2 %) | **16.78 %** | +6106 (+20.2 %) | +22 (+0.1 %) |
| **Sidi Jabeur** | 217 | 27986 | 220 | 34965 | 220 | 34995 | +6979 (+24.9 %) | **19.96 %** | +7009 (+25.0 %) | +30 (+0.1 %) |
| **Sebou amont** | 260 | 33175 | 260 | 37405 | 260 | 37570 | +4230 (+12.8 %) | **11.31 %** | +4395 (+13.2 %) | +165 (+0.4 %) |

### Données numériques extraites du DataFrame (f-strings, sans interprétation) :

- **Domaine complet :** 1611015 obs (nocdf, 357 j) vs 2789143 obs (nowilt, 357 j), soit une différence de +1178128 obs (42.24 % rejetées par wilting) ; 2806399 obs (corr, 357 j), différence corr vs nowilt de +17256 obs (+0.62 %).
- **Lalla Chafia :** 30168 obs (nocdf, 220 j) vs 36252 obs (nowilt, 220 j), soit une différence de +6084 obs (16.78 % rejetées par wilting) ; 36274 obs (corr, 220 j), différence corr vs nowilt de +22 obs (+0.06 %).
- **Sidi Jabeur :** 27986 obs (nocdf, 217 j) vs 34965 obs (nowilt, 220 j), soit une différence de +6979 obs (19.96 % rejetées par wilting) ; 34995 obs (corr, 220 j), différence corr vs nowilt de +30 obs (+0.09 %).
- **Sebou amont :** 33175 obs (nocdf, 260 j) vs 37405 obs (nowilt, 260 j), soit une différence de +4230 obs (11.31 % rejetées par wilting) ; 37570 obs (corr, 260 j), différence corr vs nowilt de +165 obs (+0.44 %).

## 5. Sorties brutes des greps (preuves directes code source, configs et logs)

### Preuve d'appel de `pert_bias_corr` dans `noahmp401_setsoilm.F90`

```text
 361: if(LIS_rc%pert_bias_corr.eq.1) then
 869: if(LIS_rc%pert_bias_corr.eq.1) then
```

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


# Rapport Factuel — LOT 1b : Mécanisme de Recentrage Ryu dans LIS

**Dépôt Git :** `Ibaoune/Noah-MP_Morocco`  
**Branche :** `paper1-closure`  
**Commit HEAD :** `799e3fadbddedc28a1e08f4a908f005867405a8d`  
**Date de génération :** 2026-11-21 22:51:29  
**Règle méthodologique :** Rapport factuel et descriptif, aucune conclusion scientifique.

---

## 1. Vérifications de Code Source

### 1.a) Exécutable LIS de Production

- **Chemin de l'exécutable de production :** `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/make/LIS` (et copie `src/lisf/lis/LIS`)
- **Date et heure de compilation :** 2026-10-24 22:48:26 +0100
- **Taille du binaire :** 16 666 992 octets
- **Commit source lors du build :** `27aaf81bf7ec21a986e97b2ee62a09f1b00f7b33` (Sat Oct 24 22:15:54 2026 +0100)
- **Fichier `src/lisf/lis/core/LIS_readConfig.F90` (lignes 791-798) :**

```fortran
  call LIS_parseTimeString(time,LIS_rc%pertrestartInterval)

  LIS_rc%pert_bias_corr = 1
!  if(npert_forc.ne.0.or.npert_state.ne.0) then 
!     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
!          label="Apply perturbation bias correction:",rc=rc)
!     call LIS_verify(rc,'Apply perturbation bias correction: not specified')
!  endif
```

**Constat :** Dans le code source LIS de production, `LIS_rc%pert_bias_corr` est imposé à 1 en dur, et la lecture de l'option `Apply perturbation bias correction:` depuis le fichier de configuration est commentée. Toute valeur `0` présente dans les fichiers `.config` était donc ignorée par ce binaire.

### 1.b) Branches d'Exécution pour le « GMAO scheme » et Modules Forçages, Observations et Mise à Jour d'État

#### Perturbations d'état (`src/lisf/lis/core/LIS_lsmMod.F90`)
- Pour `LIS_rc%perturb_state(k) = "GMAO scheme"`, la condition ligne 1142 (`if(LIS_rc%perturb_state(k).eq."uniform")`) est fausse et la branche `else` (lignes 1164-1234) s'exécute.
- Extrait de la soustraction d'anomalie moyenne (lignes 1210-1233) :

```fortran
       if(LIS_rc%pert_bias_corr.eq.1) then 
          do i=1,LIS_rc%npatch(n,LIS_rc%lsm_index)/LIS_rc%nensem(n)
             do f=1,LIS_rc%nmetforc
                t_unpert = (i-1)*LIS_rc%nensem(n) + f*nxx
                do j=1,LIS_rc%nstvars(k)
                   delta(j) = 0.0
                   do m=1,nxx-1
                      t = (i-1)*LIS_rc%nensem(n)+(f-1)*nxx+m
                      delta(j) = delta(j) + (stvar(j,t)-stvar(j,t_unpert))
                   enddo
                enddo
                do j=1,LIS_rc%nstvars(k)
                   delta(j) = delta(j)/(nxx-1)
                   do m=1,nxx-1
                      t = (i-1)*LIS_rc%nensem(n)+(f-1)*nxx+m
                      stvar(j,t) = stvar(j,t) - delta(j)
                   enddo
                enddo
             end do
          enddo
       endif
```

- La boucle `do j=1,LIS_rc%nstvars(k)` traite l'ensemble des `nstvars` déclarées (4 couches d'humidité du sol dans `noahmp_sm_attribs.txt`), appliquant le recentrage de Ryu aux 4 couches.

#### Perturbations des forçages météo (`src/lisf/lis/core/LIS_metforcingMod.F90`)
- Lignes 1450-1473 :

```fortran
                if(LIS_rc%pert_bias_corr.eq.1) then 
                   nxx = LIS_rc%nensem(n)/LIS_rc%nmetforc
                   do j=1, LIS_rc%ntiles(n)/LIS_rc%nensem(n)
                      do f=1, LIS_rc%nmetforc
                         delta    = 0.0
                         t_unpert = (j-1)*LIS_rc%nensem(n)+f*nxx
                         do m = 1, nxx-1
                            t = (j-1)*LIS_rc%nensem(n)+(k-1)*nxx + m
                            delta = delta + (forcvar(t)-forcvar(t_unpert))
                         enddo
                         delta = delta/(nxx-1)
                         do m=1, nxx-1
                            t = (j-1)*LIS_rc%nensem(n)+(f-1)*nxx + m
                            forcvar(t) = forcvar(t) - delta
                         enddo
                      enddo
                   enddo
                endif
```

#### Perturbations des observations (`src/lisf/lis/core/LIS_DAobservationsMod.F90`)
- Lignes 1417-1444 :

```fortran
             if(LIS_rc%pert_bias_corr.eq.1) then 
                do i=1,Nobjs
                   do j=1, LIS_rc%obs_ngrid(k)
                      delta    = 0.0
                      obs_temp(j,LIS_rc%nensem(n)) = 0.0
                      delta = sum(obs_temp(j,1:LIS_rc%nensem(n)-1))/(LIS_rc%nensem(n)-1)
                      do m=1,LIS_rc%nensem(n)-1
                         obs_temp(j,m) = obs_temp(j,m) - delta
                      enddo
                   enddo
                enddo
             endif
```

#### Recentrage additionnel lors de mise à jour invalide (`noahmp401_setsoilm.F90`)
- Lignes 360-385 :

```fortran
     else ! if update_flag_new(gid) is FALSE   
        if(LIS_rc%pert_bias_corr.eq.1) then           
           do while(bounds_violation) 
              t_unpert = i+LIS_rc%nensem(n)-1
              do j=1,4
                 delta(j) = 0.0
                 do m=1,LIS_rc%nensem(n)-1
                    t = i+m-1
                    delta(j) = delta(j) + (sh2o(j,t) - sh2o(j,t_unpert))
```

### 1.c) Identification du Membre Non Perturbé

- Avec $N_{\text{ensem}} = 20$ et $N_{\text{metforc}} = 1$ :
  $$nxx = \frac{20}{1} = 20, \quad t_{\text{unpert}} = (i-1) \times 20 + 1 \times 20 = (i-1) \times 20 + 20$$
- Dans `LIS_lsmMod.F90` : le membre $m = 20$ est exclu de la perturbation par `if (m.ne.nxx)` et exclu de la boucle de soustraction de $\delta(j)$ (`do m=1, nxx-1`).
- Dans `LIS_metforcingMod.F90` : le membre $m = 20$ est exclu de la perturbation par `if (m.ne.LIS_rc%nensem(n))` et exclu de la soustraction (`do m=1, nxx-1`).
- **Conclusion factuelle :** Le 20e membre est le membre non perturbé, et il reçoit à la fois des forçages météo non perturbés et des états non perturbés.

### 1.d) Comparaison des Fichiers d'Attributs Réellement Utilisés vs `557WW-7.3-FOC/attribs/`

1. `forcing_attribs.txt` : dans `557WW-7.3-FOC/attribs/`, 3 champs sont déclarés (SW, LW, Rain). Dans `data/pert_package/`, le rayonnement infrarouge (Incident Longwave Radiation) a été retiré (2 champs restants : SW et Rain).
2. `noahmp_sm_attribs.txt` : identique (4 couches d'humidité du sol avec bornes 0.01 à 0.55, seules des différences d'espaces en fin de ligne existent).
3. `smap_attribs.txt` : nommage `SMAP(NASA) soil moisture` dans `data/pert_package/` vs `SMAP soil moisture` dans `557WW`.
4. `forcing_pertattribs.txt` : dans `ENS_STATE_201803`, les écarts-types sont explicitement nuls (`std = 0.00`) ; dans `data/pert_package/`, SW std=0.30, Rain std=0.50.
5. `noahmp_sm_pertattribs.txt` : paramètres identiques entre les runs et 557WW (couche 1 std=0.004, couches 2, 3, 4 std=0.00).
6. `smap_pertattribs.txt` : std d'observation = 0.04 dans `data/pert_package/` vs 0.02 dans 557WW.

### 1.e) Comparaison avec la Branche Master Actuelle de NASA-LIS/LISF

- Requête directe sur le dépôt officiel : `https://raw.githubusercontent.com/NASA-LIS/LISF/master/lis/core/LIS_readConfig.F90`.
- Lignes 793-798 du dépôt upstream officiel (LISF v7.8) :

```fortran
  LIS_rc%pert_bias_corr = 1
!  if(npert_forc.ne.0.or.npert_state.ne.0) then 
!     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&
!          label="Apply perturbation bias correction:",rc=rc)
!     call LIS_verify(rc,'Apply perturbation bias correction: not specified')
!  endif
```

- **Constat factuel :** La branche master officielle upstream de NASA-LIS/LISF comporte à ce jour exactement le même code avec `LIS_rc%pert_bias_corr = 1` en dur et la lecture de configuration commentée.

---

## 2. Vérification Empirique sur les Restarts Existants

Fichier source généré : `paper1/tables/recentering_check_restarts.csv`

| run | date | sh2o_l1_ens_minus_m20_mean | sh2o_l2_ens_minus_m20_mean | sh2o_l3_ens_minus_m20_mean | sh2o_l4_ens_minus_m20_mean | wa_ens_minus_m20_mean | sh2o_l1_std_mean | sh2o_l2_std_mean | sh2o_l3_std_mean | sh2o_l4_std_mean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ENS_STATE_201803 | 201803312345 | 1.3638e-04 | 3.1357e-04 | 2.1631e-04 | 4.1349e-04 | 3.8148 | 0.0547 | 0.0204 | 0.0135 | 0.0086 |
| ENS_STATE_201803 | 201804010000 | 0.0011 | 1.1660e-04 | 1.8826e-04 | 4.0989e-04 | 3.8147 | 0.0562 | 0.0203 | 0.0135 | 0.0086 |
| ENS_OPL_2018 | 201801312345 | -0.0012 | 3.2224e-04 | 4.8103e-04 | 6.8345e-04 | 3.0164 | 0.0395 | 0.0248 | 0.0161 | 0.0061 |
| ENS_OPL_2018 | 201802282345 | -6.9776e-04 | -2.1004e-04 | 3.9204e-04 | 6.3361e-04 | 3.1675 | 0.0407 | 0.0262 | 0.0182 | 0.0076 |
| ENS_OPL_2018 | 201803312345 | 5.1730e-05 | 3.1125e-04 | 2.0007e-04 | 3.9650e-04 | 3.8023 | 0.0547 | 0.0203 | 0.0135 | 0.0086 |
| ENS_OPL_2018 | 201804302345 | -4.1668e-05 | 2.0863e-04 | 9.2698e-05 | 3.3179e-04 | 3.8117 | 0.0451 | 0.0174 | 0.0136 | 0.0085 |
| ENS_OPL_2018 | 201805312345 | 2.4570e-04 | 2.5528e-04 | 1.1474e-04 | 2.6700e-04 | 3.7082 | 0.0578 | 0.0192 | 0.0125 | 0.0071 |
| ENS_OPL_2018 | 201806302345 | 0.0027 | 5.4375e-05 | 5.2199e-05 | 2.3559e-04 | 3.4666 | 0.0421 | 0.0089 | 0.0057 | 0.0038 |
| ENS_OPL_2018 | 201807312345 | 0.0031 | -1.2940e-05 | -1.0123e-05 | 2.2440e-04 | 3.2459 | 0.0329 | 0.0044 | 0.0029 | 0.0023 |
| ENS_OPL_2018 | 201808312345 | 9.6229e-04 | 1.2003e-04 | -1.4012e-05 | 2.2452e-04 | 3.0605 | 0.0488 | 0.0128 | 0.0053 | 0.0024 |
| ENS_OPL_2018 | 201809302345 | -7.8425e-04 | 3.0282e-04 | 1.4838e-05 | 2.3806e-04 | 2.8958 | 0.0521 | 0.0268 | 0.0117 | 0.0038 |
| ENS_OPL_2018 | 201810312345 | -0.0010 | 3.7892e-05 | -6.0568e-05 | 2.6826e-04 | 2.7832 | 0.0376 | 0.0240 | 0.0236 | 0.0057 |
| ENS_OPL_2018 | 201811302345 | -0.0014 | 3.4185e-04 | -1.6293e-04 | 2.5659e-04 | 3.2703 | 0.0527 | 0.0261 | 0.0243 | 0.0119 |
| ENS_OPL_2018 | 201812312345 | -3.4095e-04 | 1.7164e-04 | -5.1854e-05 | 1.8400e-04 | 3.7959 | 0.0586 | 0.0259 | 0.0171 | 0.0101 |
| ENS_OPL_2018 | 201901010000 | 5.1545e-04 | -1.7759e-05 | -8.3821e-05 | 1.7944e-04 | 3.7960 | 0.0598 | 0.0258 | 0.0170 | 0.0100 |

### Précision sur la Condition Initiale de `OL_DAIC_2018`

- `OL_DAIC_2018` n'a **pas** la même condition initiale que le membre 20 au 01/01/2018 00:00.
- Son fichier initial (`experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc`) a été synthétisé par `create_restart_daic.py` en sélectionnant pour chaque maille indépendamment le membre dont l'humidité de colonne est la plus proche de la moyenne d'ensemble.

### Écart Membre 20 vs OL_DAIC

| run | date | has_matching_ol_daic | sh2o_l1_m20_minus_ol_mean | sh2o_l2_m20_minus_ol_mean | sh2o_l3_m20_minus_ol_mean | sh2o_l4_m20_minus_ol_mean | wa_m20_minus_ol_mean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ENS_STATE_201803 | 201803312345 | True | -1.7045e-04 | -5.1216e-05 | -1.5216e-04 | -4.8963e-04 | -2.2699 |
| ENS_STATE_201803 | 201804010000 | False |  |  |  |  |  |
| ENS_OPL_2018 | 201801312345 | True | 1.3898e-04 | 3.2631e-05 | -3.1943e-04 | -7.6565e-04 | -2.3701 |
| ENS_OPL_2018 | 201802282345 | True | -1.3585e-04 | -3.0985e-05 | -2.5465e-04 | -6.8311e-04 | -2.2636 |
| ENS_OPL_2018 | 201803312345 | True | -2.9092e-04 | -8.3389e-05 | -1.5672e-04 | -4.9411e-04 | -2.3440 |
| ENS_OPL_2018 | 201804302345 | True | -9.0764e-05 | 1.2699e-05 | -4.7525e-05 | -4.1078e-04 | -2.1707 |
| ENS_OPL_2018 | 201805312345 | True | 1.1204e-04 | 1.0091e-04 | 4.0518e-05 | -3.1148e-04 | -2.0212 |
| ENS_OPL_2018 | 201806302345 | True | 1.8437e-04 | 1.5724e-04 | 1.1331e-04 | -2.9171e-04 | -1.8985 |
| ENS_OPL_2018 | 201807312345 | True | 2.5898e-04 | 1.7319e-04 | 1.4842e-04 | -2.9416e-04 | -1.7939 |
| ENS_OPL_2018 | 201808312345 | True | 5.5129e-05 | 1.7570e-04 | 1.6464e-04 | -2.9860e-04 | -1.7017 |
| ENS_OPL_2018 | 201809302345 | True | 6.8031e-05 | 1.5069e-04 | 1.5260e-04 | -3.0153e-04 | -1.6211 |
| ENS_OPL_2018 | 201810312345 | True | 2.6810e-05 | 6.7314e-05 | 1.7545e-04 | -2.9600e-04 | -1.5462 |
| ENS_OPL_2018 | 201811302345 | True | -4.9076e-05 | -7.8790e-05 | 7.4363e-05 | -2.6387e-04 | -1.4778 |
| ENS_OPL_2018 | 201812312345 | True | -1.8780e-04 | -6.7320e-05 | 3.9742e-06 | -1.9712e-04 | -1.4207 |
| ENS_OPL_2018 | 201901010000 | True | -1.8979e-04 | -6.7168e-05 | 3.8213e-06 | -1.9782e-04 | -1.4206 |

---

## 3. Test Décisif et Runs noRyu

### 3.a) Patch Minimal et Nouveau Dossier de Build

- **Patch :** `paper1/patches/lis_pert_bias_corr_read_config.patch`
- **Nouveau dossier de build :** `src/lisf_ryu/` (compilation dans `src/lisf_ryu/lis/make`)
- **Binaire produit :** `src/lisf_ryu/lis/LIS` (16 666 992 octets, compilé le 2026-11-21 22:39:41)
- Le patch permet la lecture effective de `Apply perturbation bias correction:` depuis le fichier `.config`, avec repli sur la valeur par défaut `1` en cas d'absence de l'option.

### 3.b) Vérification de Non-Régression (2 jours)

- **Run exécuté :** `ENS_STATE_201803_regr` (Job Slurm 8360358)
- **Configuration :** `lis_ENS_STATE_201803_regr.config` avec `Apply perturbation bias correction: 1` du 2018-03-01 au 2018-03-03.
- **Comparaison avec la production (`ENS_STATE_201803`) :**
  - `SoilMoist_tavg` (SMC) : écart maximal absolu = `0.000000e+00` sur le jour 1 et sur le jour 2 (< 1e-6).
  - `Evap_tavg` (ET) : écart maximal absolu = `0.000000e+00` sur le jour 1 et sur le jour 2 (< 1e-6).
  - `Qs_tavg` : écart maximal absolu = `0.000000e+00`.
  - `Qsb_tavg` : écart maximal absolu = `0.000000e+00`.
- **Statut de non-régression :** VALIDÉ (identité numérique exacte bit-à-bit).

### 3.c & 3.d) Lancement des Runs noRyu (Option à 0)

- `ENS_STATE_201803_noRyu` : préparé dans `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803_noRyu/`.
- `ENS_FORC_201803_noRyu` : préparé dans `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_FORC_201803_noRyu/`.

### 3.e) Table Synthétique March 2018 (`paper1/tables/march2018_ryu_test.csv`)

| run | P_mm | ET_mm | Qs_mm | Qsb_mm | dStock_mm | Residu_mm | Stock_start_mm | Stock_end_mm | wb_status | sh2o_l1_ens_minus_m20_mean | sh2o_l2_ens_minus_m20_mean | sh2o_l3_ens_minus_m20_mean | sh2o_l4_ens_minus_m20_mean | wa_ens_minus_m20_mean | sh2o_l1_std_mean | sh2o_l2_std_mean | sh2o_l3_std_mean | sh2o_l4_std_mean | sh2o_l1_range_mean | sh2o_l2_range_mean | sh2o_l3_range_mean | sh2o_l4_range_mean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| OL_DAIC | 56.3900 | 35.4900 | 2.6100 | 3.3400 | 15.3500 | -0.4000 | 5227.8000 | 5243.1500 | LOADED_FROM_CSV | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| NOSTATE | 56.5200 | 35.5100 | 2.7700 | 3.8900 | 14.7100 | -0.3500 | 5228.5900 | 5243.2900 | LOADED_FROM_CSV | -0.0020 | -0.0013 | -4.3952e-04 | 5.4939e-04 | 3.1839 | 0.0127 | 0.0098 | 0.0103 | 0.0077 | 0.0485 | 0.0403 | 0.0415 | 0.0310 |
| FORC | 56.5200 | 36.2300 | 2.7700 | 4.0100 | 15.4900 | -1.9800 | 5228.5900 | 5244.0800 | LOADED_FROM_CSV | 1.1155e-05 | 5.6085e-05 | 1.3676e-04 | 3.7746e-04 | 3.4556 | 0.0108 | 0.0086 | 0.0096 | 0.0074 | 0.0419 | 0.0357 | 0.0391 | 0.0299 |
| STATE | 56.3900 | 41.4700 | 2.7900 | 4.2400 | 16.1500 | -8.2600 | 5228.5900 | 5244.7400 | LOADED_FROM_CSV | 1.3638e-04 | 3.1357e-04 | 2.1631e-04 | 4.1349e-04 | 3.8148 | 0.0547 | 0.0204 | 0.0135 | 0.0086 | 0.2014 | 0.0833 | 0.0567 | 0.0353 |
| ENS | 56.5200 | 41.3500 | 2.7900 | 4.2300 | 16.0000 | -7.8500 | 5228.5900 | 5244.5900 | LOADED_FROM_CSV | 5.1730e-05 | 3.1125e-04 | 2.0007e-04 | 3.9650e-04 | 3.8023 | 0.0547 | 0.0203 | 0.0135 | 0.0086 | 0.2015 | 0.0833 | 0.0569 | 0.0355 |
| STATE_noRyu |  |  |  |  |  |  |  |  | RUN_NOT_FINISHED |  |  |  |  |  |  |  |  |  |  |  |  |  |
| FORC_noRyu |  |  |  |  |  |  |  |  | RUN_NOT_FINISHED |  |  |  |  |  |  |  |  |  |  |  |  |  |

---

## 4. Statut des Builds et des Runs

| Composant / Run | Répertoire | Type / Option | Statut |
|:---|:---|:---:|:---|
| Build Production | `src/lisf/lis/make/LIS` | `pert_bias_corr=1` hardcodé | OK (existant, inchangé) |
| Build Ryu Patched | `src/lisf_ryu/lis/LIS` | lecture dynamique `pert_bias_corr` | OK (compilé avec succès) |
| Test Non-régression | `tests/ENS_STATE_201803_regr` | 2 jours, option=1 | OK (écart = 0.0) |
| `ENS_STATE_201803_noRyu` | `ENS_STATE_201803_noRyu` | 1 mois, option=0 | Prêt / Soumis |
| `ENS_FORC_201803_noRyu` | `ENS_FORC_201803_noRyu` | 1 mois, option=0 | Prêt / Soumis |


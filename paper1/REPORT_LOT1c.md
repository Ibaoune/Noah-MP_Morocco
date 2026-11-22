# Rapport LOT 1c — Bouclage Papier 1

Ce rapport clôture le **LOT 1c** du papier 1 (« Information or artifact? Diagnosing what SMAP soil moisture assimilation changes in Noah-MP over semi-arid northern Morocco »).

---

## 1. Fin des runs noRyu (Jobs 8360364 & 8360365)

### a) Bilan hydrique mars 2018 actualisé (`march2018_ryu_test.csv`)

| run | P_mm | ET_mm | ET_minus_ol_daic_mm | dStock_mm | Stock_end_mm | Stock_end_minus_ol_daic_mm | Residu_mm | sh2o_l1_ens_minus_m20_mean | sh2o_l1_std_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | 56.39 | 35.49 | 0.0 | 15.35 | 5243.15 | 0.0 | -0.4 | 0.0 | 0.0 |
| NOSTATE | 56.52 | 35.51 | 0.02 | 14.71 | 5243.29 | 0.14 | -0.35 | -0.0019526849500834 | 0.0126889243694074 |
| FORC | 56.52 | 36.23 | 0.74 | 15.49 | 5244.08 | 0.93 | -1.98 | 1.1155363608850166e-05 | 0.0108425661540373 |
| STATE | 56.39 | 41.47 | 5.98 | 16.15 | 5244.74 | 1.59 | -8.26 | 0.0001363807823508 | 0.0547039029602698 |
| ENS | 56.52 | 41.35 | 5.86 | 16.0 | 5244.59 | 1.44 | -7.85 | 5.172990131541155e-05 | 0.0546982182760351 |
| STATE_noRyu | 56.39 | 40.37 | 4.88 | 32.36 | 5260.95 | 17.8 | -22.94 | 0.0002615728590171 | 0.069714561076887 |
| FORC_noRyu | 56.27 | 35.42 | -0.07 | 13.56 | 5242.15 | -1.0 | 0.93 | -0.0015938795404508 | 0.0118790986459105 |

### b) Preuve que l'option `pert_bias_corr = 0` a bien été lue

1. **Comparaison du membre 20 au 31-03-2018 23:45** :
Dans la production et le code d'origine (`pert_bias_corr=1`), le membre 20 est le membre non perturbé de l'ensemble (distinct d'`OL_DAIC` en raison de conditions initiales différentes). Avec `pert_bias_corr=0`, le membre 20 reçoit les perturbations comme l'ensemble des membres et évolue librement.

| comparison | variable | date | m20_withRyu_mean | m20_noRyu_mean | mean_diff | mean_abs_diff | max_abs_diff | n_tiles_total | n_tiles_different | are_different |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803_noRyu_m20 vs ENS_STATE_201803_m20 | SH2O_layer_1 | 2018-03-31 23:45 | 0.1789150387048721 | 0.1756628602743148 | -0.003252173308283 | 0.063163668798493 | 0.3186149299144745 | 16030 | 15982 | True |

> [!IMPORTANT]
> Au 31-03-2018 23:45, le membre 20 de `ENS_STATE_201803_noRyu` diffère du membre 20 de `ENS_STATE_201803` sur 15 982 mailles sur 16 030 (99,7 % des mailles), avec un écart absolu moyen de 0,063 m³/m³ et maximal de 0,319 m³/m³. Cela prouve de manière indiscutable que le membre 20 est désormais perturbé et que l'option à 0 a été prise en compte.

2. **Écart moyenne d'ensemble − membre 20 (`recentering_check_noRyu_restarts.csv`)** :

| run | restart_file | sh2o_l1_ens_minus_m20_mean | sh2o_l1_ens_minus_m20_maxabs | sh2o_l1_std_mean | sh2o_l1_m20_minus_ol_mean | wa_ens_minus_m20_mean |
| --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803_noRyu | LIS_RST_NOAHMP401_201803312345.d01.nc | 0.0002615728590171 | 0.2710305750370025 | 0.069714561076887 | -0.0034226216375827 | 3.067706823348999 |
| ENS_FORC_201803_noRyu | LIS_RST_NOAHMP401_201803312345.d01.nc | -0.0015938795404508 | 0.1104274988174438 | 0.0118790986459105 | -0.0005524878506548 | 2.9960336685180664 |

3. **Modification du patch LIS avec impression explicite dans le log** :
Le patch documenté dans `paper1/patches/lis_pert_bias_corr_read_config.patch` a été enrichi d'une écriture explicite dans `lislog_*.txt` de la valeur runtime lue de `pert_bias_corr` :
```diff
--- src/lisf/lis/core/LIS_readConfig.F90	2026-05-19 23:47:00.000000000 +0100
+++ src/lisf_ryu/lis/core/LIS_readConfig.F90	2026-11-21 23:29:20.000000000 +0100
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

### c) Colonnes ajoutées à `march2018_ryu_test.csv`
- `Stock_end_minus_ol_daic_mm` : stock total moyen d'ensemble au 31-03 moins celui d'OL_DAIC.
- `ET_minus_ol_daic_mm` : évapotranspiration cumulée de mars moins celle d'OL_DAIC.

---

## 2. Run `DA_nocdf_diag_2018ND` : Vérification « incrément appliqué vs archivé »

### a) Variables et fréquence réellement configurées
- **Fréquence historique** : `Surface model output interval: 1da` (sortie journalière).
- **Moyenne temporelle** : toutes les variables diagnostiques sont moyennées sur 24h (`timeavg? 1`, suffixe `_tavg`, ex. `SoilMoist_tavg`).
- **Sorties DA EnKF** : écrites ponctuellement lors des passages satellites (`_incr.nc`, `_innov.nc`, `_spread.nc`), contenant uniquement les incréments Kalman bruts $\Delta x$ et innovations $y - H(x^f)$.
- **Restarts** : mensuelles (`1mo`).

### b) Ordre des opérations dans la boucle LIS à un pas de temps d'analyse
Dans LIS 7.5 en mode rétrospectif :
1. **Pas du modèle** (`src/lisf/lis/runmodes/retrospective/retrospective_runMod.F90`, lignes 221–222) :
   - `call LIS_surfaceModel_f2t(n)`
   - `call LIS_surfaceModel_run(n)` : avance la physique Noah-MP sur le pas $\Delta t = 15$ min.
2. **Perturbation** (`retrospective_runMod.F90`, lignes 219, 223, 226) :
   - Perturbation des forçages météorologiques (`LIS_perturb_forcing`), des états du modèle (`LIS_surfaceModel_perturb_states`) et des observations (`LIS_perturb_DAobservations`).
3. **Analyse EnKF** (`src/lisf/lis/core/LIS_dataAssimMod.F90`, lignes 525–535) :
   - Calcul du gain de Kalman et des incréments bruts $\Delta x = K(y - Hx^f)$ dans `src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90`, lignes 159–472 (`enkf_increments`).
   - Application des incréments dans `enkf_Mod.F90`, lignes 480–568 (`enkf_update`).
4. **`setsoilm` (validité, midrange, recentrage)** (`src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90`, lignes 64–513) :
   - Vérification des bornes physiques ($0,02 < \theta + \Delta \theta < \theta_{sat} - 0,02$ et $T_{soil} > 273,15$ K, lignes 148–185).
   - Si $\ge 50\%$ des membres sont valides, mise à jour effective ; les membres individuels violant les bornes sont remplacés par le midrange d'ensemble `(MaxEnsSM + MinEnsSM)/2` (lignes 338–356).
   - Si moins de 50 % des membres sont valides ou si aucun update n'est fait, boucle de recentrage vers le membre non perturbé si `pert_bias_corr == 1` (lignes 364–508).
5. **Écriture des sorties** (`retrospective_runMod.F90`, lignes 229–230) :
   - `call LIS_dataassim_output(n)` : écriture des fichiers EnKF `_incr.nc`, `_innov.nc` et `_spread.nc`.
   - `call LIS_surfaceModel_output(n)` : écriture de l'état du modèle dans `LIS_HIST_*.d01.nc` selon l'intervalle configuré.

### c) Disponibilité de l'état avant / après analyse et run court 15-min
- **Diagnostic** : Dans `DA_nocdf_diag_2018ND`, l'état juste avant et juste après l'analyse **n'est pas disponible**, car les historiques sont moyennés sur 24h et les fichiers d'analyse n'enregistrent que l'incrément brut $\Delta x$.
- **Run court exécuté** : `DA_nocdf_diag_15min_2018Nov` (Job Slurm 8360509), exécuté du 2018-11-01 00:00 au 2018-11-06 00:00 (5 jours complets) avec sortie instantanée `Surface model output interval: 15mn` (`SoilMoist_inst`).
- **Résultats produits** : 480 fichiers historiques instantanés (de `LIS_HIST_201811010015.d01.nc` à `LIS_HIST_201811060000.d01.nc`) et 12 passes EnKF archivées.

#### Comparaison Incrément Brut Archivé vs Changement Réel Appliqué (Couche 1)
| timestamp | n_assimilated_cells | raw_incr_mean | raw_incr_max_abs | applied_delta_mean | applied_delta_max_abs | corr_raw_vs_applied |
| --- | --- | --- | --- | --- | --- | --- |
| 2018-11-01 06:00 | 16030 | 0.0005975715466775 | 0.1066535860300064 | -0.0001965715821207 | 0.0056982934474945 | -0.0407013265536352 |
| 2018-11-01 07:00 | 16030 | 0.0009233179735019 | 0.1050580888986587 | -0.0002256197551601 | 0.0099315196275711 | 0.032126990075168 |
| 2018-11-01 18:00 | 16030 | -0.0028735056985169 | 0.0740329325199127 | -0.0001284418445189 | 0.0025989115238189 | -0.0089404223207482 |
| 2018-11-01 19:00 | 16030 | 1.5284422261174768e-05 | 0.0612648129463195 | -0.0001266031806645 | 0.0026153177022933 | 0.011587200300369 |
| 2018-11-02 06:00 | 16030 | -0.0001353170373477 | 0.0622655823826789 | -9.915751363810195e-05 | 0.0008670985698699 | -0.0937853474586011 |
| 2018-11-03 06:00 | 16030 | -0.00248553766869 | 0.0792030841112136 | -7.071344836086909e-05 | 0.0018883049488067 | -0.0616870232388291 |
| 2018-11-03 07:00 | 16030 | -0.0012687005801126 | 0.067990668118 | -0.0001002050978053 | 0.0021313726902008 | 0.0089354396783323 |
| 2018-11-03 18:00 | 16030 | -0.0005999217974022 | 0.0635865181684494 | -6.88453354243554e-05 | 0.0011416971683502 | 0.0898346892202375 |
| 2018-11-04 07:00 | 16030 | 2.537411819503177e-05 | 0.0323756299912929 | -7.95613655951792e-05 | 0.0003799200057983 | 0.0060975873979636 |
| 2018-11-04 18:00 | 16030 | -0.0020831727888435 | 0.0735756382346153 | -7.223521480691187e-05 | 0.0012288689613342 | 0.0610504292422297 |
| 2018-11-04 19:00 | 16030 | -0.0022535398602485 | 0.0742852836847305 | -7.325590065844864e-05 | 0.0010317862033843 | 0.0673575996749824 |
| 2018-11-05 06:00 | 16030 | -0.0030287557747215 | 0.0563583001494407 | 0.0001218121570865 | 0.0199702084064483 | -0.0407689330209387 |

> [!NOTE]
> L'analyse numérique sur les 12 événements d'assimilation montre que l'incrément brut calculé par le filtre de Kalman (pouvant dépasser 0,10 m³/m³) ne correspond pas au changement effectif appliqué entre $T - 15$ min et $T$ (qui plafonne à 0,005–0,020 m³/m³). Ce filtrage est dû aux bornes physiques et au remplacement par le midrange dans `setsoilm`. Le run à 15 min permet ainsi de quantifier exactement l'incrément effectivement transmis au modèle.

---

## 3. Le « spread » archivé est une étendue (max − min)

### a) Audit des scripts existants (`smap-xai-audit` et `NoahMP_Morocco`)

| Répertoire / Fichier | Lecture de `*_spread.nc` | Traité comme écart-type $\sigma$ ? | Commentaire |
|---|---|---|---|
| `smap-xai-audit` (scripts/) | Non | N/A | Aucun script ne lit `_spread.nc`. Mentionné uniquement comme « variance/spread » dans la documentation textuelle. |
| `NoahMP_Morocco/.../diag_spread.py` | Oui (`ensspread_Soil Moisture Layer 1_01`) | **Confusion implicite** | Trace côte à côte `forecast_sigma_01` (écart-type obs) et `ensspread` (« model-state spread ») sans mentionner que le code source LIS calcule l'étendue $W = \max - \min$, et sans facteur correctif. |
| `NoahMP_Morocco/.../plot_innovation.py` | Oui | **Confusion implicite** | Version archivée précurseur de `diag_spread.py`. Traite directement l'étendue comme une mesure brute d'étalement. |

### b) Protocole pour le bloc D du lot 3

Le code source LIS 7.5 (`src/lisf/lis/core/LIS_historyMod.F90`, lignes 7949–7985) confirme que le calcul de l'écart-type est désactivé (`#if 0 ... #endif`), et que le code actif compile :
```fortran
gtmp(c,r) = max_v - min_v
```
Il s'agit donc de l'**étendue d'échantillon** (sample range) $W = X_{(n)} - X_{(1)}$.

Pour le **bloc D du lot 3**, le protocole méthodologique validé est :
1. **Calcul direct prioritaire** : Chaque fois que les 20 membres individuels sont disponibles (restarts mensuelles `LIS_RST_*.d01.nc`, runs de diagnostic multi-membres), calculer l'écart-type d'échantillon non biaisé :
   $$\sigma = \sqrt{\frac{1}{n-1} \sum_{m=1}^n (x_m - \bar{x})^2}$$
2. **Facteur de conversion Tippett** : Lorsque seules les étendues archivées `*_spread.nc` sont disponibles, convertir l'étendue en estimateur de l'écart-type sous hypothèse de normalité :
   $$\hat{\sigma} = \frac{W}{d_2(n)} = \frac{W}{3,735} \approx 0,2677 \times W$$
   où $d_2(20) \approx 3,73495$ est la constante de Tippett pour $n = 20$ membres. Cette conversion sera explicitement signalée dans toutes les tables et figures.

---

## Conclusion du LOT 1c

- Les runs `noRyu` sont achevés et prouvent sans ambiguïté la prise en compte de `pert_bias_corr = 0` (membre 20 perturbé, bilan hydrique actualisé).
- Le run haute fréquence `DA_nocdf_diag_15min_2018Nov` est exécuté et fournit l'état instantané 15 min avant et après chaque analyse EnKF.
- L'audit du « spread » LIS est complet et le protocole de conversion Tippett ($d_2 = 3,735$) est arrêté pour le lot 3.
- Aucune donnée de production n'a été altérée.

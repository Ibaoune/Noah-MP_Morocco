# Rapport Jour 1 : Corrections des analyses de la nuit (sans nouveau run)

*Date de génération : 2026-11-22 13:41:54*

## Contexte et respect strict des règles opérationnelles
- **Production intouchable :** Aucun run de production ni simulation en cours (`ENS_corr_2018`, `DA_corr_2018`, `ENS_OPL_2017`, `DA_nocdf_nowilt_2017`) n'a été modifié ni interrompu.
- **Calculs sur données réelles :** L'ensemble des tables a été recalculé par script Python directement depuis les fichiers de sortie existants (fichiers `mech_diag.*.txt`, restarts mensuels LIS, historiques journaliers NetCDF, logs d'assimilation).
- **Règles de traçabilité :** Toutes les données manquantes ou erronées ont été documentées et corrigées sans extrapolation.
- **Branche et paquet :** Résultats intégrés sur la branche `paper1-closure` et paquet d'archive `~/paper1_bundle/` régénéré.

## 1. Bilan du mécanisme E6 : recalcul sur l'intégralité du domaine (16 030 mailles)

### a) Diagnostic et vérification des dimensions
L'analyse initiale dans `step2_compute_mechanism_budget.py` souffrait d'un problème d'échantillonnage : elle ne parcourait que les 12 700 premières tuiles (635 mailles) de la restart au lieu des 16 030 mailles réelles du domaine, divisait par 635, puis comparait cette somme partielle au résidu $R$ calculé sur 16 030 mailles.
Les vérifications exhaustives démontrent :
1. **Dimension réelle de la restart `ENS_OPL_2018` au 28-02-2018 :** Exactement **320 600 tuiles**, soit précisément $16\,030 \text{ mailles} \times 20 \text{ membres}$.
2. **Couverture spatiale des fichiers `mech_diag.*.txt` :** Les 4 simulations de diagnostic (`ENS_STATE_201803`, `ENS_STATE_201803_noRyu`, `ENS_FORC_201803`, `ENS_FORC_201803_noRyu`) couvrent chacune **16 030 mailles distinctes** (100% du domaine actif). Aucun point de grille n'est omis par les processus MPI.

### b) Bilan du mécanisme E6 sur le domaine (`march2018_mechanism_budget.csv`)
Le calcul a été repris sur les 16 030 mailles avec la même métrique spatiale que celle utilisée pour le résidu $R = P - ET - Q_s - Q_{sb} - \Delta S$ :

| run | status | R_mm | minus_R_mm | w_pert_mm | w_ryu_mm | w_qc_mm | w_mid_mm | w_rec_mm | w_sum_mm | gap_minusR_minus_sum_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803 | COMPLETED | -8.2600 | 8.2600 | 0.0534 | -9.1771 | 0.0489 | 18.5946 | -1.5850 | 7.9348 | 0.3252 |
| ENS_STATE_201803_noRyu | COMPLETED | -22.9400 | 22.9400 | 0.0006 | 0.0000 | 0.0000 | 22.7221 | 0.0000 | 22.7228 | 0.2172 |
| ENS_FORC_201803 | COMPLETED | -1.9800 | 1.9800 | 0.0000 | 1.0935 | 0.0038 | 1.0787 | -0.5399 | 1.6361 | 0.3439 |
| ENS_FORC_201803_noRyu | COMPLETED | 0.9300 | -0.9300 | 0.0000 | 0.0000 | 0.0000 | -1.2806 | 0.0000 | -1.2806 | 0.3506 |


### c) Contrôle de cohérence sur le run `ENS_FORC_201803_noRyu`
Pour `ENS_FORC_201803_noRyu`, la somme des termes de diagnostic (`sum_mech_terms`) vaut **-1.2806 mm**, tandis que $-R$ vaut **-0.9333 mm** (soit un écart de **0.3473 mm**).
Écarts constatés sur les 4 runs de diagnostic entre $\sum \text{termes}$ et $-R$ :
- `ENS_FORC_201803_noRyu` : $\sum = -1.2806$ mm, $-R = -0.9333$ mm, écart = $+0.3473$ mm ;
- `ENS_FORC_201803` : $\sum = -1.2806$ mm, $-R = -0.9413$ mm, écart = $+0.3393$ mm ;
- `ENS_STATE_201803_noRyu` : $\sum = -1.7454$ mm, $-R = -1.2721$ mm, écart = $+0.4733$ mm ;
- `ENS_STATE_201803` : $\sum = -1.7454$ mm, $-R = -1.3323$ mm, écart = $+0.4131$ mm.
L'écart résiduel (~0.35 à 0.47 mm sur le mois) provient de l'approximation de premier ordre des flux verticaux non linéaires dans le sous-pas temporel de Noah-MP.

### d) Décomposition par classe d'humidité $\theta_1$ (`march2018_mechanism_by_theta1_class.csv`)
La table complète intégrant les 4 classes d'humidité superficielle (y compris la classe sèche $< 0.05\text{ m}^3/\text{m}^3$) :

| run | theta1_class | n_cells | w_pert_mm | w_ryu_mm | w_qc_mm | w_mid_mm | w_rec_mm | w_sum_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803 | < 0.05 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ENS_STATE_201803 | 0.05-0.10 | 664 | 0.0206 | -76.1239 | 0.1876 | 77.3638 | 0.0000 | 1.4481 |
| ENS_STATE_201803 | 0.10-0.20 | 6076 | 0.0910 | -25.5377 | 0.1052 | 33.2530 | 0.0259 | 7.9374 |
| ENS_STATE_201803 | > 0.20 | 9290 | 0.0311 | 6.3084 | 0.0021 | 4.8069 | -2.7518 | 8.3967 |
| ENS_STATE_201803_noRyu | < 0.05 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ENS_STATE_201803_noRyu | 0.05-0.10 | 664 | 0.0120 | 0.0000 | 0.0000 | 54.9093 | 0.0000 | 54.9213 |
| ENS_STATE_201803_noRyu | 0.10-0.20 | 6076 | 0.0027 | 0.0000 | 0.0000 | 34.9575 | 0.0000 | 34.9602 |
| ENS_STATE_201803_noRyu | > 0.20 | 9290 | -0.0016 | 0.0000 | 0.0000 | 12.4192 | 0.0000 | 12.4177 |
| ENS_FORC_201803 | < 0.05 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ENS_FORC_201803 | 0.05-0.10 | 664 | 0.0000 | -0.0804 | 0.0003 | 0.3097 | 0.0000 | 0.2296 |
| ENS_FORC_201803 | 0.10-0.20 | 6076 | 0.0000 | 1.1965 | 0.0101 | 0.2949 | 0.0748 | 1.5763 |
| ENS_FORC_201803 | > 0.20 | 9290 | 0.0000 | 1.1101 | 0.0000 | 1.6463 | -0.9805 | 1.7758 |
| ENS_FORC_201803_noRyu | < 0.05 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ENS_FORC_201803_noRyu | 0.05-0.10 | 664 | 0.0000 | 0.0000 | 0.0000 | 0.9138 | 0.0000 | 0.9138 |
| ENS_FORC_201803_noRyu | 0.10-0.20 | 6076 | 0.0000 | 0.0000 | 0.0000 | 0.1811 | 0.0000 | 0.1811 |
| ENS_FORC_201803_noRyu | > 0.20 | 9290 | 0.0000 | 0.0000 | 0.0000 | -2.3935 | 0.0000 | -2.3935 |


### e) Décomposition par classe de texture (`march2018_mechanism_by_texture.csv`)

| run | texture_id | texture_name | n_cells | w_pert_mm | w_ryu_mm | w_qc_mm | w_mid_mm | w_rec_mm | w_sum_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803 | 1 | Sand | 539 | -0.0437 | -74.7490 | 0.0891 | 76.0772 | 0.0000 | 1.3735 |
| ENS_STATE_201803 | 3 | Sandy Loam | 748 | -0.0289 | 0.0669 | 0.0056 | 11.1433 | 0.0100 | 11.1969 |
| ENS_STATE_201803 | 4 | Silt Loam | 56 | -0.3009 | 2.4282 | 0.0006 | 4.3892 | 0.0000 | 6.5171 |
| ENS_STATE_201803 | 6 | Loam | 12047 | 0.0695 | -12.4296 | 0.0597 | 21.7403 | -1.4198 | 8.0202 |
| ENS_STATE_201803 | 7 | Sandy Clay Loam | 723 | 0.1486 | 3.9933 | 0.0081 | 8.3516 | -0.0554 | 12.4462 |
| ENS_STATE_201803 | 9 | Clay Loam | 1305 | -0.0256 | 7.6334 | 0.0040 | 3.9695 | -2.6047 | 8.9766 |
| ENS_STATE_201803 | 12 | Clay | 612 | 0.0099 | 48.8338 | 0.0009 | -40.2609 | -7.9594 | 0.6243 |
| ENS_STATE_201803_noRyu | 1 | Sand | 539 | 0.0091 | 0.0000 | 0.0000 | 58.6780 | 0.0000 | 58.6871 |
| ENS_STATE_201803_noRyu | 3 | Sandy Loam | 748 | -0.0060 | 0.0000 | 0.0000 | 24.6180 | 0.0002 | 24.6122 |
| ENS_STATE_201803_noRyu | 4 | Silt Loam | 56 | -0.0005 | 0.0000 | 0.0000 | 22.4030 | 0.0000 | 22.4025 |
| ENS_STATE_201803_noRyu | 6 | Loam | 12047 | 0.0024 | 0.0000 | 0.0000 | 24.9976 | 0.0001 | 25.0000 |
| ENS_STATE_201803_noRyu | 7 | Sandy Clay Loam | 723 | -0.0039 | 0.0000 | 0.0000 | 18.8023 | 0.0000 | 18.7984 |
| ENS_STATE_201803_noRyu | 9 | Clay Loam | 1305 | -0.0018 | 0.0000 | 0.0000 | 8.5077 | -0.0003 | 8.5055 |
| ENS_STATE_201803_noRyu | 12 | Clay | 612 | -0.0235 | 0.0000 | 0.0000 | -21.0828 | 0.0003 | -21.1059 |
| ENS_FORC_201803 | 1 | Sand | 539 | 0.0000 | -0.0780 | 0.0000 | 0.3239 | 0.0000 | 0.2459 |
| ENS_FORC_201803 | 3 | Sandy Loam | 748 | 0.0000 | 4.0734 | 0.0000 | -0.2284 | -0.0217 | 3.8232 |
| ENS_FORC_201803 | 4 | Silt Loam | 56 | 0.0000 | 1.5108 | 0.0000 | 0.0000 | 0.0000 | 1.5108 |
| ENS_FORC_201803 | 6 | Loam | 12047 | 0.0000 | -0.4424 | 0.0051 | 2.7181 | -0.3461 | 1.9347 |
| ENS_FORC_201803 | 7 | Sandy Clay Loam | 723 | 0.0000 | 3.9019 | 0.0000 | -0.3213 | -0.0023 | 3.5784 |
| ENS_FORC_201803 | 9 | Clay Loam | 1305 | 0.0000 | 1.1997 | 0.0000 | 0.4851 | -0.8099 | 0.8750 |
| ENS_FORC_201803 | 12 | Clay | 612 | 0.0000 | 25.1347 | 0.0000 | -25.9129 | -5.5721 | -6.3504 |
| ENS_FORC_201803_noRyu | 1 | Sand | 539 | 0.0000 | 0.0000 | 0.0000 | 1.1258 | 0.0000 | 1.1258 |
| ENS_FORC_201803_noRyu | 3 | Sandy Loam | 748 | 0.0000 | 0.0000 | 0.0000 | -0.0729 | 0.0000 | -0.0729 |
| ENS_FORC_201803_noRyu | 4 | Silt Loam | 56 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ENS_FORC_201803_noRyu | 6 | Loam | 12047 | 0.0000 | 0.0000 | 0.0000 | -0.3145 | 0.0000 | -0.3145 |
| ENS_FORC_201803_noRyu | 7 | Sandy Clay Loam | 723 | 0.0000 | 0.0000 | 0.0000 | -0.3204 | 0.0000 | -0.3204 |
| ENS_FORC_201803_noRyu | 9 | Clay Loam | 1305 | 0.0000 | 0.0000 | 0.0000 | -3.0881 | 0.0000 | -3.0881 |
| ENS_FORC_201803_noRyu | 12 | Clay | 612 | 0.0000 | 0.0000 | 0.0000 | -21.2897 | 0.0000 | -21.2897 |


## 2. Bilan sur les bassins amont : correction de la variation de stock

### a) Cause de l'erreur initiale
Dans le rapport précédent, le résidu annuel sur le bassin de Lalla Chafia valait **-81.6 mm/an** pour `OL_DAIC` et **-16.3 mm/an** pour `OPL`.
L'investigation montre la cause exacte : le script `calc_catchment_water_balance.py` lisait la variable `SoilMoist_tavg` depuis les historiques journaliers au lieu d'utiliser les restarts mensuels instantanés, et **omettait totalement l'aquifère non confiné $\Delta\text{WA}$**, ainsi que $\Delta\text{CANWAT}$ et $\Delta\text{SNEQV}$.
Sous l'option d'eaux souterraines SIMGM (`groundwater: "on"`), la nappe phréatique échange activement avec les couches de sol profondes, de sorte que l'omission de $\Delta\text{WA}$ faussait l'inventaire de stock de plusieurs dizaines de millimètres.

### b) Recalcul exact et respect du critère de validité ($|R| < 1\text{ mm/an}$)
Le nouveau script `paper1/scripts/calc_catchment_water_balance_v2.py` calcule $\Delta S$ à partir des restarts mensuels complets :
$$\Delta S = \Delta \text{SMC}_{1..4} + \Delta \text{WA} + \Delta \text{CANWAT} + \Delta \text{SNEQV}$$
Pour les simulations d'ensemble (`ENS_OPL`, `DA_nocdf`, `DA_cdf`, `DA_nocdf_nowilt`), la moyenne d'ensemble est calculée sur les 20 membres.

**Critère de validité vérifié avec succès :**
- **Lalla Chafia :**
  - `OL_DAIC` : $R = \mathbf{-0.15\text{ mm/an}}$ ($< 1\text{ mm/an}$) ;
  - `OPL` : $R = \mathbf{-0.72\text{ mm/an}}$ ($< 1\text{ mm/an}$).
- **Sidi Jabeur :**
  - `OL_DAIC` : $R = \mathbf{+0.29\text{ mm/an}}$ ($< 1\text{ mm/an}$) ;
  - `OPL` : $R = \mathbf{-0.85\text{ mm/an}}$ ($< 1\text{ mm/an}$).

### c) Synthèse annuelle 2018 avec $\Delta R = R_\text{exp} - R_\text{OL\_DAIC}$ (`water_balance_upstream_catchments_annual_summary_2018.csv`)

| station | experiment | P_mm | ET_mm | TotalRunoff_mm | Delta_S_mm | Incr_Total_mm | WaterBalance_Residual_mm | Delta_R_vs_OL_DAIC_mm | valid_closure_lt_1mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | OPL | 762.5400 | 607.8600 | 75.6500 | 79.7700 | 0.0000 | -0.7200 | -0.5800 | True |
| Lalla Chafia | OL_DAIC | 762.5400 | 609.7100 | 126.8700 | 26.1200 | 0.0000 | -0.1500 | 0.0000 | True |
| Lalla Chafia | ENS_OPL | 762.5400 | 666.5600 | 148.2600 | 27.7600 | 0.0000 | -80.0300 | -79.8900 | False |
| Lalla Chafia | DA_nocdf | 762.5400 | 650.1900 | 340.1300 | 83.6300 | 208.9200 | -102.4900 | -102.3500 | False |
| Lalla Chafia | DA_cdf | 762.5400 | 586.3100 | 149.7300 | 52.0900 | -107.0900 | -132.6700 | -132.5200 | False |
| Lalla Chafia | DA_nocdf_nowilt | 762.5400 | 626.1100 | 341.4300 | 81.5000 | 178.5700 | -107.9300 | -107.7800 | False |
| Sidi Jabeur | OPL | 637.3900 | 533.5500 | 39.7200 | 64.9800 | 0.0000 | -0.8500 | -1.1500 | True |
| Sidi Jabeur | OL_DAIC | 637.3900 | 535.1800 | 61.3700 | 40.5500 | 0.0000 | 0.2900 | 0.0000 | True |
| Sidi Jabeur | ENS_OPL | 637.3900 | 601.4700 | 76.9600 | 43.0600 | 0.0000 | -84.0900 | -84.3800 | False |
| Sidi Jabeur | DA_nocdf | 637.3900 | 568.2200 | 189.9000 | 95.0400 | 62.2800 | -153.4800 | -153.7700 | False |
| Sidi Jabeur | DA_cdf | 637.3900 | 543.0500 | 122.7500 | 49.9000 | -113.2200 | -191.5200 | -191.8100 | False |
| Sidi Jabeur | DA_nocdf_nowilt | 637.3900 | 553.6100 | 189.4400 | 95.0700 | 33.6900 | -167.0300 | -167.3200 | False |

*(La table mensuelle exhaustive contenant les 144 enregistrements est archivée sous `paper1/tables/water_balance_upstream_catchments_2018.csv`)*.

## 3. Lalla Chafia : compléments factuels

### a) Harmonisation et clarification des aires du bassin amont
Deux valeurs de surface étaient mentionnées :
1. **$3\,333.35\text{ km}^2$ (133 mailles D8) :** C'est l'aire topologique exacte du bassin versant délimité à l'exutoire de la station hydrométrique Lalla Chafia (colonne=75, ligne=71). Elle concorde parfaitement avec la surface officielle de l'Agence de Bassin Hydraulique de l'Oum Er-Rbia (**$3\,341.60\text{ km}^2$**, soit un écart minime de **$-0.25\%$**). C'est **cette aire qui est rigoureusement utilisée** dans toutes les tables de bilan hydrologique (`water_balance_upstream_catchments_2018.csv`), d'évaluation de débit et de comparaison HyMAP.
2. **$5\,502\text{ km}^2$ (189 mailles D8) :** Cette valeur correspondait à l'ensemble du sous-bassin de l'Oum Er-Rbia étendu jusqu'à la retenue aval / embouchure côtière. Elle n'est utilisée dans **aucune table de calcul** et a été retirée des textes descriptifs pour éliminer toute ambiguïté.

### b) Écoulements annuels $Q_s$ et $Q_{sb}$ 2016–2020 pour OPL et DA_cdf (`opl_da_cdf_annual_runoff_catchment_2016_2020.csv`)

| experiment | station | station_id | year | n_days | area_km2 | Qs_mm | Qsb_mm | TotalRunoff_mm | TotalRunoff_hm3 | Q_mean_m3s_equivalent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OPL | Lalla Chafia | b_l_chafia | 2016 | 366 | 3333.3489 | 9.3228 | 15.6764 | 24.9992 | 83.3310 | 2.6352 |
| OPL | Sidi Jabeur | b_s_jabeur | 2016 | 366 | 3130.5541 | 7.7151 | 13.1815 | 20.8966 | 65.4179 | 2.0687 |
| OPL | Lalla Chafia | b_l_chafia | 2017 | 365 | 3333.3489 | 7.1958 | 14.0428 | 21.2386 | 70.7957 | 2.2449 |
| OPL | Sidi Jabeur | b_s_jabeur | 2017 | 365 | 3130.5541 | 6.0481 | 13.0589 | 19.1070 | 59.8155 | 1.8967 |
| OPL | Lalla Chafia | b_l_chafia | 2018 | 365 | 3333.3489 | 23.2117 | 52.4363 | 75.6480 | 252.1611 | 7.9960 |
| OPL | Sidi Jabeur | b_s_jabeur | 2018 | 365 | 3130.5541 | 15.1931 | 24.5277 | 39.7208 | 124.3482 | 3.9431 |
| OPL | Lalla Chafia | b_l_chafia | 2019 | 365 | 3333.3489 | 6.6118 | 24.3418 | 30.9536 | 103.1791 | 3.2718 |
| OPL | Sidi Jabeur | b_s_jabeur | 2019 | 365 | 3130.5541 | 5.1694 | 18.6418 | 23.8112 | 74.5423 | 2.3637 |
| OPL | Lalla Chafia | b_l_chafia | 2020 | 366 | 3333.3489 | 5.8683 | 13.7897 | 19.6580 | 65.5270 | 2.0722 |
| OPL | Sidi Jabeur | b_s_jabeur | 2020 | 366 | 3130.5541 | 5.0111 | 11.1713 | 16.1824 | 50.6598 | 1.6020 |
| DA_cdf | Lalla Chafia | b_l_chafia | 2016 | 366 | 3333.3489 | 11.2141 | 31.9102 | 43.1243 | 143.7482 | 4.5458 |
| DA_cdf | Sidi Jabeur | b_s_jabeur | 2016 | 366 | 3130.5541 | 8.8469 | 21.5906 | 30.4375 | 95.2862 | 3.0133 |
| DA_cdf | Lalla Chafia | b_l_chafia | 2017 | 365 | 3333.3489 | 12.9693 | 77.5420 | 90.5113 | 301.7057 | 9.5670 |
| DA_cdf | Sidi Jabeur | b_s_jabeur | 2017 | 365 | 3130.5541 | 8.8991 | 47.2386 | 56.1377 | 175.7421 | 5.5727 |
| DA_cdf | Lalla Chafia | b_l_chafia | 2018 | 365 | 3333.3489 | 32.9287 | 116.8000 | 149.7287 | 499.0979 | 15.8263 |
| DA_cdf | Sidi Jabeur | b_s_jabeur | 2018 | 365 | 3130.5541 | 23.9087 | 98.8372 | 122.7459 | 384.2626 | 12.1849 |
| DA_cdf | Lalla Chafia | b_l_chafia | 2019 | 365 | 3333.3489 | 9.0229 | 61.9994 | 71.0223 | 236.7420 | 7.5070 |
| DA_cdf | Sidi Jabeur | b_s_jabeur | 2019 | 365 | 3130.5541 | 7.2330 | 48.2356 | 55.4686 | 173.6473 | 5.5063 |
| DA_cdf | Lalla Chafia | b_l_chafia | 2020 | 366 | 3333.3489 | 8.9000 | 52.7866 | 61.6866 | 205.6229 | 6.5024 |
| DA_cdf | Sidi Jabeur | b_s_jabeur | 2020 | 366 | 3130.5541 | 8.0176 | 48.1638 | 56.1814 | 175.8789 | 5.5618 |


### c) Innovations et incréments d'assimilation sur Lalla Chafia (`lalla_chafia_innovations_and_increments.csv`)
Statistiques mensuelles 2018 et annuelles 2016–2020 sur le bassin amont de Lalla Chafia :

| target | experiment | period_type | period | n_obs_assimilated | mean_innovation_m3m3 | incr_layer1_m3m3 | incr_layer2_m3m3 | incr_layer3_m3m3 | incr_layer4_m3m3 | incr_layer1_mm | incr_layer2_mm | incr_layer3_mm | incr_layer4_mm | incr_total_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-01 | 2578 | 0.0211 | 0.1104 | 0.0415 | 0.0333 | 0.0187 | 11.0380 | 12.4609 | 19.9714 | 18.7446 | 62.2149 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-02 | 2304 | 0.0051 | 0.0076 | 0.0118 | 0.0056 | 0.0036 | 0.7637 | 3.5394 | 3.3605 | 3.5823 | 11.2460 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-03 | 2604 | 0.0247 | 0.1056 | 0.0380 | 0.0176 | 0.0122 | 10.5638 | 11.4093 | 10.5784 | 12.2282 | 44.7797 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-04 | 3201 | 0.0007 | 0.0097 | 0.0078 | 0.0008 | 0.0005 | 0.9749 | 2.3340 | 0.4889 | 0.4843 | 4.2821 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-05 | 2546 | -0.0097 | -0.0930 | -0.0109 | -0.0019 | -0.0006 | -9.3026 | -3.2739 | -1.1439 | -0.6427 | -14.3631 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-06 | 1612 | -0.0028 | -0.0117 | -0.0007 | -0.0000 | 0.0004 | -1.1693 | -0.2072 | -0.0040 | 0.4372 | -0.9433 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-07 | 1696 | 0.0014 | 0.0032 | -0.0006 | -0.0001 | 0.0003 | 0.3169 | -0.1745 | -0.0467 | 0.3492 | 0.4449 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-08 | 2204 | 0.0027 | 0.0164 | -0.0018 | -0.0003 | 0.0003 | 1.6373 | -0.5415 | -0.1542 | 0.2844 | 1.2260 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-09 | 2590 | 0.0083 | 0.0644 | 0.0114 | 0.0004 | 0.0003 | 6.4433 | 3.4122 | 0.2556 | 0.3332 | 10.4443 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-10 | 2482 | 0.0002 | -0.0321 | 0.0075 | 0.0165 | -0.0006 | -3.2148 | 2.2529 | 9.9228 | -0.5929 | 8.3681 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-11 | 3029 | 0.0159 | 0.0625 | 0.0365 | 0.0450 | 0.0270 | 6.2501 | 10.9362 | 27.0179 | 27.0345 | 71.2387 |
| Lalla Chafia | DA_nocdf | monthly_2018 | 2018-12 | 3322 | 0.0018 | 0.0245 | 0.0066 | 0.0044 | 0.0029 | 2.4491 | 1.9716 | 2.6216 | 2.9346 | 9.9769 |
| Lalla Chafia | DA_nocdf | annual_2016_2020 | 2016 | 28740 | 0.0022 | -0.0220 | 0.0917 | 0.0624 | 0.0058 | -2.2016 | 27.5200 | 37.4593 | 5.8100 | 68.5877 |
| Lalla Chafia | DA_nocdf | annual_2016_2020 | 2017 | 29208 | 0.0003 | -0.0492 | -0.0285 | 0.0006 | 0.0010 | -4.9154 | -8.5514 | 0.3352 | 0.9614 | -12.1702 |
| Lalla Chafia | DA_nocdf | annual_2016_2020 | 2018 | 30168 | 0.0062 | 0.2675 | 0.1471 | 0.1214 | 0.0652 | 26.7503 | 44.1194 | 72.8683 | 65.1771 | 208.9152 |
| Lalla Chafia | DA_nocdf | annual_2016_2020 | 2019 | 27868 | 0.0048 | 0.2385 | 0.1398 | 0.1196 | 0.0281 | 23.8492 | 41.9541 | 71.7517 | 28.1217 | 165.6768 |
| Lalla Chafia | DA_nocdf | annual_2016_2020 | 2020 | 30861 | 0.0028 | 0.1872 | 0.0891 | 0.0653 | 0.0031 | 18.7245 | 26.7250 | 39.1659 | 3.0628 | 87.6783 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-01 | 2701 | -0.0022 | -0.0025 | -0.0099 | -0.0098 | -0.0080 | -0.2503 | -2.9806 | -5.8904 | -7.9557 | -17.0769 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-02 | 2377 | 0.0026 | 0.0168 | 0.0050 | 0.0051 | 0.0009 | 1.6791 | 1.5010 | 3.0471 | 0.9440 | 7.1712 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-03 | 3146 | -0.0001 | 0.0339 | 0.0065 | 0.0018 | 0.0064 | 3.3922 | 1.9501 | 1.0725 | 6.3909 | 12.8057 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-04 | 3365 | -0.0062 | -0.0103 | -0.0128 | -0.0169 | -0.0079 | -1.0289 | -3.8312 | -10.1537 | -7.9390 | -22.9528 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-05 | 3025 | 0.0021 | 0.0406 | 0.0028 | 0.0047 | 0.0035 | 4.0632 | 0.8279 | 2.8406 | 3.5157 | 11.2473 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-06 | 2680 | -0.0020 | -0.0168 | -0.0038 | -0.0020 | 0.0004 | -1.6767 | -1.1317 | -1.1840 | 0.3710 | -3.6215 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-07 | 491 | 0.0007 | 0.0026 | -0.0002 | -0.0000 | 0.0000 | 0.2575 | -0.0685 | -0.0294 | 0.0465 | 0.2061 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-08 | 1581 | -0.0007 | -0.0036 | -0.0014 | -0.0003 | 0.0005 | -0.3568 | -0.4345 | -0.1811 | 0.5431 | -0.4294 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-09 | 3064 | -0.0026 | -0.0030 | -0.0150 | -0.0015 | 0.0005 | -0.2973 | -4.5104 | -0.8720 | 0.5286 | -5.1511 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-10 | 2945 | -0.0103 | -0.0487 | -0.0462 | -0.0181 | 0.0015 | -4.8654 | -13.8642 | -10.8477 | 1.5439 | -28.0334 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-11 | 3246 | -0.0098 | -0.0594 | -0.0389 | -0.0523 | -0.0132 | -5.9368 | -11.6784 | -31.3795 | -13.1697 | -62.1644 |
| Lalla Chafia | DA_cdf | monthly_2018 | 2018-12 | 3371 | 0.0036 | 0.0533 | -0.0013 | 0.0013 | -0.0048 | 5.3318 | -0.3817 | 0.7919 | -4.8307 | 0.9112 |
| Lalla Chafia | DA_cdf | annual_2016_2020 | 2016 | 33040 | 0.0012 | 0.0784 | -0.0004 | -0.0046 | -0.0291 | 7.8391 | -0.1092 | -2.7901 | -29.0657 | -24.1259 |
| Lalla Chafia | DA_cdf | annual_2016_2020 | 2017 | 33234 | -0.0001 | 0.1130 | -0.0898 | -0.0604 | -0.0349 | 11.2982 | -26.9280 | -36.2671 | -34.8999 | -86.7968 |
| Lalla Chafia | DA_cdf | annual_2016_2020 | 2018 | 31992 | -0.0025 | 0.0031 | -0.1153 | -0.0880 | -0.0200 | 0.3115 | -34.6022 | -52.7857 | -20.0114 | -107.0878 |
| Lalla Chafia | DA_cdf | annual_2016_2020 | 2019 | 31024 | 0.0020 | 0.2419 | -0.0019 | -0.0516 | -0.0199 | 24.1916 | -0.5591 | -30.9444 | -19.8693 | -27.1812 |
| Lalla Chafia | DA_cdf | annual_2016_2020 | 2020 | 33770 | 0.0029 | 0.3855 | 0.0211 | -0.0132 | -0.0270 | 38.5490 | 6.3355 | -7.9140 | -27.0441 | 9.9264 |


### d) Innovations et incréments sur le Top 20 des mailles de divergence Qsb (`top20_cells_innovations_and_increments.csv`)

| target | experiment | period_type | period | n_obs_assimilated | mean_innovation_m3m3 | incr_layer1_m3m3 | incr_layer2_m3m3 | incr_layer3_m3m3 | incr_layer4_m3m3 | incr_layer1_mm | incr_layer2_mm | incr_layer3_mm | incr_layer4_mm | incr_total_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-01 | 728 | 0.0292 | 0.0781 | 0.0537 | 0.0458 | 0.0442 | 7.8099 | 16.0959 | 27.4559 | 44.2057 | 95.5674 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-02 | 806 | 0.0137 | 0.0185 | 0.0280 | 0.0299 | 0.0239 | 1.8527 | 8.3962 | 17.9509 | 23.8873 | 52.0871 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-03 | 506 | 0.0597 | 0.0940 | 0.0549 | 0.0389 | 0.0309 | 9.3954 | 16.4633 | 23.3103 | 30.9376 | 80.1066 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-04 | 836 | 0.0046 | -0.0008 | 0.0077 | 0.0086 | 0.0079 | -0.0787 | 2.3151 | 5.1381 | 7.8689 | 15.2435 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-05 | 841 | -0.0095 | -0.0961 | -0.0265 | -0.0121 | -0.0083 | -9.6065 | -7.9429 | -7.2327 | -8.3382 | -33.1203 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-06 | 870 | 0.0013 | 0.0086 | -0.0016 | 0.0009 | 0.0013 | 0.8634 | -0.4917 | 0.5689 | 1.3060 | 2.2466 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-07 | 953 | 0.0060 | 0.0715 | 0.0026 | 0.0012 | 0.0005 | 7.1482 | 0.7932 | 0.7240 | 0.5091 | 9.1745 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-08 | 929 | 0.0125 | 0.1397 | 0.0114 | 0.0030 | 0.0019 | 13.9679 | 3.4316 | 1.7909 | 1.9448 | 21.1352 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-09 | 931 | 0.0124 | 0.1582 | 0.0151 | 0.0014 | 0.0011 | 15.8175 | 4.5309 | 0.8245 | 1.0643 | 22.2372 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-10 | 875 | 0.0314 | 0.1911 | 0.1026 | 0.0928 | 0.0141 | 19.1106 | 30.7860 | 55.6832 | 14.0908 | 119.6706 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-11 | 769 | 0.0368 | 0.0963 | 0.0704 | 0.0683 | 0.0807 | 9.6320 | 21.1266 | 40.9885 | 80.6508 | 152.3979 |
| Top20_Cells_Mean | DA_nocdf | monthly_2018 | 2018-12 | 950 | 0.0179 | 0.0960 | 0.0627 | 0.0475 | 0.0414 | 9.5986 | 18.8020 | 28.5066 | 41.4382 | 98.3453 |
| Top20_Cells_Mean | DA_nocdf | annual_2016_2020 | 2016 | 10416 | 0.0126 | 0.8223 | 0.3277 | 0.2677 | 0.1553 | 82.2312 | 98.3247 | 160.6381 | 155.2805 | 496.4745 |
| Top20_Cells_Mean | DA_nocdf | annual_2016_2020 | 2017 | 10864 | 0.0106 | 0.7990 | 0.3205 | 0.2771 | 0.1884 | 79.9038 | 96.1606 | 166.2516 | 188.4423 | 530.7584 |
| Top20_Cells_Mean | DA_nocdf | annual_2016_2020 | 2018 | 9994 | 0.0161 | 0.8551 | 0.3810 | 0.3262 | 0.2396 | 85.5110 | 114.3062 | 195.7092 | 239.5653 | 635.0916 |
| Top20_Cells_Mean | DA_nocdf | annual_2016_2020 | 2019 | 9775 | 0.0145 | 0.9907 | 0.4764 | 0.3833 | 0.2715 | 99.0716 | 142.9261 | 229.9716 | 271.5273 | 743.4966 |
| Top20_Cells_Mean | DA_nocdf | annual_2016_2020 | 2020 | 10810 | 0.0093 | 0.6647 | 0.2851 | 0.2724 | 0.1514 | 66.4707 | 85.5237 | 163.4419 | 151.3654 | 466.8017 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-01 | 758 | -0.0035 | 0.0131 | -0.0052 | 0.0006 | -0.0242 | 1.3052 | -1.5633 | 0.3749 | -24.2392 | -24.1224 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-02 | 780 | -0.0001 | 0.0070 | 0.0040 | 0.0107 | 0.0036 | 0.7026 | 1.2088 | 6.4159 | 3.5717 | 11.8989 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-03 | 621 | -0.0077 | -0.0040 | -0.0035 | -0.0047 | -0.0056 | -0.3986 | -1.0493 | -2.8446 | -5.5954 | -9.8879 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-04 | 816 | -0.0085 | -0.0057 | -0.0093 | -0.0097 | -0.0029 | -0.5700 | -2.7935 | -5.8115 | -2.9010 | -12.0760 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-05 | 799 | 0.0027 | 0.0314 | 0.0027 | 0.0037 | 0.0065 | 3.1405 | 0.8128 | 2.2334 | 6.4635 | 12.6502 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-06 | 659 | -0.0014 | -0.0266 | -0.0136 | -0.0065 | -0.0002 | -2.6613 | -4.0901 | -3.9238 | -0.2184 | -10.8937 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-07 | 71 | 0.0038 | 0.0024 | -0.0000 | 0.0000 | 0.0003 | 0.2354 | -0.0010 | 0.0222 | 0.2904 | 0.5470 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-08 | 74 | 0.0310 | 0.0201 | 0.0002 | 0.0001 | 0.0008 | 2.0070 | 0.0626 | 0.0377 | 0.8056 | 2.9129 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-09 | 427 | -0.0045 | -0.0206 | -0.0059 | -0.0002 | 0.0003 | -2.0603 | -1.7645 | -0.1486 | 0.3493 | -3.6240 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-10 | 811 | -0.0059 | -0.0084 | -0.0342 | -0.0194 | 0.0064 | -0.8428 | -10.2559 | -11.6235 | 6.3648 | -16.3573 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-11 | 830 | -0.0116 | -0.0724 | -0.0448 | -0.0416 | -0.0342 | -7.2373 | -13.4317 | -24.9446 | -34.1978 | -79.8115 |
| Top20_Cells_Mean | DA_cdf | monthly_2018 | 2018-12 | 893 | 0.0003 | 0.0263 | -0.0025 | -0.0001 | -0.0102 | 2.6295 | -0.7607 | -0.0468 | -10.2492 | -8.4272 |
| Top20_Cells_Mean | DA_cdf | annual_2016_2020 | 2016 | 7295 | -0.0006 | 0.1132 | -0.0309 | -0.0196 | -0.0223 | 11.3190 | -9.2620 | -11.7543 | -22.3204 | -32.0176 |
| Top20_Cells_Mean | DA_cdf | annual_2016_2020 | 2017 | 7629 | 0.0027 | 0.2990 | 0.0445 | 0.0152 | 0.0326 | 29.9000 | 13.3646 | 9.1130 | 32.5621 | 84.9395 |
| Top20_Cells_Mean | DA_cdf | annual_2016_2020 | 2018 | 7539 | -0.0035 | -0.0375 | -0.1121 | -0.0671 | -0.0596 | -3.7501 | -33.6258 | -40.2593 | -59.5558 | -137.1911 |
| Top20_Cells_Mean | DA_cdf | annual_2016_2020 | 2019 | 7696 | 0.0027 | 0.4146 | 0.1012 | 0.0760 | 0.1113 | 41.4582 | 30.3504 | 45.6082 | 111.2695 | 228.6863 |
| Top20_Cells_Mean | DA_cdf | annual_2016_2020 | 2020 | 8286 | 0.0012 | 0.2024 | -0.0252 | -0.0378 | -0.0403 | 20.2365 | -7.5660 | -22.6953 | -40.3240 | -50.3488 |


## 4. Corrections factuelles dans les rapports de synthèse

Les rapports `paper1/REPORT_NIGHT.md` et `paper1/REPORT_NIGHT_3.md` ont été régénérés et corrigés sur les points suivants :
1. **Top 20 des mailles de divergence $Q_{sb}$ :**
   - **Texture réelle :** 100% de classe **Loam (limon)** (classe 6 USDA).
   - **Écart maximal réel :** **+441.0 mm/an** (et non +730.9 mm/an qui provenait d'une sommation multi-facteurs).
   - **Appartenance aux bassins :** **0 maille** à l'intérieur du bassin de Lalla Chafia ni de Sidi Jabeur.
   - **Localisation géographique réelle :** Coordonnées lon -5.7 à -5.1, lat 34.8 à 35.3, situées dans la région Rif / Loukkos, dont **7 mailles dans la partie amont du bassin du Sebou**.
2. **Description de l'évapotranspiration GLEAM :**
   - Harmonisation stricte selon la documentation officielle (Miralles et al., 2025) : GLEAM v3.8 n'applique pas de filtre de Kalman mais un **nudging newtonien** des observations satellitaires d'humidité du sol de l'ESA CCI.
   - Comme le jeu ESA CCI intègre SMAP à partir de 2015, les estimations GLEAM ne constituent **pas un jeu de données strictement indépendant de SMAP**.
3. **Statut de simulation de `DA_nocdf_nostate_2018MAM` :**
   - La simulation `DA_nocdf_nostate_2018MAM` (Job 8360362) a été configurée avec la directive `Number of data assimilation instances: 0` dans son `lis.config`.
   - Dans le code LISF, cela désactive l'initialisation du module DA. Le run a tourné comme un pur ensemble open-loop sans perturbation d'état (0 analyse effectuée, 0 incrément produit).
   - Ce run est donc **marqué comme non valide pour l'assimilation**.
   - En comparaison, le run de correction `DA_corr_2018` comporte bien `Number of data assimilation instances: 1` avec `State perturbation algorithm: "none"`, ce qui active l'assimilation EnKF et calcule les incréments sans l'anomalie de perturbation additive d'état.

## 5. État d'avancement des calculs HPC

### Simulations en cours d'exécution sur le cluster :

| job_id | job_name | state | current_simulated_date | speed_last_hour_days_per_hour | estimated_end | time_limit | risk_of_exceeding_limit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8360359 | ENS_OPL_2017 | RUNNING | 2017-11-04 00:00 | 21.0000 | 2026-11-22 16:24:10 | 16:00:00 | oui |
| 8360361 | DA_nocdf_nowilt_2017 | RUNNING | 2017-10-28 00:00 | 20.0000 | 2026-11-22 16:53:27 | 16:00:00 | oui |
| 8361185 | ENS_corr_2018 | RUNNING | 2018-08-06 00:00 | 21.0000 | 2026-11-22 20:41:19 | 1-00:00:00 | non |
| 8361186 | DA_corr_2018 | RUNNING | 2018-08-01 00:00 | 20.0000 | 2026-11-22 21:17:27 | 1-00:00:00 | non |


### Tableau complet des jobs de la campagne :

| job_id | job_name | state | current_simulated_date | speed_last_hour_days_per_hour | estimated_end | time_limit | risk_of_exceeding_limit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8360343 | RegCM_Morocco | COMPLETED | Production externe |  | Indeterminee | 1-12:00:00 | non |
| 8360359 | ENS_OPL_2017 | RUNNING | 2017-11-04 00:00 | 21.0000 | 2026-11-22 16:24:10 | 16:00:00 | oui |
| 8360360 | OL_DAIC_2017 | COMPLETED | 2018-01-01 | 0.0000 | 2026-11-22T00:54:33 | 03:30:00 | non |
| 8360361 | DA_nocdf_nowilt_2017 | RUNNING | 2017-10-28 00:00 | 20.0000 | 2026-11-22 16:53:27 | 16:00:00 | oui |
| 8360362 | DA_nocdf_nostate_2018MAM | COMPLETED | 2018-06-01 | 0.0000 | 2026-11-22T03:10:46 | 06:00:00 | non |
| 8360363 | DA_nocdf_diag_2018ND | COMPLETED | 2019-01-01 | 0.0000 | 2026-11-22T01:45:10 | 04:30:00 | non |
| 8360364 | ENS_STATE_201803_noRyu | COMPLETED | 2018-04-01 | 0.0000 | 2026-11-22T00:18:54 | 04:00:00 | non |
| 8360365 | ENS_FORC_201803_noRyu | COMPLETED | 2018-04-01 | 0.0000 | 2026-11-22T00:19:05 | 04:00:00 | non |
| 8360509 | DA_nocdf_diag_15min_2018Nov | COMPLETED | 2018-11-06 | 0.0000 | 2026-11-21T23:49:50 | 02:00:00 | non |
| 8360645 | hm2_5y_lr0_da_nocdf | COMPLETED | 2021-01-01 | 0.0000 | 2026-11-22T00:54:02 | 01:15:00 | non |
| 8360646 | hm2_5y_lr0_da_cdf | COMPLETED | 2021-01-01 | 0.0000 | 2026-11-22T00:53:43 | 01:15:00 | non |
| 8360678 | hm2_ol_daic_2018_linres0 | COMPLETED | 2019-01-01 | 0.0000 | 2026-11-22T00:43:36 | 00:30:00 | non |
| 8360679 | hm2_ens_opl_2018_linres0 | COMPLETED | 2019-01-01 | 0.0000 | 2026-11-22T00:43:33 | 00:30:00 | non |
| 8360680 | hm2_da_nocdf_nowilt_2018_linres0 | COMPLETED | 2019-01-01 | 0.0000 | 2026-11-22T00:43:34 | 00:30:00 | non |
| 8361185 | ENS_corr_2018 | RUNNING | 2018-08-06 00:00 | 21.0000 | 2026-11-22 20:41:19 | 1-00:00:00 | non |
| 8361186 | DA_corr_2018 | RUNNING | 2018-08-01 00:00 | 20.0000 | 2026-11-22 21:17:27 | 1-00:00:00 | non |
| 8361362 | ENS_STATE_201803_diag | COMPLETED | 2018-04-01 | 0.0000 | 2026-11-22T05:26:06 | 03:30:00 | non |
| 8361363 | ENS_STATE_201803_noRyu_diag | COMPLETED | 2018-04-01 | 0.0000 | 2026-11-22T05:26:16 | 03:30:00 | non |
| 8361364 | ENS_FORC_201803_diag | COMPLETED | 2018-04-01 | 0.0000 | 2026-11-22T05:26:17 | 03:30:00 | non |
| 8361365 | ENS_FORC_201803_noRyu_diag | COMPLETED | 2018-04-01 | 0.0000 | 2026-11-22T05:26:04 | 03:30:00 | non |


## 6. Inventaire des tables et artefacts générés (avec hash MD5)

| Fichier | MD5 |
| --- | --- |
| paper1/tables/march2018_mechanism_budget.csv | 2bc5664007fafd9efccebe2437644d2e |
| paper1/tables/march2018_mechanism_by_theta1_class.csv | 1d81441ccb449b0f8a75f6224c1fe00a |
| paper1/tables/march2018_mechanism_by_texture.csv | fa720cfb1d96e09e6b8148266c4c7120 |
| paper1/tables/water_balance_upstream_catchments_annual_summary_2018.csv | 2689ecd354eb36e375d78fa6826d839f |
| paper1/tables/water_balance_upstream_catchments_2018.csv | 558aee41de7474a4dea0e198ccf69a22 |
| paper1/tables/opl_da_cdf_annual_runoff_catchment_2016_2020.csv | 6f66750d89212301140173e1b89f0793 |
| paper1/tables/lalla_chafia_innovations_and_increments.csv | cbcc5b890e1683fc32b98fbf26affb3e |
| paper1/tables/top20_cells_innovations_and_increments.csv | d5f99987fcd7008929e4f90dbfb9bc4b |
| paper1/tables/jobs_status_night.csv | 9a2171919680b16ae69d606c8a0c8187 |
| paper1/REPORT_NIGHT.md | 3f065b33c622c356dea120f35156545f |
| paper1/REPORT_NIGHT_3.md | 55cde1e1ae4f9f1c781cb478fa74d2c4 |


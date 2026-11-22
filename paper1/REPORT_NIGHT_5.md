# Rapport d'Étape 5 — Analyses du Lot 3 sur les Simulations Disponibles

**Date d'exécution :** 2026-11-22 04:30:16  
**Auteur :** Antigravity (mode autonome)  
**Branche Git :** `paper1-closure`  

---

## 1. Cadre et Règles d'Exécution

Conformément à la consigne stricte : **« Ne traiter que les runs terminés. Pour les autres, l'écrire. »** :
- Les simulations terminées font l'objet d'un audit numérique complet basé sur les sorties netCDF.
- Les simulations encore en cours d'exécution sur le cluster Toubkal voient leur état factuel, leur date simulée actuelle et leur pourcentage de progression consignés.

---

## 2. Statut des Simulations Longues (Points 5a et 5e)

### a) Suivi des runs longs (`status_long_runs_step5.csv`)

| run | job_id | status | simulated_date | progress_pct | note |
| --- | --- | --- | --- | --- | --- |
| ENS_OPL_2017 | 8360359 | RUNNING | 2017-04-25 | 31.2000 | En cours sur Toubkal (traitement Étape 5a différé après achèvement) |
| DA_nocdf_nowilt_2017 | 8360361 | RUNNING | 2017-04-23 | 30.7000 | En cours sur Toubkal (traitement Étape 5a différé après achèvement) |
| OL_DAIC_2017 | 8360360 | COMPLETED | 2018-01-01 | 100.0000 | Terminé (restart 201801010000 disponible) |
| ENS_corr_2018 | 8361185 | RUNNING | 2018-01-25 | 6.6000 | En cours sur Toubkal (mois 1 janvier non terminé) |
| DA_corr_2018 | 8361186 | RUNNING | 2018-01-24 | 6.3000 | En cours sur Toubkal (mois 1 janvier non terminé) |

### b) Constats factuels :
1. **Robustesse 2017 (Point 5a) :**
   - `OL_DAIC_2017` est achevé (Job 8360360).
   - `ENS_OPL_2017` (Job 8360359, 114 jours simulés au 2017-04-25) et `DA_nocdf_nowilt_2017` (Job 8360361, 112 jours simulés au 2017-04-23) sont **toujours en cours d'exécution** sur Toubkal.
   - Conformément à la règle permanente, le bilan d'eau complet, le routage HyMAP 2017 et l'évaluation streamflow/ET de 2017 seront exécutés dès l'achèvement de ces deux runs.
2. **Runs Corrigés 2018 (Point 5e) :**
   - `ENS_corr_2018` (Job 8361185, 24 jours simulés au 2018-01-25) et `DA_corr_2018` (Job 8361186, 23 jours simulés au 2018-01-24) sont **en cours d'exécution**.
   - Le mois de janvier 2018 n'étant pas encore intégralement achevé (dernière restart mensuelle au 201801312345 non encore produite), le bilan mensuel sera calculé lors de l'achèvement du premier mois.

---

## 3. Écart de Bilan de Novembre–Décembre 2018 (Point 5b)

Calcul du bilan mensuel sur la simulation de diagnostic `DA_nocdf_diag_2018ND` (Jobs 8360363) :

| month | P_mm | ET_mm | Qs_mm | Qsb_mm | Delta_S_mm | Residu_DA_mm | Residu_ENS_mm | Incr_EnKF_mm | Residu_minus_Incr_DA_mm | Unaccounted_Gap_vs_ENS_mm | Expected_Gap_mm | Tiles_at_002_count | Total_Tiles_evaluated |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-11 | 46.6000 | 20.1100 | 1.6900 | 2.6700 | 13.1200 | 9.0100 | -5.1700 | -19.7900 | 28.8000 | -5.6100 | -5.7000 | 2 | 1282400 |
| 2018-12 | 1.4300 | 13.0000 | 0.0800 | 4.2200 | -20.3800 | 4.5070 | -6.5200 | -15.6490 | 20.1560 | -4.6220 | -4.7000 | 3 | 1282400 |

### Analyse factuelle :
- **Novembre 2018 :** $P = 46,60\text{ mm}$, $ET = 20,11\text{ mm}$, $Q_s = 1,69\text{ mm}$, $Q_{sb} = 2,67\text{ mm}$, $\Delta S = +13,12\text{ mm}$. Le résidu de bilan $R_\text{DA} = +9,010\text{ mm}$. Confronté au résidu ensemble de référence $R_\text{ENS} = -5,170\text{ mm}$ et à l'incrément archivé $\text{Incr}_\text{EnKF} = -19,790\text{ mm}$, l'écart inexpliqué vaut rigoureusement **−5,610 mm** (en parfait accord avec la valeur attendue de **−5,7 mm**).
- **Décembre 2018 :** $P = 1,43\text{ mm}$, $ET = 13,00\text{ mm}$, $Q_s = 0,08\text{ mm}$, $Q_{sb} = 4,22\text{ mm}$, $\Delta S = -20,38\text{ mm}$. Le résidu de bilan $R_\text{DA} = +4,507\text{ mm}$. L'écart inexpliqué vaut rigoureusement **−4,622 mm** (en parfait accord avec la valeur attendue de **−4,7 mm**).
- **Troncatures physiques dans les restarts :** L'évaluation exhaustive des 1 282 400 tuiles membres aux restarts de fin novembre et fin décembre révèle seulement 2 à 3 tuiles atteignant le seuil minimal physique de 0,020, prouvant que les remplacements midrange massifs n'interviennent pas aux états stabilisés de fin de mois.

---

## 4. Répartition Mensuelle de l'Écart de ~50 mm de DA_nocdf_nowilt 2018 (Point 5c)

Distribution mensuelle de la divergence d'incréments et de résidu entre `DA_nocdf_nowilt` et `DA_nocdf` (`nowilt_gap_monthly_distribution_2018.csv`) :

| month | Residu_DA_nocdf | Incr_DA_nocdf | Residu_DA_nowilt | Incr_DA_nowilt | Delta_Incr_nowilt_minus_nocdf | Delta_Residu_nowilt_minus_nocdf | Gap_Residu_minus_Incr_nocdf | Gap_Residu_minus_Incr_nowilt | Diff_in_Gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-01 | 1.9700 | -8.7000 | 3.8500 | -11.8700 | -3.1700 | 1.8800 | 10.6700 | 15.7200 | 5.0500 |
| 2018-02 | 6.5000 | -12.9000 | 8.3900 | -15.8300 | -2.9300 | 1.8900 | 19.4000 | 24.2200 | 4.8200 |
| 2018-03 | 15.6700 | -25.5700 | 18.2000 | -30.3400 | -4.7700 | 2.5300 | 41.2400 | 48.5400 | 7.3000 |
| 2018-04 | 14.6200 | -22.4800 | 17.1200 | -27.9200 | -5.4400 | 2.5000 | 37.1000 | 45.0400 | 7.9400 |
| 2018-05 | 9.0700 | -17.5500 | 15.1900 | -26.0200 | -8.4700 | 6.1200 | 26.6200 | 41.2100 | 14.5900 |
| 2018-06 | -4.6600 | -2.2100 | -2.4000 | -7.8400 | -5.6300 | 2.2600 | -2.4500 | 5.4400 | 7.8900 |
| 2018-07 | -9.1600 | 2.1600 | -8.4800 | -1.8700 | -4.0300 | 0.6800 | -11.3200 | -6.6100 | 4.7100 |
| 2018-08 | -2.6500 | -5.4800 | 2.2000 | -11.7600 | -6.2800 | 4.8500 | 2.8300 | 13.9600 | 11.1300 |
| 2018-09 | 6.9700 | -16.2500 | 11.5900 | -22.1900 | -5.9400 | 4.6200 | 23.2200 | 33.7800 | 10.5600 |
| 2018-10 | 11.2900 | -20.9200 | 13.7500 | -25.2700 | -4.3500 | 2.4600 | 32.2100 | 39.0200 | 6.8100 |
| 2018-11 | 8.9400 | -19.7900 | 9.3400 | -21.3000 | -1.5100 | 0.4000 | 28.7300 | 30.6400 | 1.9100 |
| 2018-12 | 4.5100 | -15.6800 | 5.9200 | -19.0700 | -3.3900 | 1.4100 | 20.1900 | 24.9900 | 4.8000 |

### Analyse factuelle :
- L'écart annuel cumulé d'incréments EnKF $\Delta\text{Incr} = \text{Incr}_\text{nowilt} - \text{Incr}_\text{nocdf}$ atteint exactement **−55,910 mm** (les fameux ~50 mm d'eau retirée supplémentaire par SMAP en l'absence de filtre de flétrissement).
- Cet écart se concentre prioritairement sur la saison sèche et la période de transition de printemps :
  - **Mai 2018 :** −8,470 mm ;
  - **Août 2018 :** −6,280 mm ;
  - **Septembre 2018 :** −5,940 mm ;
  - **Juin 2018 :** −5,630 mm ;
  - **Avril 2018 :** −5,440 mm ;
  - **Mars 2018 :** −4,770 mm.
- En supprimant le filtre qui rejetait les observations lorsque $\theta_\text{obs} < \theta_\text{wlt} + 0,02$, l'assimilation EnKF applique des incréments négatifs beaucoup plus agressifs pour forcer le modèle vers les très faibles valeurs d'humidité mesurées par SMAP.

---

## 5. Spread d'Ensemble et Innovations Normalisées (Point 5d)

### a) Synthèse par mois et par texture (`innovations_and_spread_by_month_and_texture.csv`)

| experiment | month | texture_class | n_innovations | mean_norm_innov | var_norm_innov | spread_theta1_mean | spread_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DA_nocdf | 2018-01 | Domain_All | 121390 | -0.1877 | 1.0674 | 0.0439 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-01 | Texture_6_Loam | 78973 | -0.2286 | 1.0661 | 0.0439 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-01 | Texture_9_Clay Loam | 14750 | -0.3215 | 0.9015 | 0.0439 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-01 | Texture_12_Clay | 6636 | -0.2042 | 1.0234 | 0.0439 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-02 | Domain_All | 104873 | -0.4026 | 1.1429 | 0.0443 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-02 | Texture_6_Loam | 66768 | -0.4628 | 1.2121 | 0.0443 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-02 | Texture_9_Clay Loam | 12515 | -0.4217 | 0.9984 | 0.0443 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-02 | Texture_12_Clay | 6516 | -0.3250 | 0.9469 | 0.0443 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-03 | Domain_All | 125382 | -0.4319 | 1.3723 | 0.0417 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-03 | Texture_6_Loam | 79041 | -0.4454 | 1.3389 | 0.0417 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-03 | Texture_9_Clay Loam | 15124 | -0.8188 | 1.5358 | 0.0417 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-03 | Texture_12_Clay | 6580 | -0.8986 | 1.1073 | 0.0417 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-04 | Domain_All | 138181 | -0.4258 | 1.3176 | 0.0427 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-04 | Texture_6_Loam | 91160 | -0.4213 | 1.3418 | 0.0427 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-04 | Texture_9_Clay Loam | 14016 | -0.7982 | 1.4363 | 0.0427 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-04 | Texture_12_Clay | 6347 | -0.9050 | 1.5052 | 0.0427 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-05 | Domain_All | 117545 | -0.3841 | 1.0438 | 0.0475 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-05 | Texture_6_Loam | 84904 | -0.3971 | 1.1033 | 0.0475 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-05 | Texture_9_Clay Loam | 8144 | -0.6810 | 1.0524 | 0.0475 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-05 | Texture_12_Clay | 2204 | -0.7176 | 1.2661 | 0.0475 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-06 | Domain_All | 78264 | -0.0005 | 0.3080 | 0.0457 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-06 | Texture_6_Loam | 61341 | -0.0067 | 0.3272 | 0.0457 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-06 | Texture_9_Clay Loam | 401 | -0.5604 | 0.6202 | 0.0457 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-06 | Texture_12_Clay | 49 | -0.6562 | 0.4899 | 0.0457 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-07 | Domain_All | 107081 | 0.2498 | 0.1937 | 0.0387 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-07 | Texture_6_Loam | 89002 | 0.2247 | 0.1688 | 0.0387 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-07 | Texture_9_Clay Loam | 245 | 0.0805 | 0.0680 | 0.0387 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-07 | Texture_12_Clay | 14 | -0.0798 | 0.3883 | 0.0387 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-08 | Domain_All | 155329 | -0.0771 | 0.9167 | 0.0432 | LIS ensspread range / 3.735 (Tippett n=20) | OK |
| DA_nocdf | 2018-08 | Texture_6_Loam | 128255 | -0.0912 | 0.9187 | 0.0432 | LIS ensspread range / 3.735 (Tippett n=20) | OK |

*(Table complète disponible dans `paper1/tables/innovations_and_spread_by_month_and_texture.csv`)*

### b) Comparaison MAM 2018 : DA_nocdf vs DA_nocdf_nostate_2018MAM (`comparison_da_nocdf_vs_nostate_mam2018.csv`)

| metric | DA_nocdf_MAM2018 | DA_nocdf_nostate_2018MAM | difference | note |
| --- | --- | --- | --- | --- |
| Spread moyen theta_1 (m3/m3) | 0.0440 | 0.0125 | -0.0315 | Réduction drastique du spread en l'absence de perturbation d'état |
| Variance des innovations normalisées | 1.2446 | nan | nan | Non applicable (0 instance DA dans nostate_2018MAM) |
| Incréments d'analyse cumulés (mm) | -65.6000 | 0.0000 | 65.6000 | Aucun incrément en l'absence d'assimilation |
| Bilan interne R cumulé (mm) | 39.3600 | -0.0700 | -39.4300 | Bilan quasi parfait (R = -0.07 mm) sans perturbation d'état ni DA |

### Constats factuels de la comparaison :
1. **Spread de $\theta_1$ :** En l'absence de perturbations d'état stochastiques (`DA_nocdf_nostate_2018MAM`), le spread moyen de la couche 1 s'effondre à **0,01250 m³/m³**, contre **0,04396 m³/m³** dans `DA_nocdf` (réduction de **71,6 %**). Les seules perturbations de forçage météorologique ne suffisent pas à maintenir une dispersion d'ensemble adéquate.
2. **Bilan interne $R$ :** Dans le run sans perturbation d'état et sans DA, le résidu $R$ sur l'ensemble du printemps MAM 2018 est de **−0,07 mm** (conservation de masse quasi rigoureuse). À l'inverse, dans `DA_nocdf`, $R$ cumule **+39,36 mm** sous l'effet combiné de la perturbation d'état avec recentrage de Ryu et des incréments EnKF.
3. **Innovations :** Pour `DA_nocdf` sur MAM 2018, la variance moyenne des innovations normalisées $d / \sqrt{HPH^T + R}$ s'établit à **1,2446**, traduisant une légère sous-estimation du spread d'erreur totale par rapport à la variance attendue théorique de 1,00.

---

## 6. Sommes de Contrôle MD5 des Fichiers et Scripts Produits

| Fichier Produit | Rôle | Somme de Contrôle MD5 |
|---|---|---|
| `paper1/scripts/step5_lot3_analyses.py` | Script | `e874108d4dd470c719fd003eaa5dae5c` |
| `paper1/scripts/step5_generate_report_night_5.py` | Script | `53c10611111e1c1960679e383cc86c8d` |
| `paper1/tables/nov_dec_2018_water_balance_gap.csv` | Table | `bee651688bbfbc0ba5f6c661475e6316` |
| `paper1/tables/nowilt_gap_monthly_distribution_2018.csv` | Table | `569acfb9105bbf1c1f5455ea86bd5771` |
| `paper1/tables/innovations_and_spread_by_month_and_texture.csv` | Table | `d8ea44e1f18d6b73edd8aa7900c0955c` |
| `paper1/tables/comparison_da_nocdf_vs_nostate_mam2018.csv` | Table | `0d3e80e35464b3da1447d93d472dfae0` |
| `paper1/tables/status_long_runs_step5.csv` | Table | `daa1ef518b43a228284cba566a3a1d06` |

---
*Fin du Rapport d'Étape 5.*

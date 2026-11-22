# Rapport d'Étape 3 — Diagnostic du Débit DA_nocdf (Lalla Chafia) et Corrections

**Date d'exécution :** 2026-11-22 13:36:03  
**Auteur :** Antigravity (mode autonome)  
**Branche Git :** `paper1-closure`  

---

## 1. Objectif de l'Étape 3

Constat établi au Lot 2 : à la station hydrométrique de **Lalla Chafia** (bassin amont non régulé du Bouregreg), la simulation d'assimilation sans correction de biais `DA_nocdf` produit un débit moyen annuel simulé de **35,90 m³/s** en 2018, contre **9,74 m³/s** observés (KGE = −1,795). En revanche, l'assimilation avec correction de biais CDF (`DA_cdf`) simule **15,81 m³/s** (KGE = −0,022) et le contrôle d'ensemble `ENS_OPL` simule **15,69 m³/s** (KGE = +0,014), restant proches de la dynamique observée.

L'objectif de cette étape est d'établir de manière strictement factuelle, chiffrée et sans conclusion subjective l'origine de cette anomalie de débit à travers :
1. L'analyse des séries journalières et mensuelles 2018 à Lalla Chafia et Sidi Jabeur ;
2. Le bilan hydrologique sur les bassins versants amonts HyMAP délimités par le réseau hydrographique D8 ;
3. Le contrôle du remapping de ruissellement (grille native 181×121 vers grille HyMAP 180×120) ;
4. L'impact du schéma de routage linéaire (`linres = 1` vs `linres = 0`) ;
5. La localisation spatiale des anomalies de ruissellement sous-surfacique ($Q_{sb}$) ;
6. Les corrections des rapports `REPORT_LOT2.md` et `REPORT_LOT1c.md` ;
7. L'indépendance méthodologique des produits d'évapotranspiration GLEAM v4.3a et WaPOR v3 vis-à-vis de SMAP.

---

## 2. Séries Journalières et Mensuelles 2018 (Lalla Chafia et Sidi Jabeur)

### a) Fichiers de données et figure de contrôle
- Table journalière complète (365 jours, 6 expériences + observations ABH) : `paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv`
- Figure de contrôle en échelle logarithmique : `paper1/figures/fig_control_daily_streamflow_log.png`

### b) Débits moyens mensuels 2018 (`monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv`)

| station | station_id | year_month | obs | OPL | OL_DAIC | ENS_OPL | DA_nocdf | DA_cdf | DA_nocdf_nowilt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | lalla_chafia | 2018-01 | 8.2803 | 3.7944 | 8.4382 | 10.9156 | 20.2279 | 9.5767 | 20.2279 |
| Sidi Jabeur | sidi_jabeur | 2018-01 | 15.7438 | 2.6076 | 5.0306 | 5.5379 | 7.8218 | 6.4467 | 7.8218 |
| Lalla Chafia | lalla_chafia | 2018-02 | 8.3560 | 2.9298 | 8.8075 | 11.3474 | 44.5782 | 12.7723 | 44.5782 |
| Sidi Jabeur | sidi_jabeur | 2018-02 | 15.3568 | 2.5563 | 4.8195 | 5.4839 | 19.5979 | 10.5238 | 19.5979 |
| Lalla Chafia | lalla_chafia | 2018-03 | 39.5676 | 10.5215 | 30.0290 | 41.3558 | 108.1117 | 34.0882 | 108.1118 |
| Sidi Jabeur | sidi_jabeur | 2018-03 | 32.4145 | 4.9181 | 8.1642 | 10.8439 | 39.9623 | 20.9029 | 39.9623 |
| Lalla Chafia | lalla_chafia | 2018-04 | 16.7903 | 16.6194 | 31.9098 | 36.6348 | 73.6072 | 35.8455 | 73.6008 |
| Sidi Jabeur | sidi_jabeur | 2018-04 | 19.4053 | 5.4250 | 9.5305 | 14.0593 | 40.6328 | 27.7494 | 40.6218 |
| Lalla Chafia | lalla_chafia | 2018-05 | 9.5635 | 11.1085 | 18.2621 | 20.4927 | 39.0091 | 21.6984 | 38.9607 |
| Sidi Jabeur | sidi_jabeur | 2018-05 | 9.8184 | 4.0876 | 6.9334 | 9.9652 | 24.1767 | 18.9691 | 24.1627 |
| Lalla Chafia | lalla_chafia | 2018-06 | 1.1969 | 7.9040 | 11.7383 | 12.8853 | 20.5499 | 13.7986 | 20.4162 |
| Sidi Jabeur | sidi_jabeur | 2018-06 | 0.5316 | 3.1334 | 5.2892 | 7.1868 | 14.1355 | 11.8941 | 14.1200 |
| Lalla Chafia | lalla_chafia | 2018-07 | 0.2356 | 6.6650 | 9.1679 | 9.7594 | 13.8111 | 10.0061 | 13.5686 |
| Sidi Jabeur | sidi_jabeur | 2018-07 | 0.1017 | 2.9996 | 4.7970 | 6.0691 | 10.3151 | 8.3169 | 10.3463 |
| Lalla Chafia | lalla_chafia | 2018-08 | 0.5758 | 6.1681 | 8.0087 | 8.3658 | 11.0243 | 8.6450 | 10.7797 |
| Sidi Jabeur | sidi_jabeur | 2018-08 | 0.0000 | 3.0782 | 4.6553 | 5.5878 | 8.6159 | 7.1968 | 8.6120 |
| Lalla Chafia | lalla_chafia | 2018-09 | 0.9180 | 6.8051 | 8.3327 | 8.6005 | 10.6669 | 8.6270 | 10.4784 |
| Sidi Jabeur | sidi_jabeur | 2018-09 | 4.8513 | 3.7995 | 5.3419 | 6.1400 | 8.6460 | 7.2325 | 8.7272 |
| Lalla Chafia | lalla_chafia | 2018-10 | 7.5050 | 10.1709 | 11.6444 | 11.9029 | 13.7891 | 11.7298 | 13.7617 |
| Sidi Jabeur | sidi_jabeur | 2018-10 | 14.2879 | 5.9804 | 7.7609 | 8.5409 | 11.0287 | 9.1199 | 11.0280 |
| Lalla Chafia | lalla_chafia | 2018-11 | 19.8993 | 8.8238 | 9.9867 | 10.2213 | 27.7638 | 11.9343 | 29.2737 |
| Sidi Jabeur | sidi_jabeur | 2018-11 | 16.8090 | 5.9171 | 7.3842 | 8.0096 | 15.1392 | 9.0967 | 14.9086 |
| Lalla Chafia | lalla_chafia | 2018-12 | 3.7635 | 3.9669 | 4.6201 | 5.4450 | 47.3108 | 10.7661 | 48.3396 |
| Sidi Jabeur | sidi_jabeur | 2018-12 | 1.5001 | 2.6192 | 3.4334 | 4.1769 | 25.2778 | 8.5338 | 24.9003 |

---

## 3. Bilan Hydrologique sur les Vrais Bassins Amonts HyMAP

### a) Délimitation amont par remontée topologique HyMAP D8
- **Algorithme :** Remontée récursive de la matrice de direction de drainage D8 (`HYMAP_flow_direction_x`, `HYMAP_flow_direction_y`) depuis les exutoires des stations dans `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc`.
- **Lalla Chafia (Bouregreg) :**
  - Maille exutoire : ligne 75, colonne 71 (grille 180×120).
  - Nombre de mailles amont D8 : **133 mailles** (grille 180×120).
  - Aire cumulée HyMAP D8 : **3 333,35 km²** (utilisée dans toutes les tables de calcul : `remap_runoff_check`, `water_balance_upstream_catchments`, `da_nocdf_annual_runoff`).
  - Comparaison ABH : 3 341,60 km² dans l'inventaire officiel (`table2_stations.csv`), soit un écart topologique de seulement −0,25 %.
  - **Clarification sur l'aire de 5 502 km² (189 mailles) :** cette valeur citée dans certains textes descriptifs correspondait à la délimitation globale du bassin du Bouregreg jusqu'à la retenue aval du barrage SMBA ou l'embouchure, et non au bassin amont spécifique contrôlé à la station hydrométrique de Lalla Chafia. La valeur rigoureuse et cohérente utilisée dans tous les calculs est 3 333,35 km².
- **Sidi Jabeur (Grou) :**
  - Maille exutoire : ligne 71, colonne 71 (grille 180×120).
  - Nombre de mailles amont : **66 mailles**.
  - Aire cumulée HyMAP : **3 130,55 km²** (contre 3 138,50 km² dans l'inventaire officiel des stations, écart = −0,25 %).

### b) Bilan mensuel 2018 sur le bassin amont (`water_balance_upstream_catchments_2018.csv`)

Extrait du bilan d'eau ($P$, $ET$, $Q_s$, $Q_{sb}$, Ruissellement total, $\Delta S$, Incréments totaux DA, Résidu $R$) :

| station | station_id | experiment | year_month | P_mm | ET_mm | Qs_mm | Qsb_mm | TotalRunoff_mm | Delta_S_mm | Incr_Layer1_mm | Incr_Layer2_mm | Incr_Layer3_mm | Incr_Layer4_mm | Incr_Total_mm | WaterBalance_Residual_mm | Delta_R_vs_OL_DAIC_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | b_l_chafia | OPL | 2018-01 | 101.8796 | 29.7646 | 2.0208 | 1.1405 | 3.1613 | 69.0775 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.1238 | -0.9404 |
| Sidi Jabeur | b_s_jabeur | OPL | 2018-01 | 60.6342 | 22.2239 | 1.1847 | 1.0957 | 2.2804 | 36.5726 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.4428 | -1.0559 |
| Lalla Chafia | b_l_chafia | OL_DAIC | 2018-01 | 101.8796 | 33.2635 | 3.2611 | 3.6449 | 6.9060 | 60.8936 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8166 | 0.0000 |
| Sidi Jabeur | b_s_jabeur | OL_DAIC | 2018-01 | 60.6342 | 23.5743 | 1.7774 | 2.5462 | 4.3236 | 32.1231 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.6131 | 0.0000 |
| Lalla Chafia | b_l_chafia | ENS_OPL | 2018-01 | 101.8796 | 36.5715 | 3.5333 | 5.5158 | 9.0491 | 62.5295 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -6.2705 | -7.0871 |
| Sidi Jabeur | b_s_jabeur | ENS_OPL | 2018-01 | 60.6342 | 28.4487 | 1.8500 | 2.9458 | 4.7957 | 32.3513 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -4.9616 | -5.5747 |
| Lalla Chafia | b_l_chafia | DA_nocdf | 2018-01 | 101.8796 | 41.6968 | 4.0145 | 13.5559 | 17.5704 | 122.8849 | 11.0380 | 12.4609 | 19.9714 | 18.7446 | 62.2149 | -18.0575 | -18.8741 |
| Sidi Jabeur | b_s_jabeur | DA_nocdf | 2018-01 | 60.6342 | 31.6785 | 1.9353 | 5.1484 | 7.0837 | 70.7046 | 8.6469 | 8.2150 | 16.8840 | 6.1924 | 39.9383 | -8.8943 | -9.5074 |
| Lalla Chafia | b_l_chafia | DA_cdf | 2018-01 | 101.8796 | 30.4322 | 3.2460 | 4.7459 | 7.9919 | 60.5451 | -0.2503 | -2.9806 | -5.8904 | -7.9557 | -17.0769 | -14.1664 | -14.9830 |
| Sidi Jabeur | b_s_jabeur | DA_cdf | 2018-01 | 60.6342 | 25.0223 | 1.7133 | 3.9065 | 5.6198 | 30.2177 | -1.1878 | -2.8488 | -6.8946 | -4.0895 | -15.0206 | -15.2462 | -15.8593 |
| Lalla Chafia | b_l_chafia | DA_nocdf_nowilt | 2018-01 | 101.8796 | 40.4989 | 4.0145 | 13.5559 | 17.5704 | 122.8849 | 11.0380 | 12.4609 | 19.9714 | 18.7446 | 62.2149 | -16.8596 | -17.6762 |
| Sidi Jabeur | b_s_jabeur | DA_nocdf_nowilt | 2018-01 | 60.6342 | 30.8752 | 1.9353 | 5.1484 | 7.0837 | 70.7046 | 8.6469 | 8.2150 | 16.8840 | 6.1924 | 39.9383 | -8.0910 | -8.7041 |
| Lalla Chafia | b_l_chafia | OPL | 2018-02 | 79.2278 | 38.6482 | 1.5935 | 1.0517 | 2.6452 | 37.7832 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1512 | -0.1108 |
| Sidi Jabeur | b_s_jabeur | OPL | 2018-02 | 73.1487 | 27.6011 | 1.4519 | 0.9976 | 2.4494 | 43.3052 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.2070 | -0.4161 |
| Lalla Chafia | b_l_chafia | OL_DAIC | 2018-02 | 79.2278 | 40.7229 | 2.9393 | 4.2490 | 7.1883 | 31.0546 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2620 | 0.0000 |
| Sidi Jabeur | b_s_jabeur | OL_DAIC | 2018-02 | 73.1487 | 29.5957 | 2.0838 | 2.1899 | 4.2738 | 39.0700 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2091 | 0.0000 |
| Lalla Chafia | b_l_chafia | ENS_OPL | 2018-02 | 79.2278 | 44.0195 | 3.2637 | 5.7832 | 9.0469 | 31.2344 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -5.0730 | -5.3350 |
| Sidi Jabeur | b_s_jabeur | ENS_OPL | 2018-02 | 73.1487 | 34.9138 | 2.2137 | 2.5826 | 4.7963 | 39.7095 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -6.2710 | -6.4801 |
| Lalla Chafia | b_l_chafia | DA_nocdf | 2018-02 | 79.2278 | 45.5114 | 6.3896 | 27.2427 | 33.6323 | 24.1119 | 0.7637 | 3.5394 | 3.3605 | 3.5823 | 11.2460 | -12.7818 | -13.0438 |
| Sidi Jabeur | b_s_jabeur | DA_nocdf | 2018-02 | 73.1487 | 36.4280 | 3.4357 | 12.5102 | 15.9459 | 53.1370 | -0.2444 | 3.5809 | 8.3264 | 6.4812 | 18.1441 | -14.2182 | -14.4273 |
| Lalla Chafia | b_l_chafia | DA_cdf | 2018-02 | 79.2278 | 38.0270 | 2.9281 | 7.0005 | 9.9286 | 49.4872 | 1.6791 | 1.5010 | 3.0471 | 0.9440 | 7.1712 | -11.0437 | -11.3057 |
| Sidi Jabeur | b_s_jabeur | DA_cdf | 2018-02 | 73.1487 | 32.2837 | 2.3512 | 6.3682 | 8.7194 | 55.7677 | 2.6500 | 1.7387 | 4.9781 | -2.5202 | 6.8467 | -16.7754 | -16.9845 |
| Lalla Chafia | b_l_chafia | DA_nocdf_nowilt | 2018-02 | 79.2278 | 45.5060 | 6.3897 | 27.2427 | 33.6323 | 24.1254 | 0.7655 | 3.5511 | 3.3968 | 3.5797 | 11.2931 | -12.7428 | -13.0048 |
| Sidi Jabeur | b_s_jabeur | DA_nocdf_nowilt | 2018-02 | 73.1487 | 36.4280 | 3.4357 | 12.5102 | 15.9459 | 53.1370 | -0.2444 | 3.5809 | 8.3264 | 6.4812 | 18.1441 | -14.2182 | -14.4273 |

*(Table complète de 144 enregistrements disponible dans `paper1/tables/water_balance_upstream_catchments_2018.csv`)*

### c) Ruissellement annuel DA_nocdf sur le bassin amont 2016–2020 (`da_nocdf_annual_runoff_catchment_2016_2020.csv`)

| station | station_id | year | n_days | area_km2 | Qs_mm | Qsb_mm | TotalRunoff_mm | TotalRunoff_hm3 | Q_mean_m3s_equivalent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | b_l_chafia | 2016 | 366 | 3333.3489 | 11.4406 | 36.1217 | 47.5623 | 158.5418 | 5.0136 |
| Sidi Jabeur | b_s_jabeur | 2016 | 366 | 3130.5541 | 8.6579 | 19.9755 | 28.6335 | 89.6386 | 2.8347 |
| Lalla Chafia | b_l_chafia | 2017 | 365 | 3333.3489 | 19.4923 | 127.3656 | 146.8579 | 489.5286 | 15.5229 |
| Sidi Jabeur | b_s_jabeur | 2017 | 365 | 3130.5541 | 11.8344 | 73.8941 | 85.7286 | 268.3779 | 8.5102 |
| Lalla Chafia | b_l_chafia | 2018 | 365 | 3333.3489 | 53.5019 | 286.8127 | 340.3146 | 1134.3872 | 35.9712 |
| Sidi Jabeur | b_s_jabeur | 2018 | 365 | 3130.5541 | 32.1961 | 157.8049 | 190.0009 | 594.8082 | 18.8612 |
| Lalla Chafia | b_l_chafia | 2019 | 365 | 3333.3489 | 13.6011 | 130.9348 | 144.5359 | 481.7886 | 15.2774 |
| Sidi Jabeur | b_s_jabeur | 2019 | 365 | 3130.5541 | 9.4687 | 74.6061 | 84.0749 | 263.2010 | 8.3460 |
| Lalla Chafia | b_l_chafia | 2020 | 366 | 3333.3489 | 12.8137 | 104.6413 | 117.4550 | 391.5184 | 12.3810 |
| Sidi Jabeur | b_s_jabeur | 2020 | 366 | 3130.5541 | 9.1486 | 53.0345 | 62.1831 | 194.6676 | 6.1560 |

On observe qu'en 2018, le ruissellement total de `DA_nocdf` sur le bassin de Lalla Chafia atteint **340,31 mm/an** (dont **286,81 mm/an de ruissellement sous-surfacique $Q_{sb}$**, soit 84,3 % du total), ce qui équivaut rigoureusement à un débit moyen de **35,97 m³/s**, concordant exactement avec le débit routé simule (**35,90 m³/s**).

---

## 4. Contrôle du Remapping de Ruissellement (Lalla Chafia, 2018)

Comparaison du ruissellement total annuel ($Q_s + Q_{sb}$) calculé directement sur la grille source native de Noah-MP (181×121) contre les champs remappés vers la grille de routage HyMAP (180×120) sur le bassin versant de Lalla Chafia :

| experiment | station | catchment_area_km2 | Qs_native_mm | Qsb_native_mm | TotalRunoff_native_mm | Qs_remapped_mm | Qsb_remapped_mm | TotalRunoff_remapped_mm | difference_mm | difference_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DA_nocdf | Lalla Chafia | 3333.3489 | 49.2833 | 277.3164 | 326.5997 | 53.5019 | 286.8127 | 340.3146 | 13.7149 | 4.1993 |
| ENS_OPL | Lalla Chafia | 3333.3489 | 37.8965 | 116.9488 | 154.8452 | 35.0758 | 113.1802 | 148.2560 | -6.5893 | -4.2554 |

- Pour `DA_nocdf`, le remapping introduit un écart de **+13,71 mm/an** (+4,20 %).
- Pour `ENS_OPL`, le remapping introduit un écart de **−6,59 mm/an** (−4,26 %).
- L'écart de remapping (+4,2 %) est d'un ordre de grandeur inférieur à la surestimation de débit constatée (+268 % entre 9,74 et 35,90 m³/s).

---

## 5. Routage Historique : linres = 1 vs linres = 0 (Lalla Chafia, 2018)

Comparaison des débits simulés par HyMAP-2 en configuration historique (`linres = 1`, réservoir linéaire activé, restart spinup c2) contre la configuration de référence du Lot 2 (`linres = 0`, réservoir linéaire désactivé, coldstart) :

| station | year | n_days | mean_q_linres0_m3s | mean_q_linres1_m3s | diff_m3s | diff_pct |
| --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | 2018 | 365 | 35.8291 | 35.6278 | -0.2013 | -0.5600 |

- Fichier journalier complet : `paper1/tables/lalla_chafia_streamflow_linres1_vs_linres0_2018.csv`
- Le débit annuel moyen en `linres = 1` est de **35,6278 m³/s**, contre **35,8291 m³/s** en `linres = 0` (écart de **−0,2013 m³/s**, soit **−0,56 %**).
- Cela démontre factuellement que l'activation ou la désactivation du réservoir linéaire d'HyMAP n'a qu'un impact marginal (< 0,6 %) sur le volume annuel acheminé à l'exutoire.

---

## 6. Analyse Spatiale de l'Anomalie de Ruissellement Sous-Surfacique (Qsb)

### a) Cartographie
- Figure produite : `paper1/figures/fig_map_qsb_difference_da_minus_ens.png`
  - Panneau supérieur : Différence de $Q_{sb}$ annuel 2018 (`DA_nocdf` − `ENS_OPL`) en mm/an, avec contours des bassins versants amonts de Lalla Chafia et Sidi Jabeur.
  - Panneau inférieur : Distribution des classes de texture de sol dominantes sur le domaine.

### b) Top 20 des mailles présentant le plus fort excédent de Qsb (`top20_cells_qsb_difference.csv`)

| rank | row_180 | col_180 | lon | lat | texture_id | texture_name | qsb_da_nocdf_mm | qsb_ens_opl_mm | diff_qsb_mm | inside_lalla_chafia | inside_sidi_jabeur | inside_bouregreg | inside_sebou |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 105 | 87 | -5.6250 | 35.2750 | 6 | Loam | 805.2542 | 363.7557 | 441.4985 | False | False | False | False |
| 2 | 106 | 86 | -5.6750 | 35.3250 | 6 | Loam | 842.3484 | 404.4212 | 437.9272 | False | False | False | False |
| 3 | 105 | 86 | -5.6750 | 35.2750 | 6 | Loam | 819.8523 | 384.2913 | 435.5610 | False | False | False | False |
| 4 | 100 | 87 | -5.6250 | 35.0250 | 6 | Loam | 830.8545 | 408.3979 | 422.4566 | False | False | False | False |
| 5 | 106 | 85 | -5.7250 | 35.3250 | 6 | Loam | 795.3449 | 376.4062 | 418.9387 | False | False | False | False |
| 6 | 106 | 87 | -5.6250 | 35.3250 | 6 | Loam | 776.4929 | 363.9744 | 412.5185 | False | False | False | False |
| 7 | 104 | 86 | -5.6750 | 35.2250 | 6 | Loam | 740.4784 | 329.8923 | 410.5861 | False | False | False | False |
| 8 | 96 | 96 | -5.1750 | 34.8250 | 6 | Loam | 797.3777 | 386.8273 | 410.5504 | False | False | False | True |
| 9 | 97 | 95 | -5.2250 | 34.8750 | 6 | Loam | 826.3832 | 417.9026 | 408.4807 | False | False | False | True |
| 10 | 101 | 87 | -5.6250 | 35.0750 | 6 | Loam | 798.4355 | 390.2603 | 408.1752 | False | False | False | False |
| 11 | 96 | 95 | -5.2250 | 34.8250 | 6 | Loam | 840.6846 | 433.9060 | 406.7787 | False | False | False | True |
| 12 | 97 | 96 | -5.1750 | 34.8750 | 6 | Loam | 801.7792 | 399.1389 | 402.6403 | False | False | False | True |
| 13 | 102 | 89 | -5.5250 | 35.1250 | 6 | Loam | 780.0029 | 382.9843 | 397.0186 | False | False | False | False |
| 14 | 95 | 87 | -5.6250 | 34.7750 | 6 | Loam | 745.1683 | 353.2695 | 391.8988 | False | False | False | False |
| 15 | 96 | 87 | -5.6250 | 34.8250 | 6 | Loam | 705.7672 | 316.0526 | 389.7147 | False | False | False | False |
| 16 | 103 | 89 | -5.5250 | 35.1750 | 6 | Loam | 812.9235 | 423.5051 | 389.4184 | False | False | False | False |
| 17 | 96 | 97 | -5.1250 | 34.8250 | 6 | Loam | 779.7658 | 394.3508 | 385.4151 | False | False | False | True |
| 18 | 106 | 91 | -5.4250 | 35.3250 | 6 | Loam | 724.3924 | 339.9333 | 384.4590 | False | False | False | False |
| 19 | 95 | 98 | -5.0750 | 34.7750 | 6 | Loam | 770.6555 | 386.2187 | 384.4368 | False | False | False | True |
| 20 | 95 | 97 | -5.1250 | 34.7750 | 6 | Loam | 773.5102 | 389.4517 | 384.0584 | False | False | False | True |

Sur les 20 mailles les plus émettrices d'écart $Q_{sb}$ sur le domaine (`top20_cells_qsb_difference.csv`) :
- **Texture de sol :** Toutes les 20 mailles ont pour texture **Loam** (classe 6).
- **Écart maximal :** +441,50 mm/an (maille rank 1 à lon −5,625°, lat 35,275°), et +384,06 mm/an pour le rank 20.
- **Absence dans Lalla Chafia :** **Aucune maille** n'est située à l'intérieur du bassin versant amont de Lalla Chafia (`inside_lalla_chafia = False` pour les 20 mailles) ni de Sidi Jabeur (`inside_sidi_jabeur = False`).
- **Localisation réelle :** Longitude −5,7° à −5,1°, Latitude 34,8° à 35,3° (région Rif / Loukkos, dont 7 mailles situées dans le bassin du Sebou : ranks 8, 9, 11, 12, 17, 19, 20).

---

## 7. Corrections Apportées aux Rapports Précédents

### a) Corrections de `paper1/REPORT_LOT2.md`
1. **Taille de l'ensemble ENS_OPL :** Confirmation que `ENS_OPL` comprend **20 membres** (et non 12). Toutes les tables et mentions dans le texte ont été harmonisées via le script de régénération `paper1/scripts/generate_report_lot2.py`.
2. **Nomenclature exacte des simulations du Lot 1 :**
   - `DA_nocdf_nostate_2018MAM` (Job Slurm 8360362, diagnostic blocage état MAM 2018) ;
   - `DA_nocdf_diag_2018ND` (Job Slurm 8360363, diagnostic incréments ND 2018) ;
   - `DA_nocdf_diag_15min_2018Nov` (diagnostic pas fin 15 min novembre 2018).
3. **Fichier de raccordement du 31-05-2018 :**
   - Le flux journalier du **30 mai 2018** (`LIS_HIST_201805310000.d01.nc`) a été dupliqué pour combler l'absence temporaire du fichier du 31 mai dans l'arborescence standard lors du raccordement.
   - Les audits antérieurs (`smap-xai-audit`) présentaient exactement le même trou lors de la lecture des sorties standard.
   - L'effet calculé sur la moyenne annuelle domaine est strictement de :
     - $ET$ : < 0,11 mm (−0,094 mm pour ENS_OPL, −0,105 mm pour DA_nowilt) ;
     - $Q_s$ : < 0,012 mm (+0,011 mm pour ENS_OPL, +0,010 mm pour DA_nowilt) ;
     - $Q_{sb}$ : < 0,001 mm (+0,0007 mm pour ENS_OPL, +0,0010 mm pour DA_nowilt).
4. **Configurations de routage DA basculées en coldstart :**
   - Le passage en coldstart (`Routing restart mode: 0` au 01-01-2016) pour `DA_nocdf_linres0_2016_2020` et `DA_cdf_linres0_2016_2020` est strictement conforme à la configuration de référence `OPL_linres0_2016_2020` (également en coldstart au 01-01-2016).
   - Aucune sortie préexistante n'a été altérée ni écrasée (création de répertoires de sortie vierges dédiés).

### c) Diagnostic et Statut de DA_nocdf_nostate_2018MAM
- **Constat log et sorties :** `DA_nocdf_nostate_2018MAM` (Job Slurm 8360362) a réalisé **0 instance d'assimilation** (aucune analyse EnKF effectuée, aucun fichier d'incrément généré).
- **Cause dans la configuration :** Dans `experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/config/lis_DA_nocdf_nostate_2018MAM.config`, la ligne de configuration porte `Number of data assimilation instances: 0`. Dans LIS, cette valeur désactive l'ensemble du sous-système d'assimilation, faisant tourner le run en simple ensemble open-loop.
- **Comparaison avec DA_corr_2018 :** Dans `DA_corr_2018/config/lis_DA_corr_2018.config`, `Number of data assimilation instances: 1` est actif, avec `State perturbation algorithm: 'none'`. Cette configuration active bien l'algorithme EnKF et assimile les observations SMAP à chaque passage satellite, produisant les incréments attendus.
- **Statut formel :** `DA_nocdf_nostate_2018MAM` est marqué comme **NON VALIDE pour l'évaluation de l'assimilation**.

### b) Correction de `paper1/REPORT_LOT1c.md`
- Le membre 20 de l'ensemble n'est pas `OL_DAIC`. Il s'agit du **membre non perturbé de l'ensemble**, dont les conditions initiales diffèrent de celles d'`OL_DAIC`. Le script `paper1/scripts/generate_report_lot1c.py` a été corrigé et `paper1/REPORT_LOT1c.md` a été régénéré.

---

## 8. Indépendance Méthodologique des Produits d'Évapotranspiration vis-à-vis de SMAP

### a) GLEAM v4.3a
- **Référence bibliographique officielle (attributs NetCDF) :**
  > Miralles, D.G. et al. 2025: Global land evaporation and soil moisture dataset at 0.1° resolution from 1980 to near present, *Scientific Data*, 12, 416, doi: [10.1038/s41597-025-04610-y](https://doi.org/10.1038/s41597-025-04610-y).
- **Utilisation d'humidité du sol micro-ondes :**
  - GLEAM v4 assimile explicitement l'humidité de surface micro-ondes par *nudging newtonien* dans son modèle de bilan hydrique du sol pour contraindre l'évaporation et le stress hydrique de la végétation.
  - Le produit assimilé est le jeu multi-satellites **ESA CCI Soil Moisture** (COMBINED / ACTIVE / PASSIVE). Depuis avril 2015, l'archive ESA CCI intègre directement les radiomètres bande L de **SMAP**, ainsi que SMOS et ASCAT.
  - De plus, GLEAM v4 utilise la profondeur optique de la végétation micro-ondes (VODCA L), issue de SMAP et SMOS.
- **Statut :** **Non indépendant de SMAP** (assimilation indirecte de radiométrie micro-ondes incluant SMAP).

### b) WaPOR v3 (FAO / eLEAF)
- **Référence méthodologique officielle :**
  > FAO (2020, 2023): WaPOR Database Methodology: Version 2 & 3. Food and Agriculture Organization of the United Nations, Rome.
- **Utilisation d'humidité du sol micro-ondes :**
  - L'algorithme ETLook de WaPOR repose sur un bilan d'énergie à deux couches contraint par la température de surface thermique infrarouge (**LST** MODIS et VIIRS), les indices spectraux optiques (**NDVI**, albédo Sentinel-2/PROBA-V) et les forçages météorologiques **ERA5**.
  - WaPOR v3 **n'ingère ni n'assimile aucune observation d'humidité du sol issue des micro-ondes** (ni SMAP, ni SMOS, ni ESA CCI).
- **Statut :** **Strictement indépendant de SMAP**.

---

## 9. Sommes de Contrôle MD5 des Fichiers et Scripts Produits

| Fichier Produit | Rôle | Somme de Contrôle MD5 |
|---|---|---|
| `paper1/scripts/c1_verify_lalla_chafia_streamflow.py` | Script | `4b4608c8413083488303ce0cde03012e` |
| `paper1/scripts/step3_generate_report_night_3.py` | Script | `bc30e2d8621b993937fa86c5762f6f77` |
| `paper1/scripts/generate_report_lot2.py` | Script | `40805abe5a46d044b330b375bc5c9677` |
| `paper1/scripts/generate_report_lot1c.py` | Script | `2f61292aeeca0d47131112012843a9cd` |
| `paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv` | Table | `8e2fec42bbd8c38cf3a56d3e275733fd` |
| `paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv` | Table | `bef059a5dc21d5bfcfc1741c18d3f0b6` |
| `paper1/tables/water_balance_upstream_catchments_2018.csv` | Table | `558aee41de7474a4dea0e198ccf69a22` |
| `paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv` | Table | `4c3e684a0895db46f8dbf46ce99aa7d0` |
| `paper1/tables/remap_runoff_check_lalla_chafia_2018.csv` | Table | `81f2beb44fddfd40ec4666adab509de0` |
| `paper1/tables/lalla_chafia_streamflow_linres1_vs_linres0_2018.csv` | Table | `844710518cfd1d3bbe9ac31aa213a817` |
| `paper1/tables/lalla_chafia_linres_comparison_summary_2018.csv` | Table | `8100ea182409ef0fa1089ff8a4f176f2` |
| `paper1/tables/top20_cells_qsb_difference.csv` | Table | `6d13e7b45c514f07415bf973cd73a058` |
| `paper1/figures/fig_control_daily_streamflow_log.png` | Figure | `45343a5268a6b32bba291a93b9e8108e` |
| `paper1/figures/fig_map_qsb_difference_da_minus_ens.png` | Figure | `c5a8c9aca1946c02609d527add2bd4d9` |
| `paper1/REPORT_LOT2.md` | Rapport | `41acda5d094542ff39ba070695911f78` |
| `paper1/REPORT_LOT1c.md` | Rapport | `3ba89bf6e42fcd74a2fdfc15bc008737` |

---
*Fin du Rapport d'Étape 3.*

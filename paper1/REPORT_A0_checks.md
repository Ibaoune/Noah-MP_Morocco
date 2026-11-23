# Rapport Étape A0 — Vérifications et Gel des Comparaisons

> **Statut :** Gel des comparaisons validé. Aucun run nouveau n'a été lancé sur la production.
> Tous les chiffres ci-dessous sont générés automatiquement par script à partir des tables CSV de référence.

## 1. Inventaire SMAP 2018 (INVENTORY.md)

La mention de parité stricte a été remplacée dans `paper1/INVENTORY.md` par les chiffres exacts issus de `paper1/tables/smap_obs_days_monthly_by_basin_2018.csv`.

| Entité / Bassin | Jours DA_nocdf | Jours DA_corr | Écart jours | Total Obs DA_nocdf | Total Obs DA_corr | Écart total obs | Écart (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | 220 j | 220 j | +0 j | 30 168 | 36 274 | +6 106 | +20.2 % |
| Sidi Jabeur | 217 j | 220 j | +3 j | 27 986 | 34 995 | +7 009 | +25.0 % |
| Sebou amont | 260 j | 260 j | +0 j | 33 175 | 37 570 | +4 395 | +13.2 % |
| Domaine complet | 357 j | 357 j | +0 j | 1 611 015 | 2 806 399 | +1 195 384 | +74.2 % |

### Causes confirmées par les configurations et les logs (sans spéculation) :
1. **Perturbation d'état :**
   - `DA_nocdf` : `State perturbation algorithm: "GMAO scheme"` avec `noahmp_sm_pertattribs.txt` (perturbation d'état active).
   - `DA_corr` : `State perturbation algorithm: "none"` (aucune perturbation d'état).
2. **Binaire exécutable utilisé :**
   - `DA_nocdf` : `./src/lisf/lis/LIS` (troncature LIS standard après mise à jour).
   - `DA_corr` : `./src/lisf_corr/lis/LIS` (mise à jour physique continue sans troncature).
3. **Absence de trace détaillée :** Les logs LIS de production ne tracent pas le décompte par motif de rejet EnKF ; aucune autre cause ne peut être affirmée.

## 2. Vérification des Trois Tables

### a) Table `paper1/figures/fig_02_data.csv` (Fractions de rejet par flétrissement)

**Explication chiffrée de l'écart (en une ligne) :**
> Le taux de 44,7 % (loam JJA) dans `fig_02_data.csv` provenait de l'évaluation erronée de l'observation SMAP brute (`rec1 < smcwlt + 0,02`) au lieu de l'observation rescalée CDF ; or en DA-CDF, LIS applique le test de flétrissement sur l'observation rescalée sur la climatologie Noah-MP, dont le taux de rejet réel n'est que de **4,0 % sur le domaine en JJA** (**2,5 % en MAM**, **3,1 % annuel**).

Tableau actuel `fig_02_data.csv` par texture :

| soil_id | texture | n_pixels | clay_fraction_pct | smcwlt | nocdf_mam_pct | nocdf_jja_pct | nocdf_ann_pct | cdf_mam_pct | cdf_jja_pct | cdf_ann_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sand | 539 | 3.00 | 0.01 | 6.90 | 0.00 | 12.90 | 5.80 | 0.00 | 9.40 |
| 3 | Sandy Loam | 748 | 10.00 | 0.05 | 33.00 | 41.90 | 30.00 | 0.70 | 31.60 | 9.50 |
| 4 | Silt Loam | 56 | 13.00 | 0.08 | 77.60 | 100.00 | 67.10 | 2.00 | 80.40 | 29.50 |
| 6 | Loam | 12047 | 19.00 | 0.07 | 45.60 | 46.40 | 40.50 | 22.10 | 44.70 | 24.40 |
| 7 | Sandy Clay Loam | 723 | 27.00 | 0.07 | 14.60 | 36.40 | 16.40 | 1.90 | 32.10 | 9.00 |
| 9 | Clay Loam | 1305 | 34.00 | 0.10 | 46.60 | 75.80 | 49.90 | 1.30 | 25.80 | 8.20 |
| 12 | Clay | 612 | 58.00 | 0.14 | 43.20 | 73.40 | 45.60 | 4.90 | 12.20 | 6.70 |

- **Taux domaine calculés (2016–2020) :**
  - **DA-NoCDF :** MAM = **50,91 %**, JJA = **54,87 %**, Annuel = **47,64 %**.
  - **DA-CDF (observation rescalée) :** MAM = **2,5 %**, JJA = **4,0 %**, Annuel = **3,1 %**.

### b) Table `paper1/tables/e5_2017_by_texture.csv` (Bilan ET 2017 DA_nocdf)

**Explication chiffrée de l'écart et correction :**
> Le script `step7_wilt_filter_2017.py` omettait le fichier de clôture mensuel `SURFACEMODEL/2017{m+1:02d}/LIS_HIST_2017{m+1:02d}010000.d01.nc` (353 jours pris en compte au lieu de 365, même omission que step6) ; après correction et régénération complète des 365 jours, l'ET domaine de DA_nocdf est exactement de **205,80 mm** (conforme au bilan corrigé `water_balance_2017_annual.csv`).

Tableau régénéré `e5_2017_by_texture.csv` :

| period | texture_id | texture_name | n_pixels | n_obs_nocdf | n_obs_nowilt | n_obs_rejected | rejection_fraction_pct | ET_nocdf_mm | ET_nowilt_mm | Delta_ET_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-01 | 0 | Domain_All | 16030 | 113873 | 170684 | 56811 | 33.28 | N/A | N/A | N/A |
| 2017-01 | 1 | Sand | 539 | 4961 | 8191 | 3230 | 39.43 | N/A | N/A | N/A |
| 2017-01 | 3 | Sandy Loam | 748 | 4140 | 4552 | 412 | 9.05 | N/A | N/A | N/A |
| 2017-01 | 4 | Silt Loam | 56 | 951 | 1056 | 105 | 9.94 | N/A | N/A | N/A |
| 2017-01 | 6 | Loam | 12047 | 73662 | 121072 | 47410 | 39.16 | N/A | N/A | N/A |
| 2017-01 | 7 | Sandy Clay Loam | 723 | 10062 | 10239 | 177 | 1.73 | N/A | N/A | N/A |
| 2017-01 | 9 | Clay Loam | 1305 | 12863 | 17259 | 4396 | 25.47 | N/A | N/A | N/A |
| 2017-01 | 12 | Clay | 612 | 7234 | 8315 | 1081 | 13.00 | N/A | N/A | N/A |
| 2017-02 | 0 | Domain_All | 16030 | 124169 | 210153 | 85984 | 40.91 | N/A | N/A | N/A |
| 2017-02 | 1 | Sand | 539 | 8079 | 10847 | 2768 | 25.52 | N/A | N/A | N/A |
| 2017-02 | 3 | Sandy Loam | 748 | 3175 | 6501 | 3326 | 51.16 | N/A | N/A | N/A |
| 2017-02 | 4 | Silt Loam | 56 | 973 | 975 | 2 | 0.21 | N/A | N/A | N/A |
| 2017-02 | 6 | Loam | 12047 | 79370 | 156121 | 76751 | 49.16 | N/A | N/A | N/A |
| 2017-02 | 7 | Sandy Clay Loam | 723 | 10206 | 10260 | 54 | 0.53 | N/A | N/A | N/A |
| 2017-02 | 9 | Clay Loam | 1305 | 14775 | 17582 | 2807 | 15.97 | N/A | N/A | N/A |
| 2017-02 | 12 | Clay | 612 | 7591 | 7867 | 276 | 3.51 | N/A | N/A | N/A |
| 2017-03 | 0 | Domain_All | 16030 | 121531 | 252222 | 130691 | 51.82 | N/A | N/A | N/A |
| 2017-03 | 1 | Sand | 539 | 9969 | 11991 | 2022 | 16.86 | N/A | N/A | N/A |
| 2017-03 | 3 | Sandy Loam | 748 | 3004 | 7685 | 4681 | 60.91 | N/A | N/A | N/A |
| 2017-03 | 4 | Silt Loam | 56 | 361 | 1064 | 703 | 66.07 | N/A | N/A | N/A |
| 2017-03 | 6 | Loam | 12047 | 80149 | 189892 | 109743 | 57.79 | N/A | N/A | N/A |
| 2017-03 | 7 | Sandy Clay Loam | 723 | 12028 | 12770 | 742 | 5.81 | N/A | N/A | N/A |
| 2017-03 | 9 | Clay Loam | 1305 | 10381 | 20092 | 9711 | 48.33 | N/A | N/A | N/A |
| 2017-03 | 12 | Clay | 612 | 5639 | 8728 | 3089 | 35.39 | N/A | N/A | N/A |
| 2017-04 | 0 | Domain_All | 16030 | 107444 | 263950 | 156506 | 59.29 | N/A | N/A | N/A |
| 2017-04 | 1 | Sand | 539 | 11348 | 11825 | 477 | 4.03 | N/A | N/A | N/A |
| 2017-04 | 3 | Sandy Loam | 748 | 2339 | 7139 | 4800 | 67.24 | N/A | N/A | N/A |
| 2017-04 | 4 | Silt Loam | 56 | 1 | 1064 | 1063 | 99.91 | N/A | N/A | N/A |
| 2017-04 | 6 | Loam | 12047 | 78223 | 201872 | 123649 | 61.25 | N/A | N/A | N/A |
| 2017-04 | 7 | Sandy Clay Loam | 723 | 10000 | 12880 | 2880 | 22.36 | N/A | N/A | N/A |
| 2017-04 | 9 | Clay Loam | 1305 | 4402 | 20459 | 16057 | 78.48 | N/A | N/A | N/A |
| 2017-04 | 12 | Clay | 612 | 1131 | 8711 | 7580 | 87.02 | N/A | N/A | N/A |
| 2017-05 | 0 | Domain_All | 16030 | 98727 | 261859 | 163132 | 62.30 | N/A | N/A | N/A |
| 2017-05 | 1 | Sand | 539 | 11568 | 11568 | 0 | 0.00 | N/A | N/A | N/A |
| 2017-05 | 3 | Sandy Loam | 748 | 1413 | 7491 | 6078 | 81.14 | N/A | N/A | N/A |
| 2017-05 | 4 | Silt Loam | 56 | 7 | 1003 | 996 | 99.30 | N/A | N/A | N/A |
| 2017-05 | 6 | Loam | 12047 | 74209 | 202262 | 128053 | 63.31 | N/A | N/A | N/A |
| 2017-05 | 7 | Sandy Clay Loam | 723 | 8084 | 12083 | 3999 | 33.10 | N/A | N/A | N/A |
| 2017-05 | 9 | Clay Loam | 1305 | 2248 | 19569 | 17321 | 88.51 | N/A | N/A | N/A |
| 2017-05 | 12 | Clay | 612 | 1198 | 7883 | 6685 | 84.80 | N/A | N/A | N/A |
| 2017-06 | 0 | Domain_All | 16030 | 112628 | 264530 | 151902 | 57.42 | N/A | N/A | N/A |
| 2017-06 | 1 | Sand | 539 | 11206 | 11206 | 0 | 0.00 | N/A | N/A | N/A |
| 2017-06 | 3 | Sandy Loam | 748 | 1745 | 7476 | 5731 | 76.66 | N/A | N/A | N/A |
| 2017-06 | 4 | Silt Loam | 56 | 0 | 1055 | 1055 | 100.00 | N/A | N/A | N/A |
| 2017-06 | 6 | Loam | 12047 | 90536 | 204173 | 113637 | 55.66 | N/A | N/A | N/A |
| 2017-06 | 7 | Sandy Clay Loam | 723 | 7765 | 12450 | 4685 | 37.63 | N/A | N/A | N/A |
| 2017-06 | 9 | Clay Loam | 1305 | 1273 | 20117 | 18844 | 93.67 | N/A | N/A | N/A |
| 2017-06 | 12 | Clay | 612 | 103 | 8053 | 7950 | 98.72 | N/A | N/A | N/A |
| 2017-07 | 0 | Domain_All | 16030 | 98402 | 269517 | 171115 | 63.49 | N/A | N/A | N/A |
| 2017-07 | 1 | Sand | 539 | 11577 | 11577 | 0 | 0.00 | N/A | N/A | N/A |
| 2017-07 | 3 | Sandy Loam | 748 | 852 | 7613 | 6761 | 88.81 | N/A | N/A | N/A |
| 2017-07 | 4 | Silt Loam | 56 | 2 | 1097 | 1095 | 99.82 | N/A | N/A | N/A |
| 2017-07 | 6 | Loam | 12047 | 78540 | 208030 | 129490 | 62.25 | N/A | N/A | N/A |
| 2017-07 | 7 | Sandy Clay Loam | 723 | 6610 | 12772 | 6162 | 48.25 | N/A | N/A | N/A |
| 2017-07 | 9 | Clay Loam | 1305 | 793 | 20371 | 19578 | 96.11 | N/A | N/A | N/A |
| 2017-07 | 12 | Clay | 612 | 28 | 8057 | 8029 | 99.65 | N/A | N/A | N/A |
| 2017-08 | 0 | Domain_All | 16030 | 128170 | 260764 | 132594 | 50.85 | N/A | N/A | N/A |
| 2017-08 | 1 | Sand | 539 | 11679 | 11679 | 0 | 0.00 | N/A | N/A | N/A |
| 2017-08 | 3 | Sandy Loam | 748 | 2548 | 7818 | 5270 | 67.41 | N/A | N/A | N/A |
| 2017-08 | 4 | Silt Loam | 56 | 0 | 981 | 981 | 100.00 | N/A | N/A | N/A |
| 2017-08 | 6 | Loam | 12047 | 101864 | 200469 | 98605 | 49.19 | N/A | N/A | N/A |
| 2017-08 | 7 | Sandy Clay Loam | 723 | 9246 | 12137 | 2891 | 23.82 | N/A | N/A | N/A |
| 2017-08 | 9 | Clay Loam | 1305 | 2453 | 19693 | 17240 | 87.54 | N/A | N/A | N/A |
| 2017-08 | 12 | Clay | 612 | 380 | 7987 | 7607 | 95.24 | N/A | N/A | N/A |
| 2017-09 | 0 | Domain_All | 16030 | 107955 | 258288 | 150333 | 58.20 | N/A | N/A | N/A |
| 2017-09 | 1 | Sand | 539 | 11257 | 11310 | 53 | 0.47 | N/A | N/A | N/A |
| 2017-09 | 3 | Sandy Loam | 748 | 1237 | 7499 | 6262 | 83.50 | N/A | N/A | N/A |
| 2017-09 | 4 | Silt Loam | 56 | 0 | 1049 | 1049 | 100.00 | N/A | N/A | N/A |
| 2017-09 | 6 | Loam | 12047 | 84984 | 197601 | 112617 | 56.99 | N/A | N/A | N/A |
| 2017-09 | 7 | Sandy Clay Loam | 723 | 8985 | 12627 | 3642 | 28.84 | N/A | N/A | N/A |
| 2017-09 | 9 | Clay Loam | 1305 | 1332 | 20106 | 18774 | 93.38 | N/A | N/A | N/A |
| 2017-09 | 12 | Clay | 612 | 160 | 8096 | 7936 | 98.02 | N/A | N/A | N/A |
| 2017-10 | 0 | Domain_All | 16030 | 136116 | 258897 | 122781 | 47.42 | N/A | N/A | N/A |
| 2017-10 | 1 | Sand | 539 | 9075 | 11642 | 2567 | 22.05 | N/A | N/A | N/A |
| 2017-10 | 3 | Sandy Loam | 748 | 2594 | 7724 | 5130 | 66.42 | N/A | N/A | N/A |
| 2017-10 | 4 | Silt Loam | 56 | 93 | 1000 | 907 | 90.70 | N/A | N/A | N/A |
| 2017-10 | 6 | Loam | 12047 | 108434 | 199196 | 90762 | 45.56 | N/A | N/A | N/A |
| 2017-10 | 7 | Sandy Clay Loam | 723 | 10793 | 12077 | 1284 | 10.63 | N/A | N/A | N/A |
| 2017-10 | 9 | Clay Loam | 1305 | 3698 | 19538 | 15840 | 81.07 | N/A | N/A | N/A |
| 2017-10 | 12 | Clay | 612 | 1429 | 7720 | 6291 | 81.49 | N/A | N/A | N/A |
| 2017-11 | 0 | Domain_All | 16030 | 97580 | 241737 | 144157 | 59.63 | N/A | N/A | N/A |
| 2017-11 | 1 | Sand | 539 | 5627 | 9626 | 3999 | 41.54 | N/A | N/A | N/A |
| 2017-11 | 3 | Sandy Loam | 748 | 1740 | 6733 | 4993 | 74.16 | N/A | N/A | N/A |
| 2017-11 | 4 | Silt Loam | 56 | 104 | 1039 | 935 | 89.99 | N/A | N/A | N/A |
| 2017-11 | 6 | Loam | 12047 | 76965 | 184941 | 107976 | 58.38 | N/A | N/A | N/A |
| 2017-11 | 7 | Sandy Clay Loam | 723 | 9710 | 12128 | 2418 | 19.94 | N/A | N/A | N/A |
| 2017-11 | 9 | Clay Loam | 1305 | 1966 | 19197 | 17231 | 89.76 | N/A | N/A | N/A |
| 2017-11 | 12 | Clay | 612 | 1468 | 8073 | 6605 | 81.82 | N/A | N/A | N/A |
| 2017-12 | 0 | Domain_All | 16030 | 128671 | 182822 | 54151 | 29.62 | N/A | N/A | N/A |
| 2017-12 | 1 | Sand | 539 | 4321 | 7410 | 3089 | 41.69 | N/A | N/A | N/A |
| 2017-12 | 3 | Sandy Loam | 748 | 3919 | 5354 | 1435 | 26.80 | N/A | N/A | N/A |
| 2017-12 | 4 | Silt Loam | 56 | 966 | 1007 | 41 | 4.07 | N/A | N/A | N/A |
| 2017-12 | 6 | Loam | 12047 | 87899 | 135104 | 47205 | 34.94 | N/A | N/A | N/A |
| 2017-12 | 7 | Sandy Clay Loam | 723 | 9914 | 9963 | 49 | 0.49 | N/A | N/A | N/A |
| 2017-12 | 9 | Clay Loam | 1305 | 15244 | 16682 | 1438 | 8.62 | N/A | N/A | N/A |
| 2017-12 | 12 | Clay | 612 | 6408 | 7302 | 894 | 12.24 | N/A | N/A | N/A |
| MAM_2017 | 0 | Domain_All | 16030 | 327702 | 778031 | 450329 | 57.88 | 73.27 | 63.88 | -9.39 |
| MAM_2017 | 1 | Sand | 539 | 32885 | 35384 | 2499 | 7.06 | 14.93 | 14.81 | -0.12 |
| MAM_2017 | 3 | Sandy Loam | 748 | 6756 | 22315 | 15559 | 69.72 | 96.68 | 90.85 | -5.83 |
| MAM_2017 | 4 | Silt Loam | 56 | 369 | 3131 | 2762 | 88.21 | 47.81 | 32.80 | -15.01 |
| MAM_2017 | 6 | Loam | 12047 | 232581 | 594026 | 361445 | 60.85 | 60.17 | 53.32 | -6.84 |
| MAM_2017 | 7 | Sandy Clay Loam | 723 | 30112 | 37733 | 7621 | 20.20 | 135.89 | 132.78 | -3.12 |
| MAM_2017 | 9 | Clay Loam | 1305 | 17031 | 60120 | 43089 | 71.67 | 115.65 | 88.92 | -26.73 |
| MAM_2017 | 12 | Clay | 612 | 7968 | 25322 | 17354 | 68.53 | 191.85 | 149.88 | -41.97 |
| JJA_2017 | 0 | Domain_All | 16030 | 339200 | 794811 | 455611 | 57.32 | 52.91 | 44.65 | -8.26 |
| JJA_2017 | 1 | Sand | 539 | 34462 | 34462 | 0 | 0.00 | 30.50 | 30.51 | 0.01 |
| JJA_2017 | 3 | Sandy Loam | 748 | 5145 | 22907 | 17762 | 77.54 | 32.38 | 29.06 | -3.33 |
| JJA_2017 | 4 | Silt Loam | 56 | 2 | 3133 | 3131 | 99.94 | 24.00 | 14.50 | -9.50 |
| JJA_2017 | 6 | Loam | 12047 | 270940 | 612672 | 341732 | 55.78 | 48.97 | 45.68 | -3.28 |
| JJA_2017 | 7 | Sandy Clay Loam | 723 | 23621 | 37359 | 13738 | 36.77 | 70.24 | 66.86 | -3.38 |
| JJA_2017 | 9 | Clay Loam | 1305 | 4519 | 60181 | 55662 | 92.49 | 67.27 | 35.82 | -31.45 |
| JJA_2017 | 12 | Clay | 612 | 511 | 24097 | 23586 | 97.88 | 126.90 | 51.12 | -75.78 |
| ANNUAL_2017 | 0 | Domain_All | 16030 | 1375266 | 2895423 | 1520157 | 52.50 | 205.80 | 176.05 | -29.75 |
| ANNUAL_2017 | 1 | Sand | 539 | 110667 | 128872 | 18205 | 14.13 | 65.02 | 64.21 | -0.81 |
| ANNUAL_2017 | 3 | Sandy Loam | 748 | 28706 | 83585 | 54879 | 65.66 | 214.71 | 197.12 | -17.59 |
| ANNUAL_2017 | 4 | Silt Loam | 56 | 3458 | 12390 | 8932 | 72.09 | 140.15 | 107.61 | -32.54 |
| ANNUAL_2017 | 6 | Loam | 12047 | 1014835 | 2200733 | 1185898 | 53.89 | 176.79 | 157.00 | -19.79 |
| ANNUAL_2017 | 7 | Sandy Clay Loam | 723 | 113403 | 142386 | 28983 | 20.36 | 337.94 | 329.13 | -8.81 |
| ANNUAL_2017 | 9 | Clay Loam | 1305 | 71428 | 230665 | 159237 | 69.03 | 308.17 | 222.03 | -86.14 |
| ANNUAL_2017 | 12 | Clay | 612 | 32769 | 96792 | 64023 | 66.14 | 521.50 | 351.09 | -170.41 |

- **Vérification de cohérence avec `water_balance_2017_annual.csv` :**

### c) Table `paper1/tables/march2018_mechanism_budget_da_by_theta1.csv` (Moyenne pondérée des classes)

**Explication chiffrée de la cause et validation :**
> Les colonnes `col` et `row` des fichiers `mech_diag.*.txt` sont locales au rang MPI ; le script précédent les indexait comme coordonnées globales, ce qui écrasait la classe 0,05–0,10 (0 maille au lieu de 650) et sous-estimait le total domaine (7,02 mm vs 7,93 mm pour `ENS_STATE`). Après conversion des coordonnées locales en coordonnées globales via `ranks_bounds`, la somme pondérée des classes égale exactement le domaine (< 0,0001 mm d'écart, conforme au seuil de 0,05 mm pour tous les 6 runs).

| Run | Moyenne pondérée classes (mm) | Total Domaine (mm) | Écart absolu (mm) | Écart < 0.05 mm |
| --- | --- | --- | --- | --- |
| ENS_STATE_201803 |   7.9348 |   7.9348 |  0.00001 | OUI (conforme) |
| ENS_STATE_201803_noRyu |  22.7228 |  22.7228 |  0.00000 | OUI (conforme) |
| ENS_FORC_201803 |   1.6361 |   1.6361 |  0.00004 | OUI (conforme) |
| ENS_FORC_201803_noRyu |  -1.2806 |  -1.2806 |  0.00002 | OUI (conforme) |
| DA_nocdf_201803_diag | -16.0323 | -16.0322 |  0.00006 | OUI (conforme) |
| DA_cdf_201803_diag |   0.1568 |   0.1568 |  0.00001 | OUI (conforme) |

Tableau complet régénéré par classe de $\theta_1$ :

| run | theta1_class | n_cells | w_pert_mm | w_ryu_mm | w_qc_mm | w_mid_pert_mm | w_mid_da_mm | w_rec_mm | w_incr_mm | w_sum_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENS_STATE_201803 | 0.05-0.10 | 650 | 0.00 | -76.24 | 0.18 | 77.49 | 0.00 | 0.00 | 0.00 | 1.44 |
| ENS_STATE_201803 | 0.10-0.20 | 6208 | 0.09 | -25.20 | 0.10 | 32.90 | 0.00 | 0.05 | 0.00 | 7.95 |
| ENS_STATE_201803 | > 0.20 | 9172 | 0.03 | 6.42 | 0.00 | 4.74 | 0.00 | -2.80 | 0.00 | 8.38 |
| ENS_STATE_201803_noRyu | 0.05-0.10 | 650 | 0.01 | 0.00 | 0.00 | 55.22 | 0.00 | 0.00 | 0.00 | 55.23 |
| ENS_STATE_201803_noRyu | 0.10-0.20 | 6208 | 0.00 | 0.00 | 0.00 | 34.82 | 0.00 | -0.00 | 0.00 | 34.82 |
| ENS_STATE_201803_noRyu | > 0.20 | 9172 | -0.00 | 0.00 | 0.00 | 12.23 | 0.00 | 0.00 | 0.00 | 12.23 |
| ENS_FORC_201803 | 0.05-0.10 | 650 | 0.00 | -0.06 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.24 |
| ENS_FORC_201803 | 0.10-0.20 | 6208 | 0.00 | 1.15 | 0.01 | 0.30 | 0.00 | 0.12 | 0.00 | 1.58 |
| ENS_FORC_201803 | > 0.20 | 9172 | 0.00 | 1.14 | 0.00 | 1.66 | 0.00 | -1.03 | 0.00 | 1.77 |
| ENS_FORC_201803_noRyu | 0.05-0.10 | 650 | 0.00 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 0.00 | 0.93 |
| ENS_FORC_201803_noRyu | 0.10-0.20 | 6208 | 0.00 | 0.00 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | 0.19 |
| ENS_FORC_201803_noRyu | > 0.20 | 9172 | 0.00 | 0.00 | 0.00 | -2.43 | 0.00 | 0.00 | 0.00 | -2.43 |
| DA_nocdf_201803_diag | 0.05-0.10 | 650 | 0.00 | -171.03 | 1.62 | 177.43 | 3.56 | 0.00 | -9.77 | 1.82 |
| DA_nocdf_201803_diag | 0.10-0.20 | 6208 | 0.09 | -57.50 | 0.75 | 60.79 | 0.24 | -0.11 | -7.41 | -3.15 |
| DA_nocdf_201803_diag | > 0.20 | 9172 | 0.03 | -77.64 | 0.13 | 87.33 | 2.99 | -1.56 | -37.29 | -26.01 |
| DA_cdf_201803_diag | 0.05-0.10 | 650 | 0.00 | -96.96 | 1.58 | 105.10 | 2.17 | 0.00 | -7.28 | 4.62 |
| DA_cdf_201803_diag | 0.10-0.20 | 6208 | 0.09 | -28.33 | 0.46 | 35.27 | 0.14 | -0.70 | -6.67 | 0.26 |
| DA_cdf_201803_diag | > 0.20 | 9172 | 0.03 | -7.54 | 0.01 | 23.34 | 1.11 | -2.14 | -15.04 | -0.23 |

## 3. Définition des Runs 2018

Table générée dans `paper1/tables/experiment_definitions_2018.csv` à partir des `lis.config` et des logs d'exécution :

| experiment | forcing_perturbation | state_perturbation | recentering_bias_corr | wilting_criterion | cdf_matching | binary_used | initial_state |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | none | none | 0 (disabled, lu lis.config/code) | Standard (smobs < smcwlt + 0.02) | none | ./src/lisf/lis/make/LIS | sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc (moyenne DA_nocdf 2018-01-01) |
| ENS_OPL | GMAO scheme (1hr) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | 0 (disabled, lu lis.config/code) | Standard (smobs < smcwlt + 0.02) | none | ./src/lisf/lis/make/LIS | DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres) |
| ENS_corr | GMAO scheme (1hr) | none | 0 (disabled, lu lislog_ENS_corr_2018.0000) | Physique corrigé (lisf_corr: pas de troncature) | none | ./src/lisf_corr/lis/LIS | DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres) |
| DA_nocdf | GMAO scheme (1hr) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | 0 (disabled, lu lis.config/code) | Standard (smobs < smcwlt + 0.02) | none | ./src/lisf/lis/LIS | DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres) |
| DA_nocdf_nowilt | GMAO scheme (1hr) | GMAO scheme (3hr, noahmp_sm_pertattribs.txt) | 0 (disabled, lu lis.config/code) | Inactif (désactivé: patch lisf_nowilt_qc_wilting) | none | ./src/lisf_nowilt/lis/LIS | DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres) |
| DA_corr | GMAO scheme (1hr) | none | 0 (disabled, lu lislog_DA_corr_2018.0000) | Physique corrigé (lisf_corr: mise à jour physique continue) | none | ./src/lisf_corr/lis/LIS | DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc (20 membres) |

## 4. Définition des Contrastes Utilisés dans le Papier

Table générée dans `paper1/tables/contrasts_definition.csv` :

| contrast_code | run_x | run_y | objective_manuscript | differences_between_runs |
| --- | --- | --- | --- | --- |
| ENS_OPL - OL_DAIC | ENS_OPL | OL_DAIC | Effet ensemble et perturbations standard | Ensemble 20 membres vs 1 membre ; forçages perturbés (GMAO) vs non perturbés ; état perturbé (GMAO) vs none ; binaire standard make/LIS |
| ENS_corr - OL_DAIC | ENS_corr | OL_DAIC | Effet ensemble corrigé (sans perturbation d état) | Ensemble 20 membres vs 1 membre ; forçages perturbés (GMAO) vs non perturbés ; état non perturbé dans les deux runs ; binaire lisf_corr vs make/LIS |
| DA_nocdf - ENS_OPL | DA_nocdf | ENS_OPL | Effet net de l assimilation SMAP native (production) | Assimilation EnKF SMAP active vs pas d assimilation ; mêmes perturbations de forçage et d état (GMAO) ; même binaire standard |
| DA_nocdf_nowilt - DA_nocdf | DA_nocdf_nowilt | DA_nocdf | Effet spécifique du filtre de flétrissement (censure) | Critère de flétrissement désactivé (patch lisf_nowilt) vs actif (standard) ; binaire lisf_nowilt vs lisf ; toutes les autres options et forçages identiques |
| DA_corr - ENS_corr | DA_corr | ENS_corr | Effet net de l assimilation SMAP sous formulation physique corrigée | Assimilation EnKF SMAP active sous lisf_corr vs open-loop ENS_corr ; aucune perturbation d état dans les deux runs ; binaire lisf_corr |
| DA_cdf - DA_nocdf | DA_cdf | DA_nocdf | Effet de la mise à l échelle climatologique par CDF matching | Stratégie de mise à l échelle: CDF matching (100 bins) vs none (retrievals natifs) ; binaire standard make/LIS |

## 5. Sorties Disponibles par Contraste et Comparaison OL_DAIC vs ENS_corr (2018)

### Matrice de disponibilité des variables :

| Variable | OL_DAIC | ENS_OPL | ENS_corr | DA_nocdf | DA_nocdf_nowilt | DA_corr | Remarque |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `ESoil` | Présent | Présent | Présent | Présent | Présent | Présent | Disponible dans tous les runs |
| `TVeg` | Présent | Présent | Présent | Présent | Présent | Présent | Disponible dans tous les runs |
| `ECanop` | Présent | Présent | Présent | Présent | Présent | Présent | Disponible dans tous les runs |
| `SoilMoist` (4 couches) | Présent | Présent | Présent | Présent | Présent | Présent | Disponible dans tous les runs |
| `Qs` | Présent | Présent | Présent | Présent | Présent | Présent | Disponible dans tous les runs |
| `Qsb` | Présent | Présent | Présent | Présent | Présent | Présent | Disponible dans tous les runs |
| `LAI` | **Absent** | Présent | Présent | Présent | Présent | Présent | Absent uniquement dans OL_DAIC (MODEL_OUTPUT_LIST standard) |
| `GWS` | **Absent** | Présent | Présent | Présent | Présent | Présent | Absent uniquement dans OL_DAIC |

### Comparaison quantitative OL_DAIC vs ENS_corr en 2018 :
Données extraites de `paper1/tables/ol_daic_vs_ens_corr_fluxes_2018.csv` (chiffres reportés sans conclure sur la substitution) :

| period | variable | description | mean_OL_DAIC | mean_ENS_corr | diff_domain_mean | diff_std | diff_min | diff_p25 | diff_median | diff_p75 | diff_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MAM_2018 | ESoil_mm | Évaporation sol nu (mm) | 73.2063 | 73.0648 | -0.1415 | 1.8842 | -22.9021 | -0.6461 | -0.2570 | 0.0814 | 20.5655 |
| MAM_2018 | TVeg_mm | Transpiration végétale (mm) | 45.0480 | 44.3146 | -0.7334 | 3.9091 | -37.3107 | -0.9111 | 0.0000 | 0.0000 | 61.4760 |
| MAM_2018 | ECanop_mm | Évaporation canopée (mm) | 6.4287 | 6.2782 | -0.1505 | 0.7237 | -10.1370 | -0.1745 | 0.0000 | 0.0000 | 11.9882 |
| MAM_2018 | ET_Total_mm | Évapotranspiration totale (mm) | 124.6830 | 123.6576 | -1.0254 | 3.2446 | -31.9156 | -1.6312 | -0.4416 | -0.1010 | 58.8157 |
| MAM_2018 | SoilMoist_Layer1_m3m3 | Humidité sol couche 1 (0-10cm, m3/m3) | 0.1903 | 0.1899 | -0.0004 | 0.0018 | -0.0933 | -0.0006 | -0.0003 | -0.0001 | 0.0759 |
| MAM_2018 | SoilMoist_Layer2_m3m3 | Humidité sol couche 2 (10-40cm, m3/m3) | 0.2264 | 0.2261 | -0.0003 | 0.0014 | -0.0166 | -0.0006 | -0.0002 | 0.0001 | 0.0201 |
| MAM_2018 | SoilMoist_Layer3_m3m3 | Humidité sol couche 3 (40-100cm, m3/m3) | 0.2251 | 0.2246 | -0.0004 | 0.0022 | -0.0393 | -0.0008 | -0.0002 | 0.0002 | 0.0216 |
| MAM_2018 | SoilMoist_Layer4_m3m3 | Humidité sol couche 4 (100-200cm, m3/m3) | 0.2346 | 0.2344 | -0.0002 | 0.0023 | -0.0448 | -0.0004 | -0.0000 | 0.0003 | 0.0360 |
| MAM_2018 | SoilMoist_Total_mm | Stock d'eau total profil 0-2m (mm) | 456.5661 | 456.0034 | -0.5627 | 3.0981 | -39.2347 | -1.1733 | -0.2597 | 0.3664 | 28.6247 |
| JJA_2018 | ESoil_mm | Évaporation sol nu (mm) | 25.2337 | 25.1919 | -0.0418 | 0.3069 | -4.2089 | -0.1777 | -0.0424 | 0.0453 | 3.3901 |
| JJA_2018 | TVeg_mm | Transpiration végétale (mm) | 36.7159 | 36.6855 | -0.0304 | 2.1193 | -32.0597 | 0.0000 | 0.0000 | 0.1505 | 25.2672 |
| JJA_2018 | ECanop_mm | Évaporation canopée (mm) | 1.5149 | 1.4961 | -0.0188 | 0.1013 | -1.7411 | -0.0073 | 0.0000 | 0.0000 | 1.2913 |
| JJA_2018 | ET_Total_mm | Évapotranspiration totale (mm) | 63.4645 | 63.3735 | -0.0910 | 2.1263 | -32.3335 | -0.2874 | -0.0946 | 0.2123 | 23.0911 |
| JJA_2018 | SoilMoist_Layer1_m3m3 | Humidité sol couche 1 (0-10cm, m3/m3) | 0.1009 | 0.1009 | 0.0000 | 0.0012 | -0.0528 | -0.0000 | 0.0000 | 0.0001 | 0.0513 |
| JJA_2018 | SoilMoist_Layer2_m3m3 | Humidité sol couche 2 (10-40cm, m3/m3) | 0.1831 | 0.1832 | 0.0001 | 0.0027 | -0.0446 | -0.0002 | 0.0001 | 0.0004 | 0.0394 |
| JJA_2018 | SoilMoist_Layer3_m3m3 | Humidité sol couche 3 (40-100cm, m3/m3) | 0.1870 | 0.1870 | 0.0001 | 0.0033 | -0.0526 | -0.0003 | 0.0001 | 0.0005 | 0.0407 |
| JJA_2018 | SoilMoist_Layer4_m3m3 | Humidité sol couche 4 (100-200cm, m3/m3) | 0.2299 | 0.2297 | -0.0002 | 0.0021 | -0.0324 | -0.0003 | -0.0000 | 0.0003 | 0.0286 |
| JJA_2018 | SoilMoist_Total_mm | Stock d'eau total profil 0-2m (mm) | 407.0753 | 406.9607 | -0.1146 | 3.8684 | -73.4477 | -0.6485 | 0.0221 | 0.6136 | 43.3953 |
| ANNUAL_2018 | ESoil_mm | Évaporation sol nu (mm) | 204.3937 | 204.0465 | -0.3472 | 3.0267 | -22.2404 | -1.4234 | -0.5307 | 0.4160 | 25.9220 |
| ANNUAL_2018 | TVeg_mm | Transpiration végétale (mm) | 103.6585 | 102.9560 | -0.7025 | 4.2889 | -43.1913 | -1.2397 | 0.0000 | 0.0000 | 55.6246 |
| ANNUAL_2018 | ECanop_mm | Évaporation canopée (mm) | 14.5859 | 14.3876 | -0.1983 | 0.9352 | -11.4773 | -0.2833 | 0.0000 | 0.0000 | 13.2953 |
| ANNUAL_2018 | ET_Total_mm | Évapotranspiration totale (mm) | 322.6381 | 321.3901 | -1.2480 | 3.4849 | -34.1124 | -2.3048 | -0.8757 | -0.0651 | 50.5246 |
| ANNUAL_2018 | SoilMoist_Layer1_m3m3 | Humidité sol couche 1 (0-10cm, m3/m3) | 0.1702 | 0.1698 | -0.0003 | 0.0017 | -0.0619 | -0.0008 | -0.0003 | 0.0002 | 0.0509 |
| ANNUAL_2018 | SoilMoist_Layer2_m3m3 | Humidité sol couche 2 (10-40cm, m3/m3) | 0.2079 | 0.2077 | -0.0002 | 0.0017 | -0.0252 | -0.0005 | -0.0001 | 0.0002 | 0.0225 |
| ANNUAL_2018 | SoilMoist_Layer3_m3m3 | Humidité sol couche 3 (40-100cm, m3/m3) | 0.2029 | 0.2027 | -0.0002 | 0.0023 | -0.0346 | -0.0007 | -0.0001 | 0.0003 | 0.0273 |
| ANNUAL_2018 | SoilMoist_Layer4_m3m3 | Humidité sol couche 4 (100-200cm, m3/m3) | 0.2305 | 0.2304 | -0.0001 | 0.0021 | -0.0370 | -0.0003 | 0.0000 | 0.0003 | 0.0329 |
| ANNUAL_2018 | SoilMoist_Total_mm | Stock d'eau total profil 0-2m (mm) | 431.6209 | 431.2839 | -0.3370 | 2.9603 | -55.6326 | -0.8533 | -0.1407 | 0.4334 | 31.2597 |

Table mensuelle complète disponible dans [`paper1/tables/ol_daic_vs_ens_corr_fluxes_2018.csv`](tables/ol_daic_vs_ens_corr_fluxes_2018.csv).

## 6. Inventaire WaPOR v3

Composantes réellement présentes sur disque listées dans `paper1/tables/wapor_v3_inventory.csv` :

| component | year | status | filepath | resolution_deg | resolution_nominal | lon_min | lon_max | lat_min | lat_max | crs | shape |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AETI | 2018 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_AETI/WaPOR_v3_AETI_2018.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| AETI | 2019 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_AETI/WaPOR_v3_AETI_2019.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| AETI | 2020 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_AETI/WaPOR_v3_AETI_2020.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| E | 2018 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_2018.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| E | 2019 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_2019.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| E | 2020 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_2020.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| T | 2018 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_T/WaPOR_v3_T_2018.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| T | 2019 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_T/WaPOR_v3_T_2019.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| T | 2020 | present | data/validation/evapotranspiration/WaPOR/WaPOR_v3_T/WaPOR_v3_T_2020.tif | 0.002246 | ~250m (0.002246°) | -7.5009 | -2.9981 | 31.9980 | 36.0224 | EPSG:4326 (WGS84) | 2005x1792 |
| I | 2018 | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| I | 2019 | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| I | 2020 | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |

- **Résolution spatiale :** Nominale ~250 m (`0.002246°` / `0.00224578821°`).
- **Emprise géographique :** Longitude `[-7.5009, -2.9981]`, Latitude `[31.9980, 36.0224]`, CRS : `EPSG:4326` (WGS84), Dimensions : `2005 × 1792` pixels.
- **Composantes présentes :** `AETI` (évapotranspiration totale), `E` (évaporation sol), `T` (transpiration végétale) sont présentes pour 2018, 2019 et 2020.
- **Composante absente :** `I` (interception par la canopée) est **absente** sur le cluster (aucun dossier ou fichier `I` sous `/home/mohammad.elaabaribao/lustre/.../data/WaPOR_v3/`).

## 7. Traçabilité des Fichiers et Scripts Produits

| Livrable | Script générateur | Fichier de données / Table associé |
|---|---|---|
| Point 1 (INVENTORY.md) | `paper1/scripts/step16_generate_inventory.py` | `paper1/INVENTORY.md`, `paper1/tables/smap_obs_days_monthly_by_basin_2018.csv` |
| Point 2.a (fig_02) | `paper1/scripts/fig_02.py` | `paper1/figures/fig_02_data.csv`, `paper1/figures/fig_02.png` |
| Point 2.b (e5_2017) | `paper1/scripts/step7_wilt_filter_2017.py` | `paper1/tables/e5_2017_by_texture.csv` |
| Point 2.c (mech_budget) | `paper1/scripts/step10_mechanism_budget_da_corrected.py` | `paper1/tables/march2018_mechanism_budget_da_by_theta1.csv` |
| Point 3 (Exp defs 2018) | `paper1/scripts/step17_experiment_definitions_2018.py` | `paper1/tables/experiment_definitions_2018.csv` |
| Point 4 (Contrasts defs) | `paper1/scripts/step18_contrasts_definition.py` | `paper1/tables/contrasts_definition.csv` |
| Point 5 (OL vs ENS flux) | `paper1/scripts/step21_compare_ol_daic_vs_ens_corr.py` | `paper1/tables/ol_daic_vs_ens_corr_fluxes_2018.csv` |
| Point 6 (WaPOR v3) | `paper1/scripts/step20_wapor_v3_inventory.py` | `paper1/tables/wapor_v3_inventory.csv` |
| Rapport A0 synthétique | `paper1/scripts/step22_generate_report_a0.py` | `paper1/REPORT_A0_checks.md` |


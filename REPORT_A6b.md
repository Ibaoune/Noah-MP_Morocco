# Rapport d'Étape A6b — Corrections : Incréments écrits 2016–2020 et Contrôle WaPOR

## 1. Contexte et Traçabilité
- **Commit parent** : `6a1995a` (Étape A6)
- **Branche de travail** : `paper1-closure`
- **Règles permanentes respectées** :
  - Aucun run modifié ni relancé ; sorties de production en lecture seule stricte.
  - Aucun téléchargement ni installation de paquet tiers.
  - Aucune suppression de fichier ni de dossier (`rm` interdit).
  - Tous les chiffres sont produits exclusivement par le script `scripts/paper1/step_a6b_corrections_increments_and_wapor.py` depuis les CSV.
  - Donnée manquante indiquée comme `absent`.

## 2. Inventaire et Statut de `paper1/cache/` avant suppression
- **Statut dans l'historique git** : `absent` (le dossier `paper1/cache/` n'a jamais été indexé ni committé dans git).
- **Statut dans les journaux d'exécution (logs)** : `absent` (aucun fichier documenté dans les logs d'exécution de la session avant sa suppression en A6).
- **Règle respectée** : Mention formelle `absent` consignée conformément à la consigne stricte.

## 3. TÂCHE 1 — Incréments écrits 2016–2020 (DA_nocdf et DA_cdf)

### 3.1 Contrôle obligatoire sur DA_corr_2018 (Tâche 1a)
Le calcul a été relancé sur `DA_corr_2018` avec le même code d'intégration des incréments que l'étape A4c. La comparaison avec la table de référence `paper1/tables/A4c_increments_written_vs_applied.csv` confirme que tous les écarts sont strictement inférieurs au seuil obligatoire de ±0,01 mm.

| region | written_incr_total_net_computed_mm | written_incr_total_net_a4c_ref_mm | ecart_vs_a4c_mm | status |
| :--- | :--- | :--- | :--- | :---: |
| Domaine complet | -483.475 | -483.475 | 0.000234 | VALIDÉ (<= 0.01 mm) |
| Lalla Chafia | -55.57 | -55.57 | 0.000445 | VALIDÉ (<= 0.01 mm) |
| Sidi Jabeur | -397.209 | -397.209 | 0.000325 | VALIDÉ (<= 0.01 mm) |
| Sebou amont | -561.793 | -561.793 | 0.000186 | VALIDÉ (<= 0.01 mm) |

### 3.2 Table complète des incréments écrits vs appliqués (Tâche 1b & 1c)
Fichier source : `paper1/tables/A6b_increments_written_vs_applied.csv` (colonnes synthétiques pour le rapport ; toutes les couches pos/nég/net sont disponibles dans le CSV complet).

| run | year | region | written_incr_L1_net_mm | written_incr_L2_net_mm | written_incr_L3_net_mm | written_incr_L4_net_mm | written_incr_total_net_mm | applied_increment_mm | diff_written_minus_applied_mm | pert_bias_corr | controle_fletrissement |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| DA_nocdf | 2016 | Domaine complet | -37.278 | -31.739 | -18.741 | -5.201 | -92.959 | -6.41 | -86.549 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2016 | Lalla Chafia | -2.202 | 27.52 | 37.459 | 5.81 | 68.588 | 202.18 | -133.592 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2016 | Sidi Jabeur | -30.199 | 6.173 | 12.309 | 1.897 | -9.821 | 76.64 | -86.461 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2016 | Sebou amont | -60.779 | -50.07 | -45.938 | -17.894 | -174.68 | -59.38 | -115.3 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2017 | Domaine complet | -28.986 | -23.615 | -14.737 | -11.304 | -78.642 | 6.57 | -85.212 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2017 | Lalla Chafia | -4.915 | -8.551 | 0.335 | 0.961 | -12.17 | 105.12 | -117.29 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2017 | Sidi Jabeur | -30.261 | -6.648 | 14.144 | 16.25 | -6.515 | 75.85 | -82.365 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2017 | Sebou amont | -59.624 | -47.325 | -29.965 | -18.754 | -155.668 | -73.26 | -82.408 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2018 | Domaine complet | -57.886 | -52.505 | -32.804 | -22.17 | -165.366 | -63.05 | -102.316 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2018 | Lalla Chafia | 26.75 | 44.119 | 72.868 | 65.177 | 208.915 | 309.65 | -100.735 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2018 | Sidi Jabeur | -14.837 | 15.802 | 46.757 | 14.561 | 62.283 | 213.91 | -151.627 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2018 | Sebou amont | -72.0 | -72.272 | -68.077 | -39.516 | -251.866 | -127.72 | -124.146 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2019 | Domaine complet | -26.145 | -24.63 | -11.225 | -6.748 | -68.747 | 19.37 | -88.117 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2019 | Lalla Chafia | 23.849 | 41.954 | 71.752 | 28.122 | 165.677 | 297.67 | -131.993 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2019 | Sidi Jabeur | 0.733 | 1.341 | 13.436 | 1.978 | 17.489 | 136.29 | -118.801 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2019 | Sebou amont | -29.034 | -25.732 | -21.197 | -16.218 | -92.181 | 3.76 | -95.941 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2020 | Domaine complet | -26.057 | -28.557 | -15.726 | -10.843 | -81.183 | 20.01 | -101.193 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2020 | Lalla Chafia | 18.724 | 26.725 | 39.166 | 3.063 | 87.678 | 186.62 | -98.942 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2020 | Sidi Jabeur | -10.87 | 0.759 | -3.313 | -16.862 | -30.286 | 80.34 | -110.626 | forcé=1 (option config ignorée) | actif |
| DA_nocdf | 2020 | Sebou amont | -56.762 | -50.587 | -44.652 | -39.938 | -191.939 | -75.7 | -116.239 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2016 | Domaine complet | 17.45 | -10.861 | -14.227 | -17.743 | -25.382 | 75.53 | -100.912 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2016 | Lalla Chafia | 7.839 | -0.109 | -2.79 | -29.066 | -24.126 | 112.22 | -136.346 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2016 | Sidi Jabeur | 6.734 | 3.209 | 10.958 | -16.744 | 4.156 | 88.67 | -84.514 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2016 | Sebou amont | 15.948 | -20.259 | -27.79 | -30.212 | -62.314 | 46.26 | -108.574 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2017 | Domaine complet | 16.331 | -12.261 | -14.89 | -18.377 | -29.197 | 75.9 | -105.097 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2017 | Lalla Chafia | 11.298 | -26.928 | -36.267 | -34.9 | -86.797 | 85.14 | -171.937 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2017 | Sidi Jabeur | 14.949 | -18.583 | -20.554 | -28.478 | -52.666 | 69.44 | -122.106 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2017 | Sebou amont | 21.432 | -11.21 | -20.998 | -20.042 | -30.819 | 56.09 | -86.909 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2018 | Domaine complet | -8.455 | -26.531 | -32.223 | -37.994 | -105.203 | 23.32 | -128.523 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2018 | Lalla Chafia | 0.311 | -34.602 | -52.786 | -20.011 | -107.088 | 23.83 | -130.918 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2018 | Sidi Jabeur | -8.993 | -32.341 | -46.207 | -25.674 | -113.215 | 76.45 | -189.665 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2018 | Sebou amont | -16.052 | -45.628 | -60.003 | -78.453 | -200.137 | -35.9 | -164.237 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2019 | Domaine complet | 23.483 | -7.199 | -14.833 | -22.702 | -21.251 | 95.04 | -116.291 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2019 | Lalla Chafia | 24.192 | -0.559 | -30.944 | -19.869 | -27.181 | 151.53 | -178.711 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2019 | Sidi Jabeur | 27.167 | -5.404 | -25.307 | -21.196 | -24.741 | 137.25 | -161.991 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2019 | Sebou amont | 35.853 | 1.082 | -18.247 | -39.297 | -20.609 | 107.07 | -127.679 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2020 | Domaine complet | 29.076 | -8.305 | -16.317 | -30.398 | -25.944 | 107.31 | -133.254 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2020 | Lalla Chafia | 38.549 | 6.335 | -7.914 | -27.044 | 9.926 | 152.22 | -142.294 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2020 | Sidi Jabeur | 33.997 | -2.769 | -16.196 | -18.818 | -3.787 | 129.86 | -133.647 | forcé=1 (option config ignorée) | actif |
| DA_cdf | 2020 | Sebou amont | 22.398 | -11.406 | -25.258 | -50.862 | -65.128 | 69.05 | -134.178 | forcé=1 (option config ignorée) | actif |
| DA_corr | 2018 | Domaine complet | -23.045 | -84.347 | -189.992 | -186.091 | -483.475 | -152.39 | -331.085 | 0 (lu config, confirmé lislog) | désactivé |
| DA_corr | 2018 | Lalla Chafia | -1.285 | 1.314 | -39.775 | -15.823 | -55.57 | 168.192 | -223.762 | 0 (lu config, confirmé lislog) | désactivé |
| DA_corr | 2018 | Sidi Jabeur | -7.534 | -22.916 | -93.28 | -273.479 | -397.209 | 11.179 | -408.388 | 0 (lu config, confirmé lislog) | désactivé |
| DA_corr | 2018 | Sebou amont | -18.11 | -65.407 | -249.574 | -228.702 | -561.793 | -146.978 | -414.815 | 0 (lu config, confirmé lislog) | désactivé |

### 3.3 Citations de code et configuration pour pert_bias_corr et contrôle de flétrissement (Tâche 1c)
- **Runs de la matrice 2016–2020 (`DA_nocdf` et `DA_cdf`)** :
  - `pert_bias_corr` : `forcé=1 (option config ignorée)` — Citation : `src/lisf/lis/core/LIS_readConfig.F90:793 (LIS_rc%pert_bias_corr = 1 forcé, ESMF_ConfigGetAttribute commenté) ; option experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_nocdf_noirr_2018-01.config:96 (Apply perturbation bias correction: 0) ignorée ; appelé via noahmp401_setsoilm.F90:361,869`
  - `controle_fletrissement` : `actif` — Citation : `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:272 (ligne active: elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)`
- **Run de sensibilité 2018 (`DA_corr`)** :
  - `pert_bias_corr` : `0 (lu config, confirmé lislog)` — Citation : `src/lisf_corr/lis/core/LIS_readConfig.F90:794 (LIS_rc%pert_bias_corr lu de config) ; experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/config/lis_DA_corr_2018.config:96 ; logs/lislog_DA_corr_2018.0000:4`
  - `controle_fletrissement` : `désactivé` — Citation : `src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90:273 (ligne commentée: ! elseif(smobs(t) - smcwlt_obs(t).lt.0.02) then)`

## 4. TÂCHE 2 — Contrôle et Évaluation WaPOR v3

### 4.1 Contrôle obligatoire sur DA_nocdf 2018 (Tâche 2a)
Reproduction exacte de la table de référence `paper1/tables/A1b_wapor_et_comparison.csv` (Domaine complet, Annuel) :

| Grandeur | Valeur calculée A6b (mm) | Référence A1b (mm) | Écart absolu (mm) | Statut (< 0.1 mm) |
| :--- | :---: | :---: | :---: | :---: |
| ESoil_model_mm | 229.97 | 229.97 | 0.0029 | VALIDÉ |
| E_wapor_mm | 145.41 | 145.41 | 0.0026 | VALIDÉ |
| bias_E_mm | 84.56 | 84.56 | 0.0003 | VALIDÉ |
| TVeg_model_mm | 159.74 | 159.74 | 0.0046 | VALIDÉ |
| T_wapor_mm | 215.84 | 215.84 | 0.0019 | VALIDÉ |
| bias_T_mm | -56.10 | -56.10 | 0.0027 | VALIDÉ |

### 4.2 Description de la différence de méthode (A6 vs A1b)
- **Cause de l'écart initial en A6** : En A6, l'agrégation de l'image WaPOR 2018 reposait sur un partitionnement en blocs entiers sans calage géographique explicite (`r_factor = arr.shape[0] // 121`), et tronquait arbitrairement les indices valides à 5 379 mailles sans correspondance géographique rigoureuse.
- **Méthode corrigée A1b** :
  1. **Origine et résolution géographique WaPOR** : `lat_max_w = 36.02°`, `lon_0_w = -7.50°`, `d_w = 0.0022457882102988038°`.
  2. **Boîtes englobantes exactes** : Pour chaque maille LIS $(j, i)$ de centre $(lat_c, lon_c)$, extraction du bloc raster couvrant $[lat_c \pm 0.025^\circ]$ et $[lon_c \pm 0.025^\circ]$.
  3. **Critère de validité** : Seuil de mailles valides $\ge 80\%$ par cellule 5 km.
  4. **Masque d'intersection** : Intersection stricte $(m_E \land m_T)$ avec `landmask_181`, produisant très exactement 5 379 mailles valides.
  5. **Unités et flux** : Sommation journalière des flux Noah-MP $ESoil$ et $TVeg$ en mm/jour ($86400 \times kg/m^2/s$) sur l'année calendaire complète, strictement identique au protocole A1b.

### 4.3 Table A6b_et_vs_wapor.csv (2018–2020) et comparaison OPL vs OL_DAIC 2018 (Tâche 2b)
Fichier source : `paper1/tables/A6b_et_vs_wapor.csv`

| year | run | region | ESoil_model_mm | E_wapor_mm | E_bias_vs_WaPOR_E_mm | TVeg_model_mm | T_wapor_mm | T_bias_vs_WaPOR_T_mm | ETcomb_model_mm | ETcomb_wapor_mm | ET_bias_mm | variation_abs_bias_ET_vs_OPL_mm | n_cells |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2018 | OPL | Zone WaPOR (5379 mailles) | 249.84 | 145.41 | 104.42 | 205.76 | 215.84 | -10.08 | 455.6 | 361.25 | 94.34 | - | 5379 |
| 2018 | OL_DAIC | Zone WaPOR (5379 mailles) | 244.5 | 145.41 | 99.09 | 203.06 | 215.84 | -12.78 | 447.56 | 361.25 | 86.3 | -8.04 | 5379 |
| 2018 | DA_nocdf | Zone WaPOR (5379 mailles) | 229.97 | 145.41 | 84.56 | 159.74 | 215.84 | -56.1 | 389.72 | 361.25 | 28.46 | -65.88 | 5379 |
| 2018 | DA_cdf | Zone WaPOR (5379 mailles) | 266.12 | 145.41 | 120.71 | 186.61 | 215.84 | -29.23 | 452.73 | 361.25 | 91.48 | -2.87 | 5379 |
| 2019 | OPL | Zone WaPOR (5379 mailles) | 140.72 | 149.91 | -9.18 | 153.56 | 212.86 | -59.3 | 294.28 | 362.77 | -68.49 | - | 5379 |
| 2019 | DA_nocdf | Zone WaPOR (5379 mailles) | 161.89 | 149.91 | 11.98 | 114.71 | 212.86 | -98.15 | 276.6 | 362.77 | -86.17 | 17.68 | 5379 |
| 2019 | DA_cdf | Zone WaPOR (5379 mailles) | 203.28 | 149.91 | 53.37 | 141.49 | 212.86 | -71.37 | 344.77 | 362.77 | -18.0 | -50.49 | 5379 |
| 2020 | OPL | Zone WaPOR (5379 mailles) | 165.4 | 150.5 | 14.9 | 120.91 | 201.38 | -80.48 | 286.31 | 351.89 | -65.58 | - | 5379 |
| 2020 | DA_nocdf | Zone WaPOR (5379 mailles) | 183.56 | 150.5 | 33.05 | 109.9 | 201.38 | -91.48 | 293.46 | 351.89 | -58.43 | -7.15 | 5379 |
| 2020 | DA_cdf | Zone WaPOR (5379 mailles) | 228.56 | 150.5 | 78.06 | 142.35 | 201.38 | -59.04 | 370.9 | 351.89 | 19.02 | -46.56 | 5379 |

## 5. Synthèse des Livrables
- Script : `scripts/paper1/step_a6b_corrections_increments_and_wapor.py`
- CSV 1 : `paper1/tables/A6b_increments_written_vs_applied.csv` et racine
- CSV 2 : `paper1/tables/A6b_et_vs_wapor.csv` et racine
- Rapport : `paper1/REPORT_A6b.md` et `REPORT_A6b.md`
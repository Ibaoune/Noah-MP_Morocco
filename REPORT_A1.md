# Rapport d'Étape A1 — Végétation et partition de l'ET (H1)

Ce rapport présente les résultats quantitatifs de l'étape A1, sans interprétation subjective ni spéculation.
Tous les chiffres sont issus des scripts de post-traitement sur les sorties de simulation LIS et les observations MODIS LAI et WaPOR v3.

## 1. Méthodes d'Agrégation et Données

### 1.1 Grille et Masques
- **Grille LIS NorthMor** : 121 rangées × 181 colonnes (résolution 0,05°, domaine 30,0°N à 36,0°N, 10,0°O à 1,0°O).
- **Nombre total de mailles terrestres (LANDMASK=1)** : 16030 mailles.
- **Bassin de Lalla Chafia** : 180 mailles.
- **Bassin de Sidi Jabeur** : 170 mailles.
- **Bassin de Sebou amont** : 227 mailles.

### 1.2 Occupation du Sol (MODIS-IGBP NCEP-modified)
Classes dominantes présentes sur le domaine terrestre :
- **Classe 1 - Evergreen Needleleaf Forest** : 22 mailles (0.14 %)
- **Classe 2 - Evergreen Broadleaf Forest** : 8 mailles (0.05 %)
- **Classe 3 - Deciduous Needleleaf Forest** : 2 mailles (0.01 %)
- **Classe 5 - Mixed Forest** : 37 mailles (0.23 %)
- **Classe 6 - Closed Shrublands** : 54 mailles (0.34 %)
- **Classe 7 - Open Shrublands** : 5636 mailles (35.16 %)
- **Classe 8 - Woody Savannas** : 89 mailles (0.56 %)
- **Classe 9 - Savannas** : 13 mailles (0.08 %)
- **Classe 10 - Grasslands** : 574 mailles (3.58 %)
- **Classe 12 - Croplands** : 1127 mailles (7.03 %)
- **Classe 13 - Urban and Built-Up** : 117 mailles (0.73 %)
- **Classe 14 - Cropland/Natural Vegetation Mosaic** : 1 mailles (0.01 %)
- **Classe 16 - Barren or Sparsely Vegetated** : 8350 mailles (52.09 %)

### 1.3 MODIS LAI (MCD15A2H.006)
- **Résolution native** : ~500 m (1/240°).
- **Agrégation spatiale** : blocs de 12 × 12 pixels sur chaque maille 5 km LIS (moyenne des pixels valides avec QC <= 100, facteur d'échelle 0,1).
- **Agrégation temporelle** : composites 8 jours groupés par mois civil (selon la date centrale du composite) pour chaque mois de 2018 (46 fichiers) et de 2016–2020.
- **Règle pour OL_DAIC** : la variable `LAI_tavg` n'a pas été demandée en sortie (fichier MODEL_OUTPUT_LIST hourly). Selon l'instruction, les valeurs de `ENS_corr` sont utilisées comme substitut factuel et explicitement indiquées par la mention `substitut=ENS_corr`.

### 1.4 WaPOR v3 (2018–2020)
- **Résolution native** : ~250 m (0,002246°).
- **Emprise archivée** : Longitudes -7,50° à -2,99° ; Latitudes 32,00° à 36,02° (Nord du Maroc).
- **Règle de rétention** : moyenne des pixels 250 m valides dans la maille LIS 5 km, cellule retenue uniquement si la couverture de pixels valides est ≥ 80 %.
- **Nombre de cellules retenues sur la grille LIS (couverture ≥ 80 %)** : 5379 mailles.
- **Disponibilité temporelle** : rasters annuels (2018, 2019, 2020) pour AETI, E, T, NPP. Les fichiers dékadaires et mensuels ne sont pas archivés sur disque.
- **Interception et AETI** : la composante interception (I) de WaPOR v3 n'étant pas disponible sur disque, ECanop et AETI total ne sont pas comparés et portent la mention `absent`.
- **Métriques mensuelles/saisonnières** : en l'absence de fichiers dékadaires ou mensuels sur disque, ces métriques portent la mention `absent (WaPOR v3 dékadaire non archivé sur disque)`.

---

## 2. Tableaux Récapitulatifs Factuels

### 2.1 Synthèse LAI Modèle vs MODIS en 2018 (Domaine et Bassins)

| experiment | substitut | region_or_class | lai_model_annual_mean | lai_modis_annual_mean | bias_annual | monthly_correlation | peak_month_model | peak_month_modis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | ENS_corr | Domaine complet | 0.8978 | 0.4256 | 0.4722 | 0.4904 | 6 | 4 |
| OL_DAIC | ENS_corr | Lalla Chafia | 1.9909 | 0.7229 | 1.268 | 0.7722 | 5 | 4 |
| OL_DAIC | ENS_corr | Sidi Jabeur | 1.7195 | 0.5646 | 1.1549 | 0.5708 | 5 | 4 |
| OL_DAIC | ENS_corr | Sebou amont | 1.4408 | 0.3947 | 1.0461 | 0.8316 | 6 | 5 |
| ENS_OPL | aucun | Domaine complet | 0.9114 | 0.4256 | 0.4858 | 0.4828 | 6 | 4 |
| ENS_OPL | aucun | Lalla Chafia | 1.9961 | 0.7229 | 1.2732 | 0.7721 | 5 | 4 |
| ENS_OPL | aucun | Sidi Jabeur | 1.7346 | 0.5646 | 1.17 | 0.5763 | 5 | 4 |
| ENS_OPL | aucun | Sebou amont | 1.4217 | 0.3947 | 1.027 | 0.8369 | 6 | 5 |
| ENS_corr | aucun | Domaine complet | 0.8978 | 0.4256 | 0.4722 | 0.4904 | 6 | 4 |
| ENS_corr | aucun | Lalla Chafia | 1.9909 | 0.7229 | 1.268 | 0.7722 | 5 | 4 |
| ENS_corr | aucun | Sidi Jabeur | 1.7195 | 0.5646 | 1.1549 | 0.5708 | 5 | 4 |
| ENS_corr | aucun | Sebou amont | 1.4408 | 0.3947 | 1.0461 | 0.8316 | 6 | 5 |
| DA_nocdf | aucun | Domaine complet | 0.7138 | 0.4256 | 0.2882 | 0.6451 | 5 | 4 |
| DA_nocdf | aucun | Lalla Chafia | 1.9842 | 0.7229 | 1.2613 | 0.8209 | 5 | 4 |
| DA_nocdf | aucun | Sidi Jabeur | 1.7439 | 0.5646 | 1.1793 | 0.6771 | 5 | 4 |
| DA_nocdf | aucun | Sebou amont | 0.9646 | 0.3947 | 0.5699 | 0.8852 | 6 | 5 |
| DA_nocdf_nowilt | aucun | Domaine complet | 0.7022 | 0.4256 | 0.2766 | 0.6619 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Lalla Chafia | 1.9693 | 0.7229 | 1.2464 | 0.8277 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Sidi Jabeur | 1.7358 | 0.5646 | 1.1711 | 0.6818 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Sebou amont | 0.95 | 0.3947 | 0.5553 | 0.8893 | 6 | 5 |
| DA_corr | aucun | Domaine complet | 0.6856 | 0.4256 | 0.2599 | 0.6084 | 5 | 4 |
| DA_corr | aucun | Lalla Chafia | 1.8367 | 0.7229 | 1.1138 | 0.8484 | 5 | 4 |
| DA_corr | aucun | Sidi Jabeur | 1.4309 | 0.5646 | 0.8662 | 0.7386 | 5 | 4 |
| DA_corr | aucun | Sebou amont | 1.0528 | 0.3947 | 0.6581 | 0.9231 | 6 | 5 |

### 2.2 ΔLAI dû à l'Assimilation en 2018 (Domaine et Bassins)

| contrast | region_or_class | delta_lai_annual_mean | delta_lai_m01 | delta_lai_m04 | delta_lai_m07 | delta_lai_m10 |
| --- | --- | --- | --- | --- | --- | --- |

### 2.3 Partition Annuelle de l'ET en 2018 (Domaine et Bassins)

| experiment | region_or_class | ESoil_mm | TVeg_mm | ECanop_mm | ET_total_mm | fraction_TVeg | fraction_ESoil | fraction_ECanop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | Domaine complet | 198.28 | 100.55 | 14.06 | 312.89 | 0.3213 | 0.6337 | 0.0449 |
| OL_DAIC | Lalla Chafia | 255.11 | 309.52 | 42.91 | 607.54 | 0.5095 | 0.4199 | 0.0706 |
| OL_DAIC | Sidi Jabeur | 238.88 | 260.42 | 33.84 | 533.15 | 0.4885 | 0.4481 | 0.0635 |
| OL_DAIC | Sebou amont | 226.47 | 189.63 | 43.81 | 459.9 | 0.4123 | 0.4924 | 0.0953 |
| ENS_OPL | Domaine complet | 264.71 | 101.27 | 13.89 | 379.87 | 0.2666 | 0.6968 | 0.0366 |
| ENS_OPL | Lalla Chafia | 320.39 | 306.39 | 42.0 | 668.77 | 0.4581 | 0.4791 | 0.0628 |
| ENS_OPL | Sidi Jabeur | 309.19 | 258.82 | 33.19 | 601.2 | 0.4305 | 0.5143 | 0.0552 |
| ENS_OPL | Sebou amont | 283.0 | 187.72 | 42.06 | 512.77 | 0.3661 | 0.5519 | 0.082 |
| ENS_corr | Domaine complet | 197.96 | 99.87 | 13.87 | 311.7 | 0.3204 | 0.6351 | 0.0445 |
| ENS_corr | Lalla Chafia | 254.5 | 307.24 | 42.31 | 604.05 | 0.5086 | 0.4213 | 0.07 |
| ENS_corr | Sidi Jabeur | 238.75 | 257.42 | 33.31 | 529.48 | 0.4862 | 0.4509 | 0.0629 |
| ENS_corr | Sebou amont | 226.47 | 188.45 | 43.21 | 458.13 | 0.4113 | 0.4943 | 0.0943 |
| DA_nocdf | Domaine complet | 182.63 | 75.14 | 11.59 | 269.35 | 0.279 | 0.678 | 0.043 |
| DA_nocdf | Lalla Chafia | 301.68 | 293.09 | 43.12 | 637.88 | 0.4595 | 0.4729 | 0.0676 |
| DA_nocdf | Sidi Jabeur | 269.67 | 252.44 | 34.02 | 556.12 | 0.4539 | 0.4849 | 0.0612 |
| DA_nocdf | Sebou amont | 213.19 | 118.76 | 31.91 | 363.87 | 0.3264 | 0.5859 | 0.0877 |
| DA_nocdf_nowilt | Domaine complet | 153.01 | 73.64 | 11.47 | 238.12 | 0.3093 | 0.6426 | 0.0482 |
| DA_nocdf_nowilt | Lalla Chafia | 282.43 | 290.14 | 42.94 | 615.51 | 0.4714 | 0.4589 | 0.0698 |
| DA_nocdf_nowilt | Sidi Jabeur | 258.34 | 250.62 | 33.92 | 542.88 | 0.4616 | 0.4759 | 0.0625 |
| DA_nocdf_nowilt | Sebou amont | 202.48 | 116.64 | 31.5 | 350.62 | 0.3327 | 0.5775 | 0.0898 |
| DA_corr | Domaine complet | 162.09 | 72.88 | 11.51 | 246.48 | 0.2957 | 0.6576 | 0.0467 |
| DA_corr | Lalla Chafia | 263.32 | 266.35 | 41.57 | 571.25 | 0.4663 | 0.461 | 0.0728 |
| DA_corr | Sidi Jabeur | 242.75 | 190.02 | 29.59 | 462.37 | 0.411 | 0.525 | 0.064 |
| DA_corr | Sebou amont | 223.06 | 132.57 | 34.01 | 389.64 | 0.3402 | 0.5725 | 0.0873 |

### 2.4 Contrastes Annuels C1, C2, C3, C4 Décomposés par Composante (2018)

| contrast_id | contrast_name | region_or_class | delta_ESoil_mm | delta_TVeg_mm | delta_ECanop_mm | delta_ET_total_mm |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | ENS_OPL − OL_DAIC | Domaine complet | 66.42 | 0.72 | -0.17 | 66.97 |
| C1 | ENS_OPL − OL_DAIC | Lalla Chafia | 65.28 | -3.13 | -0.91 | 61.23 |
| C1 | ENS_OPL − OL_DAIC | Sidi Jabeur | 70.31 | -1.61 | -0.65 | 68.05 |
| C1 | ENS_OPL − OL_DAIC | Sebou amont | 56.53 | -1.91 | -1.75 | 52.87 |
| C2 | DA_nocdf − ENS_OPL | Domaine complet | -82.08 | -26.13 | -2.3 | -110.51 |
| C2 | DA_nocdf − ENS_OPL | Lalla Chafia | -18.71 | -13.3 | 1.12 | -30.89 |
| C2 | DA_nocdf − ENS_OPL | Sidi Jabeur | -39.52 | -6.38 | 0.82 | -45.07 |
| C2 | DA_nocdf − ENS_OPL | Sebou amont | -69.81 | -68.95 | -10.15 | -148.9 |
| C3 | DA_corr − ENS_corr | Domaine complet | -35.87 | -26.99 | -2.36 | -65.22 |
| C3 | DA_corr − ENS_corr | Lalla Chafia | 8.82 | -40.88 | -0.74 | -32.8 |
| C3 | DA_corr − ENS_corr | Sidi Jabeur | 4.0 | -67.4 | -3.71 | -67.11 |
| C3 | DA_corr − ENS_corr | Sebou amont | -3.41 | -55.88 | -9.21 | -68.5 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Domaine complet | -29.61 | -1.5 | -0.12 | -31.23 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Lalla Chafia | -19.25 | -2.94 | -0.18 | -22.37 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sidi Jabeur | -11.33 | -1.82 | -0.1 | -13.25 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sebou amont | -10.71 | -2.12 | -0.41 | -13.25 |

### 2.5 Comparaison Annuelle contre WaPOR v3 en 2018 (Domaine et Bassins)

| experiment | region_or_class | n_cells_valid | ESoil_model_mm | E_wapor_mm | bias_E_mm | TVeg_model_mm | T_wapor_mm | bias_T_mm | ETcomb_model_mm | ETcomb_wapor_mm | bias_ETcomb_mm | ratio_T_over_ETcomb_model | ratio_T_over_ETcomb_wapor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | Domaine complet | 5379 | 244.5 | 145.25 | 99.25 | 203.06 | 215.84 | -12.78 | 447.56 | 361.09 | 86.47 | 0.4055 | 0.5096 |
| OL_DAIC | Lalla Chafia | 180 | 255.11 | 153.34 | 101.77 | 309.52 | 328.61 | -19.09 | 564.63 | 481.95 | 82.68 | 0.5481 | 0.6775 |
| OL_DAIC | Sidi Jabeur | 170 | 238.88 | 151.44 | 87.45 | 260.42 | 252.33 | 8.09 | 499.31 | 403.77 | 95.54 | 0.5157 | 0.614 |
| OL_DAIC | Sebou amont | 227 | 226.47 | 176.38 | 50.08 | 189.63 | 172.3 | 17.33 | 416.1 | 348.68 | 67.42 | 0.4542 | 0.4673 |
| ENS_OPL | Domaine complet | 5379 | 308.0 | 145.25 | 162.76 | 202.5 | 215.84 | -13.34 | 510.51 | 361.09 | 149.42 | 0.3642 | 0.5096 |
| ENS_OPL | Lalla Chafia | 180 | 320.39 | 153.34 | 167.05 | 306.39 | 328.61 | -22.22 | 626.77 | 481.95 | 144.82 | 0.4898 | 0.6775 |
| ENS_OPL | Sidi Jabeur | 170 | 309.19 | 151.44 | 157.75 | 258.82 | 252.33 | 6.48 | 568.01 | 403.77 | 164.24 | 0.452 | 0.614 |
| ENS_OPL | Sebou amont | 227 | 283.0 | 176.38 | 106.62 | 187.72 | 172.3 | 15.42 | 470.72 | 348.68 | 122.04 | 0.4005 | 0.4673 |
| ENS_corr | Domaine complet | 5379 | 244.05 | 145.25 | 98.8 | 201.66 | 215.84 | -14.18 | 445.71 | 361.09 | 84.62 | 0.4044 | 0.5096 |
| ENS_corr | Lalla Chafia | 180 | 254.5 | 153.34 | 101.16 | 307.24 | 328.61 | -21.37 | 561.74 | 481.95 | 79.79 | 0.5468 | 0.6775 |
| ENS_corr | Sidi Jabeur | 170 | 238.75 | 151.44 | 87.32 | 257.42 | 252.33 | 5.09 | 496.17 | 403.77 | 92.41 | 0.513 | 0.614 |
| ENS_corr | Sebou amont | 227 | 226.47 | 176.38 | 50.09 | 188.45 | 172.3 | 16.15 | 414.92 | 348.68 | 66.24 | 0.4525 | 0.4673 |
| DA_nocdf | Domaine complet | 5379 | 229.97 | 145.25 | 84.72 | 159.74 | 215.84 | -56.1 | 389.72 | 361.09 | 28.63 | 0.3298 | 0.5096 |
| DA_nocdf | Lalla Chafia | 180 | 301.68 | 153.34 | 148.34 | 293.09 | 328.61 | -35.52 | 594.76 | 481.95 | 112.82 | 0.4893 | 0.6775 |
| DA_nocdf | Sidi Jabeur | 170 | 269.67 | 151.44 | 118.24 | 252.44 | 252.33 | 0.1 | 522.11 | 403.77 | 118.34 | 0.472 | 0.614 |
| DA_nocdf | Sebou amont | 227 | 213.19 | 176.38 | 36.81 | 118.76 | 172.3 | -53.53 | 331.96 | 348.68 | -16.72 | 0.3352 | 0.4673 |
| DA_nocdf_nowilt | Domaine complet | 5379 | 210.38 | 145.25 | 65.13 | 157.25 | 215.84 | -58.59 | 367.63 | 361.09 | 6.54 | nan | 0.5096 |
| DA_nocdf_nowilt | Lalla Chafia | 180 | 282.43 | 153.34 | 129.09 | 290.14 | 328.61 | -38.47 | 572.57 | 481.95 | 90.62 | 0.5066 | 0.6775 |
| DA_nocdf_nowilt | Sidi Jabeur | 170 | 258.34 | 151.44 | 106.91 | 250.62 | 252.33 | -1.72 | 508.96 | 403.77 | 105.19 | 0.4815 | 0.614 |
| DA_nocdf_nowilt | Sebou amont | 227 | 202.48 | 176.38 | 26.1 | 116.64 | 172.3 | -55.66 | 319.12 | 348.68 | -29.56 | 0.3378 | 0.4673 |
| DA_corr | Domaine complet | 5379 | 220.12 | 145.25 | 74.87 | 154.47 | 215.84 | -61.37 | 374.59 | 361.09 | 13.5 | nan | 0.5096 |
| DA_corr | Lalla Chafia | 180 | 263.32 | 153.34 | 109.98 | 266.35 | 328.61 | -62.25 | 529.68 | 481.95 | 47.73 | 0.4833 | 0.6775 |
| DA_corr | Sidi Jabeur | 170 | 242.75 | 151.44 | 91.32 | 190.02 | 252.33 | -62.31 | 432.77 | 403.77 | 29.01 | 0.4211 | 0.614 |
| DA_corr | Sebou amont | 227 | 223.06 | 176.38 | 46.67 | 132.57 | 172.3 | -39.72 | 355.63 | 348.68 | 6.95 | 0.3477 | 0.4673 |

### 2.6 Direction de Changement pour C2 et C3 contre WaPOR v3 en 2018

| contrast_id | contrast_name | component | region_or_class | n_cells_valid | delta_abs_bias_mm | pct_cells_closer | pct_cells_farther | pct_cells_neutral |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Domaine complet | 5379 | -72.16 | 78.04 | 21.9 | 0.06 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Lalla Chafia | 180 | -18.71 | 51.67 | 48.33 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Sidi Jabeur | 170 | -39.52 | 81.76 | 18.24 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Sebou amont | 227 | -53.69 | 81.5 | 18.5 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Domaine complet | 5379 | 16.78 | 31.86 | 46.76 | 21.38 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Lalla Chafia | 180 | 17.04 | 45.56 | 54.44 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Sidi Jabeur | 170 | 6.41 | 45.29 | 50.0 | 4.71 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Sebou amont | 227 | 12.86 | 44.93 | 49.34 | 5.73 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Domaine complet | 5379 | -65.16 | 68.43 | 31.42 | 0.15 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Lalla Chafia | 180 | -18.26 | 46.11 | 53.89 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Sidi Jabeur | 170 | -29.8 | 68.82 | 31.18 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Sebou amont | 227 | -49.67 | 72.69 | 27.31 | 0.0 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Domaine complet | 5379 | -23.53 | 64.79 | 27.61 | 7.6 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Lalla Chafia | 180 | 8.82 | 25.0 | 75.0 | 0.0 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Sidi Jabeur | 170 | 4.0 | 33.53 | 66.47 | 0.0 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Sebou amont | 227 | -0.36 | 44.93 | 55.07 | 0.0 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Domaine complet | 5379 | 36.74 | 24.02 | 48.17 | 27.81 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Lalla Chafia | 180 | 44.79 | 28.89 | 71.11 | 0.0 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Sidi Jabeur | 170 | 24.04 | 40.0 | 55.29 | 4.71 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Sebou amont | 227 | 32.84 | 34.8 | 59.47 | 5.73 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Domaine complet | 5379 | -18.29 | 58.51 | 33.87 | 7.62 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Lalla Chafia | 180 | -5.46 | 43.89 | 56.11 | 0.0 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Sidi Jabeur | 170 | -23.76 | 61.76 | 38.24 | 0.0 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Sebou amont | 227 | -1.76 | 55.07 | 44.93 | 0.0 |

---

## 3. Liste des Fichiers Produits

### Tables CSV :
- `paper1/tables/A1_lai_model_vs_modis.csv`
- `paper1/tables/A1_delta_lai_assimilation.csv`
- `paper1/tables/A1_et_partitioning_levels.csv`
- `paper1/tables/A1_et_partitioning_contrasts.csv`
- `paper1/tables/A1_wapor_et_comparison.csv`
- `paper1/tables/A1_wapor_direction_of_change.csv`

### Figures PNG :
- `paper1/figures/A1_lai_bias_map_2018.png`
- `paper1/figures/A1_delta_lai_monthly.png`
- `paper1/figures/A1_et_partitioning_contrasts.png`
- `paper1/figures/A1_wapor_direction_of_change.png`

### Scripts :
- `scripts/paper1/step_a1_vegetation_et_partition.py`
- `paper1/scripts/step_a1_vegetation_et_partition.py`

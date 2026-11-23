# Rapport d'Étape A1 — Végétation et partition de l'ET (H1)

Ce rapport présente les résultats quantitatifs de l'étape A1, sans interprétation subjective ni spéculation.
Tous les chiffres sont issus des scripts de post-traitement sur les sorties de simulation LIS et les observations MODIS LAI et WaPOR v3.

## 1. Méthodes d'Agrégation et Données

### 1.1 Grille et Masques
- **Grille LIS NorthMor** : 121 rangées × 181 colonnes (résolution 0,05°, domaine 30,0°N à 36,0°N, 10,0°O à 1,0°O).
- **Nombre total de mailles terrestres (LANDMASK=1)** : 16030 mailles.
- **Domaine hors classes 13 et 16** : 7563 mailles.
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
- **Ratio de partitionnement** : `ratio_T_over_ETcomb` calculé en ratio des moyennes (somme T / somme (E+T)).

---

## 2. Tableaux Récapitulatifs Factuels

### 2.1 Synthèse LAI Modèle vs MODIS en 2018 (Domaine et Bassins)

| experiment | substitut | region_or_class | lai_model_annual_mean | lai_modis_annual_mean | bias_annual | monthly_correlation | peak_month_model | peak_month_modis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | ENS_corr | Domaine complet | 0.6798 | 0.4256 | 0.2542 | 0.4897 | 6 | 4 |
| OL_DAIC | ENS_corr | Domaine hors classes 13 et 16 | 1.4409 | 0.5498 | 0.8912 | 0.4776 | 6 | 4 |
| OL_DAIC | ENS_corr | Lalla Chafia | 1.9909 | 0.7229 | 1.268 | 0.7722 | 5 | 4 |
| OL_DAIC | ENS_corr | Sidi Jabeur | 1.7195 | 0.5646 | 1.1549 | 0.5708 | 5 | 4 |
| OL_DAIC | ENS_corr | Sebou amont | 1.4408 | 0.3947 | 1.0461 | 0.8316 | 6 | 5 |
| ENS_OPL | aucun | Domaine complet | 0.6903 | 0.4256 | 0.2647 | 0.4819 | 6 | 4 |
| ENS_OPL | aucun | Domaine hors classes 13 et 16 | 1.4631 | 0.5498 | 0.9133 | 0.4689 | 6 | 4 |
| ENS_OPL | aucun | Lalla Chafia | 1.9961 | 0.7229 | 1.2732 | 0.7721 | 5 | 4 |
| ENS_OPL | aucun | Sidi Jabeur | 1.7346 | 0.5646 | 1.17 | 0.5763 | 5 | 4 |
| ENS_OPL | aucun | Sebou amont | 1.4217 | 0.3947 | 1.027 | 0.8369 | 6 | 5 |
| ENS_corr | aucun | Domaine complet | 0.6798 | 0.4256 | 0.2542 | 0.4897 | 6 | 4 |
| ENS_corr | aucun | Domaine hors classes 13 et 16 | 1.4409 | 0.5498 | 0.8912 | 0.4776 | 6 | 4 |
| ENS_corr | aucun | Lalla Chafia | 1.9909 | 0.7229 | 1.268 | 0.7722 | 5 | 4 |
| ENS_corr | aucun | Sidi Jabeur | 1.7195 | 0.5646 | 1.1549 | 0.5708 | 5 | 4 |
| ENS_corr | aucun | Sebou amont | 1.4408 | 0.3947 | 1.0461 | 0.8316 | 6 | 5 |
| DA_nocdf | aucun | Domaine complet | 0.5402 | 0.4256 | 0.1146 | 0.645 | 5 | 4 |
| DA_nocdf | aucun | Domaine hors classes 13 et 16 | 1.145 | 0.5498 | 0.5952 | 0.6353 | 5 | 4 |
| DA_nocdf | aucun | Lalla Chafia | 1.9842 | 0.7229 | 1.2613 | 0.8209 | 5 | 4 |
| DA_nocdf | aucun | Sidi Jabeur | 1.7439 | 0.5646 | 1.1793 | 0.6771 | 5 | 4 |
| DA_nocdf | aucun | Sebou amont | 0.9646 | 0.3947 | 0.5699 | 0.8852 | 6 | 5 |
| DA_nocdf_nowilt | aucun | Domaine complet | 0.5313 | 0.4256 | 0.1057 | 0.6618 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Domaine hors classes 13 et 16 | 1.1262 | 0.5498 | 0.5764 | 0.6526 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Lalla Chafia | 1.9693 | 0.7229 | 1.2464 | 0.8277 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Sidi Jabeur | 1.7358 | 0.5646 | 1.1711 | 0.6818 | 5 | 4 |
| DA_nocdf_nowilt | aucun | Sebou amont | 0.95 | 0.3947 | 0.5553 | 0.8893 | 6 | 5 |
| DA_corr | aucun | Domaine complet | 0.5187 | 0.4256 | 0.093 | 0.6086 | 5 | 4 |
| DA_corr | aucun | Domaine hors classes 13 et 16 | 1.0994 | 0.5498 | 0.5496 | 0.5959 | 5 | 4 |
| DA_corr | aucun | Lalla Chafia | 1.8367 | 0.7229 | 1.1138 | 0.8484 | 5 | 4 |
| DA_corr | aucun | Sidi Jabeur | 1.4309 | 0.5646 | 0.8662 | 0.7386 | 5 | 4 |
| DA_corr | aucun | Sebou amont | 1.0528 | 0.3947 | 0.6581 | 0.9231 | 6 | 5 |

### 2.2 ΔLAI dû à l'Assimilation en 2018 (Domaine et Bassins)

| contrast | region_or_class | delta_lai_annual_mean | delta_lai_m01 | delta_lai_m04 | delta_lai_m07 | delta_lai_m10 |
| --- | --- | --- | --- | --- | --- | --- |
| DA_nocdf − ENS_OPL | Domaine complet | -0.1501 | 0.0009 | -0.136 | -0.2627 | -0.1103 |
| DA_nocdf − ENS_OPL | Domaine hors classes 13 et 16 | -0.3181 | 0.002 | -0.2882 | -0.5568 | -0.2337 |
| DA_nocdf − ENS_OPL | Lalla Chafia | -0.0119 | 0.0193 | 0.0498 | -0.2562 | 0.0858 |
| DA_nocdf − ENS_OPL | Sidi Jabeur | 0.0093 | 0.0161 | 0.1758 | -0.1927 | -0.033 |
| DA_nocdf − ENS_OPL | Sebou amont | -0.4571 | 0.0008 | -0.1874 | -0.8082 | -0.5277 |
| DA_corr − ENS_corr | Domaine complet | -0.1612 | -0.0004 | -0.212 | -0.3186 | -0.0212 |
| DA_corr − ENS_corr | Domaine hors classes 13 et 16 | -0.3416 | -0.0009 | -0.4494 | -0.6753 | -0.0449 |
| DA_corr − ENS_corr | Lalla Chafia | -0.1541 | 0.0109 | -0.2089 | -0.634 | 0.2444 |
| DA_corr − ENS_corr | Sidi Jabeur | -0.2886 | 0.0112 | -0.1417 | -0.7051 | -0.1568 |
| DA_corr − ENS_corr | Sebou amont | -0.388 | 0.0003 | -0.1412 | -0.7692 | -0.346 |

### 2.3 Partition Annuelle de l'ET en 2018 (Domaine et Bassins)

| experiment | region_or_class | ESoil_mm | TVeg_mm | ECanop_mm | ET_total_mm | fraction_TVeg | fraction_ESoil | fraction_ECanop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | Domaine complet | 198.28 | 100.55 | 14.06 | 312.89 | 0.3213 | 0.6337 | 0.0449 |
| OL_DAIC | Domaine hors classes 13 et 16 | 203.02 | 213.12 | 29.81 | 445.94 | 0.4779 | 0.4553 | 0.0668 |
| OL_DAIC | Lalla Chafia | 255.11 | 309.52 | 42.91 | 607.54 | 0.5095 | 0.4199 | 0.0706 |
| OL_DAIC | Sidi Jabeur | 238.88 | 260.42 | 33.84 | 533.15 | 0.4885 | 0.4481 | 0.0635 |
| OL_DAIC | Sebou amont | 226.47 | 189.63 | 43.81 | 459.9 | 0.4123 | 0.4924 | 0.0953 |
| ENS_OPL | Domaine complet | 264.71 | 101.27 | 13.89 | 379.87 | 0.2666 | 0.6968 | 0.0366 |
| ENS_OPL | Domaine hors classes 13 et 16 | 263.82 | 214.64 | 29.44 | 507.9 | 0.4226 | 0.5194 | 0.058 |
| ENS_OPL | Lalla Chafia | 320.39 | 306.39 | 42.0 | 668.77 | 0.4581 | 0.4791 | 0.0628 |
| ENS_OPL | Sidi Jabeur | 309.19 | 258.82 | 33.19 | 601.2 | 0.4305 | 0.5143 | 0.0552 |
| ENS_OPL | Sebou amont | 283.0 | 187.72 | 42.06 | 512.77 | 0.3661 | 0.5519 | 0.082 |
| ENS_corr | Domaine complet | 197.96 | 99.87 | 13.87 | 311.7 | 0.3204 | 0.6351 | 0.0445 |
| ENS_corr | Domaine hors classes 13 et 16 | 202.91 | 211.67 | 29.4 | 443.99 | 0.4767 | 0.457 | 0.0662 |
| ENS_corr | Lalla Chafia | 254.5 | 307.24 | 42.31 | 604.05 | 0.5086 | 0.4213 | 0.07 |
| ENS_corr | Sidi Jabeur | 238.75 | 257.42 | 33.31 | 529.48 | 0.4862 | 0.4509 | 0.0629 |
| ENS_corr | Sebou amont | 226.47 | 188.45 | 43.21 | 458.13 | 0.4113 | 0.4943 | 0.0943 |
| DA_nocdf | Domaine complet | 182.63 | 75.14 | 11.59 | 269.35 | 0.279 | 0.678 | 0.043 |
| DA_nocdf | Domaine hors classes 13 et 16 | 212.27 | 159.25 | 24.56 | 396.09 | 0.4021 | 0.5359 | 0.062 |
| DA_nocdf | Lalla Chafia | 301.68 | 293.09 | 43.12 | 637.88 | 0.4595 | 0.4729 | 0.0676 |
| DA_nocdf | Sidi Jabeur | 269.67 | 252.44 | 34.02 | 556.12 | 0.4539 | 0.4849 | 0.0612 |
| DA_nocdf | Sebou amont | 213.19 | 118.76 | 31.91 | 363.87 | 0.3264 | 0.5859 | 0.0877 |
| DA_nocdf_nowilt | Domaine complet | 153.01 | 73.64 | 11.47 | 238.12 | 0.3093 | 0.6426 | 0.0482 |
| DA_nocdf_nowilt | Domaine hors classes 13 et 16 | 189.36 | 156.08 | 24.31 | 369.76 | 0.4221 | 0.5121 | 0.0658 |
| DA_nocdf_nowilt | Lalla Chafia | 282.43 | 290.14 | 42.94 | 615.51 | 0.4714 | 0.4589 | 0.0698 |
| DA_nocdf_nowilt | Sidi Jabeur | 258.34 | 250.62 | 33.92 | 542.88 | 0.4616 | 0.4759 | 0.0625 |
| DA_nocdf_nowilt | Sebou amont | 202.48 | 116.64 | 31.5 | 350.62 | 0.3327 | 0.5775 | 0.0898 |
| DA_corr | Domaine complet | 162.09 | 72.88 | 11.51 | 246.48 | 0.2957 | 0.6576 | 0.0467 |
| DA_corr | Domaine hors classes 13 et 16 | 193.36 | 154.47 | 24.4 | 372.23 | 0.415 | 0.5195 | 0.0656 |
| DA_corr | Lalla Chafia | 263.32 | 266.35 | 41.57 | 571.25 | 0.4663 | 0.461 | 0.0728 |
| DA_corr | Sidi Jabeur | 242.75 | 190.02 | 29.59 | 462.37 | 0.411 | 0.525 | 0.064 |
| DA_corr | Sebou amont | 223.06 | 132.57 | 34.01 | 389.64 | 0.3402 | 0.5725 | 0.0873 |

### 2.4 Contrastes Annuels C1, C2, C3, C4 Décomposés par Composante (2018)

| contrast_id | contrast_name | region_or_class | delta_ESoil_mm | delta_TVeg_mm | delta_ECanop_mm | delta_ET_total_mm |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | ENS_OPL − OL_DAIC | Domaine complet | 66.42 | 0.72 | -0.17 | 66.97 |
| C1 | ENS_OPL − OL_DAIC | Domaine hors classes 13 et 16 | 60.81 | 1.52 | -0.37 | 61.96 |
| C1 | ENS_OPL − OL_DAIC | Lalla Chafia | 65.28 | -3.13 | -0.91 | 61.23 |
| C1 | ENS_OPL − OL_DAIC | Sidi Jabeur | 70.31 | -1.61 | -0.65 | 68.05 |
| C1 | ENS_OPL − OL_DAIC | Sebou amont | 56.53 | -1.91 | -1.75 | 52.87 |
| C2 | DA_nocdf − ENS_OPL | Domaine complet | -82.08 | -26.13 | -2.3 | -110.51 |
| C2 | DA_nocdf − ENS_OPL | Domaine hors classes 13 et 16 | -51.55 | -55.39 | -4.88 | -111.82 |
| C2 | DA_nocdf − ENS_OPL | Lalla Chafia | -18.71 | -13.3 | 1.12 | -30.89 |
| C2 | DA_nocdf − ENS_OPL | Sidi Jabeur | -39.52 | -6.38 | 0.82 | -45.07 |
| C2 | DA_nocdf − ENS_OPL | Sebou amont | -69.81 | -68.95 | -10.15 | -148.9 |
| C3 | DA_corr − ENS_corr | Domaine complet | -35.87 | -26.99 | -2.36 | -65.22 |
| C3 | DA_corr − ENS_corr | Domaine hors classes 13 et 16 | -9.56 | -57.2 | -5.0 | -71.76 |
| C3 | DA_corr − ENS_corr | Lalla Chafia | 8.82 | -40.88 | -0.74 | -32.8 |
| C3 | DA_corr − ENS_corr | Sidi Jabeur | 4.0 | -67.4 | -3.71 | -67.11 |
| C3 | DA_corr − ENS_corr | Sebou amont | -3.41 | -55.88 | -9.21 | -68.5 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Domaine complet | -29.61 | -1.5 | -0.12 | -31.23 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Domaine hors classes 13 et 16 | -22.91 | -3.17 | -0.25 | -26.33 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Lalla Chafia | -19.25 | -2.94 | -0.18 | -22.37 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sidi Jabeur | -11.33 | -1.82 | -0.1 | -13.25 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sebou amont | -10.71 | -2.12 | -0.41 | -13.25 |

### 2.5 Comparaison Annuelle contre WaPOR v3 en 2018 (Domaine et Bassins)

| experiment | region_or_class | n_cells_valid | ESoil_model_mm | E_wapor_mm | bias_E_mm | TVeg_model_mm | T_wapor_mm | bias_T_mm | ETcomb_model_mm | ETcomb_wapor_mm | bias_ETcomb_mm | ratio_T_over_ETcomb_model | ratio_T_over_ETcomb_wapor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | Domaine complet | 5379 | 244.5 | 145.41 | 99.09 | 203.06 | 215.84 | -12.78 | 447.56 | 361.25 | 86.3 | 0.4537 | 0.5975 |
| OL_DAIC | Domaine hors classes 13 et 16 | 4229 | 232.22 | 150.62 | 81.59 | 258.28 | 259.83 | -1.55 | 490.49 | 410.45 | 80.04 | 0.5266 | 0.633 |
| OL_DAIC | Lalla Chafia | 180 | 255.11 | 153.15 | 101.96 | 309.52 | 328.65 | -19.13 | 564.63 | 481.8 | 82.83 | 0.5482 | 0.6821 |
| OL_DAIC | Sidi Jabeur | 170 | 238.88 | 151.4 | 87.48 | 260.42 | 252.49 | 7.93 | 499.31 | 403.89 | 95.41 | 0.5216 | 0.6251 |
| OL_DAIC | Sebou amont | 227 | 226.47 | 176.41 | 50.05 | 189.63 | 173.25 | 16.38 | 416.1 | 349.66 | 66.43 | 0.4557 | 0.4955 |
| ENS_OPL | Domaine complet | 5379 | 308.0 | 145.41 | 162.59 | 202.5 | 215.84 | -13.34 | 510.51 | 361.25 | 149.25 | 0.3967 | 0.5975 |
| ENS_OPL | Domaine hors classes 13 et 16 | 4229 | 293.0 | 150.62 | 142.38 | 257.57 | 259.83 | -2.26 | 550.57 | 410.45 | 140.12 | 0.4678 | 0.633 |
| ENS_OPL | Lalla Chafia | 180 | 320.39 | 153.15 | 167.24 | 306.39 | 328.65 | -22.26 | 626.77 | 481.8 | 144.97 | 0.4888 | 0.6821 |
| ENS_OPL | Sidi Jabeur | 170 | 309.19 | 151.4 | 157.79 | 258.82 | 252.49 | 6.33 | 568.01 | 403.89 | 164.11 | 0.4557 | 0.6251 |
| ENS_OPL | Sebou amont | 227 | 283.0 | 176.41 | 106.59 | 187.72 | 173.25 | 14.47 | 470.72 | 349.66 | 121.05 | 0.3988 | 0.4955 |
| ENS_corr | Domaine complet | 5379 | 244.05 | 145.41 | 98.64 | 201.66 | 215.84 | -14.18 | 445.71 | 361.25 | 84.46 | 0.4525 | 0.5975 |
| ENS_corr | Domaine hors classes 13 et 16 | 4229 | 231.92 | 150.62 | 81.3 | 256.5 | 259.83 | -3.33 | 488.42 | 410.45 | 77.97 | 0.5252 | 0.633 |
| ENS_corr | Lalla Chafia | 180 | 254.5 | 153.15 | 101.35 | 307.24 | 328.65 | -21.41 | 561.74 | 481.8 | 79.94 | 0.5469 | 0.6821 |
| ENS_corr | Sidi Jabeur | 170 | 238.75 | 151.4 | 87.35 | 257.42 | 252.49 | 4.93 | 496.17 | 403.89 | 92.28 | 0.5188 | 0.6251 |
| ENS_corr | Sebou amont | 227 | 226.47 | 176.41 | 50.06 | 188.45 | 173.25 | 15.2 | 414.92 | 349.66 | 65.26 | 0.4542 | 0.4955 |
| DA_nocdf | Domaine complet | 5379 | 229.97 | 145.41 | 84.56 | 159.74 | 215.84 | -56.1 | 389.72 | 361.25 | 28.46 | 0.4099 | 0.5975 |
| DA_nocdf | Domaine hors classes 13 et 16 | 4229 | 239.86 | 150.62 | 89.24 | 203.18 | 259.83 | -56.64 | 443.05 | 410.45 | 32.6 | 0.4586 | 0.633 |
| DA_nocdf | Lalla Chafia | 180 | 301.68 | 153.15 | 148.53 | 293.09 | 328.65 | -35.56 | 594.76 | 481.8 | 112.96 | 0.4928 | 0.6821 |
| DA_nocdf | Sidi Jabeur | 170 | 269.67 | 151.4 | 118.27 | 252.44 | 252.49 | -0.05 | 522.11 | 403.89 | 118.21 | 0.4835 | 0.6251 |
| DA_nocdf | Sebou amont | 227 | 213.19 | 176.41 | 36.78 | 118.76 | 173.25 | -54.49 | 331.96 | 349.66 | -17.71 | 0.3578 | 0.4955 |
| DA_nocdf_nowilt | Domaine complet | 5379 | 210.38 | 145.41 | 64.97 | 157.25 | 215.84 | -58.59 | 367.63 | 361.25 | 6.38 | 0.4277 | 0.5975 |
| DA_nocdf_nowilt | Domaine hors classes 13 et 16 | 4229 | 217.24 | 150.62 | 66.62 | 200.01 | 259.83 | -59.81 | 417.25 | 410.45 | 6.8 | 0.4794 | 0.633 |
| DA_nocdf_nowilt | Lalla Chafia | 180 | 282.43 | 153.15 | 129.28 | 290.14 | 328.65 | -38.51 | 572.57 | 481.8 | 90.77 | 0.5067 | 0.6821 |
| DA_nocdf_nowilt | Sidi Jabeur | 170 | 258.34 | 151.4 | 106.94 | 250.62 | 252.49 | -1.87 | 508.96 | 403.89 | 105.06 | 0.4924 | 0.6251 |
| DA_nocdf_nowilt | Sebou amont | 227 | 202.48 | 176.41 | 26.07 | 116.64 | 173.25 | -56.61 | 319.12 | 349.66 | -30.55 | 0.3655 | 0.4955 |
| DA_corr | Domaine complet | 5379 | 220.12 | 145.41 | 74.71 | 154.47 | 215.84 | -61.37 | 374.59 | 361.25 | 13.34 | 0.4124 | 0.5975 |
| DA_corr | Domaine hors classes 13 et 16 | 4229 | 222.1 | 150.62 | 71.47 | 196.47 | 259.83 | -63.35 | 418.57 | 410.45 | 8.12 | 0.4694 | 0.633 |
| DA_corr | Lalla Chafia | 180 | 263.32 | 153.15 | 110.17 | 266.35 | 328.65 | -62.3 | 529.68 | 481.8 | 47.88 | 0.5029 | 0.6821 |
| DA_corr | Sidi Jabeur | 170 | 242.75 | 151.4 | 91.35 | 190.02 | 252.49 | -62.47 | 432.77 | 403.89 | 28.88 | 0.4391 | 0.6251 |
| DA_corr | Sebou amont | 227 | 223.06 | 176.41 | 46.64 | 132.57 | 173.25 | -40.68 | 355.63 | 349.66 | 5.97 | 0.3728 | 0.4955 |

### 2.6 Direction de Changement pour C2 et C3 contre WaPOR v3 en 2018

| contrast_id | contrast_name | component | region_or_class | n_cells_valid | delta_abs_bias_mm | pct_cells_closer | pct_cells_farther | pct_cells_neutral |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Domaine complet | 5379 | -72.14 | 77.91 | 22.01 | 0.07 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Domaine hors classes 13 et 16 | 4229 | -46.5 | 73.49 | 26.51 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Lalla Chafia | 180 | -18.71 | 51.67 | 48.33 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Sidi Jabeur | 170 | -39.52 | 81.76 | 18.24 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E (ESoil vs WaPOR E) | Sebou amont | 227 | -53.49 | 81.06 | 18.94 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Domaine complet | 5379 | 16.76 | 31.68 | 46.94 | 21.38 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Domaine hors classes 13 et 16 | 4229 | 21.32 | 40.29 | 59.71 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Lalla Chafia | 180 | 16.75 | 45.0 | 55.0 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Sidi Jabeur | 170 | 5.83 | 44.71 | 50.59 | 4.71 |
| C2 | DA_nocdf − ENS_OPL | T (TVeg vs WaPOR T) | Sebou amont | 227 | 13.14 | 44.93 | 49.34 | 5.73 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Domaine complet | 5379 | -65.08 | 68.34 | 31.51 | 0.15 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Domaine hors classes 13 et 16 | 4229 | -45.36 | 62.8 | 37.2 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Lalla Chafia | 180 | -18.57 | 45.56 | 54.44 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Sidi Jabeur | 170 | -30.02 | 68.24 | 31.76 | 0.0 |
| C2 | DA_nocdf − ENS_OPL | E+T (ESoil+TVeg vs WaPOR E+T) | Sebou amont | 227 | -48.44 | 72.25 | 27.75 | 0.0 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Domaine complet | 5379 | -23.5 | 64.64 | 27.76 | 7.6 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Domaine hors classes 13 et 16 | 4229 | -9.34 | 56.99 | 34.83 | 8.18 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Lalla Chafia | 180 | 8.82 | 25.0 | 75.0 | 0.0 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Sidi Jabeur | 170 | 4.0 | 33.53 | 66.47 | 0.0 |
| C3 | DA_corr − ENS_corr | E (ESoil vs WaPOR E) | Sebou amont | 227 | -0.3 | 44.93 | 55.07 | 0.0 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Domaine complet | 5379 | 36.73 | 24.0 | 48.19 | 27.81 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Domaine hors classes 13 et 16 | 4229 | 46.72 | 30.53 | 61.29 | 8.18 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Lalla Chafia | 180 | 44.46 | 29.44 | 70.56 | 0.0 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Sidi Jabeur | 170 | 23.8 | 39.41 | 55.88 | 4.71 |
| C3 | DA_corr − ENS_corr | T (TVeg vs WaPOR T) | Sebou amont | 227 | 32.82 | 36.56 | 57.71 | 5.73 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Domaine complet | 5379 | -18.15 | 58.47 | 33.91 | 7.62 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Domaine hors classes 13 et 16 | 4229 | -7.16 | 51.22 | 40.58 | 8.21 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Lalla Chafia | 180 | -5.94 | 45.0 | 55.0 | 0.0 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Sidi Jabeur | 170 | -24.25 | 61.18 | 38.82 | 0.0 |
| C3 | DA_corr − ENS_corr | E+T (ESoil+TVeg vs WaPOR E+T) | Sebou amont | 227 | -1.25 | 55.07 | 44.93 | 0.0 |

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
- `scripts/paper1/generate_report_a1.py`

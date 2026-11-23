# Rapport d'Étape A1b — Diagnostic par Couche et Corrections A1 (2018)

Ce rapport présente strictement les tableaux générés par script depuis les sorties brutes et les tables de l'étape A1b.
Conformément aux consignes, aucun chiffre n'est tapé à la main et le rapport ne comporte aucune phrase d'interprétation.

## 1. Diagnostic par Couche d'Humidité du Sol (2018)

Épaisseurs des couches : L1 = 100 mm (0–0,1 m), L2 = 300 mm (0,1–0,4 m), L3 = 600 mm (0,4–1,0 m), L4 = 1 000 mm (1,0–2,0 m).
Stock d'eau : $\Delta\text{Stock}_k = \Delta\theta_k \times \Delta z_k$. $\Delta\text{BTRAN}$ est noté `absent` car non archivé en sortie.

### 1.1 Contrastes Annuels C1, C2, C3, C4 par Couche (Domaine et Bassins)

| contrast_id | contrast_name | region | n_cells | delta_theta_L1_m3m3 | delta_theta_L2_m3m3 | delta_theta_L3_m3m3 | delta_theta_L4_m3m3 | delta_stock_total_mm | delta_BTRAN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | ENS_OPL − OL_DAIC | Domaine complet | 16030 | 0.00045 | 0.00016 | 6e-05 | -6e-05 | 0.07 | absent |
| C1 | ENS_OPL − OL_DAIC | Domaine hors classes 13 et 16 | 7563 | 0.0 | 0.00015 | 1e-05 | -0.00019 | -0.14 | absent |
| C1 | ENS_OPL − OL_DAIC | Lalla Chafia | 180 | -0.00024 | -4e-05 | -0.00047 | -0.00023 | -0.55 | absent |
| C1 | ENS_OPL − OL_DAIC | Sidi Jabeur | 170 | -0.00018 | -1e-05 | -0.00029 | -0.00042 | -0.62 | absent |
| C1 | ENS_OPL − OL_DAIC | Sebou amont | 227 | -0.001 | -0.00018 | -4e-05 | -8e-05 | -0.26 | absent |
| C2 | DA_nocdf − ENS_OPL | Domaine complet | 16030 | -0.02166 | -0.01881 | -0.01482 | -0.00919 | -25.89 | absent |
| C2 | DA_nocdf − ENS_OPL | Domaine hors classes 13 et 16 | 7563 | -0.01487 | -0.01516 | -0.01574 | -0.00993 | -25.41 | absent |
| C2 | DA_nocdf − ENS_OPL | Lalla Chafia | 180 | -0.00238 | 0.00174 | 0.00139 | 0.00048 | 1.6 | absent |
| C2 | DA_nocdf − ENS_OPL | Sidi Jabeur | 170 | -0.00647 | 0.00145 | 0.00438 | 0.00291 | 5.32 | absent |
| C2 | DA_nocdf − ENS_OPL | Sebou amont | 227 | -0.0182 | -0.01674 | -0.01838 | -0.00873 | -26.6 | absent |
| C3 | DA_corr − ENS_corr | Domaine complet | 16030 | -0.01412 | -0.02767 | -0.04023 | -0.03362 | -67.47 | absent |
| C3 | DA_corr − ENS_corr | Domaine hors classes 13 et 16 | 7563 | -0.0064 | -0.00872 | -0.03167 | -0.0332 | -55.46 | absent |
| C3 | DA_corr − ENS_corr | Lalla Chafia | 180 | -0.0007 | 0.0023 | -0.01224 | -0.03161 | -38.33 | absent |
| C3 | DA_corr − ENS_corr | Sidi Jabeur | 170 | -0.00252 | -0.00478 | -0.0205 | -0.07838 | -92.36 | absent |
| C3 | DA_corr − ENS_corr | Sebou amont | 227 | -0.00596 | -0.00845 | -0.03038 | -0.02018 | -41.54 | absent |
| C4 | DA_nocdf_nowilt − DA_nocdf | Domaine complet | 16030 | -0.01052 | -0.00058 | 0.00054 | 6e-05 | -0.84 | absent |
| C4 | DA_nocdf_nowilt − DA_nocdf | Domaine hors classes 13 et 16 | 7563 | -0.00749 | -0.00169 | 0.00046 | -6e-05 | -1.04 | absent |
| C4 | DA_nocdf_nowilt − DA_nocdf | Lalla Chafia | 180 | -0.00694 | 0.00029 | 0.00024 | -0.00048 | -0.95 | absent |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sidi Jabeur | 170 | -0.00375 | 0.00016 | 0.00041 | 6e-05 | -0.01 | absent |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sebou amont | 227 | -0.00268 | -0.00038 | -0.00016 | -0.0001 | -0.57 | absent |

### 1.2 Contrastes Saisonniers par Couche pour C2 et C3 (Domaine complet et Domaine hors 13/16)

| contrast_id | season | region | delta_stock_L1_mm | delta_stock_L2_mm | delta_stock_L3_mm | delta_stock_L4_mm | delta_stock_total_mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C2 | JF+D_2018 | Domaine complet | -3.01 | -3.97 | -6.25 | -4.75 | -17.97 |
| C2 | JF+D_2018 | Domaine hors classes 13 et 16 | -1.92 | -2.77 | -5.83 | -2.52 | -13.03 |
| C2 | MAM | Domaine complet | -2.93 | -6.44 | -11.38 | -8.58 | -29.33 |
| C2 | MAM | Domaine hors classes 13 et 16 | -2.88 | -7.84 | -16.55 | -11.29 | -38.56 |
| C2 | JJA | Domaine complet | -0.17 | -4.97 | -8.71 | -11.41 | -25.26 |
| C2 | JJA | Domaine hors classes 13 et 16 | -0.11 | -4.01 | -10.18 | -14.22 | -28.52 |
| C2 | SON | Domaine complet | -2.56 | -7.2 | -9.22 | -12.04 | -31.02 |
| C2 | SON | Domaine hors classes 13 et 16 | -1.04 | -3.57 | -5.22 | -11.67 | -21.51 |
| C2 | Annuel | Domaine complet | -2.17 | -5.64 | -8.89 | -9.19 | -25.89 |
| C2 | Annuel | Domaine hors classes 13 et 16 | -1.49 | -4.55 | -9.44 | -9.93 | -25.41 |
| C3 | JF+D_2018 | Domaine complet | -2.06 | -6.18 | -19.72 | -24.18 | -52.14 |
| C3 | JF+D_2018 | Domaine hors classes 13 et 16 | -0.91 | -3.51 | -15.5 | -16.61 | -36.53 |
| C3 | MAM | Domaine complet | -1.92 | -8.83 | -22.48 | -23.83 | -57.06 |
| C3 | MAM | Domaine hors classes 13 et 16 | -1.38 | -6.68 | -30.1 | -32.41 | -70.58 |
| C3 | JJA | Domaine complet | -0.31 | -8.13 | -21.16 | -33.34 | -62.93 |
| C3 | JJA | Domaine hors classes 13 et 16 | -0.15 | -0.2 | -18.0 | -43.22 | -61.57 |
| C3 | SON | Domaine complet | -1.36 | -10.07 | -33.19 | -53.11 | -97.73 |
| C3 | SON | Domaine hors classes 13 et 16 | -0.13 | -0.08 | -12.41 | -40.57 | -53.19 |
| C3 | Annuel | Domaine complet | -1.41 | -8.3 | -24.14 | -33.62 | -67.47 |
| C3 | Annuel | Domaine hors classes 13 et 16 | -0.64 | -2.62 | -19.0 | -33.2 | -55.46 |

---

## 2. Corrélations Spatiales pour C3 (MAM et JJA 2018)

Corrélations de Pearson spatiales sur les mailles de chaque région entre $\Delta\text{TVeg}$ et $\Delta\theta$ de chaque couche, et entre $\Delta\text{TVeg}$ et $\Delta\text{LAI}$.

| season | region | n_cells | corr_delta_tveg_vs_delta_theta_L1 | corr_delta_tveg_vs_delta_theta_L2 | corr_delta_tveg_vs_delta_theta_L3 | corr_delta_tveg_vs_delta_theta_L4 | corr_delta_tveg_vs_delta_lai |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MAM | Domaine complet | 16030 | 0.254 | 0.1181 | 0.6931 | 0.4276 | 0.9687 |
| MAM | Domaine hors classes 13 et 16 | 7563 | 0.7714 | 0.4697 | 0.8563 | 0.5109 | 0.9609 |
| MAM | Lalla Chafia | 180 | 0.9648 | 0.9747 | 0.9943 | 0.6542 | 0.9793 |
| MAM | Sidi Jabeur | 170 | 0.8496 | 0.9047 | 0.9508 | 0.5082 | 0.9562 |
| MAM | Sebou amont | 227 | 0.9353 | 0.8989 | 0.896 | 0.4888 | 0.9797 |
| JJA | Domaine complet | 16030 | 0.3359 | -0.0293 | 0.4487 | 0.4638 | 0.9139 |
| JJA | Domaine hors classes 13 et 16 | 7563 | 0.6678 | 0.3603 | 0.7618 | 0.55 | 0.8988 |
| JJA | Lalla Chafia | 180 | 0.6255 | 0.3787 | 0.9298 | 0.7359 | 0.9429 |
| JJA | Sidi Jabeur | 170 | 0.1486 | 0.1271 | 0.8059 | 0.5075 | 0.9259 |
| JJA | Sebou amont | 227 | 0.715 | 0.4263 | 0.8581 | 0.3204 | 0.9686 |

---

## 3. Synthèse des Tables Mises à Jour avec Corrections

### 3.1 Comparaison Annuelle contre WaPOR v3 (ratio des moyennes = somme T / somme (E+T))

| experiment | region_or_class | n_cells_valid | ESoil_model_mm | E_wapor_mm | bias_E_mm | TVeg_model_mm | T_wapor_mm | bias_T_mm | ratio_T_over_ETcomb_model | ratio_T_over_ETcomb_wapor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | Domaine complet | 5379 | 244.5 | 145.41 | 99.09 | 203.06 | 215.84 | -12.78 | 0.4537 | 0.5975 |
| OL_DAIC | Domaine hors classes 13 et 16 | 4229 | 232.22 | 150.62 | 81.59 | 258.28 | 259.83 | -1.55 | 0.5266 | 0.633 |
| OL_DAIC | Lalla Chafia | 180 | 255.11 | 153.15 | 101.96 | 309.52 | 328.65 | -19.13 | 0.5482 | 0.6821 |
| OL_DAIC | Sidi Jabeur | 170 | 238.88 | 151.4 | 87.48 | 260.42 | 252.49 | 7.93 | 0.5216 | 0.6251 |
| OL_DAIC | Sebou amont | 227 | 226.47 | 176.41 | 50.05 | 189.63 | 173.25 | 16.38 | 0.4557 | 0.4955 |
| ENS_OPL | Domaine complet | 5379 | 308.0 | 145.41 | 162.59 | 202.5 | 215.84 | -13.34 | 0.3967 | 0.5975 |
| ENS_OPL | Domaine hors classes 13 et 16 | 4229 | 293.0 | 150.62 | 142.38 | 257.57 | 259.83 | -2.26 | 0.4678 | 0.633 |
| ENS_OPL | Lalla Chafia | 180 | 320.39 | 153.15 | 167.24 | 306.39 | 328.65 | -22.26 | 0.4888 | 0.6821 |
| ENS_OPL | Sidi Jabeur | 170 | 309.19 | 151.4 | 157.79 | 258.82 | 252.49 | 6.33 | 0.4557 | 0.6251 |
| ENS_OPL | Sebou amont | 227 | 283.0 | 176.41 | 106.59 | 187.72 | 173.25 | 14.47 | 0.3988 | 0.4955 |
| ENS_corr | Domaine complet | 5379 | 244.05 | 145.41 | 98.64 | 201.66 | 215.84 | -14.18 | 0.4525 | 0.5975 |
| ENS_corr | Domaine hors classes 13 et 16 | 4229 | 231.92 | 150.62 | 81.3 | 256.5 | 259.83 | -3.33 | 0.5252 | 0.633 |
| ENS_corr | Lalla Chafia | 180 | 254.5 | 153.15 | 101.35 | 307.24 | 328.65 | -21.41 | 0.5469 | 0.6821 |
| ENS_corr | Sidi Jabeur | 170 | 238.75 | 151.4 | 87.35 | 257.42 | 252.49 | 4.93 | 0.5188 | 0.6251 |
| ENS_corr | Sebou amont | 227 | 226.47 | 176.41 | 50.06 | 188.45 | 173.25 | 15.2 | 0.4542 | 0.4955 |
| DA_nocdf | Domaine complet | 5379 | 229.97 | 145.41 | 84.56 | 159.74 | 215.84 | -56.1 | 0.4099 | 0.5975 |
| DA_nocdf | Domaine hors classes 13 et 16 | 4229 | 239.86 | 150.62 | 89.24 | 203.18 | 259.83 | -56.64 | 0.4586 | 0.633 |
| DA_nocdf | Lalla Chafia | 180 | 301.68 | 153.15 | 148.53 | 293.09 | 328.65 | -35.56 | 0.4928 | 0.6821 |
| DA_nocdf | Sidi Jabeur | 170 | 269.67 | 151.4 | 118.27 | 252.44 | 252.49 | -0.05 | 0.4835 | 0.6251 |
| DA_nocdf | Sebou amont | 227 | 213.19 | 176.41 | 36.78 | 118.76 | 173.25 | -54.49 | 0.3578 | 0.4955 |
| DA_nocdf_nowilt | Domaine complet | 5379 | 210.38 | 145.41 | 64.97 | 157.25 | 215.84 | -58.59 | 0.4277 | 0.5975 |
| DA_nocdf_nowilt | Domaine hors classes 13 et 16 | 4229 | 217.24 | 150.62 | 66.62 | 200.01 | 259.83 | -59.81 | 0.4794 | 0.633 |
| DA_nocdf_nowilt | Lalla Chafia | 180 | 282.43 | 153.15 | 129.28 | 290.14 | 328.65 | -38.51 | 0.5067 | 0.6821 |
| DA_nocdf_nowilt | Sidi Jabeur | 170 | 258.34 | 151.4 | 106.94 | 250.62 | 252.49 | -1.87 | 0.4924 | 0.6251 |
| DA_nocdf_nowilt | Sebou amont | 227 | 202.48 | 176.41 | 26.07 | 116.64 | 173.25 | -56.61 | 0.3655 | 0.4955 |
| DA_corr | Domaine complet | 5379 | 220.12 | 145.41 | 74.71 | 154.47 | 215.84 | -61.37 | 0.4124 | 0.5975 |
| DA_corr | Domaine hors classes 13 et 16 | 4229 | 222.1 | 150.62 | 71.47 | 196.47 | 259.83 | -63.35 | 0.4694 | 0.633 |
| DA_corr | Lalla Chafia | 180 | 263.32 | 153.15 | 110.17 | 266.35 | 328.65 | -62.3 | 0.5029 | 0.6821 |
| DA_corr | Sidi Jabeur | 170 | 242.75 | 151.4 | 91.35 | 190.02 | 252.49 | -62.47 | 0.4391 | 0.6251 |
| DA_corr | Sebou amont | 227 | 223.06 | 176.41 | 46.64 | 132.57 | 173.25 | -40.68 | 0.3728 | 0.4955 |

### 3.2 Direction de Changement pour C2 et C3 contre WaPOR v3

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

### 3.3 Partition Annuelle de l'ET en 2018 (avec Domaine hors classes 13 et 16)

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

---

## 4. Liste des Fichiers Produits

### Tables CSV :
- `paper1/tables/A1b_soil_moisture_layers_diagnostic.csv`
- `paper1/tables/A1b_c3_spatial_correlations.csv`
- `paper1/tables/A1b_lai_model_vs_modis.csv`
- `paper1/tables/A1b_delta_lai_assimilation.csv`
- `paper1/tables/A1b_et_partitioning_levels.csv`
- `paper1/tables/A1b_et_partitioning_contrasts.csv`
- `paper1/tables/A1b_wapor_et_comparison.csv`
- `paper1/tables/A1b_wapor_direction_of_change.csv`

### Figures PNG :
- `paper1/figures/A1b_lai_control_modis_vs_ens_corr_2018.png`

### Scripts :
- `scripts/paper1/step_a1b_corrections_and_layer_diagnostic.py`
- `paper1/scripts/step_a1b_corrections_and_layer_diagnostic.py`

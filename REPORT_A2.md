# Rapport d'Étape A2 — Du sol au débit (H6/H7)

Ce rapport présente strictement les tableaux générés par script depuis les sorties brutes et les tables de l'étape A2 (mis à jour en étape A2b).
Conformément aux consignes, aucun chiffre n'est tapé à la main et le rapport ne comporte aucune phrase d'interprétation.

## 1. Partition Annuelle des Écoulements et Bilan Hydrique (2018)

### 1.1 Totaux Annuels par Expérience et par Région

| experiment | region | n_cells | P_mm | Qs_mm | Qsb_mm | TotalRunoff_mm | ET_mm | coeff_TotalRunoff_over_P | Delta_S_sol_mm | Delta_GWS_mm | Delta_S_total_mm | WaterBalance_Residual_mm | ctrl_validated_domain_residual_mm | diff_validated_domain_residual_mm | ctrl_TotalRunoff_upstream_cb_mm | diff_TotalRunoff_vs_upstream_cb_mm | ctrl_ET_upstream_cb_mm | diff_ET_vs_upstream_cb_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OL_DAIC | Domaine complet | 16030 | 379.39 | 12.46 | 18.67 | 31.13 | 313.35 | 0.082 | 39.06 | 0.5 | 39.49 | -4.576 | -4.5755 | -0.0005 | absent | absent | absent | absent |
| OL_DAIC | Lalla Chafia | 133 | 762.54 | 32.52 | 94.35 | 126.87 | 610.61 | 0.1664 | 20.99 | 5.13 | 26.12 | -1.0459 | N/A | N/A | 126.8704 | -0.0001 | 609.7064 | 0.8988 |
| OL_DAIC | Sidi Jabeur | 121 | 637.39 | 20.02 | 41.35 | 61.37 | 535.83 | 0.0963 | 35.58 | 4.98 | 40.55 | -0.3565 | N/A | N/A | 61.3692 | -0.0 | 535.1805 | 0.6476 |
| OL_DAIC | Sebou amont | 182 | 576.56 | 8.65 | 8.95 | 17.6 | 462.85 | 0.0305 | 101.27 | -1.67 | 99.6 | -3.4891 | N/A | N/A | absent | absent | absent | absent |
| ENS_OPL | Domaine complet | 16030 | 380.33 | 12.96 | 22.07 | 35.03 | 380.36 | 0.0921 | 38.94 | 2.43 | 41.3 | -76.3593 | -76.3588 | -0.0005 | absent | absent | absent | absent |
| ENS_OPL | Lalla Chafia | 133 | 764.31 | 35.08 | 113.18 | 148.26 | 670.61 | 0.194 | 20.02 | 7.75 | 27.76 | -82.3119 | N/A | N/A | 148.2559 | 0.0001 | 666.5632 | 4.0424 |
| ENS_OPL | Sidi Jabeur | 121 | 639.25 | 22.03 | 54.93 | 76.96 | 605.0 | 0.1204 | 35.02 | 8.05 | 43.06 | -85.7594 | N/A | N/A | 76.9612 | 0.0001 | 601.4656 | 3.5299 |
| ENS_OPL | Sebou amont | 182 | 577.97 | 8.67 | 9.73 | 18.4 | 518.43 | 0.0318 | 101.62 | 1.67 | 103.29 | -62.1451 | N/A | N/A | absent | absent | absent | absent |
| ENS_corr | Domaine complet | 16030 | 378.65 | 12.56 | 19.39 | 31.95 | 312.15 | 0.0844 | 38.77 | 0.41 | 39.12 | -4.5672 | -4.5673 | 0.0001 | absent | absent | absent | absent |
| ENS_corr | Lalla Chafia | 133 | 761.15 | 33.12 | 97.64 | 130.77 | 607.06 | 0.1718 | 20.55 | 3.69 | 24.23 | -0.8985 | N/A | N/A | 130.7679 | 0.0001 | 606.0714 | 0.9864 |
| ENS_corr | Sidi Jabeur | 121 | 636.24 | 20.67 | 45.2 | 65.88 | 532.06 | 0.1035 | 34.89 | 3.93 | 38.81 | -0.5036 | N/A | N/A | 65.8756 | -0.0001 | 531.3764 | 0.6798 |
| ENS_corr | Sebou amont | 182 | 575.31 | 8.58 | 8.86 | 17.44 | 461.08 | 0.0303 | 101.5 | -1.29 | 100.2 | -3.4097 | N/A | N/A | absent | absent | absent | absent |
| DA_nocdf | Domaine complet | 16030 | 380.33 | 13.99 | 33.9 | 47.89 | 269.8 | 0.1259 | -4.85 | 4.51 | -0.4 | 63.0477 | 63.0479 | -0.0002 | absent | absent | absent | absent |
| DA_nocdf | Lalla Chafia | 133 | 764.3 | 53.5 | 286.64 | 340.13 | 650.19 | 0.445 | 36.43 | 47.21 | 83.63 | -309.6549 | N/A | N/A | 340.1337 | -0.0001 | 650.186 | -0.0001 |
| DA_nocdf | Sidi Jabeur | 121 | 639.25 | 32.19 | 157.71 | 189.9 | 568.22 | 0.2971 | 54.89 | 40.16 | 95.04 | -213.9095 | N/A | N/A | 189.8978 | -0.0 | 568.2169 | -0.0001 |
| DA_nocdf | Sebou amont | 182 | 577.97 | 9.84 | 22.3 | 32.14 | 365.01 | 0.0556 | 46.33 | 6.77 | 53.1 | 127.7172 | N/A | N/A | absent | absent | absent | absent |
| DA_nocdf_nowilt | Domaine complet | 16030 | 380.33 | 14.0 | 33.9 | 47.9 | 238.57 | 0.126 | -5.2 | 4.51 | -0.74 | 94.6059 | 94.6055 | 0.0004 | absent | absent | absent | absent |
| DA_nocdf_nowilt | Lalla Chafia | 133 | 764.31 | 53.58 | 287.85 | 341.43 | 629.44 | 0.4467 | 34.09 | 47.42 | 81.5 | -288.0576 | N/A | N/A | 341.4325 | 0.0001 | 626.1118 | 3.325 |
| DA_nocdf_nowilt | Sidi Jabeur | 121 | 639.25 | 32.16 | 157.28 | 189.44 | 556.34 | 0.2963 | 55.49 | 39.58 | 95.07 | -201.5907 | N/A | N/A | 189.4387 | 0.0 | 553.6078 | 2.7327 |
| DA_nocdf_nowilt | Sebou amont | 182 | 577.97 | 9.83 | 22.71 | 32.54 | 351.48 | 0.0563 | 46.26 | 6.89 | 53.14 | 140.8077 | N/A | N/A | absent | absent | absent | absent |
| DA_corr | Domaine complet | 16030 | 378.65 | 14.48 | 48.59 | 63.08 | 246.91 | 0.1666 | -98.63 | 14.96 | -83.73 | 152.3898 | 152.3902 | -0.0004 | absent | absent | absent | absent |
| DA_corr | Lalla Chafia | 133 | 761.15 | 49.1 | 266.92 | 316.03 | 582.56 | 0.4152 | -10.91 | 41.69 | 30.76 | -168.1924 | N/A | N/A | 316.0256 | 0.0001 | 581.4484 | 1.108 |
| DA_corr | Sidi Jabeur | 121 | 636.24 | 33.93 | 186.91 | 220.84 | 466.53 | 0.3471 | -63.89 | 23.95 | -39.95 | -11.1787 | N/A | N/A | 220.8369 | -0.0001 | 465.8293 | 0.7054 |
| DA_corr | Sebou amont | 182 | 575.31 | 11.73 | 39.67 | 51.4 | 385.95 | 0.0893 | -28.64 | 19.62 | -9.02 | 146.978 | N/A | N/A | absent | absent | absent | absent |

### 1.2 Contrastes Annuels C1, C2, C3, C4 de Partition des Écoulements

| contrast_id | contrast_name | region | delta_P_mm | delta_Qs_mm | delta_Qsb_mm | delta_TotalRunoff_mm | delta_ET_mm | delta_Delta_S_sol_mm | delta_Delta_GWS_mm | delta_Delta_S_total_mm | delta_coeff_TotalRunoff_over_P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | ENS_OPL − OL_DAIC | Domaine complet | 0.94 | 0.5 | 3.4 | 3.9 | 67.01 | -0.12 | 1.93 | 1.81 | 0.0101 |
| C1 | ENS_OPL − OL_DAIC | Lalla Chafia | 1.77 | 2.56 | 18.83 | 21.39 | 60.0 | -0.97 | 2.62 | 1.64 | 0.0276 |
| C1 | ENS_OPL − OL_DAIC | Sidi Jabeur | 1.86 | 2.01 | 13.58 | 15.59 | 69.17 | -0.56 | 3.07 | 2.51 | 0.0241 |
| C1 | ENS_OPL − OL_DAIC | Sebou amont | 1.41 | 0.02 | 0.78 | 0.8 | 55.58 | 0.35 | 3.34 | 3.69 | 0.0013 |
| C2 | DA_nocdf − ENS_OPL | Domaine complet | 0.0 | 1.03 | 11.83 | 12.86 | -110.56 | -43.79 | 2.08 | -41.7 | 0.0338 |
| C2 | DA_nocdf − ENS_OPL | Lalla Chafia | -0.01 | 18.42 | 173.46 | 191.87 | -20.42 | 16.41 | 39.46 | 55.87 | 0.251 |
| C2 | DA_nocdf − ENS_OPL | Sidi Jabeur | 0.0 | 10.16 | 102.78 | 112.94 | -36.78 | 19.87 | 32.11 | 51.98 | 0.1767 |
| C2 | DA_nocdf − ENS_OPL | Sebou amont | 0.0 | 1.17 | 12.57 | 13.74 | -153.42 | -55.29 | 5.1 | -50.19 | 0.0238 |
| C3 | DA_corr − ENS_corr | Domaine complet | 0.0 | 1.92 | 29.2 | 31.13 | -65.24 | -137.4 | 14.55 | -122.85 | 0.0822 |
| C3 | DA_corr − ENS_corr | Lalla Chafia | 0.0 | 15.98 | 169.28 | 185.26 | -24.5 | -31.46 | 38.0 | 6.53 | 0.2434 |
| C3 | DA_corr − ENS_corr | Sidi Jabeur | 0.0 | 13.26 | 141.71 | 154.96 | -65.53 | -98.78 | 20.02 | -78.76 | 0.2436 |
| C3 | DA_corr − ENS_corr | Sebou amont | 0.0 | 3.15 | 30.81 | 33.96 | -75.13 | -130.14 | 20.91 | -109.22 | 0.059 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Domaine complet | 0.0 | 0.01 | 0.0 | 0.01 | -31.23 | -0.35 | 0.0 | -0.34 | 0.0001 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Lalla Chafia | 0.01 | 0.08 | 1.21 | 1.3 | -20.75 | -2.34 | 0.21 | -2.13 | 0.0017 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sidi Jabeur | 0.0 | -0.03 | -0.43 | -0.46 | -11.88 | 0.6 | -0.58 | 0.03 | -0.0008 |
| C4 | DA_nocdf_nowilt − DA_nocdf | Sebou amont | 0.0 | -0.01 | 0.41 | 0.4 | -13.53 | -0.07 | 0.12 | 0.04 | 0.0007 |

---

## 2. Événements de Pluie et Réponse Hydrologique (2018)

### 2.1 Synthèse des Événements et Ruissellement Cumulé J0→J+5

| basin | event_id | start_date | end_date | duration_days | P_event_mm | experiment | stock_total_eve_mm | Qs_cum_j0_j5_mm | Qsb_cum_j0_j5_mm | TotalRunoff_cum_j0_j5_mm | runoff_coeff_Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | EV01 | 2018-01-08 | 2018-01-08 | 1 | absent | OL_DAIC | 484.67 | 1.36 | 0.61 | 1.98 | absent |
| Lalla Chafia | EV01 | 2018-01-08 | 2018-01-08 | 1 | 31.31 | ENS_OPL | 484.59 | 1.45 | 0.86 | 2.31 | 0.0739 |
| Lalla Chafia | EV01 | 2018-01-08 | 2018-01-08 | 1 | 31.11 | ENS_corr | 484.04 | 1.44 | 0.85 | 2.29 | 0.0737 |
| Lalla Chafia | EV01 | 2018-01-08 | 2018-01-08 | 1 | 31.31 | DA_nocdf | 493.01 | 1.49 | 1.08 | 2.57 | 0.0822 |
| Lalla Chafia | EV01 | 2018-01-08 | 2018-01-08 | 1 | 31.31 | DA_nocdf_nowilt | 493.01 | 1.49 | 1.08 | 2.57 | 0.0822 |
| Lalla Chafia | EV01 | 2018-01-08 | 2018-01-08 | 1 | 31.11 | DA_corr | 492.53 | 1.45 | 0.95 | 2.4 | 0.077 |
| Lalla Chafia | EV02 | 2018-03-03 | 2018-03-03 | 1 | absent | OL_DAIC | 562.44 | 3.97 | 1.04 | 5.01 | absent |
| Lalla Chafia | EV02 | 2018-03-03 | 2018-03-03 | 1 | 28.86 | ENS_OPL | 561.7 | 4.51 | 1.51 | 6.02 | 0.2087 |
| Lalla Chafia | EV02 | 2018-03-03 | 2018-03-03 | 1 | 28.76 | ENS_corr | 560.01 | 4.16 | 1.2 | 5.35 | 0.1861 |
| Lalla Chafia | EV02 | 2018-03-03 | 2018-03-03 | 1 | 28.86 | DA_nocdf | 574.37 | 9.01 | 6.43 | 15.44 | 0.5351 |
| Lalla Chafia | EV02 | 2018-03-03 | 2018-03-03 | 1 | 28.86 | DA_nocdf_nowilt | 574.41 | 9.01 | 6.43 | 15.44 | 0.5351 |
| Lalla Chafia | EV02 | 2018-03-03 | 2018-03-03 | 1 | 28.76 | DA_corr | 536.26 | 7.11 | 4.04 | 11.15 | 0.3875 |
| Lalla Chafia | EV03 | 2018-03-06 | 2018-03-06 | 1 | absent | OL_DAIC | 590.77 | 2.64 | 1.66 | 4.3 | absent |
| Lalla Chafia | EV03 | 2018-03-06 | 2018-03-06 | 1 | 39.57 | ENS_OPL | 589.87 | 3.08 | 2.9 | 5.98 | 0.151 |
| Lalla Chafia | EV03 | 2018-03-06 | 2018-03-06 | 1 | 39.38 | ENS_corr | 588.27 | 2.77 | 1.91 | 4.68 | 0.1188 |
| Lalla Chafia | EV03 | 2018-03-06 | 2018-03-06 | 1 | 39.57 | DA_nocdf | 599.66 | 6.18 | 10.44 | 16.62 | 0.4199 |
| Lalla Chafia | EV03 | 2018-03-06 | 2018-03-06 | 1 | 39.57 | DA_nocdf_nowilt | 599.69 | 6.18 | 10.44 | 16.62 | 0.4199 |
| Lalla Chafia | EV03 | 2018-03-06 | 2018-03-06 | 1 | 39.38 | DA_corr | 564.79 | 4.73 | 5.81 | 10.54 | 0.2677 |
| Lalla Chafia | EV04 | 2018-04-24 | 2018-04-24 | 1 | absent | OL_DAIC | 526.75 | 3.67 | 2.68 | 6.35 | absent |
| Lalla Chafia | EV04 | 2018-04-24 | 2018-04-24 | 1 | 56.03 | ENS_OPL | 526.32 | 3.92 | 3.05 | 6.97 | 0.1244 |
| Lalla Chafia | EV04 | 2018-04-24 | 2018-04-24 | 1 | 55.83 | ENS_corr | 526.33 | 3.66 | 2.66 | 6.32 | 0.1132 |
| Lalla Chafia | EV04 | 2018-04-24 | 2018-04-24 | 1 | 56.03 | DA_nocdf | 525.1 | 5.81 | 7.02 | 12.83 | 0.229 |
| Lalla Chafia | EV04 | 2018-04-24 | 2018-04-24 | 1 | 56.03 | DA_nocdf_nowilt | 525.22 | 5.81 | 7.02 | 12.83 | 0.229 |
| Lalla Chafia | EV04 | 2018-04-24 | 2018-04-24 | 1 | 55.83 | DA_corr | 477.45 | 4.81 | 4.56 | 9.37 | 0.1678 |
| Lalla Chafia | EV05 | 2018-10-31 | 2018-10-31 | 1 | absent | OL_DAIC | 464.69 | 1.0 | 0.78 | 1.78 | absent |
| Lalla Chafia | EV05 | 2018-10-31 | 2018-10-31 | 1 | 25.38 | ENS_OPL | 464.09 | 1.02 | 0.8 | 1.82 | 0.0718 |
| Lalla Chafia | EV05 | 2018-10-31 | 2018-10-31 | 1 | 25.29 | ENS_corr | 464.25 | 1.0 | 0.78 | 1.78 | 0.0703 |
| Lalla Chafia | EV05 | 2018-10-31 | 2018-10-31 | 1 | 25.38 | DA_nocdf | 473.72 | 1.12 | 1.18 | 2.29 | 0.0904 |
| Lalla Chafia | EV05 | 2018-10-31 | 2018-10-31 | 1 | 25.38 | DA_nocdf_nowilt | 474.24 | 1.12 | 1.33 | 2.45 | 0.0966 |
| Lalla Chafia | EV05 | 2018-10-31 | 2018-10-31 | 1 | 25.29 | DA_corr | 440.05 | 1.51 | 4.28 | 5.79 | 0.2288 |
| Sidi Jabeur | EV01 | 2018-03-06 | 2018-03-07 | 2 | absent | OL_DAIC | 536.34 | 1.49 | 0.51 | 2.0 | absent |
| Sidi Jabeur | EV01 | 2018-03-06 | 2018-03-07 | 2 | 50.32 | ENS_OPL | 535.52 | 1.61 | 0.7 | 2.31 | 0.0459 |
| Sidi Jabeur | EV01 | 2018-03-06 | 2018-03-07 | 2 | 50.02 | ENS_corr | 534.25 | 1.58 | 0.6 | 2.18 | 0.0435 |
| Sidi Jabeur | EV01 | 2018-03-06 | 2018-03-07 | 2 | 50.32 | DA_nocdf | 559.97 | 2.77 | 3.59 | 6.37 | 0.1265 |
| Sidi Jabeur | EV01 | 2018-03-06 | 2018-03-07 | 2 | 50.32 | DA_nocdf_nowilt | 559.97 | 2.77 | 3.59 | 6.37 | 0.1265 |
| Sidi Jabeur | EV01 | 2018-03-06 | 2018-03-07 | 2 | 50.02 | DA_corr | 508.21 | 3.17 | 5.28 | 8.45 | 0.169 |
| Sidi Jabeur | EV02 | 2018-04-24 | 2018-04-24 | 1 | absent | OL_DAIC | 501.75 | 2.24 | 0.96 | 3.2 | absent |
| Sidi Jabeur | EV02 | 2018-04-24 | 2018-04-24 | 1 | 54.85 | ENS_OPL | 501.22 | 2.66 | 1.41 | 4.08 | 0.0744 |
| Sidi Jabeur | EV02 | 2018-04-24 | 2018-04-24 | 1 | 54.52 | ENS_corr | 500.89 | 2.35 | 1.07 | 3.43 | 0.0628 |
| Sidi Jabeur | EV02 | 2018-04-24 | 2018-04-24 | 1 | 54.85 | DA_nocdf | 506.94 | 4.54 | 4.45 | 9.0 | 0.164 |
| Sidi Jabeur | EV02 | 2018-04-24 | 2018-04-24 | 1 | 54.85 | DA_nocdf_nowilt | 506.96 | 4.54 | 4.44 | 8.99 | 0.1638 |
| Sidi Jabeur | EV02 | 2018-04-24 | 2018-04-24 | 1 | 54.52 | DA_corr | 414.07 | 4.9 | 5.63 | 10.53 | 0.1931 |
| Sidi Jabeur | EV03 | 2018-10-31 | 2018-10-31 | 1 | absent | OL_DAIC | 438.65 | 0.76 | 0.58 | 1.34 | absent |
| Sidi Jabeur | EV03 | 2018-10-31 | 2018-10-31 | 1 | 21.58 | ENS_OPL | 437.93 | 0.79 | 0.64 | 1.43 | 0.0664 |
| Sidi Jabeur | EV03 | 2018-10-31 | 2018-10-31 | 1 | 21.48 | ENS_corr | 438.07 | 0.76 | 0.6 | 1.36 | 0.0632 |
| Sidi Jabeur | EV03 | 2018-10-31 | 2018-10-31 | 1 | 21.58 | DA_nocdf | 445.16 | 0.93 | 0.92 | 1.84 | 0.0854 |
| Sidi Jabeur | EV03 | 2018-10-31 | 2018-10-31 | 1 | 21.58 | DA_nocdf_nowilt | 446.45 | 0.92 | 0.9 | 1.83 | 0.0847 |
| Sidi Jabeur | EV03 | 2018-10-31 | 2018-10-31 | 1 | 21.48 | DA_corr | 325.57 | 1.02 | 1.77 | 2.79 | 0.1301 |
| Sidi Jabeur | EV04 | 2018-11-18 | 2018-11-18 | 1 | absent | OL_DAIC | 461.35 | 1.69 | 0.56 | 2.25 | absent |
| Sidi Jabeur | EV04 | 2018-11-18 | 2018-11-18 | 1 | 21.52 | ENS_OPL | 460.49 | 1.77 | 0.63 | 2.4 | 0.1114 |
| Sidi Jabeur | EV04 | 2018-11-18 | 2018-11-18 | 1 | 21.44 | ENS_corr | 460.71 | 1.7 | 0.58 | 2.28 | 0.1062 |
| Sidi Jabeur | EV04 | 2018-11-18 | 2018-11-18 | 1 | 21.52 | DA_nocdf | 469.81 | 2.36 | 1.5 | 3.86 | 0.1792 |
| Sidi Jabeur | EV04 | 2018-11-18 | 2018-11-18 | 1 | 21.52 | DA_nocdf_nowilt | 470.9 | 2.35 | 1.49 | 3.84 | 0.1784 |
| Sidi Jabeur | EV04 | 2018-11-18 | 2018-11-18 | 1 | 21.44 | DA_corr | 346.41 | 2.62 | 2.66 | 5.28 | 0.2461 |
| Sebou amont | EV01 | 2018-02-26 | 2018-02-26 | 1 | absent | OL_DAIC | 462.94 | 0.59 | 0.13 | 0.72 | absent |
| Sebou amont | EV01 | 2018-02-26 | 2018-02-26 | 1 | 21.25 | ENS_OPL | 460.96 | 0.61 | 0.13 | 0.74 | 0.035 |
| Sebou amont | EV01 | 2018-02-26 | 2018-02-26 | 1 | 21.13 | ENS_corr | 462.51 | 0.61 | 0.13 | 0.73 | 0.0347 |
| Sebou amont | EV01 | 2018-02-26 | 2018-02-26 | 1 | 21.25 | DA_nocdf | 456.42 | 0.62 | 0.13 | 0.74 | 0.035 |
| Sebou amont | EV01 | 2018-02-26 | 2018-02-26 | 1 | 21.25 | DA_nocdf_nowilt | 456.42 | 0.62 | 0.13 | 0.74 | 0.035 |
| Sebou amont | EV01 | 2018-02-26 | 2018-02-26 | 1 | 21.13 | DA_corr | 454.8 | 0.61 | 0.14 | 0.76 | 0.0358 |
| Sebou amont | EV02 | 2018-03-07 | 2018-03-07 | 1 | absent | OL_DAIC | 496.53 | 0.41 | 0.13 | 0.54 | absent |
| Sebou amont | EV02 | 2018-03-07 | 2018-03-07 | 1 | 18.52 | ENS_OPL | 494.69 | 0.42 | 0.13 | 0.55 | 0.0295 |
| Sebou amont | EV02 | 2018-03-07 | 2018-03-07 | 1 | 18.45 | ENS_corr | 496.42 | 0.41 | 0.13 | 0.54 | 0.0294 |
| Sebou amont | EV02 | 2018-03-07 | 2018-03-07 | 1 | 18.52 | DA_nocdf | 489.26 | 0.43 | 0.17 | 0.6 | 0.0323 |
| Sebou amont | EV02 | 2018-03-07 | 2018-03-07 | 1 | 18.52 | DA_nocdf_nowilt | 489.26 | 0.43 | 0.17 | 0.6 | 0.0323 |
| Sebou amont | EV02 | 2018-03-07 | 2018-03-07 | 1 | 18.45 | DA_corr | 490.72 | 0.44 | 0.27 | 0.71 | 0.0387 |
| Sebou amont | EV03 | 2018-10-01 | 2018-10-01 | 1 | absent | OL_DAIC | 417.41 | 0.29 | 0.16 | 0.44 | absent |
| Sebou amont | EV03 | 2018-10-01 | 2018-10-01 | 1 | 17.74 | ENS_OPL | 417.56 | 0.29 | 0.17 | 0.46 | 0.0259 |
| Sebou amont | EV03 | 2018-10-01 | 2018-10-01 | 1 | 17.65 | ENS_corr | 417.98 | 0.29 | 0.16 | 0.44 | 0.0251 |
| Sebou amont | EV03 | 2018-10-01 | 2018-10-01 | 1 | 17.74 | DA_nocdf | 397.64 | 0.3 | 0.21 | 0.51 | 0.0288 |
| Sebou amont | EV03 | 2018-10-01 | 2018-10-01 | 1 | 17.74 | DA_nocdf_nowilt | 397.65 | 0.3 | 0.19 | 0.49 | 0.0276 |
| Sebou amont | EV03 | 2018-10-01 | 2018-10-01 | 1 | 17.65 | DA_corr | 365.14 | 0.4 | 0.46 | 0.86 | 0.0489 |
| Sebou amont | EV04 | 2018-10-09 | 2018-10-09 | 1 | absent | OL_DAIC | 431.52 | 0.34 | 0.15 | 0.5 | absent |
| Sebou amont | EV04 | 2018-10-09 | 2018-10-09 | 1 | 20.64 | ENS_OPL | 431.72 | 0.35 | 0.16 | 0.52 | 0.025 |
| Sebou amont | EV04 | 2018-10-09 | 2018-10-09 | 1 | 20.54 | ENS_corr | 432.04 | 0.34 | 0.15 | 0.5 | 0.0242 |
| Sebou amont | EV04 | 2018-10-09 | 2018-10-09 | 1 | 20.64 | DA_nocdf | 401.76 | 0.36 | 0.21 | 0.58 | 0.028 |
| Sebou amont | EV04 | 2018-10-09 | 2018-10-09 | 1 | 20.64 | DA_nocdf_nowilt | 402.17 | 0.36 | 0.2 | 0.56 | 0.0274 |
| Sebou amont | EV04 | 2018-10-09 | 2018-10-09 | 1 | 20.54 | DA_corr | 366.46 | 0.48 | 0.42 | 0.9 | 0.044 |
| Sebou amont | EV05 | 2018-10-28 | 2018-10-28 | 1 | absent | OL_DAIC | 457.68 | 0.85 | 0.15 | 1.0 | absent |
| Sebou amont | EV05 | 2018-10-28 | 2018-10-28 | 1 | 22.04 | ENS_OPL | 457.98 | 0.87 | 0.16 | 1.03 | 0.0466 |
| Sebou amont | EV05 | 2018-10-28 | 2018-10-28 | 1 | 21.88 | ENS_corr | 458.15 | 0.85 | 0.15 | 1.0 | 0.0457 |
| Sebou amont | EV05 | 2018-10-28 | 2018-10-28 | 1 | 22.04 | DA_nocdf | 423.38 | 0.98 | 0.38 | 1.36 | 0.0617 |
| Sebou amont | EV05 | 2018-10-28 | 2018-10-28 | 1 | 22.04 | DA_nocdf_nowilt | 423.23 | 0.99 | 0.39 | 1.37 | 0.0624 |
| Sebou amont | EV05 | 2018-10-28 | 2018-10-28 | 1 | 21.88 | DA_corr | 398.23 | 1.4 | 0.95 | 2.36 | 0.1077 |
| Sebou amont | EV06 | 2018-10-31 | 2018-10-31 | 1 | absent | OL_DAIC | 481.77 | 0.49 | 0.15 | 0.63 | absent |
| Sebou amont | EV06 | 2018-10-31 | 2018-10-31 | 1 | 19.64 | ENS_OPL | 482.28 | 0.5 | 0.16 | 0.66 | 0.0334 |
| Sebou amont | EV06 | 2018-10-31 | 2018-10-31 | 1 | 19.52 | ENS_corr | 482.13 | 0.49 | 0.15 | 0.63 | 0.0325 |
| Sebou amont | EV06 | 2018-10-31 | 2018-10-31 | 1 | 19.64 | DA_nocdf | 451.55 | 0.54 | 0.46 | 1.0 | 0.0509 |
| Sebou amont | EV06 | 2018-10-31 | 2018-10-31 | 1 | 19.64 | DA_nocdf_nowilt | 452.64 | 0.55 | 0.48 | 1.03 | 0.0522 |
| Sebou amont | EV06 | 2018-10-31 | 2018-10-31 | 1 | 19.52 | DA_corr | 429.27 | 0.78 | 1.22 | 2.0 | 0.1023 |
| Sebou amont | EV07 | 2018-11-23 | 2018-11-23 | 1 | absent | OL_DAIC | 522.91 | 0.35 | 0.15 | 0.5 | absent |
| Sebou amont | EV07 | 2018-11-23 | 2018-11-23 | 1 | 19.4 | ENS_OPL | 523.54 | 0.36 | 0.17 | 0.53 | 0.0272 |
| Sebou amont | EV07 | 2018-11-23 | 2018-11-23 | 1 | 19.35 | ENS_corr | 523.17 | 0.35 | 0.15 | 0.5 | 0.0258 |
| Sebou amont | EV07 | 2018-11-23 | 2018-11-23 | 1 | 19.4 | DA_nocdf | 487.87 | 0.47 | 1.01 | 1.48 | 0.0765 |
| Sebou amont | EV07 | 2018-11-23 | 2018-11-23 | 1 | 19.4 | DA_nocdf_nowilt | 488.75 | 0.48 | 1.07 | 1.55 | 0.0799 |
| Sebou amont | EV07 | 2018-11-23 | 2018-11-23 | 1 | 19.35 | DA_corr | 460.53 | 0.69 | 2.04 | 2.73 | 0.1408 |

### 2.2 Régression Linéaire : Δ(Qs+Qsb) vs ΔStock veille (C2 et C3)

| basin | contrast_id | contrast_name | n_events | delta_stock_total_eve_mm | delta_TotalRunoff_cum_j0_j5_mm | slope | intercept | pearson_r | r_squared | p_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | C2 | DA_nocdf − ENS_OPL | 5 | 7.86 | 5.33 | 0.1212 | 4.3775 | 0.1324 | 0.0175 | 0.8319 |
| Sidi Jabeur | C2 | DA_nocdf − ENS_OPL | 4 | 11.68 | 2.71 | 0.077 | 1.8128 | 0.3131 | 0.098 | 0.6869 |
| Sebou amont | C2 | DA_nocdf − ENS_OPL | 7 | -22.98 | 0.25 | -0.0169 | -0.1333 | -0.6652 | 0.4424 | 0.103 |
| Lalla Chafia | C3 | DA_corr − ENS_corr | 5 | -22.36 | 3.77 | -0.0598 | 2.4279 | -0.5146 | 0.2649 | 0.3749 |
| Sidi Jabeur | C3 | DA_corr − ENS_corr | 4 | -84.91 | 4.45 | 0.0448 | 8.2508 | 0.6881 | 0.4734 | 0.3119 |
| Sebou amont | C3 | DA_corr − ENS_corr | 7 | -43.89 | 0.85 | -0.0202 | -0.0302 | -0.6412 | 0.4112 | 0.1206 |

---

## 3. Débit et Métriques aux Stations (2018)

### 3.1 Performance KGE 2012, Composantes, Biais et Débit de Pointe

| station | experiment | status | n_days | kge_2012 | r | beta | gamma | nse | volume_bias_m3s | rel_volume_bias_pct | peak_sim_m3s | peak_sim_date | peak_bias_m3s | peak_timing_days | nic_contrast_id | nic_reference_run | nic_kge_2012 | nic_bootstrap_mean | nic_bootstrap_ci_low | nic_bootstrap_ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | OL_DAIC | routed | 364 | 0.1202 | 0.5127 | 1.381 | 0.3744 | 0.2305 | 3.709 | 38.1 | 109.38 | 2018-04-25 | -89.62 | 48 | none | none | nan | nan | nan | nan |
| Lalla Chafia | ENS_OPL | routed | 364 | 0.0143 | 0.5204 | 1.612 | 0.3942 | 0.1743 | 5.959 | 61.2 | 116.68 | 2018-04-25 | -82.32 | 48 | C1 | OL_DAIC | -0.1204 | -0.115 | -0.2248 | 0.0029 |
| Lalla Chafia | ENS_corr | routed | 364 | 0.1086 | 0.5355 | 1.4224 | 0.3672 | 0.2469 | 4.113 | 42.24 | 108.18 | 2018-04-25 | -90.82 | 48 | none | none | nan | nan | nan | nan |
| Lalla Chafia | DA_nocdf | routed | 364 | -1.7945 | 0.51 | 3.6869 | 0.4084 | -2.3386 | 26.161 | 268.69 | 180.62 | 2018-04-25 | -18.38 | 48 | C2 | ENS_OPL | -1.835 | -1.6921 | -2.5484 | -1.021 |
| Lalla Chafia | DA_nocdf_nowilt | routed | 364 | -1.8081 | 0.511 | 3.701 | 0.4077 | -2.3584 | 26.298 | 270.1 | 180.6 | 2018-04-25 | -18.4 | 48 | C4 | DA_nocdf | -0.0049 | -0.0038 | -0.0152 | 0.0051 |
| Lalla Chafia | DA_corr | routed | 364 | -1.5739 | 0.5017 | 3.4244 | 0.2935 | -1.3101 | 23.605 | 242.44 | 142.42 | 2018-04-25 | -56.58 | 48 | C3 | ENS_corr | -1.8875 | -1.7519 | -3.0081 | -0.9884 |
| Lalla Chafia | OPL | routed | 364 | 0.1254 | 0.4559 | 0.8207 | 0.3392 | 0.1692 | -1.746 | -17.93 | 68.9 | 2018-04-25 | -130.1 | 48 | none | none | nan | nan | nan | nan |
| Lalla Chafia | DA_cdf | routed | 364 | -0.0216 | 0.5353 | 1.6237 | 0.3376 | 0.1998 | 6.072 | 62.37 | 111.48 | 2018-04-25 | -87.52 | 48 | none | none | nan | nan | nan | nan |
| Sidi Jabeur | OL_DAIC | routed | 365 | 0.0585 | 0.67 | 0.5609 | 0.2354 | 0.1312 | -4.774 | -43.91 | 43.28 | 2018-04-25 | -305.72 | 49 | none | none | nan | nan | nan | nan |
| Sidi Jabeur | ENS_OPL | routed | 365 | 0.0812 | 0.59 | 0.7026 | 0.2335 | 0.1537 | -3.233 | -29.74 | 53.25 | 2018-04-25 | -295.75 | 49 | C1 | OL_DAIC | 0.0241 | 0.0163 | -0.0641 | 0.0497 |
| Sidi Jabeur | ENS_corr | routed | 365 | 0.0721 | 0.6603 | 0.602 | 0.2337 | 0.1427 | -4.327 | -39.8 | 45.71 | 2018-04-25 | -303.29 | 49 | none | none | nan | nan | nan | nan |
| Sidi Jabeur | DA_nocdf | routed | 365 | -0.2213 | 0.3484 | 1.726 | 0.2653 | 0.032 | 7.892 | 72.6 | 117.61 | 2018-04-24 | -231.39 | 48 | C2 | ENS_OPL | -0.3292 | -0.4528 | -1.3839 | -0.0185 |
| Sidi Jabeur | DA_nocdf_nowilt | routed | 365 | -0.2182 | 0.3496 | 1.7219 | 0.2653 | 0.0341 | 7.847 | 72.19 | 117.56 | 2018-04-24 | -231.44 | 48 | C4 | DA_nocdf | 0.0025 | 0.0026 | -0.0011 | 0.0078 |
| Sidi Jabeur | DA_corr | routed | 365 | -0.3911 | 0.3243 | 2.0088 | 0.3211 | -0.1472 | 10.966 | 100.88 | 145.97 | 2018-04-24 | -203.03 | 48 | C3 | ENS_corr | -0.4992 | -0.7001 | -2.0075 | -0.0475 |
| Sidi Jabeur | OPL | routed | 365 | -0.0363 | 0.6558 | 0.3616 | 0.2598 | 0.0545 | -6.94 | -63.84 | 31.77 | 2018-04-25 | -317.23 | 49 | none | none | nan | nan | nan | nan |
| Sidi Jabeur | DA_cdf | routed | 365 | 0.0387 | 0.4064 | 1.1185 | 0.2532 | 0.1479 | 1.288 | 11.85 | 85.05 | 2018-04-24 | -263.95 | 48 | none | none | nan | nan | nan | nan |
| Sebou amont | OL_DAIC | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | ENS_OPL | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | ENS_corr | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | DA_nocdf | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | DA_nocdf_nowilt | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | DA_corr | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | OPL | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |
| Sebou amont | DA_cdf | absent (non routé en journalier 2018) | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent | absent |

### 3.2 Comparaison Annuelle et Mensuelle : Δ Débit Exutoire vs Δ(Qs+Qsb) Bassin (C2 et C3)

| station | contrast_id | time_scale | season_or_month | delta_streamflow_volume_m3 | delta_streamflow_depth_mm | delta_TotalRunoff_volume_m3 | delta_TotalRunoff_depth_mm | ratio_streamflow_over_runoff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | C2 | annual | Annuel | 635410181.8 | 190.62 | 583869384.7 | 175.16 | 1.0883 |
| Lalla Chafia | C2 | monthly | 2018-01 | 24941936.2 | 7.48 | 23933444.7 | 7.18 | 1.0421 |
| Lalla Chafia | C2 | monthly | 2018-02 | 80391990.7 | 24.12 | 69533657.0 | 20.86 | 1.1562 |
| Lalla Chafia | C2 | monthly | 2018-03 | 178799096.4 | 53.64 | 153200713.2 | 45.96 | 1.1671 |
| Lalla Chafia | C2 | monthly | 2018-04 | 95832341.4 | 28.75 | 89767084.5 | 26.93 | 1.0676 |
| Lalla Chafia | C2 | monthly | 2018-05 | 49594494.7 | 14.88 | 48133557.4 | 14.44 | 1.0304 |
| Lalla Chafia | C2 | monthly | 2018-06 | 19866552.5 | 5.96 | 19133422.4 | 5.74 | 1.0383 |
| Lalla Chafia | C2 | monthly | 2018-07 | 10851925.3 | 3.26 | 10566715.9 | 3.17 | 1.027 |
| Lalla Chafia | C2 | monthly | 2018-08 | 7120463.1 | 2.14 | 7066699.6 | 2.12 | 1.0076 |
| Lalla Chafia | C2 | monthly | 2018-09 | 5355957.7 | 1.61 | 5466692.1 | 1.64 | 0.9797 |
| Lalla Chafia | C2 | monthly | 2018-10 | 5051999.7 | 1.52 | 5133357.2 | 1.54 | 0.9842 |
| Lalla Chafia | C2 | monthly | 2018-11 | 45470241.5 | 13.64 | 47500221.1 | 14.25 | 0.9573 |
| Lalla Chafia | C2 | monthly | 2018-12 | 112133182.6 | 33.64 | 104400486.0 | 31.32 | 1.0741 |
| Sidi Jabeur | C2 | annual | Annuel | 350844549.6 | 112.07 | 345926233.4 | 110.5 | 1.0142 |
| Sidi Jabeur | C2 | monthly | 2018-01 | 6117250.2 | 1.95 | 7982913.1 | 2.55 | 0.7663 |
| Sidi Jabeur | C2 | monthly | 2018-02 | 34144621.4 | 10.91 | 32996040.7 | 10.54 | 1.0348 |
| Sidi Jabeur | C2 | monthly | 2018-03 | 77990723.6 | 24.91 | 76260299.1 | 24.36 | 1.0227 |
| Sidi Jabeur | C2 | monthly | 2018-04 | 68878699.5 | 22.0 | 65960775.9 | 21.07 | 1.0442 |
| Sidi Jabeur | C2 | monthly | 2018-05 | 38063856.9 | 12.16 | 36940539.0 | 11.8 | 1.0304 |
| Sidi Jabeur | C2 | monthly | 2018-06 | 18010953.7 | 5.75 | 16591937.0 | 5.3 | 1.0855 |
| Sidi Jabeur | C2 | monthly | 2018-07 | 11372575.9 | 3.63 | 10549967.5 | 3.37 | 1.078 |
| Sidi Jabeur | C2 | monthly | 2018-08 | 8110584.0 | 2.59 | 7575941.0 | 2.42 | 1.0706 |
| Sidi Jabeur | C2 | monthly | 2018-09 | 6495441.8 | 2.07 | 6292413.8 | 2.01 | 1.0323 |
| Sidi Jabeur | C2 | monthly | 2018-10 | 6663404.8 | 2.13 | 6417636.0 | 2.05 | 1.0383 |
| Sidi Jabeur | C2 | monthly | 2018-11 | 18479984.6 | 5.9 | 21162546.0 | 6.76 | 0.8732 |
| Sidi Jabeur | C2 | monthly | 2018-12 | 56516453.2 | 18.05 | 57195224.3 | 18.27 | 0.9881 |
| Lalla Chafia | C3 | annual | Annuel | 613015304.7 | 183.9 | 595469438.7 | 178.64 | 1.0295 |
| Lalla Chafia | C3 | monthly | 2018-01 | 13773147.6 | 4.13 | 15500072.2 | 4.65 | 0.8886 |
| Lalla Chafia | C3 | monthly | 2018-02 | 57375630.4 | 17.21 | 53133580.7 | 15.94 | 1.0798 |
| Lalla Chafia | C3 | monthly | 2018-03 | 98800374.1 | 29.64 | 88067076.6 | 26.42 | 1.1219 |
| Lalla Chafia | C3 | monthly | 2018-04 | 48841933.6 | 14.65 | 48133557.4 | 14.44 | 1.0147 |
| Lalla Chafia | C3 | monthly | 2018-05 | 18654043.9 | 5.6 | 19333423.3 | 5.8 | 0.9649 |
| Lalla Chafia | C3 | monthly | 2018-06 | 7302782.2 | 2.19 | 7266700.5 | 2.18 | 1.005 |
| Lalla Chafia | C3 | monthly | 2018-07 | 14850006.0 | 4.45 | 15800073.6 | 4.74 | 0.9399 |
| Lalla Chafia | C3 | monthly | 2018-08 | 42753642.6 | 12.83 | 41100191.3 | 12.33 | 1.0402 |
| Lalla Chafia | C3 | monthly | 2018-09 | 33894119.9 | 10.17 | 32333483.9 | 9.7 | 1.0483 |
| Lalla Chafia | C3 | monthly | 2018-10 | 33434530.5 | 10.03 | 34566827.6 | 10.37 | 0.9672 |
| Lalla Chafia | C3 | monthly | 2018-11 | 111065764.5 | 33.32 | 114867201.4 | 34.46 | 0.9669 |
| Lalla Chafia | C3 | monthly | 2018-12 | 132269329.3 | 39.68 | 125433917.2 | 37.63 | 1.0545 |
| Sidi Jabeur | C3 | annual | Annuel | 482279848.8 | 154.06 | 478223451.7 | 152.76 | 1.0085 |
| Sidi Jabeur | C3 | monthly | 2018-01 | 3256513.0 | 1.04 | 6167191.7 | 1.97 | 0.528 |
| Sidi Jabeur | C3 | monthly | 2018-02 | 33294223.6 | 10.64 | 36345733.7 | 11.61 | 0.916 |
| Sidi Jabeur | C3 | monthly | 2018-03 | 131275946.6 | 41.93 | 120682862.4 | 38.55 | 1.0878 |
| Sidi Jabeur | C3 | monthly | 2018-04 | 113300957.6 | 36.19 | 100271649.4 | 32.03 | 1.1299 |
| Sidi Jabeur | C3 | monthly | 2018-05 | 46315595.5 | 14.79 | 41542453.5 | 13.27 | 1.1149 |
| Sidi Jabeur | C3 | monthly | 2018-06 | 17776909.8 | 5.68 | 15684076.3 | 5.01 | 1.1334 |
| Sidi Jabeur | C3 | monthly | 2018-07 | 15325095.2 | 4.9 | 15809298.4 | 5.05 | 0.9694 |
| Sidi Jabeur | C3 | monthly | 2018-08 | 15410531.1 | 4.92 | 15777992.9 | 5.04 | 0.9767 |
| Sidi Jabeur | C3 | monthly | 2018-09 | 11344152.6 | 3.62 | 12052633.5 | 3.85 | 0.9412 |
| Sidi Jabeur | C3 | monthly | 2018-10 | 11879813.2 | 3.79 | 14244021.4 | 4.55 | 0.834 |
| Sidi Jabeur | C3 | monthly | 2018-11 | 31473547.5 | 10.05 | 42951202.9 | 13.72 | 0.7328 |
| Sidi Jabeur | C3 | monthly | 2018-12 | 51626563.2 | 16.49 | 56694335.6 | 18.11 | 0.9106 |

### 3.3 Timing et Ampleur des 3 Plus Grands Pics de Débit (Observés et Simulés)

| station | series_type | experiment | peak_rank | peak_date | peak_flow_m3s | precip_basin_j_minus_3_mm | precip_basin_j_minus_2_mm | precip_basin_j_minus_1_mm | precip_basin_j0_mm | precip_basin_cum_10d_prior_mm | precip_basin_cum_11d_inc_j0_mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lalla Chafia | observed | OBS | 1 | 2018-03-08 | 199.0 | 12.21 | 41.09 | 21.82 | 0.1 | 170.56 | 170.66 |
| Lalla Chafia | observed | OBS | 2 | 2018-11-01 | 99.6 | 0.34 | 17.58 | 25.86 | 1.41 | 103.36 | 104.77 |
| Lalla Chafia | observed | OBS | 3 | 2018-11-08 | 98.2 | 0.04 | 0.0 | 0.0 | 0.03 | 45.24 | 45.27 |
| Lalla Chafia | simulated | OL_DAIC | 1 | 2018-04-25 | 109.38 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | OL_DAIC | 2 | 2018-04-13 | 68.54 | 1.55 | 2.32 | 18.9 | 6.96 | 30.27 | 37.23 |
| Lalla Chafia | simulated | OL_DAIC | 3 | 2018-03-07 | 55.99 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Lalla Chafia | simulated | ENS_OPL | 1 | 2018-04-25 | 116.68 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | ENS_OPL | 2 | 2018-04-13 | 76.02 | 1.55 | 2.32 | 18.9 | 6.96 | 30.27 | 37.23 |
| Lalla Chafia | simulated | ENS_OPL | 3 | 2018-03-07 | 68.5 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Lalla Chafia | simulated | ENS_corr | 1 | 2018-04-25 | 108.18 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | ENS_corr | 2 | 2018-04-13 | 67.6 | 1.55 | 2.32 | 18.9 | 6.96 | 30.27 | 37.23 |
| Lalla Chafia | simulated | ENS_corr | 3 | 2018-03-07 | 59.91 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Lalla Chafia | simulated | DA_nocdf | 1 | 2018-04-25 | 180.62 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | DA_nocdf | 2 | 2018-03-07 | 173.82 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Lalla Chafia | simulated | DA_nocdf | 3 | 2018-03-16 | 149.44 | 0.4 | 1.4 | 9.25 | 2.56 | 79.82 | 82.38 |
| Lalla Chafia | simulated | DA_nocdf_nowilt | 1 | 2018-04-25 | 180.6 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | DA_nocdf_nowilt | 2 | 2018-03-07 | 173.82 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Lalla Chafia | simulated | DA_nocdf_nowilt | 3 | 2018-03-16 | 149.44 | 0.4 | 1.4 | 9.25 | 2.56 | 79.82 | 82.38 |
| Lalla Chafia | simulated | DA_corr | 1 | 2018-04-25 | 142.42 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | DA_corr | 2 | 2018-03-07 | 121.47 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Lalla Chafia | simulated | DA_corr | 3 | 2018-03-16 | 97.79 | 0.4 | 1.4 | 9.25 | 2.56 | 79.82 | 82.38 |
| Lalla Chafia | simulated | OPL | 1 | 2018-04-25 | 68.9 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | OPL | 2 | 2018-04-13 | 35.58 | 1.55 | 2.32 | 18.9 | 6.96 | 30.27 | 37.23 |
| Lalla Chafia | simulated | OPL | 3 | 2018-11-01 | 28.86 | 0.34 | 17.58 | 25.86 | 1.41 | 103.36 | 104.77 |
| Lalla Chafia | simulated | DA_cdf | 1 | 2018-04-25 | 111.48 | 0.0 | 0.3 | 57.29 | 2.61 | 61.42 | 64.03 |
| Lalla Chafia | simulated | DA_cdf | 2 | 2018-04-13 | 67.04 | 1.55 | 2.32 | 18.9 | 6.96 | 30.27 | 37.23 |
| Lalla Chafia | simulated | DA_cdf | 3 | 2018-03-07 | 66.11 | 2.16 | 12.21 | 41.09 | 21.82 | 148.74 | 170.56 |
| Sidi Jabeur | observed | OBS | 1 | 2018-03-07 | 349.0 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | observed | OBS | 2 | 2018-04-25 | 180.0 | 0.03 | 2.24 | 57.96 | 3.75 | 62.26 | 66.01 |
| Sidi Jabeur | observed | OBS | 3 | 2018-01-09 | 133.0 | 13.58 | 6.27 | 17.97 | 1.04 | 37.98 | 39.02 |
| Sidi Jabeur | simulated | OL_DAIC | 1 | 2018-04-25 | 43.28 | 0.03 | 2.24 | 57.96 | 3.75 | 62.26 | 66.01 |
| Sidi Jabeur | simulated | OL_DAIC | 2 | 2018-03-07 | 23.39 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | OL_DAIC | 3 | 2018-11-01 | 19.55 | 0.31 | 16.99 | 22.34 | 1.2 | 84.57 | 85.77 |
| Sidi Jabeur | simulated | ENS_OPL | 1 | 2018-04-25 | 53.25 | 0.03 | 2.24 | 57.96 | 3.75 | 62.26 | 66.01 |
| Sidi Jabeur | simulated | ENS_OPL | 2 | 2018-03-07 | 25.69 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | ENS_OPL | 3 | 2018-04-13 | 22.2 | 0.33 | 2.56 | 14.25 | 4.79 | 24.14 | 28.93 |
| Sidi Jabeur | simulated | ENS_corr | 1 | 2018-04-25 | 45.71 | 0.03 | 2.24 | 57.96 | 3.75 | 62.26 | 66.01 |
| Sidi Jabeur | simulated | ENS_corr | 2 | 2018-03-07 | 24.88 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | ENS_corr | 3 | 2018-11-01 | 19.74 | 0.31 | 16.99 | 22.34 | 1.2 | 84.57 | 85.77 |
| Sidi Jabeur | simulated | DA_nocdf | 1 | 2018-04-24 | 117.61 | 0.5 | 0.03 | 2.24 | 57.96 | 4.63 | 62.59 |
| Sidi Jabeur | simulated | DA_nocdf | 2 | 2018-04-13 | 56.98 | 0.33 | 2.56 | 14.25 | 4.79 | 24.14 | 28.93 |
| Sidi Jabeur | simulated | DA_nocdf | 3 | 2018-03-07 | 56.45 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | DA_nocdf_nowilt | 1 | 2018-04-24 | 117.56 | 0.5 | 0.03 | 2.24 | 57.96 | 4.63 | 62.59 |
| Sidi Jabeur | simulated | DA_nocdf_nowilt | 2 | 2018-04-13 | 56.98 | 0.33 | 2.56 | 14.25 | 4.79 | 24.14 | 28.93 |
| Sidi Jabeur | simulated | DA_nocdf_nowilt | 3 | 2018-03-07 | 56.45 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | DA_corr | 1 | 2018-04-24 | 145.97 | 0.5 | 0.03 | 2.24 | 57.96 | 4.63 | 62.59 |
| Sidi Jabeur | simulated | DA_corr | 2 | 2018-03-24 | 75.59 | 0.0 | 0.0 | 0.0 | 0.04 | 9.99 | 10.03 |
| Sidi Jabeur | simulated | DA_corr | 3 | 2018-03-07 | 73.96 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | OPL | 1 | 2018-04-25 | 31.77 | 0.03 | 2.24 | 57.96 | 3.75 | 62.26 | 66.01 |
| Sidi Jabeur | simulated | OPL | 2 | 2018-11-01 | 16.04 | 0.31 | 16.99 | 22.34 | 1.2 | 84.57 | 85.77 |
| Sidi Jabeur | simulated | OPL | 3 | 2018-03-07 | 15.43 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |
| Sidi Jabeur | simulated | DA_cdf | 1 | 2018-04-24 | 85.05 | 0.5 | 0.03 | 2.24 | 57.96 | 4.63 | 62.59 |
| Sidi Jabeur | simulated | DA_cdf | 2 | 2018-04-13 | 36.3 | 0.33 | 2.56 | 14.25 | 4.79 | 24.14 | 28.93 |
| Sidi Jabeur | simulated | DA_cdf | 3 | 2018-03-07 | 33.4 | 3.85 | 10.06 | 28.65 | 22.75 | 113.48 | 136.23 |

---

## 4. Liste des Fichiers Produits

### Tables CSV :
- `paper1/tables/A2_flow_partition_runs.csv`
- `paper1/tables/A2_flow_partition_contrasts.csv`
- `paper1/tables/A2_rainfall_events_runoff.csv`
- `paper1/tables/A2_rainfall_events_contrasts_regression.csv`
- `paper1/tables/A2_streamflow_metrics_stations.csv`
- `paper1/tables/A2_streamflow_vs_runoff_contrasts.csv`
- `paper1/tables/A2_peak_timing.csv`

### Figures PNG :
- `paper1/figures/A2_streamflow_hydrographs_2018.png`
- `paper1/figures/A2_flow_partition_bars.png`
- `paper1/figures/A2_rainfall_events_scatter.png`

### Scripts :
- `scripts/paper1/step_a2_soil_to_streamflow.py`
- `paper1/scripts/step_a2_soil_to_streamflow.py`

# Rapport d'intégrité — Simulation DA_cdf_noirr_2016_2020 (Étape 1)

Ce rapport documente les vérifications d'intégrité de la simulation `DA_cdf_noirr_2016_2020` sur l'ensemble de la période quinquennale (60 mois : janvier 2016 – décembre 2020) en comparaison stricte avec la simulation de référence `DA_nocdf_noirr_2016_2020` (DA-NoCDF).

---

## 1. Synthèse globale des vérifications (Étape 1)

| Critère de vérification | Statut | Observations chiffrées |
| :--- | :---: | :--- |
| **a. Présence des 60 mois** | **CONFORME** | 60 mois sur 60 présents (2016-01 à 2020-12).<br>• SURFACEMODEL : **1 827** fichiers HIST quotidiens (identique à NoCDF).<br>• EnKF spread : **1 827** fichiers quotidiens (identique à NoCDF).<br>• DAOBS / incr / innov : **4 577** fichiers dans CDF vs **4 619** dans NoCDF (écart de $-42$ fichiers, soit $0{,}91\,\%$, réparti sur 29 mois distincts). |
| **b. Continuité de la chaîne** | **CONFORME** | • 60/60 configs générées strictement enchaînées.<br>• Restart 2016-01 issu de `SPINUP_DA` (surface & perturbation).<br>• Mois $m$ démarre systématiquement sur le restart de fin du mois $m-1$ ($60/60$ fichiers existants, non vides, taille nominale).<br>• `check_cdf_domain.py` exécuté et validé (`[SUCCÈS]`) sur les **60 mois sur 60**. |
| **c. Journaux & Qualité sorties** | **CONFORME** | • Fichiers `.err` Slurm : **0 erreur** (contiennent uniquement les métriques runtime `time`).<br>• Fichiers `.log` Slurm : **0 anomalie / 0 crash**.<br>• Logs LIS (`lislog_*`) : **0 erreur critique**, avertissements nominaux (dimensions 1D lat/lon, paramètres Noah-MP par défaut, fallbacks IMERG sur MERRA-2).<br>• Sorties NetCDF : **0 NaN / 0 Inf** sur masque terre (`LANDMASK == 1`, 16 030 pixels). Pas de valeur $-9999$ sur terre. |
| **d. Dispersion ensemble (C1)** | **CONFORME** | • Moyenne 2016–2020 Couche 1 : **0,16395 m³/m³** (CDF) vs **0,16582 m³/m³** (NoCDF).<br>• Écart moyen (CDF − NoCDF) : **−0,00187 m³/m³** (ratio CDF/NoCDF = **98,89 %**).<br>• Aucun effondrement du spread : stabilité pluriannuelle (2016: $0{,}1632$, 2020: $0{,}1663$). |

---

## 2. Inventaire comparatif annuel et cumulé (CDF vs NoCDF)

| Année | DAOBS (CDF / NoCDF) | Incréments (CDF / NoCDF) | Innovations (CDF / NoCDF) | Spread EnKF (CDF / NoCDF) | HIST Surface (CDF / NoCDF) | SURFACEMODEL Total (CDF / NoCDF) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2016** | 933 / 944 | 933 / 944 | 933 / 944 | 366 / 366 | 366 / 366 | 390 / 390 |
| **2017** | 939 / 945 | 939 / 945 | 939 / 945 | 365 / 365 | 365 / 365 | 389 / 389 |
| **2018** | 911 / 929 | 911 / 929 | 911 / 929 | 365 / 365 | 365 / 365 | 389 / 389 |
| **2019** | 863 / 860 | 863 / 860 | 863 / 860 | 365 / 365 | 365 / 365 | 389 / 389 |
| **2020** | 931 / 941 | 931 / 941 | 931 / 941 | 366 / 366 | 366 / 366 | 390 / 390 |
| **TOTAL** | **4 577 / 4 619** | **4 577 / 4 619** | **4 577 / 4 619** | **1 827 / 1 827** | **1 827 / 1 827** | **1 947 / 1 947** |

> [!NOTE]
> Pour chaque pas d'assimilation où au moins une observation valide subsiste, LIS produit exactement 1 fichier `DAOBS`, 1 fichier `_incr` et 1 fichier `_innov`. L'égalité stricte `DAOBS == Incr == Innov` est vérifiée pour les 60 mois dans les deux runs. L'écart global de $-42$ pas d'assimilation résulte des passes satellitaires où l'ensemble des pixels a été exclu par le bornage ou le filtrage CDF.

---

## 3. Continuité temporelle et restarts de la chaîne (Étape 1b)

1. **Vérification des bornes temporelles dans les 60 fichiers `lis_DA_SMAP_cdf_noirr_YYYY-MM.config` :**
   - Date de démarrage globale : `2016-01-01 00:00:00`
   - Date de fin globale : `2021-01-01 00:00:00` (fin du mois 2020-12)
   - Concordance exacte des dates : pour tout mois $m \in [2, 60]$, la date de début coïncide à la seconde près avec la date de fin du mois $m-1$.
2. **Chemins et intégrité des fichiers restart :**
   - Mois 1 (`2016-01`) :
     - Surface : `.../SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc` (présent, valide)
     - Perturbation : `.../SPINUP/SPINUP_DA/restarts/pert/LIS_DAPERT_201601010000.d01.bin` (présent, valide)
   - Mois 2 à 60 (`2016-02` à `2020-12`) :
     - Surface : `restarts/surf/LIS_RST_NOAHMP401_YYYYMM010000.d01.nc` (60/60 présents, taille nominale)
     - Perturbation : `restarts/pert/LIS_DAPERT_YYYYMM010000.d01.bin` (60/60 présents, taille nominale)
3. **Exécution du garde-fou spatial `check_cdf_domain.py` :**
   - Validé dans les 60 journaux Slurm (`logs/MMYYYY/DA_SMAP_cdf_noirr_*.log`).
   - Re-vérification indépendante : `ngrid = 16 030` sur le CDF et `16 030` points terre sur `lis_input_NorthMor_5km.nc`. Écart max lat/lon = $0{,}0$, 0 pixel divergent sur `LANDMASK`.

---

## 4. Dispersion de l'ensemble — Couche 1 (0–10 cm) (Étape 1d)

La dispersion (écart-type inter-membres) de l'humidité du sol en couche 1 a été extraite de chaque fichier quotidien `LIS_DA_EnKF_*_spread.a01.d01.nc` (variable `ensspread_Soil Moisture Layer 1_01`) sur l'ensemble des 16 030 mailles terre valides (`LANDMASK == 1`, non $-9999$).

### Moyennes annuelles de la dispersion (couche 1)

| Année | Dispersion CDF ($m^3/m^3$) | Dispersion NoCDF ($m^3/m^3$) | Différence CDF − NoCDF ($m^3/m^3$) | Ratio CDF / NoCDF |
| :---: | :---: | :---: | :---: | :---: |
| **2016** | 0,16319 | 0,16693 | −0,00374 | 97,76 % |
| **2017** | 0,16375 | 0,16632 | −0,00257 | 98,45 % |
| **2018** | 0,16072 | 0,16390 | −0,00318 | 98,05 % |
| **2019** | 0,16576 | 0,16510 | +0,00065 | 100,44 % |
| **2020** | 0,16633 | 0,16684 | −0,00051 | 99,73 % |
| **Moyenne 5 ans** | **0,16395** | **0,16582** | **−0,00187** | **98,89 %** |

![Série temporelle de la dispersion de l'ensemble (couche 1, 2016–2020)](/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/fb3368fe-64c8-499b-9876-a866d379c46e/ensemble_spread_layer1_2016_2020.png)

### Constat chiffré sur l'évolution du spread
- En 2016, la dispersion moyenne annuelle s'établit à $0{,}16319\text{ m}^3/\text{m}^3$.
- En 2020, la dispersion moyenne annuelle s'établit à $0{,}16633\text{ m}^3/\text{m}^3$.
- Le minimum mensuel sur la période 2016–2020 est de $0{,}14131\text{ m}^3/\text{m}^3$ (juillet 2018) pour CDF et $0{,}14428\text{ m}^3/\text{m}^3$ pour NoCDF.
- Le maximum mensuel est de $0{,}18174\text{ m}^3/\text{m}^3$ (décembre 2018) pour CDF et $0{,}18068\text{ m}^3/\text{m}^3$ pour NoCDF.
- La dispersion inter-annuelle ne présente aucune dérive décroissante ni effondrement vers zéro.

---

## 5. Tableau mensuel exhaustif des 60 mois (2016–2020)

| Mois | DAOBS (CDF/NoCDF) | Incr (CDF/NoCDF) | Spread f. (CDF/NoCDF) | HIST (CDF/NoCDF) | Spread C1 CDF ($m^3/m^3$) | Spread C1 NoCDF ($m^3/m^3$) | Diff Spread ($m^3/m^3$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2016-01** | 85 / 85 | 85 / 85 | 31 / 31 | 31 / 31 | 0,17236 | 0,17770 | −0,00534 |
| **2016-02** | 77 / 77 | 77 / 77 | 29 / 29 | 29 / 29 | 0,16504 | 0,16794 | −0,00290 |
| **2016-03** | 80 / 80 | 80 / 80 | 31 / 31 | 31 / 31 | 0,16573 | 0,16528 | +0,00046 |
| **2016-04** | 75 / 73 | 75 / 73 | 30 / 30 | 30 / 30 | 0,17127 | 0,17541 | −0,00414 |
| **2016-05** | 77 / 77 | 77 / 77 | 31 / 31 | 31 / 31 | 0,16827 | 0,17350 | −0,00523 |
| **2016-06** | 76 / 75 | 76 / 75 | 30 / 30 | 30 / 30 | 0,16170 | 0,16203 | −0,00033 |
| **2016-07** | 75 / 81 | 75 / 81 | 31 / 31 | 31 / 31 | 0,15112 | 0,15198 | −0,00086 |
| **2016-08** | 75 / 81 | 75 / 81 | 31 / 31 | 31 / 31 | 0,15434 | 0,15716 | −0,00282 |
| **2016-09** | 67 / 69 | 67 / 69 | 30 / 30 | 30 / 30 | 0,16757 | 0,17264 | −0,00507 |
| **2016-10** | 83 / 83 | 83 / 83 | 31 / 31 | 31 / 31 | 0,17201 | 0,17868 | −0,00667 |
| **2016-11** | 82 / 82 | 82 / 82 | 30 / 30 | 30 / 30 | 0,16315 | 0,16949 | −0,00635 |
| **2016-12** | 81 / 81 | 81 / 81 | 31 / 31 | 31 / 31 | 0,14568 | 0,15131 | −0,00563 |
| **2017-01** | 81 / 81 | 81 / 81 | 31 / 31 | 31 / 31 | 0,16434 | 0,17144 | −0,00710 |
| **2017-02** | 74 / 74 | 74 / 74 | 28 / 28 | 28 / 28 | 0,15389 | 0,16023 | −0,00634 |
| **2017-03** | 80 / 79 | 80 / 79 | 31 / 31 | 31 / 31 | 0,17576 | 0,17730 | −0,00154 |
| **2017-04** | 79 / 78 | 79 / 78 | 30 / 30 | 30 / 30 | 0,17148 | 0,17343 | −0,00195 |
| **2017-05** | 83 / 80 | 83 / 80 | 31 / 31 | 31 / 31 | 0,16824 | 0,16917 | −0,00092 |
| **2017-06** | 78 / 79 | 78 / 79 | 30 / 30 | 30 / 30 | 0,16549 | 0,16448 | +0,00101 |
| **2017-07** | 72 / 82 | 72 / 82 | 31 / 31 | 31 / 31 | 0,14768 | 0,14791 | −0,00023 |
| **2017-08** | 73 / 77 | 73 / 77 | 31 / 31 | 31 / 31 | 0,15039 | 0,15555 | −0,00517 |
| **2017-09** | 78 / 76 | 78 / 76 | 30 / 30 | 30 / 30 | 0,16246 | 0,16569 | −0,00323 |
| **2017-10** | 78 / 77 | 78 / 77 | 31 / 31 | 31 / 31 | 0,17237 | 0,17659 | −0,00423 |
| **2017-11** | 80 / 79 | 80 / 79 | 30 / 30 | 30 / 30 | 0,17228 | 0,17163 | +0,00066 |
| **2017-12** | 83 / 83 | 83 / 83 | 31 / 31 | 31 / 31 | 0,16055 | 0,16240 | −0,00185 |
| **2018-01** | 72 / 72 | 72 / 72 | 31 / 31 | 31 / 31 | 0,16173 | 0,16347 | −0,00174 |
| **2018-02** | 70 / 70 | 70 / 70 | 28 / 28 | 28 / 28 | 0,15415 | 0,16447 | −0,01032 |
| **2018-03** | 81 / 81 | 81 / 81 | 31 / 31 | 31 / 31 | 0,15367 | 0,15670 | −0,00303 |
| **2018-04** | 79 / 78 | 79 / 78 | 30 / 30 | 30 / 30 | 0,15711 | 0,15942 | −0,00231 |
| **2018-05** | 74 / 73 | 74 / 73 | 31 / 31 | 31 / 31 | 0,17329 | 0,17786 | −0,00457 |
| **2018-06** | 70 / 70 | 70 / 70 | 30 / 30 | 30 / 30 | 0,16838 | 0,17005 | −0,00167 |
| **2018-07** | 70 / 85 | 70 / 85 | 31 / 31 | 31 / 31 | 0,14131 | 0,14428 | −0,00298 |
| **2018-08** | 79 / 84 | 79 / 84 | 31 / 31 | 31 / 31 | 0,15813 | 0,16111 | −0,00297 |
| **2018-09** | 78 / 77 | 78 / 77 | 30 / 30 | 30 / 30 | 0,16364 | 0,16781 | −0,00417 |
| **2018-10** | 80 / 80 | 80 / 80 | 31 / 31 | 31 / 31 | 0,15933 | 0,16272 | −0,00339 |
| **2018-11** | 79 / 79 | 79 / 79 | 30 / 30 | 30 / 30 | 0,15614 | 0,15817 | −0,00203 |
| **2018-12** | 79 / 80 | 79 / 80 | 31 / 31 | 31 / 31 | 0,18174 | 0,18068 | +0,00106 |
| **2019-01** | 80 / 80 | 80 / 80 | 31 / 31 | 31 / 31 | 0,17516 | 0,17273 | +0,00243 |
| **2019-02** | 76 / 75 | 76 / 75 | 28 / 28 | 28 / 28 | 0,17064 | 0,16756 | +0,00308 |
| **2019-03** | 85 / 85 | 85 / 85 | 31 / 31 | 31 / 31 | 0,17038 | 0,16872 | +0,00166 |
| **2019-04** | 78 / 77 | 78 / 77 | 30 / 30 | 30 / 30 | 0,16630 | 0,17297 | −0,00667 |
| **2019-05** | 83 / 80 | 83 / 80 | 31 / 31 | 31 / 31 | 0,16948 | 0,17148 | −0,00201 |
| **2019-06** | 45 / 45 | 45 / 45 | 30 / 30 | 30 / 30 | 0,16600 | 0,16006 | +0,00594 |
| **2019-07** | 21 / 21 | 21 / 21 | 31 / 31 | 31 / 31 | 0,15097 | 0,14697 | +0,00400 |
| **2019-08** | 73 / 77 | 73 / 77 | 31 / 31 | 31 / 31 | 0,15340 | 0,15590 | −0,00250 |
| **2019-09** | 77 / 77 | 77 / 77 | 30 / 30 | 30 / 30 | 0,16600 | 0,17022 | −0,00422 |
| **2019-10** | 81 / 79 | 81 / 79 | 31 / 31 | 31 / 31 | 0,16747 | 0,16559 | +0,00188 |
| **2019-11** | 83 / 83 | 83 / 83 | 30 / 30 | 30 / 30 | 0,16801 | 0,16473 | +0,00328 |
| **2019-12** | 81 / 81 | 81 / 81 | 31 / 31 | 31 / 31 | 0,16527 | 0,16431 | +0,00096 |
| **2020-01** | 78 / 78 | 78 / 78 | 31 / 31 | 31 / 31 | 0,17064 | 0,17070 | −0,00006 |
| **2020-02** | 70 / 70 | 70 / 70 | 29 / 29 | 29 / 29 | 0,17939 | 0,17782 | +0,00157 |
| **2020-03** | 79 / 78 | 79 / 78 | 31 / 31 | 31 / 31 | 0,16459 | 0,16041 | +0,00417 |
| **2020-04** | 78 / 78 | 78 / 78 | 30 / 30 | 30 / 30 | 0,16437 | 0,17023 | −0,00586 |
| **2020-05** | 79 / 79 | 79 / 79 | 31 / 31 | 31 / 31 | 0,16570 | 0,17000 | −0,00430 |
| **2020-06** | 81 / 81 | 81 / 81 | 30 / 30 | 30 / 30 | 0,16646 | 0,16369 | +0,00277 |
| **2020-07** | 74 / 83 | 74 / 83 | 31 / 31 | 31 / 31 | 0,15376 | 0,15258 | +0,00119 |
| **2020-08** | 79 / 82 | 79 / 82 | 31 / 31 | 31 / 31 | 0,15448 | 0,15601 | −0,00153 |
| **2020-09** | 78 / 77 | 78 / 77 | 30 / 30 | 30 / 30 | 0,16613 | 0,16876 | −0,00262 |
| **2020-10** | 78 / 78 | 78 / 78 | 31 / 31 | 31 / 31 | 0,16812 | 0,16388 | +0,00424 |
| **2020-11** | 80 / 80 | 80 / 80 | 30 / 30 | 30 / 30 | 0,17117 | 0,17435 | −0,00318 |
| **2020-12** | 77 / 77 | 77 / 77 | 31 / 31 | 31 / 31 | 0,17114 | 0,17363 | −0,00249 |

# Rapport d'analyse — Étape 2 : Comportement du CDF et Comparaison à DA-NoCDF (2016–2020)

Ce document rassemble l'ensemble des chiffres, métriques et figures relatifs à l'évaluation comparative des simulations `DA_cdf_noirr_2016_2020` (DA-CDF) et `DA_nocdf_noirr_2016_2020` (DA-NoCDF), ainsi que la simulation sans assimilation `OPL_noirr_2016_2020` (OL).

---

## 1. Vue d'ensemble et chiffres clés comparatifs

| Diagnostic scientifique | `DA_cdf_noirr_2016_2020` (CDF) | `DA_nocdf_noirr_2016_2020` (NoCDF) | Écart / Ratio |
| :--- | :---: | :---: | :---: |
| **Taux de rejet global des obs** | **35,60 %** | **49,99 %** | **−14,39 points** |
| **Spearman médian obs brute vs rescalée** | **0,9946** (p05 = 0,9821) | $1{,}0000$ (non rescalé) | Monotonie quasi-parfaite |
| **Biais d'innovation $O - F$ (moy. 5 ans)** | **+0,00199 m³/m³** | **−0,00552 m³/m³** | Proche de 0 dans CDF |
| **Écart-type innovation $O - F$** | **0,02921 m³/m³** | **0,03403 m³/m³** | −14,2 % dans CDF |
| **Innovations normalisées (moyenne)** | **+0,0266** | **−0,0833** | Biais réduit de 68 % |
| **Innovations normalisées (variance)** | **0,2263** | **0,3766** | Variance sous-unitaire |
| **Ajustement cumulé net (pixels communs)** | **+77,93 mm** (+15,59 mm/an) | **−176,41 mm** (−35,28 mm/an) | **+254,34 mm** sur 5 ans |
| **Ajustement cumulé absolu (pixels communs)** | **800,44 mm** (160,09 mm/an) | **679,07 mm** (135,81 mm/an) | +121,37 mm (+17,9 %) |
| **$\Delta$ Humidité racinaire (DA − OL)** | **−0,00216 m³/m³** | **−0,01524 m³/m³** | **+0,01308 m³/m³** |
| **$\Delta$ Évapotranspiration (DA − OL)** | **+0,1476 mm/j** (+53,9 mm/an) | **−0,0466 mm/j** (−17,0 mm/an) | **+0,1941 mm/j** |
| **$\Delta$ Ruissellement surface Qs (DA − OL)** | **+0,0032 mm/j** (+1,2 mm/an) | **+0,0028 mm/j** (+1,0 mm/an) | +0,0004 mm/j |
| **$\Delta$ Écoulement base Qsb (DA − OL)** | **+0,0351 mm/j** (+12,8 mm/an) | **+0,0300 mm/j** (+11,0 mm/an) | +0,0051 mm/j |
| **Variation nette de stock $\Delta S$ (5 ans)** | **+1,08 mm** (Sol: +5,54, Nappe: −4,53) | **−34,34 mm** (Sol: −22,57, Nappe: −11,84) | OL = −16,25 mm |

---

## 2. Étape 2a — Rejets par cause, Spearman et Innovations (Moyennes annuelles)

### Tableau récapitulatif annuel pour `DA_cdf_noirr_2016_2020` (CDF)

| Année | Obs Brutes | Obs Retenues | Rejets Totaux (%) | Rejets Forêt | Rejets Seuil Flétrissement | Rejets Tests CDF / Mét. | Spearman Médian | $O - F$ Moyen ($m^3/m^3$) | $O - F$ Écart-Type ($m^3/m^3$) | Innov. Norm. Moyenne | Innov. Norm. Variance |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2016** | 4 721 349 | 3 068 114 | 35,02 % | 794 804 | 133 971 | 724 460 | 0,9951 | +0,00226 | 0,02975 | +0,0346 | 0,2353 |
| **2017** | 4 669 824 | 2 794 139 | 40,16 % | 785 882 | 228 321 | 861 482 | 0,9932 | +0,00241 | 0,02904 | +0,0391 | 0,2211 |
| **2018** | 4 584 560 | 2 952 505 | 35,60 % | 774 246 | 134 263 | 723 546 | 0,9960 | −0,00189 | 0,02905 | −0,0377 | 0,2335 |
| **2019** | 4 198 120 | 2 710 137 | 35,44 % | 707 558 | 158 531 | 621 894 | 0,9942 | +0,00274 | 0,02874 | +0,0424 | 0,2159 |
| **2020** | 4 620 904 | 3 141 845 | 32,01 % | 776 569 | 108 554 | 593 936 | 0,9945 | +0,00347 | 0,02944 | +0,0544 | 0,2256 |
| **Moy.** | **4 558 951** | **2 933 348** | **35,60 %** | **767 812** | **152 728** | **705 064** | **0,9946** | **+0,00199** | **0,02921** | **+0,0266** | **0,2263** |

### Tableau récapitulatif annuel pour `DA_nocdf_noirr_2016_2020` (NoCDF)

| Année | Obs Brutes | Obs Retenues | Rejets Totaux (%) | Rejets Forêt | Rejets Seuil Flétrissement | Rejets Météo / Gel / Pluie | Spearman Médian | $O - F$ Moyen ($m^3/m^3$) | $O - F$ Écart-Type ($m^3/m^3$) | Innov. Norm. Moyenne | Innov. Norm. Variance |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2016** | 4 721 349 | 2 374 380 | 49,71 % | 794 804 | 1 454 445 | 97 720 | 1,0000 | −0,00608 | 0,03621 | −0,0916 | 0,4060 |
| **2017** | 4 669 824 | 2 064 429 | 55,79 % | 785 882 | 1 738 676 | 80 837 | 1,0000 | −0,00479 | 0,03164 | −0,0693 | 0,3026 |
| **2018** | 4 584 560 | 2 510 263 | 45,25 % | 774 246 | 1 184 743 | 115 308 | 1,0000 | −0,00943 | 0,03763 | −0,1508 | 0,4718 |
| **2019** | 4 198 120 | 2 071 547 | 50,66 % | 707 558 | 1 350 491 | 68 524 | 1,0000 | −0,00347 | 0,03391 | −0,0482 | 0,3520 |
| **2020** | 4 620 904 | 2 385 780 | 48,37 % | 776 569 | 1 386 281 | 72 274 | 1,0000 | −0,00385 | 0,03394 | −0,0564 | 0,3487 |
| **Moy.** | **4 558 951** | **2 281 280** | **49,99 %** | **767 812** | **1 422 927** | **86 933** | **1,0000** | **−0,00552** | **0,03403** | **−0,0833** | **0,3766** |

---

## 3. Étape 2b — Climatologie calendaire (2016–2020) et Dérive interannuelle

### Climatologie par mois calendaire de l'innovation $O - F$ et des innovations normalisées

| Mois calendaire | $O - F$ CDF ($m^3/m^3$) | $O - F$ NoCDF ($m^3/m^3$) | Innov. Norm. CDF (Moyenne) | Innov. Norm. CDF (Variance) | Rejet CDF (%) | Rejet NoCDF (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Janvier (1)** | **+0,00267** | −0,00516 | +0,0351 | 0,2070 | 35,76 % | 52,77 % |
| **Février (2)** | **+0,00099** | −0,01121 | +0,0092 | 0,2453 | 22,93 % | 53,12 % |
| **Mars (3)** | **+0,00070** | −0,01341 | −0,0003 | 0,2469 | 31,41 % | 51,48 % |
| **Avril (4)** | **+0,00228** | −0,01308 | +0,0250 | 0,2349 | 20,93 % | 50,20 % |
| **Mai (5)** | **+0,00254** | −0,00933 | +0,0358 | 0,2526 | 25,71 % | 54,63 % |
| **Juin (6)** | **+0,00207** | +0,00160 | +0,0430 | 0,2204 | 44,42 % | 61,22 % |
| **Juillet (7)** | **+0,00139** | +0,00921 | +0,0327 | 0,0862 | 79,20 % | 56,41 % |
| **Août (8)** | **+0,00466** | +0,00406 | +0,0897 | 0,2712 | 62,82 % | 48,03 % |
| **Septembre (9)** | **+0,00197** | −0,00435 | +0,0325 | 0,2268 | 30,71 % | 45,40 % |
| **Octobre (10)** | **−0,00017** | −0,00873 | −0,0072 | 0,2714 | 21,41 % | 44,01 % |
| **Novembre (11)** | **+0,00188** | −0,00666 | +0,0216 | 0,2699 | 25,48 % | 42,95 % |
| **Décembre (12)** | **+0,00064** | −0,00922 | +0,0017 | 0,1827 | 26,99 % | 39,25 % |

### Constats sur la climatologie et la dérive :
1. **Centrage de l'innovation dans CDF** : L'innovation moyenne $O - F$ dans l'espace rescalé reste comprise entre $-0{,}00017\text{ m}^3/\text{m}^3$ (octobre) et $+0{,}00466\text{ m}^3/\text{m}^3$ (août). La moyenne annuelle globale est de $+0{,}00199\text{ m}^3/\text{m}^3$.
2. **Dérive interannuelle dans CDF** :
   - 2016 : $+0{,}00226\text{ m}^3/\text{m}^3$
   - 2017 : $+0{,}00241\text{ m}^3/\text{m}^3$
   - 2018 : $-0{,}00189\text{ m}^3/\text{m}^3$
   - 2019 : $+0{,}00274\text{ m}^3/\text{m}^3$
   - 2020 : $+0{,}00347\text{ m}^3/\text{m}^3$
   L'amplitude maximale interannuelle est de $0{,}00536\text{ m}^3/\text{m}^3$ (entre 2018 et 2020), sans tendance monotone séculaire.

---

## 4. Étape 2c — Ajustements cumulés sur pixels-jours communs (Figure S1 recalculée)

Calculs effectués sur les mailles et dates d'assimilation conjointes entre CDF et NoCDF, pour la couche 1 ($0{,}1\text{ m}$ d'épaisseur, soit $100\text{ mm}$ de sol) :

### Cumuls annuels par an (mm équivalent eau)

| Année | Positif CDF | Négatif CDF | Net CDF | Absolu CDF | Positif NoCDF | Négatif NoCDF | Net NoCDF | Absolu NoCDF | Diff Net (CDF − NoCDF) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2016** | +90,25 mm | −72,80 mm | **+17,45 mm** | 163,05 mm | +52,19 mm | −89,49 mm | **−37,29 mm** | 141,68 mm | **+54,75 mm** |
| **2017** | +86,01 mm | −69,66 mm | **+16,35 mm** | 155,67 mm | +42,72 mm | −71,69 mm | **−28,97 mm** | 114,40 mm | **+45,32 mm** |
| **2018** | +69,36 mm | −77,81 mm | **−8,45 mm** | 147,17 mm | +51,55 mm | −109,45 mm | **−57,91 mm** | 161,00 mm | **+49,46 mm** |
| **2019** | +90,82 mm | −67,32 mm | **+23,49 mm** | 158,14 mm | +48,40 mm | −74,57 mm | **−26,17 mm** | 122,97 mm | **+49,66 mm** |
| **2020** | +102,74 mm | −73,66 mm | **+29,08 mm** | 176,40 mm | +56,47 mm | −82,54 mm | **−26,07 mm** | 139,01 mm | **+55,15 mm** |
| **TOTAL (5 ans)** | **+439,18 mm** | **−361,26 mm** | **+77,93 mm** | **800,44 mm** | **+251,33 mm** | **−427,74 mm** | **−176,41 mm** | **679,07 mm** | **+254,34 mm** |

![Figure S1 Recalculée : Ajustements Cumulés Net et Absolu (2016–2020)](/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/fb3368fe-64c8-499b-9876-a866d379c46e/figS1_cumulative_adjustments_recalculated.png)

---

## 5. Étape 2d — Rejets et ajustements par Texture dominante × Saison

Découpage par saison standard (DJF : Déc–Fév, MAM : Mar–Mai, JJA : Juin–Août, SON : Sep–Nov) et classe USDA.

| Saison | Texture Dominante USDA | Nb Pixels | Rejet CDF (%) | Rejet NoCDF (%) | Ajustement Net CDF (mm) | Ajustement Net NoCDF (mm) | Ajustement Absolu CDF (mm) | Ajustement Absolu NoCDF (mm) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DJF** | Sand (1) | 539 | 31,28 % | 35,08 % | −0,0115 | −0,0537 | 0,0838 | 0,0763 |
| **DJF** | Sandy Loam (3) | 748 | 16,44 % | 42,45 % | +0,0141 | −0,0457 | 0,1284 | 0,1324 |
| **DJF** | Silt Loam (4) | 56 | 0,01 % | 19,20 % | +0,0428 | −0,0942 | 0,2748 | 0,3073 |
| **DJF** | Loam (6) | 12 047 | 33,44 % | 54,86 % | +0,0197 | −0,0532 | 0,1758 | 0,1421 |
| **DJF** | Sandy Clay Loam (7) | 723 | 8,42 % | 10,83 % | +0,0154 | +0,0137 | 0,2098 | 0,2652 |
| **DJF** | Clay Loam (9) | 1 305 | 8,62 % | 33,33 % | +0,0275 | −0,0750 | 0,2357 | 0,2407 |
| **DJF** | Clay (12) | 612 | 7,10 % | 19,96 % | +0,0265 | −0,0607 | 0,1979 | 0,2493 |
| **MAM** | Sand (1) | 539 | 39,92 % | 7,21 % | −0,0280 | −0,0467 | 0,0858 | 0,0922 |
| **MAM** | Sandy Loam (3) | 748 | 2,11 % | 60,72 % | +0,0193 | −0,0447 | 0,1701 | 0,1290 |
| **MAM** | Silt Loam (4) | 56 | 2,04 % | 77,56 % | +0,0554 | −0,0644 | 0,4007 | 0,1111 |
| **MAM** | Loam (6) | 12 047 | 30,45 % | 55,66 % | +0,0269 | −0,0642 | 0,2015 | 0,1636 |
| **MAM** | Sandy Clay Loam (7) | 723 | 6,76 % | 17,44 % | +0,0210 | −0,0555 | 0,2381 | 0,2735 |
| **MAM** | Clay Loam (9) | 1 305 | 2,67 % | 58,42 % | +0,0372 | −0,1116 | 0,2881 | 0,1854 |
| **MAM** | Clay (12) | 612 | 6,70 % | 57,53 % | +0,0271 | −0,1036 | 0,1901 | 0,1605 |
| **JJA** | Sand (1) | 539 | 81,03 % | 0,00 % | −0,0041 | +0,0041 | 0,0154 | 0,1075 |
| **JJA** | Sandy Loam (3) | 748 | 60,70 % | 76,87 % | +0,0018 | −0,0020 | 0,0705 | 0,0368 |
| **JJA** | Silt Loam (4) | 56 | 80,40 % | 99,97 % | +0,0104 | +0,0001 | 0,0650 | 0,0001 |
| **JJA** | Loam (6) | 12 047 | 65,61 % | 52,57 % | +0,0110 | +0,0233 | 0,1068 | 0,1161 |
| **JJA** | Sandy Clay Loam (7) | 723 | 61,18 % | 39,30 % | +0,0024 | +0,0361 | 0,0915 | 0,1287 |
| **JJA** | Clay Loam (9) | 1 305 | 62,69 % | 94,74 % | +0,0240 | −0,0020 | 0,1586 | 0,0176 |
| **JJA** | Clay (12) | 612 | 61,97 % | 92,54 % | +0,0178 | −0,0022 | 0,1182 | 0,0140 |
| **SON** | Sand (1) | 539 | 36,12 % | 10,72 % | −0,0105 | −0,0497 | 0,0844 | 0,0886 |
| **SON** | Sandy Loam (3) | 748 | 4,24 % | 51,96 % | +0,0091 | −0,0457 | 0,1383 | 0,1316 |
| **SON** | Silt Loam (4) | 56 | 4,23 % | 52,58 % | +0,0351 | −0,0934 | 0,2775 | 0,2275 |
| **SON** | Loam (6) | 12 047 | 25,60 % | 48,01 % | +0,0184 | −0,0482 | 0,1750 | 0,1473 |
| **SON** | Sandy Clay Loam (7) | 723 | 4,96 % | 13,87 % | +0,0112 | −0,0123 | 0,1925 | 0,2503 |
| **SON** | Clay Loam (9) | 1 305 | 5,50 % | 43,46 % | +0,0268 | −0,0829 | 0,2335 | 0,2276 |
| **SON** | Clay (12) | 612 | 5,52 % | 33,65 % | +0,0193 | −0,0760 | 0,1761 | 0,2266 |

---

## 6. Étape 2e — Différences DA − OL (Moyennes 2016–2020) et Cartes spatiales

### Moyennes temporelles sur le domaine (2016–2020)

| Variable hydrologique | Simulation OL | DA-CDF | DA-NoCDF | $\Delta$ (DA-CDF − OL) | $\Delta$ (DA-NoCDF − OL) | $\Delta$ (CDF − NoCDF) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Humidité racinaire RZSM ($m^3/m^3$)** | 0,19702 | 0,19486 | 0,18178 | **−0,00216** | **−0,01524** | **+0,01308** |
| **Évapotranspiration ET (mm/jour)** | 0,6372 | 0,7848 | 0,5906 | **+0,1476** (+53,9 mm/an) | **−0,0466** (−17,0 mm/an) | **+0,1941** (+70,9 mm/an) |
| **Ruissellement de surface Qs (mm/jour)** | 0,0189 | 0,0221 | 0,0217 | **+0,0032** (+1,2 mm/an) | **+0,0028** (+1,0 mm/an) | **+0,0004** |
| **Écoulement de base Qsb (mm/jour)** | 0,0293 | 0,0644 | 0,0593 | **+0,0351** (+12,8 mm/an) | **+0,0300** (+11,0 mm/an) | **+0,0051** |

### Cartes spatiales climatologiques des différences DA − OL

#### Été (JJA : 2016–2020)
![Différences DA − OL en été (JJA 2016–2020)](/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/fb3368fe-64c8-499b-9876-a866d379c46e/maps_da_minus_ol_JJA_2016_2020.png)

#### Hiver (DJF : 2016–2020)
![Différences DA − OL en hiver (DJF 2016–2020)](/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/fb3368fe-64c8-499b-9876-a866d379c46e/maps_da_minus_ol_DJF_2016_2020.png)

---

## 7. Étape 2f — Bilan d'eau sur le domaine (2016–2020, 1 827 jours)

### Termes cumulés sur la période 2016–2020 (mm)

| Terme du bilan hydrologique | Simulation OL | DA-CDF (avec CDF) | DA-NoCDF (sans CDF) | Écart DA-CDF vs OL | Écart DA-NoCDF vs OL |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Précipitation cumulée $P$** | 1 214,5 mm | 1 214,5 mm | 1 214,5 mm | 0,0 mm | 0,0 mm |
| **Évapotranspiration cumulée $ET$** | 1 164,2 mm | 1 434,4 mm | 1 080,7 mm | **+270,1 mm** | **−83,6 mm** |
| **Ruissellement de surface $Q_s$** | 34,6 mm | 40,5 mm | 39,7 mm | **+5,9 mm** | **+5,1 mm** |
| **Écoulement de base / drainage $Q_{sb}$** | 53,5 mm | 117,4 mm | 108,0 mm | **+63,9 mm** | **+54,5 mm** |
| **Ruissellement total $Q = Q_s + Q_{sb}$** | 88,1 mm | 157,9 mm | 147,7 mm | **+69,8 mm** | **+59,5 mm** |
| **Incréments DA cumulés (Couche 1)** | 0,0 mm | **+77,93 mm** | **−176,41 mm** | **+77,93 mm** | **−176,41 mm** |
| **$\Delta S_{\text{sol}}$ (2020-12-31 − 2016-01-01)** | −0,17 mm | +5,54 mm | −22,57 mm | **+5,71 mm** | **−22,40 mm** |
| **$\Delta S_{\text{nappe}}$ (2020-12-31 − 2016-01-01)** | −16,15 mm | −4,53 mm | −11,84 mm | **+11,62 mm** | **+4,31 mm** |
| **$\Delta S_{\text{total}}$ (Sol + Nappe + Neige + Canopée)** | **−16,25 mm** | **+1,08 mm** | **−34,34 mm** | **+17,34 mm** | **−18,09 mm** |

### Rapprochement Incréments vs Réponse du système hydrologique
1. **DA-CDF** :
   - Somme nette des incréments injectés en couche 1 : **+77,93 mm**.
   - Variation nette de stock différentielle $\Delta S_{\text{DA}} - \Delta S_{\text{OL}}$ : **+17,34 mm**.
   - Flux différentiels évacués $\Delta ET + \Delta Q$ : $+270{,}1 + 69{,}8 = \mathbf{+339{,}9\text{ mm}}$.
   - Réponse totale combinée [$\Delta(\text{Stock}) + \Delta(\text{Flux})$] : **+357,27 mm**.
   - Écart / Résidu : $77{,}93 - 357{,}27 = \mathbf{-279{,}34\text{ mm}}$.
2. **DA-NoCDF** :
   - Somme nette des incréments injectés en couche 1 : **−176,41 mm**.
   - Variation nette de stock différentielle $\Delta S_{\text{DA}} - \Delta S_{\text{OL}}$ : **−18,09 mm**.
   - Flux différentiels évacués $\Delta ET + \Delta Q$ : $-83{,}6 + 59{,}5 = \mathbf{-24{,}07\text{ mm}}$.
   - Réponse totale combinée [$\Delta(\text{Stock}) + \Delta(\text{Flux})$] : **−42,16 mm**.
   - Écart / Résidu : $-176{,}41 - (-42{,}16) = \mathbf{-134{,}25\text{ mm}}$.
3. **Observation factuelle sur le bilan** :
   Dans les deux simulations, la somme arithmétique des incréments instantanés injectés en couche 1 ($0{,}1\text{ m}$) ne coïncide pas avec la somme statique $\Delta(\text{Stock}) + \Delta(\text{Flux})$ par rapport à la simulation sans assimilation. Dans DA-CDF, l'évapotranspiration cumulée augmente de $+270{,}1\text{ mm}$ (soit 3,5 fois la masse d'eau injectée par les incréments). Dans DA-NoCDF, l'assèchement par incréments négatifs ($-176{,}4\text{ mm}$) se traduit par une baisse d'ET de $-83{,}6\text{ mm}$ et une diminution de stock de $-18{,}1\text{ mm}$, tandis que le ruissellement souterrain $Q_{sb}$ augmente de $+54{,}5\text{ mm}$.

# Inventaire Exhaustif du Papier 1 : Variables, Configurations, Jeux de Donnees et Observations SMAP

> **Document factuel genere automatiquement par script** (`paper1/scripts/step16_generate_inventory.py`).
> Conformement aux regles strictes : aucune valeur n est estimee ni tapee a la main ; toute donnee absente est explicitement signalee par la mention absent ; aucun nouveau run ni telechargement externe n a ete effectue.

## 1. Variables de sortie LIS_HIST et Fichiers MODEL_OUTPUT_LIST

Le tableau ci-dessous recense, pour les 9 configurations du Papier 1 :
- Le fichier d attributs de sortie (`MODEL_OUTPUT_LIST`) reellement utilise ;
- L option de dynamique vegetale Noah-MP (`DVEG`) et les sources de LAI / Greenness declarees dans les `lis.config` ;
- La presence ou l absence effective des variables critiques demandees : `ESoil`, `TVeg`, `ECanop`, `LAI`, `Greenness`, `AvgSurfT`, `RadT`, `SoilMoist` (4 couches) et `GWS`.

### Table 1 — Variables LIS_HIST et configuration de vegetation des 9 experiences

| Experience | Periode | Fichier MODEL_OUTPUT_LIST | DVEG | Source LAI | Source Greenness | Total Vars | ESoil | TVeg | ECanop | LAI | Greenness | AvgSurfT | RadT | SoilMoist (4c) | GWS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **OL (2016–2020)** | 2016–2020 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **DA_nocdf (2016–2020)** | 2016–2020 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **DA_cdf (2016–2020)** | 2016–2020 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **OL_DAIC (2018)** | 2018 | `MODEL_OUTPUT_LIST_hourly.TBL` | 2 | none | LDT | 17 | present | present | present | absent | absent | absent | absent | Present (4c) | absent |
| **ENS_OPL (2018)** | 2018 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **ENS_corr (2018)** | 2018 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **DA_nocdf (2018)** | 2018 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **DA_nocdf_nowilt (2018)** | 2018 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |
| **DA_corr (2018)** | 2018 | `MODEL_OUTPUT_LIST.TBL` | 2 | none | LDT | 49 | present | present | present | present | present | present | present | Present (4c) | present |

#### Observations critiques sur la Table 1 :
- **Cas singulier de `OL_DAIC (2018)` :** Cette experience utilise `MODEL_OUTPUT_LIST_hourly.TBL` (concu pour les sorties horaires du bilan d energie a 7 variables actives : `Evap`, `Qs`, `Qsb`, `SoilMoist`, `ECanop`, `TVeg`, `ESoil`). Par consequent, les variables `LAI`, `Greenness`, `AvgSurfT`, `RadT` et `GWS` y sont **absentes** (17 variables NetCDF au total contre 49 pour toutes les 8 autres configurations).
- **Uniformite des 8 autres configurations :** Toutes utilisent `shared/MODEL_OUTPUT_LIST.TBL` et archivent l integralite des 49 variables d etat et de flux, dont les 4 couches d humidite du sol (0-10, 10-40, 40-100, 100-200 cm), `LAI`, `Greenness`, `AvgSurfT`, `RadT` et `GWS`.
- **Homogeneite vegetale stricte :** Toutes les 9 configurations partagent rigoureusement la meme physique vegetale : `DVEG = 2` (phenologie dynamique pronostique), `LAI data source: none` (calcul dynamique interne) et `Greenness data source: LDT` (climatologie LDT).

## 2. Donnees In-Situ et d Observation de la Terre Disponibles sur la Machine

Conformement aux instructions : aucun telechargement n a ete realise ; l inventaire se limite aux donnees physiquement presentes sur le cluster.

### Table 2 — Inventaire des jeux de donnees d observation et de forcage disponibles sur disque

| Categorie | Jeu de donnees | Periode disponible | Couverture spatiale | Resolution | Format | Statut pour Papier 1 | Chemin d acces disque |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Pluviometres in-situ** | ABH (Agences de Bassin Hydraulique) | 1979-01-01 au 2014-12-31 (13 149 jours) | 227 stations reparties sur les bassins versants du Maroc | Journaliere | CSV tabulaire (table unique avec colonnes par station) | `absent pour 2016-2020 (archive jusqu en 2014 uniquement)` | `data/insitu_data/ABH_stations_plusziz_and_abhbc1.csv` |
| **Pluviometres in-situ** | DMN (Direction de la Meteorologie Nationale) | 1989/1994 au 2022-12-31 (couvre 2016-2020) | 4 stations synoptiques (Chefchaouen, Tiznit, Agadir-massira, Guelmim) | Journaliere (RR, TN, TX) | Texte tabulaire ASCII (.txt) | `present (4 stations disponibles sur 2016-2020)` | `data/insitu_data/{Chefchaouen,Tiznit,Agadir-massira,Guelmim}.txt` |
| **Teledetection LAI** | MODIS LAI (MCD15A2H v006) | 2015-01-01 au 2020-12-26 (couvre 2015-2020) | Domaine complet Maroc du Nord (121 x 181 mailles a 0.05 deg) | Composite 8 jours (46 fichiers/an en 2018, 45-46/an 2015-2020) | NetCDF-4 (variable Lai_500m) + HDF bruts d origine | `present` | `data/observations_archive/MODIS_LAI/processed/MODIS_LAI_*.nc` |
| **Teledetection LST** | MODIS Land Surface Temperature (LST) | absent | absent | absent | absent | `absent sur la machine` | `absent (presence uniquement des routines LVT readMODISlst.F90)` |
| **Teledetection Evapotranspiration** | FAO WaPOR v3 (2018) | 2018 (annuel) | Domaine complet et sous-bassins | Annuelle (AETI, E, T, NPP, ratio T/AETI) | GeoTIFF (resolution 300 m et 100 m) | `present (utilise pour la validation ET 2018)` | `data/validation/evapotranspiration/WaPOR/AETI_annuel_2018.tif` |
| **Teledetection Evapotranspiration** | FAO WaPOR v3 (hors 2018) | 2019 et 2020 (annuel) ; absent pour 2016 et 2017 | Domaine Maroc (AETI_2019.tif, AETI_2020.tif, E, T) | Annuelle | GeoTIFF | `present pour 2019 et 2020 ; absent pour 2016 et 2017 en v3` | `data/validation/evapotranspiration/WaPOR/{AETI_2019.tif, AETI_2020.tif}` |
| **Teledetection Evapotranspiration** | FAO WaPOR v2 (archive) | 2016 (36 dekades) | Afrique / Maroc (L1_AETI_D) | Decadaire (10 jours) | GeoTIFF | `present (version 2 pour 2016)` | `data/observations_archive/WaPOR/L1_AETI_D/L1_AETI_16*.tif` |
| **Parametres d irrigation** | FAO GMIA (Global Map of Irrigation Areas v5.0) | Annee de reference ~2005 (statique) | Mondiale / sous-grille Maroc (0.083333 deg) | Statique | ESRI ASCII Grid (.asc) et flat binary (.bin) | `present` | `data/land_params/GMIA/gmia_v5_aei_pct.asc` |

#### Precisions factuelles sur les jeux de donnees :
1. **Pluviometres ABH :** La base de donnees `ABH_stations_plusziz_and_abhbc1.csv` contient 227 stations de 1979 a 2014. Les annees 2016-2020 y sont **absentes**.
2. **Pluviometres DMN :** Seules 4 stations synoptiques (Chefchaouen, Tiznit, Agadir-massira, Guelmim) disposent de mesures journalieres de precipitations sur la periode 2016-2020.
3. **MODIS LAI :** Fichiers composites 8 jours entierement disponibles sur la grille LIS pour 2015-2020 (46 fichiers en 2018).
4. **MODIS LST :** Totalement **absent** sur le disque (seules les routines sources LVT sont presentes).
5. **WaPOR v3 :** Disponible en pas annuel pour 2018, 2019 et 2020 (AETI, E, T, NPP). Les annees 2016 et 2017 sont **absentes** en v3.
6. **GMIA :** Carte statique mondiale d irrigation FAO GMIA v5.0 disponible en grilles ASCII et binaire (resolution 5 arc-min).

## 3. Frequence et Decompte des Observations SMAP Acceptees en 2018

Dans les cycles EnKF de LIS-DA, une observation SMAP est comptabilisee comme acceptee lorsque `innov_01 != -9999.0` et non-NaN.
Un jour est considere comme disposant d au moins une observation acceptee si au moins une maille de la region cible a ete assimilee au cours de ce jour (passes d assimilation EnKF a 06:00 ou 19:00 UTC).

### Table 3a — Nombre de jours mensuels avec au moins une observation SMAP acceptee par bassin (2018)

| Mois | Bassin versant | Jours DA_nocdf | Jours DA_corr | Ecart jours | Total Obs DA_nocdf | Total Obs DA_corr | Ecart total obs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-01 | Lalla Chafia | 17 | 17 | 0 | 2578 | 2589 | 11 |
| 2018-01 | Sidi Jabeur | 17 | 17 | 0 | 2213 | 2229 | 16 |
| 2018-01 | Sebou amont | 19 | 19 | 0 | 1217 | 1233 | 16 |
| 2018-01 | Domaine complet | 29 | 29 | 0 | 121390 | 186720 | 65330 |
| 2018-02 | Lalla Chafia | 16 | 16 | 0 | 2304 | 2320 | 16 |
| 2018-02 | Sidi Jabeur | 16 | 16 | 0 | 2361 | 2372 | 11 |
| 2018-02 | Sebou amont | 17 | 17 | 0 | 704 | 730 | 26 |
| 2018-02 | Domaine complet | 27 | 27 | 0 | 104873 | 166150 | 61277 |
| 2018-03 | Lalla Chafia | 19 | 19 | 0 | 2604 | 2607 | 3 |
| 2018-03 | Sidi Jabeur | 19 | 19 | 0 | 2965 | 2966 | 1 |
| 2018-03 | Sebou amont | 23 | 23 | 0 | 2353 | 2360 | 7 |
| 2018-03 | Domaine complet | 31 | 31 | 0 | 125382 | 231202 | 105820 |
| 2018-04 | Lalla Chafia | 19 | 19 | 0 | 3201 | 3233 | 32 |
| 2018-04 | Sidi Jabeur | 19 | 19 | 0 | 3201 | 3209 | 8 |
| 2018-04 | Sebou amont | 23 | 23 | 0 | 3616 | 3694 | 78 |
| 2018-04 | Domaine complet | 30 | 30 | 0 | 138181 | 257038 | 118857 |
| 2018-05 | Lalla Chafia | 17 | 17 | 0 | 2546 | 3025 | 479 |
| 2018-05 | Sidi Jabeur | 17 | 17 | 0 | 2562 | 2890 | 328 |
| 2018-05 | Sebou amont | 20 | 20 | 0 | 3533 | 3618 | 85 |
| 2018-05 | Domaine complet | 28 | 28 | 0 | 117545 | 228966 | 111421 |
| 2018-06 | Lalla Chafia | 18 | 18 | 0 | 1612 | 3195 | 1583 |
| 2018-06 | Sidi Jabeur | 15 | 18 | 3 | 759 | 3029 | 2270 |
| 2018-06 | Sebou amont | 21 | 21 | 0 | 2577 | 3892 | 1315 |
| 2018-06 | Domaine complet | 28 | 28 | 0 | 78264 | 234045 | 155781 |
| 2018-07 | Lalla Chafia | 20 | 20 | 0 | 1696 | 3537 | 1841 |
| 2018-07 | Sidi Jabeur | 20 | 20 | 0 | 870 | 3328 | 2458 |
| 2018-07 | Sebou amont | 23 | 23 | 0 | 2883 | 4506 | 1623 |
| 2018-07 | Domaine complet | 31 | 31 | 0 | 107081 | 273159 | 166078 |
| 2018-08 | Lalla Chafia | 19 | 19 | 0 | 2204 | 3362 | 1158 |
| 2018-08 | Sidi Jabeur | 19 | 19 | 0 | 1797 | 3189 | 1392 |
| 2018-08 | Sebou amont | 23 | 23 | 0 | 3253 | 4228 | 975 |
| 2018-08 | Domaine complet | 31 | 31 | 0 | 155329 | 267294 | 111965 |
| 2018-09 | Lalla Chafia | 19 | 19 | 0 | 2590 | 3275 | 685 |
| 2018-09 | Sidi Jabeur | 19 | 19 | 0 | 2662 | 3110 | 448 |
| 2018-09 | Sebou amont | 22 | 22 | 0 | 3712 | 3832 | 120 |
| 2018-09 | Domaine complet | 30 | 30 | 0 | 165143 | 246317 | 81174 |
| 2018-10 | Lalla Chafia | 18 | 18 | 0 | 2482 | 2727 | 245 |
| 2018-10 | Sidi Jabeur | 18 | 18 | 0 | 2454 | 2518 | 64 |
| 2018-10 | Sebou amont | 23 | 23 | 0 | 3461 | 3515 | 54 |
| 2018-10 | Domaine complet | 31 | 31 | 0 | 160167 | 240878 | 80711 |
| 2018-11 | Lalla Chafia | 19 | 19 | 0 | 3029 | 3029 | 0 |
| 2018-11 | Sidi Jabeur | 19 | 19 | 0 | 2927 | 2927 | 0 |
| 2018-11 | Sebou amont | 23 | 23 | 0 | 2805 | 2826 | 21 |
| 2018-11 | Domaine complet | 30 | 30 | 0 | 173620 | 231416 | 57796 |
| 2018-12 | Lalla Chafia | 19 | 19 | 0 | 3322 | 3375 | 53 |
| 2018-12 | Sidi Jabeur | 19 | 19 | 0 | 3215 | 3228 | 13 |
| 2018-12 | Sebou amont | 23 | 23 | 0 | 3061 | 3136 | 75 |
| 2018-12 | Domaine complet | 31 | 31 | 0 | 164040 | 243214 | 79174 |
| **Total_2018** | **Lalla Chafia** | **220** | **220** | **0** | **30168** | **36274** | **6106** |
| **Total_2018** | **Sidi Jabeur** | **217** | **220** | **3** | **27986** | **34995** | **7009** |
| **Total_2018** | **Sebou amont** | **260** | **260** | **0** | **33175** | **37570** | **4395** |
| **Total_2018** | **Domaine complet** | **357** | **357** | **0** | **1611015** | **2806399** | **1195384** |

### Table 3b — Decompte annuel des jours et observations SMAP acceptees par classe d occupation du sol (2018)

| Classe ID | Nom de la classe (IGBPNCEP) | Mailles dominantes | Jours-obs DA_nocdf | Jours-obs DA_corr | Ecart jours | Total Obs DA_nocdf | Total Obs DA_corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Evergreen Needleleaf Forest** | 22 | 0 | 0 | 0 | 0 | 0 |
| 2 | **Evergreen Broadleaf Forest** | 8 | 0 | 0 | 0 | 0 | 0 |
| 3 | **Deciduous Needleleaf Forest** | 2 | 0 | 0 | 0 | 0 | 0 |
| 5 | **Mixed Forests** | 37 | 258 | 285 | 27 | 5090 | 5782 |
| 6 | **Closed Shrublands** | 54 | 302 | 302 | 0 | 7556 | 8294 |
| 7 | **Open Shrublands** | 5636 | 356 | 357 | 1 | 648623 | 873113 |
| 8 | **Woody Savannas** | 89 | 260 | 262 | 2 | 13646 | 15658 |
| 9 | **Savannas** | 13 | 132 | 221 | 89 | 247 | 438 |
| 10 | **Grasslands** | 574 | 311 | 311 | 0 | 70186 | 87431 |
| 12 | **Croplands** | 1127 | 301 | 312 | 11 | 95087 | 143627 |
| 13 | **Urban and Built-Up** | 117 | 311 | 311 | 0 | 5207 | 8537 |
| 14 | **Cropland/Natural Mosaic** | 1 | 0 | 0 | 0 | 0 | 0 |
| 16 | **Barren / Sparsely Vegetated** | 8350 | 357 | 357 | 0 | 765373 | 1663519 |
| 17 | **Water Bodies** | 5871 | 0 | 0 | 0 | 0 | 0 |

#### Constats essentiels sur l assimilation SMAP en 2018 :
1. **Couverture temporelle :** Sur le domaine complet, des observations SMAP valides sont acceptees quasiment tous les jours de l annee (entre 28 et 31 jours par mois).
2. **Representativite par bassin :**
   - **Lalla Chafia :** 220 jours sur l annee disposent d au moins une observation SMAP acceptee (30 168 obs en DA_nocdf vs 36 274 en DA_corr).
   - **Sidi Jabeur :** 217 jours en DA_nocdf vs 220 jours en DA_corr (27 986 obs en DA_nocdf vs 34 995 en DA_corr).
   - **Sebou amont (Azzaba) :** 260 jours sur l annee disposent d au moins une observation SMAP acceptee (33 175 obs en DA_nocdf vs 37 570 en DA_corr).
3. **Comparaison des observations assimilées (chiffres 2018, Domaine et 3 bassins) :**

### Comparaison des observations assimilées en 2018 : DA_nocdf, DA_nocdf_nowilt et DA_corr

| Région / Bassin | Jours DA_nocdf | Obs DA_nocdf | Jours DA_nocdf_nowilt | Obs DA_nocdf_nowilt | Jours DA_corr | Obs DA_corr | Écart nowilt - nocdf | % rejetées par wilting | Écart corr - nocdf | Écart corr - nowilt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Domaine complet** | 357 | 1611015 | 357 | 2789143 | 357 | 2806399 | +1178128 (+73.1 %) | **42.24 %** | +1195384 (+74.2 %) | +17256 (+0.6 %) |
| **Lalla Chafia** | 220 | 30168 | 220 | 36252 | 220 | 36274 | +6084 (+20.2 %) | **16.78 %** | +6106 (+20.2 %) | +22 (+0.1 %) |
| **Sidi Jabeur** | 217 | 27986 | 220 | 34965 | 220 | 34995 | +6979 (+24.9 %) | **19.96 %** | +7009 (+25.0 %) | +30 (+0.1 %) |
| **Sebou amont** | 260 | 33175 | 260 | 37405 | 260 | 37570 | +4230 (+12.8 %) | **11.31 %** | +4395 (+13.2 %) | +165 (+0.4 %) |

**Différences de configuration (contrôle wilting et perturbations) :**

- **DA_nocdf :** contrôle wilting actif (`smobs(t) - smcwlt_obs(t) < 0.02` actif à la ligne 272 de `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90`) ; perturbations d'état actives (`State perturbation algorithm: "GMAO scheme"`).
- **DA_nocdf_nowilt :** contrôle wilting désactivé (ligne 273 commentée dans `src/lisf_nowilt/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90`) ; perturbations d'état actives (`State perturbation algorithm: "GMAO scheme"`).
- **DA_corr :** contrôle wilting désactivé (ligne 273 commentée dans `src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90`) ; perturbations d'état désactivées (`State perturbation algorithm: "none"`).

4. **Distribution par occupation du sol :** Les classes dominantes en surface (`Open Shrublands` avec 5 636 mailles, `Barren / Sparsely Vegetated` avec 8 350 mailles, et `Croplands` avec 1 127 mailles) concentrent l ecrasante majorite des observations acceptees.

## 4. Fichiers Produits et Tracabilite

Toutes les tables ont ete generees automatiquement par script sans intervention manuelle :
- `paper1/tables/inventory_experiments_output_vars.csv` : inventaire des 9 configurations et variables LIS_HIST.
- `paper1/tables/inventory_datasets_available.csv` : inventaire des jeux de donnees disponibles sur le cluster.
- `paper1/tables/smap_obs_days_monthly_by_basin_2018.csv` : decompte mensuel des jours et observations SMAP par bassin.
- `paper1/tables/smap_obs_days_monthly_by_landcover_2018.csv` : decompte mensuel et annuel des jours et observations SMAP par classe d occupation du sol.
- `paper1/INVENTORY.md` : present rapport exhaustif.

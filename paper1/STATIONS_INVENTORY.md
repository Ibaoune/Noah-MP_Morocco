# Inventaire des pluviomètres — ABH_stations_plusziz_and_abhbc.csv

Généré par `paper1/scripts/stations_inventory.py` le 2026-11-23 18:04. Lecture seule : aucune donnée source modifiée, aucun téléchargement.

Fichier : `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/SCRIPTS/paper_dataset_precip/data/raw/stations/ABH_stations_plusziz_and_abhbc.csv`

## 1. Structure

- Taille : 119343511 octets (113.8 Mio)
- Lignes (en-tête inclus) : 2392288
- Séparateur détecté : `,`
- Lignes de données : 2392287 ; colonnes : 5

6 premières lignes brutes :

```
Date,Station,Precipitation,Longitude,Latitude
1979-01-01,ABADLA,0.0,-8.56566475094,31.7210232103
1979-01-02,ABADLA,0.0,-8.56566475094,31.7210232103
1979-01-03,ABADLA,0.0,-8.56566475094,31.7210232103
1979-01-04,ABADLA,1.0,-8.56566475094,31.7210232103
1979-01-05,ABADLA,6.6,-8.56566475094,31.7210232103
```

| Colonne | Type inféré (pandas, 200 000 premières lignes) | Cellules vides | Valeurs non convertibles |
|---|---|---|---|
| Date | str | 0 | 0 |
| Station | str | 0 | n/a |
| Precipitation | float64 | 0 | 0 |
| Longitude | float64 | 0 | 0 |
| Latitude | float64 | 0 | 0 |

- Format : **long** (une ligne par couple station × date ; colonnes `Date`, `Station`, `Precipitation`, `Longitude`, `Latitude`).

## 2. Contenu

- Nombre de stations (valeurs distinctes de `Station`) : **227**
- Identifiant : seule la colonne `Station` (nom en texte) identifie les stations ; aucune colonne d'identifiant numérique.
- Nom : colonne `Station`.
- Source (ABH/DGM) : **aucune colonne du fichier ne l'indique** (colonnes présentes : `Date`, `Station`, `Precipitation`, `Longitude`, `Latitude`).
  - Le `README.md` du même dossier déclare 34 stations DGM + 183 stations ABH = 217 stations, et 10 mailles ERA5 auxiliaires dans le sud ; cette répartition n'est pas codée dans le fichier.
  - Stations dont le nom est une seule lettre majuscule : 10 (A, B, C, D, E, F, G, H, I, J) ; stations restantes : 217.
- Coordonnées : présentes (colonnes `Longitude`, `Latitude`) ; unité et système de référence non indiqués dans le fichier.
  - Longitude : min -16.00000, max -1.90000
  - Latitude : min 22.00000, max 35.85871
  - Stations avec plus d'un couple de coordonnées : 0
  - Stations partageant exactement les mêmes coordonnées qu'une autre station : 0
- Altitude : **absente** du fichier.

## 3. Temps et valeurs

- Période totale : 1979-01-01 → 2014-12-31
- Pas de temps : écarts entre dates successives (par station, doublons exclus) — 2371833 écarts de 1 jour sur 2386054 ; 14221 écarts > 1 jour (lacunes) ; écart max 7184 jours.
- Unité des valeurs : non indiquée dans le fichier (en-tête `Precipitation`). Le `README.md` du dossier mentionne des « daily precipitation records ».
- Valeurs de `Precipitation` : min 0.0, max 450.0, moyenne 1.1311
- Code de valeur manquante : aucune cellule vide, aucune valeur non numérique (0 NaN) ; valeurs sentinelles testées : -999 → 0, -9999 → 0, -99 → 0, -1 → 0, 999 → 0, 9999 → 0.
  Les jours manquants correspondent à des dates **absentes** du fichier (pas de ligne).
- Valeurs négatives : **0**
- Valeurs > 300 mm/jour : **6** (non corrigées)

| Station | Date | Precipitation |
|---|---|---|
| AMENZAL | 2006-04-24 | 450.0 |
| BENI HITEM | 1997-01-03 | 420.0 |
| BGE 9 AVRIL | 1996-12-20 | 440.0 |
| JEBEL OUDKA | 2001-01-18 | 360.0 |
| SAHEL(AZLA) | 1986-02-01 | 384.0 |
| SAHEL(AZLA) | 1998-02-01 | 336.0 |

- Couples (station, date) dupliqués : 6006 lignes en surplus ; 6006 couples concernés dont 1430 avec des valeurs différentes ; 16 stations concernées (AIT BOUIJAN, AIT_HADDOU, ALNIF, AMOUGAR TAGHIA, BOUAANANE, FOUM TILLICHT, MZIZL, RERFOUD, TADIGHOUST, TAGHZOUTE, TAMTETOUCHT, TAOUZ, TAZARINE, TAZOUGUERT, TITNAISSA, ZOUIASIDIHAMZAAA).

## 4. Couverture 2001-01-01 → 2014-12-31

- Nombre de jours de la période : 5113
- Jour valide : date présente dans le fichier pour la station, valeur numérique non manquante et ≥ 0 (doublons comptés une fois ; valeurs > 300 mm/jour conservées).
- Stations avec ≥ 80 % de jours valides : **191** / 227
  - dont stations au nom d'une seule lettre : 10
- Stations avec 0 % (aucune donnée sur la période) : 1

| Classe de % valide | Stations |
|---|---|
| 0 % | 1 |
| ]0–20[ % | 5 |
| [20–40[ % | 9 |
| [40–60[ % | 8 |
| [60–80[ % | 13 |
| [80–95[ % | 16 |
| [95–100] % | 175 |

Le détail par station est dans `paper1/tables/stations_inventory.csv`.

## 5. Position par rapport aux bassins

- Hypothèse de calcul : coordonnées des stations lues comme longitude/latitude WGS84 (EPSG:4326), le fichier n'indiquant pas de système de référence ; reprojetées dans le SCR de chaque contour.
- Bouregreg et Sebou : test point-dans-polygone (bord inclus). Le contour « Sebou » disponible est `domain/NorthMor/Basins_limits/Limite_ABHS_Export.shp` (attribut `Agence=ABHS`) ; une copie aux attributs identiques existe sous `domain/sebou/shapefiles/Sebou_limits/Limite_ABHS.shp`.
- Lalla Chafia et Sidi Jabeur : aucun polygone dans le dépôt ; les bassins amont sont des ensembles de mailles HyMAP obtenus par remontée D8 (même algorithme et mêmes exutoires que `paper1/scripts/step13_upstream_catchments_da_corr.py`). Une station est comptée si la maille qui la contient appartient à l'ensemble.

| Bassin | Contour utilisé | SCR / attributs | Stations dans le bassin | dont ≥ 80 % valides 2001–2014 | Stations ≥ 80 % |
|---|---|---|---|---|---|
| Bouregreg | `domain/NorthMor/Basins_limits/BV_Bouregreg_ExportFeatures.shp` | EPSG:26191 ; HydroID=518; Name=BOUREGREG | 10 | 9 | AL, AZR, LC, OH, RF, SJB, SMC, TIGZA, TS |
| Sebou | `domain/NorthMor/Basins_limits/Limite_ABHS_Export.shp` | EPSG:3857 ; Agence=ABHS | 46 | 40 | AGUELMAM SIDI ALI, AIN AICHA, AIN BITTIT, AIN TIMDRINE, AIT KHEBACH, AZIB SOLTANE, AZZABA, BAB ECHHOUB, BAB MERZOUKA, BAB OUENDER, BELKSIRI, BOUFLOU, BOURED, DAR ARSSA, DAR HAMRA, DRH FES, EL MALHA, EL MERS, FES, GALEZ, HAD KOURT, HAJIRIA, IFRANE, JEBEL OUDKA, KENITRA, KHAROUBA, KHENICHET, LALLA MIMOUNA, MEKNES, MY ALI CHERIF, OUELJET SOLTANE, OULAD YAACOUB, PONT DE M'DEZ, PONT DE SEBOU RP26, RATBA, SIDI MOKHEFI, SIDISLIMANE, TABOUDA, TAZA, ZRARDA |
| Lalla Chafia (amont HyMAP) | `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` (D8 HyMAP, exutoire ligne 75, colonne 71 ; 133 mailles de 0.05°) | centre maille exutoire : lat 33.775, lon -6.425 | 4 | 3 | LC, TIGZA, TS |
| Sidi Jabeur (amont HyMAP) | `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` (D8 HyMAP, exutoire ligne 71, colonne 71 ; 121 mailles de 0.05°) | centre maille exutoire : lat 33.575, lon -6.425 | 2 | 2 | OH, SJB |

## 6. Autres fichiers liés (non traités)

Dossiers parcourus : `data/raw/stations/` (y compris fichiers cachés) et `data/` (récursif, fichiers .csv/.xlsx/.xls/.txt).

| Fichier | Taille (octets) | Colonnes | Période (`Date`) | Stations distinctes | Lignes |
|---|---|---|---|---|---|
| `data/generated/interpolation_output/rf_yearly/CV_all_results.csv` | 594954 | n_estimators, max_features, min_samples_split, max_depth, rmse, date, n_neighbors | pas de colonne Date |  | 15876 |
| `data/intermediate/stations/ABH_cleaned.csv` | 119018850 | Date, Station, Precipitation, Longitude, Latitude | 1979-01-01 → 2014-12-31 | 227 | 2386281 |
| `data/intermediate/stations/ABH_cleaned_no_bad_months.csv` | 134356837 | Date, Station, Precipitation, Longitude, Latitude, Year, Month | 1979-01-01 → 2014-12-31 | 227 | 2354900 |
| `data/raw/Foldes/station_folds3.csv` | 18048 | Station, Latitude, Longitude, geometry, Region, IsSpecial, Fold | pas de colonne Date | 217 | 217 |
| `data/raw/Foldes/station_folds3.xlsx` | 17222 | non lu | | | |
| `data/raw/stations/.ipynb_checkpoints/Untitled-checkpoint.ipynb` | 72 | non lu | | | |

Racine `data/` = `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/SCRIPTS/paper_dataset_precip/data`. Non listés : 126 fichiers tabulaires sous `data/generated/hydrological_simulations/` (sorties de simulations GR4J/HBV par bassin, noms `simulated_b_*.xlsx`).

- `station_folds3.csv` : 217 stations avec coordonnées, `Region`, `IsSpecial` (True : 5) et `Fold` ; pas de colonne source ABH/DGM ni altitude.
  - Stations présentes seulement dans `station_folds3.csv` : 0 ; seulement dans le fichier principal : 10 (AFGHAL, AGADIR-MASSIRA, BOUARFA, GUELMIM, LARRACHE DPE, MARRAKECH1, NOUASSER, OUJDA HAMRI, SIDI MOKHEFI, TAGHZOUTE).
- Aucun fichier séparé DGM ou ABH n'a été trouvé dans `data/`.
- Hors dossier demandé, dans le dépôt NoahMP_Morocco : `domain/NorthMor/Basins_limits/Postes_pluvio.shp` (51 postes ; colonnes OBJECTID, Station, N__Poste, DMS, longitude, Latitude, De, Au, durée) ; `De` numérique min = 12420 (13 non numériques), `Au` numérique max = 43556 (18 non numériques) ; lus comme numéros de série Excel : 1934-01-01 → 2019-04-01.

## 7. Disponibilité IMERG V07B et MERRA-2 (2001–2014)

- IMERG : `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/IMERG/raw` — sous-dossiers mensuels 200006 → 202312 (261).
  - Produits datés 2001–2014 (préfixe, version → nombre de fichiers, tous sous-dossiers) : 3B-HHR V07B → 326821.
  - Pas de temps des fichiers : demi-horaire (`3B-HHR`, 48 créneaux/jour) ; pas de produit journalier.
  - Créneaux demi-horaires distincts 2001–2014 (date et heure lues dans le nom de fichier) : 243427 / 245424 attendus ; jours complets (48/48) : 4991 / 5113 ; jours partiels : 98 ; jours sans aucun fichier : 24.
    - Jours partiels : 20011130 (47), 20011231 (1), 20021104 (38), 20021105 (46), 20021107 (45), 20021112 (44), 20021114 (46), 20021115 (47), 20021119 (42), 20021122 (33), 20021123 (39), 20021130 (41), 20021203 (47), 20021204 (46), 20021208 (41), 20021209 (44), 20021212 (47), 20021213 (47), 20021216 (38), 20021217 (27), 20021218 (33), 20021220 (38), 20021221 (41), 20021222 (47), 20021228 (45), 20021231 (1), 20031101 (37), 20031102 (44), 20031103 (44), 20031110 (47), 20031111 (46), 20031117 (46), 20031118 (47), 20031119 (45), 20031120 (31), 20031121 (40), 20031128 (46), 20031202 (45), 20031207 (43), 20031208 (47), 20031211 (47), 20031212 (47), 20031215 (43), 20031216 (38), 20031217 (43), 20031219 (46), 20031220 (43), 20031228 (46), 20031231 (1), 20041203 (45), 20041207 (42), 20041208 (47), 20041227 (44), 20041231 (1), 20051105 (46), 20051107 (47), 20051108 (43), 20051113 (47), 20051114 (45), 20051115 (34), 20051116 (43), 20051117 (47), 20051123 (45), 20051127 (47), 20051202 (47), 20051210 (43), 20051211 (33), 20051212 (45), 20051214 (41), 20051215 (44), 20051222 (47), 20051231 (1), 20061208 (43), 20061218 (47), 20061225 (47), 20061228 (44), 20061231 (1), 20071027 (47), 20071102 (47), 20071105 (45), 20071106 (43), 20071111 (47), 20071112 (41), 20071113 (44), 20071121 (44), 20071124 (44), 20071129 (46), 20071130 (45), 20071202 (46), 20071203 (39), 20071204 (47), 20071206 (47), 20071207 (18), 20080630 (47), 20131231 (1), 20141031 (40), 20141130 (1), 20141231 (1).
    - Jours sans fichier : 20071208, 20071209, 20071210, 20071211, 20071212, 20071213, 20071214, 20071215, 20071216, 20071217, 20071218, 20071219, 20071220, 20071221, 20071222, 20071223, 20071224, 20071225, 20071226, 20071227, 20071228, 20071229, 20071230, 20071231.
  - Fichiers rangés dans un sous-dossier mensuel ne correspondant pas à leur date : 200806 → 83786.
  - Fichiers non rangés à la racine de `raw/` : 168 (préfixes : partial ; taille totale 243269632 octets ; 110 de taille nulle) ; non inclus dans les comptes ci-dessus.
  - Fichiers journaliers `3B-DAY*` sous `data/forcing/IMERG/` : 0.
  - `data/forcing/IMERG/subset/` : 0 fichier(s).
- MERRA-2 : `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2/M2T1NXFLX` (collection `tavg1_2d_flx_Nx`) — fichiers journaliers 20000101 → 20231002 (8348 fichiers).
  - Jours 2001–2014 attendus : 5113 ; présents : 4998 ; manquants : 115 (20020101, 20020123, 20020124, 20020201, 20020216, 20020225, 20020226, 20020307, 20020322, 20020323, 20020401, 20020404, 20020426, 20020507, 20020508, 20020526, 20020606, 20020607, 20020608, 20020624, 20020625, 20020627, 20020709, 20020722, 20020724, 20020730, 20020801, 20020806, 20020807, 20020821, 20020824, 20020901, 20020904, 20020906, 20020907, 20020911, 20020922, 20021001, 20021006, 20021008, 20021012, 20021017, 20021102, 20021126, 20021201, 20021208, 20021227, 20030108, 20030120, 20030207, 20030208, 20030209, 20030306, 20030308, 20030324, 20030401, 20030501, 20030601, 20030608, 20030627, 20030721, 20030724, 20030725, 20030801, 20030808, 20030820, 20030929, 20030930, 20031007, 20031010, 20031107, 20031120, 20031124, 20031126, 20031129, 20031201, 20031215, 20031224, 20031225, 20040101, 20040119, 20040126, 20040207, 20040225, 20040226, 20040310, 20040406, 20040426, 20040525, 20040527, 20040625, 20040629, 20040701, 20040716, 20040807, 20040808, 20040816, 20040831, 20040901, 20040906, 20040907, 20040908, 20040928, 20041001, 20041014, 20041024, 20041025, 20041101, 20041106, 20041107, 20041115, 20041127, 20041201, 20041208, 20041224).
  - Fichier témoin `MERRA2_300.tavg1_2d_flx_Nx.20010101.nc4` : 24 pas de temps, grille 361×576 ; variables de précipitation : `PRECANV` (kg m-2 s-1), `PRECCON` (kg m-2 s-1), `PRECLSC` (kg m-2 s-1), `PRECSNO` (kg m-2 s-1), `PRECTOT` (kg m-2 s-1), `PRECTOTCORR` (kg m-2 s-1).
  - `data/forcing/MERRA2/MERRA2_400/Yyyyy/Mmm/` contient des liens symboliques vers M2T1NXFLX (et RAD, SLV) ; `MERRA2_100/200/300` sont des liens vers `MERRA2_400`.

- Recherche complémentaire (`find -H … -maxdepth 7`, noms contenant `3B-DAY`, `imerg` ou `merra`, hors sous-dossiers déjà décrits et hors `src/`, sur les deux espaces lustre) : code retour 1 ; 18 résultats ; fichiers `3B-DAY*` : 0.

  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2` (dossier)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/MERRA-2_AOD.nc` (fichier, 2370736434 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/MERRA-2_AOD_avg.nc` (fichier, 296899327 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/MERRA2.README.pdf.1` (fichier, 1064850 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/MERRA_Tmax_Tmin.nc` (fichier, 26736528937 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/MERRA_Tmax_Tmin_NA.nc` (fichier, 2413707195 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/MERRA_Tmax_Tmin_NA_1980_2023.nc` (fichier, 2413707195 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/tasmax_MERRA-2.nc` (fichier, 1206897506 octets)
  - `~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/MERRA-2/tasmin_MERRA-2.nc` (fichier, 1206897506 octets)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/IMERG` (dossier)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2` (dossier)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2/MERRA2_100` (dossier)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2/MERRA2_200` (dossier)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2/MERRA2_300` (dossier)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2/MERRA2_400` (dossier)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/reports/inventory_imerg.csv` (fichier, 171378 octets)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/docs/reports/inventory_imerg.csv` (fichier, 247531 octets)
  - `~/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/To_rm/data/synthetic/imerg_precip.nc` (fichier, 31600 octets)

## Fichiers produits

- `paper1/tables/stations_inventory.csv` (227 lignes) : id, nom, source, lat, lon, debut, fin, n_jours_valides_2001_2014, pct_valide_2001_2014, bassin (plusieurs bassins séparés par `;`, vide si aucun), foldes_IsSpecial (colonne `IsSpecial` de `station_folds3.csv`).
- `id` = `nom` = valeur de la colonne `Station` (pas d'identifiant distinct dans le fichier) ; `debut`/`fin` = première/dernière date présente pour la station.


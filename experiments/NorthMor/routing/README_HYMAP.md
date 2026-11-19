# Documentation de référence du routage HyMAP2 (Nord Maroc 2016–2020)

> [!NOTE]
> **Manuel Technique et Guide de Référence Complet :**  
> Pour reproduire l'ensemble de la chaîne depuis zéro sur une nouvelle simulation Noah-MP, ou pour consulter l'analyse approfondie des hypothèses scientifiques et les questions techniques pour Augusto Getirana, référez-vous au guide complet :
> - **Document Markdown (source canonique) :** [HYMAP2_ROUTING_GUIDE.md](docs/HYMAP2_ROUTING_GUIDE.md)
> - **Document PDF (mise en page A4 complète, 43 pages) :** [HYMAP2_ROUTING_GUIDE.pdf](docs/HYMAP2_ROUTING_GUIDE.pdf)

## 1. Objectif scientifique et couplage Noah-MP → HyMAP2

### 1.1 Raison d'être scientifique du routage HyMAP2
Le modèle de surface continentale **Noah-MP 4.0.1** calcule les bilans d'eau et d'énergie dans la colonne de sol 1D pour chaque maille du domaine Nord Maroc (`NorthMor`). Il produit au pas journalier les flux de ruissellement superficiel rapide (`Qs_tavg`) et de drainage sous-racinaire profond (`Qsb_tavg`). Cependant, Noah-MP ne résout pas la propagation hydrodynamique de l'eau à travers les versants, les biefs fluviaux et les plaines d'inondation.

Le modèle hydrodynamique distribué **HyMAP2** (*Hydrological Modeling and Analysis Platform, version 2*) assure ce transfert spatial :
1. **Agrégation des flux :** Il convertit les flux surfaciques ($kg \cdot m^{-2} \cdot s^{-1}$) en volumes d'eau entrants sur un réseau de drainage distribué issu de MERIT-Hydro à $0.05^\circ$.
2. **Dynamique fluviale :** Il résout la propagation de l'onde cinématique en lit mineur, le stockage temporaire en nappe alluviale (vidange linéaire), et l'expansion sub-maille dans les plaines inondables.
3. **Validation terrain :** Il produit le débit fluvial routé (`Streamflow_tavg` en $m^3/s$) au droit des stations de jaugeage, rendant possible la confrontation directe et objective des simulations aux observations hydrométriques des Agences de Bassin Hydraulique (ABH).

### 1.2 Description des trois expériences de référence (2016–2020)
L'analyse porte sur la période quinquennale **2016–2020** à travers trois simulations continues initialisées par deux cycles de spin-up :
1. **Open-Loop (OPL corrigée) :** Simulation en boucle ouverte forcée par la météorologie sans assimilation de données d'humidité du sol (`OPL_2016_2020_corrigee`). Elle constitue la référence hydro-météorologique de base.
2. **Assimilation SMAP NoCDF (DA_nocdf) :** Assimilation par filtre de Kalman d'ensemble (EnKF) des observations satellitaires SMAP L3 d'humidité du sol, injectées directement sans correction préalable de biais (`DA_nocdf_2016_2020`).
3. **Assimilation SMAP DA-CDF (DA_cdf corrigée) :** Assimilation SMAP EnKF avec mise à l'échelle préalable par **CDF matching** sur l'ensemble du domaine (`DA_cdf_2016_2020`).

> [!IMPORTANT]
> **Distinction fondamentale entre les deux correctifs appliqués :**
> - **Le correctif HyMAP de nappe (`tbasflw / 86400`) :** C'est un correctif physico-numérique appliqué à la grille de paramètres HyMAP (`ldt_hymap/lis_input_corrigee.d01.nc`). La constante de temps de vidange de nappe fournie en secondes a été convertie en jours pour respecter l'équation Fortran de LISF. Ce correctif est **strictement identique pour les trois expériences** et résout le puits artificiel d'accumulation continue de nappe.
> - **Le correctif CDF matching Noah-MP :** C'est un prétraitement statistique appliqué en amont aux observations satellitaires SMAP L3 avant leur ingestion par le filtre EnKF dans Noah-MP. Il adapte la distribution d'humidité satellitaire à la climatologie du modèle, supprimant la surinjection massive et irréaliste de ruissellement constatée dans le Bouregreg sous DA-NoCDF.

### 1.3 Rôle du spin-up en deux cycles (C1 & C2)
Pour affranchir la simulation quinquennale du biais des conditions initiales nulles (*coldstart*), chaque expérience suit un protocole rigoureux de spin-up en deux cycles annuels sur l'année **2016** (366 jours) :
- **Cycle 1 (Coldstart) :** Démarrage avec stocks nuls au 01/01/2016, produisant un premier état d'équilibre au 01/01/2017.
- **Cycle 2 (Stabilisation) :** Ré-exécution de l'année 2016 initialisée par le restart du Cycle 1.
- **Convergence :** La dérive relative du stock de nappe (`BSFSTO`) entre C1 et C2 est validée sous le seuil strict de $1.0\%$ (OPL: $0.132\%$, DA-NoCDF: $0.065\%$, DA-CDF: $0.076\%$). Le restart final de C2 daté `201701010000` initialise la production continue 2016–2020.

---

## 2. Structure des répertoires

L'arborescence opérationnelle et historique du répertoire `experiments/NorthMor/routing/` est organisée de manière modulaire :

```text
experiments/NorthMor/routing/
├── README_HYMAP.md                 # Document de référence principal
├── docs/                           # Documentation opérationnelle
│   └── POSTPROCESSING.md                          # Guide de reproduction complet du post-traitement
├── stations/                       # Référentiel hydrométrique unique
│   ├── hymap_stations_pairing.csv                 # Table de référence unique des 12 stations appariées
│   └── README.md                                  # Documentation des coordonnées et conventions
├── configs/                        # Configurations LIS pour HyMAP2 (3 expériences + spin-ups)
│   ├── lis_hymap2_opl_spinup_c1_corrigee.config   # Spin-up C1 OPL corrigé (2016)
│   ├── lis_hymap2_opl_spinup_c2_corrigee.config   # Spin-up C2 OPL corrigé (2016)
│   ├── lis_hymap2_opl_2016_2020_corrigee.config   # Production 5 ans OPL corrigé
│   ├── lis_hymap2_da_nocdf_spinup_c1.config       # Spin-up C1 DA-NoCDF (2016)
│   ├── lis_hymap2_da_nocdf_spinup_c2.config       # Spin-up C2 DA-NoCDF (2016)
│   ├── lis_hymap2_da_nocdf_2016_2020.config       # Production 5 ans DA-NoCDF
│   ├── lis_hymap2_da_cdf_spinup_c1.config         # Spin-up C1 DA-CDF (2016)
│   ├── lis_hymap2_da_cdf_spinup_c2.config         # Spin-up C2 DA-CDF (2016)
│   ├── lis_hymap2_da_cdf_2016_2020.config         # Production 5 ans DA-CDF
│   └── lis_test_offline.config                    # Test unitaire hors-ligne
├── jobs/                           # Scripts SLURM d'exécution
│   ├── build_lis_hymap2.sh                        # Script de compilation de LIS HyMAP2
│   ├── run_hymap2_opl_spinup_c1_corrigee.sh       # Job SLURM Spin-up C1 OPL
│   ├── run_hymap2_opl_spinup_c2_corrigee.sh       # Job SLURM Spin-up C2 OPL
│   ├── run_hymap2_opl_2016_2020_corrigee.sh       # Job SLURM 5 ans OPL
│   ├── run_hymap2_da_nocdf_spinup_c1.sh           # Job SLURM Spin-up C1 DA-NoCDF
│   ├── run_hymap2_da_nocdf_spinup_c2.sh           # Job SLURM Spin-up C2 DA-NoCDF
│   ├── run_hymap2_da_nocdf_2016_2020.sh           # Job SLURM 5 ans DA-NoCDF
│   ├── run_hymap2_da_cdf_spinup_c1.sh             # Job SLURM Spin-up C1 DA-CDF
│   ├── run_hymap2_da_cdf_spinup_c2.sh             # Job SLURM Spin-up C2 DA-CDF
│   └── run_hymap2_da_cdf_2016_2020.sh             # Job SLURM 5 ans DA-CDF
├── scripts/                        # Scripts opérationnels maintenus
│   ├── remap_runoff_opl.py                        # Remapping conservatif Qs/Qsb OPL (181x121 -> 180x120)
│   ├── remap_runoff_da_nocdf.py                   # Remapping conservatif Qs/Qsb DA-NoCDF
│   ├── remap_runoff_da_cdf.py                     # Remapping conservatif Qs/Qsb DA-CDF
│   ├── check_remap_conservation_2018.py           # Diagnostic de conservation du remapping (S1 à S4)
│   ├── check_spinup_criterion_corrigee.py         # Contrôle de convergence du spin-up OPL (< 1.0 %)
│   ├── check_spinup_criterion_da_nocdf.py         # Contrôle de convergence du spin-up DA-NoCDF
│   ├── extract_streamflow.py                      # Extracteur unifié de débits journaliers aux stations
│   ├── evaluate_sebou_bouregreg.py                # Diagnostic hydrologique, bilans amont et figures 3exp
│   └── plot_streamflow_coverage.py                # Graphique de couverture temporelle des stations
├── ldt_hymap/                      # Génération des paramètres sous LDT
│   ├── ldt.config                                 # Configuration LDT
│   ├── lis_input.d01.nc                           # Paramètres LDT bruts (tbasflw non corrigé)
│   └── lis_input_corrigee.d01.nc                  # Paramètres opérationnels (tbasflw corrigé)
├── checks/                         # Dossiers d'audits et fiches techniques détaillées (00 à 06)
├── runoff_remap_180x120/           # Entrées routage : ruissellements reprojetés
│   ├── OPL_noirr_2016_2020/SURFACEMODEL/          # 1 828 fichiers journaliers NetCDF
│   ├── DA_nocdf_noirr_2016_2020/SURFACEMODEL/     # 1 828 fichiers journaliers NetCDF
│   └── DA_cdf_noirr_2016_2020/SURFACEMODEL/       # 1 828 fichiers journaliers NetCDF
├── output/                         # Sorties de simulation et fichiers de restart
│   ├── OPL_spinup_c1_corrigee/ROUTING/            # Sorties et restart C1 OPL
│   ├── OPL_spinup_c2_corrigee/ROUTING/            # Sorties et restart C2 OPL
│   ├── OPL_2016_2020_corrigee/ROUTING/            # 1 827 fichiers journaliers NetCDF OPL
│   ├── DA_nocdf_spinup_c1/ROUTING/                # Sorties et restart C1 DA-NoCDF
│   ├── DA_nocdf_spinup_c2/ROUTING/                # Sorties et restart C2 DA-NoCDF
│   ├── DA_nocdf_2016_2020/ROUTING/                # 1 827 fichiers journaliers NetCDF DA-NoCDF
│   ├── DA_cdf_spinup_c1/ROUTING/                  # Sorties et restart C1 DA-CDF
│   ├── DA_cdf_spinup_c2/ROUTING/                  # Sorties et restart C2 DA-CDF
│   ├── DA_cdf_2016_2020/ROUTING/                  # 1 827 fichiers journaliers NetCDF DA-CDF
│   └── [Runs obsolètes en attente de validation] :# OPL_2016_2020, OPL_201801, OPL_spinup_cycle1/2 (1.7 Go)
└── plots/                          # Figures et tables scientifiques maintenues
    ├── sebou_bouregreg/                           # Résultats scientifiques canoniques (3 figures, 3 tables)
    │   ├── figures/streamflow/                    # 3 figures scientifiques actuelles
    │   ├── tables/                                # 3 tables CSV de synthèse (11 stations, diagnostic, apports)
    │   └── README.md                              # Guide d'interprétation des résultats
    └── technical/                                 # Contrôles techniques maintenus
        ├── parameters/                            # streamflow_coverage_timeline.png
        └── spinup/                                # README.md (synthèse de convergence spin-up)
```

---

## 3. Préparation des paramètres LDT et provenance des données Augusto

Les paramètres physiographiques hydrographiques ont été élaborés et fournis par **Augusto Getirana** (NASA GSFC, Hydrological Sciences Laboratory) sous la forme d'une archive compressée `lis_param.tar.gz`.

### 3.1 Provenance, intégrité et format des grilles
- **Source d'origine :** Dérivés de MERIT-Hydro (résolution native de 3 secondes d'arc $\approx 90\text{ m}$) agrégés sur la grille régulière $0.05^\circ$ ($180 \times 120$ mailles). Le fichier `header` présent dans l'archive (`merit  1   10800    7199  0.000833  -10.000000000   -1.000000000   30.000000000   36.000000000`) atteste de cette source, sans documenter la méthode exacte d'agrégation (*upscaling*).
- **Contrôle d'intégrité SHA-256 :** L'archive source (`data/Hymap_params_from_Augusto/lis_param.tar.gz`) et les 24 fichiers binaires extraits dans `data/Hymap_params_from_Augusto/extracted/lis_param/` ont été vérifiés cryptographiquement (consulter [`checks/00_checksums_augusto.txt`](checks/00_checksums_augusto.txt)).
- **Format binaire :** Fichiers sans en-tête Fortran (*direct access*, encodage *big-endian*, 4 octets par valeur) comprenant :
  - **20 fichiers réels `float32` (IEEE 754) :** 19 grilles 2D ($180 \times 120 \times 4 = 86\,400$ octets) et 1 profil d'inondation 3D à 10 strates verticales (`lis_fldhgt_merged_005.bin`, $10 \times 180 \times 120 \times 4 = 864\,000$ octets).
  - **4 fichiers entiers signés `int32` :** 4 grilles 2D (86 400 octets) pour les directions de drainage aval (`lis_nextx_005.bin`, `lis_nexty_005.bin`), l'identifiant de bassin (`lis_basin_005.bin`) et le masque de domaine (`lis_mask_005.bin`).

### 3.2 Les cinq familles de paramètres
1. **Topologie et réseau hydrographique :** Directions de drainage vers l'aval (`lis_nextx_005.bin`, `lis_nexty_005.bin`, `int32`), coordonnées des nœuds fluviaux (`lis_nodelon_005.bin`, `lis_nodelat_005.bin`, `float32`), distance hydraulique entre mailles (`lis_nxtdst_005.bin`, `float32`), superficies drainées amont cumulées (`lis_uparea_005.bin`, `float32`) et identifiants de bassins (`lis_basin_005.bin`, `int32`).
2. **Géométrie du lit mineur :** Largeur de chenal avec estuaires fusionnés (`lis_rivwth_merged_005.bin`, `float32`, champ distribué comportant 4 080 valeurs uniques), hauteur de berge à pleins bords (`lis_rivhgt_005.bin`, `float32`), longueur réelle méandrée du bief (`lis_rivlen_005.bin`, `float32`), et coefficient de rugosité de Manning du chenal (`lis_rivman_005.bin`, `float32`). La carte de pente (`lis_slope_005.bin`) n'est pas ingérée par LDT.
3. **Dynamique des plaines d'inondation :** Profil altimétrique d'inondation sub-maille discrétisé en 10 strates de hauteur (`lis_fldhgt_merged_005.bin`, `float32` 3D) et coefficient de frottement de Manning en plaine majeure (`lis_fldman_005.bin`, `float32`).
4. **Hydrodynamique et temps de transfert :** Temps de concentration du ruissellement superficiel rapide (`lis_getirana_paiva_005.bin`, `float32`), multiplicateur de ruissellement (`lis_trunoff_005.bin`, `float32`), constante de temps de vidange du réservoir souterrain de nappe (`lis_tbasflw_005.bin`, `float32`), et débit interannuel de référence hydraulique (`lis_qrefer_005.bin`, `float32`). Le fichier `lis_maxlen_005.bin` n'est pas utilisé par LDT.
5. **Masques, maillage et orographie :** Altitude moyenne du relief (`lis_elevtn_005.bin`, `float32`), superficie réelle des cellules (`lis_grarea_005.bin`, `float32`), et masques d'activité continentale (`lis_mask_005.bin` en `int32`, `lis_real_mask_005.bin` en `float32`, ce dernier servant de substitut technique).

### 3.3 Exécution de LDT sous environnement Toubkal
L'ingestion de ces grilles binaires *big-endian* par GCC/GFortran nécessite de forcer l'environnement d'exécution :
```bash
cd experiments/NorthMor/routing/ldt_hymap
source ../../../../arch/arch_toubkal.env
export GFORTRAN_CONVERT_UNIT='big_endian'
../../../../src/lisf/ldt/LDT ldt.config
```
LDT assemble 45 variables dans `lis_input.d01.nc` (23 variables HyMAP et 22 variables de géométrie LIS).

### 3.4 Anomalies physiques signalées à discuter avec Augusto Getirana
Plusieurs cartes de paramètres présentent des propriétés spatiales atypiques qui appellent une confirmation :
- **Superficies de cellules `grarea` :** Certaines mailles côtières ou frontières atteignent jusqu'à $178.9\text{ km}^2$, s'écartant sensiblement de la superficie sphérique théorique d'une maille $0.05^\circ \times 0.05^\circ$ ($pprox 25\text{--}27\text{ km}^2$).
- **Hauteurs de berges `rivhgt` :** Distribution quasi-uniforme de $\approx 0.50\text{ m}$ sur l'ensemble du réseau, sans différenciation amont-aval marquée.
- **Largeurs de chenal `rivwth_merged` :** Atteignent localement jusqu'à $14.3\text{ km}$ au voisinage immédiat des estuaires atlantiques.
- **Rugosités de Manning `rivman` :** Valeurs quasi-uniformes proches de $0.10\text{ s}\cdot\text{m}^{-1/3}$, relativement élevées pour des lits mineurs naturels.

*Pour l'inventaire détaillé cellule par cellule et l'audit de LDT, consulter :*
👉 [`checks/01_parametres_augusto.md`](checks/01_parametres_augusto.md) et [`checks/02_preparation_ldt.md`](checks/02_preparation_ldt.md).

---

## 4. Paramètres corrigés : cas critique de `tbasflw` et rôle du plancher numérique

### 4.1 Unité attendue par le code LISF vs unité native supposée des données
Dans le code source de LISF (`HYMAP2_modelMod.F90`, l. 111), la vidange du réservoir souterrain est formulée par :
$$q_{bas} = \frac{S_{bas}}{tbsflw \times 86400}$$
Le code attend impérativement `tbsflw` en **jours** pour que la multiplication par 86 400 convertisse le temps de vidange en secondes.

Dans le fichier binaire brut `lis_tbasflw_005.bin` fourni par Augusto Getirana, la valeur moyenne sur le domaine est de $\approx 61\,703$ (attribut `units = 'none'`). Bien que cette valeur numérique suggère une grandeur nativement exprimée en secondes ($pprox 17.1\text{ h}$), **cette unité d'origine n'a pas été confirmée de façon indépendante**. Ingérées directement sans division dans `lis_input.d01.nc`, ces valeurs étaient interprétées par LISF comme $61\,703\text{ jours}$ ($pprox 169\text{ ans}$), piégeant $97.5\%$ du drainage souterrain et créant un puits d'accumulation artificiel de $+16\,525.8\text{ hm}^3$ en 5 ans dans `BSFSTO`.

### 4.2 Portée de la correction par 86 400
- **Correction opérationnelle :** Dans `ldt_hymap/lis_input_corrigee.d01.nc`, la variable `HYMAP_baseflow_time_delay` a été divisée numériquement par 86 400 (attribut `units = 'days'`).
- **Nature de la décision :** Cette division a résolu un problème numérique majeur de fermeture du bilan de masse dans notre configuration. Toutefois, son interprétation physique exacte (s'agit-il réellement de secondes converties en jours, ou d'une calibration empirique ?) demeure à confirmer auprès d'Augusto Getirana.

### 4.3 Plancher numérique LIS et dynamique d'étiage
- **Comportement du plancher numérique :** LIS applique un plancher de stabilité numérique lors de la lecture du paramètre (`HYMAP2_routingMod.F90`, l. 1265–1267) :
  $$\text{where}(tbsflw < cntime / 86400.)$$
  Ce plancher s'active dans **99.90 % des mailles actives** (15 921 / 15 937 mailles).
- **Conséquence sur la distribution de vidange :** Alors que le `tbsflw` divisé brut présente une médiane de 0.0774 jour ($\approx 1.86\text{ h}$), le plancher numérique relève le temps de séjour médian effectif à **2.4465 jours**.
- **Nuance hydrologique essentielle sur les étiages et assecs :** Cette vidange rapide accélère la restitution des flux souterrains aux cours d'eau. Néanmoins, la surestimation des débits d'étiage et l'absence totale d'assecs estivaux simulés sur les oueds temporaires (notamment à Sidi Jabeur sur l'oued Grou) **ne doivent pas être présentées comme causées exclusivement par ce plancher**. En effet :
  1. L'absence d'assecs était déjà observée dans la simulation brute non corrigée (0 jour à débit nul modélisé).
  2. Elle résulte d'une conjonction de facteurs physiques et conceptuels : le drainage souterrain continu $Q_{sb}$ généré par Noah-MP tout au long de l'année, et l'absence dans HyMAP2 de toute composante d'infiltration en lit mineur (*transmission losses*) vers les aquifères alluviaux profonds (`HYMAP2 routing model evaporation option: none`).

*Pour l'audit détaillé du code Fortran et le recalcul des distributions, consulter :*
👉 [`checks/01_parametres_augusto.md`](checks/01_parametres_augusto.md) et [`checks/06_audit_coherence.md`](checks/06_audit_coherence.md).

---

## 5. Préparation et remapping de Qs/Qsb

Les flux `Qs_tavg` et `Qsb_tavg` issus de Noah-MP (grille nodale $181 \times 121$) sont reprojetés vers la grille centrée HyMAP ($180 \times 120$) au pas journalier.

### 5.1 Formulation du stencil et scripts opérationnels
Le rééchantillonnage applique une moyenne arithmétique aux 4 sommets entourant le centre de chaque maille cible :
$$\bar{q}[j, i] = \frac{1}{4} \Big( q[j, i] + q[j, i+1] + q[j+1, i] + q[j+1, i+1] \Big)$$
Les valeurs maritimes (`-9999.0`) sont neutralisées inconditionnellement à `0.0`.

```bash
# Pour Open-Loop (OPL) :
python3 experiments/NorthMor/routing/scripts/remap_runoff_opl.py

# Pour DA NoCDF :
python3 experiments/NorthMor/routing/scripts/remap_runoff_da_nocdf.py

# Pour DA CDF :
python3 experiments/NorthMor/routing/scripts/remap_runoff_da_cdf.py
```

### 5.2 Portée réelle du contrôle de conservation
- **Quasi-conservation globale à l'échelle du domaine :** Sur l'emprise géographique commune $[30.0^\circ, 36.0^\circ]\text{N} \times [-10.0^\circ, -1.0^\circ]\text{E}$, le diagnostic annuel 2018 atteste d'une quasi-conservation du volume intégré sur le domaine ($S_2/S_1 = 100.0002\%$) sous des hypothèses géométriques centrées sur la maille.
- **Absence de préservation locale exacte :** Cette quasi-équivalence globale à l'échelle macro-régionale n'implique aucune préservation exacte des flux à l'échelle des sous-bassins individuels. En particulier, aux frontières côtières et sur les mailles littorales, l'interpolation lisse les contrastes terre-mer.
- **Filtrage par le masque de bassin :** Les 15 937 mailles actives de `HYMAP_basin_mask` excluent les flux tombant hors du réseau hydrographique actif ($184.03\text{ hm}^3$ en 2018 pour OPL ; $\approx 242.7\text{ hm}^3$ pour DA-NoCDF).

*Pour l'audit des 4 stades de volume (S1 à S4), consulter :*
👉 [`checks/03_remapping_ruissellement.md`](checks/03_remapping_ruissellement.md).

---

## 6. Spin-up HyMAP, chronologie des restarts et convergence

Pour équilibrer les réservoirs internes sans subir le biais des conditions initiales nulles (*coldstart*), un spin-up en deux cycles annuels consécutifs est exécuté sur l'année **2016** (366 jours).

### 6.1 Les quatre réservoirs d'état
HyMAP2 gère 4 réservoirs de stockage d'eau :
1. `BSFSTO` : Stock en nappe souterraine (*baseflow storage*, réservoir lent).
2. `RNFSTO` : Stock d'écoulement superficiel sur les versants (*surface runoff storage*, réservoir rapide).
3. `RIVSTO` : Stock en rivière dans le lit mineur (*river channel storage*, réservoir rapide).
4. `FLDSTO` : Stock dans les plaines d'inondation (*floodplain storage*, réservoir rapide).

### 6.2 Procédure de mise en régime (spin-up recycling) et restart `201701010000`
1. **Cycle 1 (Coldstart) :** Démarre le `2016-01-01 00:00` avec stocks nuls (`coldstart`). À la date finale `2017-01-01 00:00`, LIS écrit le fichier restart :
   `output/<EXP>_spinup_c1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`.
2. **Cycle 2 (Stabilisation) :** Démarre le `2016-01-01 00:00` en lisant le restart du Cycle 1 (`restart`). À la fin de l'année le `2017-01-01 00:00`, LIS écrit le restart stabilisé :
   `output/<EXP>_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`.
3. **Réutilisation pour initialiser la production quinquennale (2016–2020) :**
   La simulation quinquennale démarre au `2016-01-01 00:00` en pointant vers le restart du Cycle 2 daté `201701010000`.
   *Vérification du code Fortran (`HYMAP2_routing_readrst.F90`, l. 88–103) :* LIS ouvre le fichier spécifié dans la configuration, extrait les tableaux d'état (`BSFSTO`, `RNFSTO`, `RIVSTO`, `FLDSTO`) et initialise directement la mémoire du modèle sans contrôle bloquant sur la date du fichier. Il s'agit d'une **procédure standard de mise en régime (spin-up recycling)**, exploitant l'état d'équilibre atteint au 1er janvier (00h) après un cycle météorologique annuel complet, et non d'une continuité chronologique classique.

### 6.3 Critères de convergence et distinction globale vs locale
Le critère d'arrêt du spin-up est vérifié au terme du Cycle 2 :
$$\Delta_{rel}(BSFSTO) = \frac{|S_{BSF}^{(2)} - S_{BSF}^{(1)}|}{S_{BSF}^{(1)}} < 1.0\%$$

```bash
# Vérification pour OPL corrigé :
python3 experiments/NorthMor/routing/scripts/check_spinup_criterion_corrigee.py

# Vérification pour DA-NoCDF :
python3 experiments/NorthMor/routing/scripts/check_spinup_criterion_da_nocdf.py
```

#### Synthèse des stocks stabilisés au 1er janvier (Fin Cycle 2 vs Fin Cycle 1)
| Expérience | Réservoir | Cycle 1 (hm³) | Cycle 2 (hm³) | Écart absolu (hm³) | Dérive relative (%) | Statut |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **OPL Corrigé** | `BSFSTO` (nappe) | 46.504 | 46.565 | +0.061 | **0.1316 %** | Validé (< 1.0 %) |
| | `RNFSTO` (surface) | 66.908 | 67.228 | +0.320 | 0.478 % | Stabilisé |
| | `RIVSTO` (chenal) | 265.366 | 265.374 | +0.008 | 0.003 % | Stabilisé |
| | `FLDSTO` (plaine) | 195.636 | 195.640 | +0.004 | 0.002 % | Stabilisé |
| | **Stock Total** | **574.414** | **574.807** | **+0.393** | **0.0684 %** | Validé (< 1.0 %) |
| **DA-NoCDF** | `BSFSTO` (nappe) | 146.113 | 146.207 | +0.094 | **0.0645 %** | Validé (< 1.0 %) |
| | `RNFSTO` (surface) | 68.216 | 68.539 | +0.323 | 0.473 % | Stabilisé |
| | `RIVSTO` (chenal) | 443.928 | 443.935 | +0.007 | 0.0016 % | Stabilisé |
| | `FLDSTO` (plaine) | 452.853 | 452.858 | +0.005 | 0.0011 % | Stabilisé |
| | **Stock Total** | **1 111.110** | **1 111.539** | **+0.429** | **0.0386 %** | Validé (< 1.0 %) |

> [!WARNING]
> **Diagnostics indisponibles et portée de la convergence :**
> - **Convergence cellule par cellule indisponible :** Le critère $< 1.0\%$ est évalué sur la somme scalaire globale intégrée au domaine. Il ne garantit pas la convergence asymptotique locale dans chaque sous-bassin individuel.
> - **Absence de suivi temporel continu $dS/dt$ :** Les scripts ne tracent pas la dérivée temporelle continue pour vérifier l'atteinte d'un plateau asymptotique stable au cours du cycle.
> - **Réservoirs rapides :** `RNFSTO`, `RIVSTO` et `FLDSTO` ont des temps de vidange de quelques heures à quelques jours. Leur quasi-identité entre cycles reflète la répétition exacte des forçages météo du 31 décembre plutôt qu'un équilibre hydrogéologique profond.

*Pour l'audit complet du spin-up, consulter :*
👉 [`checks/04_audit_routing_historique.md`](checks/04_audit_routing_historique.md) et [`checks/06_audit_coherence.md`](checks/06_audit_coherence.md).

---

## 7. Configurations et commandes exactes des runs OL et DA-NoCDF

### 7.1 Compilation de LIS HyMAP2
```bash
bash experiments/NorthMor/routing/jobs/build_lis_hymap2.sh
```

### 7.2 Soumission SLURM (Mode recommandé sur Toubkal)
Les scripts SLURM allouent 1 nœud et 16 cœurs CPU (temps moyen d'exécution ~12 min pour 1 an de spin-up, ~45 min pour 5 ans de production) :

```bash
# Chaîne Open-Loop corrigée :
sbatch experiments/NorthMor/routing/jobs/run_hymap2_opl_spinup_c1_corrigee.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_opl_spinup_c2_corrigee.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_opl_2016_2020_corrigee.sh

# Chaîne Assimilation DA-NoCDF :
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_nocdf_spinup_c1.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_nocdf_spinup_c2.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_nocdf_2016_2020.sh

# Chaîne Assimilation DA-CDF :
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_spinup_c1.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_spinup_c2.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_2016_2020.sh

# Chaîne Assimilation DA-CDF :
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_spinup_c1.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_spinup_c2.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_2016_2020.sh

# Chaîne Assimilation DA-CDF :
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_spinup_c1.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_spinup_c2.sh
sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_cdf_2016_2020.sh
```

### 7.3 Exécution interactive / directe
```bash
source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

# Exemple pour OPL corrigé 5 ans :
mpirun -np 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_corrigee.config

# Exemple pour DA-NoCDF 5 ans :
mpirun -np 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_da_nocdf_2016_2020.config
```

---

## 8. Sorties disponibles et procédure d'extraction des débits

### 8.1 Fichiers NetCDF disponibles
Chaque simulation de 5 ans produit **1 827 fichiers journaliers NetCDF** (du `2016-01-02` au `2021-01-01`), archivés par mois dans :
`experiments/NorthMor/routing/output/<EXP>/ROUTING/YYYYMM/LIS_HIST_YYYYMMDD0000.d01.nc`

Chaque fichier journalier contient les moyennes des 24 heures précédentes :
- **`Streamflow_tavg`** : Débit fluvial moyen en rivière ($m^3/s$) — **nom exact de la variable extraite pour l'évaluation aux stations**.
- `RiverStor_tavg`, `RiverDepth_tavg`, `RiverFlowVelocity_tavg` : Stock ($m^3$), hauteur ($m$) et vitesse ($m/s$) en lit mineur.
- `FloodQ_tavg`, `FloodStor_tavg`, `FloodDepth_tavg` : Débit, stock et hauteur en plaine inondable.
- `FloodedFrac_tavg`, `FloodedArea_tavg` : Fraction et surface inondée ($m^2$).
- `BaseflowStor_tavg`, `RunoffStor_tavg` : Niveaux de stockage dans les réservoirs souterrain et superficiel ($mm$).

### 8.2 Protocole de reproduction rapide (Quick Start)

L'intégralité du post-traitement et de l'évaluation scientifique repose sur deux scripts autonomes (détaillés dans [`docs/POSTPROCESSING.md`](docs/POSTPROCESSING.md)) :

#### A. Évaluation scientifique instantanée (Recommandé, ~15 secondes)
Les débits journaliers des trois expériences étant déjà extraits et validés dans les caches de référence, l'évaluation complète se relance directement sans relire les 5 481 fichiers NetCDF :
```bash
python3 experiments/NorthMor/routing/scripts/evaluate_sebou_bouregreg.py
```
- **Livrables produits dans `plots/sebou_bouregreg/tables/` :**
  - `tableau_synthese_11stations_sebou_bouregreg.csv` (métriques complètes KGE, NSE, r, PBIAS).
  - `tableau_diagnostic_5stations.csv` (statistiques fines sur les 5 stations prioritaires).
  - `tableau_apports_noahmp_2018.csv` (bilan amont délimité $Q_s$ et $Q_{sb}$ en $\text{hm}^3$ pour 2018).
- **Figures régénérées dans `plots/sebou_bouregreg/figures/streamflow/` :**
  - `fig_detaillee_2018_b_s_jabeur.png` (zoom journalier 2018 à Sidi Jabeur, oued Grou).
  - `fig_detaillee_2018_b_l_chafia.png` (zoom journalier 2018 à Lalla Chafia, oued Bouregreg).
  - `fig_comparative_mensuelle_sebou.png` (séries mensuelles multi-stations 2016–2020 sur le Haut Sebou).

#### B. Contrôle ou ré-extraction des débits aux 12 stations
```bash
# Vérifier l'intégrité des 3 caches journaliers sans ré-extraction :
python3 experiments/NorthMor/routing/scripts/extract_streamflow.py --experiment all

# Forcer la ré-extraction complète d'une expérience depuis les NetCDF (ex: OPL) :
python3 experiments/NorthMor/routing/scripts/extract_streamflow.py --experiment opl --force
```
Les fichiers de cache journaliers générés et lus sont :
- OPL corrigée : `output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv`
- DA-NoCDF : `output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv`
- DA-CDF : `output/DA_cdf_2016_2020/t9_sim_daily_12stations_da_cdf.csv`

---

## 9. Stations ABH et périodes réellement observées

Le réseau hydrométrique de référence comprend 12 stations de jaugeage réparties sur trois bassins versants.

### 9.1 Résolution temporelle des observations par bassin
- **Bassin du Bouregreg (4 stations) :** Fournies nativement par l'ABH Bouregreg-Chaouia au pas de temps **journalier** (`obs_daily.csv`, 1 827 jours sur 2016–2020).
  *Note sur les rapports antérieurs :* Dans la Tâche 5bis préliminaire, ces débits journaliers avaient été agrégés en moyennes mensuelles pour une analyse homogène des 12 stations. Dans la synthèse finale de la Tâche 8, l'évaluation des stations du Bouregreg est effectuée à leur pas de temps natif **journalier**.
- **Bassin du Haut Sebou (7 stations) :** Fournies nativement par l'ABH Sebou exclusivement au pas de temps **mensuel** (`obs_monthly.csv`).
- **Bassin du Ksob (1 station) :** Fournie nativement au pas de temps **mensuel** (`obs_monthly.csv`).

### 9.2 Inventaire complet des 12 stations de jaugeage
| Identifiant | Nom station | Oued | Bassin | Pas de temps natif | Nbr Obs | Période observée (2016–2020) | Lacunes | Agence (ABH) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `b_a_loudah` | **Ain Loudah** | Korifla | Bouregreg | Journalier | 1 827 | 2016–2020 (100 %) | 0 | ABH Bouregreg-Chaouia |
| `b_l_chafia` | **Lalla Chafia** | Bouregreg | Bouregreg | Journalier | 1 826 | 2016–2020 (99.9 %) | 1 jour (2016-10-06) | ABH Bouregreg-Chaouia |
| `b_s_cherif` | **S.M. Cherif** | Mechraa | Bouregreg | Journalier | 1 827 | 2016–2020 (100 %) | 0 | ABH Bouregreg-Chaouia |
| `b_s_jabeur` | **Sidi Jabeur** | Grou | Bouregreg | Journalier | 1 827 | 2016–2020 (100 %) | 0 | ABH Bouregreg-Chaouia |
| `adamna` | **Adamna** | Ksob | Ksob | Mensuel | 20 | 2016/01 – 2017/08 | 40 mois | ABH Tensift |
| `ain_timedrine` | **Ain Timedrine** | Sebou | Sebou | Mensuel | 60 | 2016–2020 (100 %) | 0 | ABH Sebou |
| `ait_khabbach` | **Ait Khabbach** | Guigou | Sebou | Mensuel | 44 | 2016–2020 (73.3 %) | 16 mois | ABH Sebou |
| `azzaba` | **Azzaba** | Sebou | Sebou | Mensuel | 60 | 2016–2020 (100 %) | 0 | ABH Sebou |
| `dar_el_hamra` | **Dar El Hamra** | Zloul | Sebou | Mensuel | 60 | 2016–2020 (100 %) | 0 | ABH Sebou |
| `el_mers` | **El Mers** | Masser | Sebou | Mensuel | 20 | 2016/01 – 2017/08 | 40 mois | ABH Sebou |
| `pont_ait_aissa`| **Pont Ait Aissa**| Guigou | Sebou | Mensuel | 60 | 2016–2020 (100 %) | 0 | ABH Sebou |
| `pont_de_mdez` | **Pont de Mdez** | Sebou | Sebou | Mensuel | 44 | 2016–2020 (73.3 %) | 16 mois | ABH Sebou |

> [!IMPORTANT]
> **Vigilance critique sur les observations in-situ :**
> 1. **Duplication démontrée Ain Loudah / S.M. Cherif :** Les 1 827 valeurs journalières observées sont rigoureusement identiques entre ces deux stations situées sur deux oueds distincts (Korifla vs Mechraa). Cette anomalie provient des fichiers administratifs originaux de l'ABH et interdit de considérer ces stations comme deux validations indépendantes.
> 2. **Période restreinte d'El Mers et Adamna (20 mois) :** Ces stations ne disposent que de mesures sur la période humide 2016–2017. Tout calcul de bilan ou de métrique doit impérativement porter sur ces **stricts 20 mois identiques** (ce qui résout le prétendu dépassement volumique $V_{sim} > V_{in}$ d'El Mers dans la figure F5, attribuable à un pur artéfact d'échantillonnage interannuel).

*Pour l'inventaire des stations, les coordonnées et les fiches détaillées, consulter :*
👉 [`checks/05_evaluation_debits_historiques.md`](checks/05_evaluation_debits_historiques.md).

---

## 10. Métriques d'évaluation et principales limites hydrologiques

### 10.1 Métriques disponibles et formulations exactes
Le script d'évaluation (`evaluate_sebou_bouregreg.py`) calcule pour chaque station :
- **KGE (Kling-Gupta Efficiency, Gupta et al. 2009) :**
  $$KGE = 1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}$$
  avec $r$ le coefficient de corrélation linéaire de Pearson, $\alpha = \sigma_{sim}/\sigma_{obs}$ le ratio des écarts-types, et $\beta = \mu_{sim}/\mu_{obs}$ le ratio des moyennes.
  *Précision méthodologique :* Il s'agit bien de la formulation originale **KGE-2009** (fondée sur $\alpha$) et non de la version modifiée KGE-2012 (Kling et al., 2012) qui utilise le ratio des coefficients de variation $\gamma = \frac{\sigma_{sim}/\mu_{sim}}{\sigma_{obs}/\mu_{obs}}$.
- **NSE (Nash & Sutcliffe, 1970) :** Critère quadratique sensible aux pointes de crues.
- **PBIAS (Percent Bias, %) :** Biais volumique cumulé relatif : $PBIAS = \frac{\sum (Q_{sim} - Q_{obs})}{\sum Q_{obs}} \times 100\%$.
- **Indicateur VALUE (Amélioration par rapport à l'Open-Loop) :**
  Calculé ponctuellement par :
  $$\text{value}_t = |Q_{OPL,t} - Q_{obs,t}| - |Q_{DA,t} - Q_{obs,t}|$$
  La métrique de synthèse rapportée (`pos_val_tot` ou `VALUE > 0 Total`) mesure le **pourcentage de pas de temps où l'assimilation réduit l'erreur absolue par rapport à l'observation** :
  $$\text{pos\_val\_tot} = \frac{1}{N} \sum_{t=1}^N \mathbb{I}(\text{value}_t > 0) \times 100\%$$
  Il s'agit donc d'un indicateur de **fréquence temporelle d'amélioration**, et non d'un gain volumique global.

### 10.2 Synthèse des limites scientifiques et incertitudes démontrées
1. **Incertitudes d'appariement géomorphologique (Bouregreg) :** En l'absence de superficies officielles enregistrées dans l'archive ABH Bouregreg-Chaouia, les stations sont appariées sur le bief principal le plus proche (catégorisées Niveau B). Bien que morphologiquement cohérentes, l'incertitude sur la délimitation exacte du bassin versant amont persiste.
2. **Duplication démontrée des observations Ain Loudah / S.M. Cherif :** Les 1 827 valeurs journalières observées fournies par l'ABH sont rigoureusement identiques entre ces deux stations situées sur deux oueds distincts (Korifla vs Mechraa). Cette duplication administrative interdit de les traiter comme deux validations indépendantes.
3. **Surestimation d'étiage et absence d'assecs simulés :** À la station de Sidi Jabeur (oued Grou), 310 jours à débit strictement nul ($Q_{\text{obs}} = 0.00\text{ m}^3/\text{s}$) sont observés, alors que les trois simulations maintiennent un écoulement estival permanent ($Q_{\text{sim}} > 1.4\text{ m}^3/\text{s}$). Ce biais structurel s'explique conjointement par la recharge continue du réservoir de nappe par Noah-MP et par l'absence dans HyMAP2 de pertes par infiltration en lit mineur (*transmission losses*) vers les aquifères alluviaux profonds.
4. **Sous-estimation sur le Haut Sebou :** Les simulations OPL et assimilées sous-estiment les débits sur la majorité des stations du Haut Sebou (PBIAS de $-38\%$ à $-78\%$). Les causes physiques potentielles (sous-estimation des précipitations orographiques d'altitude, résurgences de sources karstiques non représentées, prélèvements agricoles non instrumentés) demeurent des **hypothèses explicatives ouvertes** et non des facteurs quantifiés ou isolés.
5. **Portée du remapping :** La conservation volumique est démontrée à l'échelle globale du domaine ($S_2/S_1 = 100.0002\%$), mais l'interpolation par stencil 4 points lisse localement les flux sans garantir une conservation stricte à l'échelle de chaque sous-bassin individuel.
6. **Désactivation des interactions nappe-rivière bidirectionnelles :** Option `dwi flag: 0` imposée dans toutes les configurations pour neutraliser les ratios DWI instables de l'archive brute Augusto.

---

## 11. Distinction entre les trois niveaux de validation

Pour garantir la rigueur scientifique des conclusions, la chaîne distingue formellement :

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. VALIDATION TECHNIQUE (Code, Exécution, Formats)                     │
│    - Compilation sans erreur du binaire LIS HyMAP2.                    │
│    - Lecture correcte du restart NetCDF 201701010000 sans crash.       │
│    - Production des 1 827 fichiers journaliers NetCDF non corrompus.   │
├────────────────────────────────────────────────────────────────────────┤
│ 2. COHÉRENCE DES BILANS (Physique Numérique & Conservation de Masse)  │
│    - Quasi-conservation du remapping Qs/Qsb (S2/S1 = 100.0002 %).      │
│    - Stabilisation du spin-up inter-cycles : dérive BSFSTO < 1.0 %.    │
│    - Conservation interne de masse sur 2018 : fermeture < 0.2 %.       │
│    - Ratio volumique annuel Vsim / Vin proche de 100 %.                │
├────────────────────────────────────────────────────────────────────────┤
│ 3. VALIDATION HYDROLOGIQUE (Réalisme Terrain vs Observations In-Situ)  │
│    - Confrontation des hydrogrammes aux débits observés aux 12 stations│
│    - Métriques de calage statistique (KGE-2009, NSE, r, PBIAS).        │
│    - Restitution des régimes de crue et des assecs d'étiage.           │
│    - Détection des limites du modèle (biais structurels, karst).       │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> Un modèle peut présenter une **parfaite validation technique** et une **excellente cohérence des bilans volumiques** tout en ayant une **piètre validation hydrologique** (par exemple en présence d'un biais structural ou de données in-situ lacunaires).

---

## 12. Simulation tripartite OPL / DA-NoCDF / DA-CDF (Validée)

### 12.1 Validation de l'hypothèse scientifique
Le routage de l'expérience **DA-CDF** a été complété sur les 5 années (2016–2020) après deux cycles de spin-up validés. L'hypothèse scientifique est confirmée :
- La mise à l'échelle préalable par **CDF matching** élimine la surinjection massive d'eau observée sous DA-NoCDF dans le Bouregreg (réduction de l'excès de ruissellement et rapprochement des volumes OPL).
- L'évaluation conjointe des 3 expériences montre que DA-CDF stabilise les hydrogrammes tout en améliorant ponctuellement la corrélation temporelle sur les épisodes de crue modérée.

### 12.2 Protocole d'exécution respecté
1. **Remapping conservatif Qs/Qsb :** Réalisé via `scripts/remap_runoff_da_cdf.py` vers `runoff_remap_180x120/DA_cdf_noirr_2016_2020/`.
2. **Spin-up en deux cycles :** Exécuté via `jobs/run_hymap2_da_cdf_spinup_c1.sh` et `_c2.sh` avec convergence $< 1.0\%$.
3. **Simulation quinquennale :** 1 827 fichiers journaliers produits dans `output/DA_cdf_2016_2020/ROUTING/`.
4. **Extraction et évaluation :** Intégrées dans la chaîne standard (`extract_streamflow.py` et `evaluate_sebou_bouregreg.py`).

---

## 13. Tableau récapitulatif des runs de routage

| Répertoire de sortie (`routing/output/`) | Fichier lis_input utilisé | Statut | Commentaire technique |
| :--- | :---: | :---: | :--- |
| `OPL_201801/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Test initial 1 mois, paramètre `tbasflw` brut non corrigé. |
| `OPL_spinup_cycle1/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Spin-up 2016 non corrigé, accumulation continue de nappe ($BSFSTO = 3\,553\text{ hm}^3$). |
| `OPL_spinup_cycle2/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Doublement inter-cycles ($BSFSTO = 6\,920\text{ hm}^3$, $+94.79\%$, non convergé). |
| `OPL_2016_2020/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Production 5 ans avec puits massif artificiel en nappe ($+16\,525.8\text{ hm}^3$ entre restarts). |
| `OPL_spinup_c1_corrigee/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Spin-up C1 corrigé sur 1 an (2016) ($BSFSTO = 46.504\text{ hm}^3$, total $574.414\text{ hm}^3$). |
| `OPL_spinup_c2_corrigee/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Spin-up C2 corrigé sur 1 an (2016) ($BSFSTO = 46.565\text{ hm}^3$, dérive $0.1316\% < 1.0\%$). |
| `OPL_2016_2020_corrigee/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Production 5 ans continue OPL corrigée (fermeture de masse sur 2018 à $99.965\%$, 1 827 fichiers). |
| `DA_nocdf_spinup_c1/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Spin-up C1 DA-NoCDF ($BSFSTO = 146.113\text{ hm}^3$). |
| `DA_nocdf_spinup_c2/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Spin-up C2 DA-NoCDF ($BSFSTO = 146.207\text{ hm}^3$, dérive $0.0645\% < 1.0\%$). |
| `DA_nocdf_2016_2020/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Production 5 ans continue DA-NoCDF (ratio entrée/sortie 2018 à $99.930\%$, 1 827 fichiers). |
| `DA_cdf_spinup_c1/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Spin-up C1 DA-CDF (coldstart, 2016). |
| `DA_cdf_spinup_c2/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Spin-up C2 DA-CDF (restart C1, 2016, convergence validée). |
| `DA_cdf_2016_2020/ROUTING/` | `lis_input_corrigee.d01.nc` | **RÉFÉRENCE COMPLÉTÉE** | Production 5 ans continue DA-CDF (1 827 fichiers journaliers NetCDF). |
| `OPL_test_jan2016_linres0/ROUTING/` | `lis_input_corrigee.d01.nc` | **TEST VALIDÉ** | Test 1 mois (janv. 2016) avec `linres=0` en coldstart (job 8272765, 39.4 s, 31 fichiers NetCDF, $BSFSTO=0$). |
| `OPL_linres0_2016_2020/ROUTING/` | `lis_input_corrigee.d01.nc` | **PRODUCTION VALIDÉE** | Production 5 ans OPL HyMAP-2 avec `linres=0` en coldstart (job 8272794, 28 min 43 s, 1 827 fichiers NetCDF, 61 restarts). |

---

## 14. Index des fiches techniques d'audit (`checks/`)

Pour approfondir les analyses sans alourdir ce document opérationnel, consulter les rapports spécialisés :
- [`checks/00_checksums_augusto.txt`](checks/00_checksums_augusto.txt) : Empreintes cryptographiques SHA-256 de l'archive et des fichiers binaires originaux.
- [`checks/01_parametres_augusto.md`](checks/01_parametres_augusto.md) : Audit physique des 24 grilles de paramètres, diagnostic de `tbasflw` et analyse du code source LISF.
- [`checks/02_preparation_ldt.md`](checks/02_preparation_ldt.md) : Options LDT, compilation Big-endian, vérification de `lis_input.d01.nc` et génération de `lis_input_corrigee.d01.nc`.
- [`checks/03_remapping_ruissellement.md`](checks/03_remapping_ruissellement.md) : Formulation géométrique du remap 181x121 → 180x120, conservation des 4 stades volumiques (S1 à S4) et filtrage par masque de bassin.
- [`checks/04_audit_routing_historique.md`](checks/04_audit_routing_historique.md) : Inventaire exhaustif des simulations historiques, diagnostic des 4 réservoirs et réfutation de l'ancien run brut.
- [`checks/05_evaluation_debits_historiques.md`](checks/05_evaluation_debits_historiques.md) : Confrontation aux 12 stations de jaugeage, analyse des crues, métriques KGE/NSE/PBIAS et paradoxes hydrologiques.
- [`checks/06_audit_coherence.md`](checks/06_audit_coherence.md) : Audit de cohérence méthodologique, recalcul du plancher numérique `cntime`, vérification du spin-up 1 an et résolution du paradoxe d'El Mers.
- [`checks/07_transition_hymap3_linres0.md`](checks/07_transition_hymap3_linres0.md) : Transition vers HyMAP-3, désactivation du réservoir linéaire (`linres = 0`), extinction de la dérive de nappe et simplification du protocole de spin-up suite aux recommandations directes d'Augusto Getirana.

---

## 15. Simulation HyMAP-2 OPL 2016–2020 sans réservoir linéaire (`linres = 0`) et Évaluation 2018

Suite aux recommandations d'Augusto Getirana (désactivation du réservoir linéaire souterrain pour assainir les récessions avant transition vers HyMAP-3), la simulation quinquennale OPL complète a été exécutée et validée.

### 15.1 Fichiers de configuration, soumission et sorties
- **Configuration LIS :** [`configs/lis_hymap2_opl_2016_2020_linres0.config`](configs/lis_hymap2_opl_2016_2020_linres0.config)
  - `HYMAP2 routing model linear reservoir flag: 0`
  - `HYMAP2 routing model start mode: coldstart` (aucun restart lu au démarrage)
  - Période : 01/01/2016 au 01/01/2021 (5 ans, 1 827 jours)
  - Domaine et paramètres : [`ldt_hymap/lis_input_corrigee.d01.nc`](ldt_hymap/lis_input_corrigee.d01.nc)
- **Script SLURM de production :** [`jobs/run_hymap2_linres0_opl_2016_2020.sh`](jobs/run_hymap2_linres0_opl_2016_2020.sh)
  - Exécution : **Job ID 8272794** (1 nœud, 16 tâches MPI, partition `compute`).
  - Temps de calcul réel : **28 min 43 s** (code de retour `0`, exit status `0`).
  - Logs : [`logs/slurm_hymap2_5y_lr0_opl_8272794.out`](logs/slurm_hymap2_5y_lr0_opl_8272794.out) et `logs/lislog_opl_linres0_2016_2020.*`.
- **Répertoire des sorties NetCDF :** `output/OPL_linres0_2016_2020/ROUTING/`
  - 1 827 fichiers journaliers NetCDF (`LIS_HIST_*.nc`, 100% complets, 0 jour manquant).
  - 61 fichiers de restart mensuels (`LIS_RST_*.nc`).
  - `BaseflowStor_tavg = 0.000000 mm` et `RunoffStor_tavg = 0.000000 mm` strictement nuls.
- **Cache extrait aux 12 stations :** [`output/OPL_linres0_2016_2020/t_sim_daily_12stations_opl_linres0.csv`](output/OPL_linres0_2016_2020/t_sim_daily_12stations_opl_linres0.csv).

### 15.2 Évaluation comparative 2018 à Lalla Chafia (`b_l_chafia`)
- **Figure comparative 3 panneaux :** [`plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2018_hymap2_linres0_vs_hist.png`](plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2018_hymap2_linres0_vs_hist.png) (et version vectorielle `.pdf`)
  - *(a) Full-Year 2018 Hydrograph at Lalla Chafia (Bouregreg Basin)*
  - *(b) High-Flow Period: Flood Peaks and Hydrograph Timing (March – April 2018)*
  - *(c) Summer Streamflow and Recession (June–September 2018)*
- **Tableau des métriques statistiques :** [`plots/sebou_bouregreg/tables/table_metrics_2018_lalla_chafia_linres0.csv`](plots/sebou_bouregreg/tables/table_metrics_2018_lalla_chafia_linres0.csv)
- **Script officiel et commande de régénération autonome (ciblée) :**
  ```bash
  python3 experiments/NorthMor/routing/scripts/evaluate_sebou_bouregreg.py --fig-linres0-2018
  ```
  - **Fichiers de données d'entrée nécessaires :**
    - Observations journalières ABH : `data/streamflow_clean/obs_daily.csv` (ou table consolidée `plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2018.csv`).
    - Routage historique (`linres=1`, spin-up restart C2) : `output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv`.
    - Routage modifié (`linres=0`, coldstart) : `output/OPL_linres0_2016_2020/t_sim_daily_12stations_opl_linres0.csv`.
  - **Identité stricte des forçages Noah-MP :** Les flux de ruissellement injectés ($Q_s, Q_{sb}$) proviennent tous deux de `runoff_remap_180x120/OPL_noirr_2016_2020` et sont rigoureusement identiques (différence maximale nulle sur l'ensemble des cellules et pas de temps).
  - **Condition d'état initial distincte :** `OPL_2016_2020_corrigee` démarre d'un restart issu du cycle de spin-up C2 au 01/01/2016, alors que `OPL_linres0_2016_2020` démarre en coldstart au 01/01/2016. En 2018 (3ᵉ année calendaire), le transit fluvial a convergé, mais cette différence d'initialisation reste documentée dans la légende.

#### Synthèse des métriques (364 jours communs valides, date manquante ABH : 06/01/2018)
| Métrique 2018 | Observations ABH | OPL Historique (`linres=1`) | OPL Modifié (`linres=0`) |
| :--- | :---: | :---: | :---: |
| Débit moyen annuel | 9.74 m³/s | 7.98 m³/s | **7.99 m³/s** |
| Biais moyen | — | -1.76 m³/s (-18.1 %) | **-1.75 m³/s (-17.9 %)** |
| RMSE | — | 19.20 m³/s | **18.81 m³/s** |
| Corrélation Pearson (r) | 1.000 | 0.437 | **0.456** |
| Critère NSE | 1.000 | 0.134 | **0.169** |
| Critère KGE | 1.000 | 0.017 | **0.079** |
| Débit moyen estival (juin–sept.) | 0.73 m³/s | 6.91 m³/s | **6.88 m³/s** |
| Maximum annuel simulé | 199.0 m³/s (08/03) | 34.0 m³/s (26/04) | **68.9 m³/s (25/04)** |

### 15.3 Résultats démontrés vs Hypothèses ouvertes
1. **Résultats démontrés :**
   - **Amélioration du synchronisme sur les crues :** Le calage du pic du 25 avril 2018 est exact le jour même de l'observation en `linres=0` (supprimant le retard de 24h observé en `linres=1`). En revanche, l'amplitude est sensiblement plus accentuée (68.9 m³/s simulés vs 41.4 m³/s observés le 25/04).
   - **Accélération du tarissement post-crue :** Dès la cessation des pluies printanières, la décrue est nettement plus franche, éliminant la traînée artificielle de plusieurs semaines induite par le réservoir linéaire.
   - **Persistance du plancher d'étiage estival :** Le débit estival moyen simulé reste quasi identique entre les deux configurations (6.91 m³/s en `linres=1` vs 6.88 m³/s en `linres=0`, pour 0.73 m³/s observé). La désactivation du réservoir linéaire n'élimine donc pas le biais positif estival.
2. **Hypothèses ouvertes et limites :**
   - **Origine du biais d'étiage :** Si la persistance des apports souterrains $Q_{sb}$ issus de Noah-MP constitue un contributeur majeur évident, le rôle potentiel de pertes en lit mineur (*transmission losses* alluviales), de prélèvements agricoles non jaugés ou d'infiltrations karstiques non représentées dans HyMAP demeure une hypothèse de travail ouverte. On évitera donc d'affirmer catégoriquement que Noah-MP explique 100 % du biais ou que HyMAP ne peut en aucun cas y contribuer.
   - **Sous-estimation de la crue de mars 2018 :** Le fort déficit sur l'événement des 07–08 mars (199.0 m³/s observé vs 24.0 m³/s simulé) persiste inchangé en `linres=0` et relève principalement du forçage pluviométrique IMERG ou de la partition infiltration/ruissellement amont.
   - **Différence d'initialisation :** L'historique OPL partait d'un restart issu du cycle de spin-up C2, tandis que la simulation `linres0` démarre en coldstart au 01/01/2016. La légende de la figure rappelle explicitement cette distinction.


---

## 16. Diagnostic multi-annuel des flux et des debits a Lalla Chafia (2016–2020)

### 16.1 Contexte et objectifs scientifiques
Suite au retour d'Augusto Getirana sur l'hydrogramme 2018 (suspicion d'un exces de ruissellement souterrain maintenant un plateau de debit artificiel en ete), un diagnostic approfondi des flux moyens amont a ete mene pour l'annee 2018 puis etendu a l'ensemble de la periode quinquennale 2016–2020 (1 827 jours calendaires, dont 1 826 jours communs valides avec les observations ABH, seule la journee du 06/01/2018 etant manquante).

### 16.2 Sources de donnees et methodologie d'extraction
- **Bassin versant amont :** Delimite depuis le reseau de drainage de [`ldt_hymap/lis_input_corrigee.d01.nc`](ldt_hymap/lis_input_corrigee.d01.nc) a partir de la cellule exutoire `(row=75, col=71)`. Il comprend **133 mailles HyMAP** pour une superficie cumulée de **3 333,35 km²**.
- **Precipitations ($P$) :** Extraites des sorties journalieres originales Noah-MP OPL (`matrix_2016_2020/OPL_noirr_2016_2020/output/`). La precipitation atmospherique totale correspond a `Rainf_f_tavg` (pluie liquide) et `Snowf_tavg` (neige). L'interpolation spatiale vers la grille HyMAP est bilineaire au centre des mailles (moyenne des 4 noeuds delimitant chaque cellule).
- **Ruissellements de surface ($Q_s$) et souterrain ($Q_{sb}$) :** Extraits directement des fichiers remappes conservatifs (`runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL/`) effectivement injectes dans HyMAP-2.
- **Debits a l'exutoire :** Confrontation directe entre observations ABH (`b_l_chafia`), simulation historique HyMAP-2 (`linres=1`) et simulation recente HyMAP-2 (`linres=0`, Job 8272794).

### 16.3 Figures et tables produites
- **Figure de synthese interannuelle (2016–2020) :** [`plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2016_2020_synthesis.png`](plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2016_2020_synthesis.png) (.pdf)
  - *(a) Precipitations interannuelles et partition annuelle du ruissellement ($P$, $Q_s$, $Q_{sb}$).*
  - *(b) Partition estivale des apports (juin–septembre) — $Q_{sb}$ represente plus de 90 % des apports estivaux pour chacune des 5 annees.*
  - *(c) Debits moyens estivaux et persistance du biais positif associe a des apports domines par $Q_{sb}$.*
- **Figure detaillee 3 panneaux (2018) :** [`plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2018_fluxes_and_streamflow.png`](plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2018_fluxes_and_streamflow.png) (.pdf)
  - *(a) Precipitations journalieres moyennes du bassin (pics de mars, avril et novembre 2018).*
  - *(b) Chroniques journalieres de $Q_s$, $Q_{sb}$ et ruissellement total.*
  - *(c) Hydrogramme comparatif (ABH, `linres=1`, `linres=0`), confirmant la recession physique continue en fin d'annee et l'absence de decrochage brutal a zero.*
- **Fichiers tabulaires (CSV) :**
  - Series journalieres 2016–2020 : [`plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2016_2020.csv`](plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2016_2020.csv)
  - Series journalieres 2018 : [`plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2018.csv`](plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2018.csv)
  - Bilan annuel et estival 2016–2020 : [`plots/sebou_bouregreg/tables/lalla_chafia_annual_summer_stats_2016_2020.csv`](plots/sebou_bouregreg/tables/lalla_chafia_annual_summer_stats_2016_2020.csv)

### 16.4 Synthese des resultats demontres vs Hypotheses
1. **Faits demontres :**
   - **Dominance estivale de $Q_{sb}$ superieure a 90 % confirmee sur les 5 annees :** 2016 (90,8 %), 2017 (90,4 %), 2018 (90,5 %), 2019 (94,2 %), 2020 (90,6 %). Les apports liquides estivaux recus par le modele de routage sont quasi exclusivement constitues de ruissellement souterrain issu de Noah-MP.
   - **Biais estival positif persistant sur toutes les annees :** Le debit moyen estival simule depasse systematiquement l'observe (+1,05 m³/s en 2016, +1,20 m³/s en 2017, +6,15 m³/s en 2018, +1,94 m³/s en 2019, +1,30 m³/s en 2020), alors que les observations ABH indiquent des etiages severes (0,2 a 0,7 m³/s).
   - **Gain systematique de `linres=0` sur `linres=1` :** Sur l'ensemble des 5 annees, `linres=0` ameliore constamment les criteres statistiques (NSE 2016: +0,187 vs +0,111 ; 2017: +0,121 vs +0,090 ; 2018: +0,169 vs +0,134 ; 2019: -0,262 vs -0,341 ; 2020: -0,019 vs -0,108).
   - **Continuite temporelle :** Les simulations ne presentent aucun decrochage artificiel a zero en fin d'annee.
2. **Hypotheses ouvertes et points a examiner :**
   - **Memoire hydrologique pluri-annuelle (2019) :** Malgre une faible pluviosite en 2019 (257,5 mm), le ruissellement souterrain et les debits estivaux sont restes eleves (2,48 m³/s simules vs 0,54 m³/s observes). Le stockage profond accumule lors de l'annee tres humide 2018 (780,0 mm) constitue une *hypothese de travail plausible*, mais n'est pas encore une conclusion formellement demontree (d'autres facteurs comme le parametrage des sols Noah-MP ou l'absence de prelevements/evaporation en riviere peuvent intervenir).
   - **Attribution du biais estival :** L'exces de debit en riviere est etroitement correle a des apports domines par $Q_{sb}$, mais l'attribution causale definitive necessite d'evaluer les pertes en lit mineur et les processus d'assimilation (DA).
   - **Sous-estimation de la crue de mars 2018 :** L'origine du deficit (forcage pluviometrique vs partition infiltration/ruissellement dans Noah-MP) reste a elucider.
   - **Conditions initiales distinctes en 2016 :** L'année 2016 est une année de production à part entière, mais les conditions initiales au 01/01/2016 diffèrent entre le routage historique (restart issu de spin-up C2) et le routage récent `linres=0` (coldstart). Bien que la dynamique de crue converge dès le printemps, la comparaison quantitative de 2016 doit intégrer cette différence d'état initial.

### 16.5 Commande de reproduction
```bash
python3 experiments/NorthMor/routing/scripts/diagnostic_lalla_chafia_flux.py --start-year 2016 --end-year 2020
```

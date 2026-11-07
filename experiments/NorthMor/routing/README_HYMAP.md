# Documentation de référence du routage HyMAP2 (Nord Maroc 2016–2020)

## 1. Objectif du routage HyMAP2 et lien avec Noah-MP

Cette chaîne assure le routage hydrodynamique hors ligne (*offline*) avec le modèle **HyMAP2** (*Hydrological Modeling and Analysis Platform, version 2*) des écoulements de surface et de subsurface simulés par le modèle de surface continentale **Noah-MP 4.0.1** sur le domaine Nord Maroc (`NorthMor`).

### 1.1 Couplage séquentiel Noah-MP → HyMAP2
1. **Simulation de surface (Noah-MP) :** Simule les bilans d'énergie et d'eau sur la grille régulière $181 \times 121$ (~5 km, repérage aux nœuds entiers de $30.00^\circ$ à $36.00^\circ\text{N}$ et $-10.00^\circ$ à $-1.00^\circ\text{E}$) et produit au pas journalier les flux :
   - `Qs_tavg` : ruissellement superficiel rapide ($kg \cdot m^{-2} \cdot s^{-1}$).
   - `Qsb_tavg` : drainage sous-racinaire profond / recharge de nappe ($kg \cdot m^{-2} \cdot s^{-1}$).
2. **Routage hydrodynamique (HyMAP2) :** Convertit ces flux en apports d'eau, les transfère à travers le réseau hydrographique discrétisé sur la grille $180 \times 120$ ($0.05^\circ$, repérage aux centres de mailles de $30.025^\circ$ à $35.975^\circ\text{N}$ et $-9.975^\circ$ à $-1.025^\circ\text{E}$), et simule l'onde de crue cinématique, l'expansion des plaines inondables et la vidange du réservoir de nappe vers les rivières.

### 1.2 Expériences de référence
Deux simulations quinquennales (2016–2020) constituent le socle de référence actuel :
- **Open-Loop (OPL)** : Simulation en boucle ouverte forcée par la météorologie sans assimilation (`OPL_noirr_2016_2020`).
- **Assimilation SMAP NoCDF (DA_nocdf)** : Assimilation par filtre de Kalman d'ensemble (EnKF) des données d'humidité du sol satellitaires SMAP L3 sans correction préalable de biais par CDF matching (`DA_nocdf_noirr_2016_2020`).
- **Assimilation SMAP DA-CDF (À réaliser)** : Troisième expérience dont l'hypothèse d'atténuation du biais de ruissellement sera formellement testée lors de la comparaison tripartite OPL / NoCDF / CDF (§12).

---

## 2. Structure des répertoires

L'arborescence opérationnelle et historique du répertoire `experiments/NorthMor/routing/` est organisée de manière modulaire :

```text
experiments/NorthMor/routing/
├── README_HYMAP.md                 # Le présent document de référence
├── configs/                        # Configurations LIS actives pour HyMAP2
│   ├── lis_hymap2_opl_spinup_c1_corrigee.config   # Spin-up Cycle 1 OPL corrigé (2016)
│   ├── lis_hymap2_opl_spinup_c2_corrigee.config   # Spin-up Cycle 2 OPL corrigé (2016)
│   ├── lis_hymap2_opl_2016_2020_corrigee.config   # Production 5 ans OPL corrigé
│   ├── lis_hymap2_da_nocdf_spinup_c1.config       # Spin-up Cycle 1 DA-NoCDF (2016)
│   ├── lis_hymap2_da_nocdf_spinup_c2.config       # Spin-up Cycle 2 DA-NoCDF (2016)
│   ├── lis_hymap2_da_nocdf_2016_2020.config       # Production 5 ans DA-NoCDF
│   ├── lis_test_offline.config                    # Test hors-ligne unitaire
│   └── _archive_raw/                              # [HISTORIQUE] Anciennes configs du run brut non corrigé
├── jobs/                           # Scripts SLURM d'exécution
│   ├── build_lis_hymap2.sh                        # Script de compilation de LIS HyMAP2
│   ├── run_hymap2_opl_spinup_c1_corrigee.sh       # Job SLURM Spin-up C1 OPL
│   ├── run_hymap2_opl_spinup_c2_corrigee.sh       # Job SLURM Spin-up C2 OPL
│   ├── run_hymap2_opl_2016_2020_corrigee.sh       # Job SLURM 5 ans OPL
│   ├── run_hymap2_da_nocdf_spinup_c1.sh           # Job SLURM Spin-up C1 DA-NoCDF
│   ├── run_hymap2_da_nocdf_spinup_c2.sh           # Job SLURM Spin-up C2 DA-NoCDF
│   ├── run_hymap2_da_nocdf_2016_2020.sh           # Job SLURM 5 ans DA-NoCDF
│   └── _archive_raw/                              # [HISTORIQUE] Anciens scripts SLURM du run brut
├── scripts/                        # Chaîne de scripts opérationnels
│   ├── remap_opl_2016_2020.py                     # Remapping conservatif Qs/Qsb OPL (181x121 -> 180x120)
│   ├── remap_da_nocdf_2016_2020.py                # Remapping conservatif Qs/Qsb DA-NoCDF
│   ├── check_spinup_criterion_corrigee.py         # Contrôle de convergence du spin-up OPL
│   ├── check_spinup_criterion_da_nocdf.py         # Contrôle de convergence du spin-up DA-NoCDF
│   ├── complete_t7bis_analysis.py                 # Diagnostic physique approfondi du run OPL corrigé
│   ├── complete_t8_analysis_and_plots.py          # Script principal d'évaluation aux 12 stations
│   ├── parse_stations.py                          # Analyseur des séries in-situ brutes ABH
│   ├── plot_streamflow_coverage.py                # Graphiques de couverture temporelle des stations
│   └── _history_tasks/                            # [HISTORIQUE] Scripts d'analyse exploratoire et pipelines
├── ldt_hymap/                      # Génération des paramètres sous LDT
│   ├── ldt.config                                 # Fichier de configuration LDT
│   ├── lis_input.d01.nc                           # Paramètres LDT bruts (tbasflw non corrigé)
│   └── lis_input_corrigee.d01.nc                  # Paramètres opérationnels (tbasflw divisé par 86400)
├── checks/                         # Dossiers d'audits et fiches techniques détaillées (00 à 06)
├── runoff_remap_180x120/           # Entrées routage : ruissellements reprojetés
│   ├── OPL_noirr_2016_2020/SURFACEMODEL/          # 1 828 fichiers journaliers NetCDF
│   └── DA_nocdf_noirr_2016_2020/SURFACEMODEL/     # 1 828 fichiers journaliers NetCDF
├── output/                         # Sorties de simulation et fichiers de restart
│   ├── OPL_spinup_c1_corrigee/ROUTING/            # Sorties et restart Cycle 1 OPL
│   ├── OPL_spinup_c2_corrigee/ROUTING/            # Sorties et restart Cycle 2 OPL
│   ├── OPL_2016_2020_corrigee/ROUTING/            # 1 827 fichiers journaliers NetCDF OPL
│   ├── DA_nocdf_spinup_c1/ROUTING/                # Sorties et restart Cycle 1 DA-NoCDF
│   ├── DA_nocdf_spinup_c2/ROUTING/                # Sorties et restart Cycle 2 DA-NoCDF
│   ├── DA_nocdf_2016_2020/ROUTING/                # 1 827 fichiers journaliers NetCDF DA-NoCDF
│   └── OPL_2016_2020/                             # [ARCHIVE] Sorties du run brut avec puits artificiel
├── plots/sebou_bouregreg/          # Résultats canoniques Sebou-Bouregreg (figures et tables 3exp)
├── plots/technical/                # Figures techniques (spinup, water_balance, parameters)
└── plots/_history/                 # Archives historiques (T5, T7, T8 t8_ol_nocdf, 3exp brut)
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
python3 experiments/NorthMor/routing/scripts/remap_opl_2016_2020.py

# Pour DA NoCDF :
python3 experiments/NorthMor/routing/scripts/remap_da_nocdf_2016_2020.py
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

### 8.2 Extraction et évaluation aux stations
Le script unifié extrait automatiquement les débits simulés au droit des 12 stations de jaugeage :
```bash
/home/mohammad.elaabaribao/.conda/envs/postproc_env/bin/python experiments/NorthMor/routing/scripts/complete_t8_analysis_and_plots.py
```
- **Mécanisme de mise en cache :** Pour optimiser les temps de traitement, le script met en cache les séries journalières extraites dans `output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv`.
- **Livrables produits :**
  - Table de synthèse : `plots/_history/t8_ol_nocdf/synthese_hydrologique_12stations.csv`.
  - Analyse des crues : `plots/_history/t8_ol_nocdf/t8_flood_events_comparison.csv`.
  - Figures de comparaison : `plots/_history/t8_ol_nocdf/F1_carte_situation.png` à `F6_effet_assimilation.png`.

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
Le script unifié (`complete_t8_analysis_and_plots.py`) calcule pour chaque station :
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

### 10.2 Synthèse des limites hydrologiques observées
1. **Absence d'assecs sur les oueds temporaires :** À la station de Sidi Jabeur (oued Grou), l'observation compte 310 à 312 jours à débit nul (assecs estivaux complets), alors que les simulations OPL et DA-NoCDF prédisent **0 jour d'assec** (maintien permanent d'un écoulement $\ge 0.1\text{ m}^3/s$). Cette défaillance résulte de la conjonction du drainage de nappe continu de Noah-MP et de l'absence de pertes en lit mineur dans HyMAP2.
2. **Déficit chronique sur le haut Sebou :** Les simulations OPL sous-estiment massivement les débits sur 6 des 7 stations du Sebou (PBIAS de $-56\%$ à $-78\%$, seule Ait Khabbach présentant une surestimation à $+74\%$). Les causes potentielles (sous-estimation des pluies d'altitude, résurgences karstiques non modélisées, prélèvements agricoles) restent des hypothèses physiques non isolées.
3. **Forte dégradation sous DA-NoCDF dans le Bouregreg :** L'assimilation sans correction préalable CDF injecte un excès massif d'eau (PBIAS atteignant $+115\%$ à $+480\%$, KGE s'effondrant jusqu'à $-3.86$).
4. **Désactivation des interactions nappe-rivière :** `dwi flag = 0` dans tous les runs pour neutraliser les ratios DWI fictifs de l'archive brute.

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

## 12. Procédure pour ajouter une nouvelle expérience (ex: DA-CDF)

### 12.1 Hypothèse scientifique à tester
Le routage de l'expérience **DA-CDF** corrigée n'a pas encore été réalisé. L'hypothèse scientifique sous-jacente est que la mise à l'échelle préalable de l'humidité du sol SMAP par CDF matching permettra de corriger l'injection excessive de ruissellement constatée avec DA-NoCDF. Cette hypothèse devra être formellement validée ou réfutée lors de la comparaison tripartite : **Open-Loop (OPL) vs DA-NoCDF vs DA-CDF**.

### 12.2 Protocole standardisé en 6 étapes
1. **Vérification des sorties Noah-MP :** Vérifier l'intégralité des 1 828 fichiers journaliers dans `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output/YYYY-MM/SURFACEMODEL/YYYYMM/`.
2. **Remapping conservatif Qs/Qsb (181x121 → 180x120) :** Créer et exécuter `scripts/remap_da_cdf_2016_2020.py` pour générer les ruissellements dans `runoff_remap_180x120/DA_cdf_noirr_2016_2020/`.
3. **Création des configurations LIS :** Créer `configs/lis_hymap2_da_cdf_spinup_c1.config`, `_c2.config` et `lis_hymap2_da_cdf_2016_2020.config` en pointant vers `ldt_hymap/lis_input_corrigee.d01.nc` avec `HYMAP2 routing model dwi flag: 0`.
4. **Exécution et validation du spin-up :** Exécuter les jobs de spin-up C1 puis C2, et vérifier le critère de convergence $\Delta_{rel}(BSFSTO) < 1.0\%$.
5. **Exécution de la simulation quinquennale :** Soumettre le job de production 5 ans et vérifier la création des 1 827 fichiers journaliers dans `output/DA_cdf_2016_2020/ROUTING/`.
6. **Évaluation hydrologique comparative :** Extraire la variable `Streamflow_tavg` au droit des 12 stations et confronter conjointement OPL, DA-NoCDF et DA-CDF aux observations.

### 12.3 État d'avancement de la préparation DA-CDF (Novembre 2026)
Conformément à ce protocole, l'ensemble des fichiers de la chaîne de routage DA-CDF ont été préparés :
- **Script de remapping** : `scripts/remap_da_cdf_2016_2020.py` (ciblant les 1 827 sorties de `DA_cdf_noirr_2016_2020`).
- **Configurations HyMAP** : `configs/lis_hymap2_da_cdf_spinup_c1.config`, `_c2.config` et `lis_hymap2_da_cdf_2016_2020.config` (chaînage C1 coldstart → C2 restart → Prod restart 2016–2020, `dwi flag: 0`, `lis_input_corrigee.d01.nc`).
- **Jobs SLURM** : `jobs/run_hymap2_da_cdf_spinup_c1.sh`, `_c2.sh` et `run_hymap2_da_cdf_2016_2020.sh`.

> [!NOTE]
> Les scripts et configurations DA-CDF sont prêts et validés statiquement. Aucun remapping complet et aucun routage DA-CDF n'ont encore été exécutés à ce stade.

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
| `DA_cdf_spinup_c1/ROUTING/` | `lis_input_corrigee.d01.nc` | **PRÉPARÉ (NON LANCÉ)** | Spin-up C1 DA-CDF configuré (coldstart, 2016). |
| `DA_cdf_spinup_c2/ROUTING/` | `lis_input_corrigee.d01.nc` | **PRÉPARÉ (NON LANCÉ)** | Spin-up C2 DA-CDF configuré (restart C1, 2016). |
| `DA_cdf_2016_2020/ROUTING/` | `lis_input_corrigee.d01.nc` | **PRÉPARÉ (NON LANCÉ)** | Production 5 ans continue DA-CDF configurée (restart C2, 2016–2020). |

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

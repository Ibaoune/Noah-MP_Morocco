# Audit Technique et Fiche de Reproduction : Préparation LDT des Paramètres HyMAP

Ce document consigne l'audit exhaustif, la reconstitution d'exécution et l'analyse comparative des fichiers de paramètres NetCDF générés par le processeur **LDT** (LIS Data Toolkit 7.5) pour le routage hydrodynamique HyMAP2 sur le domaine Nord Maroc ($180 \times 120$ à 0.05°).

---

## 1. Arborescence, Chemins d'Accès et Liaisons Symboliques

L'ensemble des opérations LDT a été configuré et exécuté dans le répertoire dédié :
`experiments/NorthMor/routing/ldt_hymap/`

### 1.1 Liaisons symboliques vers les données sources
Pour alimenter LDT, 24 liens symboliques ont été établis dans `ldt_hymap/`, pointant tous vers le répertoire des paramètres bruts extraits d'Augusto Getirana (`data/Hymap_params_from_Augusto/extracted/lis_param/`) :

| Nom du lien symbolique | Cible relative | Fichier source réel | Rôle dans `ldt.config` |
| :--- | :--- | :---: | :--- |
| `lis_nextx_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_nextx_005.bin` | Présent | `HYMAP flow direction x map` |
| `lis_nexty_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_nexty_005.bin` | Présent | `HYMAP flow direction y map` |
| `lis_nodelon_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_nodelon_005.bin` | Présent | `HYMAP node lon` |
| `lis_nodelat_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_nodelat_005.bin` | Présent | `HYMAP node lat` |
| `lis_nxtdst_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_nxtdst_005.bin` | Présent | `HYMAP grid distance map` |
| `lis_uparea_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_uparea_005.bin` | Présent | `HYMAP drainage area map` |
| `lis_basin_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_basin_005.bin` | Présent | `HYMAP basin map` + Placeholder bias |
| `lis_rivwth_merged_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_rivwth_merged_005.bin` | Présent | `HYMAP river width map` |
| `lis_rivwth_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_rivwth_005.bin` | Présent | *Non utilisé* (supplanté par `merged`) |
| `lis_rivhgt_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_rivhgt_005.bin` | Présent | `HYMAP river height map` |
| `lis_rivlen_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_rivlen_005.bin` | Présent | `HYMAP river length map` |
| `lis_rivman_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_rivman_005.bin` | Présent | `HYMAP river roughness map` |
| `lis_fldhgt_merged_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_fldhgt_merged_005.bin` | Présent | `HYMAP floodplain height map` (10 niveaux) |
| `lis_fldman_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_fldman_005.bin` | Présent | `HYMAP floodplain roughness map` |
| `lis_getirana_paiva_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_getirana_paiva_005.bin` | Présent | `HYMAP runoff time delay map` |
| `lis_trunoff_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_trunoff_005.bin` | Présent | `HYMAP runoff time delay mult.` |
| `lis_tbasflw_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_tbasflw_005.bin` | Présent | `HYMAP baseflow time delay map` |
| `lis_qrefer_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_qrefer_005.bin` | Présent | `HYMAP reference discharge map` (*non écrit*) |
| `lis_elevtn_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_elevtn_005.bin` | Présent | `HYMAP grid elevation map` |
| `lis_grarea_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_grarea_005.bin` | Présent | `HYMAP grid area map` |
| `lis_mask_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_mask_005.bin` | Présent | `HYMAP basin mask map` |
| `lis_real_mask_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_real_mask_005.bin` | Présent | Placeholder `flow type` et `dwi ratio` |
| `lis_maxlen_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_maxlen_005.bin` | Présent | *Non utilisé* (non requis par LDT) |
| `lis_slope_005.bin` | `../../../../data/Hymap_params_from_Augusto/extracted/lis_param/lis_slope_005.bin` | Présent | *Non utilisé* (pente issue de Noah-MP / NCEP) |

### 1.2 Analyse des cartes substituts (*placeholders*)
L'archive originale ne fournissant pas l'intégralité des cartes requises par les clés d'entrée de LDT, quatre paramètres ont été renseignés avec des substituts :
- `lis_real_mask_005.bin` a été substitué pour `HYMAP river flow type map`, `HYMAP baseflow dwi ratio map` et `HYMAP runoff dwi ratio map`.
- `lis_basin_005.bin` a été substitué pour `HYMAP runoff bias correction map`.

Dans le cadre du routage cinématique unidirectionnel (`flowtype = 1`), sans couplage nappe-inondation (`dwiflag = 0`) et sans correction de biais de ruissellement, ces quatre champs ne sont jamais lus par LISF lors des simulations de production.

---

## 2. Configuration de LDT (`ldt.config`)

Le fichier de configuration [`experiments/NorthMor/routing/ldt_hymap/ldt.config`](../ldt_hymap/ldt.config) regroupe trois blocs de directives :

### 2.1 Cadre général et grille spatiale
* `LDT running mode: "LSM parameter processing"`
* `Processed LSM parameter filename: ./lis_input.d01.nc`
* `Land surface model: "Noah-MP.4.0.1"`
* `Routing model: "HYMAP"`
* `Map projection of the LIS domain: latlon`
* `Run domain lower left lat: 30.025` / `Run domain lower left lon: -9.975`
* `Run domain upper right lat: 35.975` / `Run domain upper right lon: -1.025`
* `Run domain resolution (dx, dy): 0.05, 0.05` ($180 \times 120$ mailles centrées).

### 2.2 Champs de surface continentale Noah-MP
LDT ingère simultanément les paramètres du modèle de surface :
* **Occupation du sol :** `MODIS_Native` (`IGBPNCEP`, fichier `igbp.bin`, 20 classes).
* **Masque continental :** créé depuis MODIS (`create`, méthode `mode`).
* **Texture des sols :** `STATSGOFAO_Native` (fichier `topsoil30snew`, 16 classes).
* **Orographie MNT :** `GTOPO30_Native` (30 secondes d'arc).
* **Climatologies NCEP :** albédo mensuel, albédo de neige maximal (`maxsnoalb.asc`), fraction végétale verte mensuelle (`gfrac_*`), pente NCEP (`islope`), température profonde (`SOILTEMP.60`).
* **Forçage invariant MERRA-2 :** Fichier géopotentiel invariant `MERRA2_101.const_2d_asm_Nx.00000000.nc4` pour l'application du gradient thermique vertical (*lapse-rate*).

### 2.3 Directives hydrographiques HyMAP
* `HYMAP params spatial transform: none` (projection 1:1 sans interpolation spatiale).
* `HYMAP params map projection: latlon` (mêmes bornes et résolution que le domaine LIS).
* `HYMAP floodplain height levels: 10` (profil vertical d'inondation à 10 strates).

---

## 3. Historique d'Exécution et Preuves Matérielles

L'exécution originale de LDT a été menée le **24 octobre 2026 à 15:13** sur le cluster Toubkal. Les preuves directes conservées dans le répertoire `ldt_hymap/` sont :

1. **Journal d'exécution principal (`ldtlog.0000`, 14 802 octets) :**
   - Horodaté du 24/10/2026 à 15:13.
   - Confirme l'initialisation du domaine $180 \times 120$, le traitement des données de surface Noah-MP, puis l'ingestion séquentielle des 22 grilles de paramètres HyMAP déclarées sans agrégation (`No aggregation applied for parameter file ...`) ainsi que des 2 grilles de coordonnées nodales,
   - Se conclut par :
     ```text
     -- Finished writing parameters to netcdf output file --
     --------------------------------
      Finished LDT run
     --------------------------------
     ```
2. **Journal de diagnostic de masque (`MPFilltest.log`, 175 252 octets) :**
   - Horodaté du 24/10/2026 à 15:13.
   - Détaille le remplissage par plus proche voisin (*neighbor fill*) des valeurs de bordure côtière pour assurer l'accord masque-paramètres.

---

## 4. Environnement d'Exécution et Contraintes de Compilation

La reproduction rigoureuse de l'exécution LDT impose le respect de trois conditions techniques :

### 4.1 Chargement de l'environnement cluster
Le binaire LDT dépend de bibliothèques dynamiques partagées (notamment `libesmf.so`, NetCDF-Fortran, HDF5). L'environnement doit être initialisé via :
```bash
source /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/arch/arch_toubkal.env
```
*(ou via le chemin relatif [`../../../../arch/arch_toubkal.env`](../../../../arch/arch_toubkal.env)).*

### 4.2 Lecture des binaires *big-endian* sous GFortran
Les fichiers binaires d'Augusto Getirana ont été produits en encodage *big-endian* IEEE 754 sans en-tête d'enregistrement Fortran (*direct access*). Sur architecture x86_64 (*little-endian*), le compilateur GFortran exige la variable d'environnement :
```bash
export GFORTRAN_CONVERT_UNIT='big_endian'
```
*Sans cette variable, GFortran lit les octets dans l'ordre inverse, produisant des valeurs numériques corrompues ou des dépassements de capacité.*

### 4.3 Commande exacte de reproduction
Depuis le répertoire `experiments/NorthMor/routing/ldt_hymap/` :
```bash
../../../../src/lisf/ldt/LDT ldt.config
```

> [!CAUTION]
> **Avertissement :** Ne pas exécuter cette commande dans le dossier de production sans précaution, sous peine d'écraser le fichier `lis_input.d01.nc` de référence.

---

## 5. Contenu et Structure des Fichiers NetCDF Existants

### 5.1 Dimensions du fichier NetCDF
Les fichiers `lis_input.d01.nc` et `lis_input_corrigee.d01.nc` partagent exactement **12 dimensions** :

| Dimension | Taille | Description |
| :--- | :---: | :--- |
| `east_west` | 180 | Nombre de colonnes de la grille régulière 0.05° |
| `north_south` | 120 | Nombre de lignes de la grille régulière 0.05° |
| `east_west_b` | 184 | Grille étendue avec halo (est-ouest) |
| `north_south_b` | 124 | Grille étendue avec halo (nord-sud) |
| `east_west_MERRA2` | 576 | Grille zonale du forçage MERRA-2 global |
| `north_south_MERRA2` | 361 | Grille méridienne du forçage MERRA-2 global |
| `month` | 12 | Mois de l'année pour les climatologies de surface |
| `time` | 1 | Coordonnée temporelle stationnaire |
| `sfctypes` | 20 | Classes de végétation MODIS-IGBP |
| `soiltypes` | 16 | Classes de texture de sol STATSGO-FAO |
| `elevbins` | 1 | Tranches altimétriques de sous-maille |
| `fld_height_levels` | 10 | Niveaux verticaux de la plaine d'inondation HyMAP |

### 5.2 Les 23 variables HyMAP écrites par LDT

Toutes les variables sont de type `float32` et dimensionnées en 2D `(north_south, east_west)` soit $(120, 180)$, à l'exception de la hauteur d'inondation qui est 3D `(fld_height_levels, north_south, east_west)` soit $(10, 120, 180)$ :

| Variable NetCDF | Dimensions | `missing_value` | `scale_factor` / `add_offset` | `units` (brut) | Rôle et source |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `HYMAP_flow_direction_x` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Direction d'écoulement zonale (`lis_nextx_005.bin`) |
| `HYMAP_flow_direction_y` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Direction d'écoulement méridienne (`lis_nexty_005.bin`) |
| `HYMAP_node_lon` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Longitude du nœud aval (`lis_nodelon_005.bin`) |
| `HYMAP_node_lat` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Latitude du nœud aval (`lis_nodelat_005.bin`) |
| `HYMAP_grid_distance` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Distance au nœud suivant (`lis_nxtdst_005.bin`) |
| `HYMAP_drain_area` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Aire drainée amont (`lis_uparea_005.bin`) |
| `HYMAP_basin` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Identifiant du bassin hydrographique (`lis_basin_005.bin`) |
| `HYMAP_river_width` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Largeur du chenal principal (`lis_rivwth_merged_005.bin`) |
| `HYMAP_river_height` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Hauteur de berge du lit mineur (`lis_rivhgt_005.bin`) |
| `HYMAP_river_length` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Longueur du bief fluvial (`lis_rivlen_005.bin`) |
| `HYMAP_river_roughness` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Rugosité de Manning du chenal (`lis_rivman_005.bin`) |
| `HYMAP_floodplain_height` | $(10, 120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Profil altimétrique de plaine d'inondation (`lis_fldhgt_merged_005.bin`) |
| `HYMAP_floodplain_roughness` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Rugosité de Manning en plaine d'inondation (`lis_fldman_005.bin`) |
| `HYMAP_runoff_time_delay` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Temps de concentration superficiel (`lis_getirana_paiva_005.bin`) |
| `HYMAP_runoff_time_delay_multiplier` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Multiplicateur cinématique de ruissellement (`lis_trunoff_005.bin`) |
| `HYMAP_baseflow_time_delay` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` *(modifié en `days`)* | Délai de vidange souterraine (`lis_tbasflw_005.bin`) |
| `HYMAP_grid_elevation` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Altitude moyenne de la maille (`lis_elevtn_005.bin`) |
| `HYMAP_grid_area` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Superficie de la maille (`lis_grarea_005.bin`) |
| `HYMAP_basin_mask` | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Masque de drainage hydrographique (`lis_mask_005.bin`) |
| `HYMAP_river_flow_type` *(placeholder)* | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Régime d'écoulement (`lis_real_mask_005.bin`, inactif si flowtype=1) |
| `HYMAP_baseflow_dwi_ratio` *(placeholder)* | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Ratio DWI nappe (`lis_real_mask_005.bin`, inactif si dwiflag=0) |
| `HYMAP_runoff_dwi_ratio` *(placeholder)* | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Ratio DWI ruissellement (`lis_real_mask_005.bin`, inactif si dwiflag=0) |
| `HYMAP_runoff_bias_correction` *(placeholder)* | $(120, 180)$ | -9999.0 | 1.0 / 0.0 | `none` | Facteur de correction de biais (`lis_basin_005.bin`, inactif) |

*(Chaque variable comporte en outre un attribut `standard_name` identique à son nom et un attribut `num_bins = 1`).*

> [!NOTE]
> **Incohérence des attributs `vmin` et `vmax` écrits par LDT :**
> Dans le fichier NetCDF brut, LDT adjoint systématiquement à chaque variable deux attributs scalaires d'en-tête `vmin` et `vmax`. L'audit numérique démontre que **ces métadonnées sont incohérentes avec les plages physiques effectives** des paramètres : elles présentent fréquemment des anomalies manifestes telles que des inversions où `vmin > vmax` (par exemple `vmin = 19727.38` et `vmax = 18292.54` pour `HYMAP_river_roughness`, `vmin = 412.73` et `vmax = 367.10` pour `HYMAP_node_lon`, ou `vmin = 0.90` et `vmax = 0.15` pour `HYMAP_baseflow_dwi_ratio`). La cause exacte de ces valeurs écrites par LDT n'étant pas formellement établie dans le code source, ces métadonnées ne doivent en aucun cas être interprétées comme les bornes physiques réelles des variables.

### 5.3 Observation sur l'absence de `HYMAP_ref_discharge`
Bien que le fichier `lis_qrefer_005.bin` soit présent dans l'archive d'Augusto et déclaré dans `ldt.config`, la variable NetCDF correspondante **n'est pas écrite** dans `lis_input.d01.nc`.
* **Preuve dans le code source de LDT :** La routine `read_HYMAP_refq.F90` existe dans `src/lisf/ldt/params/HYMAP/`, mais elle n'est appelée par aucune directive de traitement dans `HYMAP_parmsMod.F90`.
* **Conséquence :** Cette omission n'est pas bloquante pour la configuration actuelle de routage cinématique (`flowtype = 1`), mais son besoin fonctionnel pour d'autres options hydrodynamiques reste non résolu.

### 5.4 Les 22 variables de surface continentale et repérage spatial
Le fichier contient également 22 variables non hydrographiques :
`ALBEDO`, `DOMAINMASK`, `ELEVATION`, `ELEVDIFF_MERRA2`, `ELEVFGRD`, `ELEV_MERRA2`, `GREENNESS`, `LANDCOVER`, `LANDMASK`, `MXSNALBEDO`, `NOAHMP36_PBLH`, `SHDMAX`, `SHDMIN`, `SLOPETYPE`, `SURFACETYPE`, `TBOT`, `TEXTURE`, `lat`, `lat_b`, `lon`, `lon_b`, `time`.

* **Justification d'architecture logicielle :** Dans LISF, même en configuration de routage hors ligne, la routine d'initialisation du domaine (`LIS_domain_init`) vérifie et lit les coordonnées, le masque continental (`LANDMASK`), l'orographie (`ELEVATION`) et le type de surface (`SURFACETYPE`) depuis le fichier de paramètres maître déclaré dans `lis.config`. Les autres variables (albédo, végétation, texture) sont générées par LDT du fait de l'activation du mode `LSM parameter processing` pour Noah-MP.

---

## 6. Comparaison Microscopique : `lis_input.d01.nc` vs `lis_input_corrigee.d01.nc`

Une comparaison systématique sous `netCDF4` et `numpy` établit que :
1. **Dimensions :** 12 dimensions strictement identiques.
2. **Attributs globaux :** 28 attributs globaux strictement identiques.
3. **Variables identiques (44 sur 45) :** Toutes les variables (les 22 variables HyMAP restantes et les 22 variables de surface) présentent des **valeurs numériques décodées et attributs identiques selon la comparaison netCDF4** (mêmes valeurs numériques, masques et attributs de variable).
4. **Variable modifiée unique : `HYMAP_baseflow_time_delay`** :
   - Attribut `units` : `'none'` dans le brut $\rightarrow$ `'days'` dans le corrigé.
   - Données numériques : strictement divisées par **86 400.0** sur l'ensemble de la grille.

| Statistique | `lis_input.d01.nc` (Brut) | `lis_input_corrigee.d01.nc` (Corrigé) | Ratio brut / corrigé |
| :--- | :---: | :---: | :---: |
| Minimum | $203.65605$ | $0.00235713$ | $86\,400.00$ |
| Médiane | $6\,688.70$ | $0.077415$ | $86\,400.00$ |
| Moyenne | $61\,702.98$ | $0.714155$ | $86\,400.00$ |
| Maximum | $2\,631\,664.50$ | $30.45908$ | $86\,400.00$ |

5. **Différence de taille de fichier sur disque :**
   `lis_input.d01.nc` pèse 2 532 062 octets contre 2 587 165 octets pour `lis_input_corrigee.d01.nc` (+55 103 octets). Cette variation s'explique par la réallocation de chunks compressés HDF5/zlib lors de la réécriture in-place sous Python sans tassement de conteneur.

---

## 7. Commande Python Historique de Modification

> [!CAUTION]
> **STATUT : COMMANDE HISTORIQUE / NON VALIDÉE SCIENTIFIQUEMENT**
> Cette commande est documentée à des fins de traçabilité et de reproductibilité historique. Elle n'est **pas destinée à être réexécutée immédiatement** sans validation préalable du schéma hydrologique.

La création de `lis_input_corrigee.d01.nc` a été réalisée le 25 octobre 2026 à 21:32:44 par l'instruction Python en ligne suivante :

```python
python3 -c "
import shutil
import netCDF4 as nc

src = 'experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc'
dst = 'experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc'

# 1. Duplication intégrale du fichier LDT brut
shutil.copyfile(src, dst)

# 2. Division de tbasflw par 86400.0 et affectation de l'unité 'days'
with nc.Dataset(dst, 'r+') as ds:
    v = ds.variables['HYMAP_baseflow_time_delay']
    v[:] = v[:] / 86400.0
    v.units = 'days'
"
```

---

## 8. Incertitudes Scientifiques et Limites Méthodologiques

L'audit met en évidence quatre incertitudes majeures restant ouvertes :

1. **Unités et plancher numérique de `tbasflw` :**
   - Le code LISF attend `tbsflw` en jours (`qbas = basfsto / (tbsflw * 86400.)`).
   - Les unités physiques d'origine des grilles fournies par Augusto ne sont pas confirmées de façon indépendante.
   - La division par 86 400 appliquée dans le fichier corrigé force la condition numérique de garde `where(tbsflw < cntime/86400.) tbsflw = cntime/86400.` à s'activer sur **99.9 % des mailles actives** (15 921 cellules sur 15 937). Le délai de vidange souterrain effectif est alors calé sur le temps de concentration de surface ($2.45\text{ jours}$ en médiane).
   - Cette modification stabilise le bilan de masse global du réservoir de nappe en éliminant l'accumulation infinie observée en run brut, mais elle homogénéise le temps de séjour souterrain sur la cinématique superficielle. Son impact exact sur les dynamiques de décrue et les régimes d'étiage n'est pas étayé par une validation physique formelle et demeure une question ouverte nécessitant une confrontation avec les débits observés en station. Cette conversion ne peut donc pas être qualifiée de scientifiquement validée.
2. **Anomalie de superficie des mailles (`HYMAP_grid_area` / `grarea`) :**
   - Les superficies atteignent jusqu'à $178.9\text{ km}^2$, avec 3 020 mailles supérieures à $40\text{ km}^2$, alors que l'aire géométrique réelle d'une maille à 0.05° sur l'ellipsoïde terrestre est strictement comprise entre $24.6\text{ km}^2$ et $26.8\text{ km}^2$. L'origine physique de cette discordance reste à élucider.
3. **Cohérence spatiale des masques continentaux et hydrographiques :**
   - Le masque continental Noah-MP (`LANDMASK`) compte **15 888 mailles terrestres** actives (`LANDMASK == 1.0`, sur un domaine total de $180 \times 120 = 21\,600$ mailles).
   - Le masque hydrographique HyMAP (`HYMAP_basin_mask`) compte **15 937 mailles actives** (`HYMAP_basin_mask == 1.0`), 1 950 mailles avec valeur zéro (`0.0`) et 3 713 mailles nodata (`-9999.0`, masquées sous netCDF4).
   - **Décomposition des écarts entre masques :**
     - Lors d'une évaluation booléenne standard sous `netCDF4` (`(LANDMASK == 1) != (HYMAP_basin_mask == 1)`), le tableau masqué ignore les 3 713 mailles nodata, laissant **136 mailles discordantes** :
       - **98 mailles actives dans HyMAP mais inactives dans LANDMASK** (`HYMAP_basin_mask == 1.0` et `LANDMASK == 0.0`), situées le long du trait de côte (immédiatement adjacentes au littoral MODIS).
       - **38 mailles actives dans LANDMASK mais nulles dans HyMAP** (`LANDMASK == 1.0` et `HYMAP_basin_mask == 0.0`), réparties à l'intérieur des terres ou en bordure.
     - En incluant les **11 mailles actives dans LANDMASK mais en valeur nodata dans HyMAP** (`LANDMASK == 1.0` et `HYMAP_basin_mask == -9999.0`, situées en bordure de domaine ou côtière), l'écart cellule par cellule sur la grille complète atteint **147 mailles** ($98 + 38 + 11 = 147$, soit 98 mailles actives HyMAP hors masque continental et 49 mailles continentales inactives dans HyMAP, expliquant la différence nette $15\,937 - 15\,888 = 49$ mailles).
4. **Statut de `HYMAP_ref_discharge` :**
   - L'impact de la non-génération de cette variable par LDT sur d'autres schémas hydrauliques reste indéterminé.

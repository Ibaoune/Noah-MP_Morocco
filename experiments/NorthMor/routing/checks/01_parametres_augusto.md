# Audit Technique et Fiche d'Inventaire des Paramètres HyMAP d'Augusto Getirana

Ce document consigne l'inventaire factuel, la vérification cryptographique et l'analyse technique des paramètres hydrographiques HyMAP à 0.05° fournis pour le Nord Maroc par Augusto Getirana (NASA Goddard Space Flight Center).

---

## 1. Provenance et Traçabilité Cryptographique

### 1.1 Source et archive originale
* **Fournisseur :** Augusto Getirana (NASA GSFC, Hydrological Sciences Laboratory).
* **Archive source :** `data/Hymap_params_from_Augusto/lis_param.tar.gz` (taille : 971 307 octets).
* **Empreinte SHA-256 de l'archive :**
  `eb7dc30e3502c133c0c50364fec594c2a2ef372069cdef7813a9b754bcc96cc4`
* **Contrôle d'intégrité :** L'intégralité des 24 fichiers binaires extraits dans `data/Hymap_params_from_Augusto/extracted/lis_param/` a été vérifiée par calcul SHA-256 et concorde strictement avec les empreintes archivées dans [`00_checksums_augusto.txt`](00_checksums_augusto.txt).

### 1.2 Métadonnées d'origine (Fichier `header`)
L'archive tar originale contient un fichier texte d'en-tête [`header`](../../../../data/Hymap_params_from_Augusto/extracted/header) horodaté du 13 octobre 2026 à 21:05 (utilisateur `agetiran/s1189`) :
```text
merit  1   10800    7199  0.000833  -10.000000000   -1.000000000   30.000000000   36.000000000
```
Ce fichier d'en-tête atteste d'une source liée à MERIT (résolution native de 3 secondes d'arc $\approx 0.000833^\circ$, grille source $10\,800 \times 7\,199$ points sur $[-10^\circ, -1^\circ]\text{E} \times [30^\circ, 36^\circ]\text{N}$). Il témoigne de l'origine MERIT des données hydrographiques de base, mais ne constitue pas une preuve documentée de la méthode exacte d'agrégation, de vectorisation ou de mise à l'échelle (*upscaling*) employée pour dériver chacun des paramètres à 0.05°.

### 1.3 Domaine et discrétisation spatiale
* **Dimensions de la grille :** $180 \text{ colonnes} \times 120 \text{ lignes}$ (21 600 mailles 2D).
* **Résolution spatiale :** $dx = 0.05^\circ$, $dy = 0.05^\circ$ (projection cylindrique équidistante / latlon).
* **Centres des mailles extrêmes :**
  - Coin inférieur gauche (Sud-Ouest) : centre à $(30.025^\circ\text{N}, -9.975^\circ\text{E})$.
  - Coin supérieur droit (Nord-Est) : centre à $(35.975^\circ\text{N}, -1.025^\circ\text{E})$.
* **Limites externes du domaine :** $30.00^\circ\text{N}$ à $36.00^\circ\text{N}$, $-10.00^\circ\text{E}$ à $-1.00^\circ\text{E}$.

---

## 2. Tableau Exhaustif des 24 Paramètres Originaux

Les 24 fichiers binaires sont au format direct sans en-tête Fortran (*direct access*, encodage *big-endian*). Ils se répartissent en deux types de données distincts :
* **20 fichiers réels en virgule flottante simple précision `float32` (IEEE 754) :** 19 grilles 2D de taille exacte 86 400 octets ($180 \times 120 \times 4$ octets) et 1 profil d'inondation 3D à 10 niveaux verticaux de 864 000 octets (`lis_fldhgt_merged_005.bin`, $10 \times 180 \times 120 \times 4$ octets).
* **4 fichiers en entiers signés 32 bits `int32` :** 4 grilles 2D de 86 400 octets (`lis_nextx_005.bin`, `lis_nexty_005.bin`, `lis_basin_005.bin`, et `lis_mask_005.bin`). Ces fichiers ne sont pas en virgule flottante.

| Nom de fichier binaire | Définition physique / hydrologique | Grille et Type binaire | Unités dans le code LISF / Documentation | Rôle dans `ldt.config` | Variable NetCDF générée |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `lis_nextx_005.bin` | Indice X (colonne) de la cellule aval cible | $180 \times 120$, `int32` big-endian | Indice 1-indexé (ou -9 = exutoire mer) | `HYMAP flow direction x map` | `HYMAP_flow_direction_x` |
| `lis_nexty_005.bin` | Indice Y (ligne) de la cellule aval cible | $180 \times 120$, `int32` big-endian | Indice 1-indexé (ou -9 = exutoire mer) | `HYMAP flow direction y map` | `HYMAP_flow_direction_y` |
| `lis_nodelon_005.bin` | Longitude géodésique du noeud fluvial principal | $180 \times 120$, `float32` big-endian | Degrés décimaux Est ($^\circ\text{E}$) | `HYMAP node lon` | `HYMAP_node_lon` |
| `lis_nodelat_005.bin` | Latitude géodésique du noeud fluvial principal | $180 \times 120$, `float32` big-endian | Degrés décimaux Nord ($^\circ\text{N}$) | `HYMAP node lat` | `HYMAP_node_lat` |
| `lis_nxtdst_005.bin` | Distance de routage vers la maille aval | $180 \times 120$, `float32` big-endian | Mètres ($\text{m}$) (`HYMAP2_routingMod.F90` l.1213) | `HYMAP grid distance map` | `HYMAP_grid_distance` |
| `lis_uparea_005.bin` | Superficie drainée amont cumulée | $180 \times 120$, `float32` big-endian | Mètres carrés ($\text{m}^2$) (`HYMAP2_routingMod.F90` l.654) | `HYMAP drainage area map` | `HYMAP_drain_area` |
| `lis_basin_005.bin` | Identifiant entier du bassin hydrographique | $180 \times 120$, `int32` big-endian | Code entier identifiant | `HYMAP basin map` + Placeholder bias | `HYMAP_basin` |
| `lis_rivwth_merged_005.bin` | Largeur du chenal avec estuaires fusionnés | $180 \times 120$, `float32` big-endian | Mètres ($\text{m}$) (`HYMAP2_routingMod.F90` l.1098) | `HYMAP river width map` | `HYMAP_river_width` |
| `lis_rivwth_005.bin` | Largeur du chenal hydraulique pure (max 148.5 m) | $180 \times 120$, `float32` big-endian | Mètres ($\text{m}$) | **Non utilisé** (supplanté par `merged`) | *(aucune)* |
| `lis_rivhgt_005.bin` | Profondeur à pleins bords / hauteur de berge | $180 \times 120$, `float32` big-endian | Mètres ($\text{m}$) (`HYMAP2_routingMod.F90` l.1131) | `HYMAP river height map` | `HYMAP_river_height` |
| `lis_rivlen_005.bin` | Longueur réelle du bief fluvial dans la maille | $180 \times 120$, `float32` big-endian | Mètres ($\text{m}$) (`HYMAP2_routingMod.F90` l.1120) | `HYMAP river length map` | `HYMAP_river_length` |
| `lis_rivman_005.bin` | Coefficient de rugosité de Manning du lit mineur | $180 \times 120$, `float32` big-endian | $\text{s}\cdot\text{m}^{-1/3}$ (`HYMAP2_routingMod.F90` l.1153) | `HYMAP river roughness map` | `HYMAP_river_roughness` |
| `lis_fldhgt_merged_005.bin` | Profil altimétrique d'inondation (10 niveaux) | $10 \times 180 \times 120$, `float32` | Mètres ($\text{m}$ au-dessus du lit) | `HYMAP floodplain height map` | `HYMAP_floodplain_height` |
| `lis_fldman_005.bin` | Coefficient de Manning du lit majeur / plaine | $180 \times 120$, `float32` big-endian | $\text{s}\cdot\text{m}^{-1/3}$ (`HYMAP2_routingMod.F90` l.1188) | `HYMAP floodplain roughness map` | `HYMAP_floodplain_roughness` |
| `lis_getirana_paiva_005.bin` | Temps de concentration du ruissellement rapide | $180 \times 120$, `float32` big-endian | Secondes ($\text{s}$) (`HYMAP2_modelMod.F90` l.98) | `HYMAP runoff time delay map` | `HYMAP_runoff_time_delay` |
| `lis_trunoff_005.bin` | Multiplicateur du temps de ruissellement | $180 \times 120$, `float32` big-endian | Adimensionnel (valeur = 1.0) | `HYMAP runoff time delay mult.` | `HYMAP_runoff_time_delay_multiplier` |
| `lis_tbasflw_005.bin` | Constante de temps de vidange de nappe | $180 \times 120$, `float32` big-endian | LISF attend des jours ; unités brutes non confirmées | `HYMAP baseflow time delay map` | `HYMAP_baseflow_time_delay` |
| `lis_qrefer_005.bin` | Débit interannuel de référence hydraulique | $180 \times 120$, `float32` big-endian | $\text{m}^3/\text{s}$ (`HYMAP2_routingMod.F90` l.1136) | `HYMAP reference discharge map` | `HYMAP_ref_discharge` |
| `lis_elevtn_005.bin` | Altitude moyenne du modèle numérique de terrain | $180 \times 120$, `float32` big-endian | Mètres a.s.l. ($\text{m}$) (`HYMAP2_routingMod.F90` l.650) | `HYMAP grid elevation map` | `HYMAP_grid_elevation` |
| `lis_grarea_005.bin` | Superficie de la maille de routage | $180 \times 120$, `float32` big-endian | Mètres carrés ($\text{m}^2$) (`HYMAP2_routingMod.F90` l.1223) | `HYMAP grid area map` | `HYMAP_grid_area` |
| `lis_mask_005.bin` | Masque d'activité du domaine (-9999 / 0 / 1) | $180 \times 120$, `int32` big-endian | Masque entier binaire | `HYMAP basin mask map` | `HYMAP_basin_mask` |
| `lis_real_mask_005.bin` | Version réelle flottante du masque (-9999 / 0 / 1) | $180 \times 120$, `float32` big-endian | Masque réel flottant | Placeholders DWI et flow type | `HYMAP_river_flow_type`, `*dwi_ratio` |
| `lis_maxlen_005.bin` | Longueur maximale de transfert sub-maille | $180 \times 120$, `float32` big-endian | Mètres ($\text{m}$) | **Non utilisé** (non demandé par LDT) | *(aucune)* |
| `lis_slope_005.bin` | Pente topographique du lit fluvial | $180 \times 120$, `float32` big-endian | $\text{m}/\text{m}$ | **Non utilisé** (pente issue de Noah-MP / NCEP) | *(aucune)* |

---

## 3. Cartographie Effective dans LDT et Rôle des Placeholders

Quatre cartes attendues par LDT n'étaient pas fournies dans l'archive originale. La configuration [`ldt.config`](../ldt_hymap/ldt.config) a utilisé des substituts (*placeholders*) :
```text
HYMAP river flow type map:               ./lis_real_mask_005.bin   # Placeholder
HYMAP baseflow dwi ratio map:            ./lis_real_mask_005.bin   # Placeholder
HYMAP runoff dwi ratio map:              ./lis_real_mask_005.bin   # Placeholder
HYMAP runoff bias correction map:        ./lis_basin_005.bin       # Placeholder
```

* **`HYMAP river flow type map` :**
  Dans [`src/lisf/lis/routing/HYMAP2_router/HYMAP2_routingMod.F90`](../../../../src/lisf/lis/routing/HYMAP2_router/HYMAP2_routingMod.F90#L1306-L1308), cette variable n'est lue que si `flowtype == 0` ou `flowtype == 4`. Or, la clé `HYMAP2 routing method: kinematic` impose `flowtype = 1` (l. 409). La variable NetCDF n'est donc **jamais lue** lors des simulations de production.
* **`HYMAP baseflow dwi ratio map` et `HYMAP runoff dwi ratio map` :**
  Dans `HYMAP2_routingMod.F90` (l. 1272-1300), ces variables ne sont lues que si `dwiflag == 1`. Tous les fichiers `lis.config` de notre chaîne fixent `HYMAP2 routing model dwi flag: 0`, ce qui force les ratios de transfert nappe-inondation à 0.0 et **neutralise complètement leur lecture**.
* **`HYMAP runoff bias correction map` :**
  La variable NetCDF `HYMAP_runoff_bias_correction` écrite par LDT **n'apparaît dans aucune routine de calcul** du routeur HYMAP2.
* **Mise en garde scientifique :** L'absence d'impact de ces bouche-trous est établie **strictement dans le cadre de la configuration actuelle** (routage cinématique unidirectionnel hors ligne avec `dwiflag = 0`). Toute tentative future d'activer le couplage nappe-rivière (DWI) ou un schéma d'écoulement local/urbain exigerait la production de cartes physiques réelles.

---

## 4. Analyse Critique de `tbasflw` : Code LISF, Données Brutes et Simulations

Le délai de vidange de l'écoulement de base souterrain (`tbasflw`) constitue un paramètre clé du routage.

### 4.1 Faits démontrés dans le code source de LISF 7.5
1. **Attente du code source :**
   Dans [`src/lisf/lis/routing/HYMAP2_router/HYMAP2_modelMod.F90`](../../../../src/lisf/lis/routing/HYMAP2_router/HYMAP2_modelMod.F90#L111) :
   ```fortran
   qbas = basfsto / (tbsflw * 86400.)
   ```
   Comme `basfsto` est un volume en $\text{m}^3$, `dt` est en secondes et `qbas` est un débit en $\text{m}^3/\text{s}$, le dénominateur représente une durée en secondes. La présence du facteur multiplicateur explicite `86400.` indique mathématiquement que **le code source LISF attend `tbsflw` en jours**.
2. **Plancher numérique d'initialisation :**
   Dans `HYMAP2_routingMod.F90` (l. 1265) :
   ```fortran
   where(tbsflw < cntime/86400. .and. cntime > 0) tbsflw = cntime/86400.
   ```
   `cntime` (temps de concentration du ruissellement superficiel rapide issu de `lis_getirana_paiva_005.bin`, moyenne $325\,138\text{ s} \approx 3.76\text{ j}$) est divisé par 86 400 pour être comparé à `tbsflw`, confirmant que `tbsflw` est manipulé en jours dans le modèle.

### 4.2 Valeurs du fichier binaire brut
* Dans `lis_tbasflw_005.bin`, les valeurs valides sur les 15 937 mailles actives présentent un minimum de $203.7$, une médiane de $6\,688.7$, une moyenne de $61\,703.0$ et un maximum de $2\,631\,664.5$.
* Les unités physiques des valeurs binaires d'origine fournies par Augusto ne sont **pas confirmées de façon indépendante** (l'archive ne contient aucune documentation d'unité pour ce champ).
* À titre d'ordre de grandeur :
  - Si ces valeurs étaient lues comme des jours, la vidange moyenne prendrait environ 169 ans.
  - Si elles représentaient des secondes, elles correspondraient à un minimum de $3.4\text{ minutes}$, une médiane de $1.86\text{ heure}$, une moyenne de $17.1\text{ heures}$ et un maximum de $30.5\text{ jours}$.

### 4.3 Comportement en simulation
* **Simulation avec fichier brut (`lis_input.d01.nc`) :** En injectant le champ binaire brut sans division, la multiplication par 86 400 dans le code génère un temps de vidange de l'ordre du siècle. Le réservoir souterrain BSFSTO accumule $16\,518\text{ hm}^3$ en 5 ans de manière strictement monotone ($R^2 = 0.977$), piégeant 97.5 % du débit de base $Q_{sb}$ et provoquant un sous-débit fluvial massif.
* **Simulation avec NetCDF corrigé (`lis_input_corrigee.d01.nc`) :** Les simulations de production existantes (Open-Loop et DA-NoCDF) ont utilisé le fichier NetCDF corrigé, dans lequel la variable `HYMAP_baseflow_time_delay` a été divisée par 86 400. Sous cette division, le plancher numérique `cntime/86400.` devient actif dans 99.9 % des mailles actives (délai effectif médian calé sur $2.45\text{ jours}$). Le spin-up se stabilise dès le premier cycle ($\Delta S < 0.14\%$) et la conservation de masse sur 5 ans est rigoureusement respectée ($V_{sim} \approx V_{in}$).

### 4.4 Prudence méthodologique et statut
* **Absence de confirmation d'origine :** Les intentions initiales de l'auteur concernant les unités de `lis_tbasflw_005.bin` (export accidentel en secondes ou adéquation avec une variante antérieure de routine) ne sont pas formellement attestées.
* **Nécessité de vérifications ultérieures :** La division par 86 400 appliquée dans `lis_input_corrigee.d01.nc` stabilise le bilan de masse des runs de production, mais entraîne un écrasement quasi-systématique du paramètre par le plancher numérique `cntime/86400.`. Cette correction et ses répercussions hydrologiques réelles sur la dynamique d'étiage et le temps de réponse du bassin nécessitent des vérifications plus approfondies.

---

## 5. Anomalies et Points d'Attention Signalés

Les paramètres suivants présentent des valeurs atypiques qui restent **explicitement signalées pour investigation physique ultérieure**, sans préjuger ni inventer à ce stade d'explications sur leur cause :

1. **Superficie des mailles (`lis_grarea_005.bin`) :**
   - Les valeurs s'étendent de $22\,256\text{ m}^2$ ($0.022\text{ km}^2$, bordures maritimes) jusqu'à **$178\,880\,670\text{ m}^2$ ($178.9\text{ km}^2$)**, avec 3 020 mailles dépassant $40\text{ km}^2$.
   - *Constat géométrique :* Pour une grille régulière à $0.05^\circ \times 0.05^\circ$ entre $30^\circ\text{N}$ et $36^\circ\text{N}$, l'aire géodésique théorique d'une cellule sur le sphéroïde terrestre varie strictement entre **$24.6\text{ km}^2$** (à $36^\circ\text{N}$) et **$26.8\text{ km}^2$** (à $30^\circ\text{N}$). L'apparition de superficies allant jusqu'à $178.9\text{ km}^2$ constitue une anomalie flagrante qui reste réservée pour étude physique approfondie.
2. **Profondeur à pleins bords du chenal (`lis_rivhgt_005.bin`) :**
   - Les valeurs sont quasi-uniformes entre $0.500\text{ m}$ et $0.554\text{ m}$ sur l'ensemble des 15 937 mailles actives du domaine (médiane à $0.500\text{ m}$).
   - Cette quasi-invariance et cette hauteur uniforme de ~50 cm à l'échelle de l'ensemble des bassins du Nord Maroc sont signalées pour examen géomorphologique ultérieur.
3. **Largeur fusionnée du chenal (`lis_rivwth_merged_005.bin`) :**
   - Les largeurs atteignent jusqu'à $14\,263.9\text{ m}$ (~14.3 km) aux débouchés maritimes, avec 156 mailles présentant une largeur supérieure à $1\,000\text{ m}$. Ce comportement aux exutoires est maintenu pour investigation ultérieure.
4. **Rugosité de Manning du lit mineur (`lis_rivman_005.bin`) :**
   - Plage de variation très resserrée et élevée : $n = 0.1015$ à $0.1042\,\text{s}\cdot\text{m}^{-1/3}$. Des rugosités d'environ 0.10 sont élevées pour des lits fluviaux de plaine et sont signalées pour calibration ou révision future.

---

## 6. Domaine, Réutilisabilité et Précautions Méthodologiques

* **Spécificité géographique et spatiale :** Les 24 fichiers binaires sont strictement restreints au domaine Nord Maroc ($[-10.0^\circ, -1.0^\circ]\text{E} \times [30.0^\circ, 36.0^\circ]\text{N}$) sur la grille régulière $180 \times 120$ à 0.05°.
* **Précautions de réutilisation :**
  Ces paramètres ne peuvent pas être considérés a priori comme physiquement validés dans leur intégralité ni comme universellement réutilisables. Toute réutilisation pour d'autres simulations requiert de vérifier :
  - La concordance stricte de la grille spatiale ($180 \times 120$ à 0.05°, mêmes bornes et centres).
  - La compatibilité avec la version de HyMAP2 / LISF.
  - La configuration retenue : la neutralité des placeholders (`lis_real_mask_005.bin` et `lis_basin_005.bin`) n'est garantie qu'en mode cinématique (`flowtype = 1`) avec couplage nappe désactivé (`dwiflag = 0`). Toute autre configuration nécessiterait des données physiques réelles.
* **Traitement de `tbasflw` :**
  Les simulations existantes de production ont utilisé le fichier NetCDF corrigé (`lis_input_corrigee.d01.nc`). La transposition de cette correction et ses conséquences hydrologiques doivent faire l'objet de vérifications attentives pour toute nouvelle application.

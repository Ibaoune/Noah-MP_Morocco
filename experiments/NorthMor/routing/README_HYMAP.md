# Documentation de reproduction du routage HyMAP2 (Nord Maroc 2016–2020)

## 1. Objectif

Cette chaîne assure le routage hydrodynamique hors ligne (offline) avec **HyMAP2** des écoulements de surface simulés par le modèle de surface continentale **Noah-MP 4.0.1** sur le domaine Nord Maroc (bassin du Bouregreg, haut Sebou, Ksob) sur la période continue **2016–2020**.

Deux expériences majeures sont routées et comparées aux observations hydrologiques jaugées aux 12 stations de référence :
1. **Open-Loop (OPL)** : simulation en boucle ouverte (`OPL_noirr_2016_2020`).
2. **Assimilation SMAP NoCDF (DA_nocdf)** : assimilation d'humidité du sol satellitaire SMAP sans mise à l'échelle préalable par CDF matching (`DA_nocdf_noirr_2016_2020`).

---

## 2. Provenance et description des paramètres (Étape 01)

Les paramètres physiographiques du réseau hydrographique HyMAP ont été fournis directement par **Augusto Getirana** (NASA GSFC, Hydrological Sciences Laboratory) sous la forme de l'archive compressée `lis_param.tar.gz`.

### 2.1 Grille et format des données
* **Emprise et résolution :** Grille régulière de $180 \times 120$ mailles à la résolution spatiale de **0.05°** ($dx = dy = 0.05^\circ$), couvrant le domaine Nord Maroc de $30.00^\circ\text{N}$ à $36.00^\circ\text{N}$ et de $-10.00^\circ\text{E}$ à $-1.00^\circ\text{E}$ (centres des mailles extrêmes de $30.025^\circ\text{N}$ à $35.975^\circ\text{N}$ et $-9.975^\circ\text{E}$ à $-1.025^\circ\text{E}$).
* **Format binaire et types de données :** Fichiers binaires directs sans en-tête Fortran (*direct access*, encodage *big-endian*, 4 octets par valeur). Deux types de données coexistent :
  - **20 fichiers réels `float32` (IEEE 754) :** 19 grilles 2D ($180 \times 120 \times 4 = 86\,400$ octets) et 1 profil d'inondation 3D à 10 niveaux verticaux (`lis_fldhgt_merged_005.bin`, $10 \times 180 \times 120 \times 4 = 864\,000$ octets).
  - **4 fichiers entiers signés `int32` :** 4 grilles 2D ($180 \times 120 \times 4 = 86\,400$ octets) pour les directions de drainage aval (`lis_nextx_005.bin`, `lis_nexty_005.bin`), l'identifiant de bassin (`lis_basin_005.bin`) et le masque de domaine (`lis_mask_005.bin`).
* **Traçabilité cryptographique SHA-256 :** L'archive source (`data/Hymap_params_from_Augusto/lis_param.tar.gz`) et les 24 fichiers binaires extraits dans `data/Hymap_params_from_Augusto/extracted/lis_param/` ont été contrôlés par hachage SHA-256 et sont consignés dans [`checks/00_checksums_augusto.txt`](checks/00_checksums_augusto.txt).
* **Fichier d'en-tête MERIT :** Le fichier `header` présent dans l'archive (`merit  1   10800    7199  0.000833  -10.000000000   -1.000000000   30.000000000   36.000000000`) atteste d'une source liée à MERIT (résolution native de 3 secondes d'arc $\sim 0.000833^\circ$, domaine $[-10^\circ, -1^\circ]\text{E} \times [30^\circ, 36^\circ]\text{N}$), sans constituer une preuve documentée de la méthode exacte d'agrégation ou de mise à l'échelle (*upscaling*) utilisée pour générer ces cartes 0.05°.

### 2.2 Les cinq familles de paramètres
Les 24 fichiers binaires décrivent l'ensemble des propriétés physiques du réseau d'écoulement :
1. **Topologie et réseau hydrographique :** Directions de drainage vers l'aval (`lis_nextx_005.bin`, `lis_nexty_005.bin`, format `int32`), coordonnées des nœuds fluviaux (`lis_nodelon_005.bin`, `lis_nodelat_005.bin`, `float32`), distance hydraulique entre mailles (`lis_nxtdst_005.bin`, `float32`), superficies drainées amont cumulées (`lis_uparea_005.bin`, `float32`) et identifiants de bassins (`lis_basin_005.bin`, `int32`).
2. **Géométrie du lit mineur :** Largeur de chenal avec estuaires fusionnés (`lis_rivwth_merged_005.bin`, `float32`, préférée dans LDT à la largeur non fusionnée `lis_rivwth_005.bin`), hauteur de berge à pleins bords (`lis_rivhgt_005.bin`, `float32`), longueur réelle méandrée du bief (`lis_rivlen_005.bin`, `float32`), et coefficient de rugosité de Manning du chenal (`lis_rivman_005.bin`, `float32`). La carte de pente (`lis_slope_005.bin`, `float32`) n'est pas ingérée par LDT.
3. **Dynamique des plaines d'inondation :** Profil altimétrique d'inondation sub-maille discrétisé en 10 strates de hauteur (`lis_fldhgt_merged_005.bin`, `float32` 3D) et coefficient de frottement de Manning en plaine majeure (`lis_fldman_005.bin`, `float32`).
4. **Hydrodynamique et temps de transfert :** Temps de concentration du ruissellement superficiel rapide (`lis_getirana_paiva_005.bin`, `float32`, méthode Getirana & Paiva 2013), multiplicateur de ruissellement (`lis_trunoff_005.bin`, `float32`), constante de temps de vidange du réservoir souterrain de nappe (`lis_tbasflw_005.bin`, `float32`), et débit interannuel de référence hydraulique (`lis_qrefer_005.bin`, `float32`). Le fichier `lis_maxlen_005.bin` (`float32`) n'est pas utilisé par LDT.
5. **Masques, maillage et orographie :** Altitude moyenne du relief (`lis_elevtn_005.bin`, `float32`), superficie réelle des cellules (`lis_grarea_005.bin`, `float32`), et masques d'activité continentale (`lis_mask_005.bin` en `int32`, `lis_real_mask_005.bin` en `float32`, ce dernier servant également de bouche-trou technique dans LDT).

### 2.3 Réutilisabilité et précautions d'emploi
Ces paramètres sont spécifiques au domaine Nord Maroc à 0.05° et à la configuration du routeur HyMAP2 sous LISF :
* **Réutilisabilité sous conditions :** Ces jeux de paramètres ne doivent pas être considérés a priori comme universellement validés physiquement ou réutilisables sans vérification. Toute réutilisation pour d'autres simulations requiert de vérifier la stricte compatibilité avec la même grille ($180 \times 120$ à 0.05°), la même version de HyMAP2 / LISF et la configuration du modèle (routage cinématique, désactivation du couplage nappe-inondation DWI).
* **Signalement d'anomalies physiques :** Plusieurs champs présentent des valeurs atypiques qui restent explicitement signalées pour des investigations physiques ultérieures (notamment des superficies de maille `grarea` atteignant 178.9 km², une hauteur de berge `rivhgt` quasi-uniforme de ~0.50 m, des largeurs `rivwth_merged` atteignant ~14.3 km à l'exutoire, et des rugosités de Manning `rivman` uniformes proches de 0.10 s/m$^{1/3}$).
* **Constante de vidange `tbasflw` :**
  - Le code source de LISF attend `tbsflw` en jours (`qbas = basfsto / (tbsflw * 86400.)`).
  - Les unités des valeurs binaires d'origine fournies par Augusto ne sont pas confirmées de façon indépendante.
  - Les simulations de production existantes (Open-Loop et DA-NoCDF) ont utilisé le fichier NetCDF corrigé (`lis_input_corrigee.d01.nc`, division par 86 400).
  - La correction appliquée et ses conséquences hydrologiques (activation du plancher numérique `cntime/86400.` sur 99.9 % des mailles, vidange accélérée du réservoir souterrain) requièrent des vérifications plus approfondies.

*Pour l'inventaire détaillé cellule par cellule, l'audit du code LISF, la cartographie LDT et l'analyse critique de `tbasflw`, consulter la fiche technique :*
👉 [`checks/01_parametres_augusto.md`](checks/01_parametres_augusto.md)

---

## 3. Chaîne de traitement

La chaîne d'exécution comprend 4 étapes séquentielles :

### Étape 3.1 : Génération du fichier de paramètres NetCDF avec LDT
Préparation du maillage et ingestion des 24 grilles binaires HyMAP :
```bash
cd experiments/NorthMor/routing/ldt_hymap
../../../src/lisf/ldt/LDT ldt.config
```
*Sortie générée* : `lis_input.d01.nc` (180x120, contenant les 23 variables `HYMAP_*`).

### Étape 3.2 : Rééchantillonnage conservatif du ruissellement (181x121 → 180x120)
Les sorties de surface Noah-MP (`Qs_tavg` et `Qsb_tavg`) produites sur la grille $181 \times 121$ sont reprojetées de façon rigoureusement conservative en masse vers la grille HyMAP $180 \times 120$ :
```bash
# Pour Open-Loop :
python3 experiments/NorthMor/routing/scripts/remap_opl_2016_2020.py

# Pour DA NoCDF :
python3 experiments/NorthMor/routing/scripts/remap_da_nocdf_2016_2020.py
```
*Répertoires produits* : `experiments/NorthMor/routing/runoff_remap_180x120/{OPL_noirr_2016_2020,DA_nocdf_noirr_2016_2020}/SURFACEMODEL/` (1 828 fichiers journaliers par expérience).

### Étape 3.3 : Spin-up hydrodynamique en 2 cycles (Année 2016)
Initialisation et équilibrage des 4 réservoirs (BSFSTO, RNFSTO, RIVSTO, FLDSTO) par double boucle sur l'année 2016 :
```bash
# Cycle 1 (cold start) :
mpirun -np 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_opl_spinup_c1_corrigee.config

# Cycle 2 (restart depuis fin cycle 1) :
mpirun -np 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_opl_spinup_c2_corrigee.config
```
*Critère de convergence validé* : variation inter-cycles du stock souterrain $\Delta S_{BSF} < 1.0\%$ ($0.13\%$ pour OPL, $0.0645\%$ pour DA).

### Étape 3.4 : Simulation de production continue 5 ans (2016–2020)
Exécution continue à partir du restart équilibré issu du Cycle 2 de spin-up :
```bash
mpirun -np 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_corrigee.config
mpirun -np 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_da_nocdf_2016_2020.config
```

---

## 4. Décisions et écarts documentés

1. **Grilles décalées d'une demi-maille & remap conservatif** :
   - Grille Noah-MP de surface : $30.00^\circ$ à $36.00^\circ\text{N}$, $-10.00^\circ$ à $-1.00^\circ\text{E}$ ($181 \times 121$, repérage aux nœuds).
   - Grille HyMAP : $30.025^\circ$ à $35.975^\circ\text{N}$, $-9.975^\circ$ à $-1.025^\circ\text{E}$ ($180 \times 120$, repérage aux centres).
   - *Décision* : Préservation intégrale du volume ruisselé via un opérateur de remap surfacique pondéré conservatif.
2. **Délai de vidange du débit de base (`tbasflw`) divisé par 86 400 (STATUT : À VÉRIFIER)** :
   - LIS implémente la vidange du réservoir souterrain sous la forme $q_{bas} = S_{bas} / (tbsflw \times 86400)$, attendant `tbsflw` en **jours**.
   - Les cartes brutes `lis_tbasflw_005.bin` d'Augusto Getirana contiennent des valeurs en **secondes** (moyenne ~61 703 s). Ingérées directement, elles induisent un temps de séjour de ~169 ans piégeant 97.5 % du débit souterrain.
   - *Décision* : Création de `lis_input_corrigee.d01.nc` où `HYMAP_baseflow_time_delay` est divisé par 86 400. Le plancher numérique du code `where(tbsflw < cntime/86400.)` s'applique alors dans 99.9 % des mailles, fixant le temps de vidange effectif à `cntime/86400` (médiane 2.45 jours).
3. **Fichiers bouche-trou (placeholders dans `ldt.config`)** :
   - Les cartes `HYMAP river flow type map`, `HYMAP baseflow dwi ratio map` et `HYMAP runoff dwi ratio map` pointent vers `lis_real_mask_005.bin`.
   - La carte `HYMAP runoff bias correction map` pointe vers `lis_basin_005.bin`.
4. **Désactivation des interactions nappe-rivière (`dwi flag = 0`)** :
   - `HYMAP2 routing model dwi flag: 0` dans tous les `lis.config` pour neutraliser les ratios DWI fictifs.

---

## 5. Tableau des runs de routage

| Répertoire de sortie (`routing/output/`) | Fichier lis_input utilisé | Statut | Commentaire technique |
| :--- | :---: | :---: | :--- |
| `OPL_201801/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Test initial 1 mois, paramètre `tbasflw` brut. |
| `OPL_spinup_cycle1/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Spin-up 2016 non corrigé, BSFSTO accumule sans converger. |
| `OPL_spinup_cycle2/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | BSFSTO double entre cycle 1 et 2 (+3 368 hm³). |
| `OPL_2016_2020/ROUTING/` | `lis_input.d01.nc` | **OBSOLÈTE** | Production 5 ans avec puits massif artificiel en nappe. |
| `OPL_spinup_c1_corrigee/ROUTING/` | `lis_input_corrigee.d01.nc` | **VALIDE** | Spin-up cycle 1 OPL corrigé (BSFSTO = 146.4 hm³). |
| `OPL_spinup_c2_corrigee/ROUTING/` | `lis_input_corrigee.d01.nc` | **VALIDE** | Spin-up cycle 2 OPL corrigé (écart 0.13 % < 1.0 %). |
| `OPL_2016_2020_corrigee/ROUTING/` | `lis_input_corrigee.d01.nc` | **VALIDE** | Production 5 ans OPL ($V_{sim}/V_{in} = 100.0\%$, bilan 2018 fermé à 0.035 %). |
| `DA_nocdf_spinup_c1/ROUTING/` | `lis_input_corrigee.d01.nc` | **VALIDE** | Spin-up cycle 1 DA_nocdf (BSFSTO = 146.1 hm³). |
| `DA_nocdf_spinup_c2/ROUTING/` | `lis_input_corrigee.d01.nc` | **VALIDE** | Spin-up cycle 2 DA_nocdf (écart 0.0645 % < 1.0 %). |
| `DA_nocdf_2016_2020/ROUTING/` | `lis_input_corrigee.d01.nc` | **VALIDE** | Production 5 ans DA_nocdf ($V_{sim}/V_{in} = 100.0\%$, bilan 2018 fermé à 0.070 %). |

---

## 6. Journal des vérifications

| Date | Quoi | Résultat | Commit |
| :--- | :--- | :--- | :--- |
| *(journal ouvert — les vérifications futures seront consignées ici)* | | | |

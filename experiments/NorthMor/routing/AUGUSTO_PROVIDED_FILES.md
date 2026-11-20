# Fichiers de Routage HyMAP Fournis par Augusto Getirana (NASA GSFC)

Ce document récapitule l'inventaire exact, la provenance, la discrétisation spatiale, les modifications locales et le statut de partage des fichiers de paramètres de routage hydrodynamique HyMAP transmis par **Augusto Getirana** (NASA Goddard Space Flight Center, Hydrological Sciences Laboratory) pour le domaine Nord-Maroc.

Il est destiné à clarifier auprès de l'équipe et des collaborateurs ce qui est **déjà disponible** dans le projet `NoahMP_Morocco`, comment ces paramètres sont exploités, et ce qu'il reste à valider avant la bascule vers HyMAP-3.

---

## 1. Fichiers Originaux Reçus d'Augusto Getirana

### 1.1 Archive source et intégrité cryptographique
* **Fournisseur :** Augusto Getirana (NASA GSFC).
* **Archive originale :** `data/Hymap_params_from_Augusto/lis_param.tar.gz`
* **Taille :** 971 307 octets (~949 Ko).
* **Empreinte SHA-256 attendue et vérifiée (100% conforme) :**
  ```text
  eb7dc30e3502c133c0c50364fec594c2a2ef372069cdef7813a9b754bcc96cc4  data/Hymap_params_from_Augusto/lis_param.tar.gz
  ```
* **Contrôle d'intégrité :** Fichier de contrôle historique dans [`experiments/NorthMor/routing/checks/00_checksums_augusto.txt`](checks/00_checksums_augusto.txt).

### 1.2 Métadonnées d'origine (Fichier `header`)
L'archive contient un fichier texte `header` horodaté du 13 octobre 2026 (utilisateur `agetiran/s1189`) :
```text
merit  1   10800    7199  0.000833  -10.000000000   -1.000000000   30.000000000   36.000000000
```
Ce fichier atteste que les données de base sont issues de **MERIT-Hydro** à résolution native de 3 secondes d'arc (~0.000833°), agrégées et mises à l'échelle à 0.05° sur le rectangle $[-10.0^\circ, -1.0^\circ]	ext{E} 	imes [30.0^\circ, 36.0^\circ]	ext{N}$.

### 1.3 Liste des 24 fichiers binaires extraits
Les 24 fichiers binaires sont situés sous :  
`data/Hymap_params_from_Augusto/extracted/lis_param/`  
Format binaire : accès direct sans en-tête Fortran (*direct access*, encodage *big-endian*).

| Nom du fichier binaire | Description du paramètre | Dimensions / Type | Taille octets |
| :--- | :--- | :---: | :---: |
| `lis_nextx_005.bin` | Indice colonne (X) de la maille aval (1-indexé) | $180 \times 120$, `int32` | 86 400 |
| `lis_nexty_005.bin` | Indice ligne (Y) de la maille aval (1-indexé) | $180 \times 120$, `int32` | 86 400 |
| `lis_nodelon_005.bin` | Longitude géodésique du noeud fluvial | $180 \times 120$, `float32` | 86 400 |
| `lis_nodelat_005.bin` | Latitude géodésique du noeud fluvial | $180 \times 120$, `float32` | 86 400 |
| `lis_nxtdst_005.bin` | Distance vers la maille aval (m) | $180 \times 120$, `float32` | 86 400 |
| `lis_uparea_005.bin` | Aire drainée amont cumulée (m²) | $180 \times 120$, `float32` | 86 400 |
| `lis_basin_005.bin` | Identifiant du bassin versant | $180 \times 120$, `int32` | 86 400 |
| `lis_rivwth_merged_005.bin` | Largeur du chenal avec estuaires (m) | $180 \times 120$, `float32` | 86 400 |
| `lis_rivwth_005.bin` | Largeur du chenal sans estuaires (m) | $180 \times 120$, `float32` | 86 400 |
| `lis_rivhgt_005.bin` | Hauteur de berge / profondeur lit mineur (m) | $180 \times 120$, `float32` | 86 400 |
| `lis_rivlen_005.bin` | Longueur du bief fluvial dans la maille (m) | $180 \times 120$, `float32` | 86 400 |
| `lis_rivman_005.bin` | Rugosité de Manning du lit mineur ($s \cdot m^{-1/3}$) | $180 \times 120$, `float32` | 86 400 |
| `lis_fldhgt_merged_005.bin` | Profil altimétrique d'inondation (10 niveaux) | $10 \times 180 \times 120$, `float32` | 864 000 |
| `lis_fldman_005.bin` | Rugosité de Manning du lit majeur ($s \cdot m^{-1/3}$) | $180 \times 120$, `float32` | 86 400 |
| `lis_getirana_paiva_005.bin` | Temps de concentration du ruissellement rapide (s) | $180 \times 120$, `float32` | 86 400 |
| `lis_trunoff_005.bin` | Facteur d'échelle du temps de ruissellement (1.0) | $180 \times 120$, `float32` | 86 400 |
| `lis_tbasflw_005.bin` | Constante de vidange de l'écoulement de base | $180 \times 120$, `float32` | 86 400 |
| `lis_qrefer_005.bin` | Débit moyen de référence hydraulique (m³/s) | $180 \times 120$, `float32` | 86 400 |
| `lis_elevtn_005.bin` | Altitude moyenne du MNT (m a.s.l.) | $180 \times 120$, `float32` | 86 400 |
| `lis_grarea_005.bin` | Aire de la maille HyMAP (m²) | $180 \times 120$, `float32` | 86 400 |
| `lis_mask_005.bin` | Masque de terre / activité (1 / 0 / -9999) | $180 \times 120$, `int32` | 86 400 |
| `lis_real_mask_005.bin` | Version réelle flottante du masque (1.0 / 0.0) | $180 \times 120$, `float32` | 86 400 |
| `lis_maxlen_005.bin` | Longueur de transfert maximale sub-maille (m) | $180 \times 120$, `float32` | 86 400 |
| `lis_slope_005.bin` | Pente topographique fluviale (m/m) | $180 \times 120$, `float32` | 86 400 |

*Taille totale des 24 fichiers extraits : ~2.85 Mo.*

### 1.4 Statut du « mémo technique HyMAP-3 »
Après recherche exhaustive sur le HPC et dans l'historique du projet, **aucun document PDF ou traitement de texte externe intitulé « mémo technique HyMAP-3 » n'a été déposé sous forme de fichier autonome**.  
Les recommandations techniques d'Augusto Getirana ont été communiquées directement par échanges de courriels et synthétisées localement dans le document de référence :  
[`experiments/NorthMor/routing/checks/07_transition_hymap3_linres0.md`](checks/07_transition_hymap3_linres0.md)  
Points clés des recommandations d'Augusto :
1. Basculer vers HyMAP-3 pour devancer la dépréciation de HyMAP-2.
2. Désactiver le réservoir linéaire (`linear reservoir flag: 0`) pour les couplages avec un modèle physique distributed comme Noah-MP.
3. Attribuer le biais d'étiage estival à la sur-génération de drainage profond par Noah-MP et non au routage.

---

## 2. Grille de Routage HyMAP-2 vs Grille Surface Noah-MP

> [!WARNING]
> **Attention :** La grille de surface Noah-MP et la grille de routage HyMAP n'ont pas les mêmes dimensions. Elles ne doivent jamais être confondues.

### 2.1 Grille de routage HyMAP-2 (fournie par Augusto)
Vérifiée directement dans les métadonnées de `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` :
* **Dimensions :** $180 	ext{ colonnes} (lon) 	imes 120 	ext{ lignes} (lat)$
* **Résolution spatiale :** $dx = 0.05^\circ$, $dy = 0.05^\circ$
* **Projection :** Cylindrique équidistante (`latlon`)
* **Centres des cellules extrêmes :**
  - Coin Sud-Ouest (min lat, min lon) : $30.025^\circ	ext{N}, -9.975^\circ	ext{E}$
  - Coin Nord-Est (max lat, max lon) : $35.975^\circ	ext{N}, -1.025^\circ	ext{E}$
* **Bords externes du domaine :**
  - Latitude : $[30.00^\circ	ext{N}, 36.00^\circ	ext{N}]$
  - Longitude : $[-10.00^\circ	ext{E}, -1.00^\circ	ext{E}]$

### 2.2 Grille de surface Noah-MP (`data/lis_input/lis_input_NorthMor_5km.nc`)
* **Dimensions :** $181 	ext{ colonnes} (east\_west) 	imes 121 	ext{ lignes} (north\_south)$
* **Résolution :** $0.05^\circ$
* **Discrétisation :** Grille enregistrée sur les noeuds/coins entiers de $30.00^\circ	ext{N}$ à $36.00^\circ	ext{N}$ et $-10.00^\circ	ext{E}$ à $-1.00^\circ	ext{E}$.

### 2.3 Conséquence sur le couplage
Les flux de ruissellement Noah-MP ($181 	imes 121$) ne peuvent pas être injectés directement dans HyMAP ($180 	imes 120$). Un remapping spatial conservatif est obligatoirement appliqué par le sous-système :  
[`experiments/NorthMor/routing/runoff_remap_180x120/`](runoff_remap_180x120/)  
Scripts de remapping vérifiés : `experiments/NorthMor/routing/scripts/remap_runoff_*.py`.

---

## 3. Modifications Effectuées Localement et Fichiers Dérivés

### 3.1 Prétraitement LDT (`ldt.config`)
Le script de prétraitement LDT 7.5 associe 20 fichiers d'Augusto aux variables LISF. Quatre cartes attendues par LDT n'étaient pas fournies dans l'archive et ont été définies via des *placeholders* :
```text
HYMAP river flow type map:               ./lis_real_mask_005.bin   # Placeholder
HYMAP baseflow dwi ratio map:            ./lis_real_mask_005.bin   # Placeholder
HYMAP runoff dwi ratio map:              ./lis_real_mask_005.bin   # Placeholder
HYMAP runoff bias correction map:        ./lis_basin_005.bin       # Placeholder
```
*Vérification dans le code source LISF 7.5 :* Ces quatre variables sont **inactives et non lues** en mode cinématique unidirectionnel (`flowtype = 1`, `dwiflag = 0`). Elles n'introduisent aucun biais.

### 3.2 Fichiers NetCDF générés par LDT
1. `experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc` (~2.5 Mo) :  
   Sortie brute directe de LDT. Contient les valeurs brutes de `tbasflw`. Dans LISF (`qbas = basfsto / (tbsflw * 86400.)`), cela provoquait des constantes de vidange centennales et une accumulation infinie d'eau souterraine.
2. `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` (~2.5 Mo) :  
   Fichier opérationnel de production. La variable `HYMAP_baseflow_time_delay` a été divisée par 86 400 (`tbasflw / 86400`) pour rétablir une vidange en jours. C'est le fichier de paramètres utilisé pour toutes les simulations corrigées 2016–2020.

### 3.3 Configurations de routage historiques vs actualisées
* **Historiques HyMAP-2 (`linres=1`) :**
  - `experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_corrigee.config`
  - Utilise `lis_input_corrigee.d01.nc` avec réservoir linéaire actif et spin-up de nappe en 2 cycles (C1/C2).
* **Actualisées HyMAP-2 (`linres=0`) :**
  - `experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_linres0.config`
  - Désactive le réservoir linéaire, annulant la sensibilité à `tbasflw`.
* **Configurations prêtes pour HyMAP-3 :**
  - `experiments/NorthMor/routing/configs/lis_hymap3_opl_2016_2020.config` (et variantes DA-NoCDF, DA-CDF).

---

## 4. Préparation pour HyMAP-3 : Fichiers Utilisables et Informations Manquantes

### 4.1 Fichiers utilisables immédiatement pour HyMAP-3
* Le fichier de paramètres `lis_input_corrigee.d01.nc` est **pleinement compatible** avec le routeur `HYMAP3` de LISF.
* En mode `linres = 0`, le routeur HyMAP-3 additionne directement ruissellement et baseflow (`runoff0 + basflw0`) dans le bief fluvial, éliminant tout besoin de recalculer `tbasflw`.
* Les 6 fichiers de configuration `lis_hymap3_*.config` et scripts SLURM sous `jobs/` sont déjà préparés et testés sur 1 pas de temps.

### 4.2 Informations encore manquantes auprès d'Augusto
1. **Grille native HyMAP-3 :** Augusto prévoit-il de fournir un nouveau jeu de paramètres spécifiques à HyMAP-3 (ex. nouvelle version de MERIT-Hydro v2, lit majeur réétalonné, nouvelle discrétisation) ou confirme-t-il l'utilisation de la grille 180 × 120 existante ?
2. **Autorisation formelle de redistribution :** Préciser la licence et le droit de partage public des 24 fichiers binaires `lis_*_005.bin` sur un dépôt GitHub public.

---

## 5. Inventaire et Statut de Partage GitHub

Conformément à la politique de partage :
- Les documentations, scripts et configurations créés localement sont suivis dans Git.
- Les fichiers binaires originaux d'Augusto et les NetCDF volumineux restent sous `.gitignore` et sont partagés en privé sur le HPC avec le collègue.

| Fichier | Origine | Dimensions / Taille | Original ou Dérivé | Déjà suivi Git | Statut de partage | Action proposée |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `data/Hymap_params_from_Augusto/lis_param.tar.gz` | Augusto Getirana (NASA) | 949 Ko | Original | Non (`.gitignore`) | Privé interne | Garder sous `.gitignore` ; partage HPC interne |
| `data/Hymap_params_from_Augusto/extracted/lis_param/lis_*_005.bin` (24 fichiers) | Augusto Getirana (NASA) | $180 \times 120$, 2.85 Mo | Original | Non (`.gitignore`) | Privé interne | Garder sous `.gitignore` ; documenter dans Git |
| `experiments/NorthMor/routing/checks/00_checksums_augusto.txt` | Équipe locale | 3.4 Ko (25 SHA-256) | Dérivé | **Oui** | Public | Maintenir dans Git pour contrôle d'intégrité |
| `experiments/NorthMor/routing/checks/01_parametres_augusto.md` | Équipe locale | 18 Ko | Dérivé | **Oui** | Public | Maintenir dans Git comme audit de référence |
| `experiments/NorthMor/routing/checks/07_transition_hymap3_linres0.md` | Équipe locale | 4.5 Ko | Dérivé | **Oui** | Partageable équipe | Maintenir dans Git (synthèse recommandations Augusto) |
| `experiments/NorthMor/routing/ldt_hymap/ldt.config` | Équipe locale | 3.8 Ko | Dérivé | **Oui** | Public | Maintenir dans Git (reproductibilité LDT) |
| `experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc` | LDT local brut | $180 \times 120$, 2.5 Mo | Dérivé | Non (`.gitignore`) | Interne | Conserver localement sur HPC |
| `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` | LDT local corrigé | $180 \times 120$, 2.5 Mo | Dérivé | Non (`.gitignore`) | Privé collègue | Conserver sur HPC ; partage par chemin local |
| `experiments/NorthMor/routing/configs/lis_hymap2_*.config` | Équipe locale | ~3.5 Ko chacun | Dérivé | **Oui** | Public | Maintenir dans Git |
| `experiments/NorthMor/routing/configs/lis_hymap3_*.config` (6 fichiers) | Équipe locale | ~3.5 Ko chacun | Dérivé | **Oui** | Public | Maintenir dans Git pour transition HyMAP-3 |
| `experiments/NorthMor/routing/scripts/remap_runoff_*.py` | Équipe locale | ~8 Ko chacun | Dérivé | **Oui** | Public | Maintenir dans Git (remapping 181x121 -> 180x120) |
| `experiments/NorthMor/routing/AUGUSTO_PROVIDED_FILES.md` | Équipe locale | ~12 Ko | Dérivé | À ajouter | Public | Ajouter au suivi Git pour partage avec le collègue |

---

## 6. Commandes de Vérification et de Consultation Rapide

### 6.1 Vérifier l'intégrité des 24 paramètres originaux et de l'archive
```bash
sha256sum -c experiments/NorthMor/routing/checks/00_checksums_augusto.txt
```
*Toutes les lignes doivent afficher `OK`.*

### 6.2 Inspecter les dimensions et variables du fichier LDT HyMAP opérationnel
```bash
python3 -c "
import netCDF4 as nc
ds = nc.Dataset('experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc')
print('Dimensions:', {d: len(ds.dimensions[d]) for d in ds.dimensions})
print('Variables HyMAP:', [v for v in ds.variables if 'HYMAP' in v])
print('Lat bounds:', float(ds.variables['lat'][:].min()), float(ds.variables['lat'][:].max()))
print('Lon bounds:', float(ds.variables['lon'][:].min()), float(ds.variables['lon'][:].max()))
ds.close()
"
```

### 6.3 Localisation des fichiers sur le cluster HPC pour le collègue
* **Archive originale :**
  `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/Hymap_params_from_Augusto/lis_param.tar.gz`
* **Paramètres binaires extraits :**
  `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/Hymap_params_from_Augusto/extracted/lis_param/`
* **Fichier LDT opérationnel corrigé :**
  `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc`

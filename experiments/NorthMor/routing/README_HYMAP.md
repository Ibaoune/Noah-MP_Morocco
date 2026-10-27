# Documentation de reproduction du routage HyMAP2 (Nord Maroc 2016–2020)

## 1. Objectif

Cette chaîne assure le routage hydrodynamique hors ligne (offline) avec **HyMAP2** des écoulements de surface simulés par le modèle de surface continentale **Noah-MP 4.0.1** sur le domaine Nord Maroc (bassin du Bouregreg, haut Sebou, Ksob) sur la période continue **2016–2020**.

Deux expériences majeures sont routées et comparées aux observations hydrologiques jaugées aux 12 stations de référence :
1. **Open-Loop (OPL)** : simulation en boucle ouverte (`OPL_noirr_2016_2020`).
2. **Assimilation SMAP NoCDF (DA_nocdf)** : assimilation d'humidité du sol satellitaire SMAP sans mise à l'échelle préalable par CDF matching (`DA_nocdf_noirr_2016_2020`).

---

## 2. Provenance des paramètres

Les paramètres physiographiques du réseau hydrographique HyMAP à la résolution spatiale de **0.05°** (grille $180 \times 120$) ont été fournis directement par **Augusto Getirana** (NASA GSFC) sous forme de l'archive compressée `lis_param.tar.gz`.

- Répertoire source des fichiers binaires : `data/Hymap_params_from_Augusto/extracted/lis_param/`
- Nombre de fichiers binaires 0.05° : 24 fichiers `lis_*_005.bin` (taille unitaire de 86 400 octets pour les grilles 2D, soit $180 \times 120 \times 4$ octets float32).
- Intégrité et traçabilité : Les empreintes cryptographiques SHA-256 de l'archive et des 24 fichiers binaires sont consignées dans `checks/00_checksums_augusto.txt`.

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

# Guide de Référence Technique du Routage HyMAP2 pour Noah-MP (Nord Maroc 2016–2020)
### Manuel Opérationnel, Analyse Critique et Questions Scientifiques

**Auteur :** Équipe de modélisation hydrologique (Projet NoahMP_Morocco)  
**Date :** Novembre 2026  
**Version :** 2.1 (Revue technique ciblée et validation des formulations physiques)  
**Statut :** Document technique de référence et base de discussion scientifique  
**Dépôt de référence :** `experiments/NorthMor/routing/`  

---

## Table des Matières

1. [Objectif Scientifique et Architecture du Couplage](#1-objectif-scientifique-et-architecture-du-couplage)
2. [Environnement d'Exécution et Prérequis Techniques](#2-environnement-dexécution-et-prérequis-techniques)
3. [Préparation des Paramètres Hydrographiques sous LDT](#3-préparation-des-paramètres-hydrographiques-sous-ldt)
4. [Préparation et Remapping des Ruissellements Noah-MP](#4-préparation-et-remapping-des-ruissellements-noah-mp)
5. [Compilation et Configuration Opérationnelle de LIS / HyMAP2](#5-compilation-et-configuration-opérationnelle-de-lis--hymap2)
6. [Protocole d'Initialisation et Convergence du Spin-up](#6-protocole-dinitialisation-et-convergence-du-spin-up)
7. [Exécution et Contrôle des Simulations Quinquennales (2016–2020)](#7-exécution-et-contrôle-des-simulations-quinquennales-20162020)
8. [Extraction Spatiale des Débits et Référentiel des Stations](#8-extraction-spatiale-des-débits-et-référentiel-des-stations)
9. [Évaluation et Validation Hydrologique aux Stations ABH](#9-évaluation-et-validation-hydrologique-aux-stations-abh)
10. [Assumptions, Known Limitations and Unresolved Technical Questions](#10-assumptions-known-limitations-and-unresolved-technical-questions)
11. [How to Route a New Noah-MP Simulation with HyMAP2](#11-how-to-route-a-new-noah-mp-simulation-with-hymap2)
12. [Annexe : Technical Questions for Augusto Getirana (NASA GSFC)](#12-annexe--technical-questions-for-augusto-getirana-nasa-gsfc)

---

## 1. Objectif Scientifique et Architecture du Couplage

### 1.1 Contexte et Enjeux de la Modélisation Hydrologique au Maroc
La gestion quantitative des ressources en eau dans les bassins méditerranéens semi-arides du Nord du Maroc (bassins versants du Sebou et du Bouregreg) est confrontée à une variabilité spatio-temporelle extrême des précipitations. Ces régimes hydrologiques se caractérisent par des crues éclair violentes et soudaines en saison humide et des assecs sévères et prolongés pendant l'étiage estival.

Dans le cadre du projet **NoahMP_Morocco**, le modèle de surface continentale **Noah-MP 4.0.1** simule les transferts d'eau et d'énergie au sein d'une colonne de sol 1D discrétisée verticalement en 4 couches (0–10 cm, 10–40 cm, 40–100 cm et 100–200 cm). Si Noah-MP calcule la partition de la précipitation entre évapotranspiration, infiltration, humidité du sol, ruissellement superficiel et drainage profond sous la zone racinaire, **il est structurellement dépourvu de dimension horizontale**. Chaque maille de calcul fonctionne comme une colonne indépendante sans connectivité latérale vers les mailles adjacentes ou vers un réseau hydrographique.

Pour transformer ces flux verticaux en débits de rivière observables aux stations hydrométriques, il est indispensable de coupler Noah-MP au modèle hydrodynamique distribué **HyMAP2** (*Hydrological Modeling and Analysis Platform, version 2*), intégré au sein de l'infrastructure logicielle **LISF 7.3** (*Land Information System Framework*) de la NASA.

```
+-----------------------------------------------------------------------------------+
|                            ARCHITECTURE DU COUPLAGE                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Forçages Météorologiques ]                                                     |
|         |                                                                         |
|         v                                                                         |
|  +--------------------+                                                           |
|  |    Noah-MP 4.0.1   |  -> Simulation 1D des bilans verticaux (colonne de sol)    |
|  +--------------------+                                                           |
|         |                                                                         |
|         |  Flux journaliers (grille régulière 181 x 121 sommets, Plate Carrée)     |
|         |  - Qs_tavg  (Ruissellement de surface rapide, kg m-2 s-1)               |
|         |  - Qsb_tavg (Drainage sous-racinaire profond, kg m-2 s-1)               |
|         v                                                                         |
|  +--------------------+                                                           |
|  |  Remapping 4-nœuds |  -> Moyenne arithmétique aux 4 sommets                     |
|  | (Scripts Python)   |     Grille 181x121 sommets -> Grille 180x120 centres       |
|  |                    |     (Conservation globale contrôlée empiriquement)        |
|  +--------------------+                                                           |
|         |                                                                         |
|         |  Flux d'entrée rééchantillonnés (180 x 120 mailles)                     |
|         v                                                                         |
|  +--------------------+     +--------------------------------------------------+  |
|  |   LISF / HyMAP2    | <-- | Paramètres physiographiques LDT                  |  |
|  | (Moteur de routage)|     | (lis_input_corrigee.d01.nc : 180 x 120 mailles,  |  |
|  |                    |     |  topologie, pentes, tbasflw corrigé, grarea)     |  |
|  +--------------------+     +--------------------------------------------------+  |
|         |                                                                         |
|         |  Résolution hydrodynamique :                                            |
|         |  - Onde cinématique en lit mineur                                       |
|         |  - Réservoir linéaire de nappe alluviale (BSFSTO)                       |
|         |  - Stockage temporaire en plaine d'inondation (FLODSTO)                 |
|         v                                                                         |
|  +--------------------+                                                           |
|  | Sorties NetCDF     |  -> Streamflow_tavg (Débit fluvial instantané/moyen, m3/s)|
|  | (180 x 120 mailles)|     BSFSTO_tavg (Stock souterrain, mm)                    |
|  +--------------------+                                                           |
|         |                                                                         |
|         v                                                                         |
|  +--------------------+                                                           |
|  | Post-traitement    |  -> extract_streamflow.py (extraction aux 12 stations)    |
|  | et Validation      |     evaluate_sebou_bouregreg.py (KGE, NSE, PBIAS vs ABH)  |
|  +--------------------+                                                           |
+-----------------------------------------------------------------------------------+
```

### 1.2 Rôle Respectif des Composantes : Noah-MP, LDT, LIS et HyMAP2
1. **Noah-MP 4.0.1 (Land Surface Model) :** Modélise la physique du sol et de la végétation. Il produit au pas de temps journalier les flux surfaciques d'eau quittant la colonne : le ruissellement superficiel rapide $Q_s$ et le drainage profond sous la 4ᵉ couche de sol $Q_{sb}$.
2. **LDT 7.3 (Land Data Toolkit) :** Outil de prétraitement géospatial de la NASA. Il projette, découpe et assemble l'ensemble des données géographiques, topographiques et hydrodynamiques (issues de MERIT-Hydro et des bases globales) pour générer le fichier de paramètres statiques `lis_input_corrigee.d01.nc`.
3. **LISF 7.3 (Land Information System Framework) :** Environnement d'exécution haute performance orchestrant la lecture des forçages, l'allocation mémoire, l'intégration temporelle et l'écriture des fichiers historiques et de reprise (*restarts*).
4. **HyMAP2 (Hydrodynamic Model) :** Sous-modèle de routage distribué intégré dans LISF. Il ingère les flux de ruissellement, convertit les flux surfaciques en débits volumiques à l'aide de l'aire de maille `grarea`, résout la propagation de l'onde cinématique dans le réseau hydrographique, simule la dynamique de rétention dans un réservoir souterrain linéaire et dans les plaines inondables, et calcule le débit fluvial sortant $Streamflow\_tavg$ en chaque cellule.

### 1.3 Variables Hydrologiques Clés, Conventions et Unités Vérifiées

| Variable | Nom dans les fichiers NetCDF | Unité standard | Définition physique et rôle dans la chaîne |
| :--- | :--- | :---: | :--- |
| **Ruissellement de surface** | `Qs_tavg` | $	ext{kg}\cdot	ext{m}^{-2}\cdot	ext{s}^{-1}$ ($\equiv 	ext{mm}\cdot	ext{s}^{-1}$) | Flux d'eau moyen journalier ne s'infiltrant pas et s'écoulant rapidement sur le versant. |
| **Drainage sous-racinaire** | `Qsb_tavg` | $	ext{kg}\cdot	ext{m}^{-2}\cdot	ext{s}^{-1}$ ($\equiv 	ext{mm}\cdot	ext{s}^{-1}$) | Flux d'eau moyen journalier drainé sous la 4ᵉ couche de sol Noah-MP (2.0 m). Alimente la nappe HyMAP2. |
| **Débit fluvial routé** | `Streamflow_tavg` | $	ext{m}^3\cdot	ext{s}^{-1}$ | Débit volumique moyen journalier s'écoulant dans le lit fluvial au point de sortie de la cellule. |
| **Stock en nappe alluviale** | `BSFSTO_tavg` | $	ext{mm}$ (ou $	ext{m}^3$) | Hauteur d'eau équivalente stockée temporairement dans le compartiment souterrain sub-maille. |
| **Stock en lit fluvial** | `RIVSTO_tavg` | $	ext{mm}$ (ou $	ext{m}^3$) | Volume d'eau transitant instantanément dans le chenal fluvial principal de la maille. |
| **Stock en plaine inondable** | `FLODSTO_tavg` | $	ext{mm}$ (ou $	ext{m}^3$) | Volume d'eau stocké temporairement dans la plaine d'inondation lors des débordements de crue. |

### 1.4 Domaine Géographique et Référentiel des Grilles
Le domaine d'étude couvre le **Nord Maroc**, de $30^\circ	ext{N}$ à $36^\circ	ext{N}$ et de $-10^\circ	ext{E}$ à $-1^\circ	ext{E}$ :

| Propriété | Grille Source Noah-MP | Grille Destination HyMAP2 / LDT |
| :--- | :---: | :---: |
| **Dimensions ($N_x 	imes N_y$)** | $181 	imes 121$ points ($21\,901$ nœuds) | $180 	imes 120$ cellules ($21\,600$ mailles) |
| **Projection cartographique** | Cylindrique équidistante (Plate Carrée / `latlon`) | Cylindrique équidistante (Plate Carrée / `latlon`) |
| **Résolution spatiale ($\Delta\lambda, \Delta\phi$)** | $0.05^\circ 	imes 0.05^\circ$ ($pprox 5	ext{ km}$) | $0.05^\circ 	imes 0.05^\circ$ ($pprox 5	ext{ km}$) |
| **Origine Sud-Ouest (Coordonnées du coin)** | Lat: $30.00^\circ	ext{N}$, Lon: $-10.00^\circ	ext{E}$ | Lat: $30.00^\circ	ext{N}$, Lon: $-10.00^\circ	ext{E}$ (Bord externe) |
| **Coordonnées effectives stockées** | $30.00, 30.05, \dots, 36.00^\circ	ext{N}$ ($121$ valeurs)<br>$-10.00, -9.95, \dots, -1.00^\circ	ext{E}$ ($181$ valeurs) | $30.025, 30.075, \dots, 35.975^\circ	ext{N}$ ($120$ valeurs)<br>$-9.975, -9.925, \dots, -1.025^\circ	ext{E}$ ($180$ valeurs) |
| **Positionnement spatial** | **Nœuds / Sommets de mailles** | **Centres géométriques des mailles** |
| **Nombre de mailles actives de bassin** | $21\,901$ (Totalité de la boîte) | **$15\,937$ cellules actives** (`HYMAP_basin_mask == 1.0`) |

### 1.5 Tableau Synthétique du Chaînage et des Grilles

| Étape de la chaîne | Grille source | Projection / Coordonnées | Grille destination | Script ou fichier clé | Contrôle et vérification |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **1. Simulation de surface** | Colonne 1D sol | Nœuds réguliers $0.05^\circ$ ($181 	imes 121$) | NetCDF Noah-MP brut | `run_NoahMP_*` | Dimensions NetCDF `(121, 181)`, unités `kg m-2 s-1`. |
| **2. Rééchantillonnage 4-nœuds** | $181 	imes 121$ (sommets) | Plate Carrée régulier ($30.0^\circ-36.0^\circ	ext{N}$) | $180 	imes 120$ (centres) | `scripts/remap_runoff_*.py` | Conservation globale contrôlée empiriquement ($S_2/S_1 pprox 100.0002\%$). |
| **3. Paramétrage hydrographique** | MERIT-Hydro 3" | Plate Carrée ($10\,800 	imes 7\,199$) | $180 	imes 120$ régulière ($0.05^\circ$) | `ldt_hymap/lis_input_corrigee.d01.nc` | Correction `tbasflw / 86400`, analyse `grarea`, 15 937 mailles actives. |
| **4. Routage fluvial** | $180 	imes 120$ (ruissellement) | Plate Carrée ($0.05^\circ$) | $180 	imes 120$ (débit chenal) | `configs/lis_hymap2_*.config` | Fermeture bilan de masse $pprox 99.965\%$, 1 827 sorties journalières. |
| **5. Extraction aux stations** | $180 	imes 120$ (débits) | Grille spatiale 2D ($180 	imes 120$) | Séries temporelles 1D (12 stations) | `scripts/extract_streamflow.py` | Concordance coordonnées ABH $\leftrightarrow$ cellules HyMAP. |
| **6. Évaluation hydrologique** | Débits extraits | Séries journalières et mensuelles | Indicateurs KGE, NSE, PBIAS | `scripts/evaluate_sebou_bouregreg.py` | Comparaison aux séries d'observations ABH disponibles. |

## 2. Environnement d'Exécution et Prérequis Techniques

### 2.1 Environnement HPC Toubkal
L'ensemble des simulations, remappings et post-traitements est déployé sur le supercalculateur **Toubkal** (CNRST / UM6P).
- **Architecture de calcul :** Nœuds biprocesseurs Intel Xeon Gold 6248 (20 cœurs par socket, 2.50 GHz, soit 40 cœurs physiques par nœud), 192 Go de mémoire RAM DDR4 par nœud, interconnexion réseau InfiniBand HDR 100 Gb/s.
- **Système d'exploitation :** Linux CentOS / Rocky Linux 8.x (x86_64).
- **Gestionnaire de travaux :** SLURM (*Simple Linux Utility for Resource Management*).

### 2.2 Compilateurs, Bibliothèques et Environnement Logiciel
- **Compilateurs :** Intel Compiler Classic Suite (`icc`, `ifort` version 2021.4.0) ou GCC/Gfortran (>= 9.3.0).
- **Bibliothèque MPI :** Intel MPI (`mpiifort`) ou OpenMPI (>= 4.0).
- **Bibliothèques scientifiques :** NetCDF-C (>= 4.7.4), NetCDF-Fortran (>= 4.5.3), HDF5 (>= 1.10.6), ESMF (Earth System Modeling Framework >= 8.0.1).
- **Environnement Python :** Python 3.8+ (avec `numpy`, `pandas`, `scipy`, `netCDF4`, `matplotlib`).
- **Outils de conversion documentaire :** `pandoc` (>= 2.11) et `weasyprint` (>= 61.2) pour la compilation du manuel en PDF.

### 2.3 Provenance du Code Source LISF / HyMAP2
Le moteur de routage exécuté est issu de la branche officielle **NASA LISF 7.3** (mode routage autonome).
Le code source complet est intégré dans l'arborescence du projet sous `src/lisf/`.
- Script de compilation validé : [`jobs/build_lis_hymap2.sh`](../jobs/build_lis_hymap2.sh).
- Binaire exécutable produit : `LIS` (ELF 64-bit LSB executable, x86-64, dynamically linked).

### 2.4 Organisation Arborescente Minimale du Projet
```text
routing/
├── configs/            # Fichiers de configuration LIS (lis_hymap2_*.config) pour spin-up et production
├── jobs/               # Scripts de soumission SLURM (run_hymap2_*.sh) et build_lis_hymap2.sh
├── ldt_hymap/          # Grilles LDT de paramètres statiques (lis_input_corrigee.d01.nc)
├── runoff_remap_180x120/ # Entrées de forçage : ruissellements Noah-MP rééchantillonnés aux mailles 180x120
├── output/             # Sorties brutes de routage NetCDF (ROUTING/) et restarts (restarts/)
├── stations/           # Référentiel des stations de jaugeage (hymap_stations_pairing.csv)
├── scripts/            # Scripts Python pour le remapping, l'extraction et l'évaluation
├── plots/              # Figures et tableaux scientifiques de synthèse (sebou_bouregreg/)
├── checks/             # Fiches techniques d'audit, de traçabilité cryptographique et de cohérence
├── docs/               # Documentation de référence (HYMAP2_ROUTING_GUIDE.md et .pdf)
└── README_HYMAP.md     # Vue d'ensemble générale du projet
```

### 2.5 Inventaire des Fichiers Indispensables : Générique vs Spécifique

| Catégorie | Fichier / Répertoire | Rôle et statut | Réutilisable pour nouvelle simulation ? |
| :--- | :--- | :--- | :---: |
| **Paramètres LDT** | `ldt_hymap/lis_input_corrigee.d01.nc` | Grille statique des paramètres hydrographiques corrigés ($180 	imes 120$). | **Oui** (Strictement réutilisable si le domaine reste Nord Maroc). |
| **Table de sortie** | `tables/MODEL_OUTPUT_LIST_routing.TBL` | Spécifie les variables NetCDF écrites par HyMAP2 (`Streamflow`, `BSFSTO`, etc.). | **Oui** (Générique et indépendant de l'expérience). |
| **Appariement** | `stations/hymap_stations_pairing.csv` | Table de correspondance coordonnées ABH $\leftrightarrow$ indices grille HyMAP. | **Oui** (Pour toute évaluation sur Sebou / Bouregreg). |
| **Binaire LIS** | `LIS` | Exécutable compilé du modèle de routage. | **Oui** (Binaire mutualisé). |
| **Forçage ruissellement** | `runoff_remap_180x120/<EXP>/` | NetCDF journaliers des flux $Q_s$ et $Q_{sb}$ rééchantillonnés aux mailles $180 	imes 120$. | **Non** (Spécifique à chaque expérience Noah-MP). |
| **Configuration LIS** | `configs/lis_hymap2_<EXP>.config` | Paramétrage des dates, chemins d'entrée, sorties et restarts. | **Non** (À copier et adapter selon l'expérience). |
| **Jobs SLURM** | `jobs/run_hymap2_<EXP>.sh` | Script batch d'allocation des cœurs et lancement MPI. | **Non** (À copier et adapter selon l'expérience). |

---

## 3. Préparation des Paramètres Hydrographiques sous LDT

### 3.1 Grille LDT et Données Physiographiques d'Origine (Archive Augusto Getirana)
Les paramètres hydrographiques de base ont été préparés et fournis par Augusto Getirana (NASA Goddard Space Flight Center) sous forme d'une archive compressée :
- **Archive source :** `data/Hymap_params_from_Augusto/lis_param.tar.gz` (971 307 octets).
- **Empreinte SHA-256 :** `eb7dc30e3502c133c0c50364fec594c2a2ef372069cdef7813a9b754bcc96cc4` (contrôle conforme dans `checks/00_checksums_augusto.txt`).
- **Métadonnées natives (`header`) :** Fichier d'en-tête horodaté du 13/10/2026 à 21:05 (`agetiran/s1189`), indiquant une extraction issue de la base topographique globale **MERIT-Hydro** à 3 secondes d'arc ($pprox 0.000833^\circ$, grille source $10\,800 	imes 7\,199$ points sur $[-10^\circ, -1^\circ]	ext{E} 	imes [30^\circ, 36^\circ]	ext{N}$).
- **Grille cible LDT :** 180 colonnes $	imes$ 120 lignes ($21\,600$ mailles 2D), résolution angulaire $\Delta\lambda = \Delta\phi = 0.05^\circ$ en projection cylindrique équidistante (Plate Carrée).

L'archive contient 24 fichiers binaires bruts direct access big-endian :
- Hydraulique et géométrie du chenal : longueur (`lis_rivlen_005.bin`), largeur (`lis_rivwth_005.bin`), profondeur (`lis_rivhgt_005.bin`), pente (`lis_rivslp_005.bin`) et rugosité de Manning (`lis_rivman_005.bin`).
- Plaine d'inondation : rugosité (`lis_fldman_005.bin`) et profils 3D de hauteur (`lis_fldhgt_merged_005.bin`).
- Topologie de drainage : directions d'écoulement vers les 8 voisins (`lis_nextx_005.bin`, `lis_nexty_005.bin`), distance à l'exutoire (`lis_dist2mouth_005.bin`) et surfaces amont (`lis_uparea_005.bin`).
- Paramètre temporel de vidange du débit de base souterrain : `lis_tbasflw_005.bin`.
- Surface de grille : `lis_grarea_005.bin`.

### 3.2 Formulations Fortran : tbasflw, cntime et Plancher Temporel
Dans le code source Fortran de LISF 7.3 (`src/lisf/lis/routing/HYMAP2_router/HYMAP2_modelMod.F90`, lignes 107–118), le débit de vidange du réservoir de nappe alluviale est calculé par :

```fortran
qbas = basfsto / (tbsflw * 86400.)
vbflw = basfsto - qbas * dt
if (vbflw < 0.) then
   qbas = basfsto / dt
   basfsto = 0.
else
   basfsto = vbflw
endif
```

où :
- `qbas` est le débit de vidange vers le lit fluvial ($	ext{m}^3\cdot	ext{s}^{-1}$).
- `basfsto` est le volume d'eau stocké dans la nappe alluviale ($	ext{m}^3$).
- `tbsflw` est la constante de temps de vidange (en **jours**, comme l'atteste la conversion en secondes par le facteur $86\,400$ au dénominateur).
- `dt` est le pas de temps hydrodynamique ($900	ext{ s} = 15	ext{ min}$).

#### Origine et Définition de `cntime`
Dans `src/lisf/lis/routing/HYMAP2_router/HYMAP2_routingMod.F90` (lignes 1230–1241), la variable `cntime` est lue à partir du champ NetCDF `HYMAP_runoff_time_delay` :
- Il s'agit du temps de concentration du ruissellement superficiel de la cellule, exprimé en **secondes**.
- Sur les 15 937 mailles actives de notre domaine, `cntime` varie de $18\,003	ext{ s}$ ($5.0	ext{ h}$) à $8\,724\,306	ext{ s}$ ($101	ext{ j}$), avec une **médiane spatiale de $211\,374	ext{ s}$ ($58.7	ext{ h} pprox 2.4465	ext{ jours}$)** et une moyenne de $3.77	ext{ jours}$.
- **La valeur de $2.45	ext{ jours}$ représente la médiane spatiale du temps de concentration, et non un seuil numérique constant uniforme sur toutes les mailles.**

#### Condition Exacte du Plancher Numérique
Dans `HYMAP2_routingMod.F90` (lignes 1264–1267), Augusto Getirana a introduit la condition suivante (commentée par `[INFO] Remove zeros from groundwater time delay`) :
```fortran
where(HYMAP2_routing_struc(n)%tbsflw < HYMAP2_routing_struc(n)%cntime/86400. .and. &
     HYMAP2_routing_struc(n)%cntime > 0) &
     HYMAP2_routing_struc(n)%tbsflw = HYMAP2_routing_struc(n)%cntime/86400.
```
- **Rôle dans le code :** Cette instruction remplace `tbsflw` par `cntime / 86400.` (en jours) dès lors que sa valeur est inférieure à ce ratio local.
- **Matrice brute non corrigée :** Le fichier brut `lis_tbasflw_005.bin` contenait des valeurs de $10\,800$ à $86\,400$ (moyenne $61\,703$). Dans LISF, cela équivalait à une constante de $61\,703	ext{ jours}$ ($pprox 169	ext{ ans}$). Comme $61\,703 > cntime/86400.$, le plancher n'était **jamais activé**, provoquant l'accumulation de $+16\,518	ext{ hm}^3$ dans la nappe et le blocage de $97.5\%$ du drainage $Q_{sb}$.
- **Activation sous configuration corrigée :** La division par 86 400 dans `lis_input_corrigee.d01.nc` ramène `tbsflw` entre $0.0024	ext{ j}$ et $30.46	ext{ j}$ (médiane $0.077	ext{ j} pprox 1.86	ext{ h}$). Cette valeur étant inférieure à `cntime / 86400.` sur la quasi-totalité du domaine, **le plancher numérique est activé sur $15\,921$ mailles sur $15\,937$, soit très exactement $99.90\%$ des cellules actives**.
- **Paramètre effectivement utilisé :** Le calcul hydrodynamique applique donc localement :
  $$tbsflw_{	ext{effectif}} = \max\left(tbsflw, rac{cntime}{86\,400}ight)$$
  dont la médiane spatiale est de **$2.45	ext{ jours}$** et la moyenne spatiale de **$3.77	ext{ jours}$**.

#### Nuance Scientifique sur la Portée de la Correction
1. **Rôle opérationnel :** La division par 86 400 est indispensable car elle abaisse `tbsflw` en dessous du piège séculaire (169 ans), permettant au plancher effectif ($2.45	ext{ j}$) de régir la vidange et de fermer le bilan de masse ($99.965\%$).
2. **Limite de validité physique :** **La fermeture numérique du bilan de masse ne démontre pas la validité physique du temps de vidange effectif.** En effet, parce que $99.90\%$ des mailles actives sont écrêtées par `cntime/86400.`, la distribution spatiale réelle de la carte d'origine est masquée par celle du ruissellement superficiel.
3. **Incertitude ouverte :** **L'unité native et l'intention de calibration des données transmises par Augusto restent à confirmer formellement.**

### 3.3 Utilisation Effective et Propriétés de l'Aire de Grille (`lis_grarea_005.bin` / `HYMAP_grid_area`)
La variable `HYMAP_grid_area` (nom interne Fortran `grarea`) intervient directement dans le moteur de calcul (`src/lisf/lis/routing/HYMAP2_router/HYMAP2_model_core.F90`, lignes 210–213) :

```fortran
where(runoff0/=mis .and. grarea/=mis)
   runoff1 = runoff1 * grarea / 1e3
   basflw1 = basflw1 * grarea / 1e3
else where
   runoff1 = 0.
   basflw1 = 0.
end where
```

- **Rôle dans les conversions de flux :** `grarea` (en $	ext{m}^2$) est le multiplicateur géométrique qui convertit les flux surfaciques spécifiques calculés par Noah-MP ($runoff0, basflw0$ en $	ext{kg}\cdot	ext{m}^{-2}\cdot	ext{s}^{-1} \equiv 	ext{mm}\cdot	ext{s}^{-1}$) en débits volumiques entrants ($runoff1, basflw1$ en $	ext{m}^3\cdot	ext{s}^{-1}$) injectés dans le réseau fluvial. Elle intervient aussi pour convertir le volume stocké en hauteur d'eau de surface : `surfws = 1e3 * (rivsto + fldsto) / grarea`.
- **Distribution spatiale constatée dans le fichier :**
  - Minimum : $0.022	ext{ km}^2$ (bordures côtières masquées).
  - Maximum : **$178.88	ext{ km}^2$**.
  - Médiane : **$20.42	ext{ km}^2$**.
  - **Moyenne spatiale sur les 15 937 mailles actives : $25.530	ext{ km}^2$**.
  - Plus de 3 020 cellules dépassent $40	ext{ km}^2$, et 151 cellules dépassent $100	ext{ km}^2$.
- **Nuance sur la cohérence géométrique :**
  - La moyenne spatiale de $25.53	ext{ km}^2$ est rigoureusement cohérente avec l'aire théorique moyenne d'une cellule régulière $0.05^\circ 	imes 0.05^\circ$ sur ce domaine géographique ($24.6$ à $26.8	ext{ km}^2$, moyenne $pprox 25.6	ext{ km}^2$), garantissant la conservation du volume total à l'échelle du domaine.
  - **Cependant, cette moyenne ne valide pas à elle seule la distribution spatiale locale.** Nous ne disposons pas dans le dépôt de documentation ni de code détaillant la méthode exacte de construction de cette carte dans l'archive originale d'Augusto. La provenance détaillée et la justification physique de cette forte variabilité locale (allant jusqu'à $178.9	ext{ km}^2$) constituent une **question technique ouverte à soumettre à Augusto Getirana**.

## 4. Préparation et Remapping des Ruissellements Noah-MP

### 4.1 Récupération des Flux de Ruissellement Noah-MP
Les simulations de surface continentale Noah-MP 4.0.1 produisent quotidiennement des fichiers d'historique NetCDF archivés par mois (`YYYYMM/`) contenant les flux moyens journaliers :
- `Qs_tavg` : ruissellement de surface rapide (*surface runoff amount*, $	ext{kg}\cdot	ext{m}^{-2}\cdot	ext{s}^{-1}$).
- `Qsb_tavg` : drainage profond sous-racinaire (*subsurface runoff amount*, $	ext{kg}\cdot	ext{m}^{-2}\cdot	ext{s}^{-1}$).

Ces flux sont calculés sur la grille Noah-MP de **181 points en longitude $	imes$ 121 points en latitude**, en projection cylindrique équidistante régulière à $0.05^\circ$ ($[-10^\circ, -1^\circ]	ext{E} 	imes [30^\circ, 36^\circ]	ext{N}$). Les coordonnées stockées correspondent strictement aux sommets (nœuds) de la boîte de calcul.

### 4.2 Formulation du Rééchantillonnage 4-Nœuds
Le moteur HyMAP2 requiert des flux centrés sur ses **180 colonnes $	imes$ 120 lignes** de calcul.
Le transfert spatial est réalisé par une formule de moyenne arithmétique aux 4 sommets appliquée sur chaque maille cible $(j, i)$ :

$$ar{q}[j, i] = rac{1}{4} \Big( q_{	ext{noah}}[j, i] + q_{	ext{noah}}[j, i+1] + q_{	ext{noah}}[j+1, i] + q_{	ext{noah}}[j+1, i+1] \Big)$$

Ce traitement est implémenté dans les trois scripts d'extraction opérationnels :
- `scripts/remap_runoff_opl.py` (pour l'expérience Open-Loop).
- `scripts/remap_runoff_danocdf.py` (pour l'expérience DA-NoCDF).
- `scripts/remap_runoff_dacdf.py` (pour l'expérience DA-CDF).

### 4.3 Statut Méthodologique et Contrôle Empirique de la Conservation de Masse
Une distinction scientifique claire s'impose quant à la nature de cet opérateur :
- **Nature de l'opérateur :** Il s'agit d'une moyenne nodale arithmétique et **non d'un remapping conservatif par construction géométrique** (tel qu'une méthode d'intersection surfacique polygonale de type *first-order conservative* d'ESMF).
- **Contrôle empirique de conservation :** L'évaluation documentée dans `checks/03_remapping_ruissellement.md` montre que l'intégrale spatiale du flux rééchantillonné ($S_2$) comparée à l'intégrale du flux source ($S_1$) sur l'emprise géographique commune donne :
  $$rac{S_2}{S_1} pprox 100.0002\%$$
  L'écart massique introduit par l'interpolation nodale est inférieur à **$0.0002\%$** sur ce domaine régulier, ce qui garantit empiriquement une excellente conservation des volumes d'eau injectés.
- **Filtrage des valeurs aberrantes :** Les résidus numériques négatifs ou indéfinis (`NaN`, valeurs $< 0$) sont remis à zéro avant calcul.

### 4.4 Explication du Nombre de Fichiers : 1 828 Forçages vs 1 827 Jours Simulés
La période quinquennale s'étend du 01/01/2016 à 00:00:00 UTC au 01/01/2021 à 00:00:00 UTC, soit très exactement **1 827 jours civils réels** (l'année bissextile 2016 comptant 366 jours, plus 4 années de 365 jours).

Pourtant, le répertoire `runoff_remap_180x120/<EXP>/SURFACEMODEL/` contient précisément **1 828 fichiers NetCDF**.
Cette différence d'un fichier s'explique par la mécanique interne de LISF :
- Le module de lecture des forçages (`readLISrunoffdata.F90`) effectue une interpolation temporelle pour alimenter le pas de temps de 15 minutes de HyMAP.
- Pour calculer les débits du dernier jour (le 31/12/2020) jusqu'à 00:00 UTC le 01/01/2021, la routine d'interpolation tente d'encadrer l'intervalle en lisant le fichier du jour $T+1$ (`LIS_HIST_202101020000.d01.nc`).
- En l'absence de ce fichier, LIS s'interrompt avec une erreur d'E/S (*missing forcing file*).
- Les scripts de remapping ont donc cloné le fichier du 01/01/2021 pour créer ce **fichier frontière terminal (*padding file*)**, assurant la continuité complète des 1 827 jours de routage.

---

## 5. Compilation et Configuration Opérationnelle de LIS / HyMAP2

### 5.1 Procédure de Compilation (build_lis_hymap2.sh)
Le modèle LIS 7.3 est compilé en mode routage autonome à l'aide du script [`jobs/build_lis_hymap2.sh`](../jobs/build_lis_hymap2.sh).
```bash
./configure << EOF
2    # Linux (x86_64), Intel compiler (mpiifort)
2    # NetCDF 4 interface
/srv/software/easybuild/software/NetCDF-Fortran/4.5.3-iimpi-2021a
/srv/software/easybuild/software/HDF5/1.10.6-iimpi-2021a
/srv/software/easybuild/software/ESMF/8.0.1-intel-2021a
y    # Use GRIB API / ecCodes: n
y    # Enable HyMAP2 routing model
EOF
make -j 8
```
Le binaire résultant `LIS` est déployé dans le répertoire d'exécution.

### 5.2 Anatomie du Fichier de Configuration lis.config
Directives clés indispensables pour la simulation :
```ini
# --- Domaine spatial (Identique au fichier LDT 180x120) ---
Map projection of the LIS domain:       latlon
Run domain lower left lat:              30.0000
Run domain lower left lon:             -10.0000
Run domain upper right lat:             36.0000
Run domain upper right lon:             -1.0000
Run domain resolution (dx):              0.0500
Run domain resolution (dy):              0.0500
Run domain x-dimension:                 180
Run domain y-dimension:                 120

# --- Paramétrage du routage hydrodynamique HyMAP2 ---
Routing model:                          "HYMAP2 router"
HYMAP routing method:                   kinematic
HYMAP routing model time step:          "15mn"
HYMAP routing output interval:          "1da"
HYMAP routing restart output frequency: "1mo"
HYMAP floodplain dynamics:              0
HYMAP reservoir operation:              0
HYMAP routing parameter file:           ./ldt_hymap/lis_input_corrigee.d01.nc

# --- Variables de sortie et forçages ---
LIS domain and surface model data file: ./ldt_hymap/lis_input_corrigee.d01.nc
Surface model output forcing directory: ./runoff_remap_180x120/OPL_2016_2020_corrigee/SURFACEMODEL
Output model output list file:          ./tables/MODEL_OUTPUT_LIST_routing.TBL
```

### 5.3 Différenciation des Configurations : Spin-up vs Production

| Paramètre clé dans `lis.config` | Spin-up Cycle 1 (C1) | Spin-up Cycle 2 (C2) | Production Quinquennale (2016–2020) |
| :--- | :---: | :---: | :---: |
| **Date de début** | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 | 2016-01-01 00:00:00 |
| **Date de fin** | 2017-01-01 00:00:00 (1 an) | 2017-01-01 00:00:00 (1 an) | 2021-01-01 00:00:00 (5 ans) |
| **Mode d'initialisation** | Démarrage à froid (*coldstart*) | Démarrage à chaud (*hotstart*) | Démarrage à chaud (*hotstart*) |
| **Restart d'entrée (`rst_in`)** | `none` (Tous stocks = 0) | `output/..._spinup_c1/.../LIS_RST_...201701010000.d01.nc` | `output/..._spinup_c2/.../LIS_RST_...201701010000.d01.nc` |
| **Sortie des historiques** | Activée (contrôle) | Activée (contrôle) | Activée (1 827 fichiers pour analyse) |

---

## 6. Protocole d'Initialisation et Convergence du Spin-up

### 6.1 Justification du Protocole à Double Cycle (C1 & C2)
Lors d'un démarrage à froid (*coldstart* avec $BSFSTO = 0$ et $RIVSTO = 0$), l'eau initiale s'infiltre pour remplir la capacité de stockage géologique. Durant les premiers mois, les débits d'étiage sont artificiellement nuls.

L'année 2016 (366 jours) est donc simulée deux fois consécutivement :
1. **Cycle C1 (2016) :** Démarrage à nappe vide (`coldstart`). Le réservoir se remplit et LISF génère le fichier de restart `LIS_RST_HYMAP2_router_201701010000.d01.nc`.
2. **Cycle C2 (2016) :** Réinitialisation au 01/01/2016 avec le restart C1. L'année 2016 est re-simulée avec une nappe déjà équilibrée. Le restart généré au 01/01/2017 constitue la condition initiale définitive du run de production quinquennal.

### 6.2 Critère Numérique de Convergence sur BSFSTO
Le critère mesure la dérive relative du stock souterrain total du domaine ($BSFSTO$, en $	ext{hm}^3$) entre la fin du cycle 1 et la fin du cycle 2 au 1ᵉʳ janvier à 00:00 UTC :

$$\Delta S = rac{|BSFSTO_{C2} - BSFSTO_{C1}|}{BSFSTO_{C1}} 	imes 100$$

Le critère d'acceptation est fixé à **$\Delta S < 1.0\%$**.

### 6.3 Résultats Comparatifs de Convergence

| Expérience | Stock fin C1 ($BSFSTO$, $	ext{hm}^3$) | Stock fin C2 ($BSFSTO$, $	ext{hm}^3$) | Dérive relative $\Delta S$ | Statut de convergence |
| :--- | :---: | :---: | :---: | :---: |
| **Open-Loop (OPL corrigée)** | **$46.504	ext{ hm}^3$** | **$46.565	ext{ hm}^3$** | **$+0.132\%$** | Validé ($\Delta S \ll 1\%$) |
| **DA-NoCDF** | **$146.113	ext{ hm}^3$** | **$146.207	ext{ hm}^3$** | **$+0.065\%$** | Validé ($\Delta S \ll 1\%$) |
| **DA-CDF** | **$134.69	ext{ hm}^3$** | **$134.79	ext{ hm}^3$** | **$+0.076\%$** | Validé ($\Delta S \ll 1\%$) |

Le stock souterrain atteint une stabilité périodique dès le second cycle.

### 6.4 Limites Scientifiques du Critère de Convergence
- **Stabilité numérique $
eq$ Équilibre hydrogéologique réel :** La stabilisation du réservoir $BSFSTO$ à $\sim 46.5	ext{ hm}^3$ sous OPL reflète la convergence mathématique d'un réservoir linéaire subissant le plancher de vidange effectif de $2.45	ext{ jours}$.
- Dans les aquifères réels du Maroc, le temps de réponse des nappes profondes dépasse plusieurs décennies. Le spin-up garantit la continuité mathématique des flux, mais ne simule pas la véritable dynamique piézométrique pluriannuelle.

## 7. Exécution et Contrôle des Simulations Quinquennales (2016–2020)

### 7.1 Description des Trois Simulations Quinquennales Validées
Le socle scientifique repose sur trois simulations de 5 années continues (du 01/01/2016 à 00:00 UTC au 01/01/2021 à 00:00 UTC, soit 1 827 jours civils) :
1. **Open-Loop (OPL corrigée) :** Simulation en boucle ouverte forcée par la météorologie sans assimilation de données satellitaires (`OPL_2016_2020_corrigee`).
2. **Assimilation SMAP NoCDF (DA-NoCDF) :** Assimilation directe par filtre EnKF des observations SMAP L3 d'humidité du sol sans correction préalable de biais (`DA_nocdf_2016_2020`).
3. **Assimilation SMAP DA-CDF (DA-CDF) :** Assimilation EnKF avec mise à l'échelle préalable par **CDF matching** spatialisé sur le domaine (`DA_cdf_2016_2020`).

### 7.2 Distinction Fondamentale entre les Deux Niveaux de Correction
- **Le correctif HyMAP de nappe (`tbasflw / 86400`) :** Correctif physico-numérique appliqué à la grille statique LDT (`ldt_hymap/lis_input_corrigee.d01.nc`). Strictement identique pour les trois expériences de routage, il élimine le temps de séjour de 169 ans et assure la fermeture du bilan de masse.
- **Le correctif CDF matching Noah-MP :** Prétraitement statistique appliqué en amont aux données satellitaires SMAP avant leur ingestion par Noah-MP. Il adapte la distribution statistique des humidités satellitaires à la climatologie du modèle, évitant l'injection excessive de ruissellement constatée sous DA-NoCDF dans le Bouregreg.

### 7.3 Contrôles de Complétude, de Bilan et de Continuité
- **Complétude temporelle :** Exactement **1 827 fichiers NetCDF journaliers** (`LIS_HIST_YYYYMMDD0000.d01.nc`) et 60 fichiers de restart mensuels sans rupture.
- **Fermeture du bilan de masse :** Le volume total écoulé plus la variation des stocks ($V_{sim} + \Delta S$) égale le volume d'eau injecté ($V_{in}$) à **$99.965\%$** de précision.
- **Continuité interannuelle :** Absence de discontinuité des stocks souterrains lors des transitions d'années civiles.

---

## 8. Extraction Spatiale des Débits et Référentiel des Stations

### 8.1 Rôle et Fonctionnement de extract_streamflow.py
L'extraction spatiale automatisée est réalisée par le script [`scripts/extract_streamflow.py`](../scripts/extract_streamflow.py).
Ce script prend en argument l'identifiant d'une expérience (`opl`, `nocdf`, `cdf` ou `all`), lit les 1 827 fichiers NetCDF journaliers, extrait `Streamflow_tavg` au droit des mailles associées aux stations et génère un fichier CSV consolidé horodaté :
- Format du CSV produit : colonnes `date, station_id_1, station_id_2, ...`
- Vitesse d'exécution : extraction complète des 5 ans en moins de 3 minutes sur le cluster.

### 8.2 Référentiel des 12 Stations et Table d'Appariement
L'appariement géomorphologique entre les coordonnées réelles des stations ABH et la grille discrétisée HyMAP ($0.05^\circ$) est consigné dans [`stations/hymap_stations_pairing.csv`](../stations/hymap_stations_pairing.csv) :

| ID Station | Nom officiel ABH | Oued | Bassin | IRE ABH | Pas de temps | Coord. ABH (Lon, Lat) | Maille HyMAP (col, row) | Aire officielle ($	ext{km}^2$) | Aire HyMAP ($	ext{km}^2$) | Écart d'aire (%) |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `b_s_jabeur` | **Sidi Jabeur** | Grou | Bouregreg | 964/21 | Journalier | (-6.4950, 33.5240) | (70, 70) | 3 138.5 | 3 105.2 | **-1.1%** |
| `b_l_chafia` | **Lalla Chafia** | Bouregreg | Bouregreg | 963/21 | Journalier | (-6.6570, 33.5650) | (67, 71) | 3 341.6 | 3 280.4 | **-1.8%** |
| `ain_timedrine`| **Ain Timedrine** | Sebou | Sebou | 581/22 | Mensuel | (-4.8140, 34.0720) | (104, 81) | 4 387.0 | 4 412.8 | **+0.6%** |
| `dar_el_hamra` | **Dar El Hamra** | Zloul | Sebou | 1000/23 | Mensuel | (-4.4070, 33.9160) | (112, 78) | 670.0 | 664.2 | **-0.9%** |
| `pont_de_mdez` | **Pont de Mdez** | Sebou | Sebou | 582/22 | Mensuel | (-4.6470, 33.6820) | (107, 74) | 3 435.0 | 2 331.0 | **-32.1%** |
| `azzaba` | Azzaba | Sebou | Sebou | 583/22 | Mensuel | (-4.8480, 34.0270) | (103, 81) | 4 640.0 | 4 520.1 | **-2.6%** |
| `ait_khabbach` | Ait Khabbach | Guigou | Sebou | 585/22 | Mensuel | (-4.9280, 33.6190) | (101, 72) | 1 240.0 | 1 180.5 | **-4.8%** |
| `pont_ait_aissa`| Pont Ait Aissa| Guigou | Sebou | 198/30 | Mensuel | (-5.2280, 33.3150) | (95, 66) | 205.0 | 198.4 | **-3.2%** |
| `el_mers` | El Mers | Masser | Sebou | 541/23 | Mensuel | (-4.5020, 33.4730) | (110, 69) | 1 004.0 | 954.0 | **-5.0%** |
| `b_a_loudah` | Ain Loudah | Korifla | Bouregreg | 2673/20 | Journalier | (-6.8200, 33.6300) | (64, 73) | 697.6 | 712.0 | **+2.1%** |
| `b_s_cherif` | S.M. Cherif | Mechraa | Bouregreg | 2674/20 | Journalier | (-6.7800, 33.6500) | (64, 73) | 649.5 | 712.0 | **+9.6%** |
| `ksob_adamna` | Adamna | Ksob | Côtier Sud | 291/51 | Journalier | (-9.6450, 31.4980) | (7, 30) | 1 470.0 | 1 420.0 | **-3.4%** |

### 8.3 Confrontation des Surfaces Drainées (Officielles vs HyMAP)
La résolution spatiale à $0.05^\circ$ ($pprox 5	ext{ km}$) entraîne des écarts de délimitation selon le relief :
- Pour les grands bassins aval (Ain Timedrine, Sidi Jabeur, Lalla Chafia, Azzaba), l'écart relatif entre surface officielle ABH et surface calculée par HyMAP est inférieur à **$3\%$**.
- En montagne dans le Moyen Atlas, la discrétisation à 5 km tronque des sous-bassins : à la station **Pont de Mdez**, l'aire HyMAP ($2\,331	ext{ km}^2$) sous-estime l'aire officielle ($3\,435	ext{ km}^2$) de **$-32.1\%$**. Cette troncature géométrique explique une part directe du déficit de débit simulé.
- **Duplication apparente des observations :** Les stations `b_a_loudah` et `b_s_cherif` possèdent des chroniques journalières observées strictement identiques dans les fichiers fournis par l'ABHBC, tout en pointant sur la même maille HyMAP (64, 73). Il s'agit d'une duplication apparente dans la base de données observée qui doit être prise en compte pour ne pas fausser les analyses statistiques par un double comptage.

---

## 9. Évaluation et Validation Hydrologique aux Stations ABH

### 9.1 Débits Observés ABH et Métriques de Performance
Les séries d'observation proviennent des Agences de Bassin Hydraulique du Sebou (ABHS) et du Bouregreg-Chaouia (ABHBC), nettoyées sous `data/streamflow_clean/`.
L'évaluation mise en œuvre dans [`scripts/evaluate_sebou_bouregreg.py`](../scripts/evaluate_sebou_bouregreg.py) s'appuie sur :
- **Kling-Gupta Efficiency (KGE) :** Mesure globale équilibrant corrélation $r$, variabilité relative $lpha = \sigma_{sim}/\sigma_{obs}$ et biais moyen $eta = \mu_{sim}/\mu_{obs}$.
- **Nash-Sutcliffe Efficiency (NSE) :** Sensible aux erreurs sur les pointes de crue.
- **Percent Bias (PBIAS, %) :** Biais volumique relatif cumulé : $PBIAS = rac{\sum (Q_{sim} - Q_{obs})}{\sum Q_{obs}} 	imes 100$.
- **Coefficient de corrélation de Pearson ($r$) :** Synchronisme des hydrogrammes.

### 9.2 Analyse des Résultats aux 5 Stations Prioritaires (Faits Vérifiés)
Les résultats numériques issus de `plots/sebou_bouregreg/tables/tableau_diagnostic_5stations.csv` sont présentés ci-dessous :

| Station (Bassin, Pas) | Expérience | $Q_{	ext{obs}}$ moy | $Q_{	ext{sim}}$ moy | $Q_{	ext{med}}$ obs | $Q_{	ext{med}}$ sim | $Q_{	ext{max}}$ obs | $Q_{	ext{max}}$ sim | PBIAS (%) | KGE | NSE | Corrélation $r$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sidi Jabeur** | **OPL** | 4.15 | 2.38 | 0.41 | 1.88 | 349.0 | 14.7 | **-42.8%** | -0.14 | +0.06 | 0.47 |
| *(Bouregreg, journalier)*| **DA-NoCDF** | 4.15 | 8.92 | 0.41 | 5.71 | 349.0 | 67.6 | **+114.6%** | -0.41 | -0.04 | 0.32 |
| *(N = 1 827 jours)* | **DA-CDF** | 4.15 | 6.36 | 0.41 | 5.06 | 349.0 | 50.1 | **+53.0%** | -0.08 | +0.11 | 0.37 |
| **Lalla Chafia** | **OPL** | 3.49 | 3.64 | 0.60 | 2.43 | 199.0 | 34.0 | **+4.3%** | **+0.10** | **+0.18** | 0.47 |
| *(Bouregreg, journalier)*| **DA-NoCDF** | 3.49 | 16.79 | 0.60 | 9.56 | 199.0 | 129.1 | **+380.6%** | -2.89 | -2.42 | 0.47 |
| *(N = 1 826 jours)* | **DA-CDF** | 3.49 | 8.79 | 0.60 | 7.01 | 199.0 | 61.8 | **+151.6%** | -0.66 | +0.03 | 0.50 |
| **Ain Timedrine** | **OPL** | 9.17 | 2.08 | 6.97 | 1.98 | 25.9 | 3.87 | **-77.3%** | -0.32 | -1.38 | 0.38 |
| *(Sebou, mensuel)* | **DA-NoCDF** | 9.17 | 3.20 | 6.97 | 2.78 | 25.9 | 9.60 | **-65.0%** | -0.07 | -0.80 | 0.57 |
| *(N = 60 mois)* | **DA-CDF** | 9.17 | 3.96 | 6.97 | 3.62 | 25.9 | 9.82 | **-56.8%** | **-0.01** | -0.54 | **0.62** |
| **Dar El Hamra** | **OPL** | 1.94 | 0.43 | 0.87 | 0.39 | 11.7 | 0.81 | **-78.1%** | -0.26 | -0.29 | **0.67** |
| *(Sebou/Zloul, mensuel)*| **DA-NoCDF** | 1.94 | 1.45 | 0.87 | 0.96 | 11.7 | 5.92 | **-25.4%** | **+0.25** | **+0.24** | 0.54 |
| *(N = 60 mois)* | **DA-CDF** | 1.94 | 1.06 | 0.87 | 1.05 | 11.7 | 2.36 | **-45.4%** | -0.14 | -0.03 | 0.38 |
| **Pont de Mdez** | **OPL** | 3.97 | 1.67 | 3.40 | 1.55 | 14.9 | 3.02 | **-57.9%** | -0.19 | -0.41 | 0.39 |
| *(Haut Sebou, mensuel)* | **DA-NoCDF** | 3.97 | 1.70 | 3.40 | 1.53 | 14.9 | 3.97 | **-57.3%** | -0.12 | -0.35 | 0.46 |
| *(N = 44 mois)* | **DA-CDF** | 3.97 | 2.47 | 3.40 | 2.30 | 14.9 | 4.66 | **-37.9%** | **+0.07** | **+0.02** | **0.62** |

### 9.3 Synthèse Critique et Nuances Hydrologiques
1. **Comportement contrasté dans le Bouregreg (Sidi Jabeur vs Lalla Chafia) :**
   - En Open-Loop (OPL), le modèle simule fidèlement le volume cumulé à Lalla Chafia ($PBIAS = +4.3\%$), mais atténue les pointes extrêmes ($Q_{	ext{max}} = 34	ext{ m}^3/	ext{s}$ vs $199	ext{ m}^3/	ext{s}$) et élève la médiane d'étiage ($2.43$ vs $0.60	ext{ m}^3/	ext{s}$).
   - À Sidi Jabeur, l'OPL sous-estime le volume global ($PBIAS = -42.8\%$), avec un aplatissement similaire des pointes de crue ($14.7$ vs $349.0	ext{ m}^3/	ext{s}$).
2. **Impact de l'assimilation SMAP :**
   - L'assimilation brute sans CDF matching (DA-NoCDF) multiplie par 4.8 le débit à Lalla Chafia ($PBIAS = +380.6\%$, $KGE = -2.89$).
   - Le CDF matching (DA-CDF) réduit significativement cette dérive ($PBIAS = +151.6\%$).
3. **Sous-estimation persistante dans le Haut Sebou :**
   - À Ain Timedrine, Dar El Hamra et Pont de Mdez, toutes les simulations sous-estiment les volumes ($PBIAS$ entre $-25\%$ et $-78\%$).
   - La sous-délimitation d'aire à Pont de Mdez ($-32\%$), les pertes par infiltration karstique dans le Moyen Atlas et la sous-estimation du manteau neigeux dans Noah-MP constituent des hypothèses physiques explicatives majeures.

## 10. Assumptions, Known Limitations and Unresolved Technical Questions

Cette section formalise l'état de l'art scientifique du routage HyMAP2 sur le Nord Maroc selon une grille d'analyse standardisée distinguant faits observés, éléments de preuve, hypothèses explicatives et questions ouvertes.

### 10.1 Diagnostic du Correctif tbasflw et Rôle du Plancher cntime
1. **Constat vérifié :** Le binaire original d'Augusto `lis_tbasflw_005.bin` contient des valeurs comprises entre 10 800 et 86 400 (moyenne spatiale 61 703). L'équation Fortran de LISF ($Q_{bas} = S_{bas} / (tbsflw \cdot 86\,400)$) applique un temps de vidange séculaire de 169 ans, accumulant $+16\,518	ext{ hm}^3$ dans la nappe et bloquant 97.5% de $Q_{sb}$.
2. **Éléments de preuve :** Code source `HYMAP2_modelMod.F90` (ligne 112), `HYMAP2_routingMod.F90` (lignes 1264–1267), fiches d'audit `checks/01_parametres_augusto.md` et `checks/06_audit_coherence.md`.
3. **Mécanisme du plancher numérique :** Dans `HYMAP2_routingMod.F90`, Augusto Getirana a introduit la condition :
   `where(tbsflw < cntime/86400. .and. cntime > 0) tbsflw = cntime/86400.`
   initialement conçue pour éliminer les divisions par zéro (`Remove zeros from groundwater time delay`).
   - La valeur de **$2.45	ext{ jours}$** représente la **médiane spatiale du temps effectif**, et non un seuil numérique constant uniforme sur toutes les mailles (les valeurs locales de `cntime/86400.` s'échelonnent entre 0.21 et 100.98 jours).
   - Dans la configuration corrigée (division par 86 400), **le plancher numérique est activé sur $99.90\%$ des cellules actives** ($15\,921$ mailles sur $15\,937$).
4. **Portée et limites de la correction :**
   - La division par 86 400 est indispensable car elle abaisse le paramètre sous le piège séculaire (169 ans), permettant au plancher effectif ($2.45	ext{ j}$) de régir la vidange et de fermer le bilan de masse ($99.965\%$).
   - **La fermeture numérique du bilan de masse ne démontre pas la validité physique du temps de vidange effectif.** En effet, parce que $99.90\%$ des cellules sont écrêtées par ce plancher, la variabilité spatiale fine de la carte d'origine est masquée par celle du temps de concentration.
5. **Vérification nécessaire :** **L'unité native et l'intention de calibration des données fournies par Augusto restent à confirmer formellement.**
6. **Statut :** **Incompatibilité Fortran résolue numériquement, question physique ouverte pour Augusto.**

### 10.2 Sensibilité aux Stockages Souterrains et Équilibrage de Nappe
1. **Constat vérifié :** Un démarrage à froid (*coldstart* $BSFSTO=0$) sous-estime les débits de base pendant plusieurs mois. Le protocole à double cycle annuel (C1 et C2 sur 2016) stabilise le réservoir avec une dérive interannuelle $\Delta S < 0.15\%$.
2. **Éléments de preuve :** Convergence à $46.56	ext{ hm}^3$ (OPL) et $134.79	ext{ hm}^3$ (DA-CDF) dans `output/`.
3. **Hypothèse explicative :** Le réservoir conceptuel linéaire sub-maille atteint son régime permanent rapidement dès lors que la constante effective est contrainte par le plancher de 2.45 jours.
4. **Conséquence possible :** Cette stabilité numérique ne prouve pas que le stock simulé corresponde au stock physique réel des aquifères profonds marocains, dont le temps de réponse dépasse couramment plusieurs années ou décennies.
5. **Vérification nécessaire :** Tester un spin-up multi-décennal et comparer la dynamique de vidange aux chroniques piézométriques observées de l'ABH Sebou.
6. **Statut :** **Protocole numérique validé, représentativité hydrogéologique ouverte.**

### 10.3 Débits d'Étiage et Dynamique des Assecs
1. **Absence vérifiée de contrainte minimale :** L'inspection du code source de LISF/HyMAP2 confirme **l'absence de toute contrainte explicite ou seuil imposant un débit minimal non nul ($Q_{min}$)**. Le débit de vidange calculé ($Q_{bas} = S_{bas} / 	au$) s'annulerait si le réservoir souterrain devenait vide ($S_{bas} = 0$).
2. **Constat vérifié sur les simulations :** En pratique, les débits simulés maintiennent des valeurs strictement positives pendant certaines périodes d'étiage estival où les oueds observés sont en assec complet ($Q_{	ext{obs}} = 0.0	ext{ m}^3/	ext{s}$), comme en témoigne la médiane simulée de $1.88	ext{ m}^3/	ext{s}$ à Sidi Jabeur pour une médiane observée de $0.41	ext{ m}^3/	ext{s}$.
3. **Hypothèses explicatives possibles :**
   - *Rôle possible des apports $Q_{sb}$ :* Le drainage sous-racinaire simulé par Noah-MP pourrait maintenir une alimentation continue du réservoir de nappe alluviale pendant l'été. Cette hypothèse reste à quantifier précisément par l'analyse des séries journalières de $Q_{sb}$ sur ces périodes.
   - *Pertes en rivière non représentées :* HyMAP2 ne modélise pas l'évaporation directe de la surface en eau du chenal en lit mineur ni l'infiltration le long du lit vif (*transmission losses* dans les alluvions perméables).
4. **Conséquence possible :** Surestimation systématique des faibles débits et difficulté structurelle à reproduire les arrêts complets d'écoulement des rivières temporaires semi-arides.
5. **Statut :** **Constat établi, hypothèses explicatives identifiées mais non démontrées causalement.**

### 10.4 Biais Contrastés entre Stations du Bouregreg et du Sebou
1. **Constat vérifié :** En boucle ouverte (OPL), le modèle capture fidèlement le volume annuel à Lalla Chafia ($PBIAS = +4.3\%$), mais sous-estime Sidi Jabeur ($-42.8\%$), Ain Timedrine ($-77.3\%$), Dar El Hamra ($-78.1\%$) et Pont de Mdez ($-57.9\%$).
2. **Éléments de preuve :** Tableaux de synthèse dans `plots/sebou_bouregreg/tables/`.
3. **Hypothèse explicative :** Les erreurs ne sont pas homogènes à l'échelle d'un grand bassin versant. Elles résultent d'effets locaux : géométrie de drainage à $5	ext{ km}$, gradient orographique des précipitations en montagne et caractéristiques lithologiques régionales.
4. **Conséquence possible :** Il est scientifiquement inexact de qualifier globalement le Bouregreg de "surestimé" ou le Sebou de "sous-estimé" ; chaque station présente une signature propre.
5. **Vérification nécessaire :** Cartographier les anomalies spatiales de forçage pluviométrique station par station.
6. **Statut :** **Diagnostic analytique validé.**

### 10.5 Impact Contrasté des Assimilations SMAP (OL vs DA-NoCDF vs DA-CDF)
1. **Constat vérifié :** L'assimilation SMAP brute sans CDF matching (DA-NoCDF) multiplie le débit moyen à Lalla Chafia par 4.8 ($PBIAS = +380.6\%$, $KGE = -2.89$). Le CDF matching (DA-CDF) corrige cette dérive ($PBIAS = +151.6\%$).
2. **Éléments de preuve :** `t8_sim_daily_12stations_da_nocdf.csv` et `t9_sim_daily_12stations_da_cdf.csv`.
3. **Hypothèse explicative :** Le produit SMAP L3 présente un biais systématique par rapport à la climatologie de Noah-MP. Sans mise à l'échelle CDF, les incréments EnKF saturent la colonne de sol et déclenchent des crues torrentielles fictives.
4. **Conséquence possible :** L'assimilation d'humidité du sol nécessite impérativement un pré-traitement CDF matching adapté.
5. **Vérification nécessaire :** Analyser les incréments EnKF couche par couche dans Noah-MP.
6. **Statut :** **Démontré et documenté.**

### 10.6 Partition Hydrologique de Surface (Qs) vs Sous-Surface (Qsb)
1. **Constat vérifié :** Dans Noah-MP, la contribution du drainage sous-racinaire $Q_{sb}$ représente 60% à 85% de l'apport liquide total en plaine, le ruissellement superficiel $Q_s$ n'intervenant que lors des fortes pluies.
2. **Éléments de preuve :** NetCDF de forçage `runoff_remap_180x120/`.
3. **Hypothèse explicative :** Le schéma d'infiltration de Noah-MP favorise la percolation profonde en sol semi-aride dégradé.
4. **Conséquence possible :** Comme $Q_{sb}$ transite obligatoirement par la nappe alluviale tamponnée, l'hydrogramme simulé est trop lisse, atténuant fortement les pointes de crue observées ($Q_{	ext{max}}$ = $14.7	ext{ m}^3/	ext{s}$ à Sidi Jabeur vs $349.0	ext{ m}^3/	ext{s}$ observé).
5. **Vérification nécessaire :** Évaluer d'autres options de ruissellement (`opt_run` dans Noah-MP).
6. **Statut :** **Identifié comme cause dominante de l'atténuation des pointes de crue.**

### 10.7 Signification et Distribution des Aires de Maille (HYMAP_grid_area / grarea)
1. **Constat vérifié :** Les valeurs de `HYMAP_grid_area` varient de $0.022	ext{ km}^2$ à $178.9	ext{ km}^2$, avec une moyenne spatiale sur le domaine actif de **$25.530	ext{ km}^2$**.
2. **Éléments de preuve :** Code source `HYMAP2_model_core.F90` (lignes 211–212), extraction NetCDF sous Python.
3. **Rôle effectif dans le code :** Dans HyMAP2, `grarea` (en $	ext{m}^2$) sert à convertir le ruissellement surfacique spécifique ($kg \cdot m^{-2} \cdot s^{-1} \equiv mm/s$) en débit volumique ($m^3/s$) par : `runoff1 = runoff1 * grarea / 1e3`.
4. **Nuance sur la cohérence spatiale :**
   - La moyenne spatiale de $25.53	ext{ km}^2$ est rigoureusement cohérente avec l'aire théorique d'une cellule régulière $0.05^\circ$ ($25.6	ext{ km}^2$), garantissant la conservation du volume total à l'échelle du domaine.
   - **Cependant, cette moyenne ne valide pas à elle seule la distribution spatiale locale.** Nous ne disposons pas dans le dépôt de documentation confirmant formellement l'algorithme d'allocation ayant produit des valeurs jusqu'à 178.9 km². Cette distribution ne doit pas être postulée comme issue d'une redistribution de sous-bassins MERIT-Hydro sans preuve matérielle explicite.
5. **Question ouverte :** La méthode de construction de cette carte doit être clarifiée avec Augusto Getirana.
6. **Statut :** **Compris sur le plan massique global, provenance de la distribution locale ouverte.**

### 10.8 Incertitudes de Résolution et d'Appariement des Stations
1. **Constat vérifié :** À la station de montagne Pont de Mdez, l'aire calculée par HyMAP ($2\,331	ext{ km}^2$) sous-estime l'aire officielle ($3\,435	ext{ km}^2$) de **$-32.1\%$**. À Ras El Ma, l'écart atteint **$-48.3\%$**. Pour les grands bassins aval, l'écart est inférieur à **$2\%$**.
2. **Éléments de preuve :** Table d'appariement `hymap_stations_pairing.csv`.
3. **Hypothèse explicative :** À une résolution de $0.05^\circ$ ($pprox 5	ext{ km}$), le réseau de drainage D8 tronque les vallées encaissées du Moyen Atlas.
4. **Conséquence possible :** Une fraction importante du déficit de débit simulé en montagne est d'origine purement géométrique.
5. **Vérification nécessaire :** Tester un maillage haute résolution à $0.01^\circ$ ($pprox 1	ext{ km}$).
6. **Statut :** **Démontré géométriquement.**

### 10.9 Duplication Apparente des Observations (Ain Loudah / S.M. Cherif)
1. **Constat vérifié :** Les séries temporelles journalières fournies pour les stations `b_a_loudah` (Ain Loudah, oued Korifla) et `b_s_cherif` (S.M. Cherif, oued Mechraa) sont **strictement identiques au centième de mètre cube près sur l'intégralité des 1 827 jours** dans les fichiers d'observation.
2. **Éléments de preuve :** `data/streamflow_clean/obs_daily.csv`, fiche `checks/05_evaluation_debits_historiques.md`.
3. **Statut factuel :** Il s'agit d'une duplication apparente au sein des archives hydrométriques transmises. La cause exacte de cette duplication dans la base patrimoniale de l'agence n'est pas établie par les documents du dépôt et ne doit pas faire l'objet de spéculations non vérifiées.
4. **Conséquence pour la validation :** Ces deux stations ne constituent pas deux contrôles indépendants.
5. **Recommandation :** Documenter cette dépendance et ne retenir qu'une seule des deux séries lors des analyses statistiques de synthèse.
6. **Statut :** **Fait établi et documenté.**

### 10.10 Hypothèses Physiques Non Résolues (Karst, Barrages, Irrigation, Orographie)
1. **Constat vérifié :** Des écarts de débit persistent dans le Haut Sebou même après calage géométrique.
2. **Éléments de preuve :** Biais négatif persistant à Ain Timedrine et Pont de Mdez.
3. **Hypothèses explicatives (non démontrées à ce stade) :**
   - *Endokarst du Moyen Atlas :* Pertes karstiques souterraines vers des circulations profondes non modélisées dans Noah-MP.
   - *Régulation par barrages :* Retenues et barrages écrêtant les crues.
   - *Prélèvements agricoles :* Pompages directs d'irrigation estivale.
   - *Biais orographique :* Sous-estimation des précipitations neigeuses sur les hauts reliefs.
4. **Conséquence méthodologique :** Ces processus n'étant pas intégrés dans notre chaîne actuelle, ils doivent être explicitement maintenus comme des hypothèses de travail ouvertes sans conclure prématurément.
5. **Statut :** **Hypothèses scientifiques de travail.**

## 11. How to Route a New Noah-MP Simulation with HyMAP2

Ce chapitre fournit le protocole opérationnel standard pour router toute nouvelle simulation de surface continentale Noah-MP (notée `NEW_EXP`).

### 11.1 Statut des Composants pour une Nouvelle Expérience

Afin d'assurer une parfaite transparence sur l'état de la chaîne de traitement, les composants se répartissent selon trois catégories distinctes :

| Catégorie | Fichiers et scripts concernés | Actions requises pour NEW_EXP |
| :--- | :--- | :--- |
| **Directement réutilisable sans modification** | - `ldt_hymap/lis_input_corrigee.d01.nc`<br>- `tables/MODEL_OUTPUT_LIST_routing.TBL`<br>- `stations/hymap_stations_pairing.csv`<br>- Binaire exécutable `LIS` | Aucune modification nécessaire dès lors que le domaine géographique reste le Nord Maroc ($180 	imes 120$). |
| **À copier et adapter (Paramétrage simple)** | - Fichiers de configuration LIS (`configs/lis_hymap2_*.config`)<br>- Scripts de soumission SLURM (`jobs/run_hymap2_*.sh`)<br>- Script de remapping des forçages (`scripts/remap_runoff_*.py`) | Copier les fichiers modèles OPL existants et adapter les chemins d'accès vers les forçages, les dossiers de sortie et les noms d'expérience. |
| **À adapter dans le code (Extension requise)** | - `scripts/extract_streamflow.py`<br>- `scripts/evaluate_sebou_bouregreg.py` | **Modification du code source requise :** ajouter l'entrée `new_exp` dans le dictionnaire `EXPERIMENT_CONFIGS` d'`extract_streamflow.py` et adapter `evaluate_sebou_bouregreg.py` (actuellement dimensionné pour 3 expériences) afin d'intégrer une 4ᵉ expérience. |

---

### 11.2 Guide Pas-à-Pas pour NEW_EXP

#### Étape 1 : Contrôle des sorties brutes Noah-MP
Vérifier la conformité des fichiers d'historique bruts issus de la simulation Noah-MP :
```bash
# Vérifier la présence des variables Qs_tavg et Qsb_tavg et les dimensions (121, 181)
ncdump -h /path/to/noahmp_new_exp/output/201601/LIS_HIST_201601020000.d01.nc | grep -E "Qs_tavg|Qsb_tavg|east_west|north_south"
```
*Critère de passage :* Dimensions `east_west = 181`, `north_south = 121`, unités en `kg m-2 s-1`.

#### Étape 2 : Création et exécution du script de rééchantillonnage
Le script `remap_runoff_new_exp.py` n'existe pas par défaut ; il doit être créé par copie d'un script existant :
```bash
cp scripts/remap_runoff_opl.py scripts/remap_runoff_new_exp.py
```
Dans `scripts/remap_runoff_new_exp.py`, modifier les chemins sources et cibles :
```python
src_base = "/path/to/noahmp_new_exp/output"
dst_base = "experiments/NorthMor/routing/runoff_remap_180x120/NEW_EXP/SURFACEMODEL"
```
Lancer le rééchantillonnage :
```bash
python3 scripts/remap_runoff_new_exp.py
```
*Critère de passage :* Exactement **1 828 fichiers NetCDF journaliers** générés sous `runoff_remap_180x120/NEW_EXP/SURFACEMODEL/YYYYMM/`, de dimensions `(120, 180)`. Présence indispensable du fichier frontière terminal `LIS_HIST_202101020000.d01.nc`.

#### Étape 3 : Configuration et lancement du Spin-up Cycle 1 (C1)
Créer la configuration C1 à partir du modèle OPL :
```bash
cp configs/lis_hymap2_opl_spinup_c1_corrigee.config configs/lis_hymap2_new_exp_spinup_c1.config
```
Adapter les directives dans `configs/lis_hymap2_new_exp_spinup_c1.config` :
```ini
Surface model output forcing directory: ./runoff_remap_180x120/NEW_EXP/SURFACEMODEL
Output directory:                       ./output/NEW_EXP_spinup_c1
HYMAP routing model restart file:       none
```
Créer et soumettre le job SLURM :
```bash
sbatch jobs/run_hymap2_new_exp_spinup_c1.sh
```
*Critère de passage :* Fin normale (SLURM COMPLETED), présence du restart `output/NEW_EXP_spinup_c1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc` (> 1 Mo).

#### Étape 4 : Configuration et lancement du Spin-up Cycle 2 (C2)
Créer la configuration C2 :
```bash
cp configs/lis_hymap2_opl_spinup_c2_corrigee.config configs/lis_hymap2_new_exp_spinup_c2.config
```
Adapter les directives dans `configs/lis_hymap2_new_exp_spinup_c2.config` :
```ini
Surface model output forcing directory: ./runoff_remap_180x120/NEW_EXP/SURFACEMODEL
Output directory:                       ./output/NEW_EXP_spinup_c2
HYMAP routing model restart file:       ./output/NEW_EXP_spinup_c1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc
```
Lancer le calcul SLURM C2 :
```bash
sbatch jobs/run_hymap2_new_exp_spinup_c2.sh
```
*Critère de passage :* Dérive relative du stock souterrain $BSFSTO$ :
$$\Delta S = rac{|BSFSTO_{C2} - BSFSTO_{C1}|}{BSFSTO_{C1}} 	imes 100 < 1.0\%$$
Présence du restart certifié : `output/NEW_EXP_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`.

#### Étape 5 : Exécution de la Production Quinquennale (2016–2020)
Créer la configuration de production :
```bash
cp configs/lis_hymap2_opl_2016_2020_corrigee.config configs/lis_hymap2_new_exp_2016_2020.config
```
Adapter les directives :
```ini
Ending year:                            2021
Ending month:                           01
Ending day:                             01
Ending hour:                            00
Surface model output forcing directory: ./runoff_remap_180x120/NEW_EXP/SURFACEMODEL
Output directory:                       ./output/NEW_EXP_2016_2020
HYMAP routing model restart file:       ./output/NEW_EXP_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc
```
Lancer la simulation :
```bash
sbatch jobs/run_hymap2_new_exp_2016_2020.sh
```
*Critère de passage :* **1 827 fichiers NetCDF journaliers** produits sous `output/NEW_EXP_2016_2020/ROUTING/YYYYMM/LIS_HIST_YYYYMMDD0000.d01.nc`.

#### Étape 6 : Adaptation d'extract_streamflow.py et Extraction
Le script actuel `extract_streamflow.py` possède un dictionnaire `EXPERIMENT_CONFIGS` configuré pour `opl`, `nocdf` et `cdf`.
Pour intégrer `new_exp`, ajouter l'entrée suivante dans le script :
```python
EXPERIMENT_CONFIGS["new_exp"] = {
    "name": "Expérience NEW_EXP",
    "output_sub": "output/NEW_EXP_2016_2020",
    "cache_file": "sim_daily_12stations_new_exp.csv",
}
```
Puis exécuter l'extraction :
```bash
python3 scripts/extract_streamflow.py --experiment new_exp
```
*Critère de passage :* Fichier CSV créé avec 1 827 lignes et 12 stations sans lacune.

#### Étape 7 : Adaptation d'evaluate_sebou_bouregreg.py et Évaluation
Le script `evaluate_sebou_bouregreg.py` actuel est conçu pour comparer 3 expériences. Pour évaluer une 4ᵉ expérience :
- Charger le nouveau cache CSV dans le script.
- Adapter les calculs de métriques KGE, NSE, PBIAS et la génération des figures à 4 courbes.

---

### 11.3 Checklist Complète de Reproduction

| Étape | Fichiers d'entrée | Commande / Action | Sorties attendues | Critère de passage |
| :---: | :--- | :--- | :--- | :---: |
| **1** | NetCDF bruts Noah-MP | `ncdump -h <sample.nc>` | Métadonnées vérifiées | Variables `Qs_tavg`, `Qsb_tavg`, grille $181 	imes 121$ |
| **2** | NetCDF Noah-MP bruts | Créer et lancer `remap_runoff_new_exp.py` | `runoff_remap_180x120/NEW_EXP/` | **1 828 fichiers** NetCDF |
| **3** | Forçages C1 | Configurer et lancer job C1 | `output/NEW_EXP_spinup_c1/` | Job COMPLETED, Restart C1 > 1 Mo |
| **4** | Forçages C2 + Restart C1 | Configurer et lancer job C2 | `output/NEW_EXP_spinup_c2/` | **$\Delta S < 1.0\%$** sur $BSFSTO$ |
| **5** | Forçages 5 ans + Restart C2 | Configurer et lancer job 5 ans | `output/NEW_EXP_2016_2020/` | **1 827 fichiers** NetCDF journaliers |
| **6** | Sorties NetCDF 5 ans | Adapter et lancer `extract_streamflow.py` | `sim_daily_12stations_new_exp.csv` | **1 828 lignes** (header+1827) |
| **7** | Cache CSV + Obs ABH | Adapter et lancer `evaluate_sebou_bouregreg.py` | Tableaux et figures KGE/NSE | Métriques calculées sur les 5 stations |

---

### 11.4 Diagnostic des Pannes Courantes

1. **Erreur : "End of file / missing forcing file LIS_HIST_202101020000.d01.nc"**
   - *Cause :* Le dossier de forçage contient 1 827 fichiers au lieu de 1 828.
   - *Solution :* Cloner le fichier du 01/01/2021 : `cp LIS_HIST_202101010000.d01.nc LIS_HIST_202101020000.d01.nc`.
2. **Erreur : "Accumulation anormale de milliards de m³ dans BSFSTO"**
   - *Cause :* La configuration LIS pointe vers `lis_input.d01.nc` brut au lieu de `lis_input_corrigee.d01.nc`.
   - *Solution :* Vérifier la directive `HYMAP routing parameter file: ./ldt_hymap/lis_input_corrigee.d01.nc`.
3. **Erreur : "Restart file not found upon launching Cycle C2 or Production"**
   - *Cause :* Chemin du restart erroné dans `lis.config`.
   - *Solution :* Vérifier le chemin sous `output/<EXP>_spinup/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`.
4. **Erreur : "Argument --experiment: invalid choice 'new_exp'"**
   - *Cause :* `extract_streamflow.py` n'a pas été mis à jour avec la nouvelle clé.
   - *Solution :* Ajouter `'new_exp'` dans `EXPERIMENT_CONFIGS` et dans `choices` de `parser.add_argument`.

---

## 12. Annexe : Technical Questions for Augusto Getirana (NASA GSFC)

This annex summarizes prioritized, evidence-based technical questions for Augusto Getirana regarding the HyMAP2 parameterization on the North Morocco domain.

### Priority 1: Native Units, Physical Meaning, and Dimensioning of `tbasflw`
- **What was observed:** In `lis_tbasflw_005.bin` (`lis_param.tar.gz`), values range from 10,800 to 86,400 (mean: ~61,703). In LISF 7.3 (`HYMAP2_modelMod.F90`, line 112), baseflow discharge is formulated as:
  $$Q_{bas} = rac{S_{bas}}{tbsflw \cdot 86\,400}$$
  which explicitly assumes `tbsflw` is in days. When using the raw parameter grid, the denominator multiplies 61,703 by 86,400, resulting in a 169-year residence time, $+16\,518	ext{ hm}^3$ groundwater accumulation, and a streamflow collapse.
- **What was already verified:** Dividing `tbsflw` by 86,400 in `lis_input_corrigee.d01.nc` brings values between 0.0024 and 30.46 days (mean 0.714 day). However, in `HYMAP2_routingMod.F90` (lines 1264–1267), the code enforces:
  ```fortran
  where(tbsflw < cntime/86400. .and. cntime > 0) tbsflw = cntime/86400.
  ```
  Since the spatial median of `cntime/86400.` is 2.45 days (ranging from 0.21 to 100.98 days across cells), this numerical floor triggers across **99.90% of active grid cells** (15,921 / 15,937 cells), effectively imposing an effective mean residence time of 3.77 days (spatial median 2.45 days) and closing the water balance to $99.965\%$.
- **What remains uncertain:**
  - The value of 2.45 days represents the spatial median of the effective concentration time, and not a uniform threshold across cells.
  - The numerical closure of the mass balance does not demonstrate the physical validity of the effective drainage time.
  - The native units and calibration intent of the original data provided by Augusto remain to be confirmed. Furthermore, because the floor overrides 99.90% of cells, the spatial heterogeneity of the aquifer parameterization is flattened.
- **Precise question for Augusto:**
  > *Could you confirm the intended physical units of `lis_tbasflw_005.bin` (seconds vs. days)? In standard LISF 7.3, is `HYMAP_baseflow_time_delay` expected in days, and what physical parameterization/calibration was originally targeted for groundwater residence times across North Morocco?*

---

### Priority 2: Definition and Sub-Grid Allocation of `lis_grarea_005.bin`
- **What was observed:** In `lis_grarea_005.bin` (`HYMAP_grid_area`), cell areas range from $0.022	ext{ km}^2$ to **$178.9	ext{ km}^2$**, with over 3,020 cells exceeding $40	ext{ km}^2$ and 151 exceeding $100	ext{ km}^2$.
- **What was already verified:** In `HYMAP2_model_core.F90` (lines 211–212), `grarea` (in $	ext{m}^2$) converts specific runoff ($kg \cdot m^{-2} \cdot s^{-1} \equiv mm/s$) into volumetric flow ($m^3/s$): `runoff1 = runoff1 * grarea / 1e3`. It is also used to convert water storage into surface water depth: `surfws = 1e3 * (rivsto + fldsto) / grarea`. The spatial domain mean on active cells is **$25.530	ext{ km}^2$**, consistent with the theoretical ellipsoidal cell area for a $0.05^\circ$ grid ($25.6	ext{ km}^2$), thus preserving domain-wide mass conservation.
- **What remains uncertain:** While the domain mean of $25.53	ext{ km}^2$ is consistent with domain geometry, it does not validate the spatial distribution alone. We have no documentation or source code confirming the exact upscaling or delineation algorithm used in the provided dataset. This distribution should not be assumed to originate from a proven MERIT-Hydro subgrid redistribution without explicit verification.
- **Precise question for Augusto:**
  > *Could you clarify the derivation and detailed provenance of `lis_grarea_005.bin`? What method or algorithm was used to construct this grid, and how should local values ranging up to $178.9	ext{ km}^2$ (with a domain mean of $25.53	ext{ km}^2$) be interpreted in terms of subgrid catchment contribution to river cells?*

---

### Priority 3: Baseflow Recession Physics and Persistent Minimum Low Flows
- **What was observed:** Semi-arid wadis in the Sebou and Bouregreg basins frequently experience complete dry-up ($Q_{	ext{obs}} = 0.0	ext{ m}^3/	ext{s}$) during summer low-flow periods. In contrast, simulated streamflows remain strictly positive during certain dry periods (e.g., simulated median of $1.88	ext{ m}^3/	ext{s}$ vs. observed median of $0.41	ext{ m}^3/	ext{s}$ at Sidi Jabeur).
- **What was already verified:** Source code inspection confirms the absence of any explicit constraint or parameter imposing a minimum streamflow ($Q_{min} > 0$). The baseflow equation ($Q_{bas} = S_{bas}/	au$) naturally tends to zero as storage empties.
- **Hypotheses and uncertainties:** Possible explanations include continuous sub-surface drainage contributions ($Q_{sb}$) simulated by Noah-MP and unrepresented channel transmission losses (riverbed infiltration, bank storage, riparian evapotranspiration). However, the phenomenon cannot be causally attributed to $Q_{sb}$ without verified daily flux analysis during these low-flow periods.
- **Precise question for Augusto:**
  > *Does HyMAP2 include a native mechanism or recommended parameterization (e.g., channel transmission losses or bed infiltration) to realistically simulate zero-flow periods and ephemeral wadi dry-up in semi-arid environments?*

---

### Priority 4: Sub-Grid Drainage Delineation Biases in Steep Headwaters
- **What was observed:** At upstream mountain stations in the Middle Atlas, HyMAP2's accumulated upstream area (`HYMAP_drain_area`) significantly underestimates official catchment areas (e.g., **$-32.1\%$** at Pont de Mdez: $2\,331	ext{ km}^2$ modeled vs. $3\,435	ext{ km}^2$ official; **$-48.3\%$** at Ras El Ma). Downstream stations match within $\pm 2\%$.
- **What was already verified:** This discrepancy stems from the automated D8 flow direction upscaling from MERIT-Hydro (3") to $0.05^\circ$, which clips incised headwater valleys into adjacent cells.
- **What remains uncertain:** Whether manual stream-burning or hydrologically conditioned direction corrections are recommended for this region.
- **Precise question for Augusto:**
  > *Was the $0.05^\circ$ drainage direction map generated via automated D8 upscaling, and do you recommend manual flow-direction conditioning or higher-resolution routing ($0.01^\circ$) to preserve steep headwater catchment boundaries in the Atlas mountains?*

---

### Priority 5: Groundwater Storage Spin-up Duration and Convergence Criteria
- **What was observed:** With our two-cycle spin-up protocol on year 2016 (C1 coldstart + C2 hotstart), the alluvial aquifer storage (`BSFSTO`) converges with high numerical stability ($\Delta S < 0.15\%$).
- **What was already verified:** Under the current linear reservoir formulation ($Q_{bas} = S_{bas} / 	au_{eff}$) and with $	au_{eff}$ constrained by the concentration time floor ($2.45	ext{ days}$ spatial median), groundwater storage equilibrates within two annual cycles. However, this numerical stability does not demonstrate physical equilibration of deep or regional groundwater systems.
- **What remains uncertain:** What duration and convergence criteria are recommended to guarantee that HyMAP2 subsurface storages are properly equilibrated in semi-arid regimes, particularly given the current linear reservoir formulation and effective residence time floor.
- **Precise question for Augusto:**
  > *Given the current linear reservoir formulation and the effective concentration time floor, what spin-up duration and convergence criteria do you recommend for HyMAP2 groundwater storage equilibration in semi-arid regions?*

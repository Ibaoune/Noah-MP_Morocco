# Audit Technique et Bilan de Masse : Rééchantillonnage du Ruissellement Noah-MP vers HyMAP

**Date :** 30 octobre 2026  
**Branche Git :** `hymap-routing` (HEAD : `3ec082f`)  
**Fichiers de référence :** [`experiments/NorthMor/routing/README_HYMAP.md`](../README_HYMAP.md)  
**Tâches associées :** TASK 03A, TASK 03B, TASK 03C, TASK 03D, TASK 03E, TASK 03F, TASK 03G  

---

## 1. Contexte et Objectifs de l'Audit

Dans la chaîne de modélisation hydrologique LIS, les simulations de surface Noah-MP (expériences Open-Loop `OPL` et assimilation d'humidité du sol `DA-NoCDF`) génèrent deux flux journaliers moyennés dans le temps :
- `Qs_tavg` : ruissellement de surface (*surface runoff amount*, $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$)
- `Qsb_tavg` : drainage ou débit de base sous-surfacique (*subsurface runoff amount*, $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$)

Ces flux sont calculés sur une grille de $181 \times 121$ nœuds et doivent être transférés vers la grille de routage HyMAP2 de $180 \times 120$ mailles. L'audit a pour objectif de vérifier :
1. La formulation mathématique et le traitement des frontières du rééchantillonnage.
2. La quasi-conservation du volume d'eau intégré sur le domaine ($S_2/S_1 \approx 100.0002\%$) sur l'emprise géographique commune sous les hypothèses géométriques centrées sur la maille, ainsi que la distinction fondamentale entre le support physique des colonnes et la coïncidence nodale.
3. L'impact du filtrage par le masque de bassin HyMAP et l'évaluation du volume diagnostique $S_4$ obtenu par application de la carte de surface `HYMAP_grid_area` (`grarea`).
4. La convention temporelle exacte des fichiers d'historique LISF (`SURFACEMODEL`) et le bilan annuel physique sur l'année civile 2018.

---

## 2. Scripts de Production et Traçabilité des Données

Le transfert opérationnel des flux de ruissellement pour les 5 années de simulation (2016–2020) a été assuré par deux scripts Python dédiés :

| Expérience | Script de production historique | Répertoire source des sorties Noah-MP | Répertoire cible rééchantillonné |
| :--- | :--- | :--- | :--- |
| **Open-Loop (OL)** | [`experiments/NorthMor/routing/scripts/remap_opl_2016_2020.py`](../scripts/remap_opl_2016_2020.py) | `experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/` | `experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL/` |
| **DA NoCDF** | [`experiments/NorthMor/routing/scripts/remap_da_nocdf_2016_2020.py`](../scripts/remap_da_nocdf_2016_2020.py) | `experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/` | `experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL/` |

### 2.1 Organisation et inventaire des fichiers
- **Arborescence mensuelle :** Les fichiers cibles sont ventilés en sous-dossiers mensuels `YYYYMM/` sous le répertoire `SURFACEMODEL/`.
- **Volume produit :** Exactement **1 828 fichiers NetCDF journaliers** par expérience.
- **Rôle du 1 828ᵉ fichier (`LIS_HIST_202101020000.d01.nc`) :** La période de simulation continue couvre 1 827 jours (du 2016-01-01 au 2021-01-01 à 00:00:00 UTC). Lors du dernier jour simulé, le pilote d'interpolation temporelle de LIS (`readLISrunoffdata.F90`) tente d'encadrer l'intervalle sub-journalier (pas de 15 min) en lisant le fichier du jour suivant `202101020000`. Les scripts de production ont cloné `LIS_HIST_202101010000.d01.nc` vers `LIS_HIST_202101020000.d01.nc` pour servir de **fichier frontière terminal** (*padding file*) évitant l'arrêt prématuré de LIS. Ce fichier n'ajoute pas de 6ᵉ année de simulation.

---

## 3. Grilles, Coordonnées et Formulation du Rééchantillonnage

### 3.1 Définition des grilles source et cible

| Caractéristique | Grille source Noah-MP | Grille cible HyMAP |
| :--- | :---: | :---: |
| **Dimensions ($N_x \times N_y$)** | $181 \times 121$ ($21\,901$ points) | $180 \times 120$ ($21\,600$ points) |
| **Projection cartographique** | Cylindrique équidistante (Plate Carrée) | Cylindrique équidistante (Plate Carrée) |
| **Résolution angulaire ($\Delta\lambda, \Delta\phi$)** | $0.05^\circ \times 0.05^\circ$ | $0.05^\circ \times 0.05^\circ$ |
| **Origine Sud-Ouest (`SOUTH_WEST_CORNER`)** | Lat: $30.00^\circ\text{N}$, Lon: $-10.00^\circ\text{E}$ | Lat: $30.025^\circ\text{N}$, Lon: $-9.975^\circ\text{E}$ |
| **Coordonnées `lat` stockées** | $30.00, 30.05, \dots, 36.00^\circ\text{N}$ ($121$ valeurs) | $30.025, 30.075, \dots, 35.975^\circ\text{N}$ ($120$ valeurs) |
| **Coordonnées `lon` stockées** | $-10.00, -9.95, \dots, -1.00^\circ\text{E}$ ($181$ valeurs) | $-9.975, -9.925, \dots, -1.025^\circ\text{E}$ ($180$ valeurs) |
| **Nature du repérage** | Nœuds entiers (sommets) | Centres de mailles |
| **Limites du domaine physique** | $[29.975^\circ, 36.025^\circ]\text{N} \times [-10.025^\circ, -0.975^\circ]\text{E}$ | $[30.000^\circ, 36.000^\circ]\text{N} \times [-10.000^\circ, -1.000^\circ]\text{E}$ |
| **Surface géométrique totale** ($R=6371\text{ km}$) | $565\,911.39\text{ km}^2$ | $559\,723.32\text{ km}^2$ |

### 3.2 Formule de rééchantillonnage aux quatre nœuds
Le rééchantillonnage repose sur l'hypothèse opérationnelle que les coordonnées de la grille $181 \times 121$ constituent géométriquement les sommets des mailles cibles de la grille $180 \times 120$. Chaque maille cible $(j, i)$ reçoit la moyenne arithmétique de ses quatre sommets :
$$\bar{q}[j, i] = \frac{1}{4} \Big( q[j, i] + q[j, i+1] + q[j+1, i] + q[j+1, i+1] \Big)$$

Implémentation dans `remap_opl_2016_2020.py` :
```python
qs_dst = 0.25 * (qs_clean[:-1, :-1] + qs_clean[:-1, 1:] +
                 qs_clean[1:, :-1] + qs_clean[1:, 1:])
qsb_dst = 0.25 * (qsb_clean[:-1, :-1] + qsb_clean[:-1, 1:] +
                  qsb_clean[1:, :-1] + qsb_clean[1:, 1:])
```

**Distinction entre support physique et coïncidence géométrique :**  
Il importe de distinguer formellement le support physique des colonnes de surface Noah-MP (volumes de contrôle finis générant localement du ruissellement) de la simple coïncidence géométrique nodale de leurs coordonnées avec les sommets des mailles cibles HyMAP. L'opération ci-dessus constitue une interpolation nodale de l'intensité surfacique de flux ($[\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}]$) et n'équivaut pas à un remaillage conservatif direct de cellule à cellule fondé sur l'intersection géométrique exacte des polygones sources et cibles.

---

## 4. Traitement des Masques, Valeurs Négatives et Zones Côtières

### 4.1 Nettoyage des valeurs négatives et océaniques
Dans les sorties brutes Noah-MP, les mailles océaniques non simulées portent la valeur manquante `_FillValue = -9999.0f`.
Le script applique :
```python
qs_clean = np.where((qs_src < 0) | np.isnan(qs_src), 0.0, qs_src)
qsb_clean = np.where((qsb_src < 0) | np.isnan(qsb_src), 0.0, qsb_src)
```
- Toutes les valeurs manquantes et éventuels flux négatifs sont convertis inconditionnellement en `0.0`.
- Les fichiers cibles résultants sont écrits sous forme de tableaux denses 2D continus **sans aucun masque appliqué** (0 valeur manquante).

### 4.2 Dilution côtière et diffusion littorale
Lorsqu'une maille cible se situe sur le trait de côte, elle borde à la fois des nœuds continentaux actifs et des nœuds marins mis à zéro. Pour une maille ayant 2 sommets terrestres ($q_1, q_2$) et 2 sommets marins ($0, 0$) :
$$\bar{q} = \frac{q_1 + q_2 + 0 + 0}{4} = 0.5 \times \left( \frac{q_1 + q_2}{2} \right)$$
L'intensité du flux continental est diluée de moitié, mais étalée sur toute la surface de la maille littorale.
Par conséquent, le nombre de mailles cibles présentant un flux strictement positif ($16\,071$ mailles pour le débit de base) dépasse le nombre de mailles continentales actives de la grille cible (`LANDMASK == 1`, $15\,888$ mailles).

### 4.3 Concordance et discordance des masques cible
La comparaison croisée des masques dans le fichier de paramètres HyMAP [`experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc`](../ldt_hymap/lis_input.d01.nc) révèle la distribution suivante sur les 21 600 mailles :

| Catégorie | `LANDMASK` | `HYMAP_basin_mask` | Nombre de mailles | Surface géométrique | Devenir dans HyMAP |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Terre active routée** | `1.0` | `1.0` | **$15\,839$** | $413\,239.28\text{ km}^2$ | Routée normalement |
| **Mer côtière routée** | `0.0` | `1.0` | **$98$** | $2\,523.07\text{ km}^2$ | **Injectée dans le réseau hydrographique** ($10.59\text{ hm}^3$ en 2018 OPL) |
| **Terre inactive (valeur 0)** | `1.0` | `0.0` | **$38$** | $985.34\text{ km}^2$ | **Exclue du routage** (perdue pour le réseau) |
| **Terre inactive (nodata)** | `1.0` | `-9999.0` | **$11$** | $283.18\text{ km}^2$ | **Exclue du routage** (perdue pour le réseau) |
| **Océan concordant** | `0.0` | `0.0` ou `-9999.0` | **$5\,614$** | $142\,692.45\text{ km}^2$ | Non routé |

*Total des discordances de masques :* **136 mailles** hors nodata ($98 + 38$), **147 mailles** nodata inclus ($98 + 38 + 11$).

*Remarque diagnostique sur les mailles exclues :*  
Sur une journée test estivale particulière (ex. le 2018-07-15), 134 mailles cibles présentant un débit de base positif se trouvent hors du masque actif HyMAP. Ce décompte journalier de mailles ne doit pas être confondu avec le volume annuel total exclu ($184.03\text{ hm}^3$ pour OPL sur l'ensemble de l'année 2018).

---

## 5. Les Quatre Stades d'Évaluation Volumique (S1 à S4)

Pour tracer sans ambiguïté les flux d'eau depuis leur genèse dans Noah-MP jusqu'à leur routage dans HyMAP, quatre définitions volumiques rigoureuses ont été établies :

* **Stade S1 (Volume source sur l'emprise géographique commune) :**
  Intégration du flux source $q_{\text{src}}$ sur le domaine commun $[30.0^\circ, 36.0^\circ]\text{N} \times [-10.0^\circ, -1.0^\circ]\text{E}$ sous l'hypothèse de mailles sources centrées sur leurs coordonnées (*cell-centered*). Les mailles sources internes sont intégrées à $100\%$ de leur surface (poids $1.0$). Les mailles de bordure sont tronquées à leur moitié interne (poids $0.5$) et les quatre mailles de coin à leur quart interne (poids $0.25$).
* **Stade S2 (Volume rééchantillonné géométrique total) :**
  Intégration du flux rééchantillonné $\bar{q}$ sur l'intégralité des 21 600 mailles cibles à l'aide de leur surface géométrique sphérique exacte ($R=6371\text{ km}$, intervalle $\Delta t = 86\,400\text{ s}$, $\rho = 1000\text{ kg}\cdot\text{m}^{-3}$).
* **Stade S3 (Volume géométrique sur le bassin actif HyMAP) :**
  Intégration de $\bar{q}$ sur les seules **$15\,937$ mailles actives** du réseau hydrographique (`HYMAP_basin_mask == 1`). Les flux tombant sur les 5 663 mailles inactives sont rejetés.
* **Stade S4 (Volume diagnostique via `HYMAP_grid_area`) :**
  Volume diagnostique calculé en appliquant la carte de paramètres `HYMAP_grid_area` (`grarea / 1e3` dans `HYMAP2_model_core.F90`, lignes 210–212) aux flux rééchantillonnés journaliers sur les 15 937 mailles actives du bassin. Ce total constitue une évaluation diagnostique au pas journalier ; il ne doit pas être qualifié de volume exact effectivement intégré par HyMAP au pas sub-journalier (15 minutes) avant audit formel de l'interpolation temporelle et des flux au pas de temps de routage.

---

## 6. Vérification du Code Source LISF et Convention Temporelle

### 6.1 Traçabilité du code source LISF
L'inspection directe de l'arborescence source de LISF (`src/lisf/lis/`) documente précisément l'enchaînement des sous-programmes assurant la production des fichiers d'historique journaliers de surface (`SURFACEMODEL`) :

1. **Incrémentation temporelle (`LIS_ticktime`) :**
   - Au début de chaque pas de temps dans la boucle principale rétrospective (`src/lisf/lis/runmodes/retrospective/retrospective_runMod.F90`, ligne 212), la routine `LIS_ticktime` est appelée avant toute résolution physique.
   - Définie dans `src/lisf/lis/core/LIS_coreMod.F90` (lignes 444–457), elle invoque `LIS_advance_timestep(LIS_rc)` pour faire avancer l'horloge de simulation `LIS_rc%time` d'un pas de temps. L'horodatage courant pointe ainsi vers l'échéance terminale du pas de modélisation.
2. **Accumulation diagnostique temporelle (`diagnoseDataEntry`) :**
   - Durant l'exécution du modèle de surface (`call LIS_surfaceModel_run(n)` dans `retrospective_runMod.F90`, ligne 222), les flux instantanés calculés par le schéma de surface sont transmis au gestionnaire d'historique via la routine `diagnoseDataEntry`.
   - Définie dans `src/lisf/lis/core/LIS_histDataMod.F90` (lignes 6960–7090), cette routine cumule les grandeurs physiques dans l'accumulateur `dataEntry%modelOutput` et incrémente le compteur `dataEntry%count` à chaque pas de temps où le diagnostic est évalué.
3. **Déclenchement de la sortie SURFACEMODEL :**
   - À chaque pas, `retrospective_runMod.F90` appelle `LIS_surfaceModel_output(n)` (ligne 229).
   - Définie dans `src/lisf/lis/core/LIS_surfaceModelMod.F90` (lignes 316–424), cette routine vérifie si l'alarme d'écriture est active via `alarmCheck = LIS_isAlarmRinging(...)` (lignes 373–380). Lorsque l'intervalle de sortie journalier est atteint (à minuit `00:00:00` UTC), l'alarme déclenche la séquence d'écriture.
4. **Génération du nom de fichier et horodatage (`create_output_filename`) :**
   - Dans `LIS_surfaceModelMod.F90` (lignes 386 et 396), LIS crée le sous-répertoire puis appelle `LIS_create_output_filename(n, outfile, model_name = 'SURFACEMODEL', ...)`.
   - L'interface dans `src/lisf/lis/core/LIS_fileIOMod.F90` (lignes 178–181) renvoie à la routine `create_output_filename` (lignes 314–892), qui formate le chemin `SURFACEMODEL/YYYYMM/LIS_HIST_YYYYMMDD0000.d01.nc` à partir de l'heure courante `LIS_rc%time`. Ce nom de fichier porte donc la date de fin de la fenêtre d'intégration journalière.
5. **Écriture NetCDF et normalisation temporelle (`writeNetcdfOutput` & `writeSingleNETCDFvar`) :**
   - `LIS_surfaceModel_output` transmet le contrôle à `LIS_writeModelOutput` dans `src/lisf/lis/core/LIS_historyMod.F90` (lignes 409–590), qui appelle à la ligne 581 la routine `writeNetcdfOutput` (lignes 1955–2310).
   - Pour chaque champ physique, `writeNetcdfOutput` appelle `writeSingleNETCDFvar` (lignes 3032–3146). Pour les flux déclarés en moyenne temporelle (`timeAvgOpt == 1` ou `2`), la normalisation temporelle est effectuée par division vectorielle :
     ```fortran
     ! src/lisf/lis/core/LIS_historyMod.F90 (lignes 3088–3090)
     dataEntry%modelOutput(1,t,k) = dataEntry%modelOutput(1,t,k) / dataEntry%count(t,k)
     ```
     Cette opération ramène l'accumulation brute à la moyenne temporelle exacte des flux sur la période écoulée, exprimée en $\text{kg}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$.
6. **Réinitialisation des variables de sortie (`LIS_resetOutputVars`) :**
   - Dès la fin de l'écriture du fichier NetCDF, le point d'appel à la ligne 589 de `LIS_writeModelOutput` (`src/lisf/lis/core/LIS_historyMod.F90`) invoque la routine `LIS_resetOutputVars(n, group_temp)`.
   - Définie dans `src/lisf/lis/core/LIS_histDataMod.F90` (lignes 7218–7255), elle remet à zéro l'accumulateur `dataEntry%modelOutput` et le compteur `dataEntry%count`, préparant sans biais le cycle d'accumulation des 24 heures suivantes.

> **Règle formelle établie :**  
> Un fichier estampillé `LIS_HIST_YYYYMMDD0000.d01.nc` contient la moyenne temporelle exacte des flux sur les **24 heures qui précèdent** son horodatage (soit du jour civil précédent `YYYY-MM-(DD-1)` de 00:00:00 à 23:59:59 UTC).

### 6.2 Délimitation de l'année civile 2018 physique
Pour agréger rigoureusement l'année civile 2018 (du 2018-01-01 00:00 UTC au 2018-12-31 24:00 UTC), l'échantillon physique des 365 fichiers journaliers est :
- **Premier jour :** `LIS_HIST_201801020000.d01.nc` (moyenne du 2018-01-01).
- **Dernier jour :** `LIS_HIST_201901010000.d01.nc` (moyenne du 2018-12-31).

La sommation par convention « année-nom » (`201801010000` à `201812310000`) inclut le 2017-12-31 et omet le 2018-12-31. La correction physique consiste donc à :
$$\text{Total Physique 2018} = \text{Total Année-Nom} - \text{Jour}(20180101) + \text{Jour}(20190101)$$

---

## 7. Bilans Annuels 2018 et Analyse de Conservation

### 7.1 Volumes annuels physiques corrigés (Année 2018, 365 jours)

*Intervalle physique : du 2018-01-01 00:00 au 2019-01-01 00:00 UTC (fichiers `201801020000` à `201901010000`). Volumes en $\text{hm}^3$.*

| Expérience | Composante | S1 : Source Emprise Commune | S2 : Remap Géom Total | S3 : Bassin Actif Géom | S4 : Volume Diagnostique grarea | Rapport S2/S1 (Quasi-conservation) | Exclusion Masque (S2 - S3) | Rapport S4/S3 (Pondération grarea) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Open-Loop (OL)** | **Ruissellement ($Q_s$)** | $4\,913.72$ | $4\,913.74$ | $4\,788.68$ | $4\,647.43$ | $100.0004\%$ | $125.06\text{ hm}^3$ ($2.54\%$) | $97.05\%$ ($-2.95\%$) |
| | **Débit de base ($Q_{sb}$)** | $6\,691.67$ | $6\,691.67$ | $6\,632.70$ | $6\,333.06$ | $100.0000\%$ | $58.97\text{ hm}^3$ ($0.88\%$) | $95.48\%$ ($-4.52\%$) |
| | **Total ($Q_{\text{tot}}$)** | **$11\,605.39$** | **$11\,605.41$** | **$11\,421.38$** | **$10\,980.49$** | **$100.0002\%$** | **$184.03\text{ hm}^3$ ($1.59\%$)** | **$96.14\%$ ($-3.86\%$)** |
| **DA-NoCDF** | **Ruissellement ($Q_s$)** | $5\,752.44$ | $5\,752.47$ | $5\,620.55$ | $5\,482.30$ | $100.0005\%$ | $131.92\text{ hm}^3$ ($2.29\%$) | $97.54\%$ ($-2.46\%$) |
| | **Débit de base ($Q_{sb}$)** | $13\,907.12$ | $13\,907.14$ | $13\,796.34$ | $13\,517.91$ | $100.0001\%$ | $110.80\text{ hm}^3$ ($0.80\%$) | $97.98\%$ ($-2.02\%$) |
| | **Total ($Q_{\text{tot}}$)** | **$19\,659.57$** | **$19\,659.61$** | **$19\,416.89$** | **$19\,000.21$** | **$100.0002\%$** | **environ $242.7\text{ hm}^3$ ($1.23\%$)** | **$97.85\%$ ($-2.15\%$)** |

*(Note sur la précision numérique de l'exclusion : la différence directe des totaux annuels arrondis au centième donne $19\,659.61 - 19\,416.89 = 242.72\text{ hm}^3$, tandis que la sommation des exclusions par composante donne $131.92 + 110.80 = 242.72\text{ hm}^3$, et que la valeur de $242.71\text{ hm}^3$ apparaissait dans certains bilans intermédiaires. L'ordre de grandeur retenu de façon cohérente est d'environ $242.7\text{ hm}^3$).*

### 7.2 Incréments annuels d'assimilation (DA-NoCDF minus OL)

*Différences en volume ($\Delta = \text{DA} - \text{OL}$) sur l'année civile physique 2018 :*

| Composante | S1 : Source Emprise Commune | S2 : Remap Géom Total | S3 : Bassin Actif Géom | S4 : Volume Diagnostique grarea | Écart Remap (S2 vs S1) | Impact Masque (S3 vs S2) | Écart grarea vs Géom (S4 vs S3) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ruissellement ($\Delta Q_s$)** | $+838.73\text{ hm}^3$ | $+838.74\text{ hm}^3$ | $+831.87\text{ hm}^3$ | $+834.88\text{ hm}^3$ | $+0.01\text{ hm}^3$ | $-6.87\text{ hm}^3$ ($-0.82\%$) | $+3.01\text{ hm}^3$ ($+0.36\%$) |
| **Débit de base ($\Delta Q_{sb}$)** | $+7\,215.45\text{ hm}^3$ | $+7\,215.47\text{ hm}^3$ | $+7\,163.65\text{ hm}^3$ | $+7\,184.84\text{ hm}^3$ | $+0.02\text{ hm}^3$ | $-51.82\text{ hm}^3$ ($-0.72\%$) | $+21.19\text{ hm}^3$ ($+0.30\%$) |
| **Total ($\Delta Q_{\text{tot}}$)** | **$+8\,054.18\text{ hm}^3$** | **$+8\,054.20\text{ hm}^3$** | **$+7\,995.52\text{ hm}^3$** | **$+8\,019.72\text{ hm}^3$** | **$+0.02\text{ hm}^3$** | **$-58.68\text{ hm}^3$ ($-0.73\%$)** | **$+24.20\text{ hm}^3$ ($+0.30\%$)** |

### 7.3 Bilan de la correction aux jours frontières
Comparaison entre l'agrégation brute par nom de fichier (fichiers `20180101` à `20181231`, documentée dans TASK 03D) et l'agrégation physique (fichiers `20180102` à `20190101`) :
- **Jour soustrait (`20180101`, 2017-12-31) :** OL Tot S4 (diagnostique) = $10.17\text{ hm}^3$ ; DA Tot S4 (diagnostique) = $20.77\text{ hm}^3$.
- **Jour ajouté (`20190101`, 2018-12-31) :** OL Tot S4 (diagnostique) = $13.27\text{ hm}^3$ ; DA Tot S4 (diagnostique) = $40.70\text{ hm}^3$.
- **Déplacement net :** OL Total S4 $+3.10\text{ hm}^3$ ($+0.028\%$) ; DA Total S4 $+19.93\text{ hm}^3$ ($+0.105\%$) ; incrément $\Delta(\text{DA}-\text{OL})$ $+16.83\text{ hm}^3$ ($+0.21\%$).
- La correction aux frontières ne modifie aucune conclusion scientifique : la quasi-conservation S2/S1 reste d'environ **$100.0002\%$**.

---

## 8. Profil Mensuel et Attribution Spatiale Altimétrique (Diagnostic TASK 03D, Convention Année-Nom 2018)

> [!IMPORTANT]
> **Avertissement méthodologique (Convention Année-Nom / TASK 03D) :**  
> Les tableaux mensuels (Section 8.1) et les résultats par tranche d'altitude (Section 8.2) présentés ci-après sont des **diagnostics issus de TASK 03D basés sur la convention année-nom de fichier** (sommation des fichiers journaliers datés `20180101` à `20181231`).  
> **Ils ne constituent pas des analyses corrigées sur l'année civile physique** (qui nécessiterait la fenêtre physique `20180102` à `20190101` démontrée en TASK 03E). Ils ne doivent en aucun cas être requalifiés de bilans civils physiques corrigés, et aucune valeur mensuelle ou altimétrique corrigée n'a été extrapolée ou inventée.

### 8.1 Ventilation mensuelle du volume total (Diagnostic TASK 03D, convention année-nom, $Q_{\text{tot}}$ en $\text{hm}^3$)

| Mois (dossier) | OL S1 | OL S2 | OL S3 | OL S4 (diag.) | DA S1 | DA S2 | DA S3 | DA S4 (diag.) | DA - OL (S1) | DA - OL (S4 diag.) | S2 / S1 (%) | Exclusion S2-S3 | S4 / S3 (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Janvier (01)** | $811.90$ | $811.90$ | $793.97$ | $763.53$ | $1\,544.95$ | $1\,544.94$ | $1\,521.65$ | $1\,494.22$ | $+733.05$ | $+730.69$ | $100.0003\%$ | $17.93\text{ hm}^3$ | $96.17\%$ |
| **Février (02)** | $639.26$ | $639.26$ | $628.43$ | $604.78$ | $1\,600.54$ | $1\,600.55$ | $1\,583.07$ | $1\,568.57$ | $+961.28$ | $+963.79$ | $100.0003\%$ | $10.83\text{ hm}^3$ | $96.24\%$ |
| **Mars (03)** | $1\,734.19$ | $1\,734.19$ | $1\,691.81$ | $1\,603.11$ | $3\,989.98$ | $3\,989.99$ | $3\,930.28$ | $3\,836.39$ | $+2\,255.80$ | $+2\,233.27$ | $100.0002\%$ | $42.38\text{ hm}^3$ | $94.76\%$ |
| **Avril (04)** | $1\,865.52$ | $1\,865.53$ | $1\,836.88$ | $1\,752.41$ | $2\,935.53$ | $2\,935.54$ | $2\,898.74$ | $2\,815.45$ | $+1\,070.01$ | $+1\,063.04$ | $100.0001\%$ | $28.65\text{ hm}^3$ | $95.40\%$ |
| **Mai (05)** | $1\,089.80$ | $1\,089.80$ | $1\,079.31$ | $1\,035.81$ | $1\,525.12$ | $1\,525.13$ | $1\,511.46$ | $1\,469.21$ | $+435.32$ | $+433.40$ | $100.0001\%$ | $10.50\text{ hm}^3$ | $95.97\%$ |
| **Juin (06)** | $693.24$ | $693.24$ | $686.84$ | $655.76$ | $849.93$ | $849.93$ | $842.29$ | $815.87$ | $+156.69$ | $+160.11$ | $100.0001\%$ | $6.40\text{ hm}^3$ | $95.48\%$ |
| **Juillet (07)** | $583.08$ | $583.08$ | $578.38$ | $554.61$ | $678.83$ | $678.83$ | $673.37$ | $654.57$ | $+95.75$ | $+99.96$ | $100.0001\%$ | $4.70\text{ hm}^3$ | $95.89\%$ |
| **Août (08)** | $638.40$ | $638.41$ | $634.04$ | $616.53$ | $716.58$ | $716.58$ | $711.59$ | $699.18$ | $+78.17$ | $+82.65$ | $100.0002\%$ | $4.37\text{ hm}^3$ | $97.24\%$ |
| **Septembre (09)**| $721.47$ | $721.47$ | $715.41$ | $699.72$ | $796.59$ | $796.59$ | $790.00$ | $780.23$ | $+75.12$ | $+80.51$ | $100.0003\%$ | $6.06\text{ hm}^3$ | $97.81\%$ |
| **Octobre (10)** | $1\,275.06$ | $1\,275.07$ | $1\,252.19$ | $1\,227.18$ | $1\,372.01$ | $1\,372.02$ | $1\,348.67$ | $1\,330.38$ | $+96.95$ | $+103.20$ | $100.0004\%$ | $22.87\text{ hm}^3$ | $98.00\%$ |
| **Novembre (11)** | $1\,098.97$ | $1\,098.97$ | $1\,074.26$ | $1\,037.49$ | $1\,838.49$ | $1\,838.49$ | $1\,808.96$ | $1\,772.58$ | $+739.52$ | $+735.09$ | $100.0004\%$ | $24.71\text{ hm}^3$ | $96.58\%$ |
| **Décembre (12)** | $451.19$ | $451.19$ | $446.59$ | $426.44$ | $1\,790.34$ | $1\,790.34$ | $1\,776.32$ | $1\,743.63$ | $+1\,339.16$ | $+1\,317.18$ | $100.0002\%$ | $4.60\text{ hm}^3$ | $95.49\%$ |

### 8.2 Test d'attribution spatiale par tranche d'altitude (Diagnostic TASK 03D, convention année-nom 2018)

Pour examiner la sensibilité spatiale de la pondération par `HYMAP_grid_area` et vérifier comment elle modifie localement la conversion des flux en volumes selon le relief, les flux annuels (convention année-nom 2018) ont été partitionnés par tranches d'altitude à partir du champ `HYMAP_grid_elevation` sur les 15 937 mailles actives du bassin :

| Tranche d'altitude | Mailles actives | Surface Géom. ($\text{km}^2$) | Surface `grarea` ($\text{km}^2$) | Rapport `grarea` / Géom | Volume Géom. $\Delta Q_{sb}$ ($\text{hm}^3$) | Volume Diagnostique `grarea` $\Delta Q_{sb}$ ($\text{hm}^3$) | Écart relatif S4 vs Géom sur $\Delta Q_{sb}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Plaines ($< 200\text{ m}$)** | $2\,007$ | $51\,538.2$ | $52\,076.6$ | **$1.0104$** | $1\,376.81$ | $1\,530.92$ | **$+11.19\%$ (Pondération plus forte)** |
| **Collines ($200 - 500\text{ m}$)** | $2\,337$ | $60\,515.2$ | $63\,078.5$ | **$1.0424$** | $2\,384.52$ | $2\,573.16$ | **$+7.91\%$ (Pondération plus forte)** |
| **Moyenne montagne ($500 - 1000\text{ m}$)** | $6\,008$ | $157\,881.8$ | $158\,216.9$ | **$1.0021$** | $2\,921.96$ | $2\,729.14$ | **$-6.60\%$ (Pondération plus faible)** |
| **Haute montagne ($\ge 1000\text{ m}$)** | $5\,585$ | $145\,827.2$ | $133\,503.1$ | **$0.9155$** | $462.98$ | $334.66$ | **$-27.72\%$ (Pondération plus faible)** |
| **Total Bassin Actif** | **$15\,937$** | **$415\,762.4$** | **$406\,875.0$** | **$0.9786$** | **$7\,146.27$** | **$7\,167.88$** | **$+0.30\%$ (Quasi-neutre au total)** |

#### Enseignements scientifiques majeurs :
1. **Décomposition de l'effet de pondération `grarea` par tranche altimétrique :**  
   L'application de la surface de maille `HYMAP_grid_area` (`grarea`) en lieu et place de la surface géométrique sphérique modifie la conversion locale des flux en volumes selon les quatre bandes d'altitude du bassin actif :
   - **Plaines ($< 200\text{ m}$) :** contribution de **$+154.11\text{ hm}^3$** ($1\,530.92$ vs $1\,376.81\text{ hm}^3$, pondération accrue de $+11.19\%$).
   - **Collines ($200 - 500\text{ m}$) :** contribution de **$+188.64\text{ hm}^3$** ($2\,573.16$ vs $2\,384.52\text{ hm}^3$, pondération accrue de $+7.91\%$).
   - **Moyenne montagne ($500 - 1000\text{ m}$) :** contribution de **$-192.82\text{ hm}^3$** ($2\,729.14$ vs $2\,921.96\text{ hm}^3$, pondération réduite de $-6.60\%$).
   - **Haute montagne ($\ge 1000\text{ m}$) :** contribution de **$-128.32\text{ hm}^3$** ($334.66$ vs $462.98\text{ hm}^3$, pondération réduite de $-27.72\%$).
   - **Total Bassin Actif :** solde net de **$+21.61\text{ hm}^3$** ($7\,167.88$ vs $7\,146.27\text{ hm}^3$, écart global de $+0.30\%$).
2. **Compensation statistique à l'échelle du domaine :**  
   Le cumul des sous-pondérations en moyenne et haute montagne ($-192.82 - 128.32 = -321.14\text{ hm}^3$) compense presque exactement le cumul des surpondérations en plaine et collines ($+154.11 + 188.64 = +342.75\text{ hm}^3$). Cette compensation explique pourquoi l'incrément annuel global d'assimilation $\Delta Q_{sb}$ calculé avec `grarea` reste à $+0.30\%$ près de sa valeur géométrique.
3. **Absence de transfert physique :**  
   Il est fondamental de rappeler que `grarea` ne déplace aucunement d'eau physiquement entre tranches altimétriques. Elle modifie uniquement le coefficient multiplicateur local de conversion flux-volume au droit de chaque maille.

---

## 9. Quasi-Conservation Volumique vs Préservation de la Distribution Spatiale

L'audit met en évidence une distinction conceptuelle fondamentale entre bilan volumique global et distribution spatiale :

1. **Quasi-conservation volumique globale sur l'emprise commune :**  
   Le diagnostic annuel 2018 montre une quasi-conservation du volume intégré sur le domaine ($S_2/S_1$ d'environ $100.0002\%$) sur l'emprise géographique commune $[30.0^\circ, 36.0^\circ]\text{N} \times [-10.0^\circ, -1.0^\circ]\text{E}$, sous les hypothèses géométriques centrées sur la maille (*The annual 2018 diagnostic shows near-conservation of the domain-integrated volume (S2/S1 approximately 100.0002%) over the common geographic footprint, under the stated cell-centered geometric assumptions*).  
   L'intégration surfacique discrète affecte un poids de 1.0 aux nœuds internes, 0.5 aux nœuds de bordure et 0.25 aux 4 coins, ce qui correspond géométriquement à la troncature d'un domaine polygonal partagé.  
   Toutefois, il convient de **distinguer le support physique des colonnes de surface Noah-MP** (volumes de contrôle finis générant localement du ruissellement) **de leur simple coïncidence géométrique nodale** avec les sommets des mailles cibles HyMAP. Cette quasi-équivalence globale n'est pas une propriété universelle et elle **n'implique pas la préservation exacte des flux à l'échelle des sous-bassins versants**.

2. **Altération de la distribution spatiale : Établie**  
   - Le stencil aux 4 points opère comme un filtre passe-bas bidimensionnel : il atténue les pointes locales de ruissellement et diffuse les flux continentaux vers les mailles marines adjacentes le long du littoral.
   - Le masque de bassin `HYMAP_basin_mask` exclut les flux tombant hors du réseau hydrographique actif (soit $184.03\text{ hm}^3$ pour OL et environ $242.7\text{ hm}^3$ pour DA en 2018).
   - L'application du champ de paramètres `HYMAP_grid_area` modifie la pondération spatiale locale de conversion flux-volume par rapport à la métrique géométrique sphérique, sans toutefois constituer un transfert physique d'eau entre régions.

---

## 10. Questions Scientifiques Ouvertes et Recommandations

L'audit du rééchantillonnage dégage six questions scientifiques et techniques ouvertes à instruire lors des étapes ultérieures :

1. **Origine et interprétation physique de `grarea.bin` :** La formule de calcul, la méthode d'élaboration et la signification physique exacte de la carte fournie par Augusto Getirana (stockée dans `lis_grarea_005.bin` puis `HYMAP_grid_area`) restent non documentées et non élucidées à ce stade. L'origine des écarts systématiques observés par rapport à la surface géométrique sphérique (surfaces inférieures en haute montagne, supérieures en plaine) demeure non résolue et ne doit pas faire l'objet d'hypothèses non vérifiées (telles que des erreurs de projection ou des fractions de sous-bassin non démontrées).
2. **Décalage spatial `LANDMASK` / `HYMAP_basin_mask` :** L'existence de 98 mailles océaniques routées et de 49 mailles terrestres déconnectées (38 nulles et 11 nodata) mérite une analyse cartographique approfondie pour clarifier le devenir des flux littoraux.
3. **Doublement observé de $Q_{sb}$ sous DA-NoCDF :** Les sorties du modèle font apparaître une différence majeure sur le ruissellement sous-surfacique / débit de base simulé ($Q_{sb}$), qui passe de $6\,691.67\text{ hm}^3$ en Open-Loop à $13\,907.12\text{ hm}^3$ sous DA-NoCDF en 2018 ($+7\,215.45\text{ hm}^3$, soit plus qu'un doublement). Cette divergence constitue une différence observée entre sorties de modèle et ne doit pas être interprétée prématurément comme une relation de cause à effet directe ou démontrée avec les incréments d'assimilation d'humidité du sol ; l'élucidation de ce mécanisme physique nécessite un audit complet du bilan en eau interne de Noah-MP (termes d'évapotranspiration, de variation de stock d'humidité du sol et de drainage gravitaire). De plus, ce flux modélisé $Q_{sb}$ ne doit pas être confondu avec une mesure in-situ de la recharge des aquifères.
4. **Validation hydrométrique en rivière requise :** L'impact effectif de ce rééchantillonnage et de la pondération par `grarea` sur les débits fluviaux simulés ne peut être affirmé sans validation hydrométrique. Aucune amélioration des débits simulés ne peut être présumée avant l'évaluation rigoureuse face aux chroniques de jaugeage in-situ lors de l'Étape 05.
5. **Convention temporelle des débits hydrodynamiques HyMAP :** La convention temporelle des débits simulés en sortie de routage (`ROUTING/YYYYMM/LIS_HIST_*.d01.nc`) n'a pas encore été auditée : il conviendra d'établir formellement dans le code source de LISF si le débit fluvial exporté à `00:00:00` représente un débit instantané ou un débit moyenné sur la journée écoulée.
6. **Maintien de la traçabilité sans réécriture :** Les scripts historiques `remap_opl_2016_2020.py` et `remap_da_nocdf_2016_2020.py` constituent la base exacte des simulations existantes. Leurs sorties doivent être conservées telles quelles pour assurer la reproductibilité stricte des simulations de production historiques.

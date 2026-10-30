# Audit Technique du Routage HyMAP2 : Expériences Historiques, Spin-up, Paramètres et Diagnostics de Masse

**Date :** 30 octobre 2026
**Branche Git :** `hymap-routing` (HEAD : `41a33cb`)
**Fichiers de référence :** [`experiments/NorthMor/routing/README_HYMAP.md`](../README_HYMAP.md)
**Tâches associées :** TASK 04A, TASK 04B, TASK 04C, TASK 04D, TASK 04E

---

## 1. Contexte et Objectifs de l'Audit

Ce document consigne l'audit technique et scientifique exhaustif de l'implémentation historique du routeur hydrodynamique **HyMAP2** couplé hors ligne aux sorties de surface Noah-MP sur le domaine Nord Maroc (grille $180 \times 120$ à 0.05°).

L'audit vise à documenter et comprendre l'état **EXISTANT** des simulations historiques sans modification de code ni relance de calcul :
1. Établir l'inventaire complet et la traçabilité des configurations, scripts de soumission SLURM, fichiers de restart, journaux d'exécution MPI et répertoires de sortie pour toutes les expériences historiques (Open-Loop brut, Open-Loop corrigé, Assimilation SMAP DA-NoCDF et bancs d'essai).
2. Vérifier le protocole d'initialisation et de spin-up cyclique (Coldstart $\to$ Cycle 1 $\to$ Cycle 2 $\to$ Production 5 ans), quantifier la convergence des stocks d'eau dans les 4 réservoirs HyMAP2 ($BSFSTO, RNFSTO, RIVSTO, FLDSTO$) et corriger les erreurs de transcription documentaires.
3. Auditer les fichiers de paramètres NetCDF (`lis_input.d01.nc` vs `lis_input_corrigee.d01.nc`), documenter la division par 86 400 appliquée au délai de vidange de nappe `HYMAP_baseflow_time_delay`, et vérifier les attributs d'unités NetCDF exacts.
4. Analyser le comportement effectif du paramètre de vidange de nappe `tbasflw` dans le code Fortran (`HYMAP2_routingMod.F90` et `HYMAP2_modelMod.F90`), en évaluant l'impact du plancher numérique `cntime / 86400.` et sa distribution statistique sur les 15 937 mailles actives.
5. Clarifier la distinction physique entre le bilan de masse interne du modèle (conservation mathématique) et le déficit volumique de débit observé aux exutoires, en réfutant les interprétations erronées relatives aux pertes d'eau numériques.
6. Dresser une synthèse critique structurée des anomalies et questions ouvertes pour guider la documentation hydrologique de l'Étape 05.

---

## 2. Inventaire Exhaustif des Expériences Historiques

L'ensemble des expériences de routage HyMAP2 sur le domaine Nord Maroc est regroupé dans l'arborescence `experiments/NorthMor/routing/`. Toutes les simulations ont été exécutées en mode parallèle MPI (16 processus) sous environnement SLURM sur le cluster Toubkal.

### 2.1 Tableau de traçabilité complète des expériences

| Expérience | Fichier de configuration LISF (`configs/`) | Script SLURM (`jobs/`) | Fichier de paramètres NetCDF | Mode départ / Restart source | Fichier restart généré (`ROUTING/201701/`) | Logs MPI d'exécution (`logs/`) | Répertoire des sorties NetCDF (`output/`) | Statut |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **OPL 201801 (Prototype)** | `lis_hymap2_opl_201801.config` | `run_hymap2_opl_201801.sh` | `lis_input.d01.nc` (brut) | `coldstart` (1 mois, janv. 2018) | *(aucun)* | `lislog_opl_201801.*` (16 logs) | `OPL_201801/ROUTING/` (31 fichiers) | **OBSOLÈTE** |
| **OPL Spin-up Cycle 1 (Brut)** | `lis_hymap2_opl_spinup_cycle1.config` | `run_hymap2_opl_spinup_cycle1.sh` | `lis_input.d01.nc` (brut) | `coldstart` (1 an, 2016) | `LIS_RST_HYMAP2_router_201701010000.d01.nc` | `lislog_opl_spinup_cycle1.*` | `OPL_spinup_cycle1/ROUTING/` (366 fichiers) | **OBSOLÈTE** |
| **OPL Spin-up Cycle 2 (Brut)** | `lis_hymap2_opl_spinup_cycle2.config` | `run_hymap2_opl_spinup_cycle2.sh` | `lis_input.d01.nc` (brut) | `restart` depuis fin cycle 1 brut | `LIS_RST_HYMAP2_router_201701010000.d01.nc` | `lislog_opl_spinup_cycle2.*` | `OPL_spinup_cycle2/ROUTING/` (366 fichiers) | **OBSOLÈTE** |
| **OPL 2016–2020 (Brut)** | `lis_hymap2_opl_2016_2020.config` | `run_hymap2_opl_2016_2020.sh` | `lis_input.d01.nc` (brut) | `restart` depuis fin cycle 2 brut | `LIS_RST_HYMAP2_router_202101010000.d01.nc` | `lislog_opl_2016_2020.*` | `OPL_2016_2020/ROUTING/` (1 827 fichiers) | **OBSOLÈTE** |
| **OPL Spin-up Cycle 1 (Corrigé)** | `lis_hymap2_opl_spinup_c1_corrigee.config` | `run_hymap2_opl_spinup_c1_corrigee.sh` | `lis_input_corrigee.d01.nc` | `coldstart` (1 an, 2016) | `LIS_RST_HYMAP2_router_201701010000.d01.nc` | `lislog_opl_spinup_c1_corrigee.*` | `OPL_spinup_c1_corrigee/ROUTING/` (366 fichiers) | **RÉFÉRENCE HISTORIQUE (COMPLÉTÉ)** |
| **OPL Spin-up Cycle 2 (Corrigé)** | `lis_hymap2_opl_spinup_c2_corrigee.config` | `run_hymap2_opl_spinup_c2_corrigee.sh` | `lis_input_corrigee.d01.nc` | `restart` depuis fin cycle 1 corrigé | `LIS_RST_HYMAP2_router_201701010000.d01.nc` | `lislog_opl_spinup_c2_corrigee.*` | `OPL_spinup_c2_corrigee/ROUTING/` (366 fichiers) | **RÉFÉRENCE HISTORIQUE (COMPLÉTÉ)** |
| **OPL 2016–2020 (Corrigé)** | `lis_hymap2_opl_2016_2020_corrigee.config` | `run_hymap2_opl_2016_2020_corrigee.sh` | `lis_input_corrigee.d01.nc` | `restart` depuis fin cycle 2 corrigé | `LIS_RST_HYMAP2_router_202101010000.d01.nc` | `lislog_opl_2016_2020_corrigee.*` | `OPL_2016_2020_corrigee/ROUTING/` (1 827 fichiers) | **RÉFÉRENCE HISTORIQUE (COMPLÉTÉ)** |
| **DA-NoCDF Spin-up Cycle 1** | `lis_hymap2_da_nocdf_spinup_c1.config` | `run_hymap2_da_nocdf_spinup_c1.sh` | `lis_input_corrigee.d01.nc` | `coldstart` (1 an, 2016) | `LIS_RST_HYMAP2_router_201701010000.d01.nc` | `lislog_da_nocdf_spinup_c1.*` | `DA_nocdf_spinup_c1/ROUTING/` (366 fichiers) | **RÉFÉRENCE HISTORIQUE (COMPLÉTÉ)** |
| **DA-NoCDF Spin-up Cycle 2** | `lis_hymap2_da_nocdf_spinup_c2.config` | `run_hymap2_da_nocdf_spinup_c2.sh` | `lis_input_corrigee.d01.nc` | `restart` depuis fin cycle 1 DA | `LIS_RST_HYMAP2_router_201701010000.d01.nc` | `lislog_da_nocdf_spinup_c2.*` | `DA_nocdf_spinup_c2/ROUTING/` (366 fichiers) | **RÉFÉRENCE HISTORIQUE (COMPLÉTÉ)** |
| **DA-NoCDF 2016–2020 (Production)** | `lis_hymap2_da_nocdf_2016_2020.config` | `run_hymap2_da_nocdf_2016_2020.sh` | `lis_input_corrigee.d01.nc` | `restart` depuis fin cycle 2 DA | `LIS_RST_HYMAP2_router_202101010000.d01.nc` | `lislog_da_nocdf_2016_2020.*` | `DA_nocdf_2016_2020/ROUTING/` (1 827 fichiers) | **RÉFÉRENCE HISTORIQUE (COMPLÉTÉ)** |

### 2.2 Distinctions opérationnelles majeures
1. **Runs bruts (obsolètes) :** Utilisent `lis_input.d01.nc`. La constante de vidange `HYMAP_baseflow_time_delay` y possède des valeurs de l'ordre de $61\,703$. Couplée à la formulation du code LISF attendant des jours, cette configuration a induit un piégeage artificiel continu de 97.5 % du débit de base souterrain dans le réservoir linéaire $BSFSTO$.
2. **Runs de référence historique (techniquement achevés) :** Utilisent `lis_input_corrigee.d01.nc`. La division préalable par 86 400 rétablit la cohérence d'ordre de grandeur du temps de vidange et assure le transfert de la quasi-totalité de l'eau injectée (ratio entrée/sortie $V_{sim}/V_{in} \approx 99.97\%$ en 2018). Leur complétion technique et leur cohérence numérique ne préjugent pas de leur réalisme physique ou de leur performance hydrologique.
3. **Chaînage des flux d'entrée :**
   - Les expériences OPL lisent le ruissellement rééchantillonné dans `runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL/`.
   - Les expériences DA-NoCDF lisent le ruissellement rééchantillonné dans `runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL/`.
4. **Intégrité temporelle des sorties :**
   Les simulations continues de 5 ans contiennent chacune exactement **1 827 fichiers NetCDF journaliers** (`LIS_HIST_201601020000.d01.nc` à `LIS_HIST_202101010000.d01.nc`), sans aucune interruption d'échéance.

---

## 3. Protocole de Spin-up et Restarts

### 3.1 Chaîne séquentielle d'initialisation
Pour éviter d'initialiser les simulations de production de 5 ans avec des rivières et des nappes vides (`coldstart`, stocks nuls $S=0$), un protocole de stabilisation par double cycle annuel a été déployé sur l'année hydrologique initiale 2016 (du 2016-01-01 au 2017-01-01 à 00:00:00 UTC) :

```mermaid
flowchart LR
    CS[Coldstart S=0\n2016-01-01] --> C1[Cycle 1 2016\n1 an]
    C1 -->|Restart fin C1\n2017-01-01| C2[Cycle 2 2016\n1 an]
    C2 -->|Restart fin C2\n2017-01-01| PROD[Production 2016–2020\n5 ans continus]
```

Dans les fichiers de configuration de production (`lis_hymap2_opl_2016_2020_corrigee.config` et `lis_hymap2_da_nocdf_2016_2020.config`), le restart pointe explicitement vers la sortie terminale du Cycle 2 :
```ini
HYMAP2 routing model start mode:         restart
HYMAP2 routing model restart file:       "experiments/NorthMor/routing/output/OPL_spinup_c2_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
```

### 3.2 Diagnostic volumique des 4 réservoirs et convergence

La stabilisation du modèle est évaluée à la fin de chaque cycle annuel en intégrant sur l'ensemble des mailles actives les 4 réservoirs d'état HyMAP2 :
- $BSFSTO$ : Stock du réservoir de nappe souterraine (réservoir conceptuel linéaire)
- $RNFSTO$ : Stock du réservoir de ruissellement superficiel rapide (retard de concentration)
- $RIVSTO$ : Stock d'eau dans le lit mineur des biefs fluviaux
- $FLDSTO$ : Stock d'eau stocké dans les plaines d'inondation

Dans les fichiers NetCDF de restart (`LIS_RST_HYMAP2_router_*.nc`), les quatre variables d'état sont formellement enregistrées en **volume brut en mètres cubes** ($\text{m}^3$, avec attribut de métadonnées `units: "-"`). Dans les fichiers d'historique diagnostique journalier (`LIS_HIST_*.nc`), $BSFSTO$ et $RNFSTO$ sont convertis en lame d'eau équivalente en millimètres ($1000 \times \text{sto} / \text{grarea}$), tandis que $RIVSTO$ et $FLDSTO$ demeurent en volumes ou profondeurs de bief. Les valeurs présentées ci-après sont issues de la sommation directe des volumes en $\text{m}^3$ sur l'ensemble des 15 937 mailles actives, convertis en $\text{hm}^3$ ($1\text{ hm}^3 = 10^6\text{ m}^3$).

Le critère d'arrêt retenu historiquement exige une variation relative inter-cycles du stock souterrain inférieure à 1.0 % :
$$\Delta_{rel}(BSFSTO) = \frac{|S_{BSF}^{(2)} - S_{BSF}^{(1)}|}{S_{BSF}^{(1)}} < 1.0\%$$

#### Résultats quantitatifs vérifiés aux fichiers de restart :

| Simulation | Cycle | BSFSTO (nappe) | RNFSTO (surf) | RIVSTO (riv) | FLDSTO (fld) | Stock Total ($S_{tot}$) | $\Delta BSFSTO$ | $\Delta_{rel}(BSFSTO)$ | Statut du critère |
| :--- | :---: | ---:| ---:| ---:| ---:| ---:| ---:| ---:| :---: |
| **OPL Brut** | Cycle 1 | $3\,552.817\text{ hm}^3$ | $66.908\text{ hm}^3$ | $205.146\text{ hm}^3$ | $147.524\text{ hm}^3$ | $3\,972.395\text{ hm}^3$ | $+3\,552.817\text{ hm}^3$ | $+100.0\%$ | Initialisation |
| (`lis_input.d01.nc`) | Cycle 2 | $6\,920.422\text{ hm}^3$ | $67.228\text{ hm}^3$ | $209.342\text{ hm}^3$ | $150.534\text{ hm}^3$ | $7\,347.526\text{ hm}^3$ | $+3\,367.605\text{ hm}^3$ | **$+94.79\%$** | **ÉCHEC (> 1%)** |
| **OPL Corrigé** | Cycle 1 | **$46.504\text{ hm}^3$** | $66.908\text{ hm}^3$ | $265.366\text{ hm}^3$ | $195.636\text{ hm}^3$ | $574.414\text{ hm}^3$ | $+46.504\text{ hm}^3$ | $+100.0\%$ | Initialisation |
| (`lis_input_corrigee.d01.nc`) | Cycle 2 | **$46.565\text{ hm}^3$** | $67.228\text{ hm}^3$ | $265.374\text{ hm}^3$ | $195.640\text{ hm}^3$ | $574.807\text{ hm}^3$ | **$+0.061\text{ hm}^3$** | **$+0.1316\%$** | **CONVERGÉ (< 1%)** |
| **DA-NoCDF** | Cycle 1 | $146.113\text{ hm}^3$ | $68.216\text{ hm}^3$ | $443.928\text{ hm}^3$ | $452.853\text{ hm}^3$ | $1\,111.110\text{ hm}^3$ | $+146.113\text{ hm}^3$ | $+100.0\%$ | Initialisation |
| (`lis_input_corrigee.d01.nc`) | Cycle 2 | $146.207\text{ hm}^3$ | $68.539\text{ hm}^3$ | $443.935\text{ hm}^3$ | $452.858\text{ hm}^3$ | $1\,111.539\text{ hm}^3$ | **$+0.094\text{ hm}^3$** | **$+0.0645\%$** | **CONVERGÉ (< 1%)** |

> [!IMPORTANT]
> **Correction de la coquille documentaire dans `README_HYMAP.md` :**
> Le tableau historique de `README_HYMAP.md` (l. 163) indiquait par erreur `BSFSTO = 146.4 hm³` pour le Cycle 1 OPL corrigé, résultant d'une confusion typographique avec la valeur de l'expérience DA ($146.11	ext{ hm}^3$). La valeur numérique exacte extraite du fichier restart `output/OPL_spinup_c1_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc` est rigoureusement **$46.504	ext{ hm}^3$**.

### 3.3 Portée et limites scientifiques du critère de convergence
La convergence numérique inter-cycles ($\Delta_{rel} < 0.15\%$) atteste que le système d'équations différentielles ordinaires linéaires régissant les réservoirs a atteint son attracteur cyclique sous forçage annuel périodique.

Néanmoins, **la convergence globale des stocks ne démontre en aucun cas la validité physique du modèle ni sa convergence cellule par cellule** :
1. **Comportement asymptotique d'un réservoir linéaire :** Pour toute entrée périodique positive $I(t)$, le réservoir $dS/dt = I(t) - S/	au$ admet une solution périodique unique. La stabilisation est une propriété purement mathématique de l'opérateur, indépendante de la justesse physique de $	au$.
2. **Effet de masque spatial :** Une variation nette globale de $+0.06	ext{ hm}^3$ à l'échelle du Nord Maroc peut masquer des compensations locales entre cellules en cours d'assèchement et cellules en cours d'accumulation.
3. **Distinction entre réservoir conceptuel et aquifères réels :** La valeur stabilisée $BSFSTO = 46.5\text{ hm}^3$ représente une lame d'eau moyenne sur le domaine actif HyMAP (15 937 mailles, soit environ $415\,762\text{ km}^2$) de seulement $\approx 0.112\text{ mm}$ ($46.504 \times 10^6\text{ m}^3 / 415\,762 \times 10^6\text{ m}^2$). Ce stock numérique de vidange rapide ne doit en aucun cas être assimilé au stockage réel des aquifères régionaux marocains ni à une piézométrie souterraine physique : il s'agit uniquement de la variable d'état d'un simple réservoir conceptuel linéaire de routage.

---

## 4. Fichiers de Paramètres NetCDF : `lis_input.d01.nc` vs `lis_input_corrigee.d01.nc`

### 4.1 Audit microscopique des variables et métadonnées
Une comparaison systématique sous `netCDF4` entre les fichiers `experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc` (2 532 062 octets) et `lis_input_corrigee.d01.nc` (2 587 165 octets) établit que :
- Les **12 dimensions** spatiales et temporelles sont strictement identiques ($180 	imes 120$).
- Les **28 attributs globaux** NetCDF sont rigoureusement identiques.
- **44 des 45 variables NetCDF** présentent des valeurs numériques, masques et attributs parfaitement identiques au bit près.
- **Une seule variable a été modifiée :** `HYMAP_baseflow_time_delay`.

### 4.2 Métadonnées et distribution statistique de `HYMAP_baseflow_time_delay`

| Propriété / Statistique | Fichier brut (`lis_input.d01.nc`) | Fichier corrigé (`lis_input_corrigee.d01.nc`) | Ratio Brut / Corrigé |
| :--- | :---: | :---: | :---: |
| **Attribut `standard_name`** | `'HYMAP_baseflow_time_delay'` | `'HYMAP_baseflow_time_delay'` | Identique |
| **Attribut `units`** | `'none'` | `'days'` | Modification d'attribut |
| **Attribut `missing_value`** | `-9999.0` | `-9999.0` | Identique |
| **Nombre de mailles actives (> 0)** | 15 937 | 15 937 | Identique |
| **Minimum** | $203.656	ext{ (none)}$ | $0.002357	ext{ days}$ ($203.656 / 86400$) | $86\,400.00$ |
| **Percentile 5 (P5)** | $2\,049.400	ext{ (none)}$ | $0.023720	ext{ days}$ | $86\,400.00$ |
| **Médiane (P50)** | $6\,690.718	ext{ (none)}$ | $0.077439	ext{ days}$ | $86\,400.00$ |
| **Moyenne** | $61\,702.975	ext{ (none)}$ | $0.714155	ext{ days}$ | $86\,400.00$ |
| **Percentile 95 (P95)** | $26\,209.052	ext{ (none)}$ | $0.303346	ext{ days}$ | $86\,400.00$ |
| **Maximum** | $2\,631\,664.500	ext{ (none)}$ | $30.459080	ext{ days}$ | $86\,400.00$ |

> [!WARNING]
> **Statut de l'unité d'origine du binaire d'Augusto Getirana :**
> Le fichier binaire d'origine `lis_tbasflw_005.bin` ne comporte aucun en-tête ni descripteur d'unité. Les valeurs numériques brutes (moyenne $pprox 61\,703$) ont été transférées telles quelles par LDT dans `lis_input.d01.nc` avec `units = 'none'`. L'hypothèse historique selon laquelle Augusto Getirana aurait fourni des données en secondes est **NON VÉRIFIÉE**. L'origine exacte, la base théorique et l'unité d'intention de cette carte binaire restent indéterminées en l'absence de documentation d'origine de l'auteur.

---

## 5. Délai de Vidange Effectif du Débit de Base (`tbasflw`) et Effet Plancher

### 5.1 Formulation dans le code source HyMAP2
Dans le code source Fortran de HyMAP2, le calcul et l'encadrement de la vidange du réservoir linéaire de nappe s'articulent entre deux modules distincts :

1. **Plancher numérique sur le paramètre `tbsflw`** lors du chargement des paramètres dans `src/lisf/lis/routing/HYMAP2_router/HYMAP2_routingMod.F90` (l. 1265–1267) :
```fortran
where(HYMAP2_routing_struc(n)%tbsflw < HYMAP2_routing_struc(n)%cntime/86400. .and. &
      HYMAP2_routing_struc(n)%cntime > 0) &
   HYMAP2_routing_struc(n)%tbsflw = HYMAP2_routing_struc(n)%cntime/86400.
```

2. **Flux de vidange linéaire du réservoir souterrain** dans `src/lisf/lis/routing/HYMAP2_router/HYMAP2_modelMod.F90` (subroutine `HYMAP2_linear_reservoir_lis`, l. 109–118, appelée à chaque pas de temps pour chaque cellule active depuis `HYMAP2_model_core.F90`, l. 222–225) :
```fortran
basfsto = basfsto + basflw0*dt
qbas = basfsto / (tbsflw * 86400.)
vbflw = basfsto - qbas*dt
if (vbflw < 0.) then
   qbas = basfsto / dt
   basfsto = 0.
else
   basfsto = vbflw
endif
```

#### Analyse rigoureuse des grandeurs et des unités :
1. **Unité attendue de `tbsflw` :** Le dénominateur de la formulation linéaire (`HYMAP2_modelMod.F90`, l. 111) comporte le produit `tbsflw * 86400.`. Pour obtenir un flux $q_{bas}$ en $\text{m}^3/\text{s}$ à partir d'un stock $basfsto$ en $\text{m}^3$, **le modèle attend formellement `tbsflw` en JOURS**.
2. **Unité et distribution spatiale de `cntime` :** La variable `cntime` (chargée depuis le champ 2D `HYMAP_runoff_time_delay` dans `lis_input`) représente le temps de concentration du ruissellement superficiel issu de la méthode de Getirana & Paiva (2013). Elle est exprimée en **SECONDES** et constitue un champ spatialement distribué (médiane $\approx 211\,374\text{ s} \approx 2.45\text{ jours}$, moyenne $\approx 325\,138\text{ s} \approx 3.76\text{ jours}$, minimum $\approx 18\,004\text{ s} \approx 0.21\text{ jour}$, maximum $\approx 8\,724\,306\text{ s} \approx 101.0\text{ jours}$). Il ne s'agit en aucun cas d'un paramètre uniforme de 86 400 secondes.
3. **Terme de comparaison `cntime / 86400.` :** La division par 86 400 dans `HYMAP2_routingMod.F90` (l. 1265–1267) convertit le temps de concentration en **JOURS**, rendant la condition de plancher dimensionnellement cohérente en jours (`tbsflw` et `cntime / 86400.` sont tous deux en jours).

### 5.2 Démonstration de l'écrêtage massif sur la grille (99.90 %)
Dans le fichier corrigé `lis_input_corrigee.d01.nc`, la division par 86 400 a abaissé la médiane de `tbsflw` à **0.077 jour** (environ 1.8 heure).

En comparant cellule par cellule `tbsflw` et `cntime / 86400.` sur les 15 937 mailles actives :
- Dans **15 921 mailles sur 15 937 (soit 99.8996 % $pprox 99.90\%$)**, la valeur du paramètre est strictement inférieure au plancher :
  $$tbsflw <
rac{cntime}{86400}$$
- Dans ces 15 921 mailles, la valeur issue de la carte de paramètres est **totalement écrasée et remplacée à l'exécution par `cntime / 86400.`**.
- Seules **16 mailles** (situées sur les zones planes où le paramètre corrigé atteint son maximum local de $pprox 30.46	ext{ jours}$) conservent leur valeur de paramètre non modifiée.

### 5.3 Distribution statistique du délai effectif d'écoulement
Le délai effectif de vidange du débit de base $t_{eff} = \max\left(tbsflw,
rac{cntime}{86400}
ight)$ ne s'étend pas sur la fourchette étroite de 1 à 2.8 jours (qui ne correspondait qu'à un sous-ensemble du bassin du Bouregreg), mais suit la distribution spatiale réelle suivante sur l'ensemble du domaine Nord Maroc :

| Grandeur statistique | Valeur en jours | Équivalent physique |
| :--- | ---:| :--- |
| **Minimum absolu** | $0.2084	ext{ j}$ | $pprox 5.0	ext{ heures}$ (zones de forte pente) |
| **Percentile 5 (P5)** | $1.0909	ext{ j}$ | $pprox 26.2	ext{ heures}$ |
| **Médiane (P50)** | **$2.4465	ext{ j}$** | $pprox 58.7	ext{ heures}$ |
| **Moyenne spatiale** | $3.7719	ext{ j}$ | $pprox 90.5	ext{ heures}$ |
| **Percentile 90 (P90)** | $4.6945	ext{ j}$ | $pprox 4.7	ext{ jours}$ |
| **Percentile 95 (P95)** | **$5.8522	ext{ j}$** | $pprox 5.9	ext{ jours}$ |
| **Percentile 99 (P99)** | $54.8214	ext{ j}$ | $pprox 54.8	ext{ jours}$ (plaines terminales) |
| **Maximum absolu** | $100.9758	ext{ j}$ | $pprox 101.0	ext{ jours}$ (exutoires lagunaires) |

```
Distribution du délai effectif de vidange (15 937 mailles actives) :
Min: 0.21 j  ---- P5: 1.09 j ---- Médiane: 2.45 j ---- P95: 5.85 j ---------------- Max: 100.98 j
[==== 5% ====] [============ 45% ============] [==== 45% ====] [=========== 5% ===========]
```

#### Conséquence physique majeure :
En fixant le temps de séjour du réservoir souterrain à une médiane de **2.45 jours** (et P95 à 5.85 jours), la vidange s'opère sur une échelle temporelle proche de celle du ruissellement superficiel retardé. Cette vidange rapide sans seuil d'interruption constitue un mécanisme plausible expliquant la difficulté du modèle à reproduire des régimes d'étiages sévères ou des assecs prolongés, sans exclure le rôle d'autres composantes (dynamique du flux $Q_{sb}$ de Noah-MP ou absence d'infiltration en lit mineur).

---

## 6. Diagnostic des Stocks et Bilans Volumiques

### 6.1 L'accumulation massive dans BSFSTO en configuration brute
Dans la simulation brute `OPL_2016_2020`, le cumul des débits restitués aux exutoires présentait un déficit d'environ 50 % par rapport au ruissellement total généré par Noah-MP ($V_{out} pprox 0.50 V_{in}$).

L'audit interne du modèle a prouvé de façon irréfutable que **cette anomalie ne résultait pas d'une perte d'eau numérique ni d'un défaut de conservation mathématique**, mais d'une accumulation continue dans le réservoir linéaire souterrain :
- La simulation de production brute OPL a démarré à partir du restart du Cycle 2 (stock initial $BSFSTO \approx 6\,920.4\text{ hm}^3$) pour atteindre un stock final d'environ $23\,446.2\text{ hm}^3$ au 31 décembre 2020 / 1er janvier 2021 (fichier `output/OPL_2016_2020/ROUTING/202101/LIS_RST_HYMAP2_router_202101010000.d01.nc`). La différence de stockage aux bornes de la simulation, calculée directement entre ces deux fichiers de restart, est de **$+16\,525.8\text{ hm}^3$** ($23\,446.18 - 6\,920.42\text{ hm}^3$).
- La valeur historique de **$+16\,518\text{ hm}^3$** (mentionnée dans les notes préliminaires `Hymap_troubleshooting.txt`) provient d'un diagnostic distinct calculé à partir des fichiers d'historique journalier : cette valeur ne doit pas être déclarée strictement équivalente à la différence des restarts, et leur écart résiduel d'environ $7.4\text{ hm}^3$ demeure non résolu. Toutes deux représentent l'**augmentation nette de stockage** ($\Delta S_{BSF}$) sur 5 ans, et **non le stock final**.
- La régression linéaire montre une accumulation moyenne de **$+3\,677\text{ hm}^3/\text{an}$** ($R^2 = 0.977$).
- En raison de la valeur non corrigée `tbsflw` $\approx 61\,703$ interprétée en jours par le code (soit $\tau \approx 169\text{ ans}$), le taux de vidange journalier n'était que de $1 / (61\,703 \times 86400) \approx 1.88 \times 10^{-10}\text{ s}^{-1}$ : le réservoir fonctionnait comme un cul-de-sac hydrologique capturant 97.5 % du débit de base souterrain $Qsb$.

```
Bilan de masse schématique (Simulation brute OPL 2016–2020) :
Entrée Noah-MP (Vin) = 100 %
    ├── Ruissellement de surface rapide (Qs)  --> Routé aux exutoires (~50 %)
    └── Débit de base sous-surfacique (Qsb)  --> Piégé dans BSFSTO (+16 525.8 hm³ entre restarts, stock final ~23 446.2 hm³ ; diag. hist. +16 518 hm³)
```

### 6.2 Ratio d'écoulement entrée/sortie vs Bilan de masse complet et Réalisme physique
Dans l'analyse historique préliminaire de la simulation corrigée `OPL_2016_2020_corrigee` sur l'année 2018, les volumes cumulés rapportés étaient :
$$V_{in} = 6\,864.08\text{ hm}^3 \quad \text{et} \quad V_{sim} = 6\,861.68\text{ hm}^3$$

- **Statut diagnostique et limitation explicite de périmètre :** Ces grandeurs sont retenues exclusivement comme des **valeurs diagnostiques historiques avec une limitation explicite de périmètre**, leur provenance exacte n'ayant pu être reconstituée de manière univoque dans le code actif existant :
  - **Périmètre spatial et sélection des exutoires :** Le masque spatial exact, la surface contributive drainée et la sélection précise des cellules d'exutoire ayant produit ce couple de valeurs demeurent non résolus dans les scripts historiques. Ces valeurs ne doivent donc pas être qualifiées de volumes représentatifs de l'ensemble des bassins versants jaugés, ni assimilées à un agrégat régional particulier.
  - **Conventions temporelles (année calendaire vs date de nommage des fichiers) :** Les fichiers journaliers LIS `LIS_HIST_YYYYMMDD0000.d01.nc` enregistrant la moyenne des 24 heures précédentes (jour $J-1$), la période physique cumulée peut différer d'un jour aux bornes selon la convention de filtrage temporel adoptée dans les scripts d'analyse.
  - **Distinction avec l'Étape 03 ($S_4$) :** Ce diagnostic historique possède un support spatial propre et restreint. Il ne doit en aucun cas être assimilé ni comparé au volume diagnostique total $S_4 = 10\,980.49\text{ hm}^3$ établi à l'Étape 03, qui intègre les flux journaliers pondérés par `HYMAP_grid_area` sur l'ensemble des 15 937 mailles actives du domaine de routage.
- **Interprétation de l'écart résiduel :** Le rapport $V_{sim} / V_{in} = 6\,861.68 / 6\,864.08 \approx 99.965\%$ présente un écart résiduel entrée-sortie de $V_{in} - V_{sim} = 2.40\text{ hm}^3$ (soit $0.035\%$). Cet écart constitue une divergence historique dont la provenance spatio-temporelle reste non résolue ; il ne doit pas être interprété comme une variation physique de stockage vérifiée ($\Delta S$) des réservoirs HyMAP2.
- **Absence de garantie sur le réalisme physique :** La proximité du ratio $V_{sim}/V_{in}$ avec 100 % (faible rétention pluriannuelle dans le réservoir linéaire) ne constitue en aucun cas une preuve de réalisme physique :

1. **Neutralisation de la dynamique temporelle :** Tout modèle conservatif sans pertes par évaporation fluviale restituera à terme 100 % de l'eau entrée, que le temps de transfert soit de 2 jours ou de 2 ans.
2. **Transfert aveugle de biais de surface :** Si Noah-MP sous-estime ou surestime la production d'eau (comme dans le Sebou ou le Bouregreg sous DA), le routeur HyMAP2 restitue fidèlement cette anomalie à l'exutoire.
3. **Absence de pertes en lit mineur :** HyMAP2 ne modélise pas l'infiltration vers les nappes profondes le long des biefs ni l'évaporation sur les plans d'eau temporaires en zone semi-aride (`HYMAP2 routing model evaporation option: none`).

---

## 7. Tableau des Problèmes Historiques et Questions Ouvertes

Le tableau ci-dessous synthétise de manière factuelle et rigoureuse l'ensemble des anomalies détectées, en distinguant clairement les mécanismes démontrés des hypothèses physiques plausibles :

| Anomalie / Phénomène observé | Fichiers, code et journaux d'appui | Mécanisme confirmé | Explication plausible | Incertitude non résolue | Conséquence sur l'évaluation des débits |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Piégeage massif d'eau dans BSFSTO en OPL brut** | - `lis_input.d01.nc`\n- `HYMAP2_modelMod.F90` (l. 111)\n- `HYMAP2_model_core.F90` (l. 222–225)\n- `Hymap_troubleshooting.txt` | Valeurs brutes de `tbasflw` (~61 703) ingérées en jours, induisant un temps de vidange de ~169 ans piégeant une augmentation nette de stockage entre restarts de $+16\,525.8\text{ hm}^3$ en 5 ans (stock initial au restart cycle 2 $\approx 6\,920.4\text{ hm}^3 \to$ final $\approx 23\,446.2\text{ hm}^3$ ; diagnostic historique antérieur de $+16\,518\text{ hm}^3$, écart résiduel non résolu). | Erreur d'homogénéité dimensionnelle lors de la création de la carte LDT. | Unité d'intention d'origine dans le binaire d'Augusto Getirana (`lis_tbasflw_005.bin`). | Déficit apparent de débit de 50 % aux exutoires dans toutes les publications antérieures au 26 octobre 2026. |
| **Écrasement du paramètre par le plancher `cntime`** | - `lis_input_corrigee.d01.nc`\n- `HYMAP2_routingMod.F90` (l. 1265–1267)\n- `HYMAP2_modelMod.F90` (l. 111)\n- `README_HYMAP.md` | La division par 86 400 a rendu `tbsflw` < `cntime/86400.` sur 99.90 % des mailles (15 921 / 15 937). | Le code LISF applique un garde-fou numérique conçu pour empêcher que la vidange de nappe ne soit plus rapide que la concentration superficielle. | Justification hydrodynamique d'imposer un plancher de concentration fluviale à un aquifère souterrain. | Temps de vidange effectif médian réduit à 2.45 j ; vidange quasi-immédiate du stock d'eau souterraine. |
| **Surestimation des débits d'étiage et absence d'assecs** | - `obs_daily.csv` (Sidi Jabeur)\n- `t5bis_lowflow_stats.csv`\n- `F3_courbes_debits_classes.png` | Résultat observé : 0 jour d'assec simulé sur l'oued Grou à Sidi Jabeur (contre 312 jours observés) ; réduction de $\tau$ de 15.6 j à 2.1 j. | Mécanisme plausible : La vidange continue rapide imposée par le plancher `cntime` (médiane 2.45 j) alimente sans seuil d'interruption le réseau hydrographique. | Explication non vérifiée : Part respective de l'absence de pertes en lit mineur dans HyMAP2 et de la dynamique continue du drainage $Q_{sb}$ généré par Noah-MP. | Mauvaise restitution systématique des régimes hydrologiques intermittents méditerranéens. |
| **Convergence de spin-up sans réalisme physique** | - `check_spinup_criterion_corrigee.py`\n- Restarts `LIS_RST_*`\n- `README_HYMAP.md` | Critère $\Delta_{rel} < 1.0\%$ validé dès le Cycle 2 ($0.13\%$ en OPL, $0.06\%$ en DA), mais avec un stock de nappe stabilisé à seulement 46.5 hm³ ($\approx 0.112\text{ mm}$ sur le domaine actif de $\approx 415\,762\text{ km}^2$, réservoir conceptuel distinct des aquifères régionaux réels). | Le réservoir linéaire atteint rapidement son équilibre cyclique du fait de sa vidange très rapide (médiane 2.45 j). | Représentativité de ce stock résiduel par rapport aux réserves réelles des aquifères marocains. | L'état initial de production démarre avec un réservoir souterrain quasi-vide qui ne joue aucun rôle tampon pluriannuel. |
| **Explosion des débits sous assimilation DA-NoCDF** | - `complete_t8_analysis_and_plots.py`\n- `synthese_hydrologique_12stations.csv`\n- `F6_effet_assimilation.png` | Résultat observé : Forte dégradation du biais volumique relatif aux observations (PBIAS) dans le Bouregreg, atteignant $+380.6\%$ à Lalla Chafia (contre $+4.3\%$ en OPL corrigé, KGE chutant à $-2.89$) et $+480.4\%$ à S.M. Cherif (contre $+14.6\%$ en OPL corrigé). | Mécanisme plausible : Absence de correction de biais (CDF matching), SMAP L3 étant plus humide que Noah-MP, l'EnKF injecte continuellement de l'eau en surface. | Bilan quantitatif exact des incréments d'analyse EnKF ventilés entre les 4 couches de sol et le ruissellement. | Dégradation sévère des simulations hydrologiques en régime atlantique pluvial non contraint. |
| **Déficit volumique persistant sur le haut Sebou** | - `obs_monthly.csv`\n- `synthese_hydrologique_12stations.csv`\n- `F2b_hydrogrammes_sebou.png` | Résultat observé : PBIAS persistant de $-74\%$ à $-78\%$ sur les 4 stations du haut Sebou en OPL corrigé ($V_{sim} \approx 15\text{--}20\text{ mm/an}$ vs $V_{obs} \approx 60\text{--}90\text{ mm/an}$). | Explication non vérifiée : L'infiltration vers des réservoirs karstiques profonds avec résurgences vauclusiennes non modélisées par Noah-MP constitue une hypothèse hydrogéologique non vérifiée parmi d'autres (sous-estimation des pluies d'altitude, prélèvements ou évapotranspiration). | Part respective du déficit imputable aux forçages pluviométriques d'altitude, aux prélèvements et à la géologie. | La réduction apparente du déficit sous DA-NoCDF constitue une compensation arithmétique plausible mais non démontrée comme causale. |

---

## 8. Recommandations pour l'Étape 05 (Documentation Hydrologique)

1. **Réfuter explicitement les conclusions basées sur le run brut :** Toutes les figures et métriques issues des scripts préliminaires (`extract_and_plot_9stations_2016_2020.py`, `confrontation_adamna.py`, `analysis_tache5bis.py`) doivent être formellement étiquetées comme **obsolètes** dans les rapports et archives.
2. **Distinguer régimes pluviaux et bassins spécifiques :** L'évaluation de l'Étape 05 doit analyser séparément le comportement du Bouregreg (régime pluvial réagissant fortement à DA-NoCDF) et celui du Sebou (fort déficit volumique en OPL corrigé dont les causes potentielles — karst, forçage pluviométrique, prélèvements — restent des hypothèses non vérifiées).
3. **Distinguer rigoureusement fait établi et causalité :** L'écrêtage de `tbasflw` par `cntime/86400.` sur 99.90 % des mailles est un fait mathématique établi dans le code ; en revanche, sa contribution relative à la surestimation des étiages par rapport aux autres facteurs (absence d'infiltration en lit mineur, dynamique du ruissellement souterrain Noah-MP) doit être qualifiée de mécanisme plausible.

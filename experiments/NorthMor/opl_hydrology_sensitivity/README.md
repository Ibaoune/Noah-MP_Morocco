# Étude Pilote de Sensibilité Hydrologique Noah-MP 4.0.1 (Open-Loop, 2017–2018)
**Auteur :** M. El Aabaribaoune (@um6p)  
**Date :** Novembre 2026  
**Statut :** Validation technique opérationnelle terminée. Chaînage mensuel strict (anti-écrasement, vérification exacte des jours et des restarts), remapping conservatif et routage HyMAP-2 local validés. **Chaînes de 24 mois prêtes pour lancement.**

---

## 1. Contexte et Problématique Scientifique

Dans la simulation de référence Open-Loop (**SIMGM**, Option 1 de ruissellement et nappe de Noah-MP 4.0.1) sur le domaine du Nord du Maroc (grille `NorthMor` $181 \times 121$ à $0.05^\circ$), deux anomalies hydrologiques majeures ont été identifiées :
1. **Sous-estimation chronique des pointes de crues hivernales et printanières :** En particulier lors des événements extrêmes de mars, avril et novembre 2018 aux stations de **Lalla Chafia** (bassin du **Bouregreg**) et **Sidi Jabeur** (sur l'oued **Grou**, bassin du **Bouregreg**).
2. **Persistance anormale des débits d'étiage estivaux :** Pendant la saison sèche (juin à septembre), le modèle maintient un débit continu à Sidi Jabeur alors que les observations de l'Agence de Bassin Hydraulique (ABH) documentent un tarissement complet ($Q_{\text{obs}} \approx 0\text{ m}^3\text{/s}$).

L'objectif de cette étude pilote est d'évaluer l'impact direct des formulations physiques de surface et de subsurface de Noah-MP 4.0.1, en comparant 4 schémas sans modification du forçage météorologique (MERRA-2 + GPM IMERG V07B) ni des paramètres de sol de base.

---

## 2. Matrice des 4 Expériences Testées

| Identifiant Expérience | Formulation Ruissellement & Nappe | Code LIS (`dveg=2`) | Référence Clé | Hypothèse Physique Testée |
| :--- | :--- | :---: | :--- | :--- |
| **`OL_R1_SIMGM`** | Simple Groundwater Model (Baseline) | `opt_run=1` | Niu et al. (2007) | Recharge et nappe 1D dynamique couplée à la colonne de sol. Drainage exponentiel. |
| **`OL_R2_SIMTOP`** | TOPMODEL-based runoff & groundwater | `opt_run=2` | Niu et al. (2005) | Fraction saturée spatiale sous-maille issue de l'indice topographique. Nappe diagnostique ($Z_{wt}$). |
| **`OL_R3_SCHAAKE96`**| Schaake 96 (Infiltration-excess) | `opt_run=3` | Schaake et al. (1996) | Infiltration de type VIC basée sur la capacité maximale. Drainage gravitaire libre avec correction de pente. |
| **`OL_R4_BATS`** | BATS (Biosphere-Atmosphere Transfer) | `opt_run=4` | Dickinson et al. (1993) | Ruissellement de saturation proportionnel à $(\theta/\theta_{\text{sat}})^4$. Drainage libre gravitaire standard. |

---

## 3. Statut d'Avancement et Validation Opérationnelle

Pour garantir l'intégrité opérationnelle avant le calcul intensif de 24 mois, chaque maillon a été testé et vérifié de manière isolée.

### Tableau de Synthèse de Validation

| Expérience | Test court (2j) | Chaînage Janv. 2017 & Restart | Reprise Fév. 2017 | Remapping HyMAP (180x120) | Extraction débits (ABH) | Statut Prêt 2017–2018 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`OL_R1_SIMGM`** | **Validé** | **Validé** (31j, restart 1.6MB) | **Validé** (53s, 0 err) | **Validé** (31j conservatifs) | **Validé** (31j extraits) | **PRÊT** |
| **`OL_R2_SIMTOP`** | **Validé** | **Validé** (31j, restart 1.6MB) | **Validé** (53s, 0 err) | **Validé** (31j conservatifs) | **Validé** (31j extraits) | **PRÊT** |
| **`OL_R3_SCHAAKE96`**| **Validé** | **Validé** (31j, restart 1.6MB) | **Validé** (53s, 0 err) | **Validé** (31j conservatifs) | **Validé** (31j extraits) | **PRÊT** |
| **`OL_R4_BATS`** | **Validé** | **Validé** (31j, restart 1.6MB) | **Validé** (53s, 0 err) | **Validé** (31j conservatifs) | **Validé** (31j extraits) | **PRÊT** |

---

## 4. Détail des Éléments Réellement Testés et Validés

1. **Test court de 2 jours (01/01/2017 au 03/01/2017) :**
   - Exécution complète sur 32 cœurs MPI OpenMPI 5.0.3 en ~55s walltime.
   - Confirmation de l'équivalence thermique et d'évapotranspiration hivernale ($ET = 0.65\text{ mm/j}$ pour tous).
   - Contraste immédiat du ruissellement : BATS produit $+196\%$ de $Q_s$ vs SIMGM ; SIMTOP réajuste $Z_{wt}$ à $2.26\text{ m}$.
2. **Simulation complète de Janvier 2017 (31 jours) :**
   - 31 fichiers journaliers NetCDF générés par expérience dans `output/2017-01/SURFACEMODEL/201701/`.
   - Restarts terminaux `restarts/LIS_RST_NOAHMP401_201702010000.d01.nc` validés (intégrité NetCDF sans NaN, taille 1.6 MB, stockage pérenne).
   - Recalage physique de nappe SIMTOP ($Z_{wt}=2.278\text{ m}$ vs $3.092\text{ m}$ pour SIMGM).
3. **Chaînage mensuel et reprise sécurisée :**
   - Le script `chain_opl.py` vérifie le nombre exact de jours du mois (31j en janvier, 28j en février, etc.), la présence et la taille non nulle de chaque fichier journalier `LIS_HIST`, ainsi que l'intégrité du restart terminal ($> 1\text{ MB}$).
   - Un mois incomplet n'est jamais considéré comme terminé.
   - Les quatre chaînes reprennent automatiquement au **01/02/2017** en sautant janvier 2017 sans écraser les résultats déjà validés.
4. **Conservation des volumes et remapping HyMAP-2 :**
   - **Méthode :** Stencil conservatif 4 points sur grille centrée $180 \times 120$ avec paramètres LDT `lis_input_corrigee.d01.nc` (conforme au standard historique).
   - **Conservation des flux $Q_s + Q_{sb}$ :** L'intégrale spatiale sphérique avec pondération trapézoïdale de bord montre une conservation rigoureuse à **99.9999% / 100.0000%** ($S_2/S_1$) entre la grille source et la grille cible sur l'ensemble du mois de janvier 2017.
   - **Nettoyage des fichiers de test :** Les fichiers artificiellement dupliqués lors des tests préliminaires de bookend ont été supprimés. Les entrées de février proviendront exclusivement des sorties réelles de Noah-MP.
5. **Routage HyMAP-2 et extraction locale (Janvier 2017) :**
   - Routage exécuté avec succès en 37s walltime par expérience (`linres=0`, onde cinématique, plaine inondable activée).
   - Extraction exacte du calendrier ($t_{\text{sim}} = t_{\text{file}} - 1\text{ j}$) au droit des stations ABH (Lalla Chafia et Sidi Jabeur, bassin du Bouregreg).
6. **Post-traitement des observations ABH :**
   - Lecture robuste du format long (`data/streamflow_clean/obs_daily.csv` : `station_id`, `date`, `q_m3s`), pivot par date, élimination des valeurs manquantes/négatives.
   - Calcul validé de KGE-2009, NSE, PBIAS, Pearson $r$, et des métriques d'étiage estivales (débit moyen, jours à débit nul $\le 0.01\text{ m}^3\text{/s}$ et faible $\le 0.1\text{ m}^3\text{/s}$).

### Résultats d'Évaluation Préliminaire (Janvier 2017 — Tests Techniques Uniquement)

> [!NOTE]
> **Avertissement méthodologique :** Les résultats numériques ci-dessous sont présentés uniquement à titre de test technique du pipeline de calcul. Le routage HyMAP-2 y démarre à froid (`coldstart`, chenaux initialement vides) et les 4 formulations physiques de sol et de nappe sont en début de période de relaxation/ajustement hydrodynamique. Ils ne préjugent en rien des performances scientifiques finales sur l'année d'évaluation 2018.

| Station ABH | Bassin Versant | Obs Moyenne | SIMGM (Opt 1) | SIMTOP (Opt 2) | Schaake96 (Opt 3) | BATS (Opt 4) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Lalla Chafia** | Bouregreg | **3.48 m³/s** | 1.85 (PBIAS -47%) | 7.62 (PBIAS +119%) | 1.74 (PBIAS -50%) | 8.34 (PBIAS +140%) |
| **Sidi Jabeur** | Grou (Bouregreg) | **4.35 m³/s** | 1.44 (PBIAS -67%) | 7.79 (PBIAS +79%) | 1.10 (PBIAS -75%) | 7.26 (PBIAS +67%) |

---

## 5. Éléments Préparés mais Non Encore Validés Scientifiquement

- **Simulations de 24 mois (Février 2017 à Décembre 2018) :** Les scripts et configurations sont générés et prêts, mais le lancement n'est pas encore déclenché.
- **Routage HyMAP-2 complet 2017–2018 :** Les fichiers de configuration pour la période complète sont prêts avec `linres=0` et pointent vers `lis_input_corrigee.d01.nc`.
- **Évaluation scientifique de l'année 2018 :** Les métriques complètes de crue (mars, avril, nov 2018) et d'étiage (juin–sept 2018) ainsi que les figures graphiques seront produites à l'issue des 24 mois.

---

## 6. Arborescence du Projet Indépendant

```text
opl_hydrology_sensitivity/
├── README.md                                  # Synthèse opérationnelle et statut
├── experiments/                               # Simulations Noah-MP OPL (4 options)
│   ├── OL_R1_SIMGM/                           # Option 1 (SIMGM baseline)
│   ├── OL_R2_SIMTOP/                          # Option 2 (SIMTOP)
│   ├── OL_R3_SCHAAKE96/                       # Option 3 (Schaake96)
│   └── OL_R4_BATS/                            # Option 4 (BATS)
├── routing/                                   # Chaîne de routage HyMAP-2 locale
│   ├── configs/                               # Configs HyMAP-2 2017-2018 & test_jan2017
│   ├── scripts/                               # Remapping, routage et extraction
│   ├── runs/                                  # Ruissellements remappés (180x120) et logs
│   └── outputs/                               # Débits routés journaliers par station
├── postproc/                                  # Évaluation ABH et métriques
│   ├── scripts/evaluate_opl_hydrology.py      # Calcul KGE, NSE, PBIAS, étiages
│   └── tables/                                # Tables de métriques exportées
└── scripts/                                   # Utilitaires de validation et lancement
    ├── update_chain_scripts.py                # Maintenance du chaînage strict
    ├── verify_jan2017_restarts.py             # Contrôle intégrité des restarts
    └── launch_all_production_2017_2018.sh     # Lanceur master 2017-2018 (en attente)
```

---

## 7. Commandes pour le Lancement de la Production (À Déclencher à l'Étape Suivante)

Lorsque vous validerez le lancement des simulations 2017–2018 :

```bash
# Lancement des 4 chaînes en parallèle (avec reprise automatique au 01/02/2017) :
bash experiments/NorthMor/opl_hydrology_sensitivity/scripts/launch_all_production_2017_2018.sh

# Ou lancement individuel par schéma :
bash experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/scripts/launch_2017_2018.sh
bash experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/scripts/launch_2017_2018.sh
bash experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/scripts/launch_2017_2018.sh
bash experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R4_BATS/scripts/launch_2017_2018.sh
```

---

## 8. Respect Strict de l'Environnement

- Aucun fichier n'a été créé ni modifié dans `experiments/NorthMor/routing/`, `experiments/NorthMor/matrix_2016_2020/` ou dans `data/streamflow_clean/`.
- Tous les travaux, fichiers de configuration, sorties NetCDF et tables de métriques sont strictement cantonnés dans `experiments/NorthMor/opl_hydrology_sensitivity/`.

---

## 5. Exécution et Résultats du Routage HyMAP-2 (2017–2018)

- **Remapping conservatif :** 731 fichiers journaliers remappés par expérience (2017–2018 + jour tampon du 02/01/2019) sur la grille HyMAP $180 \times 120$ via `routing/scripts/remap_runoff_sensitivity.py`.
- **Routage HyMAP-2 local (`linres=0`) :**
  - Jobs SLURM `8315612` (`OL_R1_SIMGM`), `8315613` (`OL_R2_SIMTOP`), `8315614` (`OL_R3_SCHAAKE96`), `8315615` (`OL_R4_BATS`).
  - Statut : 100% complétés avec succès (`ExitCode = 0:0`, durée ~11 min 38 s).
  - 730 fichiers journaliers NetCDF de débit routé générés par expérience (2017 initialisation, 2018 évaluation).
- **Post-traitement scientifique 2018 :**
  - Extraction journalière aux stations ABH (`routing/scripts/extract_streamflow_sensitivity.py`).
  - Comparaison sur Lalla Chafia et Sidi Jabeur (`postproc/scripts/compare_opl_hydrology_2018.py`).
  - Figures et tables synthétiques générées dans `postproc/figures/` et `postproc/tables/`.

---

## 9. Évaluation des Contraintes Physiques Indépendantes (2018) : ET, SMAP et Bilan Hydrique

### 9.1 Objectif et Cadre d'Évaluation
Après validation des performances de débit routé par HyMAP-2 sur 2018, ce diagnostic évalue si les améliorations de débit obtenues avec **SIMTOP** et **BATS** restent cohérentes avec l'évapotranspiration (ET), l'humidité superficielle du sol (SM) et la fermeture du bilan hydrique sur les bassins versants amont D8 de **Lalla Chafia** (3 333,3 km²) et **Sidi Jabeur** (3 130,6 km²).

### 9.2 Méthodologie et Données Indépendantes
1. **Évapotranspiration (ET)** :
   - Extrait journalier de `Evap_tavg` (converti en mm/jour) depuis les sorties Noah-MP 2018.
   - Benchmark indépendant : **GLEAM v4.3a** (résolution 0,1°, pas de temps journalier), complété par GLEAM v3.7a. (WaPOR v3 disponible principalement à l'échelle décadaire/mensuelle continentale).
   - Métriques : Biais annuel (mm et %), RMSD journalier (mm/j), coefficient de corrélation de Pearson journalier ($R_{\text{daily}}$) et mensuel ($R_{\text{monthly}}$).
2. **Humidité du Sol Superficielle (SM)** :
   - Couche 1 Noah-MP (0–10 cm, `SoilMoist_tavg`) comparée aux observations satellitaires micro-ondes L-band (1,4 GHz, ~0–5 cm) du produit **SMAP SPL3SMP_E** (grille EASE-Grid 2.0 à 9 km, orbite AM descendante).
   - Masque d'observations valides strictement commun aux 4 expériences (175 jours à Lalla Chafia, 174 jours à Sidi Jabeur en 2018).
   - Filtre qualité : `retrieval_qual_flag bit0 == 0` et valeurs physiques $0 < \theta \le 0{,}60\text{ m}^3\text{/m}^3$.
   - Métriques : Biais volumique, RMSD, unbiased RMSD (ubRMSD), corrélation temporelle directe ($R$) et corrélation des anomalies ($R_{\text{anom}}$, après retrait de la climatologie mobile 31 jours).
3. **Bilan Hydrique et Variations de Stockage** :
   - Flux annuels intégrés : Précipitations ($P$), Évapotranspiration ($ET$), Ruissellement de surface ($Q_s$), Ruissellement de base ($Q_{sb}$).
   - Variation du stock d'eau dans le sol ($\Delta S_{\text{soil}}$) calculée sur les 4 couches de sol ($dz = [100, 300, 600, 1000]\text{ mm}$) entre les fichiers restart du 01/01/2018 00:00 et du 01/01/2019 00:00.
   - Variation du stock souterrain ($\Delta S_{\text{gw}}$) : calculée via la variable de nappe `WA` pour SIMGM (+30,9 mm à LC, +20,1 mm à SJ). Pour SIMTOP, Schaake96 et BATS, $\Delta S_{\text{gw}} \equiv 0{,}0\text{ mm}$ (pas de réservoir d'aquifère explicite distinct de la colonne de sol).
   - Fermeture du bilan : $\epsilon = P - ET - (Q_s + Q_{sb}) - (\Delta S_{\text{soil}} + \Delta S_{\text{gw}} + \Delta S_{\text{surf}})$.

### 9.3 Synthèse des Résultats Physiques 2018
- **Fermeture du bilan hydrique** : Erreur résiduelle inférieure à **0,13%** ($|\epsilon| < 0{,}85\text{ mm}$ sur un cumul de pluie annuel de 637 à 762 mm), confirmant la stricte conservation de la masse.
- **Évapotranspiration** :
  - Tous les schémas surestiment l'ET par rapport à GLEAM v4.3a (+14% à +32%).
  - **BATS** présente le biais le plus faible (+19,9% à Lalla Chafia, +13,8% à Sidi Jabeur) et le RMSD le plus réduit (0,65 mm/j et 0,54 mm/j), car son fort ruissellement superficiel évacue rapidement l'eau et limite l'ET.
  - **SIMTOP** modère également l'ET (+27,8% et +17,0%) par rapport à SIMGM (+28,9% et +22,0%) et Schaake96 (+31,9% et +22,5%).
- **Humidité du sol** :
  - Cohérence exceptionnelle des 4 schémas avec SMAP ($R = 0{,}88\text{ à }0{,}91$, $R_{\text{anom}} = 0{,}76\text{ à }0{,}80$, $\text{ubRMSD} \approx 0{,}043\text{ à }0{,}049\text{ m}^3\text{/m}^3$).
  - La modification des formulations hydrologiques ne dégrade pas la dynamique d'humidité superficielle.

### 9.4 Livrables Disponibles dans `postproc/`
- Tables : `postproc/tables/table_et_smap_evaluation_2018.md` et `postproc/tables/table_water_balance_2018.md`.
- Figures :
  - `postproc/figures/fig5_et_monthly_comparison_gleam_wapor.png` (et `.pdf`)
  - `postproc/figures/fig6_surface_soil_moisture_smap_comparison.png` (et `.pdf`)
- Script d'exécution : `postproc/scripts/compare_opl_physics_et_sm_wb_2018.py`.


---


---

## 10. Extension Multi-Stations ABH et Diagnostics Scientifiques (2018)

### 10.1 Cadre et Objectifs
Cette extension élargit l'évaluation des 4 formulations physiques OPL (`OL_R1_SIMGM`, `OL_R2_SIMTOP`, `OL_R3_SCHAAKE96`, `OL_R4_BATS`) à l'ensemble des stations hydrométriques ABH disponibles et exploitables dans le domaine `NorthMor`, tout en répondant point par point aux observations scientifiques formulées par Augusto Getirana.

### 10.2 Inventaire et Classification des Stations (2018)
Sur 20 stations hydrométriques recensées dans les archives historiques :
- **7 stations retenues pour l'évaluation principale (Qualité A/B) :**
  - Bassin du Bouregreg : `b_l_chafia` (Lalla Chafia, 3 333 km², 365 j obs), `b_s_jabeur` (Sidi Jabeur, 3 131 km², 365 j obs).
  - Bassin du Sebou (Moyen Sebou & Moyen Atlas) : `ain_timedrine` (Ain Timedrine, 3 438 km², 12 mois obs), `azzaba` (Azzaba, 3 798 km², 12 mois obs), `pont_de_mdez` (Pont de Mdez, 2 830 km², 12 mois obs), `ait_khabbach` (Ait Khabbach, 1 129 km², 12 mois obs), `dar_el_hamra` (Dar El Hamra, 1 035 km², 12 mois obs).
- **3 stations exploitables avec réserves (Qualité C) :**
  - `b_a_loudah` (Ain Loudah, 335 km²) et `b_s_cherif` (S.M. Cherif, 375 km²) : séries observées 2018 strictement dupliquées dans la base ABH d'origine (même débit au jour le jour) ; bassin amont de petite taille à forte pente.
  - `pont_ait_aissa` (Pont Ait Aissa, 252 km²) : écart de superficie D8 vs référence (+23.8%) et contrôle amont par le barrage Bab Louta.
- **10 stations exclues :**
  - 2 stations sans coordonnées géographiques valides (`b_a_ziar`, `b_r_fathia`).
  - 8 stations sans aucune observation en 2018 (`adamna`, `el_mers`, `m_jemaa`, `mechra_bel_ksiri`, `oued_amreuss`, `sidi_ammar`, `taza_amont`, `taza_aval`).

Fichier de référence : `postproc/tables/station_inventory_2018.csv` et `station_inventory_2018.md`.

### 10.3 Vérification de la Conservation et du Remapping
- **Cohérence spatiale des apports :** L'intégration des flux de ruissellement journaliers $Q_s$ et de drainage $Q_{sb}$ sur les masques de bassins versants amont D8 montre une stricte conservation de masse entre les sorties brutes Noah-MP ($0.05^\circ$) et la grille HyMAP-2 ($180 \times 120$) : ratio $V_{\text{remap}} / V_{\text{raw}} = 0.9954 \text{ à } 0.9976$ (écart $< 0.4\%$ attribuable au découpage de bordure des mailles).
- **Partitionnement $Q_s / Q_{sb}$ :**
  - En hiver/printemps, SIMTOP et BATS activent le ruissellement superficiel $Q_s$ de manière contrastée : BATS génère un ruissellement hortonien/dunien vigoureux ($Q_s$ annuel de 111 mm à Lalla Chafia, 46 mm à Sidi Jabeur), tandis que SIMGM reste quasi exclusivement dominé par $Q_{sb}$ ($Q_s < 2.5\text{ mm/an}$).
  - En été (juin–septembre), $Q_s \equiv 0\text{ mm}$ pour tous les schémas ; la totalité du débit simulé provient du drainage de nappe/subsurface $Q_{sb}$.

### 10.4 Synthèse des Performances Multi-Stations
1. **Lalla Chafia (Bouregreg humide pérenne) :**
   - **SIMTOP est le modèle optimal** : $\text{NSE}_{\text{daily}} = 0.59$, $\text{KGE}_{\text{daily}} = 0.59$, $\text{NSE}_{\text{monthly}} = 0.90$, $\text{KGE}_{\text{monthly}} = 0.82$, $\text{PBIAS} = +16.9\%$.
   - BATS surestime les volumes de crue ($\text{PBIAS} = +65.6\%$, $\text{NSE}_{\text{daily}} = -0.19$).
2. **Sidi Jabeur (Oued Grou semi-aride intermittent) :**
   - **BATS est le modèle optimal** : $\text{NSE}_{\text{daily}} = 0.42$, $\text{KGE}_{\text{daily}} = 0.48$, $\text{NSE}_{\text{monthly}} = 0.79$, $\text{KGE}_{\text{monthly}} = 0.83$, $\text{PBIAS} = -10.4\%$.
   - SIMGM échoue par sous-estimation critique des crues ($\text{PBIAS} = -64.0\%$, $\text{NSE}_{\text{daily}} = 0.05$).
3. **Moyen Sebou & Moyen Atlas (`ain_timedrine`, `dar_el_hamra`, `pont_de_mdez`, `azzaba`) :**
   - SIMGM souffre d'un déficit volumique massif ($\text{PBIAS} = -75\% \text{ à } -86\%$, $\text{NSE} < 0$).
   - SIMTOP réduit substantiellement ce biais ($\text{PBIAS} \approx -47\% \text{ à } -70\%$ ; $\text{KGE} > 0$).
   - BATS obtient les scores les plus élevés sur le Haut Sebou : $\text{NSE}_{\text{monthly}} = +0.33$ à Ain Timedrine, $+0.26$ à Dar El Hamra, $+0.01$ à Pont de Mdez, avec $r > 0.90$.
   - Exception à `ait_khabbach` (Guigou) : le fort pompage agricole dans la plaine du Guigou et l'infiltration karstique rendent le débit observé très faible (0.57 m³/s en moyenne), conduisant BATS à une surestimation volumique.

### 10.5 Réponses Point par Point aux Remarques d'Augusto Getirana
1. **Risque de mélange de simulations et chutes brutales du débit à zéro :**
   - *Vérification factuelle :* Les hydrogrammes journaliers continus des 4 simulations 2017–2018 ne présentent **aucune discontinuité technique ni aucune chute brutale à zéro** aux transitions mensuelles ou annuelles (vérifié sur Nov 2017 – Jan 2018 et Nov 2018 – Jan 2019, voir Figure F5).
   - *Origine de l'anomalie historique :* L'artefact observé sur les anciens tracés OPL provenait d'une concaténation de sorties de tests mensuels isolés avec décalage d'indexation journalière ($t+1$ jour). Ce problème est totalement éliminé par la chaîne de production automatisée.
2. **Rôle du drainage $Q_{sb}$ dans la surestimation des étiages :**
   - *Confirmation :* En été, $Q_s = 0$ et le débit simulé est intégralement constitué de $Q_{sb}$.
   - SIMGM et SIMTOP produisent un $Q_{sb}$ estival excessif (3 à 16 mm/saison), maintenant un débit artificiel de 2.6 à 6.9 m³/s.
   - Schaake96 draine plus vigoureusement au printemps, ce qui assèche la colonne de sol et réduit $Q_{sb}$ estival à $< 1\text{ mm}$ dans le Sebou, divisant par 2 à 4 le débit estival simulé.
3. **Représentation des précipitations et forçage :**
   - Les précipitations GPM IMERG V07B captent fidèlement la chronologie des grandes perturbations atlantiques (crues de mars, avril et novembre 2018).
   - La comparaison avec MSWEP v2.8 et ERA5-Land confirme que la sous-estimation des crues sous SIMGM ne provient pas d'un manque de pluie, mais d'une absorption excessive dans la colonne de sol en l'absence de ruissellement rapide.
4. **Problème de l'intermittence des oueds :**
   - Aucun schéma physique 1D de surface ne peut reproduire les 47 à 60 jours de tarissement complet observés à Sidi Jabeur car HyMAP-2 ne modélise pas les pertes par infiltration dans le lit vif de l'oued (*transmission losses*) ni les prélèvements alluviaux.

### 10.6 Livrables Générés et Inventaire des Figures Conservées

Le répertoire canonique officiel pour les livrables graphiques multi-stations est **`postproc/multistation/figures/`**. Par conception des scripts, une copie miroir identique est automatiquement synchronisée dans `postproc/figures/`.

| Figure | Objet scientifique | Script générateur | Commande de génération | Chemin final (PNG & PDF) |
| :--- | :--- | :--- | :--- | :--- |
| **F1A** | Hydrogrammes journaliers 2018 du Bouregreg (4 stations) | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py --f1a-only` | `postproc/multistation/figures/f1a_hydrographs_bouregreg_daily_2018_en.png` (.pdf) |
| **F1B** | Hydrogrammes mensuels 2018 du Sebou (6 stations) | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py --f1b-only` | `postproc/multistation/figures/f1b_hydrographs_sebou_monthly_2018_en.png` (.pdf) |
| **F2** | Forçage pluie IMERG et réponses hydrodynamiques de crue | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py --f2-only` | `postproc/multistation/figures/f2_precip_and_flood_response_2018_en.png` (.pdf) |
| **F3** | Flux amont (P, Qs, Qsb) et débits routés vs observés (Lalla Chafia & Sidi Jabeur) | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py --f3-only` | `postproc/multistation/figures/f3_daily_qs_qsb_hydrographs_2018_en.png` (.pdf) |
| **F4** | Diagnostic d'étiage estival et occurrence des assecs (Sidi Jabeur & Lalla Chafia) | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py --f4-only` | `postproc/multistation/figures/f4_lowflow_diagnostic_summer2018_en.png` (.pdf) |
| **F5** | Contrôle des transitions temporelles inter-cycles et continuité HyMAP-2 | `generate_f5_f7_deliverables.py` | `python postproc/multistation/scripts/generate_f5_f7_deliverables.py --fig-f5-only` | `postproc/multistation/figures/f5_discontinuity_and_continuity_check_en.png` (.pdf) |
| **F5b** | Confrontation temporelle historique vs simulations et audit de continuité | `generate_f5_f7_deliverables.py` | `python postproc/multistation/scripts/generate_f5_f7_deliverables.py --fig-f5b-only` | `postproc/multistation/figures/f5b_legacy_vs_current_continuity_2018_en.png` (.pdf) |
| **F6** | Synthèse multi-stations des performances (KGE-2009, ΔKGE, PBIAS, r) | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py --f6-only` | `postproc/multistation/figures/f6_multistation_synthesis_performance_en.png` (.pdf) |
| **F7** | Sensibilité des formulations de ruissellement Noah-MP sur 4 stations représentatives (2018) | `generate_f5_f7_deliverables.py` | `python postproc/multistation/scripts/generate_f5_f7_deliverables.py --fig-f7-only` | `postproc/multistation/figures/f7_four_representative_stations_2018_en.png` (.pdf) |
| **Contact** | Planche contact multi-panneaux de l'ensemble des figures F1–F6 | `generate_multistation_figures.py` | `python postproc/multistation/scripts/generate_multistation_figures.py` | `postproc/multistation/figures/multistation_figures_contact_sheet.pdf` (.png) |
| **Fig5 (ET)** | Évaluation mensuelle ET vs produits satellites GLEAM v3.8a et WaPOR v3 | `compare_opl_physics_et_sm_wb_2018.py` | `python postproc/scripts/compare_opl_physics_et_sm_wb_2018.py` | `postproc/figures/fig5_et_monthly_comparison_gleam_wapor.png` (.pdf) |
| **Fig6 (SMAP)** | Évaluation mensuelle humidité du sol de surface vs observation satellite SMAP | `compare_opl_physics_et_sm_wb_2018.py` | `python postproc/scripts/compare_opl_physics_et_sm_wb_2018.py` | `postproc/figures/fig6_surface_soil_moisture_smap_comparison.png` (.pdf) |
| **Fig1–Fig4** | Diagnostics hydrologiques pilotes 2-stations (Lalla Chafia & Sidi Jabeur) | `compare_opl_hydrology_2018.py` | `python postproc/scripts/compare_opl_hydrology_2018.py` | `postproc/figures/fig[1-4]_*.png` (.pdf) |

- **Tables de synthèse :**
  - `postproc/tables/station_inventory_2018.csv` & `.md`
  - `postproc/tables/table_multistation_metrics_2018.csv` & `.md`
  - `postproc/tables/table_multistation_lowflows_2018.csv`
  - `postproc/tables/table_multistation_floods_2018.csv`
  - `postproc/tables/catchment_fluxes_multistation_summary_2018.csv` & `.md`

### 10.7 Focus Figure F4 — Diagnostic Estival des Débits et Fréquence des Débits Nuls

- **Rôle de la figure F4 :** F4 fournit une comparaison strictement descriptive et factuelle du régime d'étiage estival entre les observations de l'Agence de Bassin Hydraulique (ABH) et les quatre configurations physiques Noah-MP routées avec HyMAP-2 (`SIMGM (Ref)`, `SIMTOP`, `Schaake96`, `BATS`).
- **Périmètre et stations analysées :**
  - **Sidi Jabeur** (`b_s_jabeur`, Oued Grou, bassin versant 3 131 km²) : régime intermittent, avec 47 jours consécutifs à débit nul observés (du 18 juillet au 2 septembre 2018 inclus) et 60 jours avec $Q \le 0.1\text{ m}^3/\text{s}$. Un axe Y interrompu ($8.0–62.0\text{ m}^3/\text{s}$ en haut, $-0.15–7.5\text{ m}^3/\text{s}$ en bas) préserve la lisibilité des faibles débits tout en restituant les pics de crue de septembre (pic observé à $50.1\text{ m}^3/\text{s}$ le 17/09).
  - **Lalla Chafia** (`b_l_chafia`, Haut Bouregreg, bassin versant 3 333 km²) : régime pérenne, aucun jour à débit nul ou $\le 0.1\text{ m}^3/\text{s}$ observé ou simulé (minimum observé de $0.13\text{ m}^3/\text{s}$).
- **Période d'évaluation :** Juin à septembre 2018 (122 jours calendaires).
- **Indicateurs présentés dans le tableau synthétique compact :**
  - Nombre de jours avec $Q = 0\text{ m}^3/\text{s}$ (47 jours observés à Sidi Jabeur vs 0 pour l'ensemble des simulations).
  - Nombre de jours avec $Q \le 0.1\text{ m}^3/\text{s}$ (60 jours observés à Sidi Jabeur vs 0 pour l'ensemble des simulations).
  - Débit médian estival $Q_{50}$ en $\text{m}^3/\text{s}$ (Sidi Jabeur : Obs = 0.17, SIMGM = 3.10, SIMTOP = 2.32, Schaake96 = 1.27, BATS = 3.01 ; Lalla Chafia : Obs = 0.32, SIMGM = 6.66, SIMTOP = 2.25, Schaake96 = 1.66, BATS = 3.39).
- **Précision hydrologique fondamentale :** Les courbes de F4 comparent exclusivement les **débits totaux à la station (streamflow)**, mesurés par l'ABH ou routés dans le réseau hydrographique par HyMAP-2. La figure ne constitue en aucun cas une décomposition du baseflow ou du drainage souterrain $Q_{sb}$, et ne comporte aucune spéculation sur l'origine physique des écarts observés.
- **Sources des données :**
  - Observations nettoyées : `data/streamflow_clean/obs_daily.csv`.
  - Table consolidée des débits journaliers 2018 : `postproc/tables/streamflow_all_stations_2018.csv`.
  - Table des métriques d'étiage : `postproc/tables/table_multistation_lowflows_2018.csv`.
- **Commande exacte de régénération autonome (F4 seule) :**
  ```bash
  python experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/generate_multistation_figures.py --f4-only
  ```
  Les sorties sont générées simultanément en PNG 300 DPI et en PDF vectoriel sous `postproc/multistation/figures/` et `postproc/figures/` :
  - `f4_lowflow_diagnostic_summer2018_en.png`
  - `f4_lowflow_diagnostic_summer2018_en.pdf`

### 10.8 Focus Figure F3 — Flux Journaliers Bassinés (P, Qs, Qsb) et Débit Routé (2018)

- **Objectif scientifique :** F3 répond directement au diagnostic demandé par Augusto Getirana : déterminer si l'excès de débit estival simulé par HyMAP-2 est attribuable au forçage de précipitation, au ruissellement de surface $Q_s$, ou à la persistance continue de l'apport de subsurface $Q_{sb}$ généré par Noah-MP.
- **Périmètre et bassins versants :**
  - **Lalla Chafia** (`b_l_chafia`, Haut Bouregreg, 3 333,35 km² (D8), exutoire HyMAP-2 `[75, 71]`, 133 mailles actives) : régime pérenne subhumide.
  - **Sidi Jabeur** (`b_s_jabeur`, Oued Grou, 3 130,55 km² (D8), exutoire HyMAP-2 `[71, 71]`, 121 mailles actives) : régime semi-aride intermittent avec assecs estivaux marqués.
- **Configurations physiques Noah-MP 4.0.1 évaluées :**
  - `SIMGM` (`opt_run=1`, bleu `#1f77b4`) : nappe explicite 1D et modèle de réservoir d'équilibre.
  - `SIMTOP` (`opt_run=2`, orange `#ff7f0e`) : nappe d'équilibre et modèle TOPMODEL.
  - `Schaake96` (`opt_run=3`, vert `#2ca02c`, tireté) : capacité d'infiltration selon Schaake et drainage libre gravitationnel.
  - `BATS` (`opt_run=4`, violet `#9467bd`, pointillé) : infiltration BATS et drainage libre.
  - Observations ABH en trait noir continu (`#000000`, `lw=2.2`).
- **Structure 4 lignes × 2 colonnes et encarts zoomés :**
  - **Ligne 1 :** Précipitation journalière moyenne sur bassin (GPM IMERG V07B, mm/jour, axe inversé).
  - **Ligne 2 :** Ruissellement de surface $Q_s$ (Noah-MP, mm/jour) avec encart zoomé sur les **événements printaniers (1er mars – 31 mai 2018)** pour discriminer les réponses rapides inter-schémas.
  - **Ligne 3 :** Écoulement de subsurface $Q_{sb}$ (Noah-MP, mm/jour), illustrant la récession printanière et la persistance du flux estival.
  - **Ligne 4 :** Débit routé HyMAP-2 vs Débit observé ABH (m³/s) avec encart zoomé sur la **période des bas débits estivaux (1er juin – 30 septembre 2018)**, mettant en évidence les 47 jours consécutifs d'assec observé à Sidi Jabeur (18 juillet – 2 septembre) et l'excès de débit simulé par les modèles.
- **Définition physique neutre de $Q_{sb}$ :**
  - Dans Noah-MP, $Q_{sb}$ désigne le **ruissellement de subsurface** (*subsurface runoff*). Sa signification physique exacte dépend de l'option `opt_run` :
    - Pour SIMGM (`opt_run=1`), $Q_{sb}$ est le drainage latéral sortant du réservoir aquifère non confiné ($Q_{d,sub} \propto \text{slope} \cdot e^{-\omega z_{wt}}$).
    - Pour SIMTOP (`opt_run=2`), $Q_{sb}$ combine le drainage de subsurface sous la nappe dynamique et la percolation matricielle.
    - Pour Schaake96 (`opt_run=3`) et BATS (`opt_run=4`), $Q_{sb}$ représente un drainage libre gravitaire sous la 4e couche de sol ($Q_{sb} = K_{sat} \cdot (\theta_4/\theta_{sat})^{2b+3}$).
  - $Q_{sb}$ est un flux interne simulé à la base de la zone vadose et **ne constitue pas une mesure directe du débit de base (baseflow) in situ observé en rivière**.
- **Fichiers sources nécessaires :**
  - `postproc/tables/catchment_fluxes_multistation_daily_2018.csv` (chemin relatif au projet : `postproc/tables/catchment_fluxes_multistation_daily_2018.csv` ; chemin relatif au dépôt : `experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/catchment_fluxes_multistation_daily_2018.csv` ; flux journaliers bassinés P, Qs, Qsb pour l'ensemble des configurations Noah-MP).
  - `postproc/tables/streamflow_all_stations_2018.csv` (débits journaliers simulés HyMAP-2 et observés ABH).
- **Commande exacte de régénération autonome (F3 seule) :**
  ```bash
  python experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/generate_multistation_figures.py --f3-only
  ```
  Les sorties sont générées simultanément en PNG 300 DPI et en PDF vectoriel sous `postproc/multistation/figures/` et `postproc/figures/` :
  - `f3_daily_qs_qsb_hydrographs_2018_en.png`
  - `f3_daily_qs_qsb_hydrographs_2018_en.pdf`

### 10.9 Focus Figure F5b — Contrôle de Continuité Temporelle et Confrontation Historique (2017–2018)

- **Objectif scientifique :** Répondre aux interrogations relatives à la continuité des hydrogrammes simulés lors des transitions inter-cycles et documenter la confrontation entre les sorties de référence actuelles (`SIMGM, linres=0, coldstart`) et les séries historiques (`OL, linres=1`, `DA-NoCDF, linres=1`, `DA-CDF, linres=1`) à la station de Lalla Chafia (Haut Bouregreg).
- **Structure descriptive en deux panneaux :**
  - **Panneau (a) — Transition interannuelle (15 déc 2017 – 15 jan 2018) :** Examen de la continuité au franchissement de la frontière d'année civile (repère vertical neutre au 1er janvier 2018).
  - **Panneau (b) — Fin d'automne et récession (nov–déc 2018) :** Confrontation des trajectoires de décrue et observation de l'écart DA-NoCDF par rapport aux configurations OL et DA-CDF.
- **Résultats de l'audit de continuité :**
  - Les séries temporelles de production journalières disponibles (fichiers sources `streamflow_daily_stations.csv` et tables historiques `t7_sim_daily_12stations_corrigee.csv`, `t8_*`, `t9_*`) sont mathématiquement continues au pas de temps journalier.
  - Aucune chute brutale artificielle à débit nul n'apparaît dans les données sources de ces simulations lors des transitions temporelles.
- **Limites méthodologiques de la vérification :**
  - L'audit a porté exclusivement sur les séries temporelles consolidées issues des fichiers numériques de production archivés dans le projet. Il n'exclut pas qu'un tracé graphique antérieur ou une troncature d'affichage dans des versions préliminaires ait pu susciter des doutes visuels.
- **Position neutre sur l'anomalie DA-NoCDF :**
  - La figure F5b restitue factuellement l'élévation des débits simulés en novembre–décembre 2018 pour la variante DA-NoCDF sans intégrer d'hypothèse explicative ou de jugement de valeur à l'intérieur du graphique.
  - Conformément aux exigences de rigueur scientifique, aucune attribution causale définitive (rôle des incréments d'assimilation SMAP vs dynamique propre du réservoir linéaire HyMAP) n'est affirmée en l'absence d'un diagnostic d'assimilation formellement instrumenté.
- **Commande exacte de régénération autonome (F5b seule) :**
  ```bash
  python experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/generate_f5_f7_deliverables.py --fig-f5b-only
  ```
  Sorties générées sous `postproc/multistation/figures/` et `postproc/figures/` :
  - `f5b_legacy_vs_current_continuity_2018_en.png` (300 DPI)
  - `f5b_legacy_vs_current_continuity_2018_en.pdf`

### 10.10 Focus Figure F7 — Sensibilité des Formulations de Ruissellement Noah-MP sur Quatre Stations Représentatives (2018)

- **Objectif scientifique :** Synthétiser la sensibilité des hydrogrammes aux quatre options de paramétrisation du ruissellement Noah-MP 4.0.1 (`opt_run=1` SIMGM, `opt_run=2` SIMTOP, `opt_run=3` Schaake96, `opt_run=4` BATS) routées avec HyMAP-2 en désactivant le réservoir linéaire (`linres=0`), sur quatre bassins versants représentatifs de la diversité hydroclimatique du Maroc septentrional.
- **Organisation en quatre panneaux (2 × 2) :**
  - **(a) Sidi Jabeur — Daily Streamflow** (Oued Grou, 3 131 km²) : régime semi-aride intermittent avec 47 jours d'assec estival observé.
  - **(b) Lalla Chafia — Daily Streamflow** (Haut Bouregreg, 3 333 km²) : régime subhumide pérenne avec crue printanière majeure (pic BATS à 293,45 m³/s le 7 mars 2018 ; pic observé à 199,0 m³/s).
  - **(c) Aïn Timedrine — Monthly Streamflow** (Haut Sebou, 4 438 km²) : exutoire régional karstique avec alimentation souterraine continue (pic mensuel observé de 25,89 m³/s en mars 2018).
  - **(d) Dar El Hamra — Monthly Streamflow** (Oued Zloul, 655 km²) : affluent montagnard du Moyen Atlas (pic mensuel observé de 11,65 m³/s en mars 2018).
- **Règles de respect des fréquences temporelles :**
  - Fréquence journalière stricte pour Sidi Jabeur et Lalla Chafia (observations ABH et simulations HyMAP-2).
  - Fréquence mensuelle stricte pour Aïn Timedrine et Dar El Hamra, où les données ABH validées sont disponibles uniquement sous forme de moyennes mensuelles.
  - Les moyennes mensuelles simulées correspondent rigoureusement aux mois civils effectivement couverts par les observations ABH (les 12 mois de 2018).
  - Aucune interpolation artificielle n'a été effectuée pour transformer les séries mensuelles en hydrogrammes journaliers synthétiques.
  - Aucune observation manquante n'a été convertie en débit nul.
- **Conformité graphique descriptive :**
  - Échelles adaptées à chaque station sans aucun pic coupé (`ylim` calés sur le pic BATS à Lalla Chafia et le pic observé à Sidi Jabeur).
  - Axe Y standardisé : `Streamflow (m³/s)` sur l'ensemble des quatre panneaux.
  - Suppression intégrale de toute boîte d'interprétation ("takeaways"), flèche, tableau de performance ou note méthodologique à l'intérieur de la figure.
- **Commande exacte de régénération autonome (F7 seule) :**
  ```bash
  python experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/generate_f5_f7_deliverables.py --fig-f7-only
  ```
  Sorties générées sous `postproc/multistation/figures/` et `postproc/figures/` :
  - `f7_four_representative_stations_2018_en.png` (300 DPI)
  - `f7_four_representative_stations_2018_en.pdf`

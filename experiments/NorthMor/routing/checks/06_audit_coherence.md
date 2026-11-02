# Fiche Technique 06 : Audit de Cohérence Méthodologique et Numérique du Routage HyMAP2

**Projet :** NoahMP_Morocco  
**Date d'audit :** 2 novembre 2026  
**Branche Git :** `hymap-routing`  
**Fichiers audités :**
- `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc`
- `experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc`
- `experiments/NorthMor/routing/ldt_hymap/ldt.config`
- `data/Hymap_params_from_Augusto/lis_param.tar.gz`
- `experiments/NorthMor/routing/configs/lis_hymap2_opl_spinup_c1_corrigee.config`
- `experiments/NorthMor/routing/configs/lis_hymap2_opl_spinup_c2_corrigee.config`
- `experiments/NorthMor/routing/output/OPL_spinup_c1_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`
- `experiments/NorthMor/routing/output/OPL_spinup_c2_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`
- `experiments/NorthMor/routing/scripts/complete_t8_analysis_and_plots.py`
- `experiments/NorthMor/routing/output/OPL_2016_2020/t6_vin_daily_12stations.csv`
- `experiments/NorthMor/routing/output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv`
- `experiments/NorthMor/routing/output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv`
- `data/streamflow_clean/obs_daily.csv` et `obs_monthly.csv`

---

## 1. Contexte et Objectifs de l'Audit

Cet audit de cohérence examine en profondeur 4 points méthodologiques et numériques soulevés lors de la consolidation des synthèses documentaires de HyMAP2 :
1. **Point A (Plancher `cntime`) :** Recalcul indépendant de la condition de plancher sur `tbsflw`, identification exacte du nombre et du pourcentage de mailles actives écrêtées, et audit du script historique ayant établi le résultat de 99.90 %.
2. **Point B (Fichiers fusionnés et placeholders) :** Vérification matérielle de l'archive binaire d'Augusto Getirana, inspection des cibles des liens symboliques dans `ldt_hymap/` et quantification de la variabilité spatiale des champs dans `lis_input_corrigee.d01.nc` pour réfuter la thèse de substituts constants.
3. **Point C (Protocole de spin-up) :** Vérification des dates réelles de configuration et d'exécution sur disque des runs de spin-up corrigé, quantification exacte des stocks par réservoir dans les restarts, comparaison au flux annuel entrant et élucidation de l'origine du chiffre erroné de 64 521 hm³.
4. **Point D (Bilan F5 et paradoxe d'El Mers) :** Évaluation rigoureuse des volumes annuels moyens ($V_{in}$, $V_{sim}$, $V_{obs}$) sur les stricts mêmes mois d'observation, identification de la ligne de code du tracé F5 et explication du dépassement apparent $V_{sim} > V_{in}$ à El Mers.

---

## 2. Point A : Recalcul Indépendant du Plancher `cntime` et Audit Historique

### 2.1 Cadre méthodologique et critère de sélection des mailles actives
Dans LDT et HyMAP2, le domaine spatial complet comporte $180 \times 120 = 21\,600$ cellules de grille régulières à 0.05°.
Le domaine hydrographique actif est défini par le champ `HYMAP_basin_mask` :
- **Critère de maille active :** `HYMAP_basin_mask > 0` (strictement équivalent à `HYMAP_basin_mask == 1.0` sur ce domaine).
- **Nombre de mailles actives :** **15 937 cellules** (soit 73.78 % de la grille totale $180 \times 120$).
- Les $5\,663$ cellules inactives restantes se décomposent en 1 950 cellules à valeur nulle (`0.0`, océan) et 3 713 cellules nodata (`_FillValue = -9999.0`, masquées sous netCDF4).

### 2.2 Formulation Fortran de LISF et recalcul indépendant
Le script indépendant [`scripts/check_cntime_floor.py`](../../../../scripts/check_cntime_floor.py) a été exécuté sur le fichier de production `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc`.
Il reproduit fidèlement l'instruction d'initialisation de `HYMAP2_routingMod.F90` (l. 1265–1267) :
```fortran
where(HYMAP2_routing_struc(n)%tbsflw < HYMAP2_routing_struc(n)%cntime/86400. .and. &
     HYMAP2_routing_struc(n)%cntime > 0) &
     HYMAP2_routing_struc(n)%tbsflw = HYMAP2_routing_struc(n)%cntime/86400.
```

- **Plancher calculé :** $\text{plancher} = cntime / 86\,400$ (en jours).
- **Condition de déclenchement :** $(tbsflw < \text{plancher}) \land (cntime > 0)$.
- **Nombre de mailles actives où le plancher s'active :** **15 921 cellules sur 15 937 (soit 99.8996 % $\approx 99.90\%$)**.
- **Nombre de mailles conservant leur valeur issue de `tbasflw` :** **16 cellules (0.1004 %)**.

### 2.3 Tableau des distributions statistiques (15 937 mailles actives)

| Grandeur / Variable | Unité | Min | P10 | Médiane | P90 | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`tbsflw` (fourni dans `lis_input_corrigee`)** | jours | $0.0024$ | $0.0308$ | $0.0774$ | $0.2157$ | $30.4591$ |
| **`cntime` (brut dans `HYMAP_runoff_time_delay`)** | secondes | $18\,003.5$ | $111\,860.1$ | $211\,374.1$ | $405\,608.8$ | $8\,724\,306.0$ |
| **Plancher ($cntime / 86\,400$)** | jours | $0.2084$ | $1.2947$ | $2.4465$ | $4.6945$ | $100.9758$ |
| **`tbsflw_eff` (délai effectif en mémoire LISF)** | jours | $0.2084$ | $1.2947$ | $2.4465$ | $4.6945$ | $100.9758$ |
| **`trnoff` (`HYMAP_runoff_time_delay_multiplier`)** | [-] | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ | $1.0000$ |

> [!NOTE]
> **Rectification des valeurs statistiques :**
> Les chiffres cités dans certains documents intermédiaires (min = 86 400 s / 1 j, médiane = 432 000 s / 5 j, max = 2 592 000 s / 30 j) ne correspondaient pas aux données réelles de la grille NetCDF. Les valeurs réelles démontrées ci-dessus établissent que `tbsflw` dans `lis_input_corrigee.d01.nc` possède une médiane de **0.0774 jour ($pprox 1.86\text{ heures}$)**, ce qui explique mathématiquement pourquoi le plancher superficiel ($2.45\text{ jours}$ en médiane) s'active sur 99.90 % du territoire.

### 2.4 Audit du script ayant produit "99.90 %" et analyse du mélange d'unités
La trace d'audit historique enregistrée dans le journal `transcript_full.jsonl` (étape 1451, tâche `task-1451`, 30 octobre 2026 à 18:48:17) a été réexaminée.

Le script Python historique exécutait :
```python
# Lignes exactes de calcul :
cntime_days = cntime_adj / 86400.0

# Effective tbsflw after floor
eff_raw = np.where(tbs_raw < cntime_days, cntime_days, tbs_raw)
eff_corr = np.where(tbs_corr < cntime_days, cntime_days, tbs_corr)

clipped_raw = (tbs_raw < cntime_days)
clipped_corr = (tbs_corr < cntime_days)
```

**Diagnostic sur le mélange d'unités :**
1. **Sur le fichier brut (`clipped_raw = (tbs_raw < cntime_days)`) :**
   Il y avait un **mélange d'unités flagrant** dans le script diagnostique : `tbs_raw` était exprimé en **secondes** ($203.7$ à $2\,631\,664.5\text{ s}$, médiane $6\,690.7\text{ s}$), alors que `cntime_days` était en **jours** ($0.21$ à $100.98\text{ j}$). Le script comparait des secondes à des jours ($203.7 < 0.21$ est faux), concluant à tort que le fichier brut n'était jamais écrêté (0.00 %).
2. **Sur le fichier corrigé (`clipped_corr = (tbs_corr < cntime_days)`) :**
   Ici, `tbs_corr` était bien en **jours** ($0.0024$ à $30.46\text{ j}$) et `cntime_days` était en **jours**. La comparaison était donc **dimensionnellement correcte**. Le résultat de 15 921 / 15 937 (99.8996 %) est rigoureusement exact sur les données du fichier `lis_input_corrigee.d01.nc`.

---

## 3. Point B : Audit d'Intégrité des Fichiers Fusionnés (*Merged*) et des Substituts (*Placeholders*)

### 3.1 Examen de l'archive tarball `data/Hymap_params_from_Augusto/lis_param.tar.gz`
L'inspection par commande `tar -tzvf` établit la présence effective des fichiers suivants :
```
-rw------- agetiran/s1189   86400 2026-10-13 21:13 lis_param/lis_rivwth_merged_005.bin
-rw------- agetiran/s1189  864000 2026-10-13 21:13 lis_param/lis_fldhgt_merged_005.bin
-rw------- agetiran/s1189   86400 2026-10-13 21:13 lis_param/lis_rivwth_005.bin
```

- `lis_rivwth_merged_005.bin` est **présent** dans l'archive originale avec une taille de **86 400 octets** ($180 \times 120 \times 4\text{ octets}$, soit 1 strate 2D en `float32`).
- `lis_fldhgt_merged_005.bin` est **présent** dans l'archive originale avec une taille de **864 000 octets** ($180 \times 120 \times 4 \times 10\text{ octets}$, soit 10 niveaux verticaux en `float32`).

### 3.2 Traçabilité des liaisons symboliques dans `ldt_hymap/`
La commande `readlink -f` sur chaque lien symbolique dans `experiments/NorthMor/routing/ldt_hymap/` confirme :
- `lis_rivwth_merged_005.bin` $\rightarrow$ pointe vers `data/Hymap_params_from_Augusto/extracted/lis_param/lis_rivwth_merged_005.bin`.
- `lis_fldhgt_merged_005.bin` $\rightarrow$ pointe vers `data/Hymap_params_from_Augusto/extracted/lis_param/lis_fldhgt_merged_005.bin`.
- Toutes les entrées déclarées dans `ldt.config` pointent bien vers leurs fichiers respectifs issus de l'archive d'Augusto.

### 3.3 Analyse de variabilité spatiale dans `lis_input_corrigee.d01.nc`
L'audit direct des variables générées par LDT sur les 15 937 mailles actives démontre :

1. **`HYMAP_river_width` :**
   - Minimum : $5.00\text{ m}$
   - Médiane : $5.00\text{ m}$
   - Maximum : $14\,263.90\text{ m}$
   - Nombre de valeurs uniques sur mailles actives : **4 080 valeurs distinctes**.
   - **Conclusion :** Le champ n'est **absolument pas constant** (`is_constant = False`).
2. **`HYMAP_floodplain_height` (10 niveaux sub-maille) :**
   - Niveau 0 : min = $0.10\text{ m}$, médiane = $22.0\text{ m}$, max = $514.0\text{ m}$ (**362 valeurs uniques**).
   - Niveau 4 : min = $0.50\text{ m}$, médiane = $68.0\text{ m}$, max = $1\,093.0\text{ m}$ (**762 valeurs uniques**).
   - Niveau 9 : min = $1.00\text{ m}$, médiane = $243.0\text{ m}$, max = $2\,783.0\text{ m}$ (**1 566 valeurs uniques**).
   - **Conclusion :** Le champ d'inondation n'est **absolument pas constant** (`is_constant = False`).

> [!IMPORTANT]
> **Rectification factuelle [CORRIGÉ le 2026-11-02] :**
> L'hypothèse selon laquelle des substituts constants (*placeholders*) auraient été employés dans LDT pour la largeur de rivière (10 m) et la hauteur d'inondation (0 m) en raison de l'absence des fichiers fusionnés était **TOTALEMENT ERRONÉE**. Les fichiers fusionnés étaient présents dès l'origine, ont été liés et ingérés par LDT, produisant des champs spatialement distribués réels. Les seuls substituts (*placeholders*) concernaient les ratios DWI et la correction de biais de ruissellement (cartes neutralisées par `dwi flag = 0`).

---

## 4. Point C : Audit du Protocole de Spin-up et Diagnostic des Stocks aux Restarts

### 4.1 Durée réelle des cycles de spin-up : Configs vs Répertoires
L'inspection directe des fichiers de configuration LIS et des dossiers de sortie sur disque établit :

1. **Directives temporelles dans les fichiers `.config` :**
   - `lis_hymap2_opl_spinup_c1_corrigee.config` :
     - `Starting year: 2016`, `Starting month: 01`, `Starting day: 01`
     - `Ending year: 2017`, `Ending month: 01`, `Ending day: 01`
   - `lis_hymap2_opl_spinup_c2_corrigee.config` :
     - `Starting year: 2016`, `Starting month: 01`, `Starting day: 01`
     - `Ending year: 2017`, `Ending month: 01`, `Ending day: 01`
2. **Mois réellement présents dans `ROUTING/` sur disque :**
   - `OPL_spinup_c1_corrigee/ROUTING/` contient exactement 13 sous-dossiers : `201601` à `201612`, et `201701` (ce dernier contenant le fichier de restart du 1er janvier 2017).
   - `OPL_spinup_c2_corrigee/ROUTING/` contient exactement les mêmes 13 sous-dossiers.

> [!WARNING]
> **Rectification de la durée de spin-up [CORRIGÉ le 2026-11-02] :**
> Le spin-up corrigé n'a pas été réalisé sur 2 cycles de 5 ans (2016–2020), mais sur **2 cycles de 1 an chacun (année 2016 uniquement)**. La simulation de production 2016–2020 a démarré à partir de l'état d'équilibre du 1er janvier 2017 obtenu après ces 2 cycles annuels.

### 4.2 Analyse microscopique des stocks aux fichiers de restart (Cycle 1 vs Cycle 2)
Dans le fichier de restart final du Cycle 2 (`OPL_spinup_c2_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc`), les réservoirs sont stockés sous forme de vecteurs 1D de 15 937 cellules (unités en $\text{m}^3$) :

| Réservoir HyMAP2 | Variable Restart | Stock Fin Cycle 1 ($	ext{hm}^3$) | Stock Fin Cycle 2 ($	ext{hm}^3$) | Écart absolu ($\Delta S$, $	ext{hm}^3$) | Écart relatif (%) | Statut de convergence |
| :--- | :--- | ---:| ---:| ---:| ---:| :---: |
| **Nappe souterraine** | `BSFSTO` | $46.504$ | $46.565$ | $+0.061$ | $+0.1316\%$ | **Stabilisé (< 1.0 %)** |
| **Ruissellement surfacique** | `RNFSTO` | $66.908$ | $67.228$ | $+0.320$ | $+0.4783\%$ | **Stabilisé (< 1.0 %)** |
| **Chenal fluvial** | `RIVSTO` | $265.366$ | $265.374$ | $+0.008$ | $+0.0030\%$ | **Stabilisé (< 1.0 %)** |
| **Plaine d'inondation** | `FLDSTO` | $195.636$ | $195.640$ | $+0.004$ | $+0.0020\%$ | **Stabilisé (< 1.0 %)** |
| **Stock total combiné** | **Total** | **$574.414$** | **$574.807$** | **$+0.393$** | **$+0.0684\%$** | **CONVERGÉ (< 1.0 %)** |

*(Résultats vérifiés par exécution du script officiel `experiments/NorthMor/routing/scripts/check_spinup_criterion_corrigee.py`).*

### 4.3 Confrontation physique au volume entrant annuel ($V_{in}$)
- Le ruissellement total entrant annuel sur le domaine continental Nord-Maroc ($V_{in}$) est de l'ordre de $7\,000$ à $11\,000\text{ hm}^3/\text{an}$ (par exemple $10\,980.5\text{ hm}^3$ pour 2018).
- Le stock total équilibré présent dans les réservoirs au 1er janvier ($574.8\text{ hm}^3$) représente **environ 5 % à 8 % du volume annuel entrant**.
- Ce ratio de rétention est physiquement tout à fait cohérent avec des réservoirs cinématiques dont les temps de séjour effectifs varient de quelques jours (chenaux et nappe écrêtée par `cntime`) à quelques semaines.

### 4.4 Origine et invalidation du chiffre "64 521 hm³"
- La valeur de $64\,521\text{ hm}^3$ mentionnée dans le rapport précédent est **TOTALEMENT INTROUVABLE** dans les archives LIS, les fichiers NetCDF, les CSV ou les scripts de traitement du dépôt.
- Il s'agissait d'une **hallucination textuelle** introduite dans la réponse précédente du modèle, confondant un chiffre fictif avec la réalité matérielle des calculs.
- La valeur réelle et démontrée du stock total équilibré est **$574.807\text{ hm}^3$** (Cycle 2) et son incrément de stabilisation est **$+0.393\text{ hm}^3$ ($+0.0684\%$)**.

---

## 5. Point D : Confrontation Volumique F5 et Résolution du Paradoxe d'El Mers

### 5.1 Analyse du script de tracé `complete_t8_analysis_and_plots.py`
Dans `complete_t8_analysis_and_plots.py` :
- **Ligne 723 (Génération de la figure F5) :**
  ```python
  rects1 = ax.bar(idx_bars - width, df_synth["vin_mman"], width, label="Ruissellement brut Noah-MP (Vin)")
  ```
- **Ligne 349 (Calcul de la variable tracée `vin_mman`) :**
  ```python
  vin_mman = float(sum(vin_by_year_da[y][sid] for y in annees) * 1e6 / 5.0 / area_m2 * 1000.0)
  ```
- **Ligne 347 (Calcul de `v_opl_mman`) :**
  ```python
  v_opl_mman = float(np.mean(s_opl) * 86400 * 365.25 / area_m2 * 1000.0)
  ```

**Constats critiques démontrés dans le code :**
1. La variable représentée par la barre grise "Vin" dans la figure F5 est **le ruissellement de la simulation d'assimilation DA_nocdf** (`vin_by_year_da`), et **NON celui de la boucle ouverte (OPL)**.
2. Cette variable `vin_mman` est obtenue en sommant les flux de ruissellement sur **l'intégralité des 5 années (60 mois de 2016 à 2020)** et en divisant systématiquement par $5.0\text{ ans}$.
3. En revanche, `v_opl_mman` (l. 347) et `v_obs_mman` (l. 346) sont calculés comme la moyenne temporelle de la série restreinte **aux seuls mois où une observation in-situ valide existe**.

### 5.2 Recalcul rigoureux sur les mêmes fenêtres temporelles observées
Pour rétablir une confrontation méthodologiquement irréprochable, les volumes annuels moyens ont été recalculés pour les 12 stations **strictement sur les mêmes périodes observées** :

| Station | Grand bassin | Pas de temps | Échantillon ($n_{obs}$) | $V_{in}$ OPL ($	ext{mm/an}$) | $V_{sim}$ OPL ($	ext{mm/an}$) | Ratio $V_{sim}/V_{in}$ OPL | $V_{in}$ DA ($	ext{mm/an}$) | $V_{sim}$ DA ($	ext{mm/an}$) | $V_{obs}$ Observé ($	ext{mm/an}$) |
| :--- | :--- | :---: | ---:| ---:| ---:| :---: | ---:| ---:| ---:|
| **Ain Loudah** | Bouregreg | jour | 1 827 j (100 %) | $14.73$ | $14.74$ | **100.05 %** | $63.39$ | $63.54$ | $13.04$ |
| **Lalla Chafia** | Bouregreg | jour | 1 826 j (99.95 %) | $34.33$ | $34.42$ | **100.27 %** | $158.28$ | $158.60$ | $33.00$ |
| **S.M. Cherif** | Bouregreg | jour | 1 827 j (100 %) | $16.04$ | $16.05$ | **100.03 %** | $81.29$ | $81.29$ | $14.01$ |
| **Sidi Jabeur** | Bouregreg | jour | 1 827 j (100 %) | $23.87$ | $23.89$ | **100.07 %** | $89.64$ | $89.64$ | $41.78$ |
| **Adamna** | Ksob | mois | 20 mois (33.3 %) | $23.84$ | $23.94$ | **100.40 %** | $28.26$ | $28.47$ | $12.78$ |
| **Ain Timedrine**| Sebou | mois | 60 mois (100 %) | $14.94$ | $14.98$ | **100.33 %** | $23.00$ | $23.05$ | $65.94$ |
| **Ait Khabbach** | Sebou | mois | 44 mois (73.3 %) | $11.85$ | $11.91$ | **100.54 %** | $15.03$ | $15.09$ | $6.83$ |
| **Azzaba** | Sebou | mois | 60 mois (100 %) | $14.55$ | $14.59$ | **100.33 %** | $22.20$ | $22.26$ | $64.96$ |
| **Dar El Hamra** | Sebou | mois | 60 mois (100 %) | $19.98$ | $20.02$ | **100.24 %** | $67.93$ | $68.13$ | $91.37$ |
| **El Mers** | Sebou | mois | 20 mois (33.3 %) | **$23.64$** | **$23.65$** | **100.06 %** | $20.65$ | $20.68$ | $53.59$ |
| **Pont Ait Aissa**| Sebou | mois | 60 mois (100 %) | $15.04$ | $15.11$ | **100.47 %** | $22.72$ | $22.81$ | $58.19$ |
| **Pont de Mdez** | Sebou | mois | 44 mois (73.3 %) | $15.30$ | $15.36$ | **100.41 %** | $15.53$ | $15.59$ | $36.51$ |

### 5.3 Explication physique et méthodologique du cas El Mers ($V_{sim} = 23.7 > V_{in} = 15.2$)
Le tableau ci-dessus résout définitivement l'anomalie apparente d'El Mers :
1. **Période observée :** À la station d'El Mers, les observations n'étaient disponibles que sur **20 mois** (janvier 2016 à août 2017). Ces 20 mois correspondaient à une période particulièrement pluvieuse dans le Moyen Atlas (fortes crues de l'oued Masser).
2. **Ce que calculait `v_opl_mman` ($23.7\text{ mm/an}$) :** La moyenne temporelle du débit simulé OPL sur ces **20 mois humides**, extrapolée sur une base annuelle.
3. **Ce que calculait `vin_mman` ($15.2\text{ mm/an}$) dans F5 :** La somme du ruissellement DA sur l'ensemble des **60 mois (2016–2020)** divisée par **5.0 ans**, intégrant ainsi 40 mois de sécheresse sévère (2018–2020) non observés en station.
4. **Conclusion rigoureuse :** Lorsque l'on compare $V_{in}$ et $V_{sim}$ sur les **stricts mêmes 20 mois observés**, $V_{in\_OPL} = 23.64\text{ mm/an}$ et $V_{sim\_OPL} = 23.65\text{ mm/an}$. Le ratio de transmission est de **100.06 %** : il n'y a **aucune création magique d'eau ni dépassement physique**. Le paradoxe était un pur artefact statistique causé par la comparaison de fenêtres temporelles hétérogènes dans le script `complete_t8_analysis_and_plots.py`.

---

## 6. Synthèse des Rectifications Factuelles et Statuts `[CORRIGÉ le 2026-11-02]`

| Point audité | Affirmation antérieure (Réfutée / Corrigée) | Vérité matérielle et numérique démontrée | Référence preuve | Statut |
| :--- | :--- | :--- | :--- | :---: |
| **Fichiers merged** | Cartes fusionnées absentes de l'archive d'Augusto ; placeholders constants utilisés (5 m et 0 m). | `lis_rivwth_merged_005.bin` (86.4 ko) et `lis_fldhgt_merged_005.bin` (864 ko) sont présents dans l'archive, liés dans LDT et variables (4 080 valeurs uniques de largeur ; profil 10 niveaux distribué). | `data/Hymap_params_from_Augusto/lis_param.tar.gz` ; `checks/06` Section 3 | **[CORRIGÉ le 2026-11-02]** |
| **Durée du spin-up** | 2 cycles de 5 ans chacun (2016–2020). | **2 cycles de 1 an chacun (année 2016 uniquement)** (2016-01-01 au 2017-01-01). | `lis_hymap2_opl_spinup_c1_corrigee.config` ; 13 sous-dossiers `ROUTING/` sur disque | **[CORRIGÉ le 2026-11-02]** |
| **Stocks aux restarts** | Stock total = 64 521 hm³ ; écart = 4.7 hm³. | Stock total = **574.807 hm³** (C2) vs **574.414 hm³** (C1) ; écart = **+0.393 hm³ (+0.0684 %)**. Le chiffre 64 521 hm³ était une hallucination. | `LIS_RST_HYMAP2_router_201701010000.d01.nc` ; `check_spinup_criterion_corrigee.py` | **[CORRIGÉ le 2026-11-02]** |
| **Plancher `cntime`** | Stats de `tbasflw` brut : 1 à 30 jours (médiane 5 j). | `tbsflw` dans `lis_input_corrigee` : médiane = **0.0774 jour ($pprox 1.86\text{ h}$)**, min = $0.0024\text{ j}$, max = $30.46\text{ j}$. Le plancher superficiel ($2.45\text{ j}$ en médiane) s'active sur **99.90 % (15 921 / 15 937)** des mailles. | `scripts/check_cntime_floor.py` ; `checks/06` Section 2 | **[CORRIGÉ le 2026-11-02]** |
| **Bilan F5 et El Mers** | $V_{sim}$ OPL (23.7 mm/an) dépasse $V_{in}$ (15.2 mm/an) ; F5 trace $V_{in}$ OPL. | F5 traçait $V_{in}$ **DA_nocdf** sur 5 ans complets ($15.2\text{ mm/an}$), face à $V_{sim}$ calculé sur les 20 mois humides ($23.7\text{ mm/an}$). Sur les mêmes 20 mois, $V_{in\_OPL} = 23.64\text{ mm/an}$ et $V_{sim\_OPL} = 23.65\text{ mm/an}$ (conservation 100.06 %). | `complete_t8_analysis_and_plots.py` (l. 347, 349, 723) ; `checks/06` Section 5 | **[CORRIGÉ le 2026-11-02]** |\n
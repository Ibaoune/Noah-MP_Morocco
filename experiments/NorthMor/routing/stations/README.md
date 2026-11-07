# Répertoire des Stations et Tables d'Appariement HyMAP

Ce répertoire centralise les tables d'appariement géométrique et hydrologique entre les stations d'observation in-situ (Agences de Bassin Hydraulique - ABH) et le maillage de routage HyMAP (180 colonnes × 120 lignes à 0.05°).

---

## 1. Table de Référence : `hymap_stations_pairing.csv`

### Origine et Historique
- **Création initiale** : Générée le 25 octobre 2026 lors de la Tâche 5bis (`scripts/_history_tasks/analysis_tache5bis.py`) à partir des métadonnées d'observation (`data/streamflow_clean/stations.csv`) et des paramètres physiographiques du fichier LDT HyMAP corrigé (`ldt_hymap/lis_input_corrigee.d01.nc`).
- **Ancien emplacement** : `experiments/NorthMor/routing/output/OPL_2016_2020/t5bis_stations_pairing.csv` (conservé à l'identique pour assurer la rétrocompatibilité des anciens scripts archivés).
- **Centralisation (07/11/2026)** : Placée dans ce répertoire sous le nom unique `hymap_stations_pairing.csv` afin de constituer la source de vérité canonique pour tous les scripts actifs de post-traitement.

### Rôle dans le Pipeline HyMAP
Cette table est la référence d'extraction spatiale :
- Elle définit pour chacune des 12 stations les indices Python 0-basés `(row_hymap, col_hymap)`.
- Ces indices sont utilisés par les scripts pour extraire directement la variable 2D `Streamflow_tavg[row_hymap, col_hymap]` des fichiers NetCDF de simulation (`LIS_HIST_*.nc`).
- Elle est exploitée par les quatre scripts actifs de la chaîne :
  1. `scripts/complete_t7bis_analysis.py`
  2. `scripts/complete_t8_analysis_and_plots.py`
  3. `scripts/compare_3experiments_hydro.py`
  4. `scripts/sebou_bouregreg_diagnostic.py`

### Description des Colonnes
| Colonne | Type | Description |
| :--- | :--- | :--- |
| `station_id` | Chaîne | Identifiant unique normalisé de la station (ex. `b_l_chafia`, `pont_de_mdez`). |
| `nom` | Chaîne | Nom usuel de la station hydrométrique. |
| `bassin` | Chaîne | Bassin versant d'appartenance (`Sebou`, `Bouregreg`, `Ksob`). |
| `niveau` | Chaîne | Catégorie méthodologique d'appariement : `A (Valide)` ou `B (Non validable)`. |
| `validable` | Chaîne | `oui` si adossé à une superficie officielle vérifiée, `non` sinon. |
| `lon_obs`, `lat_obs` | Flottant | Coordonnées géographiques de la station in-situ (WGS84). |
| `row_hymap`, `col_hymap` | Entier | **Indices Python 0-basés** dans la grille HyMAP `(120, 180)`. Ligne = latitude (0 à 119), Colonne = longitude (0 à 179). |
| `lon_hymap`, `lat_hymap` | Flottant | Coordonnées du centre de la maille HyMAP correspondante dans `lis_input_corrigee.d01.nc`. |
| `dist_km` | Flottant | Distance entre la station in-situ et le centre de la maille HyMAP appariée (km). |
| `aire_off_km2` | Flottant | Superficie officielle du bassin versant d'après l'archive ABH (km²). `NaN` pour Bouregreg. |
| `aire_hymap_km2` | Flottant | Superficie drainée calculée par HyMAP (`HYMAP_drain_area`) au niveau de la maille (km²). |
| `ecart_pct` | Flottant | Écart relatif surfacique : $(A_{\\text{HyMAP}} - A_{\\text{off}}) / A_{\\text{off}} \\times 100$ (%). |
| `ref_ecart_pct` | Flottant | Valeur de référence arrondie de l'écart surfacique. |
| `type_pas` | Chaîne | Résolution temporelle native des observations (`journalier` ou `mensuel`). |

---

## 2. Typologie des Appariements

### Niveau A — Sebou (7 stations, pas mensuel)
- **Méthode** : Recherche dans une fenêtre locale de 5 × 5 mailles (±2 mailles, environ ±20 km) autour des coordonnées in-situ, en sélectionnant la maille minimisant l'écart relatif avec la superficie officielle ABH.
- **Résultats** :
  - 5 stations avec un accord surfacique remarquable (< 3.5 %) : Azzaba (+0.4 %), Ain Timedrine (+1.4 %), Pont de Mdez (-0.2 %), Dar El Hamra (-2.0 %), El Mers (-3.2 %).
  - Ait Khabbach : écart de +8.3 % (distance 4.38 km).
  - Pont Ait Aissa : écart de +23.8 % (bassin de seulement 205 km², sensibilité élevée à la résolution 0.05° ~ 25 km² par maille).

### Niveau B — Bouregreg & Ksob (5 stations)
- **Méthode** : En l'absence de superficies officielles enregistrées dans l'archive ABH source (`aire_off_km2 = NaN`), l'appariement a été réalisé par sélection du bief principal le plus proche respectant les critères de cohérence géomorphologique (distance < 10 km, aire drainée > 500 km²).
- **Couverture** :
  - Bouregreg (4 stations journalières) : Sidi Jabeur (dist 0.78 km, 3 138.5 km²), Lalla Chafia (dist 9.72 km, 3 341.6 km²), Ain Loudah (dist 3.24 km, 697.6 km²), S.M. Cherif (dist 2.83 km, 649.5 km²).
  - Ksob (1 station mensuelle) : Adamna (dist 2.03 km, 1 617.0 km²). Note : Adamna est exclue des analyses ciblées Sebou–Bouregreg conformément aux consignes actuelles.

---

## 3. Contrôles et Vérifications Réalisés (07/11/2026)

1. **Cohérence avec le fichier LDT corrigé (`ldt_hymap/lis_input_corrigee.d01.nc`)** :
   - Les coordonnées 2D `lon[row, col]` et `lat[row, col]` concordent rigoureusement avec `lon_hymap` et `lat_hymap` (tolérance < 1e-5 degré).
   - Les superficies `aire_hymap_km2` correspondent au champ `HYMAP_drain_area[row, col]` (tolérance < 0.0002 km²).
2. **Intégrité de la table** :
   - Checksum MD5 identique à l'original historique : `604f032a444478d182a1e5c9081620f0`.
   - Conservation intégrale des 12 stations, coordonnées, indices et superficies.
3. **Validation des scripts dépendants** :
   - Syntaxe Python 3 validée par compilation (`py_compile`) sur les 4 scripts adaptés.
   - Les 4 scripts pointent désormais de façon unifiée vers `experiments/NorthMor/routing/stations/hymap_stations_pairing.csv`.

---

## 4. Limites Méthodologiques et Incertitudes Restantes

- **Absence de superficie officielle pour le Bouregreg** : Les quatre stations du Bouregreg ne disposent pas d'aire officielle dans les données brutes ABH. Bien que le calage sur le bief principal soit morphologiquement robuste, ces stations restent catégorisées en Niveau B.
- **Doublon d'observation Ain Loudah / S.M. Cherif** : Les séries temporelles de débit observé fournies par l'ABH pour Ain Loudah et S.M. Cherif sont strictement identiques (corrélation r = 1.0, valeurs identiques au centième de m³/s). HyMAP les modélise néanmoins sur deux mailles distinctes (`[70, 64]` et `[70, 67]`).
- **Échelle d'agrégation amont** : Trois notions d'aires sont à distinguer :
  1. `aire_off_km2` : Aire administrative officielle (ABH Sebou uniquement).
  2. `aire_hymap_km2` : Aire drainée calculée à la maille par HyMAP via `HYMAP_drain_area`.
  3. `Somme du masque amont délimité` : Somme géométrique des mailles contribuant à la station via l'arbre de direction de drainage (`sebou_bouregreg_diagnostic.py`), très proche de `aire_hymap_km2` (ex. Lalla Chafia : 3 333.3 km² pour 133 mailles vs 3 341.6 km² pour `HYMAP_drain_area`).

---

## 5. Archive Historique : `_history/stations.csv`

Le fichier `stations.csv` archivé dans le sous-dossier `_history/` (528 octets, daté du 25/10/2026) est un **fichier historique exploratoire**.
- Il contient les coordonnées d'exutoires majeurs (Moulouya, Sebou, Oum Er Rbia, Tensift, Souss, Bouregreg, Loukkos) et de la station d'Adamna.
- **Statut** : Archivé dans `_history/` pour la traçabilité des premiers tests HyMAP.
- **Règle d'usage** : Aucun script actif ne doit utiliser `_history/stations.csv` pour l'extraction hydrologique. Toutes les analyses doivent obligatoirement utiliser `hymap_stations_pairing.csv`.

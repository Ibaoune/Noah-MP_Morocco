# Justification Scientifique de la Sélection des Quatre Stations Représentatives (2018)

**Document de travail pour échange avec Augusto Getirana et maturation d'article scientifique**  
**Auteurs :** Équipe de modélisation hydrologique Noah-MP Maroc & Antigravity  
**Date :** Novembre 2026  
**Localisation :** `experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/`  
**Statut :** Sélection représentative provisoire (soumise à concertation scientifique)

---

## 1. Justification Globale de la Sélection des Quatre Stations

Pour synthétiser la réponse des quatre schémas de ruissellement Noah-MP 4.0.1 (SIMGM, SIMTOP, Schaake96, BATS) routés avec HyMAP-2 (`linres=0`), une sélection restreinte de quatre stations représentatives a été établie. Cette sélection n'a pas été conçue pour maximiser artificiellement les scores statistiques, mais pour illustrer un **gradient représentatif de comportements hydroclimatiques, d'échelles spatiales et de défis de modélisation** à l'échelle du Nord-Maroc :

1. **Lalla Chafia (Bouregreg principal, $3\,333\text{ km}^2$, journalier) :** Bassin atlantique pluvial d'échelle intermédiaire, non influencé par des barrages en amont.
2. **Sidi Jabeur (Oued Grou, $3\,131\text{ km}^2$, journalier) :** Bassin semi-aride à forte réactivité hydrologique et intermittence estivale marquée.
3. **Aïn Timedrine (Haut Sebou, $4\,438\text{ km}^2$, mensuel) :** Grand exutoire régional du Moyen Atlas calcaire, marqué par des débits karstiques pérennes et un fort déficit volumique des LSM globaux.
4. **Dar El Hamra (Oued Zloul, $655\text{ km}^2$, mensuel) :** Petit affluent montagneux de rive droite du Sebou, à régime pluvio-nival naturel et forte synchronicité temporelle.

---

## 2. Enseignements Hydrologiques Spécifiques par Station

### 2.1 Station A — Lalla Chafia : Amélioration de la dynamique de crue avec SIMTOP
- **Message clé :** SIMTOP surpasse nettement la référence SIMGM ($NSE = 0.592$ vs $0.169$, $KGE = 0.593$ vs $0.079$, corrélation $r = 0.777$ vs $0.456$). La paramétrisation de la transmissivité exponentielle et de la fraction de surface saturée permet de capturer efficacement la réactivité aux épisodes pluvieux de janvier, mars et avril 2018.
- **Limite physique partagée :** Malgré cette nette amélioration en crue, le débit de tarissement estival simulé reste légèrement excessif par rapport aux étiages observés (surestimation du drainage sous-surfacique $Q_{sb}$).

### 2.2 Station B — Sidi Jabeur : Capture des volumes de crue par BATS et échec sur l'intermittence estivale
- **Message clé :** Le schéma BATS obtient la meilleure restitution globale des crues éclair ($NSE = 0.422$, $KGE = 0.476$, biais volumique minimal $PBIAS = -10.1\%$). Il démontre que l'infiltration BATS génère un ruissellement superficiel ($Q_s$) réactif adapté aux sols peu perméables du bassin du Grou.
- **Défaut structural majeur :** Tous les schémas échouent à reproduire l'assec estival strict observé par l'ABH (47 jours consécutifs à $0.0\text{ m}^3/\text{s}$ du 28 juin au 13 août 2018). Même au cœur de l'été, les modèles maintiennent un débit de base fictif de $1.2$ à $2.7\text{ m}^3/\text{s}$ issu du drainage matriciel profond.

### 2.3 Station C — Aïn Timedrine : Réduction du déficit volumique régional Sebou par BATS
- **Message clé :** Alors que le schéma de référence SIMGM subit un effondrement volumique massif ($PBIAS = -79.8\%$, $NSE = -2.008$, débit simulé moyen de $2.50\text{ m}^3/\text{s}$ contre $12.41\text{ m}^3/\text{s}$ observé), le schéma BATS réduit spectaculairement ce déficit ($PBIAS = -36.8\%$, $NSE = +0.330$, $r = 0.909$).
- **Portée scientifique :** Cela prouve la transférabilité de certaines avancées paramétriques de Noah-MP à un grand bassin méditerranéen contrasté, tout en soulignant la persistance d'un biais d'échelle lié aux résurgences karstiques non modélisées.

### 2.4 Station D — Dar El Hamra : Synchronicité saisonnière et sous-estimation orographique
- **Message clé :** Tous les schémas présentent une corrélation temporelle remarquable avec les observations ($r = 0.773$ à $0.956$), confirmant la bonne capture du cycle pluviométrique par le forçage LIS/CHIRPS. BATS est le seul schéma à atteindre un $NSE$ mensuel positif ($+0.258$).
- **Limite persistance :** Le volume écoulé annuel reste sévèrement sous-estimé (déficit de $-54\%$ à $-85\%$), reflétant la sous-estimation systématique des précipitations orographiques en haute montagne et l'absence de réservoirs hydrogéologiques profonds.

---

## 3. Limites et Réserves Méthodologiques Documentées

1. **Hétérogénéité des résolutions temporelles :**  
   Les stations du Bouregreg disposent de mesures journalières complètes validées par l'ABHBC ($364$ et $365$ jours en 2018). Les stations du Haut Sebou ne disposent, dans les archives officielles validées de l'ABHS, que d'agrégats mensuels ($12$ mois). **Aucune comparaison arithmétique directe entre $NSE$ journalier et $NSE$ mensuel ne doit être effectuée.**
2. **Influence karstique dans le Sebou :**  
   Le Moyen Atlas est caractérisé par un vaste réseau de calcaires et dolomies liasiques (sources de l'Aïn Sebou, causse d'Ifrane-Immouzzer). Les modèles de surface continentale 1D comme Noah-MP ne simulent pas les circulations souterraines karstiques ni les transferts inter-bassins profonds.
3. **Pression anthropique amont :**  
   Bien que les quatre stations aient été sélectionnées en évitant les barrages majeurs en exploitation directe à leur amont immédiat, les prélèvements pour irrigation agricole (notamment pompages estivaux) contribuent à accentuer l'étiage observé par rapport aux simulations naturelles (« natural flow »).

---

## 4. Comparaison avec Pont de M'Dez et Aït Khabbach

Pourquoi ces deux stations n'ont pas été retenues dans la sélection restreinte des quatre cas d'étude principaux ?

### 4.1 Pont de M'Dez (Sebou, $3\,421\text{ km}^2$)
- **Raison d'exclusion :** Chantier actif de construction du grand barrage de M'Dez au cours de la période 2017–2018 (dérivation provisoire, pertuis de fond et ouvrages de terrassement perturbant les débits jaugés).
- **Redondance d'emboîtement :** Le bassin amont de Pont de M'Dez ($135$ mailles) est quasi-entièrement inclus dans celui d'Aïn Timedrine ($175$ mailles). Conserver Aïn Timedrine évite une redondance spatiale tout en intégrant l'ensemble du continuum d'écoulement à l'exutoire régional.

### 4.2 Aït Khabbach (Oued Guigou, $1\,340\text{ km}^2$)
- **Raison d'exclusion :** Bassin situé au cœur du causse karstique et de la plaine agricole du Guigou, soumis à d'intenses pompages saisonniers d'eaux souterraines.
- **Comportement statistique trompeur :** SIMGM y affiche un $PBIAS$ artificiellement faible ($-12.4\%$) en raison d'une compensation de bilans, tandis que BATS y explose avec un biais positif extrême ($PBIAS = +220.0\%$, $NSE = -6.276$). Cette station illustre une anomalie hydrogéologique locale plutôt qu'un comportement représentatif généralisable.

---

## 5. Rôle de l'Évaluation Multi-Stations Complémentaire

L'exclusion de Pont de M'Dez et d'Aït Khabbach de la sélection principale F7 ne signifie en aucun cas leur mise à l'écart :
- Elles demeurent **intégralement documentées** dans le catalogue d'inventaire (`station_inventory_2018.csv`), la figure de distribution des flux (`F3`), la synthèse globale (`F6`) et la table multi-stations exhaustive (`table_multistation_metrics_2018.csv`).
- Elles apportent un éclairage complémentaire sur les limites de modélisation en contexte karstique et anthropisé.

---

## 6. Articulation de F7 avec les Figures Validées F1–F6

La figure F7 s'insère de manière cohérente dans la trame scientifique globale :
- **F2 & F3 :** Établissent la causalité hydrodynamique entre forçage pluviométrique, partitionnement $Q_s / Q_{sb}$ et temps de transfert HyMAP.
- **F4 :** Démontre la domination estivale du drainage sous-surfacique ($>95\%$) et quantifie l'erreur de simulation de l'assec à Sidi Jabeur.
- **F5 & F5b :** Apportent la preuve absolue de la continuité numérique et temporelle des simulations, répondant formellement au doute de mélange de simulations.
- **F6 :** Fournit la vision synthétique horizontale des métriques sur les 10 stations du réseau d'observation.
- **F7 :** Offre l'illustration hydrographique concrète des quatre archétypes hydrologiques majeurs, permettant à Augusto Getirana et aux pairs évaluateurs d'appréhender d'un coup d'œil les réussites (SIMTOP au Bouregreg, BATS au Sebou) et les frontières physiques de la modélisation Noah-MP au Maroc.

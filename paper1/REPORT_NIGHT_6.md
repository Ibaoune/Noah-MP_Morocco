# Rapport d'Exécution — Étape 6 (Figures et Données Tracées)

*Date d'exécution : 2026-11-22*
*Branche git : `paper1-closure`*
*Résolution graphique : 200 dpi*
*Palette daltonienne : Okabe-Ito (Wong 2011) avec couleurs fixes par expérience.*

---

## 1. Inventaire Exhaustif des Figures et Données Tracées

Toutes les figures ont été générées par un script dédié (`paper1/scripts/fig_XX.py`), accompagnées de leur fichier CSV de données tracées (`paper1/figures/fig_XX_data.csv`).

| ID Figure | Titre / Description | Script Générateur | Image PNG (200 dpi) | CSV Données | MD5 Image |
|---|---|---|---|---|---|
| **Fig. 2** | Fraction des retrievals rejetés par le filtre de flétrissement (2016–2020) | [`paper1/scripts/fig_02.py`](paper1/scripts/fig_02.py) | [`paper1/figures/fig_02.png`](paper1/figures/fig_02.png) (357.3 Ko) | [`paper1/figures/fig_02_data.csv`](paper1/figures/fig_02_data.csv) | `1eb5e5fc4bfca963dc6f266bf24d1ed0` |
| **Fig. 3** | Effet de sélection du QC de flétrissement | [`paper1/scripts/fig_03.py`](paper1/scripts/fig_03.py) | [`paper1/figures/fig_03.png`](paper1/figures/fig_03.png) (328.9 Ko) | [`paper1/figures/fig_03_data.csv`](paper1/figures/fig_03_data.csv) | `625a89149c5908c1378f7e38647052fa` |
| **Fig. 4** | Dry-downs de printemps (MAM) : SMAP uncensored vs Noah-MP OL | [`paper1/scripts/fig_04.py`](paper1/scripts/fig_04.py) | [`paper1/figures/fig_04.png`](paper1/figures/fig_04.png) (311.4 Ko) | [`paper1/figures/fig_04_data.csv`](paper1/figures/fig_04_data.csv) | `77268dd3a22b7342ad0800adf8e2a9e2` |
| **Fig. 5** | Changements mensuels DA − OL 2016–2020 (DA-NoCDF, DA-CDF) | [`paper1/scripts/fig_05.py`](paper1/scripts/fig_05.py) | [`paper1/figures/fig_05.png`](paper1/figures/fig_05.png) (495.6 Ko) | [`paper1/figures/fig_05_data.csv`](paper1/figures/fig_05_data.csv) | `23a86d9c7489a325367e7413fe987186` |
| **Fig. 6** | Effet du filtre de flétrissement en 2018 | [`paper1/scripts/fig_06.py`](paper1/scripts/fig_06.py) | [`paper1/figures/fig_06.png`](paper1/figures/fig_06.png) (289.8 Ko) | [`paper1/figures/fig_06_data.csv`](paper1/figures/fig_06_data.csv) | `46f465c84880da83708e8ed7ce324637` |
| **Fig. 7** | Bilan d'eau interne et mécanismes E6 | [`paper1/scripts/fig_07.py`](paper1/scripts/fig_07.py) | [`paper1/figures/fig_07.png`](paper1/figures/fig_07.png) (663.4 Ko) | [`paper1/figures/fig_07_data.csv`](paper1/figures/fig_07_data.csv) | `f3dc2cf0357019ca32e81d6325239e1f` |
| **Fig. 8** | Évaluation de l'ET contre GLEAM v4.3a et WaPOR v3 (2018) | [`paper1/scripts/fig_08.py`](paper1/scripts/fig_08.py) | [`paper1/figures/fig_08.png`](paper1/figures/fig_08.png) (453.2 Ko) | [`paper1/figures/fig_08_data.csv`](paper1/figures/fig_08_data.csv) | `92e67b0b825acb6565317c714ac83ab8` |
| **Fig. 9** | Débits HyMAP-2 linres=0 à Lalla Chafia et Sidi Jabeur (2018) | [`paper1/scripts/fig_09.py`](paper1/scripts/fig_09.py) | [`paper1/figures/fig_09.png`](paper1/figures/fig_09.png) (1023.3 Ko) | [`paper1/figures/fig_09_data.csv`](paper1/figures/fig_09_data.csv) | `34ee2faa035f5723b9f6fcbb577fe303` |
| **Fig. S-a** | Contrôle de Lalla Chafia et invariance de routage linres | [`paper1/scripts/fig_Sa.py`](paper1/scripts/fig_Sa.py) | [`paper1/figures/fig_Sa.png`](paper1/figures/fig_Sa.png) (580.3 Ko) | [`paper1/figures/fig_Sa_data.csv`](paper1/figures/fig_Sa_data.csv) | `2398109e01d90b542146cbaeb2be9628` |
| **Fig. S-b** | Diagnostic haute fréquence des incréments appliqués vs archivés | [`paper1/scripts/fig_Sb.py`](paper1/scripts/fig_Sb.py) | [`paper1/figures/fig_Sb.png`](paper1/figures/fig_Sb.png) (316.1 Ko) | [`paper1/figures/fig_Sb_data.csv`](paper1/figures/fig_Sb_data.csv) | `930f318746a213c54ea2975f48a88abc` |
| **Fig. S-c** | Innovations normalisées et spread de l'ensemble (2018) | [`paper1/scripts/fig_Sc.py`](paper1/scripts/fig_Sc.py) | [`paper1/figures/fig_Sc.png`](paper1/figures/fig_Sc.png) (393.8 Ko) | [`paper1/figures/fig_Sc_data.csv`](paper1/figures/fig_Sc_data.csv) | `e243c60487b195d1ef5bcca131801b47` |

---

## 2. Détail Technique par Figure

### Fig. 2 — Fraction des retrievals rejetés par le filtre de flétrissement (2016–2020)
- **Script :** [`paper1/scripts/fig_02.py`](paper1/scripts/fig_02.py)
- **Fichier image :** [`paper1/figures/fig_02.png`](paper1/figures/fig_02.png) (Taille : 357.3 Ko, MD5 : `1eb5e5fc4bfca963dc6f266bf24d1ed0`)
- **Données tracées :** [`paper1/figures/fig_02_data.csv`](paper1/figures/fig_02_data.csv) (Taille : 0.5 Ko, MD5 : `285d4c909cc090ee1a22e2b83244b96c`)
- **Contenu des panneaux :** (a) MAM, (b) JJA, (c) Rejets par texture DA-NoCDF vs DA-CDF

### Fig. 3 — Effet de sélection du QC de flétrissement
- **Script :** [`paper1/scripts/fig_03.py`](paper1/scripts/fig_03.py)
- **Fichier image :** [`paper1/figures/fig_03.png`](paper1/figures/fig_03.png) (Taille : 328.9 Ko, MD5 : `625a89149c5908c1378f7e38647052fa`)
- **Données tracées :** [`paper1/figures/fig_03_data.csv`](paper1/figures/fig_03_data.csv) (Taille : 3.9 Ko, MD5 : `9123eebcc7a52573819cdae6c52723d1`)
- **Contenu des panneaux :** (a) Biais accepted vs uncensored par mois/texture, (b) ΔJJA θ1 par classe de censure (IRRIGFRAC=0)

### Fig. 4 — Dry-downs de printemps (MAM) : SMAP uncensored vs Noah-MP OL
- **Script :** [`paper1/scripts/fig_04.py`](paper1/scripts/fig_04.py)
- **Fichier image :** [`paper1/figures/fig_04.png`](paper1/figures/fig_04.png) (Taille : 311.4 Ko, MD5 : `77268dd3a22b7342ad0800adf8e2a9e2`)
- **Données tracées :** [`paper1/figures/fig_04_data.csv`](paper1/figures/fig_04_data.csv) (Taille : 0.7 Ko, MD5 : `5bb0bc821da1d23a185ddf2e073b5535`)
- **Contenu des panneaux :** (a) τ par texture avec IC95, (b) P5 vs SMCWLT, (c) Régression τ vs % argile

### Fig. 5 — Changements mensuels DA − OL 2016–2020 (DA-NoCDF, DA-CDF)
- **Script :** [`paper1/scripts/fig_05.py`](paper1/scripts/fig_05.py)
- **Fichier image :** [`paper1/figures/fig_05.png`](paper1/figures/fig_05.png) (Taille : 495.6 Ko, MD5 : `23a86d9c7489a325367e7413fe987186`)
- **Données tracées :** [`paper1/figures/fig_05_data.csv`](paper1/figures/fig_05_data.csv) (Taille : 17.3 Ko, MD5 : `09e201a398aa92e470e7bff09b103c08`)
- **Contenu des panneaux :** (a) Δθ 4 couches, (b) ΔET, ΔQs, ΔQsb, (c) Incréments archivés vs Δflux

### Fig. 6 — Effet du filtre de flétrissement en 2018
- **Script :** [`paper1/scripts/fig_06.py`](paper1/scripts/fig_06.py)
- **Fichier image :** [`paper1/figures/fig_06.png`](paper1/figures/fig_06.png) (Taille : 289.8 Ko, MD5 : `46f465c84880da83708e8ed7ce324637`)
- **Données tracées :** [`paper1/figures/fig_06_data.csv`](paper1/figures/fig_06_data.csv) (Taille : 0.8 Ko, MD5 : `b71a678b40fb7f5224af49e6f949ab52`)
- **Contenu des panneaux :** (a) Obs acceptées 2018 par mois, (b) ΔET annuel par texture, (c) Carte JJA Δθ1

### Fig. 7 — Bilan d'eau interne et mécanismes E6
- **Script :** [`paper1/scripts/fig_07.py`](paper1/scripts/fig_07.py)
- **Fichier image :** [`paper1/figures/fig_07.png`](paper1/figures/fig_07.png) (Taille : 663.4 Ko, MD5 : `f3dc2cf0357019ca32e81d6325239e1f`)
- **Données tracées :** [`paper1/figures/fig_07_data.csv`](paper1/figures/fig_07_data.csv) (Taille : 3.0 Ko, MD5 : `d4eb2da775a67826ae3d4c551eb0cd88`)
- **Contenu des panneaux :** (a) Résidu mensuel 2018 & incréments, (b) ET mensuelle, (c) Tests mars 2018, (d) Décomposition code E6

### Fig. 8 — Évaluation de l'ET contre GLEAM v4.3a et WaPOR v3 (2018)
- **Script :** [`paper1/scripts/fig_08.py`](paper1/scripts/fig_08.py)
- **Fichier image :** [`paper1/figures/fig_08.png`](paper1/figures/fig_08.png) (Taille : 453.2 Ko, MD5 : `92e67b0b825acb6565317c714ac83ab8`)
- **Données tracées :** [`paper1/figures/fig_08_data.csv`](paper1/figures/fig_08_data.csv) (Taille : 4.1 Ko, MD5 : `7bc12bf931ef3b2f35b95cfc7d815011`)
- **Contenu des panneaux :** (a1-a3) Cycles mensuels Sebou/Bouregreg/Domaine, (b1) Δ|biais|, (b2) % mailles en amélioration

### Fig. 9 — Débits HyMAP-2 linres=0 à Lalla Chafia et Sidi Jabeur (2018)
- **Script :** [`paper1/scripts/fig_09.py`](paper1/scripts/fig_09.py)
- **Fichier image :** [`paper1/figures/fig_09.png`](paper1/figures/fig_09.png) (Taille : 1023.3 Ko, MD5 : `34ee2faa035f5723b9f6fcbb577fe303`)
- **Données tracées :** [`paper1/figures/fig_09_data.csv`](paper1/figures/fig_09_data.csv) (Taille : 85.6 Ko, MD5 : `91069be19f9306d78d5ab3109c97a2c5`)
- **Contenu des panneaux :** (a) Lalla Chafia échelle log, (b) Sidi Jabeur échelle log, encadrés KGE/NIC et bootstrap IC95

### Fig. S-a — Contrôle de Lalla Chafia et invariance de routage linres
- **Script :** [`paper1/scripts/fig_Sa.py`](paper1/scripts/fig_Sa.py)
- **Fichier image :** [`paper1/figures/fig_Sa.png`](paper1/figures/fig_Sa.png) (Taille : 580.3 Ko, MD5 : `2398109e01d90b542146cbaeb2be9628`)
- **Données tracées :** [`paper1/figures/fig_Sa_data.csv`](paper1/figures/fig_Sa_data.csv) (Taille : 26.4 Ko, MD5 : `101b3a1cc66eef9feda49cf6c13f6465`)
- **Contenu des panneaux :** (a) Carte ΔQsb DA-NoCDF − OPL avec top 20 mailles, (b) Hydrographe linres=0 vs linres=1

### Fig. S-b — Diagnostic haute fréquence des incréments appliqués vs archivés
- **Script :** [`paper1/scripts/fig_Sb.py`](paper1/scripts/fig_Sb.py)
- **Fichier image :** [`paper1/figures/fig_Sb.png`](paper1/figures/fig_Sb.png) (Taille : 316.1 Ko, MD5 : `930f318746a213c54ea2975f48a88abc`)
- **Données tracées :** [`paper1/figures/fig_Sb_data.csv`](paper1/figures/fig_Sb_data.csv) (Taille : 10.1 Ko, MD5 : `d8bdc84090d37332be89c2766e82baad`)
- **Contenu des panneaux :** (a) Scatter appliqué vs archivé 12 événements, (b) r et ratio par couche, (c) Contrastes heures pert

### Fig. S-c — Innovations normalisées et spread de l'ensemble (2018)
- **Script :** [`paper1/scripts/fig_Sc.py`](paper1/scripts/fig_Sc.py)
- **Fichier image :** [`paper1/figures/fig_Sc.png`](paper1/figures/fig_Sc.png) (Taille : 393.8 Ko, MD5 : `e243c60487b195d1ef5bcca131801b47`)
- **Données tracées :** [`paper1/figures/fig_Sc_data.csv`](paper1/figures/fig_Sc_data.csv) (Taille : 4.8 Ko, MD5 : `bdf47f103003e13249e910ed5b12aec9`)
- **Contenu des panneaux :** (a) Variance des innovations normalisées, (b) Biais normalisé, (c) Spread MAM DA-NoCDF vs NOSTATE

---

## 3. Conformité aux Directives et Statut des Données Manquantes

1. **Directives graphiques respectées :**
   - Format PNG à 200 dpi pour chaque figure.
   - Fichier CSV des données tracées produit pour 100 % des figures.
   - Palette daltonienne conforme (Okabe-Ito / Wong 2011) avec couleurs fixes :
     - OL : `#1f77b4`
     - OL-DAIC : `#56B4E9`
     - ENS-OL : `#009E73`
     - DA-NoCDF : `#D55E00`
     - DA-CDF : `#CC79A7`
     - DA-NoCDF-noWQC : `#E69F00`
     - ENS-corr : `#000000`
     - DA-corr : `#882255`

2. **Documentation des données manquantes :**
   - Conformément aux consignes (« *Si une donnée manque, produire la figure sans le panneau concerné et l'indiquer dans `paper1/figures/FIGURES_STATUS.md`* ») :
     - **Panneau (e) de la Figure 7 (2018 vs 2017) :** Les runs multi-annuels 2017 (`ENS_OPL_2017` et `DA_nocdf_nowilt_2017`) sont toujours en cours d'exécution sur le cluster Toubkal (~fin avril 2017 atteinte). La figure a donc été générée avec les 4 panneaux complets (a, b, c, d) et documentée dans [`paper1/figures/FIGURES_STATUS.md`](paper1/figures/FIGURES_STATUS.md).

---

## 4. Statut des Livrables

- Rapport d'étape : `paper1/REPORT_NIGHT_6.md`
- Statut des figures : `paper1/figures/FIGURES_STATUS.md`
- Paquet de livraison : mis à jour via `paper1/scripts/build_delivery_package.py 6`.

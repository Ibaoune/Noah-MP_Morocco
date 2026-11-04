# NoahMP-LIS Morocco — Modélisation et Assimilation SMAP

Ce dépôt héberge le pipeline scientifique de modélisation des surfaces continentales et d'assimilation de données d'humidité du sol sur le Nord du Maroc (**NorthMor**), développé sous le framework **NASA Land Information System (LIS 7.4)** couplé au modèle de surface **Noah-MP 4.0.1** et aux observations satellitaires **NASA SMAP**.

* **Auteur** : M. El Aabaribaoune (@um6p)
* **Infrastructure HPC** : Cluster Toubkal, UM6P
* **Domaine d'étude** : Domaine Nord Maroc (`NorthMor`, grille régulière $180 \times 120$ à $0.05^\circ \approx 5\text{ km}$, 16 030 points terre)
* **Observations assimilées** : Humidité de surface SMAP L3 Enhanced 9 km (`SPL3SMP_E`) via Filtre de Kalman d'Ensemble (EnKF, 20 membres)
* **Forçages météorologiques** : Couplage bimoteur MERRA-2 (NASA GMAO) + GPM IMERG Final Run v07B

---

## 1. Organisation du Répertoire

```
NoahMP_Morocco/
│
├── arch/                     # Environnement HPC Toubkal (modules MPI/Intel/NetCDF)
│   ├── arch_toubkal.env      #   Script d'initialisation de l'environnement (à sourcer)
│   └── README.md
│
├── src/                      # Code source LISF et exécutables
│   ├── lisf/                 #   NASA LISF officiel compilé (exécutable : src/lisf/lis/LIS)
│   └── lisf_nowilt/          #   Copie d'audit LIS (test sans seuil flétrissement QC)
│
├── data/                     # Données d'entrée (structures lourdes exclues de Git)
│   ├── forcing/              #   Forçages météo (MERRA2, IMERG, GDAS)
│   ├── observations/         #   Observations satellitaires (SMAP_SPL3SMP_E, MODIS)
│   ├── lis_input/            #   Fichier de domaine de référence lis_input_NorthMor_5km.nc
│   ├── land_params/          #   Tables physiques Noah-MP (VEGPARM, SOILPARM, etc.)
│   ├── pert_package/         #   Tables d'attributs de perturbation d'ensemble GMAO
│   └── validation/           #   Produits d'évaluation indépendants
│
├── experiments/NorthMor/     # Matrice d'expériences de modélisation
│   ├── SPINUP/               #   [PRODUCTION] Spinup en 3 étapes (2005-2015, restarts 2016)
│   │   ├── SPINUP_OPL/       #     Étape 1 : Spinup déterministe 2005–2015 (11 ans)
│   │   ├── ENS_OPL_2015/     #     Étape 2 : Ensemble Open Loop 2015 (20 membres)
│   │   └── SPINUP_DA/        #     Étape 3 : Spinup DA avr–déc 2015 (stabilisation EnKF)
│   │
│   ├── matrix_2016_2020/     #   Matrice principale 5 ans (2016–2020)
│   │   ├── OPL_noirr_2016_2020/      # [PRODUCTION] Open Loop 60 mois (baseline unperturbed)
│   │   ├── DA_nocdf_noirr_2016_2020/ # [PRODUCTION] Assimilation SMAP brute sans CDF (60 mois)
│   │   ├── DA_cdf_noirr_2016_2020/   # [PRODUCTION] Assimilation SMAP avec CDF corrigée (60 mois)
│   │   ├── CDF/                      # [PRODUCTION] Dépendance LDT : calcul de la CDF NorthMor
│   │   ├── _ARCHIVE_WRONG_CDF_DOMAIN/# [ARCHIVE] Ancien run avec CDF sur mauvais domaine
│   │   ├── tests/                    # Expériences de test, audits et sensibilités
│   │   └── planned/                  # Expériences prévues ou suspendues
│   │
│   └── routing/              # Module de routage hydraulique des débits (HyMAP)
│
├── scripts/                  # Chaînes d'exécution et post-traitement
│   ├── download/             #   Scripts d'acquisition de données
│   └── postproc/             #   Chaînes d'analyse et validation
│
├── reports/                  # Rapports d'intégrité et diagnostics expérimentaux
└── docs/                     # Documentation technique de référence
    ├── RUNS.md               #   Registre exhaustif de toutes les expériences
    ├── DATA.md               #   Détail des données d'entrée et citations des sources
    └── CHANGELOG.md          #   Historique des décisions et notes techniques
```

---

## 2. État d'Avancement des Simulations

Toutes les simulations de production de la matrice principale 2016–2020 sont **100% achevées et validées** :

| Expérience | Période | Membres | Statut | Outputs générés |
| :--- | :---: | :---: | :---: | :---: |
| **`SPINUP_OPL`** | 2005–2015 | 1 | **Terminé** | 11 années (restarts annuels) |
| **`ENS_OPL_2015`** | 2015 | 20 | **Terminé** | 12 mois (restarts de perturbation) |
| **`SPINUP_DA`** | 2015-04 à 2015-12 | 20 | **Terminé** | 9 mois (restarts surface et perturbation au 2016-01-01) |
| **`OPL_noirr_2016_2020`** | 2016–2020 | 1 | **Terminé** | 60 mois complets (`output/2016-01` .. `2020-12`) |
| **`DA_nocdf_noirr_2016_2020`** | 2016–2020 | 20 | **Terminé** | 60 mois complets (120 restarts surf/pert) |
| **`DA_cdf_noirr_2016_2020`** | 2016–2020 | 20 | **Terminé** | 60 mois complets (CDF NorthMor vérifiée) |

*Pour le détail complet de chaque simulation, consulter [`docs/RUNS.md`](docs/RUNS.md).*

---

## 3. Guide d'Exécution : Lancer une Chaîne d'Assimilation

Les simulations multi-annuelles sont découpées mois par mois via un script daisy-chain (`chain_da.py` ou `chain_opl.py`) pour respecter les limites de temps de calcul (wall-time SLURM de 12 heures) et propager rigoureusement les fichiers restart.

### Étape 1 : Initialiser l'environnement cluster Toubkal
```bash
# À exécuter à la racine du dépôt avant toute soumission
source arch/arch_toubkal.env
```

### Étape 2 : Lancer la chaîne daisy-chain
Pour lancer ou reprendre une expérience d'assimilation depuis une date spécifique :
```bash
# Se placer dans le répertoire de l'expérience cible
cd experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020

# Lancer la chaîne à partir du premier mois avec soumission SLURM automatique
python3 scripts/chain_da.py --current-date 2016-01-01 --submit
```

Le script réalise automatiquement :
1. La vérification de la présence des fichiers restart du mois précédent.
2. Pour les runs avec CDF (`DA_cdf_noirr`) : l'exécution du **garde-fou obligatoire `check_cdf_domain.py`** qui bloque immédiatement le job si une incohérence de domaine est détectée.
3. La génération du fichier de configuration LIS (`generated/configs/lis_*.config`).
4. La génération et la soumission du job SLURM 32 cœurs (`sbatch generated/jobs/job_*.sh`).
5. À la fin du mois, la copie automatique des restarts et la soumission récursive du mois suivant jusqu'à la date de fin configurée dans `config/experiment.ini`.

---

## 4. Garde-Fou de Cohérence Spatiale CDF

Pour prévenir toute erreur de domaine similaire à celle archivée dans `_ARCHIVE_WRONG_CDF_DOMAIN`, le script de contrôle qualité spatial [`check_cdf_domain.py`](experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/scripts/check_cdf_domain.py) vérifie l'accord strict entre les fichiers CDF LDT et le fichier de domaine `lis_input` :
```bash
# Test manuel du garde-fou
python3 experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/scripts/check_cdf_domain.py \
  --config experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_cdf_noirr_2016-01.config \
  --run-dir $(pwd)
```
Critères vérifiés :
* Égalité stricte de la dimension $ngrid$ de la CDF ($16\,030$) avec le nombre de mailles terre (`LANDMASK == 1`) dans `lis_input_NorthMor_5km.nc`.
* Concordance pixel par pixel du masque continental (0 pixel d'écart).
* Écart maximal de latitude et de longitude nul ($\Delta < 10^{-6}$).

---

## 5. Documentation Technique Associée

* [`docs/RUNS.md`](docs/RUNS.md) : Registre complet de toutes les expériences (configurations, statuts, volumes, binaires).
* [`docs/DATA.md`](docs/DATA.md) : Inventaire exhaustif des jeux de données d'entrée, sources, versions et citations des fichiers de configuration.
* [`docs/CHANGELOG.md`](docs/CHANGELOG.md) : Historique des décisions techniques et section « Notes techniques » sur les spécificités LIS/Noah-MP.

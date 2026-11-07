# Résumé de l'inventaire HyMAP / LDT / LIS (27/10/2026)

## 1. Arborescence pertinente

```text
NoahMP_Morocco/
├── data/
│   ├── Hymap_params/                               # Paramètres régionaux/globaux non 0.05° (fichiers 2D de 3.45 Mo)
│   ├── Hymap_params_from_Augusto/                  # Paramètres 0.05° fournis par Augusto Getirana (NASA)
│   │   ├── lis_param.tar.gz
│   │   └── extracted/lis_param/
│   │       └── lis_*_005.bin (24 fichiers de 86.4 Ko, grille 180x120)
│   └── lis_input/                                  # Fichiers paramètres de surface Noah-MP (sans HyMAP)
│       ├── lis_input_NorthMor_5km.nc (181x121)
│       └── lis_input_NorthMor_5km_irr.nc (181x121)
├── experiments/NorthMor/
│   ├── matrix_2016_2020/                           # Expériences de surface Noah-MP (Routing model: "none")
│   │   ├── CDF/                                    # Fichiers ldt.config.cdf*
│   │   ├── OPL_noirr_2016_2020/                    # Open-Loop surface 2016-2020
│   │   └── DA_nocdf_noirr_2016_2020/               # Assimilation SMAP NoCDF surface 2016-2020
│   └── routing/                                    # Chaîne de routage hors ligne HyMAP2
│       ├── ldt_hymap/                              # Préparation LDT des paramètres HyMAP (180x120)
│       │   ├── ldt.config
│       │   ├── lis_input.d01.nc                    # Paramètres LDT bruts (tbasflw en secondes)
│       │   └── lis_input_corrigee.d01.nc           # Paramètres LDT corrigés (tbasflw / 86400)
│       ├── configs/                                # Fichiers lis.config pour le routage hors ligne
│       ├── runoff_remap_180x120/                   # Ruissellements Noah-MP rééchantillonnés de 181x121 vers 180x120
│       ├── output/                                 # Sorties netCDF du routeur HyMAP2
│       ├── plots/pour_hydro/                       # Figures d'évaluation hydrologique F1-F6
│       └── checks/                                 # Vérifications, checksums et traçabilité
```

## 2. Tableau des runs de routage (dossiers ROUTING)

| Répertoire de sortie | Période simulée | Fichiers NetCDF | Fichier lis_input utilisé | Statut |
| :--- | :---: | :---: | :---: | :---: |
| `output/OPL_201801/ROUTING/` | 2018-01 à 2018-02 (2 mois) | 33 | `lis_input.d01.nc` | OBSOLÈTE (test initial, tbasflw brut) |
| `output/OPL_spinup_cycle1/ROUTING/` | 2016-01 à 2017-01 (13 mois) | 379 | `lis_input.d01.nc` | OBSOLÈTE (tbasflw non corrigé) |
| `output/OPL_spinup_cycle2/ROUTING/` | 2016-01 à 2017-01 (13 mois) | 379 | `lis_input.d01.nc` | OBSOLÈTE (tbasflw non corrigé) |
| `output/OPL_2016_2020/ROUTING/` | 2016-01 à 2021-01 (61 mois) | 1 888 | `lis_input.d01.nc` | OBSOLÈTE (tbasflw non corrigé) |
| `output/OPL_spinup_c1_corrigee/ROUTING/` | 2016-01 à 2017-01 (13 mois) | 379 | `lis_input_corrigee.d01.nc` | VALIDE (Spin-up cycle 1 OPL corrigé) |
| `output/OPL_spinup_c2_corrigee/ROUTING/` | 2016-01 à 2017-01 (13 mois) | 379 | `lis_input_corrigee.d01.nc` | VALIDE (Spin-up cycle 2 OPL corrigé) |
| `output/OPL_2016_2020_corrigee/ROUTING/` | 2016-01 à 2021-01 (61 mois) | 1 888 | `lis_input_corrigee.d01.nc` | VALIDE (Production 5 ans OPL corrigée) |
| `output/DA_nocdf_spinup_c1/ROUTING/` | 2016-01 à 2017-01 (13 mois) | 379 | `lis_input_corrigee.d01.nc` | VALIDE (Spin-up cycle 1 DA_nocdf) |
| `output/DA_nocdf_spinup_c2/ROUTING/` | 2016-01 à 2017-01 (13 mois) | 379 | `lis_input_corrigee.d01.nc` | VALIDE (Spin-up cycle 2 DA_nocdf) |
| `output/DA_nocdf_2016_2020/ROUTING/` | 2016-01 à 2021-01 (61 mois) | 1 888 | `lis_input_corrigee.d01.nc` | VALIDE (Production 5 ans DA_nocdf) |

## 3. Incohérences majeures relevées

1. **Grilles décalées d'une demi-maille** :
   - Surface Noah-MP (`lis_input_NorthMor_5km.nc`) : 181x121 mailles ($30.00^\circ\text{N}$ à $36.00^\circ\text{N}$, $-10.00^\circ\text{E}$ à $-1.00^\circ\text{E}$, bords/noeuds).
   - Routage HyMAP2 (`lis_input_corrigee.d01.nc`) : 180x120 mailles ($30.025^\circ\text{N}$ à $35.975^\circ\text{N}$, $-9.975^\circ\text{E}$ à $-1.025^\circ\text{E}$, centres de mailles).
   - Solution appliquée : remap conservatif des flux de ruissellement (dossier `runoff_remap_180x120/`).
2. **Unités du délai de vidange du débit de base (`tbasflw`)** :
   - Les cartes binaires d'Augusto Getirana contiennent des valeurs en secondes (moyenne ~61 703 s).
   - LIS interprète `tbsflw` en jours dans l'équation $Q_{bas} = S_{bas} / (tbsflw \times 86400)$, provoquant une constante de vidange de ~169 ans si non converti.
   - Dans `lis_input_corrigee.d01.nc`, `tbasflw` a été divisé par 86 400. Statut : À VÉRIFIER auprès d'Augusto Getirana.

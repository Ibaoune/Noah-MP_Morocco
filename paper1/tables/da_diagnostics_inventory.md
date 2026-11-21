# Inventaire des Diagnostics d'Assimilation SMAP Archivés en Production (LIS 7.5)

Ce document présente l'inventaire technique exhaustif des fichiers et variables diagnostiques d'assimilation EnKF réellement générés et archivés sur l'ensemble de la période d'audit 2016–2020 pour les simulations de production `DA_nocdf_noirr_2016_2020` et `DA_cdf_noirr_2016_2020`.

## 1. Inventaire des Fichiers Archivés (Volume 2016–2020, 60 mois)

| Type de Fichier | Sous-Dossier | Fréquence de Sortie | Format | Nb Fichiers DA_nocdf | Nb Fichiers DA_cdf |
|---|---|---|---|:---:|:---:|
| **Innovations (`*_innov`)** | `EnKF/YYYYMM/` | À chaque passage SMAP assimilé | NetCDF4 | 4619 | 4577 |
| **Incréments d'analyse (`*_incr`)** | `EnKF/YYYYMM/` | À chaque passage SMAP assimilé | NetCDF4 | 4619 | 4577 |
| **Spread d'ensemble (`*_spread`)** | `EnKF/YYYYMM/` | Quotidien (00:00 UTC) | NetCDF4 | 1827 | 1827 |
| **Observations prétraitées (`LISDAOBS_*`)** | `DAOBS/YYYYMM/` | À chaque passage SMAP lu | Binaire LIS (1gs4r) | 4619 | 4577 |
| **Restarts de perturbation (`LIS_DAPERT_*`)** | `DAPERT/YYYYMM/` | Mensuel (fin de mois) | Binaire Fortran | 60 | 60 |

## 2. Variables Diagnostiques NetCDF Archivées

### 2.1. Fichiers d'Innovations (`LIS_DA_EnKF_YYYYMMDDHHMM_innov.a01.d01.nc`)

- **Dimensions de grille** : `east_west = 181`, `north_south = 121`

| Nom de la Variable NetCDF | Dimensions | Shape | Type | Description & Définition LIS |
|---|---|---|---|---|
| `ninnov_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Normalized_innovations_for_DA_instance_01 |
| `innov_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Innovations_for_DA_instance_01 |
| `analysis_residual_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Analysis_residuals_for_DA_instance_01 |
| `forecast_sigma_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Forecast_variance_for_DA_instance_01 |

> **Signification des variables d'innovation** :
- `innov_01` : Innovation brute en espace observation, calculée comme $y - \overline{H(x^f)}$ (observation SMAP moins la prévision moyenne d'ensemble de l'humidité de surface, en $\text{m}^3/\text{m}^3$).
- `ninnov_01` : Innovation normalisée par la variance totale d'innovation, calculée comme $\frac{y - \overline{H(x^f)}}{\sqrt{H P^f H^T + R}}$.
- `analysis_residual_01` : Résidu d'analyse après mise à jour EnKF, calculé comme $y - \overline{H(x^a)}$ (écart post-assimilation).
- `forecast_sigma_01` : Variance d'ébauche (forecast variance en espace observation), soit $H P^f H^T$.
- **$H(\bar{x})$ moyen** : N'est pas stocké sous forme de variable dédiée, mais se déduit exactement à chaque point par soustraction $H(\bar{x}) = y - \text{innov\_01}$ (les observations $y$ étant disponibles dans `DAOBS`).

### 2.2. Fichiers d'Incréments d'Analyse (`LIS_DA_EnKF_YYYYMMDDHHMM_incr.a01.d01.nc`)

- **Dimensions de grille** : `east_west = 181`, `north_south = 121`

| Nom de la Variable NetCDF | Dimensions | Shape | Type | Description & Définition LIS |
|---|---|---|---|---|
| `anlys_incr_Soil Moisture Layer 1_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Analysis_incr_for_DA_instance_Soil Moisture Layer 1_01 |
| `anlys_incr_Soil Moisture Layer 2_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Analysis_incr_for_DA_instance_Soil Moisture Layer 2_01 |
| `anlys_incr_Soil Moisture Layer 3_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Analysis_incr_for_DA_instance_Soil Moisture Layer 3_01 |
| `anlys_incr_Soil Moisture Layer 4_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Analysis_incr_for_DA_instance_Soil Moisture Layer 4_01 |

> **Note critique sur les incréments** : Ces 4 champs correspondent aux incréments $\Delta \theta_l$ calculés directement par le filtre EnKF pour chaque couche de sol $l \in \{1, 2, 3, 4\}$. Ces valeurs sont archivées avant l'application des bornes physiques et de flétrissement dans `NoahMP401_setsoilm.F90`.

### 2.3. Fichiers de Spread d'Ensemble (`LIS_DA_EnKF_YYYYMMDD0000_spread.a01.d01.nc`)

- **Dimensions de grille** : `east_west = 181`, `north_south = 121`

| Nom de la Variable NetCDF | Dimensions | Shape | Type | Description & Définition LIS |
|---|---|---|---|---|
| `ensspread_Soil Moisture Layer 1_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Ensemble_spread_for_DA_instance_Soil Moisture Layer 1_01 |
| `ensspread_Soil Moisture Layer 2_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Ensemble_spread_for_DA_instance_Soil Moisture Layer 2_01 |
| `ensspread_Soil Moisture Layer 3_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Ensemble_spread_for_DA_instance_Soil Moisture Layer 3_01 |
| `ensspread_Soil Moisture Layer 4_01` | `('north_south', 'east_west')` | `(121, 181)` | `float32` | Ensemble_spread_for_DA_instance_Soil Moisture Layer 4_01 |

---

## 3. Analyse du Code Source LIS 7.5 : Nature Mathématique du « Spread »

### 3.1. Localisation dans le code source
- **Fichier** : [`src/lisf/lis/core/LIS_historyMod.F90`](file:///srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/core/LIS_historyMod.F90#L7886-L8003)
- **Routine** : `subroutine LIS_writevar_spread(ftn, n, m, varid, var, v)` (lignes 7886 à 8003)
- **Appelante** : `subroutine writeEnsembleSpread(n, k)` dans [`src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90:865-1000`](file:///srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90#L865-L1000)

### 3.2. Constat capital : Le spread archivé est une ÉTENDUE (MAX − MIN) et NON un écart-type

L'inspection détaillée des lignes 7949 à 7985 de `src/lisf/lis/core/LIS_historyMod.F90` démontre sans équivoque :

1. **Le calcul de l'écart-type est désactivé à la compilation (`#if 0`)** :
```fortran
! Lignes 7949-7971 dans src/lisf/lis/core/LIS_historyMod.F90
#if 0 
                      mean_v = 0 
                      var_v  = 0 
                      do t=1,npatch
                         mean_v = mean_v + gtmp1(count1)
                         var_v  = var_v + gtmp1(count1)*gtmp1(count1)
                         count1 = count1 + 1
                      enddo
                      if(npatch.gt.0) then 
                         mean_v = mean_v/npatch
                         std_v  = (var_v/npatch - mean_v*mean_v)
                         if(std_v.ge.0) then 
                            std_v = sqrt(std_v)
                         else
                            std_v = LIS_rc%udef
                         endif
                      else
                         std_v = LIS_rc%udef
                      endif
                      gtmp(c,r) = std_v
#endif
```

2. **Le code actif compilé et exécuté calcule l'étendue maximale de l'ensemble** :
```fortran
! Lignes 7973-7985 dans src/lisf/lis/core/LIS_historyMod.F90
                      min_v = 1000000
                      max_v = -1000000 
                      do t=1,npatch
                         if(gtmp1(count1).lt.min_v) min_v = gtmp1(count1)
                         if(gtmp1(count1).gt.max_v) max_v = gtmp1(count1)
                         count1 = count1 + 1
                      enddo                      
                      gtmp(c,r) = max_v - min_v
                      if(min_v.eq. 1000000.or. &
                           max_v.eq.-1000000 ) then 
                         gtmp(c,r) = LIS_rc%udef
                      endif
```

3. **Conséquence pour le papier** :
   - Bien que l'en-tête de `writeEnsembleSpread` mentionne `standard deviation` et que l'attribut NetCDF porte le standard_name `Ensemble_spread_...`, la valeur physique écrite dans `ensspread_Soil Moisture Layer X_01` est **rigoureusement l'étendue** $\max_{m=1..20}(\theta_m) - \min_{m=1..20}(\theta_m)$.
   - Pour un échantillon gaussien de 20 membres, le rapport moyen entre l'étendue et l'écart-type est $d_2 \approx 3.735$. Toute utilisation du spread archivé doit impérativement expliciter cette nature d'étendue ou la convertir rigoureusement.

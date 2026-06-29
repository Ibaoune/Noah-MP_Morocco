# Expérience : DA_SMAP_inflation_sensitivity_2016

Ce répertoire contient une configuration spécifique du modèle LIS/Noah-MP pour l'année 2016, générée dans le cadre de la matrice d'évaluation des processus d'assimilation et d'irrigation.

## 1. Objectif et Description
Il s'agit d'un **Test de Sensibilité** conçu pour explorer la robustesse de la configuration de base face à des variations de paramètres (erreur d'observation, inflation, biais, etc.).

## 2. Configuration Physique et d'Assimilation
- **Irrigation** : **Désactivée**
- **Observations Assimilées** : SMAP (SPL3SMP_E) uniquement
- **Correction de Biais (CDF Matching) pour SMAP** : **Désactivée** (none)

## 3. Dépendances et Restarts
Pour s'exécuter, cette expérience requiert :
1. **Spin-up initial** : Le restart de surface (`LIS_RST_NOAHMP401_201601010000.d01.nc`) provenant du répertoire `step1_spinup`.
2. **Restart des perturbations** : Le fichier binaire `LIS_DAPERT_201601010000.d01.bin` provenant de `step3_da_2015/restarts/pert/`.

## 4. Spécificités Techniques (`lis_da.config.template`)

> [!WARNING]
> **Test de Sensibilité** : Cette expérience nécessite potentiellement une modification manuelle externe avant son exécution complète (ex: modification d'un script Fortran de LIS, altération manuelle des HDFs originaux pour introduire un biais, ou altération des valeurs de variance dans les fichiers de perturbation).

## 5. Instructions de Lancement
Une fois les dépendances satisfaites, lancez simplement :
```bash
sbatch job.sh
```
Le script `chain_da.py` s'occupera d'itérer mois par mois sur l'année 2016.
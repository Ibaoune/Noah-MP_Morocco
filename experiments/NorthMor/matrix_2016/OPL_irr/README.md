# Expérience : OPL_irr (2016-2020)
**Auteur : M. El Aabaribaoune (@um6p)**

## Description
Cette expérience représente la ligne de base (baseline) Open-Loop pour la période de 2016 à 2020, avec le **module d'irrigation activé**.
Elle sert de contrôle pour évaluer l'impact de l'irrigation explicite (schéma Sprinkler) isolée, sans aucune assimilation de données satellite.

## Initialisation et Workflow
- **Initialisation** : La simulation démarre le 1er Janvier 2016 en utilisant le restart déterministe produit par le run de spin-up (`step1_spinup`).
- Fichier de restart initial utilisé : `LIS_RST_NOAHMP401_201601010000.d01.nc`
- **Exécution** : Le script `scripts/chain_opl.py` gère le daisy-chaining des exécutions mois par mois de 2016 jusqu'à la fin de 2020.

## Configuration de l'Irrigation et Troubleshooting
L'activation de l'irrigation via le schéma `Sprinkler` a nécessité plusieurs ajustements stricts imposés par LIS 7.4. Voici les problèmes rencontrés et leurs résolutions :

1. **Paramètre de profondeur des racines (Max Root Depth File)** :
   - *Erreur* : `Max root depth file, none, not found.`
   - *Explication* : LIS exige un fichier textuel définissant les profondeurs maximales de racines par classe de couverture terrestre pour l'irrigation.
   - *Résolution* : Nous avons explicitement pointé vers le fichier existant dans notre environnement : `./data/land_params/noahmp401_parms/maxrootdepth32.txt`.

2. **Paramètres GVF (Green Vegetation Fraction)** :
   - *Erreur* : `Irrigation GVF parameter 1: not defined`
   - *Explication* : Les paramètres régissant la saison de croissance pour l'irrigation manquaient.
   - *Résolution* : Nous avons configuré les paramètres standard de la méthode de Ozdogan et al. (2010) :
     - `Irrigation GVF parameter 1: 0.40`
     - `Irrigation GVF parameter 2: 0.00`

3. **Carte des classes de cultures (Crop Classification Map)** :
   - *Erreur* : `nf90_inq_varid failed for CROPTYPE`
   - *Explication* : La contrainte majeure était que le module d'irrigation de LIS 7.4 **force la lecture d'une carte de cultures (`CROPTYPE`)** même lorsqu'une fraction d'irrigation uniforme est préférée ou que les classes de cultures ne sont pas explicitement définies dans le domaine initial.
   - *Résolution* : L'outil de modification NetCDF (`ncap2`) pouvant corrompre des dimensions existantes importantes (comme `elevbins` nécessaire pour corriger la topographie), nous avons évité une réécriture destructive.
     Nous avons créé une copie de sécurité du fichier LDT : `lis_input_NorthMor_5km_irr.nc`.
     Ensuite, nous y avons injecté proprement la variable et les attributs globaux attendus en utilisant la commande d'ajout sécurisée de variables avec `ncap2 -A` :
     ```bash
     # Injection d'un CROPTYPE uniforme fictif basé sur la structure existante
     ncap2 -A -s 'CROPTYPE=int(IRRIGFRAC*0+1)' data/lis_input/lis_input_NorthMor_5km.nc data/lis_input/lis_input_NorthMor_5km_irr.nc
     ncatted -A -a CROPCLASS_SCHEME,global,c,c,"IGBPNCEP" data/lis_input/lis_input_NorthMor_5km_irr.nc
     ncatted -A -a CROPCLASS_NUMBER,global,c,i,1 data/lis_input/lis_input_NorthMor_5km_irr.nc
     ```
     L'expérience `OPL_irr` est configurée pour utiliser exclusivement ce fichier modifié.

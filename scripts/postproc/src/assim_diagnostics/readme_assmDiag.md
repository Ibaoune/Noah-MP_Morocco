# Assimilation Diagnostics Module

Ce répertoire contient le module de diagnostic des résultats d'assimilation de données (Data Assimilation). Il permet de générer des figures de qualité "publication" pour évaluer l'impact de l'assimilation des observations (ex: SMAP).

## Que calcule ce module et comment l'interpréter ?

Le module est divisé en plusieurs scripts de diagnostics indépendants situés dans `diagnostics/` :

1. **`diag_coverage.py`** :
   - **Carte du nombre total d'observations assimilées** : Affiche combien d'observations ont été intégrées à chaque pixel.
     *Interprétation* : Permet de vérifier si le modèle reçoit suffisamment d'observations sur l'ensemble du domaine. Des zones vides peuvent indiquer des données manquantes (par exemple, des passages de satellite non disponibles ou rejetés par le contrôle qualité).
   - **Carte de la fréquence d'assimilation** : Convertit le total en `obs/jour`.
     *Interprétation* : Utile pour comprendre la densité temporelle des données assimilées par pixel.
   - **Histogramme mensuel** : Montre la distribution temporelle des observations assimilées (total par mois).
     *Interprétation* : Aide à repérer les périodes où peu d'observations ont été assimilées, ce qui pourrait s'expliquer par des conditions météorologiques (ex: neige, végétation dense bloquant le signal).

2. **`diag_innovations.py`** :
   - **Innovation Moyenne (Obs - Forecast)** : Différence entre l'observation satellitaire et la prévision du modèle *avant* assimilation.
     *Interprétation* : Une innovation positive (rouge) indique que l'observation est plus humide que le modèle (le modèle est trop sec). Une innovation négative (bleue) indique que le modèle est plus humide que l'observation.
   - **Incrément Moyen (Analysis - Forecast)** : Quantité d'humidité ajoutée ou retirée au sol *pendant* l'étape d'analyse de l'EnKF.
     *Interprétation* : Montre l'effort de correction réalisé par l'assimilation. Un incrément positif signifie que l'assimilation a ajouté de l'eau dans le modèle. Un incrément négatif signifie qu'elle en a retiré.
   - **Histogramme des Incréments** : Visualise la distribution globale des corrections.
     *Interprétation* : Un biais (histogramme décalé vers la droite ou la gauche) indique que l'assimilation a systématiquement cherché à humecter ou assécher le modèle sur l'ensemble du domaine.

3. **`diag_seasonal_increments.py`** :
   - **Incréments saisonniers** : Génère deux cartes côte-à-côte (Saison humide vs Saison sèche) pour analyser si les corrections de l'assimilation dépendent du cycle hydrologique.
     *Interprétation* : Permet de voir si le modèle a des biais saisonniers spécifiques (ex: le modèle s'assèche trop vite en été, conduisant à des incréments positifs importants).

4. **`diag_spread.py`** :
   - **Ensemble Spread (Dispersion)** : Calcule l'écart-type de l'ensemble *a priori* (`forecast_sigma_01`) pour évaluer l'incertitude du modèle de surface avant d'assimiler les données.
     *Interprétation* : Les zones avec un fort 'spread' indiquent une forte incertitude de la prévision. C'est dans ces zones que l'observation aura le plus d'impact pour corriger l'état du modèle.
   - **Histogramme du Spread** : Distribution des valeurs d'incertitude sur toute la période.

---

## Quels fichiers NetCDF sont utilisés ?

Le module extrait la majorité de ses informations depuis le sous-répertoire `EnKF` du répertoire Data Assimilation (`da_dir`) :
- **Fichiers d'Innovation** (`*_innov.a01.d01.nc`) : 
   - `innov_01` : L'innovation.
   - `forecast_sigma_01` : Le spread (dispersion de l'ensemble).
- **Fichiers d'Incrément** (`*_incr.a01.d01.nc`) : 
   - `anlys_incr_Soil Moisture Layer 1_01` : L'incrément d'humidité du sol.
- **Fichiers d'Historique LIS** (`LIS_HIST_*.nc`) dans `SURFACEMODEL/` :
   - Utilisés uniquement au démarrage pour extraire la grille de référence (Latitude `lat` et Longitude `lon`).

---

## Comment lancer les diagnostics ?

Tout est paramétré par fichier de configuration central.

1. **Éditer le fichier `config_diagAssim.yaml`** :
   - Définissez le répertoire principal `project_root`.
   - Modifiez le répertoire de sortie `output_dir`.
   - Mettez à jour le répertoire de l'expérience DA (`da_dir`). Il doit pointer vers le sous-dossier `output` de votre run (ex: `.../DA_nocdf_noirr_2016/output`).
   - Définissez la période temporelle `start_date` et `end_date`.
   - (Optionnel) Modifiez les mois correspondant à vos saisons humide/sèche.
   - Activez/désactivez les diagnostics que vous souhaitez générer dans `active_diagnostics`.

2. **Soumettre le job SLURM** :
   Assurez-vous d'être dans le dossier racine de `postproc` et lancez :
   ```bash
   sbatch src/assim_diagnostics/job_assim_diag.sh
   ```
   *Ce script chargera l'environnement Conda `postproc_env` et lancera `main.py`.*

## Ajouter un nouveau diagnostic

Pour ajouter un nouveau diagnostic :
1. Créez un fichier `diag_nouveau.py` dans `diagnostics/`.
2. Créez une fonction `run_nouveau(config, base_dir_da, out_dir)` qui fait vos calculs et vos tracés. Utilisez `utils.generate_filename()` pour sauvegarder la figure.
3. Importez-la dans `main.py` et ajoutez-la à la liste des `active_diagnostics`.

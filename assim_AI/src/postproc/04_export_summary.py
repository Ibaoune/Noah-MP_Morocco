"""
04_export_summary.py
====================

This script compiles all results, metrics, and metadata from the previous 
steps into a comprehensive summary report (often exported as Markdown or text).
It facilitates the tracking of different experiment variations and their results.
"""

# Author: M. EL Aabaribaoune (@um6p)
import os
import argparse
import pandas as pd
import yaml

def export_summary():
    print("--- Starting Summary Export (04_export_summary.py) ---")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=None)
    parser.add_argument("--dataset", default="v0")
    parser.add_argument("--cv", default="temporal")
    parser.add_argument("--mini-test", action="store_true")
    args = parser.parse_args()
    
    config_path = "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    paths = config.get("paths", {})
    output_metrics = paths.get("output_metrics", "results/metrics/rf_metrics.csv")
    output_perm_imp = "results/metrics/rf_permutation_importance.csv"
    report_file = "logs/rf_v0_results_summary.md"
    
    if args.cv == "spatial":
        output_metrics = output_metrics.replace(".csv", "_v02_spatial_cv.csv")
        output_perm_imp = output_perm_imp.replace(".csv", "_v02_spatial_cv.csv")
        report_file = "logs/rf_v02_spatial_validation_summary.md"
    elif args.dataset == "static":
        output_metrics = output_metrics.replace(".csv", "_v01_static.csv")
        output_perm_imp = output_perm_imp.replace(".csv", "_v01_static.csv")
        report_file = "logs/rf_v01_static_results_summary.md"
        
    if args.mini_test:
        output_metrics = output_metrics.replace(".csv", "_test.csv")
        output_perm_imp = output_perm_imp.replace(".csv", "_test.csv")
        report_file = report_file.replace(".md", "_test.md")
        
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, "w") as f:
        title = "Random Forest Validation Summary"
        if args.cv == "spatial": title = "Random Forest V0.2 (Spatial Cross-Validation) Summary"
        elif args.dataset == "static": title = "Random Forest V0.1 (Static Predictors) Summary"
        
        f.write(f"# {title}\n\n")
        
        f.write("## A. Pourquoi la validation spatiale est nécessaire\n")
        f.write("Les variables statiques (land cover, texture, elevation) peuvent être très informatives. Cependant, avec un split temporel, le modèle Random Forest pourrait mémoriser la configuration spatiale spécifique de ces variables (qui ne bougent pas) au lieu d'apprendre une véritable relation physique généralisable. La validation spatiale par blocs (Spatial Block Validation) permet de tester le modèle sur des grilles non vues pendant l'entraînement et donc de s'assurer de la robustesse spatiale des relations diagnostiquées.\n\n")
        
        f.write("## B. Comparaison des scores (Temporal vs Spatial)\n")
        
        if args.cv == "spatial":
            # Compare with V0.1 temporal
            temporal_metrics_file = paths.get("output_metrics", "results/metrics/rf_metrics.csv").replace(".csv", "_v01_static.csv")
            temporal_imp_file = "results/metrics/rf_permutation_importance_v01_static.csv"
            
            if os.path.exists(temporal_metrics_file) and os.path.exists(output_metrics) and os.path.exists(temporal_imp_file) and os.path.exists(output_perm_imp):
                temp_df = pd.read_csv(temporal_metrics_file)
                spat_df = pd.read_csv(output_metrics)
                temp_imp = pd.read_csv(temporal_imp_file)
                spat_imp = pd.read_csv(output_perm_imp)
                
                f.write("| Target | R2_temporal | R2_spatial | Pearson_temporal | Pearson_spatial | score_drop |\n")
                f.write("|---|---|---|---|---|---|\n")
                
                targets = spat_df['Target'].unique()
                for t in targets:
                    if t in temp_df['Target'].values:
                        r2_temp = temp_df[temp_df['Target'] == t]['R2'].values[0]
                        r2_spat = spat_df[spat_df['Target'] == t]['R2'].values[0]
                        pearson_temp = temp_df[temp_df['Target'] == t]['Pearson'].values[0]
                        pearson_spat = spat_df[spat_df['Target'] == t]['Pearson'].values[0]
                        drop = r2_temp - r2_spat
                        
                        f.write(f"| {t} | {r2_temp:.3f} | {r2_spat:.3f} | {pearson_temp:.3f} | {pearson_spat:.3f} | {drop:.3f} |\n")
                
                f.write("\n## C. Robustesse des top predictors\n")
                for t in targets:
                    if t in temp_df['Target'].values:
                        f.write(f"### {t}\n")
                        top_temp = temp_imp[temp_imp['Target'] == t].nlargest(5, 'Importance')['Predictor'].tolist()
                        top_spat = spat_imp[spat_imp['Target'] == t].nlargest(5, 'Importance')['Predictor'].tolist()
                        robustes = [p for p in top_temp if p in top_spat]
                        
                        f.write(f"- **Top temporal** : {', '.join(top_temp)}\n")
                        f.write(f"- **Top spatial** : {', '.join(top_spat)}\n")
                        f.write(f"- **Predictors robustes** : {', '.join(robustes)}\n\n")
            else:
                f.write("Fichiers V0.1 ou V0.2 manquants pour la comparaison.\n")
                
        f.write("\n## D. Interprétation prudente\n")
        f.write("- Les incréments sont spatialement **associated with** les types de sols et d'occupation des terres identifiés.\n")
        f.write("- La persistance de l'importance de ces variables en validation spatiale est **spatially consistent with** l'hypothèse qu'elles contrôlent une part systématique des incréments d'assimilation.\n")
        f.write("- Cette analyse **suggests** une dépendance forte, et est **diagnostic of** possibles hétérogénéités dans la représentation OPL, sans toutefois prouver causalement une correction directe d'irrigation.\n")

    print(f"Summary successfully exported to {report_file}")

if __name__ == "__main__":
    export_summary()

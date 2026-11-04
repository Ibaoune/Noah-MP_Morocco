#!/usr/bin/env python3
"""
check_cdf_domain.py
-------------------
Garde-fou d'intégrité spatiale pour l'assimilation LIS/DA-CDF.
Vérifie qu'un ou plusieurs fichiers CDF correspondent strictement au domaine LIS :
1. ngrid (dimension 1D dans le CDF) == nombre de points terre (LANDMASK == 1) dans lis_input.
2. Égalité stricte des dimensions de grille, du LANDMASK, de la latitude et de la
   longitude entre le fichier domaine LDT (*_domain.nc) et lis_input.

Sort avec le code d'erreur 1 si une anomalie est détectée, 0 si tout est strictement conforme.
"""

import sys
import os
import argparse
import netCDF4 as nc
import numpy as np

def resolve_path(path, base_dir):
    if not path:
        return None
    path = os.path.expanduser(path.strip().strip('"').strip("'"))
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(base_dir, path))
    return path

def parse_lis_config(config_path, run_dir):
    """Extrait les fichiers CDF et le lis_input depuis un lis.config en résolvant par rapport à run_dir."""
    model_cdf = None
    obs_cdf = None
    domain_file = None
    
    with open(config_path, "r") as f:
        for line in f:
            clean = line.strip()
            if not clean or clean.startswith("#") or clean.startswith("!"):
                continue
            if "SMAP(NASA) model CDF file:" in clean:
                parts = clean.split(":", 1)
                model_cdf = resolve_path(parts[1], run_dir)
            elif "SMAP(NASA) observation CDF file:" in clean:
                parts = clean.split(":", 1)
                obs_cdf = resolve_path(parts[1], run_dir)
            elif "Data assimilation observation domain file:" in clean:
                parts = clean.split(":", 1)
                domain_file = resolve_path(parts[1], run_dir)
                
    return model_cdf, obs_cdf, domain_file

def verify_single_cdf(cdf_path, domain_path, lis_input_path):
    print(f"\n[CHECK] Validation du fichier CDF : {cdf_path}")
    print(f"        Fichier domaine LDT associé : {domain_path}")
    print(f"        Fichier lis_input référence : {lis_input_path}")
    
    if not os.path.exists(cdf_path):
        print(f"[ERROR] Le fichier CDF n'existe pas : {cdf_path}")
        return False
        
    if not os.path.exists(domain_path):
        print(f"[ERROR] Le fichier domaine LDT n'existe pas : {domain_path}")
        return False
        
    if not os.path.exists(lis_input_path):
        print(f"[ERROR] Le fichier lis_input LIS n'existe pas : {lis_input_path}")
        return False

    errors = 0

    # 1. Vérification ngrid vs points terre dans lis_input
    with nc.Dataset(lis_input_path) as ds_ref:
        mask_ref = ds_ref.variables["LANDMASK"][:].squeeze()
        lat_ref = ds_ref.variables["lat"][:].squeeze()
        lon_ref = ds_ref.variables["lon"][:].squeeze()
        n_land_ref = int((mask_ref == 1).sum())

    with nc.Dataset(cdf_path) as ds_cdf:
        if "ngrid" not in ds_cdf.dimensions:
            print(f"[ERROR] Dimension 'ngrid' introuvable dans {cdf_path}")
            return False
        ngrid = ds_cdf.dimensions["ngrid"].size

    print(f"  - ngrid CDF              : {ngrid}")
    print(f"  - Points terre lis_input : {n_land_ref}")
    if ngrid != n_land_ref:
        print(f"[ERROR] Incohérence ngrid : {ngrid} != {n_land_ref} (différence = {ngrid - n_land_ref})")
        errors += 1
    else:
        print("  -> ngrid == points terre : OK")

    # 2. Vérification stricte LANDMASK, lat, lon entre domain.nc et lis_input
    with nc.Dataset(domain_path) as ds_dom:
        if "LANDMASK" not in ds_dom.variables or "lat" not in ds_dom.variables or "lon" not in ds_dom.variables:
            print(f"[ERROR] Variables manquantes dans {domain_path} (attendues: LANDMASK, lat, lon)")
            return False
        mask_dom = ds_dom.variables["LANDMASK"][:].squeeze()
        lat_dom = ds_dom.variables["lat"][:].squeeze()
        lon_dom = ds_dom.variables["lon"][:].squeeze()

    # Vérification des dimensions de grille 2D
    if mask_dom.shape != mask_ref.shape:
        print(f"[ERROR] Incohérence des dimensions de grille : domaine={mask_dom.shape} != lis_input={mask_ref.shape}")
        return False

    diff_mask = int((mask_dom != mask_ref).sum())
    max_diff_lat = float(np.max(np.abs(lat_dom - lat_ref)))
    max_diff_lon = float(np.max(np.abs(lon_dom - lon_ref)))

    print(f"  - Pixels de LANDMASK différents : {diff_mask}")
    print(f"  - Écart maximal sur latitude    : {max_diff_lat:.6e}")
    print(f"  - Écart maximal sur longitude   : {max_diff_lon:.6e}")

    if diff_mask != 0:
        print(f"[ERROR] Échec de concordance stricte du LANDMASK ({diff_mask} pixels différents) !")
        errors += 1
    else:
        print("  -> LANDMASK strictement identique : OK")

    if max_diff_lat > 1e-6 or max_diff_lon > 1e-6:
        print(f"[ERROR] Échec de concordance des coordonnées lat/lon (max diff lat={max_diff_lat}, lon={max_diff_lon}) !")
        errors += 1
    else:
        print("  -> Coordonnées lat/lon strictement identiques : OK")

    return errors == 0

def main():
    parser = argparse.ArgumentParser(
        description="Garde-fou de cohérence spatiale entre CDF LDT et lis_input LIS."
    )
    parser.add_argument("--config", help="Chemin vers le fichier lis.config")
    parser.add_argument(
        "--run-dir",
        default=os.getcwd(),
        help="Répertoire de travail de LIS pour résoudre les chemins relatifs (défaut: CWD actuel)"
    )
    parser.add_argument("--cdf-file", action="append", help="Chemin vers un fichier CDF (peut être répété)")
    parser.add_argument("--domain-file", help="Chemin vers le fichier domaine LDT correspondant (déduit si omis)")
    parser.add_argument(
        "--lis-input",
        help="Chemin vers le fichier lis_input LIS (par défaut: extrait du config ou lis_input_NorthMor_5km.nc)"
    )

    args = parser.parse_args()
    run_dir = os.path.abspath(args.run_dir)

    files_to_check = []

    if args.config:
        config_path = os.path.abspath(args.config)
        print(f"[CHECK] Analyse de la configuration LIS : {config_path}")
        print(f"[CHECK] Répertoire de référence LIS (run-dir) : {run_dir}")
        model_cdf, obs_cdf, lis_inp_cfg = parse_lis_config(config_path, run_dir)
        
        lis_input = args.lis_input if args.lis_input else (
            lis_inp_cfg if lis_inp_cfg else os.path.join(run_dir, "data/lis_input/lis_input_NorthMor_5km.nc")
        )
        
        print("[CHECK] Chemins résolus depuis le fichier de configuration :")
        print(f"  - Model CDF : {model_cdf}")
        print(f"  - Obs CDF   : {obs_cdf}")
        print(f"  - LIS Input : {lis_input}")
        
        if model_cdf:
            dom = model_cdf.replace(".nc", "_domain.nc")
            files_to_check.append((model_cdf, dom, lis_input))
        if obs_cdf and obs_cdf != model_cdf:
            dom = obs_cdf.replace(".nc", "_domain.nc")
            files_to_check.append((obs_cdf, dom, lis_input))
    elif args.cdf_file:
        lis_input = args.lis_input if args.lis_input else os.path.join(run_dir, "data/lis_input/lis_input_NorthMor_5km.nc")
        for cdf in args.cdf_file:
            cdf_resolved = resolve_path(cdf, run_dir)
            if args.domain_file:
                dom_resolved = resolve_path(args.domain_file, run_dir)
            else:
                dom_resolved = cdf_resolved.replace(".nc", "_domain.nc")
            files_to_check.append((cdf_resolved, dom_resolved, lis_input))
    else:
        parser.print_help()
        sys.exit(1)

    all_passed = True
    for cdf_path, dom_path, lis_inp in files_to_check:
        passed = verify_single_cdf(cdf_path, dom_path, lis_inp)
        if not passed:
            all_passed = False

    if all_passed:
        print("\n=======================================================")
        print("[SUCCÈS] Tous les contrôles de domaine CDF sont VALIDES.")
        print("=======================================================")
        sys.exit(0)
    else:
        print("\n=======================================================")
        print("[ÉCHEC] Au moins une anomalie critique de domaine détectée.")
        print("=======================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()

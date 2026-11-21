#!/usr/bin/env python3
"""
generate_sources_md.py -- Traçabilité des sources (paper1, lot 1).

Génère `paper1/SOURCES.md` avec les hashes de commit exacts de chaque
dépôt et fichier source utilisé.
"""
import hashlib
import os
import subprocess

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
AUDIT_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit"


def get_git_info(repo_path):
    cmd = ["git", "rev-parse", "HEAD"]
    commit = subprocess.check_output(cmd, cwd=repo_path, text=True).strip()
    cmd_branch = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    branch = subprocess.check_output(cmd_branch, cwd=repo_path, text=True).strip()
    cmd_log = ["git", "log", "-n", "1", "--format=%cd (%s)", "--date=iso"]
    last_log = subprocess.check_output(cmd_log, cwd=repo_path, text=True).strip()
    return branch, commit, last_log


def get_md5(fpath):
    if not os.path.exists(fpath):
        return "FICHIER_INTROUVABLE"
    h = hashlib.md5()
    with open(fpath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    b_noah, c_noah, log_noah = get_git_info(BASE_DIR)
    b_audit, c_audit, log_audit = get_git_info(AUDIT_DIR)

    bin_prod = os.path.join(BASE_DIR, "src/lisf/lis/make/LIS")
    bin_nowilt = os.path.join(BASE_DIR, "src/lisf_nowilt/lis/LIS")
    lis_input = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

    md5_prod = get_md5(bin_prod)
    md5_nowilt = get_md5(bin_nowilt)
    md5_input = get_md5(lis_input)

    out_file = os.path.join(BASE_DIR, "paper1/SOURCES.md")
    with open(out_file, "w") as f:
        f.write("# Sources et Hashes de Commit — Papier 1 (Lot 1)\n\n")
        f.write("Ce fichier consigne l'ensemble des dépôts, commits, patchs et binaires utilisés pour garantir la reproductibilité intégrale des résultats du papier 1.\n\n")

        f.write("## 1. Dépôts Git\n\n")
        f.write("| Dépôt | Branche | Commit Hash (HEAD) | Dernier Message de Commit |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| **`Ibaoune/Noah-MP_Morocco`** | `{b_noah}` | `{c_noah}` | {log_noah} |\n")
        f.write(f"| **`Ibaoune/smap-xai-audit`** | `{b_audit}` | `{c_audit}` | {log_audit} |\n\n")

        f.write("## 2. Binaires et Exécutables LISF 7.5\n\n")
        f.write("| Binaire | Usage | Chemin Relatif | Somme de Contrôle MD5 |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| **LIS Production** | Runs standard (OPL, DA, Sensibilité) | `src/lisf/lis/make/LIS` | `{md5_prod}` |\n")
        f.write(f"| **LIS NoWilt** | Runs audit sans filtre flétrissement | `src/lisf_nowilt/lis/LIS` | `{md5_nowilt}` |\n\n")

        f.write("## 3. Fichiers de Données Clés et Paramètres\n\n")
        f.write("| Fichier | Rôle | MD5 |\n")
        f.write("|---|---|---|\n")
        f.write(f"| `data/lis_input/lis_input_NorthMor_5km.nc` | Domaine de référence 181×121 (16 030 mailles terre) | `{md5_input}` |\n")
        f.write(f"| `patches/lisf_nowilt_qc_wilting.patch` | Patch Fortran supprimant le filtre QC flétrissement | `{get_md5(os.path.join(BASE_DIR, 'patches/lisf_nowilt_qc_wilting.patch'))}` |\n")
        f.write(f"| `patches/lisf_hymap1_fixes.patch` | Patch correctifs routage HyMAP v1 | `{get_md5(os.path.join(BASE_DIR, 'patches/lisf_hymap1_fixes.patch'))}` |\n\n")

        f.write("## 4. Fichiers d'Entrée des Stations et Forçages\n\n")
        f.write("- **Inventaire 2018 des stations** : `experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.csv`\n")
        f.write("- **Appariement HyMAP des stations** : `experiments/NorthMor/routing/stations/hymap_stations_pairing.csv`\n")
        f.write("- **Données débit nettoyées** : `data/streamflow_clean/obs_daily.csv`, `obs_monthly.csv`, `stations.csv`\n")
        f.write("- **Forçages météorologiques** : MERRA-2 (NASA GMAO) + GPM IMERG Final Run v07B (`data/forcing/`)\n")
        f.write("- **Observations satellitaires** : SMAP L3 Enhanced 9 km `SPL3SMP_E` (`data/observations/SMAP_SPL3SMP_E/`)\n")

    print(f"[OK] Fichier SOURCES.md généré : {out_file}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
setup_runs.py -- Bloc A (paper1, lot 1).

Prépare et génère les configurations, scripts Slurm et READMEs pour les runs :
  1. ENS_OPL_2017 (P1)
  2. OL_DAIC_2017 (P1)
  3. DA_nocdf_nowilt_2017 (P2)
  4. DA_nocdf_nostate_2018MAM (P2)
  5. DA_nocdf_diag_2018ND (P1)

Soumet les jobs Slurm via sbatch, capture les Job IDs et génère :
  paper1/runs/RUNS_STATUS.md
  paper1/tables/runs_status.csv
  paper1/runs/<RUN_NAME>/README.md
  paper1/runs/<RUN_NAME>/<config>
  paper1/runs/<RUN_NAME>/<job.sh>
"""
import os
import subprocess
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
BIN_PROD = "./src/lisf/lis/make/LIS"
BIN_NOWILT = "./src/lisf_nowilt/lis/LIS"

RUNS = {
    "ENS_OPL_2017": {
        "prio": "P1",
        "lustre_dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017"),
        "paper1_dir": os.path.join(BASE_DIR, "paper1/runs/ENS_OPL_2017"),
        "base_template": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/config/lis_ENS_OPL_2018.config"),
        "binary": BIN_PROD,
        "walltime": "16:00:00",
        "job_name": "ENS_OPL_17",
        "start_date": ("2017", "01", "01"),
        "end_date": ("2018", "01", "01"),
        "rst_surf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "rst_pert": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201701010000.d01.bin"),
        "purpose": "Ensemble Open-Loop de 20 membres sur l'année sèche 2017 (P=177.03 mm) pour isoler l'effet d'ensemble sans assimilation.",
        "ic_desc": "Initialisé au 01-01-2017 à partir des restarts surface et perturbation d'ensemble de DA_nocdf_noirr_2016_2020.",
        "diff_prod": "Pas d'assimilation (instances DA = 0). Perturbations forçages et état actives (schéma GMAO 20 membres).",
    },
    "OL_DAIC_2017": {
        "prio": "P1",
        "lustre_dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017"),
        "paper1_dir": os.path.join(BASE_DIR, "paper1/runs/OL_DAIC_2017"),
        "base_template": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/config/lis_OL_DAIC_2018.config"),
        "binary": BIN_PROD,
        "walltime": "03:30:00",
        "job_name": "OL_DAIC_17",
        "start_date": ("2017", "01", "01"),
        "end_date": ("2018", "01", "01"),
        "rst_surf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "rst_pert": "none",
        "purpose": "Simulation déterministe (1 membre) sur l'année sèche 2017 avec la même condition initiale que l'ensemble (membre le plus proche de l'eau colonne moyenne).",
        "ic_desc": "Restart 1 membre généré par paper1/scripts/create_restart_daic_2017.py. Écart stock humidité colonne = -0.0290 mm (< 0.5 mm).",
        "diff_prod": "1 membre non perturbé, initialisé sur la trajectoire DA_nocdf plutôt que sur le spinup déterministe OPL.",
    },
    "DA_nocdf_nowilt_2017": {
        "prio": "P2",
        "lustre_dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017"),
        "paper1_dir": os.path.join(BASE_DIR, "paper1/runs/DA_nocdf_nowilt_2017"),
        "base_template": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/config/lis_DA_nocdf_nowilt_2018.config"),
        "binary": BIN_NOWILT,
        "walltime": "16:00:00",
        "job_name": "DA_nowilt_17",
        "start_date": ("2017", "01", "01"),
        "end_date": ("2018", "01", "01"),
        "rst_surf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "rst_pert": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201701010000.d01.bin"),
        "purpose": "Assimilation SMAP sans CDF et sans seuil QC de flétrissement sur l'année sèche 2017 (20 membres EnKF).",
        "ic_desc": "Initialisé au 01-01-2017 à partir des restarts de DA_nocdf_noirr_2016_2020.",
        "diff_prod": "Binaire lisf_nowilt désactivant le rejet d'observation (smobs - smcwlt < 0.02). Exécution continue 1 an.",
    },
    "DA_nocdf_nostate_2018MAM": {
        "prio": "P2",
        "lustre_dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM"),
        "paper1_dir": os.path.join(BASE_DIR, "paper1/runs/DA_nocdf_nostate_2018MAM"),
        "base_template": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_NOSTATE_201803/config/lis_ENS_NOSTATE_201803.config"),
        "binary": BIN_PROD,
        "walltime": "06:00:00",
        "job_name": "DA_nost_18MAM",
        "start_date": ("2018", "03", "01"),
        "end_date": ("2018", "06", "01"),
        "rst_surf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201803010000.d01.nc"),
        "rst_pert": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201803010000.d01.bin"),
        "purpose": "Diagnostic de spread en assimilation SMAP sans perturbation additive d'état sur mars-mai 2018 (3 mois).",
        "ic_desc": "Initialisé au 01-03-2018 à partir des restarts de DA_nocdf_noirr_2016_2020.",
        "diff_prod": "State perturbation algorithm: none (au lieu de GMAO scheme). Diagnostics DA complets activés (innovations, increments, spread).",
    },
    "DA_nocdf_diag_2018ND": {
        "prio": "P1",
        "lustre_dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND"),
        "paper1_dir": os.path.join(BASE_DIR, "paper1/runs/DA_nocdf_diag_2018ND"),
        "base_template": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/generated/configs/lis_DA_SMAP_nocdf_noirr_2018-11.config"),
        "binary": BIN_PROD,
        "walltime": "04:30:00",
        "job_name": "DA_diag_18ND",
        "start_date": ("2018", "11", "01"),
        "end_date": ("2019", "01", "01"),
        "rst_surf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201811010000.d01.nc"),
        "rst_pert": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/pert/LIS_DAPERT_201811010000.d01.bin"),
        "purpose": "Run de diagnostic de fermeture du bilan hydrique sur novembre-décembre 2018 avec archivage complet des incréments et diagnostics.",
        "ic_desc": "Initialisé au 01-11-2018 à partir des restarts de DA_nocdf_noirr_2016_2020.",
        "diff_prod": "Exécution continue sur 2 mois (novembre-décembre 2018) dans un seul run au lieu de chunks mensuels indépendants.",
    }
}


def df_to_markdown(df):
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)


def build_config(run_key, meta):
    with open(meta["base_template"], "r") as f:
        content = f.read()

    lines = content.splitlines()
    new_lines = []
    sy, sm, sd = meta["start_date"]
    ey, em, ed = meta["end_date"]

    for line in lines:
        if line.startswith("Starting year:"):
            new_lines.append(f"Starting year:                          {sy}")
        elif line.startswith("Starting month:"):
            new_lines.append(f"Starting month:                         {sm}")
        elif line.startswith("Starting day:"):
            new_lines.append(f"Starting day:                           {sd}")
        elif line.startswith("Ending year:"):
            new_lines.append(f"Ending year:                            {ey}")
        elif line.startswith("Ending month:"):
            new_lines.append(f"Ending month:                           {em}")
        elif line.startswith("Ending day:"):
            new_lines.append(f"Ending day:                             {ed}")
        elif line.startswith("Output directory:"):
            new_lines.append(f'Output directory:                       "{meta["lustre_dir"]}/output"')
        elif line.startswith("Diagnostic output file:"):
            new_lines.append(f'Diagnostic output file:                 "{meta["lustre_dir"]}/logs/lislog_{run_key}"')
        elif line.startswith("Noah-MP.4.0.1 restart file:"):
            new_lines.append(f'Noah-MP.4.0.1 restart file:                 {meta["rst_surf"]}')
        elif line.startswith("Perturbations restart filename:"):
            if meta["rst_pert"] == "none":
                new_lines.append('Perturbations restart filename:           "none"')
            else:
                new_lines.append(f'Perturbations restart filename:           "{meta["rst_pert"]}"')
        else:
            new_lines.append(line)

    return "\n".join(new_lines) + "\n"


def build_job_script(run_key, meta, cfg_path):
    job_str = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name={meta["job_name"]}
#SBATCH --output={meta["lustre_dir"]}/logs/slurm_{meta["job_name"]}_%j.log
#SBATCH --error={meta["lustre_dir"]}/logs/slurm_{meta["job_name"]}_%j.err
#SBATCH --time={meta["walltime"]}
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {BASE_DIR}

source arch/arch_toubkal.env

CONFIG="{cfg_path}"
BIN="{meta["binary"]}"

echo "=========================================================="
echo " LIS NorthMor - {run_key}"
echo " Start: {meta['start_date'][0]}-{meta['start_date'][1]}-{meta['start_date'][2]} | End: {meta['end_date'][0]}-{meta['end_date'][1]}-{meta['end_date'][2]}"
echo " Config: ${{CONFIG}}"
echo " Binary: ${{BIN}}"
echo "=========================================================="

time mpirun -n 32 "${{BIN}}" -f "${{CONFIG}}"

echo "=========================================================="
echo " Simulation {run_key} terminee avec succes "
echo "=========================================================="
"""
    return job_str


def build_readme(run_key, meta, cfg_name, job_name, job_id):
    md = f"""# Run {run_key}

- **Priorité** : {meta["prio"]}
- **Job ID Slurm** : `{job_id}`
- **Binaire** : `{meta["binary"]}`
- **Période** : {meta['start_date'][0]}-{meta['start_date'][1]}-{meta['start_date'][2]} au {meta['end_date'][0]}-{meta['end_date'][1]}-{meta['end_date'][2]}
- **Répertoire d'exécution HPC** : `{meta["lustre_dir"]}`
- **Fichier de configuration** : [`{cfg_name}`]({cfg_name})
- **Script de lancement** : [`{job_name}`]({job_name})

## 1. But de l'expérience
{meta["purpose"]}

## 2. Condition Initiale
{meta["ic_desc"]}
- **Surface restart** : `{meta["rst_surf"]}`
- **Perturbations restart** : `{meta["rst_pert"]}`

## 3. Différences avec la production
{meta["diff_prod"]}

## 4. Statut d'exécution
- **Soumis via Slurm** : Job `{job_id}`
- **Logs** : `{meta["lustre_dir"]}/logs/slurm_{meta["job_name"]}_{job_id}.log`
"""
    return md


def main():
    records = []

    for run_key, meta in RUNS.items():
        print(f"\n[INFO] Configuration de {run_key} ({meta['prio']})...")
        lustre_dir = meta["lustre_dir"]
        paper_dir = meta["paper1_dir"]
        os.makedirs(os.path.join(lustre_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(lustre_dir, "jobs"), exist_ok=True)
        os.makedirs(os.path.join(lustre_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(lustre_dir, "output"), exist_ok=True)
        os.makedirs(paper_dir, exist_ok=True)

        cfg_name = f"lis_{run_key}.config"
        job_name = f"run_{run_key}.sh"

        cfg_content = build_config(run_key, meta)
        cfg_lustre = os.path.join(lustre_dir, "config", cfg_name)
        with open(cfg_lustre, "w") as f:
            f.write(cfg_content)

        cfg_paper = os.path.join(paper_dir, cfg_name)
        with open(cfg_paper, "w") as f:
            f.write(cfg_content)

        job_content = build_job_script(run_key, meta, cfg_lustre)
        job_lustre = os.path.join(lustre_dir, "jobs", job_name)
        with open(job_lustre, "w") as f:
            f.write(job_content)
        os.chmod(job_lustre, 0o775)

        job_paper = os.path.join(paper_dir, job_name)
        with open(job_paper, "w") as f:
            f.write(job_content)
        os.chmod(job_paper, 0o775)

        # Soumission Slurm
        print(f"[INFO] Soumission sbatch {job_lustre}...")
        cmd = ["sbatch", job_lustre]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
        if res.returncode == 0:
            out = res.stdout.strip()
            # "Submitted batch job 123456"
            jid = out.split()[-1]
            status = "SUBMITTED"
            print(f"[OK] Job soumis avec succès : ID {jid}")
        else:
            jid = "SUBMIT_FAILED"
            status = f"FAILED: {res.stderr.strip()}"
            print(f"[ERR] Échec soumission : {res.stderr.strip()}")

        # README
        readme_content = build_readme(run_key, meta, cfg_name, job_name, jid)
        with open(os.path.join(paper_dir, "README.md"), "w") as f:
            f.write(readme_content)

        records.append({
            "run_name": run_key,
            "priority": meta["prio"],
            "job_id": jid,
            "status": status,
            "period": f"{meta['start_date'][0]}-{meta['start_date'][1]} to {meta['end_date'][0]}-{meta['end_date'][1]}",
            "binary": meta["binary"],
            "walltime": meta["walltime"],
            "purpose": meta["purpose"]
        })

    df = pd.DataFrame(records)
    csv_out = os.path.join(BASE_DIR, "paper1/tables/runs_status.csv")
    df.to_csv(csv_out, index=False)
    print(f"\n[OK] CSV de statut généré : {csv_out}")

    runs_status_path = os.path.join(BASE_DIR, "paper1/runs/RUNS_STATUS.md")
    with open(runs_status_path, "w") as f:
        f.write("# Statut des Runs de Robustesse et de Diagnostic — Papier 1\n\n")
        f.write(df_to_markdown(df))
        f.write("\n\n*Note : Ce tableau est généré directement à partir de `paper1/tables/runs_status.csv` par `paper1/scripts/setup_runs.py`.*\n")

    print(f"[OK] Fichier markdown généré : {runs_status_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os, sys, glob, tarfile, subprocess, datetime, shutil

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode().strip(), err.decode().strip()

def build_package(step_reached="jour1", issues_encountered="Aucun probleme bloquant."):
    bundle_dir = os.path.expanduser("~/paper1_bundle")
    os.makedirs(bundle_dir, exist_ok=True)
    tar_path = os.path.join(bundle_dir, "paper1_bundle_latest.tar.gz")
    contents_path = os.path.join(bundle_dir, "CONTENTS.txt")
    
    # 1. Update jobs status if script exists
    if os.path.exists("paper1/scripts/step0_jobs_status.py"):
        run_cmd("python3 paper1/scripts/step0_jobs_status.py")
        
    # Read jobs status
    jobs_summary = []
    if os.path.exists("paper1/tables/jobs_status_night.csv"):
        with open("paper1/tables/jobs_status_night.csv", "r") as f:
            import csv
            r = csv.DictReader(f)
            for row in r:
                jobs_summary.append(f"| {row['job_id']} | {row['job_name']} | {row['state']} | {row['current_simulated_date']} | {row['speed_last_hour_days_per_hour']} | {row['estimated_end']} | {row['time_limit']} | {row['risk_of_exceeding_limit']} |")
                
    # List of reports and tables produced
    reports = sorted(glob.glob("paper1/REPORT_*.md"))
    tables = sorted(glob.glob("paper1/tables/*"))
    figures = sorted(glob.glob("paper1/figures/*"))
    scripts = sorted(glob.glob("paper1/scripts/*"))
    
    # Preserve section 7 of REPORT_NIGHT.md if present
    section_7 = ""
    if os.path.exists("paper1/REPORT_NIGHT.md"):
        with open("paper1/REPORT_NIGHT.md", "r") as f:
            old_night = f.read()
            if "## 7. Corrections Factuelles Apportées aux Analyses de la Nuit" in old_night:
                section_7 = old_night[old_night.index("## 7. Corrections Factuelles Apportées aux Analyses de la Nuit"):]
    
    # Git push attempt log holder
    push_result = "Non tente (initial)"
    if os.path.exists("paper1/.last_git_push_status"):
        with open("paper1/.last_git_push_status", "r") as f:
            push_result = f.read().strip()
            
    # Generate REPORT_NIGHT.md
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_content = f"""# Rapport Global d'Exécution — Papier 1

**Dernière mise à jour :** {now_str}  
**Étape atteinte :** Étape {step_reached}

## 1. Statut des Jobs en Cours et Historiques

| Job ID | Nom | État | Date Simulée Actuelle | Vitesse (dernière heure, j/h) | Fin Estimée | Limite `--time` | Risque Dépassement |
|---|---|---|---|---|---|---|---|
""" + "\n".join(jobs_summary) + f"""

## 2. Rapports Produits
""" + "\n".join([f"- [{os.path.basename(p)}]({p})" for p in reports]) + f"""

## 3. Tables Produites
""" + "\n".join([f"- [{os.path.basename(p)}]({p})" for p in tables]) + f"""

## 4. Figures Disponibles
""" + "\n".join([f"- [{os.path.basename(p)}]({p})" for p in figures]) + f"""

## 5. Problèmes Rencontrés
{issues_encountered}

## 6. Résultat des Tentatives de Git Push
`{push_result}`

""" + (section_7 if section_7 else "")

    with open("paper1/REPORT_NIGHT.md", "w") as f:
        f.write(report_content)
    print("Generated paper1/REPORT_NIGHT.md")

    # 2. Gather allowed files
    allowed_extensions = ('.md', '.csv', '.py', '.sh', '.config', '.patch', '.txt', '.png', '.pdf')
    all_files = []
    for root, dirs, files in os.walk("paper1"):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_extensions:
                rel_path = os.path.join(root, file)
                all_files.append(rel_path)
                
    if os.path.exists("paper1/SOURCES.md") and "paper1/SOURCES.md" not in all_files:
        all_files.append("paper1/SOURCES.md")
        
    all_files = sorted(list(set(all_files)))
    
    # 3. Create tar.gz
    with tarfile.open(tar_path, "w:gz") as tar:
        for f in all_files:
            tar.add(f)
            
    tar_size_bytes = os.path.getsize(tar_path)
    tar_size_mb = tar_size_bytes / (1024.0 * 1024.0)
    print(f"Archive created: {tar_path} ({tar_size_mb:.2f} MB)")
    
    if tar_size_mb > 40.0:
        print("Warning: Archive exceeds 40 MB limit!")

    # 4. Write CONTENTS.txt
    with open(contents_path, "w") as f:
        f.write(f"Archive: paper1_bundle_latest.tar.gz\n")
        f.write(f"Generated at: {now_str}\n")
        f.write(f"Total size: {tar_size_bytes} bytes ({tar_size_mb:.2f} MB)\n")
        f.write(f"Total files: {len(all_files)}\n\n")
        f.write("Files included:\n")
        for fpath in all_files:
            size_b = os.path.getsize(fpath)
            f.write(f"{fpath:<65} ({size_b} bytes)\n")
    print(f"Generated {contents_path}")

    # 5. Git commit and push attempt
    run_cmd("git add paper1/ 2>/dev/null || true")
    run_cmd("git add paper1/*.md paper1/tables/* paper1/scripts/* paper1/figures/* 2>/dev/null || true")
    run_cmd(f'git commit -m "[paper1-closure] Step {step_reached} completed" || true')
    
    code, out, err = run_cmd("git push origin paper1-closure")
    if code == 0:
        push_msg = f"Succes: git push origin paper1-closure au {now_str}"
    else:
        push_msg = f"Echec ({code}): {err if err else out}"
        
    with open("paper1/.last_git_push_status", "w") as f:
        f.write(push_msg)
        
    # Re-update REPORT_NIGHT.md with the push result
    with open("paper1/REPORT_NIGHT.md", "r") as f:
        content = f.read()
    content = content.replace(f"`{push_result}`", f"`{push_msg}`")
    with open("paper1/REPORT_NIGHT.md", "w") as f:
        f.write(content)
        
    print(f"Git push result: {push_msg}")

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "jour1"
    build_package(step)

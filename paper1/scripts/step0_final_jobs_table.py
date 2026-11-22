#!/usr/bin/env python3
import subprocess
import csv
import os

jobs = [
    "8360359", "8360931",
    "8360361", "8360932",
    "8361185", "8361187",
    "8361186", "8361188"
]

cmd = f"sacct -j {','.join(jobs)} --format=JobID,JobName,State,ExitCode,Start,End,Elapsed -P"
res = subprocess.check_output(cmd, shell=True).decode('utf-8').strip().split('\n')

header = res[0].split('|')
rows = []
for line in res[1:]:
    parts = line.split('|')
    jid = parts[0]
    if '.' in jid:  # skip .batch, .extern
        continue
    rows.append(parts)

out_csv = "paper1/tables/jobs_status_final.csv"
with open(out_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["job_id", "job_name", "state", "exit_code", "start", "end", "elapsed", "final_simulated_date", "notes"])
    
    sim_dates = {
        "8360359": ("2017-11-04", "TIMEOUT a 16h00; relais assure par 8360931"),
        "8360931": ("2018-01-01", "COMPLETED; annee 2017 terminee avec succes (restart 20180101)"),
        "8360361": ("2017-10-28", "TIMEOUT a 16h00; relais assure par 8360932"),
        "8360932": ("2018-01-01", "COMPLETED; annee 2017 terminee avec succes (restart 20180101)"),
        "8361185": ("2019-01-01", "COMPLETED; annee 2018 terminee avec succes (restart 20190101)"),
        "8361187": ("2019-01-01", "Exited 15s (2018 deja completee par 8361185, aucune sortie ecrasee)"),
        "8361186": ("2019-01-01", "COMPLETED; annee 2018 terminee avec succes (restart 20190101)"),
        "8361188": ("2019-01-01", "Exited 16s (2018 deja completee par 8361186, aucune sortie ecrasee)")
    }
    
    for r in rows:
        jid = r[0]
        s_date, note = sim_dates.get(jid, ("Inconnue", ""))
        writer.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6], s_date, note])

print(f"Generated {out_csv}")

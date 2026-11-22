#!/usr/bin/env python3
import subprocess, datetime, glob, os, csv

jobs_info = [
    {"id": "8360343", "name": "RegCM_Morocco", "type": "regcm", "out": None, "period": "2016-01-01 to 2020-12-31"},
    {"id": "8360359", "name": "ENS_OPL_2017", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017/output", "period": "2017-01-01 to 2018-01-01"},
    {"id": "8360360", "name": "OL_DAIC_2017", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/output", "period": "2017-01-01 to 2018-01-01"},
    {"id": "8360361", "name": "DA_nocdf_nowilt_2017", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/output", "period": "2017-01-01 to 2018-01-01"},
    {"id": "8360362", "name": "DA_nocdf_nostate_2018MAM", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/output", "period": "2018-03-01 to 2018-06-01"},
    {"id": "8360363", "name": "DA_nocdf_diag_2018ND", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND/output", "period": "2018-11-01 to 2019-01-01"},
    {"id": "8360364", "name": "ENS_STATE_201803_noRyu", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803_noRyu/output", "period": "2018-03-01 to 2018-04-01"},
    {"id": "8360365", "name": "ENS_FORC_201803_noRyu", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_FORC_201803_noRyu/output", "period": "2018-03-01 to 2018-04-01"},
    {"id": "8360509", "name": "DA_nocdf_diag_15min_2018Nov", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov/output", "period": "2018-11-01 to 2018-11-06"},
    {"id": "8360645", "name": "hm2_5y_lr0_da_nocdf", "type": "routing", "out": "experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020", "period": "2016-01-01 to 2021-01-01"},
    {"id": "8360646", "name": "hm2_5y_lr0_da_cdf", "type": "routing", "out": "experiments/NorthMor/routing/output/DA_cdf_linres0_2016_2020", "period": "2016-01-01 to 2021-01-01"},
    {"id": "8360678", "name": "hm2_ol_daic_2018_linres0", "type": "routing", "out": "experiments/NorthMor/routing/output/OL_DAIC_linres0_2018", "period": "2018-01-01 to 2019-01-01"},
    {"id": "8360679", "name": "hm2_ens_opl_2018_linres0", "type": "routing", "out": "experiments/NorthMor/routing/output/ENS_OPL_linres0_2018", "period": "2018-01-01 to 2019-01-01"},
    {"id": "8360680", "name": "hm2_da_nocdf_nowilt_2018_linres0", "type": "routing", "out": "experiments/NorthMor/routing/output/DA_nocdf_nowilt_linres0_2018", "period": "2018-01-01 to 2019-01-01"}
]

# Query sacct
cmd = "sacct -j " + ",".join([j["id"] for j in jobs_info]) + " --format=JobID,JobName,State,Start,End,Elapsed,Timelimit -P"
res = subprocess.check_output(cmd, shell=True).decode()
sacct_map = {}
for line in res.strip().split("\n")[1:]:
    parts = line.split("|")
    jid = parts[0]
    if "." not in jid and jid not in sacct_map:
        sacct_map[jid] = {
            "name": parts[1],
            "state": parts[2],
            "start": parts[3],
            "end": parts[4],
            "elapsed": parts[5],
            "timelimit": parts[6]
        }

now = datetime.datetime.now()
one_hour_ago = now - datetime.timedelta(hours=1)

rows = []
for j in jobs_info:
    s = sacct_map.get(j["id"], {})
    state = s.get("state", "UNKNOWN")
    tlimit = s.get("timelimit", "UNKNOWN")
    start = s.get("start", "UNKNOWN")
    end = s.get("end", "UNKNOWN")
    elapsed = s.get("elapsed", "UNKNOWN")
    
    cur_date = "N/A"
    speed_1h = "N/A"
    est_end = end if state == "COMPLETED" else "N/A"
    risk = "non"
    
    if j["type"] == "lis" and j["out"] and os.path.exists(j["out"]):
        nc_files = sorted(glob.glob(os.path.join(j["out"], "SURFACEMODEL/**/*.nc"), recursive=True))
        hist_files = [f for f in nc_files if "LIS_HIST" in f]
        rst_files = [f for f in nc_files if "LIS_RST" in f]
        if hist_files:
            last_hist = os.path.basename(hist_files[-1])
            dstr = last_hist.replace("LIS_HIST_", "").split(".")[0]
            cur_date = f"{dstr[:4]}-{dstr[4:6]}-{dstr[6:8]} {dstr[8:10]}:{dstr[10:12]}"
        if state == "COMPLETED":
            cur_date = j["period"].split(" to ")[1]
            speed_1h = "0.00"
            risk = "non"
        elif state == "RUNNING":
            recent = [f for f in hist_files if datetime.datetime.fromtimestamp(os.path.getmtime(f)) >= one_hour_ago]
            if len(recent) >= 2:
                t0 = os.path.getmtime(recent[0])
                t1 = os.path.getmtime(recent[-1])
                dt = (t1 - t0) / 3600.0
                spd = (len(recent) - 1) / dt if dt > 0 else 0
                speed_1h = f"{spd:.2f}"
                target_dt = datetime.datetime.strptime(j["period"].split(" to ")[1].strip(), "%Y-%m-%d")
                curr_dt = datetime.datetime.strptime(dstr[:8], "%Y%m%d")
                rem_days = (target_dt - curr_dt).days
                if spd > 0:
                    rem_hours = rem_days / spd
                    est_finish = now + datetime.timedelta(hours=rem_hours)
                    est_end = est_finish.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # check timelimit
                    tl_parts = tlimit.split(":")
                    tl_hours = float(tl_parts[0]) + float(tl_parts[1])/60.0
                    el_parts = elapsed.split(":")
                    el_hours = float(el_parts[0]) + float(el_parts[1])/60.0
                    if (el_hours + rem_hours) > tl_hours:
                        risk = "oui"
            else:
                speed_1h = "calcul en cours"
    elif j["type"] == "routing":
        if state == "COMPLETED":
            cur_date = j["period"].split(" to ")[1]
            speed_1h = "0.00"
            risk = "non"
    elif j["type"] == "regcm":
        cur_date = "Production externe"
        speed_1h = "N/A"
        risk = "non"
        est_end = "Indeterminee"
        
    row = {
        "job_id": j["id"],
        "job_name": j["name"],
        "state": state,
        "current_simulated_date": cur_date,
        "speed_last_hour_days_per_hour": speed_1h,
        "estimated_end": est_end,
        "time_limit": tlimit,
        "risk_of_exceeding_limit": risk
    }
    rows.append(row)

# Save to CSV
os.makedirs("paper1/tables", exist_ok=True)
csv_path = "paper1/tables/jobs_status_night.csv"
fieldnames = ["job_id", "job_name", "state", "current_simulated_date", "speed_last_hour_days_per_hour", "estimated_end", "time_limit", "risk_of_exceeding_limit"]
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {csv_path}")

# Print markdown table
print("| job_id | job_name | state | current_simulated_date | speed_last_hour_days_per_hour | estimated_end | time_limit | risk_of_exceeding_limit |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['job_id']} | {r['job_name']} | {r['state']} | {r['current_simulated_date']} | {r['speed_last_hour_days_per_hour']} | {r['estimated_end']} | {r['time_limit']} | {r['risk_of_exceeding_limit']} |")

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
    {"id": "8360680", "name": "hm2_da_nocdf_nowilt_2018_linres0", "type": "routing", "out": "experiments/NorthMor/routing/output/DA_nocdf_nowilt_linres0_2018", "period": "2018-01-01 to 2019-01-01"},
    {"id": "8361185", "name": "ENS_corr_2018", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output", "period": "2018-01-01 to 2019-01-01"},
    {"id": "8361186", "name": "DA_corr_2018", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output", "period": "2018-01-01 to 2019-01-01"},
    {"id": "8361362", "name": "ENS_STATE_201803_diag", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/ENS_STATE_201803/output", "period": "2018-03-01 to 2018-04-01"},
    {"id": "8361363", "name": "ENS_STATE_201803_noRyu_diag", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/ENS_STATE_201803_noRyu/output", "period": "2018-03-01 to 2018-04-01"},
    {"id": "8361364", "name": "ENS_FORC_201803_diag", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/ENS_FORC_201803/output", "period": "2018-03-01 to 2018-04-01"},
    {"id": "8361365", "name": "ENS_FORC_201803_noRyu_diag", "type": "lis", "out": "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/ENS_FORC_201803_noRyu/output", "period": "2018-03-01 to 2018-04-01"}
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
    speed = 0.0
    est_end = "N/A"
    risk = "non"
    
    if j["type"] == "regcm":
        cur_date = "Production externe"
        speed = "N/A"
        est_end = "Indeterminee"
        risk = "non"
    elif j["type"] == "lis":
        if state == "COMPLETED":
            cur_date = j["period"].split(" to ")[1]
            speed = 0.0
            est_end = end
            risk = "non"
        elif state == "RUNNING":
            # Check latest file in output
            out_dir = j["out"]
            files = sorted(glob.glob(os.path.join(out_dir, "SURFACEMODEL", "*", "LIS_HIST_*.d01.nc")))
            if not files:
                files = sorted(glob.glob(os.path.join(out_dir, "**", "LIS_HIST_*.d01.nc"), recursive=True))
            if files:
                latest = files[-1]
                bname = os.path.basename(latest)
                # LIS_HIST_YYYYMMDDHHMM.d01.nc
                dt_str = bname.replace("LIS_HIST_", "").replace(".d01.nc", "")
                try:
                    f_dt = datetime.datetime.strptime(dt_str, "%Y%m%d%H%M")
                    cur_date = f_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    cur_date = dt_str
                
                # Count files created in last hour
                recent_files = [f for f in files if datetime.datetime.fromtimestamp(os.path.getmtime(f)) >= one_hour_ago]
                speed = len(recent_files) * 1.0 # 1 daily file = 1 day
                
                # Estimate end date
                target_dt = datetime.datetime.strptime(j["period"].split(" to ")[1], "%Y-%m-%d")
                curr_dt = datetime.datetime.strptime(cur_date.split()[0], "%Y-%m-%d")
                remaining_days = (target_dt - curr_dt).days
                if speed > 0:
                    hours_needed = remaining_days / speed
                    est_end_dt = now + datetime.timedelta(hours=hours_needed)
                    est_end = est_end_dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Risk of exceeding limit
                    # parse tlimit (format D-HH:MM:SS or HH:MM:SS)
                    parts_tl = tlimit.split("-")
                    if len(parts_tl) == 2:
                        days_tl = int(parts_tl[0])
                        hms = parts_tl[1].split(":")
                    else:
                        days_tl = 0
                        hms = parts_tl[0].split(":")
                    tot_tl_hours = days_tl * 24 + int(hms[0]) + int(hms[1])/60.0
                    
                    # parse elapsed
                    parts_el = elapsed.split("-")
                    if len(parts_el) == 2:
                        days_el = int(parts_el[0])
                        hms_el = parts_el[1].split(":")
                    else:
                        days_el = 0
                        hms_el = parts_el[0].split(":")
                    tot_el_hours = days_el * 24 + int(hms_el[0]) + int(hms_el[1])/60.0
                    
                    rem_tl_hours = tot_tl_hours - tot_el_hours
                    if hours_needed > rem_tl_hours:
                        risk = "oui"
                else:
                    est_end = "Inconnue (vitesse=0)"
            else:
                cur_date = "Initialisation"
                est_end = "Indeterminee"
        else:
            cur_date = "Non demarre / En attente"
            est_end = "N/A"
    elif j["type"] == "routing":
        if state == "COMPLETED":
            cur_date = j["period"].split(" to ")[1]
            speed = 0.0
            est_end = end
            risk = "non"
        elif state == "RUNNING":
            cur_date = "En cours"
            speed = "N/A"
            est_end = "Imminente"
            risk = "non"
        else:
            cur_date = "En attente"
            est_end = "N/A"

    rows.append({
        "job_id": j["id"],
        "job_name": j["name"],
        "state": state,
        "current_simulated_date": cur_date,
        "speed_last_hour_days_per_hour": f"{speed:.2f}" if isinstance(speed, float) else speed,
        "estimated_end": est_end,
        "time_limit": tlimit,
        "risk_of_exceeding_limit": risk
    })

os.makedirs("paper1/tables", exist_ok=True)
with open("paper1/tables/jobs_status_night.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "job_id", "job_name", "state", "current_simulated_date",
        "speed_last_hour_days_per_hour", "estimated_end", "time_limit", "risk_of_exceeding_limit"
    ])
    writer.writeheader()
    writer.writerows(rows)

print("Saved paper1/tables/jobs_status_night.csv")
print("| job_id | job_name | state | current_simulated_date | speed_last_hour_days_per_hour | estimated_end | time_limit | risk_of_exceeding_limit |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['job_id']} | {r['job_name']} | {r['state']} | {r['current_simulated_date']} | {r['speed_last_hour_days_per_hour']} | {r['estimated_end']} | {r['time_limit']} | {r['risk_of_exceeding_limit']} |")

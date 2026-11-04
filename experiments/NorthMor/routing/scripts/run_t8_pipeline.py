#!/usr/bin/env python3
import subprocess, time, os, sys
import netCDF4 as nc
import numpy as np

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def wait_for_slurm_job(job_id, job_name="Job"):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] En attente du job {job_name} (ID: {job_id})...")
    while True:
        stdout, _, _ = run_cmd(f"squeue -j {job_id} -h")
        if not stdout:
            break
        time.sleep(15)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Job {job_name} termine.")

def get_stocks(rst_file):
    if not os.path.exists(rst_file):
        return None
    with nc.Dataset(rst_file, 'r') as ds:
        bsf = np.where(ds.variables['BSFSTO'][:] > 0, ds.variables['BSFSTO'][:], 0.0)
        tot = bsf + np.where(ds.variables['RNFSTO'][:] > 0, ds.variables['RNFSTO'][:], 0.0) + \
                    np.where(ds.variables['RIVSTO'][:] > 0, ds.variables['RIVSTO'][:], 0.0) + \
                    np.where(ds.variables['FLDSTO'][:] > 0, ds.variables['FLDSTO'][:], 0.0)
        return {
            'bsf_hm3': float(np.sum(bsf)) / 1e6,
            'tot_hm3': float(np.sum(tot)) / 1e6
        }

def main():
    # Job 1 (Cycle 1) is already running (Job ID passed as arg or 8176298)
    job_c1 = sys.argv[1] if len(sys.argv) > 1 else "8176298"
    wait_for_slurm_job(job_c1, "Cycle 1 Spin-up")
    
    rst_c1 = "experiments/NorthMor/routing/output/DA_nocdf_spinup_c1/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
    if not os.path.exists(rst_c1):
        raise RuntimeError(f"Erreur : Restart Cycle 1 non genere : {rst_c1}")
    
    s_c1 = get_stocks(rst_c1)
    print(f"Cycle 1 BSFSTO = {s_c1['bsf_hm3']:.3f} hm3 | Total = {s_c1['tot_hm3']:.3f} hm3")
    
    # Soumission Cycle 2
    out, _, code = run_cmd("sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_nocdf_spinup_c2.sh")
    if code != 0 or "Submitted batch job" not in out:
        raise RuntimeError(f"Erreur soumission Cycle 2 : {out}")
    job_c2 = out.split()[-1]
    print(f"Cycle 2 soumis avec ID : {job_c2}")
    wait_for_slurm_job(job_c2, "Cycle 2 Spin-up")
    
    rst_c2 = "experiments/NorthMor/routing/output/DA_nocdf_spinup_c2/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
    if not os.path.exists(rst_c2):
        raise RuntimeError(f"Erreur : Restart Cycle 2 non genere : {rst_c2}")
    
    s_c2 = get_stocks(rst_c2)
    delta_bsf = abs(s_c2['bsf_hm3'] - s_c1['bsf_hm3']) / s_c1['bsf_hm3'] * 100.0
    print(f"Cycle 2 BSFSTO = {s_c2['bsf_hm3']:.3f} hm3 | Total = {s_c2['tot_hm3']:.3f} hm3")
    print(f"Ecart inter-cycles : {delta_bsf:.4f} %")
    if delta_bsf >= 1.0:
        raise RuntimeError(f"ARRET : Critere de spin-up decroche ({delta_bsf:.4f} % >= 1.0 %)")
    print("--> Critere de spin-up valide (< 1.0 %). Lancement de la production 5 ans...")
    
    # Soumission Production 5 ans
    out, _, code = run_cmd("sbatch experiments/NorthMor/routing/jobs/run_hymap2_da_nocdf_2016_2020.sh")
    if code != 0 or "Submitted batch job" not in out:
        raise RuntimeError(f"Erreur soumission 5 ans : {out}")
    job_5y = out.split()[-1]
    print(f"Production 5 ans soumise avec ID : {job_5y}")
    wait_for_slurm_job(job_5y, "Production 5 ans 2016-2020")
    
    print("Toutes les simulations sont terminees avec succes !")

if __name__ == "__main__":
    main()

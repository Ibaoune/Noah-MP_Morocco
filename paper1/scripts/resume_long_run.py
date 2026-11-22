#!/usr/bin/env python3
import sys, os, glob, re, subprocess

def prepare_resume(run_dir, config_template, bin_path):
    print(f"Checking run directory: {run_dir}")
    surf_dir = os.path.join(run_dir, "output", "SURFACEMODEL")
    pert_dir = os.path.join(run_dir, "output", "DAPERT")
    
    rst_files = sorted(glob.glob(os.path.join(surf_dir, "**/LIS_RST_NOAHMP401_*.d01.nc"), recursive=True))
    if not rst_files:
        print("Error: No restart files found in", surf_dir)
        sys.exit(1)
        
    latest_rst = rst_files[-1]
    fname = os.path.basename(latest_rst)
    print(f"Latest restart found: {latest_rst}")
    
    # Example filename: LIS_RST_NOAHMP401_201702282345.d01.nc or LIS_RST_NOAHMP401_201801010000.d01.nc
    m = re.search(r"LIS_RST_NOAHMP401_(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})\.d01\.nc", fname)
    if not m:
        print("Cannot parse restart filename:", fname)
        sys.exit(1)
        
    yr, mo, dy, hr, mn = m.groups()
    print(f"Restart timestamp: {yr}-{mo}-{dy} {hr}:{mn}:00")
    
    if yr == "2018" and mo == "01" and dy == "01" and hr == "00" and mn == "00":
        print("Run has already completed full period 2018-01-01 00:00:00! Exiting gracefully.")
        sys.exit(0)
        
    # Read template config
    with open(config_template, "r") as f:
        cfg = f.read()
        
    # Update start date
    cfg = re.sub(r"Starting year:\s+\d+", f"Starting year:                          {yr}", cfg)
    cfg = re.sub(r"Starting month:\s+\d+", f"Starting month:                         {mo}", cfg)
    cfg = re.sub(r"Starting day:\s+\d+", f"Starting day:                           {dy}", cfg)
    cfg = re.sub(r"Starting hour:\s+\d+", f"Starting hour:                          {hr}", cfg)
    cfg = re.sub(r"Starting minute:\s+\d+", f"Starting minute:                        {mn}", cfg)
    cfg = re.sub(r"Starting second:\s+\d+", f"Starting second:                        00", cfg)
    
    # Update restart file
    cfg = re.sub(r"Noah-MP\.4\.0\.1 restart file:\s+.*", f"Noah-MP.4.0.1 restart file:                 {os.path.abspath(latest_rst)}", cfg)
    
    # If DAPERT exists, check DAPERT restart
    if os.path.exists(pert_dir):
        pert_rsts = sorted(glob.glob(os.path.join(pert_dir, f"**/LIS_DAPERT_{yr}{mo}{dy}{hr}{mn}.d01.bin"), recursive=True))
        if pert_rsts:
            latest_pert = pert_rsts[-1]
            print(f"Matching DAPERT restart found: {latest_pert}")
            cfg = re.sub(r"Perturbations restart filename:\s+.*", f'Perturbations restart filename:           "{os.path.abspath(latest_pert)}"', cfg)
            
    resume_cfg_path = os.path.join(run_dir, "config", "lis_resume.config")
    with open(resume_cfg_path, "w") as f:
        f.write(cfg)
    print(f"Generated resume config: {resume_cfg_path}")
    
    # Run LIS
    cmd = f"time mpirun -n 32 {bin_path} -f {resume_cfg_path}"
    print(f"Executing: {cmd}")
    subprocess.check_call(cmd, shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: resume_long_run.py <run_dir> <config_template> <bin_path>")
        sys.exit(1)
    prepare_resume(sys.argv[1], sys.argv[2], sys.argv[3])

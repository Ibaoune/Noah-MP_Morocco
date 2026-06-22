import os
import glob
import h5py
import calendar
import sys
import argparse
from multiprocessing import Pool, cpu_count

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing"
MERRA2_DIR = os.path.join(BASE_DIR, "MERRA2")
IMERG_DIR = os.path.join(BASE_DIR, "IMERG/raw")

def check_file(filepath):
    try:
        with h5py.File(filepath, 'r') as f:
            list(f.keys())
        return (filepath, True, None)
    except Exception as e:
        # If corrupted, delete it immediately so it can be re-downloaded
        try:
            os.remove(filepath)
            action = "DELETED"
        except Exception as rm_e:
            action = f"FAILED TO DELETE: {rm_e}"
        return (filepath, False, f"{os.path.basename(filepath)}: {str(e)} [{action}]")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int, help='Year to check (e.g. 2000)')
    args = parser.parse_args()
    
    year = args.year
    months = range(1, 13)
    
    print(f"Gathering files for YEAR {year}...")
    
    merra2_files = []
    imerg_files = []
    
    for month in months:
        yyyymm = f"{year}{month:02d}"
        
        # MERRA-2 matching YYYYMM
        m_pattern = os.path.join(MERRA2_DIR, "*", f"*.{yyyymm}*.nc4")
        merra2_files.extend(glob.glob(m_pattern))
        
        # IMERG matching YYYYMM directory
        i_pattern1 = os.path.join(IMERG_DIR, yyyymm, "*.HDF5")
        i_pattern2 = os.path.join(IMERG_DIR, yyyymm, "*.h5")
        imerg_files.extend(glob.glob(i_pattern1) + glob.glob(i_pattern2))
        
    all_files = merra2_files + imerg_files
    print(f"Total files found for {year}: {len(all_files)}")
    
    with Pool(cpu_count()) as pool:
        results_list = pool.map(check_file, all_files)
        
    results_dict = {res[0]: res for res in results_list}
    
    all_complete = True
    
    for month in months:
        yyyymm = f"{year}{month:02d}"
        
        m_files = [f for f in merra2_files if f".{yyyymm}" in f]
        i_files = [f for f in imerg_files if f"/{yyyymm}/" in f]
        
        m_valid = sum(1 for f in m_files if results_dict[f][1])
        i_valid = sum(1 for f in i_files if results_dict[f][1])
        
        corrupted = [results_dict[f][2] for f in (m_files + i_files) if not results_dict[f][1]]
        
        days = calendar.monthrange(year, month)[1]
        m_expected = days * 3
        i_expected = days * 48
        
        if year == 2000 and month < 6:
            i_expected = 0
            
        if corrupted:
            print(f"[{yyyymm}] ❌ CORRUPTED ({len(corrupted)} files deleted)")
            for c in corrupted:
                print(f"  -> {c}")
            all_complete = False
        elif m_valid < m_expected or (i_expected > 0 and i_valid == 0):
            print(f"[{yyyymm}] ⏳ PARTIAL | MERRA-2: {m_valid}/{m_expected} | IMERG: {i_valid}/{i_expected} (Requires > 0)")
            all_complete = False
        elif m_valid == 0 and i_valid == 0 and m_expected > 0:
            print(f"[{yyyymm}] ⭕ EMPTY | MERRA-2: {m_valid}/{m_expected} | IMERG: {i_valid}/{i_expected}")
            all_complete = False
        else:
            print(f"[{yyyymm}] ✅ COMPLETE | MERRA-2: {m_valid}/{m_expected} | IMERG: {i_valid}/{i_expected}")

    if all_complete:
        print(f"\nSUCCESS: Year {year} is fully downloaded and verified!")
        sys.exit(0)
    else:
        print(f"\nFAILURE: Year {year} is missing files or had corrupted files.")
        sys.exit(1)

if __name__ == '__main__':
    main()

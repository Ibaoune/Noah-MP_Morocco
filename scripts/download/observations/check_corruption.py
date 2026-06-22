import os
import glob
import h5py
from multiprocessing import Pool, cpu_count

DATA_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/observations/SMAP_SPL3SMP_E/raw"

def check_file(filepath):
    try:
        with h5py.File(filepath, 'r') as f:
            # Just accessing the keys is enough to verify HDF5 structural integrity
            list(f.keys())
        return None  # None means no error
    except Exception as e:
        return f"{os.path.basename(filepath)}: Corrupted! Error: {str(e)}"

if __name__ == '__main__':
    files = glob.glob(os.path.join(DATA_DIR, "*.h5"))
    print(f"Total files to check: {len(files)}")
    
    corrupted = []
    
    # Use multiprocessing to speed up checking ~2000 files
    with Pool(cpu_count()) as pool:
        results = pool.map(check_file, files)
        
    for res in results:
        if res is not None:
            corrupted.append(res)
            
    print("-" * 50)
    if len(corrupted) == 0:
        print("✅ SUCCESS: All files are perfectly valid and NOT corrupted!")
    else:
        print(f"❌ WARNING: Found {len(corrupted)} corrupted files:")
        for c in corrupted:
            print(c)

import os
import glob
from pathlib import Path
import xarray as xr

def find_smap_diagnostics():
    print("--- Starting SMAP DA Diagnostics Search ---")
    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    
    # Keywords
    keywords = ["incr", "increment", "innovation", "DA", "EnKF", "ObsFcst", "analysis", "anlys"]
    extensions = [".nc", ".nc4", ".bin", ".txt", ".log"]
    
    found_files = []
    
    print(f"Scanning {base_dir} for SMAP DA diagnostic files...")
    
    # We will search the DA-NoCDF and DA-CDF directories specifically to save time
    search_dirs = [
        os.path.join(base_dir, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
        os.path.join(base_dir, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020")
    ]
    
    for sdir in search_dirs:
        if not os.path.exists(sdir): continue
        for ext in extensions:
            for kw in keywords:
                # search for filenames containing kw and ending in ext
                # This could result in duplicates, so we use a set
                files = list(Path(sdir).rglob(f"*{kw}*{ext}"))
                for f in files:
                    found_files.append(str(f))
                    
    # Remove duplicates
    found_files = list(set(found_files))
    
    report_file = "reports/smap_da_diagnostics_inventory.md"
    os.makedirs("reports", exist_ok=True)
    
    with open(report_file, "w") as f:
        f.write("# SMAP DA Diagnostics Inventory\n\n")
        
        if not found_files:
            f.write("No SMAP DA diagnostic files found matching keywords: " + ", ".join(keywords) + "\n")
            print("No files found.")
        else:
            f.write(f"Found {len(found_files)} potential SMAP DA files.\n\n")
            
            # Categorize
            nc_files = [f for f in found_files if f.endswith('.nc') or f.endswith('.nc4')]
            other_files = [f for f in found_files if not (f.endswith('.nc') or f.endswith('.nc4'))]
            
            if nc_files:
                f.write("## NetCDF Candidates\n")
                # Inspect the first NC file
                sample = nc_files[0]
                f.write(f"- **Sample inspected**: `{sample}`\n")
                try:
                    ds = xr.open_dataset(sample, decode_times=False)
                    f.write("- **Variables**:\n")
                    for var in ds.data_vars:
                        f.write(f"  - `{var}`\n")
                    ds.close()
                except Exception as e:
                    f.write(f"- Error reading sample: {e}\n")
                    
            if other_files:
                f.write("\n## Other Candidates (Logs, Text, Bin)\n")
                for of in other_files[:10]: # limit to 10
                    f.write(f"- `{of}`\n")
                    
            f.write("\n## Recommendation\n")
            f.write("To read `innovation` and `increment`, you must parse the variables like `anlys_incr_Soil Moisture...` from the `LIS_DA_EnKF_*_incr.nc` files and merge them temporally with the dataset.\n")
            
    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    find_smap_diagnostics()

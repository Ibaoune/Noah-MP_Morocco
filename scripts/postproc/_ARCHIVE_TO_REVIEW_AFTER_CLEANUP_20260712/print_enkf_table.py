import xarray as xr
import pandas as pd
from lis_postproc.diagnostics.increment_propagation.loader import discover_enkf_files, extract_time_from_filename

exp_path = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016/DA_smap_cdf_noirr_2016'
files = discover_enkf_files(exp_path)

if not files:
    print("No files found.")
    exit()

first_file = files[0]
mid_file = files[len(files)//2]
last_file = files[-1]

times = []
for f in files:
    try:
        times.append(extract_time_from_filename(f))
    except:
        pass
        
first_timestamp = min(times)
last_timestamp = max(times)
file_count = len(files)

ds = xr.open_dataset(first_file, engine='netcdf4')

print(f"{'layer':<10} | {'exact_variable_name':<40} | {'dimensions':<30} | {'units':<10} | {'long_name':<60} | {'file_count':<10} | {'first_timestamp':<20} | {'last_timestamp':<20} | {'valid_fraction':<15}")
print("-" * 230)

for i in range(1, 5):
    var_name = f'anlys_incr_Soil Moisture Layer {i}_01'
    if var_name in ds:
        v = ds[var_name]
        dims = str(v.dims)
        units = v.attrs.get('units', 'N/A')
        long_name = v.attrs.get('standard_name', 'N/A')
        
        # Calculate valid fraction for the first file
        valid_frac = float(v.notnull().sum() / v.size)
        
        print(f"{i:<10} | {var_name:<40} | {dims:<30} | {units:<10} | {long_name:<60} | {file_count:<10} | {str(first_timestamp):<20} | {str(last_timestamp):<20} | {valid_frac:.4f}")

ds.close()

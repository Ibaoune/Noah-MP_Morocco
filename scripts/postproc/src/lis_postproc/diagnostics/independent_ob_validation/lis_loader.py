import os
import glob
import xarray as xr
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class LISLoader:
    """Load LIS outputs into xarray datasets."""
    
    @staticmethod
    def load_variable(exp_dir, variable_name, start_date=None, end_date=None):
        search_path = os.path.join(exp_dir, "output", "**", "SURFACEMODEL", "**", "LIS_HIST_*.nc")
        files = glob.glob(search_path, recursive=True)
        files = sorted(files)
        
        is_smoke_test = os.environ.get("SMOKE_TEST", "0") == "1"
        if is_smoke_test:
            smoke_patterns = ['20160115', '20160415', '20160715', '20161015']
            files = [f for f in files if any(p in os.path.basename(f) for p in smoke_patterns)]
            
        if not files:
            raise FileNotFoundError(f"No LIS_HIST files found in {exp_dir}/SURFACEMODEL")
            
        # We need to extract only the requested variable to save memory
        def preprocess(d):
            keep_vars = [variable_name]
            if 'lat' in d.variables: keep_vars.append('lat')
            if 'lon' in d.variables: keep_vars.append('lon')
            d = d[keep_vars]
            if 'lat' in d.variables and 'lon' in d.variables:
                d = d.set_coords(['lat', 'lon'])
            return d
            
        try:
            ds = xr.open_mfdataset(files, combine='by_coords', engine='netcdf4', preprocess=preprocess)
        except Exception as e:
            ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', engine='netcdf4', preprocess=preprocess)
            
        # Manually extract time from filenames to ensure absolute correctness
        times = []
        for f in files:
            fname = os.path.basename(f)
            if fname.startswith("LIS_HIST_") and len(fname) >= 21:
                date_str = fname[9:17]
                try:
                    times.append(pd.to_datetime(date_str, format="%Y%m%d"))
                except:
                    pass
        
        if 'time' in ds.dims:
            if len(times) != ds.sizes['time']:
                print(f"WARNING: Extracted times ({len(times)}) != ds.time size ({ds.sizes['time']})")
                times = times[:ds.sizes['time']]
            # Must use assign_coords, direct assignment might not overwrite correctly in xarray
            ds = ds.assign_coords(time=times)
            
        # Apply layer slicing if it has SoilMoist_tavg which has 4 layers
        if variable_name == 'SoilMoist_tavg' and 'SoilMoist_profiles' in ds.dims:
            # Select first layer
            ds = ds.isel(SoilMoist_profiles=0)
            
        return ds

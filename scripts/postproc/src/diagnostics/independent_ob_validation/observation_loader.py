# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import xarray as xr
import os
import glob
import logging

logger = logging.getLogger(__name__)

class ObservationLoader:
    """Load observation data (NetCDF/TIFF) into standardized xarray datasets."""
    
    @staticmethod
    def load_dataset(cfg):
        status = cfg.get("readiness_status")
        if status != "READY":
            raise ValueError(f"Dataset {cfg['dataset_id']} is not READY. Status: {status}")
            
        full_path = cfg["local_full_path"]
        pattern = cfg.get("files", {}).get("pattern", "*.nc")
        files = glob.glob(os.path.join(full_path, "**", pattern), recursive=True)
        files = sorted(files)
        
        # Speed optimization for 2016 period experiments
        if "ESA_CCI" in full_path or "ESA_CCI" in cfg.get("dataset_id", "").upper():
            files_2016 = [f for f in files if "2016" in f]
            if files_2016:
                files = files_2016
        
        if not files:
            raise FileNotFoundError(f"No files found for {cfg['dataset_id']} with pattern {pattern}")
            
        if pattern.endswith(".tif") or pattern.endswith(".tiff"):
            return ObservationLoader._load_tiffs(cfg, files)
        else:
            return ObservationLoader._load_netcdfs(cfg, files)
            
    @staticmethod
    def _load_netcdfs(cfg, files):
        # We might need to handle specific time decoding issues
        try:
            ds = xr.open_mfdataset(files, combine='by_coords', engine='netcdf4', data_vars='minimal', coords='minimal', compat='override', chunks={'time': 1})
        except Exception as e:
            # Fallback for some tricky datasets
            ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', engine='netcdf4', data_vars='minimal', coords='minimal', compat='override', chunks={'time': 1})
            
        var_name = cfg["variables"]["observation"]
        
        # Apply scaling and offset
        scale = float(cfg.get("units", {}).get("scale_factor", 1.0))
        offset = float(cfg.get("units", {}).get("offset", 0.0))
        fill_val = cfg.get("missing_values", {}).get("fill_value")
        
        da = ds[var_name]
        
        if fill_val is not None:
            da = da.where(da != fill_val)
            
        if scale != 1.0 or offset != 0.0:
            da = da * scale + offset
            
        # Ensure standard coordinate names
        coord_map = cfg.get("coordinates", {})
        rename_dict = {}
        if coord_map.get("latitude") and coord_map.get("latitude") != "lat" and coord_map.get("latitude") in da.coords:
            rename_dict[coord_map["latitude"]] = "lat"
        if coord_map.get("longitude") and coord_map.get("longitude") != "lon" and coord_map.get("longitude") in da.coords:
            rename_dict[coord_map["longitude"]] = "lon"
        if coord_map.get("time") and coord_map.get("time") != "time" and coord_map.get("time") in da.coords:
            rename_dict[coord_map["time"]] = "time"
            
        if rename_dict:
            da = da.rename(rename_dict)
            
        # Convert to dataset
        res_ds = da.to_dataset(name=cfg["variables"]["lis"])
        # Drop duplicate times if they exist
        if 'time' in res_ds.dims and res_ds.indexes['time'].has_duplicates:
            res_ds = res_ds.drop_duplicates(dim='time')
            
        # Ensure lat/lon do not have time dimension
        for coord in ['lat', 'lon']:
            if coord in res_ds.coords and 'time' in res_ds[coord].dims:
                res_ds = res_ds.assign_coords({coord: res_ds[coord].isel(time=0).drop_vars('time', errors='ignore')})
            
        return res_ds

    @staticmethod
    def _load_tiffs(cfg, files):
        import rioxarray
        import pandas as pd
        import datetime
        datasets = []
        times = []
        for f in files:
            da = rioxarray.open_rasterio(f)
            
            basename = os.path.basename(f)
            stem = basename.replace('.tif', '').replace('.tiff', '')
            
            # Attempt to parse WaPOR dekad format (e.g. L1_AETI_1601 -> Year 16, Dekad 01)
            if len(stem) >= 4 and stem[-4:].isdigit():
                yy = int(stem[-4:-2])
                dd = int(stem[-2:])
                year = 2000 + yy if yy < 50 else 1900 + yy
                
                # Dekad 1-3 -> Jan, 4-6 -> Feb, etc.
                month = (dd - 1) // 3 + 1
                dekad_in_month = (dd - 1) % 3 + 1
                day = 1 if dekad_in_month == 1 else (11 if dekad_in_month == 2 else 21)
                
                try:
                    dt = pd.Timestamp(datetime.datetime(year, month, day))
                    times.append(dt)
                except ValueError:
                    times.append(pd.Timestamp(os.path.getmtime(f), unit='s'))
            else:
                times.append(pd.Timestamp(os.path.getmtime(f), unit='s'))
            
            if 'band' in da.dims and len(da['band']) == 1:
                da = da.squeeze('band').drop_vars('band', errors='ignore')
                
            if 'y' in da.coords and 'x' in da.coords:
                da = da.rename({'y': 'lat', 'x': 'lon'})
                
            datasets.append(da)
            
        if not datasets:
            return None
            
        time_idx = pd.DatetimeIndex(times)
        ds_concat = xr.concat(datasets, dim=xr.DataArray(time_idx, name='time'))
        
        var_name = cfg["variables"]["lis"]
        res_ds = ds_concat.to_dataset(name=var_name)
        
        scale = float(cfg.get("units", {}).get("scale_factor", 1.0))
        offset = float(cfg.get("units", {}).get("offset", 0.0))
        fill_val = cfg.get("missing_values", {}).get("fill_value")
        
        if fill_val is not None:
            res_ds[var_name] = res_ds[var_name].where(res_ds[var_name] != fill_val)
        if scale != 1.0 or offset != 0.0:
            res_ds[var_name] = res_ds[var_name] * scale + offset
            
        return res_ds

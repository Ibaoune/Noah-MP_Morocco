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
            ds = xr.open_mfdataset(files, combine='by_coords', engine='netcdf4', data_vars='minimal', coords='minimal', compat='override')
        except Exception as e:
            # Fallback for some tricky datasets
            ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', engine='netcdf4', data_vars='minimal', coords='minimal', compat='override')
            
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
        datasets = []
        for f in files:
            da = rioxarray.open_rasterio(f)
            # WaPOR files have dates in their names, e.g., L2_AETI_0911_2016.tif
            # Extract year from filename, but for generic logic we just use creation time or parse
            # Here we just stack them
            datasets.append(da)
        if not datasets:
            return None
        # Combine without assuming time dimension is present inside the TIFF
        return xr.concat(datasets, dim='time')

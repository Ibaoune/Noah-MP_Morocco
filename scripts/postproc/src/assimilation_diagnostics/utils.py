import os
import yaml
import glob
import netCDF4 as nc
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def load_config(yaml_file):
    """Load the YAML configuration file."""
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_lat_lon(base_dir, start_date):
    """Extract latitude and longitude from the first valid LIS_HIST NetCDF file."""
    yr = start_date.strftime("%Y")
    mo = start_date.strftime("%m")
    search_path = os.path.join(base_dir, f"{yr}-{mo}", "SURFACEMODEL", f"{yr}{mo}", "LIS_HIST_*.nc")
    files = glob.glob(search_path)
    if not files:
        print(f"No LIS_HIST files found in {search_path} to determine lat/lon")
        return None, None
        
    for f in files:
        try:
            ds = nc.Dataset(f, 'r')
            if 'lat' in ds.variables and 'lon' in ds.variables:
                lat = ds.variables['lat'][:]
                lon = ds.variables['lon'][:]
                ds.close()
                return lat, lon
            ds.close()
        except:
            pass
    return None, None

def add_map_features(ax, map_cfg=None, gl_cfg=None):
    """Add standard geographical features and gridlines to a map."""
    map_cfg = map_cfg or {}
    gl_cfg = gl_cfg or {}
    
    ax.coastlines(linewidth=map_cfg.get('coastline_linewidth', 0.6), 
                  color=map_cfg.get('coastline_color', '0.2'))
    ax.add_feature(cfeature.BORDERS, 
                   linewidth=map_cfg.get('border_linewidth', 0.4), 
                   linestyle=':', 
                   color=map_cfg.get('border_color', '0.3'))
    ax.set_facecolor('#f0f0f0') # Light gray for no-data regions
    
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=gl_cfg.get('linewidth', 0.3), 
                      color=gl_cfg.get('color', '0.5'), 
                      alpha=gl_cfg.get('alpha', 0.35), 
                      linestyle=gl_cfg.get('linestyle', '--'))
    gl.top_labels = False
    gl.right_labels = False
    if not gl_cfg.get('left_labels', True):
        gl.left_labels = False
    gl.xlabel_style = {'size': gl_cfg.get('label_fontsize', 10)}
    gl.ylabel_style = {'size': gl_cfg.get('label_fontsize', 10)}
    return gl

def generate_filename(out_dir, prefix, variable, exp_name, year, ext="png"):
    """
    Generate a standardized filename.
    Format: {prefix}_{variable}_{exp_name}_{year}.{ext}
    """
    filename = f"{prefix}_{variable}_{exp_name}_{year}.{ext}"
    return os.path.join(out_dir, filename)

def get_lis_files(base_dir, start_date, end_date, file_pattern="LIS_HIST_*.nc", subfolder_pattern="{yr}-{mo}/EnKF/{yr}{mo}"):
    """
    Retrieve LIS NetCDF files iterating day by day.
    """
    from datetime import timedelta
    import glob
    
    files = []
    curr_date = start_date
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        subfolder = subfolder_pattern.format(yr=yr, mo=mo)
        search_path = os.path.join(base_dir, subfolder, file_pattern)
        files.extend(glob.glob(search_path))
        
        # Advance by 1 day
        curr_date += timedelta(days=1)
        
    return sorted(list(set(files)))

def deep_merge_dicts(dict1, dict2):
    """
    Recursively merges dict2 into dict1.
    """
    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
            deep_merge_dicts(dict1[key], value)
        else:
            dict1[key] = value
    return dict1

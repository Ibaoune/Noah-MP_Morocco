# Author: M. EL Aabaribaoune (@um6p)
import xarray as xr
import pandas as pd
import yaml

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def load_netcdf(path, **kwargs):
    """Load a netcdf dataset, returning None if path is None or not found."""
    try:
        if path is None:
            return None
        return xr.open_dataset(path, **kwargs)
    except Exception as e:
        print(f"Warning: Could not load {path} - {e}")
        return None

def save_parquet(df, path):
    """Save a pandas DataFrame to parquet format."""
    df.to_parquet(path, index=False)

def load_parquet(path):
    """Load a pandas DataFrame from parquet format."""
    return pd.read_parquet(path)

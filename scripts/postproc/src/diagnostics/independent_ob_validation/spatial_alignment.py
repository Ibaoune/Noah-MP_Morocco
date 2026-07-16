# Author: M. El Aabaribaoune (@um6p)
import xarray as xr
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SpatialAlignment:
    """Handles regridding and alignment between generic datasets and LIS."""

    @staticmethod
    def normalize_longitudes(ds):
        """Ensures all longitudes are in the range [-180, 180]."""
        lon_name = 'lon' if 'lon' in ds.coords else 'longitude'
        if lon_name not in ds.coords:
            return ds
            
        lon = ds[lon_name].values
        lon = ((lon + 180) % 360) - 180
        ds = ds.assign_coords({lon_name: lon})
        return ds

    @staticmethod
    def sort_spatial_coordinates(ds):
        """Ensures latitude and longitude are monotonically increasing."""
        lon_name = 'lon' if 'lon' in ds.coords else 'longitude'
        lat_name = 'lat' if 'lat' in ds.coords else 'latitude'
        
        if lon_name in ds.coords:
            ds = ds.sortby(lon_name)
        if lat_name in ds.coords:
            ds = ds.sortby(lat_name)
        return ds

    @staticmethod
    def get_grid_bounds(ds):
        """Returns the spatial bounding box (lon_min, lon_max, lat_min, lat_max)."""
        lon_name = 'lon' if 'lon' in ds.coords else 'longitude'
        lat_name = 'lat' if 'lat' in ds.coords else 'latitude'
        
        lon = ds[lon_name].values
        lat = ds[lat_name].values
        
        return float(np.nanmin(lon)), float(np.nanmax(lon)), float(np.nanmin(lat)), float(np.nanmax(lat))

    @staticmethod
    def coordinate_edges(coord):
        """Calculate approximate coordinate edges from cell centers."""
        values = np.asarray(coord, dtype=float)
        if len(values) < 2:
            raise ValueError("Coordinate must have at least 2 points to infer edges.")
        midpoints = 0.5 * (values[:-1] + values[1:])
        first = values[0] - 0.5 * (values[1] - values[0])
        last = values[-1] + 0.5 * (values[-1] - values[-2])
        return np.concatenate([[first], midpoints, [last]])

    @staticmethod
    def subset_observation_to_domain(obs_ds, lis_bounds):
        """Clips observation strictly to LIS bounds plus half a cell margin."""
        lis_lon_min, lis_lon_max, lis_lat_min, lis_lat_max = lis_bounds
        
        lon_name = 'lon' if 'lon' in obs_ds.coords else 'longitude'
        lat_name = 'lat' if 'lat' in obs_ds.coords else 'latitude'
        
        obs_lon = obs_ds[lon_name].values
        obs_lat = obs_ds[lat_name].values
        
        obs_dlon = float(np.nanmedian(np.abs(np.diff(obs_lon)))) if len(obs_lon) > 1 else 0.25
        obs_dlat = float(np.nanmedian(np.abs(np.diff(obs_lat)))) if len(obs_lat) > 1 else 0.25
            
        margin_lon = 0.5 * obs_dlon
        margin_lat = 0.5 * obs_dlat
        
        lon_slice = slice(lis_lon_min - margin_lon, lis_lon_max + margin_lon)
        lat_slice = slice(lis_lat_min - margin_lat, lis_lat_max + margin_lat)
        
        subset = obs_ds.sel({lon_name: lon_slice, lat_name: lat_slice})
        return subset, (obs_dlon, obs_dlat)

    @staticmethod
    def aggregate_lis_to_observation_grid(lis_ds, obs_ds, min_coverage=0.50):
        """Explicit conservative area-weighted aggregation."""
        obs_lon_name = 'lon' if 'lon' in obs_ds.coords else 'longitude'
        obs_lat_name = 'lat' if 'lat' in obs_ds.coords else 'latitude'
        
        obs_lon = obs_ds[obs_lon_name].values
        obs_lat = obs_ds[obs_lat_name].values
        
        obs_lon_edges = SpatialAlignment.coordinate_edges(obs_lon)
        obs_lat_edges = SpatialAlignment.coordinate_edges(obs_lat)
        
        if 'north_south' in lis_ds.dims and 'east_west' in lis_ds.dims:
            lat_v = 'lat' if 'lat' in lis_ds.variables else 'latitude'
            lon_v = 'lon' if 'lon' in lis_ds.variables else 'longitude'
            if len(lis_ds[lat_v].dims) == 2:
                lat_1d = lis_ds[lat_v].isel(east_west=0).values
                lon_1d = lis_ds[lon_v].isel(north_south=0).values
            else:
                lat_1d = lis_ds[lat_v].values
                lon_1d = lis_ds[lon_v].values
            lis_ds = lis_ds.drop_vars([lat_v, lon_v], errors='ignore')
            lis_ds = lis_ds.rename_dims({'north_south': 'lat', 'east_west': 'lon'})
            lis_ds = lis_ds.assign_coords({lat_v: ('lat', lat_1d), lon_v: ('lon', lon_1d)})
            
        lis_lon_name = 'lon' if 'lon' in lis_ds.coords else 'longitude'
        lis_lat_name = 'lat' if 'lat' in lis_ds.coords else 'latitude'
        
        lis_lon = lis_ds[lis_lon_name].values
        lis_lat = lis_ds[lis_lat_name].values
        
        if len(lis_lon.shape) == 1 and len(lis_lat.shape) == 1:
            lis_lon_grid, lis_lat_grid = np.meshgrid(lis_lon, lis_lat)
        else:
            lis_lon_grid, lis_lat_grid = lis_lon, lis_lat
            
        lis_lon_flat = lis_lon_grid.flatten()
        lis_lat_flat = lis_lat_grid.flatten()
        
        lis_cell_area = np.cos(np.deg2rad(lis_lat_flat))
        
        lon_bins = np.digitize(lis_lon_flat, obs_lon_edges) - 1
        lat_bins = np.digitize(lis_lat_flat, obs_lat_edges) - 1
        
        valid_idx = (lon_bins >= 0) & (lon_bins < len(obs_lon)) & (lat_bins >= 0) & (lat_bins < len(obs_lat))
        
        out_ds = xr.Dataset(coords={obs_lat_name: obs_lat, obs_lon_name: obs_lon})
        
        for var in lis_ds.data_vars:
            if 'lat' not in lis_ds[var].dims or 'lon' not in lis_ds[var].dims:
                continue
                
            has_time = 'time' in lis_ds[var].dims
            has_profile = 'SoilMoist_profiles' in lis_ds[var].dims
            
            da = lis_ds[var]
            if has_profile:
                da = da.isel(SoilMoist_profiles=0)
                
            if has_time:
                times = da.time.values
                agg_data = np.full((len(times), len(obs_lat), len(obs_lon)), np.nan, dtype=np.float32)
                for t_idx in range(len(times)):
                    val_flat = da.isel(time=t_idx).values.flatten()
                    flat_obs_idx = lat_bins[valid_idx] * len(obs_lon) + lon_bins[valid_idx]
                    
                    val_valid = val_flat[valid_idx]
                    weight_valid = lis_cell_area[valid_idx]
                    not_nan = ~np.isnan(val_valid)
                    
                    if not_nan.any():
                        w_sum = np.bincount(flat_obs_idx[not_nan], weights=(val_valid * weight_valid)[not_nan], minlength=len(obs_lat)*len(obs_lon))
                        w_tot = np.bincount(flat_obs_idx[not_nan], weights=weight_valid[not_nan], minlength=len(obs_lat)*len(obs_lon))
                        count_tot = np.bincount(flat_obs_idx, minlength=len(obs_lat)*len(obs_lon))
                        count_valid = np.bincount(flat_obs_idx[not_nan], minlength=len(obs_lat)*len(obs_lon))
                        
                        coverage = np.zeros_like(count_tot, dtype=float)
                        np.divide(count_valid, count_tot, out=coverage, where=count_tot>0)
                        
                        mean_val = np.full_like(w_sum, np.nan)
                        np.divide(w_sum, w_tot, out=mean_val, where=w_tot>0)
                        mean_val[coverage < min_coverage] = np.nan
                        
                        agg_data[t_idx, :, :] = mean_val.reshape((len(obs_lat), len(obs_lon)))
                        
                out_ds[var] = xr.DataArray(agg_data, coords=[times, obs_lat, obs_lon], dims=['time', obs_lat_name, obs_lon_name])
            else:
                val_flat = da.values.flatten()
                flat_obs_idx = lat_bins[valid_idx] * len(obs_lon) + lon_bins[valid_idx]
                val_valid = val_flat[valid_idx]
                weight_valid = lis_cell_area[valid_idx]
                
                not_nan = ~np.isnan(val_valid)
                if not_nan.any():
                    w_sum = np.bincount(flat_obs_idx[not_nan], weights=(val_valid * weight_valid)[not_nan], minlength=len(obs_lat)*len(obs_lon))
                    w_tot = np.bincount(flat_obs_idx[not_nan], weights=weight_valid[not_nan], minlength=len(obs_lat)*len(obs_lon))
                    count_tot = np.bincount(flat_obs_idx, minlength=len(obs_lat)*len(obs_lon))
                    count_valid = np.bincount(flat_obs_idx[not_nan], minlength=len(obs_lat)*len(obs_lon))
                    
                    coverage = np.zeros_like(count_tot, dtype=float)
                    np.divide(count_valid, count_tot, out=coverage, where=count_tot>0)
                    
                    mean_val = np.full_like(w_sum, np.nan)
                    np.divide(w_sum, w_tot, out=mean_val, where=w_tot>0)
                    mean_val[coverage < min_coverage] = np.nan
                    
                    out_ds[var] = xr.DataArray(mean_val.reshape((len(obs_lat), len(obs_lon))), coords=[obs_lat, obs_lon], dims=[obs_lat_name, obs_lon_name])
        
        return out_ds

    @staticmethod
    def build_lis_valid_mask(lis_ds):
        """Builds a primary binary mask from the valid LIS simulation grid cells."""
        if 'SoilMoist_tavg' in lis_ds.data_vars:
            da = lis_ds['SoilMoist_tavg']
            if 'SoilMoist_profiles' in da.dims:
                da = da.isel(SoilMoist_profiles=0)
            if 'time' in da.dims:
                return da.notnull().any(dim='time')
            return da.notnull()
        return None

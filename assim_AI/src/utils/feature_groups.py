# Author: M. EL Aabaribaoune (@um6p)
# Grouping predictors to help explain dominant factors

FEATURE_GROUPS = {
    'precipitation_forcing': [
        'imerg_precip', 'insitu_precip', 'precip_error', 
        'ant_precip_7d', 'ant_precip_30d', 'ant_precip_90d'
    ],
    'meteorology': [
        't2m', 'q2m', 'swdown', 'lwdown', 'wind'
    ],
    'model_initial_state': [
        'opl_ssm', 'opl_rzsm', 'opl_et', 'opl_runoff', 'opl_baseflow'
    ],
    'topography': [
        'elevation', 'slope'
    ],
    'land_cover_and_management': [
        'land_cover', 'cropland_fraction', 'irrigation_proxy'
    ],
    'soil': [
        'soil_texture', 'sand_fraction', 'clay_fraction'
    ],
    'smap_obs_availability': [
        'smap_obs_count', 'smap_quality_count'
    ]
}

def get_group_name(feature_name):
    """Return the group name for a given feature."""
    for group, features in FEATURE_GROUPS.items():
        # Using simple substring match because exact names might vary
        if any(f in feature_name.lower() for f in features):
            return group
    return 'other'

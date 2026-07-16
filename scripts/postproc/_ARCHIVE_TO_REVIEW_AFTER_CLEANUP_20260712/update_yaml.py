import yaml
import sys

with open('configs/recipes/smap_cdf_sensitivity_2016.yaml', 'r') as f:
    recipe = yaml.safe_load(f)

recipe['diagnostics']['increment_propagation'] = {
  'enabled': True,
  'increment_source': {
    'priority': ['explicit_increment', 'analysis_minus_forecast'],
    'allow_da_minus_opl_proxy': False
  },
  'soil_layers': {
    'thickness_m': [0.1, 0.3, 0.6, 1.0],
    'labels': ["0–10 cm", "10–40 cm", "40–100 cm", "100–200 cm"]
  },
  'event_detection': {
    'spatial_aggregation': 'basin_mean',
    'method': 'quantile',
    'threshold_quantile': 0.75,
    'strong_event_quantile': 0.90,
    'minimum_absolute_increment_mm': 0.1,
    'minimum_separation_days': 3,
    'separate_positive_negative': True,
    'exclude_boundary_events': True
  },
  'composites': {
    'full_window_days': 14,
    'lags_days': [0, 1, 3, 7, 14],
    'statistic': 'median',
    'bootstrap_samples': 1000,
    'confidence_level': 0.95
  },
  'lagged_correlation': {
    'enabled': True,
    'max_lag_days': 14,
    'methods': ['pearson', 'spearman'],
    'minimum_samples': 20,
    'significance_level': 0.05
  },
  'persistence': {
    'enabled': True,
    'threshold_fraction': 0.20,
    'consecutive_days_below_threshold': 2,
    'maximum_duration_days': 14,
    'compute_efolding_time': True
  },
  'transfer_efficiency': {
    'enabled': True,
    'lags_days': [0, 1, 3, 7, 14],
    'minimum_denominator_mm': 0.1,
    'mask_extreme_ratios': True,
    'ratio_limits_for_plot': [-2.0, 2.0],
    'report_unclipped_statistics': True
  },
  'precipitation_control': {
    'enabled': True,
    'accumulation_windows_days': [1, 3, 7, 14],
    'dry_threshold_mm_1d': 1.0,
    'dry_threshold_mm_3d': 3.0,
    'categories': ['all', 'dry_following_period', 'wet_following_period']
  }
}

with open('configs/recipes/smap_cdf_sensitivity_2016.yaml', 'w') as f:
    yaml.dump(recipe, f, default_flow_style=False, sort_keys=False)

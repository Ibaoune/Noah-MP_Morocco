import numpy as np

def calculate_bias(obs, mod):
    return np.nanmean(mod - obs)

def calculate_rmse(obs, mod):
    return np.sqrt(np.nanmean((mod - obs)**2))

def calculate_correlation(obs, mod):
    valid = ~np.isnan(obs) & ~np.isnan(mod)
    if not np.any(valid): return np.nan
    return np.corrcoef(obs[valid], mod[valid])[0, 1]

# Autres métriques (ubRMSE, NSE, KGE) à ajouter selon le besoin.

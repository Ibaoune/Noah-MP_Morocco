# Author: M. EL Aabaribaoune (@um6p)
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.inspection import permutation_importance
import scipy.stats as stats
import numpy as np

def train_rf_model(X_train, y_train, **kwargs):
    """Train a Random Forest Regressor."""
    model = RandomForestRegressor(random_state=42, n_jobs=-1, **kwargs)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate model and return a dictionary of metrics."""
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    
    # Handle constant predictions or constant true values for Pearson
    if np.std(preds) == 0 or np.std(y_test) == 0:
        pearson = 0.0
    else:
        pearson, _ = stats.pearsonr(y_test, preds)
        
    return {
        'R2': r2,
        'RMSE': rmse,
        'MAE': mae,
        'Pearson': pearson
    }

def get_permutation_importance(model, X_test, y_test):
    """Calculate and return permutation feature importance."""
    result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
    return result.importances_mean, result.importances_std

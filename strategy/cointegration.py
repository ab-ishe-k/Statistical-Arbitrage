"""
Cointegration & Statistical Modeling Module.
Implements OLS Hedge Ratio Estimation, Engle-Granger ADF Stationarity Testing, and Ornstein-Uhlenbeck Half-Life Computation.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

def calculate_hedge_ratio(series_a: pd.Series, series_b: pd.Series) -> Tuple[float, float]:
    """
    Calculates Hedge Ratio (Beta) using Ordinary Least Squares (OLS) Linear Regression.
    Price_A = alpha + beta * Price_B
    """
    if len(series_a) != len(series_b):
        raise ValueError("Series lengths do not match.")
    if len(series_a) < 10:
        raise ValueError("Insufficient sample size for OLS estimation.")
        
    beta, alpha = np.polyfit(series_b, series_a, 1)
    return float(beta), float(alpha)

def run_engle_granger_test(series_a: pd.Series, series_b: pd.Series, p_threshold: float = 0.05) -> Dict[str, Any]:
    """
    Performs Engle-Granger two-step cointegration test:
    1. Estimate OLS regression PriceA = alpha + beta * PriceB -> Spread residuals.
    2. Run Augmented Dickey-Fuller (ADF) test on Spread residuals to evaluate stationarity.
    """
    beta, alpha = calculate_hedge_ratio(series_a, series_b)
    spread = series_a - (beta * series_b) - alpha
    
    try:
        import warnings
        from statsmodels.tsa.stattools import adfuller
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            adf_result = adfuller(spread, autolag='AIC')
            
        test_stat = float(adf_result[0])
        p_value = float(adf_result[1])
        crit_values = dict(adf_result[4])
    except Exception as e:
        raise RuntimeError(f"ADF Cointegration test failed to execute: {e}")
        
    is_cointegrated = p_value < p_threshold
    half_life = calculate_half_life(spread)
    
    return {
        'p_value': p_value,
        'test_stat': test_stat,
        'beta': beta,
        'alpha': alpha,
        'critical_values': crit_values,
        'is_cointegrated': is_cointegrated,
        'half_life_bars': half_life
    }

# Alias for backward compatibility
test_cointegration = run_engle_granger_test

def calculate_half_life(spread: pd.Series) -> float:
    """
    Calculates the Half-Life of Mean Reversion using an AR(1) Ornstein-Uhlenbeck process:
    Delta Spread_t = lambda * Spread_{t-1} + mu + epsilon_t
    Half-Life = -ln(2) / lambda
    """
    spread_clean = spread.dropna()
    if len(spread_clean) < 10:
        return np.nan
        
    spread_lag = spread_clean.shift(1).iloc[1:]
    spread_diff = spread_clean.diff().iloc[1:]
    
    if len(spread_lag) < 5 or np.std(spread_lag) == 0:
        return np.nan
        
    lambda_coef, _ = np.polyfit(spread_lag, spread_diff, 1)
    
    if lambda_coef >= 0:
        return np.nan
        
    half_life = -np.log(2) / lambda_coef
    return float(half_life)

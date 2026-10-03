"""
Data Generator Module - Creates synthetic cointegrated asset price series for backtesting.
"""
import numpy as np
import pandas as pd

def generate_cointegrated_pairs(n_bars=500, beta=1.2, noise_std=1.5, seed=42):
    """
    Generates synthetic cointegrated price series for Stock A and Stock B.
    Stock B follows a random walk.
    Stock A = beta * Stock B + stationary noise.
    """
    np.random.seed(seed)
    
    # Random walk for Stock B
    returns_b = np.random.normal(loc=0.0005, scale=0.015, size=n_bars)
    price_b = 100 * np.exp(np.cumsum(returns_b))
    
    # Mean-reverting stationary noise
    noise = np.zeros(n_bars)
    phi = 0.85 # AR(1) coefficient for mean reversion
    for t in range(1, n_bars):
        noise[t] = phi * noise[t-1] + np.random.normal(0, noise_std)
        
    # Stock A constructed to be cointegrated with Stock B
    price_a = beta * price_b + noise + 20.0
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq='D')
    
    df = pd.DataFrame({
        'Stock_A': price_a,
        'Stock_B': price_b
    }, index=dates)
    
    return df

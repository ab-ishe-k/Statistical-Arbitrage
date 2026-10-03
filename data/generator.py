"""
Data Generator Module - Creates synthetic cointegrated asset price series for strategy testing.
"""
import numpy as np
import pandas as pd
from data.validation import validate_price_series

def generate_cointegrated_pairs(n_bars: int = 500, beta: float = 1.2, noise_std: float = 1.5, seed: int = 42) -> pd.DataFrame:
    """
    Generates deterministic, seedable synthetic cointegrated price series for Stock A and Stock B.
    Stock B follows a geometric Brownian motion (random walk).
    Stock A = beta * Stock B + mean-reverting AR(1) stationary spread process + alpha offset.
    """
    np.random.seed(seed)
    
    # Geometric Brownian motion for Stock B
    returns_b = np.random.normal(loc=0.0003, scale=0.012, size=n_bars)
    price_b = 100.0 * np.exp(np.cumsum(returns_b))
    
    # AR(1) stationary mean-reverting noise process for the spread
    noise = np.zeros(n_bars)
    phi = 0.82  # Mean reversion AR(1) speed coefficient (0 < phi < 1)
    for t in range(1, n_bars):
        noise[t] = phi * noise[t-1] + np.random.normal(0, noise_std)
        
    # Construct Stock A to be cointegrated with Stock B
    alpha_offset = 25.0
    price_a = beta * price_b + noise + alpha_offset
    
    dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=n_bars, freq='D')
    
    df = pd.DataFrame({
        'Stock_A': price_a,
        'Stock_B': price_b
    }, index=dates)
    
    return validate_price_series(df, min_bars=30)

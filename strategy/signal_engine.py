"""
Signal Engine Module - Calculates Residual Spread, Rolling Z-Scores, and State Machine Signals.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any

# Signal State Machine Constants
FLAT = 0
LONG_SPREAD = 1        # Buy Asset A, Sell Asset B (Asset A Undervalued, Z <= -entry_z)
SHORT_SPREAD = -1      # Sell Asset A, Buy Asset B (Asset A Overvalued, Z >= +entry_z)
EXIT_SIGNAL = 0        # Exit position on mean reversion (|Z| <= exit_z)
STOP_LOSS_SIGNAL = 99  # Exit position on statistical breakdown (|Z| >= stop_z)

def calculate_spread(series_a: pd.Series, series_b: pd.Series, beta: float, alpha: float = 0.0) -> pd.Series:
    """
    Spread_t = PriceA_t - (beta * PriceB_t) - alpha
    """
    return series_a - (beta * series_b) - alpha

def calculate_rolling_zscore(spread: pd.Series, window: int = 20, shift_for_no_leakage: bool = True) -> pd.Series:
    """
    Z_t = (Spread_t - Mean_{t-1}) / Std_{t-1}
    
    If shift_for_no_leakage is True, rolling mean and rolling std dev are calculated 
    strictly on past observations [t-window, t-1] using shift(1).
    This guarantees zero look-ahead data leakage into signal parameters.
    """
    if shift_for_no_leakage:
        past_spread = spread.shift(1)
        mean = past_spread.rolling(window=window, min_periods=window).mean()
        std = past_spread.rolling(window=window, min_periods=window).std()
    else:
        mean = spread.rolling(window=window, min_periods=window).mean()
        std = spread.rolling(window=window, min_periods=window).std()
        
    std = std.replace(0, np.nan)
    z_score = (spread - mean) / std
    return z_score

def generate_signals(
    df: pd.DataFrame, 
    beta: float, 
    alpha: float = 0.0,
    lookback: int = 20, 
    entry_z: float = 2.0, 
    exit_z: float = 0.2, 
    stop_z: float = 3.5,
    shift_for_no_leakage: bool = True
) -> pd.DataFrame:
    """
    Generates quantitative market-neutral trading signals using a state machine:
    - Long Spread (1):  Z <= -entry_z  (Buy A, Short B)
    - Short Spread (-1): Z >= +entry_z  (Short A, Buy B)
    - Exit (0):          |Z| <= exit_z  (Mean Reversion Exit)
    - Stop Loss (99):    |Z| >= stop_z  (Statistical Breakdown Exit)
    """
    df = df.copy()
    df['Spread'] = calculate_spread(df['Stock_A'], df['Stock_B'], beta, alpha)
    df['Z_Score'] = calculate_rolling_zscore(df['Spread'], window=lookback, shift_for_no_leakage=shift_for_no_leakage)
    
    signals = pd.Series(index=df.index, data=FLAT, dtype=int)
    current_state = FLAT
    
    for i in range(len(df)):
        z = df['Z_Score'].iloc[i]
        
        if pd.isna(z):
            signals.iloc[i] = FLAT
            continue
            
        # Check Stop-Loss
        if abs(z) >= stop_z:
            if current_state != FLAT:
                signals.iloc[i] = STOP_LOSS_SIGNAL
                current_state = FLAT
        # Check Entry
        elif current_state == FLAT:
            if z <= -entry_z:
                signals.iloc[i] = LONG_SPREAD
                current_state = LONG_SPREAD
            elif z >= entry_z:
                signals.iloc[i] = SHORT_SPREAD
                current_state = SHORT_SPREAD
        # Check Exit (Mean Reversion)
        elif current_state != FLAT:
            if abs(z) <= exit_z:
                signals.iloc[i] = EXIT_SIGNAL
                current_state = FLAT
            else:
                signals.iloc[i] = current_state  # Maintain current active state
                
    df['Signal'] = signals
    return df

"""
Data Validation & Integrity Engineering Module.
Ensures time series datasets are clean, synchronized, chronological, and free of missing values.
"""
import pandas as pd
import numpy as np

def validate_price_series(df: pd.DataFrame, min_bars: int = 30) -> pd.DataFrame:
    """
    Validates, cleans, and synchronizes a pair price DataFrame.
    Enforces:
    1. Required columns ('Stock_A', 'Stock_B').
    2. Datetime index ordering (strictly ascending).
    3. Removal of duplicate timestamps.
    4. Forward-filling / interpolation of missing values.
    5. Non-zero, strictly positive price validation.
    6. Minimum history length.
    """
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None.")
        
    required_cols = ['Stock_A', 'Stock_B']
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required price column: {col}")
            
    df_clean = df.copy()
    
    # Ensure DatetimeIndex
    if not isinstance(df_clean.index, pd.DatetimeIndex):
        try:
            df_clean.index = pd.to_datetime(df_clean.index)
        except Exception as e:
            raise ValueError(f"Could not convert index to DatetimeIndex: {e}")
            
    # Sort index ascending
    df_clean = df_clean.sort_index()
    
    # Remove duplicate timestamps
    df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
    
    # Clean non-numeric or missing values
    df_clean['Stock_A'] = pd.to_numeric(df_clean['Stock_A'], errors='coerce')
    df_clean['Stock_B'] = pd.to_numeric(df_clean['Stock_B'], errors='coerce')
    
    # Forward fill then backward fill missing values
    df_clean = df_clean.ffill().bfill()
    
    # Drop any remaining NaNs
    df_clean = df_clean.dropna(subset=['Stock_A', 'Stock_B'])
    
    # Check positive prices
    if (df_clean['Stock_A'] <= 0).any() or (df_clean['Stock_B'] <= 0).any():
        raise ValueError("Price series contains zero or negative price values.")
        
    if len(df_clean) < min_bars:
        raise ValueError(f"Insufficient history: dataset has {len(df_clean)} bars, minimum required is {min_bars}.")
        
    return df_clean

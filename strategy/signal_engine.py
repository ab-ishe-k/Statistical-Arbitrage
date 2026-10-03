"""
Signal Engine Module - Calculates Spread, Rolling Z-Score and Generates Entry/Exit Trading Signals.
"""
import numpy as np
import pandas as pd
from config import settings

def calculate_spread(series_a, series_b, beta):
    """
    Spread_t = PriceA_t - beta * PriceB_t
    """
    return series_a - beta * series_b

def calculate_rolling_zscore(spread, window=settings.LOOKBACK_WINDOW):
    """
    Z-score = (Current Spread - Rolling Mean Spread) / Rolling Standard Deviation
    """
    mean_spread = spread.rolling(window=window).mean()
    std_spread = spread.rolling(window=window).std()
    
    # Prevent division by zero
    std_spread = std_spread.replace(0, np.nan)
    
    z_score = (spread - mean_spread) / std_spread
    return z_score

def generate_signals(df, beta):
    """
    Generates quantitative market-neutral signals:
     1  : BUY Stock A, SELL Stock B (Z-score < -2.0) [Stock A Undervalued]
    -1  : SELL Stock A, BUY Stock B (Z-score > +2.0) [Stock A Overvalued]
     0  : EXIT position (Reverted to Mean |Z| < 0.2)
    99  : STOP-LOSS exit (|Z| > 3.5)
    """
    df = df.copy()
    df['Spread'] = calculate_spread(df['Stock_A'], df['Stock_B'], beta)
    df['Z_Score'] = calculate_rolling_zscore(df['Spread'])
    
    signals = pd.Series(index=df.index, data=0)
    
    position = 0 # 0: flat, 1: long A short B, -1: short A long B
    
    for i in range(len(df)):
        z = df['Z_Score'].iloc[i]
        
        if pd.isna(z):
            signals.iloc[i] = 0
            continue
            
        # Check Stop Loss condition
        if abs(z) >= settings.STOP_LOSS_Z_SCORE:
            if position != 0:
                signals.iloc[i] = 99 # Stop loss signal
                position = 0
        # Check Entry conditions
        elif position == 0:
            if z <= -settings.ENTRY_Z_SCORE:
                signals.iloc[i] = 1 # Buy A, Sell B
                position = 1
            elif z >= settings.ENTRY_Z_SCORE:
                signals.iloc[i] = -1 # Sell A, Buy B
                position = -1
        # Check Exit condition (Mean Reversion)
        elif position != 0:
            if abs(z) <= settings.EXIT_Z_SCORE:
                signals.iloc[i] = 0 # Exit signal
                position = 0
            else:
                signals.iloc[i] = position # Maintain active position
                
    df['Signal'] = signals
    return df

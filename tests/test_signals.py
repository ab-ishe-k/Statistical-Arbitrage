"""
Unit Tests for Signal Generation Engine.
"""
import pytest
import pandas as pd
import numpy as np
from strategy.signal_engine import generate_signals, calculate_rolling_zscore, LONG_SPREAD, SHORT_SPREAD, FLAT

def test_signal_generation_thresholds():
    # Construct cointegrated synthetic pair with a clear step shift
    np.random.seed(42)
    b_series = np.linspace(100, 120, 100)
    a_series = 1.2 * b_series + 15.0 + np.random.normal(0, 0.5, 100)
    
    df = pd.DataFrame({
        'Stock_A': a_series,
        'Stock_B': b_series
    }, index=pd.date_range('2025-01-01', periods=100))
    
    # Introduce sharp divergence on bars 50..55
    df.iloc[50:55, 0] += 15.0
    
    df_sig = generate_signals(df, beta=1.2, alpha=15.0, lookback=20, entry_z=1.5, shift_for_no_leakage=True)
    assert 'Z_Score' in df_sig.columns
    assert 'Signal' in df_sig.columns
    assert (df_sig['Signal'] != FLAT).any()

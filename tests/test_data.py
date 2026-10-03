"""
Unit Tests for Data Validation & Preprocessing.
"""
import pytest
import pandas as pd
import numpy as np
from data.validation import validate_price_series
from data.generator import generate_cointegrated_pairs

def test_generate_cointegrated_pairs():
    df = generate_cointegrated_pairs(n_bars=200, seed=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 200
    assert 'Stock_A' in df.columns and 'Stock_B' in df.columns
    assert not df.isnull().any().any()

def test_validate_price_series_clean():
    df = generate_cointegrated_pairs(n_bars=100, seed=42)
    clean_df = validate_price_series(df, min_bars=50)
    assert len(clean_df) == 100

def test_validate_price_series_missing_values():
    df = generate_cointegrated_pairs(n_bars=100, seed=42)
    df.iloc[10, 0] = np.nan
    clean_df = validate_price_series(df, min_bars=50)
    assert not clean_df.isnull().any().any()

def test_validate_price_series_insufficient_history():
    raw_df = pd.DataFrame({
        'Stock_A': [100.0] * 20,
        'Stock_B': [100.0] * 20
    }, index=pd.date_range('2025-01-01', periods=20))
    
    with pytest.raises(ValueError, match="Insufficient history"):
        validate_price_series(raw_df, min_bars=50)

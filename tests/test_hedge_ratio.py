"""
Unit Tests for Hedge Ratio & Cointegration Modeling.
"""
import pytest
import numpy as np
import pandas as pd
from strategy.cointegration import calculate_hedge_ratio, run_engle_granger_test, calculate_half_life

def test_calculate_hedge_ratio():
    np.random.seed(42)
    b_series = pd.Series(np.linspace(100, 150, 100))
    a_series = 1.5 * b_series + 10.0 + np.random.normal(0, 0.1, 100)
    
    beta, alpha = calculate_hedge_ratio(a_series, b_series)
    assert pytest.approx(beta, rel=1e-1) == 1.5
    assert pytest.approx(alpha, abs=2.0) == 10.0

def test_calculate_half_life_mean_reverting():
    np.random.seed(42)
    spread = [0.0]
    for _ in range(200):
        spread.append(0.7 * spread[-1] + np.random.normal(0, 1))
    s_series = pd.Series(spread)
    
    hl = calculate_half_life(s_series)
    assert not np.isnan(hl)
    assert hl > 0.0

def test_run_engle_granger_test():
    np.random.seed(42)
    b_series = pd.Series(np.cumsum(np.random.normal(0, 1, 200)) + 100)
    a_series = 1.2 * b_series + np.random.normal(0, 0.5, 200) + 15
    
    res = run_engle_granger_test(a_series, b_series)
    assert 'p_value' in res
    assert 'beta' in res
    assert 'is_cointegrated' in res
    assert isinstance(res['is_cointegrated'], (bool, np.bool_))

"""
Unit Tests for Walk-Forward Event-Driven Backtesting Pipeline.
"""
import pytest
import pandas as pd
from data.generator import generate_cointegrated_pairs
from backtest.engine import WalkForwardBacktester

def test_walk_forward_backtest_pipeline():
    df = generate_cointegrated_pairs(n_bars=300, seed=42)
    bt = WalkForwardBacktester(initial_capital=10000.0, training_window=100, lookback_window=20)
    
    metrics, ledger, equity_df = bt.run(df)
    
    assert isinstance(metrics, dict)
    assert 'Sharpe Ratio' in metrics
    assert 'Max Drawdown (%)' in metrics
    assert isinstance(ledger, pd.DataFrame)
    assert isinstance(equity_df, pd.DataFrame)
    assert 'Equity' in equity_df.columns
    assert len(equity_df) == 300

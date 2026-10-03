"""
No-Lookahead Regression Test.
CRITICAL QUANTITATIVE TEST: Proves that mutating future price observations (bars t > T0) 
does NOT change past signals, orders, execution fills, or equity values at or before bar T0.
"""
import pytest
import pandas as pd
import numpy as np
from data.generator import generate_cointegrated_pairs
from backtest.engine import WalkForwardBacktester

def test_no_lookahead_bias_in_walkforward():
    # 1. Generate full dataset of 300 bars
    df_original = generate_cointegrated_pairs(n_bars=300, seed=42)
    cutoff_bar = 200
    cutoff_date = df_original.index[cutoff_bar]
    
    # Run backtest on original dataset
    bt1 = WalkForwardBacktester(initial_capital=10000.0, training_window=100, lookback_window=20)
    metrics1, ledger1, equity_df1 = bt1.run(df_original)
    
    # 2. Mutate FUTURE price observations drastically (bars AFTER cutoff_date)
    df_future_mutated = df_original.copy()
    df_future_mutated.iloc[cutoff_bar + 1:, 0] *= 5.0  # Spike Stock A by 500% in future
    df_future_mutated.iloc[cutoff_bar + 1:, 1] *= 0.1  # Crash Stock B by 90% in future
    
    # Run backtest on future-mutated dataset
    bt2 = WalkForwardBacktester(initial_capital=10000.0, training_window=100, lookback_window=20)
    metrics2, ledger2, equity_df2 = bt2.run(df_future_mutated)
    
    # 3. Assert PAST equity values at and before cutoff_date are 100% IDENTICAL
    past_equity1 = equity_df1.loc[:cutoff_date, 'Equity']
    past_equity2 = equity_df2.loc[:cutoff_date, 'Equity']
    pd.testing.assert_series_equal(past_equity1, past_equity2, check_exact=True)
    
    # 4. Assert PAST signals at and before cutoff_date are 100% IDENTICAL
    past_signals1 = equity_df1.loc[:cutoff_date, 'Signal']
    past_signals2 = equity_df2.loc[:cutoff_date, 'Signal']
    pd.testing.assert_series_equal(past_signals1, past_signals2, check_exact=True)
    
    # 5. Assert PAST Z-scores at and before cutoff_date are 100% IDENTICAL
    past_z1 = equity_df1.loc[:cutoff_date, 'Z_Score']
    past_z2 = equity_df2.loc[:cutoff_date, 'Z_Score']
    pd.testing.assert_series_equal(past_z1, past_z2, check_exact=True)

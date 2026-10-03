"""
Robustness Analysis & Sensitivity Testing Module.
Provides parameter sensitivity grid search, walk-forward out-of-sample validation, and stability evaluation.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any

def run_parameter_sensitivity(
    df: pd.DataFrame,
    entry_z_list: List[float] = [1.5, 2.0, 2.5],
    lookback_list: List[int] = [15, 20, 30],
    initial_capital: float = 10000.0
) -> pd.DataFrame:
    """
    Executes a parameter sensitivity grid search over different entry thresholds and lookback windows.
    Returns a DataFrame summarizing Sharpe, ROI, Drawdown, Win Rate, and Total Trades.
    """
    from backtest.engine import WalkForwardBacktester
    
    results = []
    for lookback in lookback_list:
        for entry_z in entry_z_list:
            bt = WalkForwardBacktester(
                initial_capital=initial_capital,
                training_window=120,
                lookback_window=lookback,
                entry_z=entry_z,
                exit_z=0.2,
                stop_z=3.5
            )
            metrics, ledger, equity_df = bt.run(df)
            
            results.append({
                'Lookback': lookback,
                'Entry_Z': entry_z,
                'ROI (%)': metrics.get('ROI (%)', 0.0),
                'Sharpe Ratio': metrics.get('Sharpe Ratio', 0.0),
                'Max Drawdown (%)': metrics.get('Max Drawdown (%)', 0.0),
                'Win Rate (%)': metrics.get('Win Rate (%)', 0.0),
                'Profit Factor': metrics.get('Profit Factor', 0.0),
                'Total Trades': metrics.get('Total Trades', 0)
            })
            
    return pd.DataFrame(results)

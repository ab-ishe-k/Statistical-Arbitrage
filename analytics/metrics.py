"""
Quantitative Performance Analytics & Metrics Engine.
Computes mathematically rigorous risk-adjusted performance metrics.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List

def compute_performance_metrics(
    equity_series: pd.Series,
    trade_ledger: pd.DataFrame,
    initial_capital: float,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Computes comprehensive, defensible quantitative strategy metrics.
    """
    if equity_series.empty or len(equity_series) < 2:
        raise ValueError("Equity series must contain at least two observations.")
        
    final_capital = float(equity_series.iloc[-1])
    net_profit = final_capital - initial_capital
    roi_pct = (net_profit / initial_capital) * 100.0
    
    # Daily returns series
    daily_returns = equity_series.pct_change().fillna(0.0)
    
    # Annualized Sharpe Ratio
    ret_std = float(daily_returns.std())
    ret_mean = float(daily_returns.mean())
    if ret_std > 1e-8:
        sharpe_ratio = (ret_mean / ret_std) * np.sqrt(trading_days_per_year)
    else:
        sharpe_ratio = 0.0
        
    # Annualized Sortino Ratio (downside risk only)
    downside_returns = daily_returns[daily_returns < 0.0]
    downside_std = float(downside_returns.std()) if len(downside_returns) > 0 else 0.0
    if downside_std > 1e-8:
        sortino_ratio = (ret_mean / downside_std) * np.sqrt(trading_days_per_year)
    else:
        sortino_ratio = 0.0
        
    # Drawdown calculations
    cummax = equity_series.cummax()
    drawdown_series = (equity_series - cummax) / cummax
    max_drawdown_pct = float(drawdown_series.min()) * 100.0
    
    # Drawdown Duration
    is_in_drawdown = drawdown_series < 0
    drawdown_durations = []
    current_dur = 0
    for in_dd in is_in_drawdown:
        if in_dd:
            current_dur += 1
        else:
            if current_dur > 0:
                drawdown_durations.append(current_dur)
            current_dur = 0
    if current_dur > 0:
        drawdown_durations.append(current_dur)
    max_drawdown_duration = max(drawdown_durations) if drawdown_durations else 0
    
    # Annualized CAGR
    n_days = len(equity_series)
    if n_days > 1:
        years = n_days / trading_days_per_year
        cagr_pct = (((final_capital / initial_capital) ** (1.0 / max(years, 0.01))) - 1.0) * 100.0
    else:
        cagr_pct = 0.0
        
    # Calmar Ratio
    calmar_ratio = (cagr_pct / abs(max_drawdown_pct)) if abs(max_drawdown_pct) > 1e-5 else 0.0
    
    # Trade Level Analytics
    total_trades = len(trade_ledger)
    total_commissions = float(trade_ledger['Fees ($)'].sum()) if not trade_ledger.empty and 'Fees ($)' in trade_ledger.columns else 0.0
    total_slippage = float(trade_ledger['Slippage ($)'].sum()) if not trade_ledger.empty and 'Slippage ($)' in trade_ledger.columns else 0.0
    
    if total_trades > 0 and 'Net PnL ($)' in trade_ledger.columns:
        net_pnls = trade_ledger['Net PnL ($)'].astype(float)
        wins = net_pnls[net_pnls > 0]
        losses = net_pnls[net_pnls < 0]
        
        n_wins = len(wins)
        n_losses = len(losses)
        win_rate_pct = (n_wins / total_trades) * 100.0
        
        avg_win = float(wins.mean()) if n_wins > 0 else 0.0
        avg_loss = float(abs(losses.mean())) if n_losses > 0 else 0.0
        win_loss_ratio = (avg_win / avg_loss) if avg_loss > 0 else 0.0
        
        gross_profits = float(wins.sum()) if n_wins > 0 else 0.0
        gross_losses = float(abs(losses.sum())) if n_losses > 0 else 0.0
        profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else (np.inf if gross_profits > 0 else 0.0)
        
        expectancy = ((win_rate_pct / 100.0) * avg_win) - (((100.0 - win_rate_pct) / 100.0) * avg_loss)
        
        if 'Holding Period (bars)' in trade_ledger.columns:
            avg_holding_period = float(trade_ledger['Holding Period (bars)'].mean())
        else:
            avg_holding_period = 0.0
    else:
        win_rate_pct = 0.0
        avg_win = 0.0
        avg_loss = 0.0
        win_loss_ratio = 0.0
        profit_factor = 0.0
        expectancy = 0.0
        gross_profits = 0.0
        gross_losses = 0.0
        avg_holding_period = 0.0

    return {
        'Initial Capital ($)': initial_capital,
        'Final Capital ($)': final_capital,
        'Net Profit ($)': net_profit,
        'ROI (%)': roi_pct,
        'CAGR (%)': cagr_pct,
        'Sharpe Ratio': float(sharpe_ratio),
        'Sortino Ratio': float(sortino_ratio),
        'Calmar Ratio': float(calmar_ratio),
        'Max Drawdown (%)': float(max_drawdown_pct),
        'Max Drawdown Duration (bars)': int(max_drawdown_duration),
        'Total Trades': int(total_trades),
        'Win Rate (%)': float(win_rate_pct),
        'Gross Profit ($)': float(gross_profits),
        'Gross Loss ($)': float(gross_losses),
        'Profit Factor': float(profit_factor),
        'Average Win ($)': float(avg_win),
        'Average Loss ($)': float(avg_loss),
        'Win/Loss Ratio': float(win_loss_ratio),
        'Expectancy ($)': float(expectancy),
        'Average Holding Period (bars)': float(avg_holding_period),
        'Total Commissions ($)': float(total_commissions),
        'Total Slippage ($)': float(total_slippage)
    }

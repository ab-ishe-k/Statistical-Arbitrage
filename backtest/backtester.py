"""
Backtesting & Performance Metrics Engine.
"""
import numpy as np
import pandas as pd
from config import settings

class StatArbBacktester:
    def __init__(self, df, beta, initial_capital=settings.INITIAL_CAPITAL):
        self.df = df.copy()
        self.beta = beta
        self.initial_capital = initial_capital
        
    def run_backtest(self):
        capital = self.initial_capital
        position = 0
        trade_log = []
        equity_curve = [capital]
        
        qty_a = 0
        qty_b = 0
        entry_price_a = 0
        entry_price_b = 0
        entry_date = None
        
        for i in range(1, len(self.df)):
            date = self.df.index[i]
            price_a = self.df['Stock_A'].iloc[i]
            price_b = self.df['Stock_B'].iloc[i]
            signal = self.df['Signal'].iloc[i]
            z_score = self.df['Z_Score'].iloc[i]
            
            # Close existing position if signal is 0 (exit) or 99 (stop-loss)
            if position != 0 and (signal == 0 or signal == 99 or signal != position):
                # Calculate PnL
                if position == 1: # Long A, Short B
                    pnl_a = qty_a * (price_a - entry_price_a)
                    pnl_b = qty_b * (entry_price_b - price_b) # Short gain if price fell
                else: # Short A, Long B
                    pnl_a = qty_a * (entry_price_a - price_a)
                    pnl_b = qty_b * (price_b - entry_price_b)
                    
                gross_pnl = pnl_a + pnl_b
                fees = (qty_a * price_a + qty_b * price_b) * settings.TRANSACTION_FEE
                net_pnl = gross_pnl - fees
                
                capital += net_pnl
                
                reason = "Stop Loss" if signal == 99 else "Mean Reversion Exit"
                trade_log.append({
                    'Entry Date/Time': entry_date,
                    'Exit Date/Time': date,
                    'Type': 'BUY_A_SELL_B' if position == 1 else 'SELL_A_BUY_B',
                    'Price A Entry': round(entry_price_a, 2),
                    'Price A Exit': round(price_a, 2),
                    'Price B Entry': round(entry_price_b, 2),
                    'Price B Exit': round(price_b, 2),
                    'Net PnL ($)': round(net_pnl, 2),
                    'Reason': reason
                })
                
                position = 0
                qty_a = 0
                qty_b = 0
                entry_date = None

            # Open new position if signal is 1 or -1 and flat
            if position == 0 and signal in [1, -1]:
                position = signal
                target_capital = capital * 0.4 # allocate 40% capital to Stock A
                
                qty_a = target_capital / price_a
                qty_b = (target_capital / price_a) * self.beta
                
                entry_price_a = price_a
                entry_price_b = price_b
                entry_date = date
                
            equity_curve.append(capital)
            
        self.df['Equity'] = equity_curve
        metrics = self._compute_metrics(trade_log, equity_curve)
        return metrics, pd.DataFrame(trade_log), self.df

    def _compute_metrics(self, trade_log, equity_curve):
        equity_series = pd.Series(equity_curve)
        net_profit = equity_series.iloc[-1] - self.initial_capital
        roi = (net_profit / self.initial_capital) * 100.0
        
        # Calculate daily returns for Sharpe Ratio
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() != 0 else 0.0
        
        # Calculate Maximum Drawdown
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        max_drawdown = drawdown.min() * 100.0 # Percentage
        
        trades_df = pd.DataFrame(trade_log)
        total_trades = len(trades_df)
        
        if total_trades > 0:
            win_trades = len(trades_df[trades_df['Net PnL ($)'] > 0])
            win_rate = (win_trades / total_trades) * 100.0
            
            gross_profits = trades_df[trades_df['Net PnL ($)'] > 0]['Net PnL ($)'].sum()
            gross_losses = abs(trades_df[trades_df['Net PnL ($)'] < 0]['Net PnL ($)'].sum())
            profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else np.nan
        else:
            win_rate = 0.0
            profit_factor = 0.0
            
        return {
            'Initial Capital ($)': self.initial_capital,
            'Final Capital ($)': equity_series.iloc[-1],
            'Net Profit ($)': net_profit,
            'ROI (%)': roi,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown (%)': max_drawdown,
            'Total Trades': total_trades,
            'Win Rate (%)': win_rate,
            'Profit Factor': profit_factor
        }

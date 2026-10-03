"""
Backtest Module Wrapper for WalkForwardBacktester.
Preserves backward compatibility while forwarding to the rigorous WalkForwardBacktester engine.
"""
from backtest.engine import WalkForwardBacktester

class StatArbBacktester(WalkForwardBacktester):
    def __init__(self, df, beta=None, initial_capital=1000.0):
        super().__init__(initial_capital=initial_capital)
        self.df = df
        
    def run_backtest(self):
        metrics, ledger, equity_df = self.run(self.df)
        return metrics, ledger, equity_df

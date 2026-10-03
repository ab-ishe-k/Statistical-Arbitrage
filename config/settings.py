"""
Configuration Settings for Statistical Arbitrage Engine
"""

# Statistical Model Parameters
ENTRY_Z_SCORE = 2.0        # Threshold for entering trade (+2.0 or -2.0)
EXIT_Z_SCORE = 0.2         # Threshold for mean reversion exit
STOP_LOSS_Z_SCORE = 3.5    # Threshold for statistical breakdown stop-loss

LOOKBACK_WINDOW = 20       # Rolling window for Z-Score mean and std dev
ADF_P_VALUE_THRESHOLD = 0.05 # P-value threshold for cointegration test

# Backtesting Parameters
INITIAL_CAPITAL = 1000.0   # Initial portfolio capital in USD
TRANSACTION_FEE = 0.001     # 0.1% per trade commission
SLIPPAGE = 0.0005           # 0.05% slippage simulation

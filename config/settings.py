"""
Quantitative Research & Trading Engine Configuration.
Centralized configuration for strategy, statistical models, backtesting, portfolio accounting, and risk management.
"""

# Capital & Allocation
INITIAL_CAPITAL: float = 10000.0        # Portfolio initial equity USD
PAIR_ALLOCATION_PCT: float = 0.40       # Allocate 40% of equity per pair trade
MAX_GROSS_EXPOSURE_PCT: float = 1.0     # Maximum gross exposure cap (100% of equity)
MAX_LEVERAGE: float = 1.0               # Maximum portfolio leverage cap

# Statistical & Model Estimation (Walk-Forward)
TRAINING_WINDOW: int = 120              # In-sample historical bars to estimate Beta and Cointegration
REFIT_FREQUENCY: int = 20               # Bars between dynamic Hedge Ratio (Beta) re-estimation
ADF_P_VALUE_THRESHOLD: float = 0.05     # p-value cutoff for ADF cointegration test

# Signal Thresholds (Rolling Z-Score)
LOOKBACK_WINDOW: int = 20               # Rolling window for spread mean and std dev calculation
ENTRY_Z_SCORE: float = 2.0              # Entry threshold (|Z| >= 2.0)
EXIT_Z_SCORE: float = 0.2               # Mean-reversion exit threshold (|Z| <= 0.2)
STOP_LOSS_Z_SCORE: float = 3.5          # Statistical breakdown stop-loss threshold (|Z| >= 3.5)

# Execution Simulation & Transaction Frictions
EXECUTION_DELAY_BARS: int = 1           # Execution delay: signal at bar t executes on bar t+1
BID_ASK_SPREAD_PCT: float = 0.0005      # 0.05% bid-ask spread cost
COMMISSION_PCT: float = 0.0010          # 0.10% commission fee per leg side
SLIPPAGE_PCT: float = 0.0005            # 0.05% slippage cost per trade

# Risk Limits & Stop Mechanics
MAX_DAILY_DRAWDOWN_PCT: float = 0.05    # 5% max daily drawdown halt
MAX_TOTAL_DRAWDOWN_PCT: float = 0.15   # 15% max portfolio total drawdown halt
MIN_HISTORY_REQUIRED: int = 60          # Minimum price bars required before trading

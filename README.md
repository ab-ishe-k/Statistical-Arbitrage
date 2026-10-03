# Statistical Arbitrage Research Engine 📈

> **A Quant-Grade Walk-Forward Market-Neutral Pairs Trading Engine in Python**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Tests: PyTest](https://img.shields.io/badge/tests-14%20passed-brightgreen.svg)](https://docs.pytest.org/)

A research-grade quantitative trading backtesting engine built to discover, fit, backtest, and evaluate **Statistical Arbitrage** (Pairs Trading) strategies over equities and cryptocurrencies with zero look-ahead bias and event-driven market simulation.

---

## 🌟 Quantitative Architectural Rigor

- **Walk-Forward In-Sample Estimation**: Hedge Ratios ($\beta$) and Engle-Granger ADF cointegration statistics are refitted dynamically using rolling in-sample historical training windows ($W_{\text{train}} = 120$ bars).
- **Zero Look-Ahead Data Leakage**: Rolling mean ($\mu$) and rolling standard deviation ($\sigma$) parameters for Z-score normalization are calculated strictly over past historical observations $[t-W, t-1]$ using explicit 1-bar shifts.
- **Event-Driven Execution Simulator**: Next-bar execution delay ($t+1$) models realistic market latency. Orders are filled with bid-ask spread costs ($0.05\%$), slippage ($0.05\%$), and brokerage commissions ($0.10\%$).
- **Mark-to-Market Portfolio Accounting**: Bar-by-bar portfolio tracking incorporating cash, long/short positions, unrealized PnL, realized PnL, gross exposure, and net exposure.
- **Dollar-Neutral Position Sizing**: Leg quantities strictly obey the Hedge Ratio $\beta$ ($\text{Qty}_B = \beta \times \text{Qty}_A$) to neutralize directional market beta risk.
- **Ornstein-Uhlenbeck Half-Life Computation**: Estimates the mean-reversion speed ($\text{Half-Life} = -\frac{\ln 2}{\lambda}$) via an AR(1) continuous process.
- **Comprehensive Unit & Regression Test Suite**: Automated PyTest suite containing 14 unit tests, including a no-lookahead regression test proving future price mutations do not change past signals or executions.

---

## 📐 Mathematical Methodology

### 1. Dynamic Hedge Ratio (OLS Linear Regression)
$$\text{Price A}_t = \alpha_{\text{past}} + \beta_{\text{past}} \times \text{Price B}_t + \epsilon_t$$

### 2. Residual Spread & No-Leakage Z-Score
$$\text{Spread}_t = \text{Price A}_t - \beta_{\text{past}} \times \text{Price B}_t - \alpha_{\text{past}}$$
$$\text{Z-score}_t = \frac{\text{Spread}_t - \mu_{\text{past}}}{\sigma_{\text{past}}}$$
*where $\mu_{\text{past}}$ and $\sigma_{\text{past}}$ are calculated over past historical bars $[t-W, t-1]$.*

### 3. Half-Life of Mean Reversion (AR(1) Process)
$$\Delta \text{Spread}_t = \lambda \times \text{Spread}_{t-1} + \mu + \epsilon_t \implies \text{Half-Life} = -\frac{\ln 2}{\lambda}$$

---

## 📂 Project Architecture

```text
stat_arb_engine/
├── config/
│   └── settings.py           # Centralized strategy parameters (Z-thresholds, fees, initial capital)
├── data/
│   ├── validation.py         # Data validation, cleaning, and timestamp synchronization
│   ├── generator.py          # Seedable synthetic cointegrated time-series generator
│   └── real_data.py          # Real market Yahoo Finance fetcher module
├── strategy/
│   ├── cointegration.py      # OLS Beta, ADF test, and Ornstein-Uhlenbeck Half-Life
│   └── signal_engine.py      # Spread calculation, zero-leakage Z-score, and signal state machine
├── execution/
│   └── simulator.py          # Next-bar execution simulator with bid-ask spread, slippage, and commissions
├── portfolio/
│   └── accounting.py         # Full mark-to-market portfolio tracker (Cash, Positions, PnL, Exposure)
├── risk/
│   └── manager.py            # Dollar-neutral position sizer and drawdown kill-switch
├── backtest/
│   ├── engine.py             # Event-driven Walk-Forward Backtester
│   └── backtester.py         # Backward-compatible wrapper
├── analytics/
│   ├── metrics.py            # Risk-adjusted performance metrics calculator (Sharpe, Sortino, Calmar)
│   └── robustness.py         # Parameter sensitivity grid search and stability analysis
├── monitoring/
│   └── app.py                # Streamlit visual dashboard interface
├── tests/
│   ├── test_data.py          # Data validation unit tests
│   ├── test_hedge_ratio.py   # OLS Beta and cointegration unit tests
│   ├── test_signals.py       # Signal engine state machine unit tests
│   ├── test_no_lookahead.py  # No-lookahead bias regression test
│   ├── test_execution.py     # Execution simulator unit tests
│   ├── test_portfolio.py     # Mark-to-market accounting unit tests
│   ├── test_risk.py          # Risk manager unit tests
│   └── test_backtest.py      # Walk-forward integration unit tests
├── main.py                   # Master entry-point runner script
├── PROJECT_DOCUMENTATION.md  # Detailed quantitative research report & Interview Q&A
└── requirements.txt          # Python project dependencies
```

---

## 🧪 Testing & Verification

Run the automated test suite with PyTest:
```bash
python -m pytest
```

Output:
```text
tests\test_backtest.py .                                                 [  7%]
tests\test_data.py ....                                                  [ 35%]
tests\test_execution.py .                                                [ 42%]
tests\test_hedge_ratio.py ...                                            [ 64%]
tests\test_no_lookahead.py .                                             [ 71%]
tests\test_portfolio.py .                                                [ 78%]
tests\test_risk.py ..                                                    [ 92%]
tests\test_signals.py .                                                  [100%]
============================= 14 passed in 7.37s ==============================
```

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/ab-ishe-k/Statistical-Arbitrage.git
cd Statistical-Arbitrage
pip install -r requirements.txt
```

### 2. Run Terminal Walk-Forward Pipeline
Execute the master runner script:
```bash
python main.py
```

### 3. Launch Streamlit Web Dashboard
Start the web dashboard interface:
```bash
python -m streamlit run monitoring/app.py
```

---

## 📊 Verified Walk-Forward Performance Report

*Results generated under event-driven walk-forward execution ($W_{\text{train}}=120$, $W_{\text{refit}}=20$), 0.10% commission, 0.05% bid-ask spread, 0.05% slippage, and 1-bar execution delay over 500 daily price bars:*

```text
======================================================================
           HONEST WALK-FORWARD PERFORMANCE REPORT
======================================================================
  Initial Capital ($)             : 10,000.00
  Final Capital ($)               : 10,170.18
  Net Profit ($)                  : 170.18
  ROI (%)                         : 1.70
  CAGR (%)                        : 0.85
  Sharpe Ratio                    : 0.22
  Sortino Ratio                   : 0.27
  Calmar Ratio                    : 0.21
  Max Drawdown (%)                : -3.98
  Max Drawdown Duration (bars)    : 128
  Total Trades                    : 17
  Win Rate (%)                    : 70.59
  Gross Profit ($)                : 1,083.09
  Gross Loss ($)                  : 445.92
  Profit Factor                   : 2.43
  Average Win ($)                 : 90.26
  Average Loss ($)                : 89.18
  Win/Loss Ratio                  : 1.01
  Expectancy ($)                  : 37.48
  Average Holding Period (bars)   : 13.65
  Total Commissions ($)           : 249.82
  Total Slippage ($)              : 187.37
======================================================================
```

---

## 📜 Educational Disclaimer

This software is developed strictly for quantitative research, academic evaluation, and paper-trading simulation purposes. It does not constitute financial advice or claim guaranteed trading profits.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

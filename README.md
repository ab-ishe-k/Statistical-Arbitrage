# Statistical Arbitrage Engine 📈

> **An Automated Quantitative Market-Neutral Pairs Trading Platform in Python**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)

A production-grade, modular quantitative trading engine designed to discover, backtest, and execute market-neutral **Statistical Arbitrage** (Pairs Trading) strategies over equities and cryptocurrencies.

---

## 🌟 Key Features

- **Statistical Cointegration Testing**: Implements the Engle-Granger two-step method using Augmented Dickey-Fuller (ADF) stationarity testing ($p < 0.05$).
- **Dynamic Hedge Ratio Calculation**: Derives optimal $\beta$ ratios via Ordinary Least Squares (OLS) linear regression.
- **Z-Score Signal Generation**: Normalizes residual spread dynamics using rolling mean and standard deviation to trigger quantitative Entry ($\pm 2.0$), Exit ($0.0$), and Stop-Loss ($\pm 3.5$) thresholds.
- **Market-Neutral Exposure**: Balances Long and Short legs to hedge broad market beta risk.
- **Real Market Data Ingestion**: Seamlessly fetches real-time and historical OHLCV data for US Equities, Indian Equities (NSE), and Cryptocurrencies via `yfinance`.
- **Interactive Visual Dashboard**: Feature-rich Streamlit web interface featuring real-time Plotly charts for price series, residual spreads, Z-scores, and equity curves.
- **Comprehensive Backtesting Suite**: Calculates institutional risk metrics including Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Win Rate, and Profit Factor with simulated slippage and commissions.

---

## 📐 Mathematical Formulation

### 1. Residual Spread
$$\text{Spread}_t = \text{Price A}_t - \beta \times \text{Price B}_t$$
*where $\beta$ is the OLS slope coefficient.*

### 2. Rolling Z-Score Standardization
$$\text{Z-score}_t = \frac{\text{Spread}_t - \mu_{\text{spread}}}{\sigma_{\text{spread}}}$$
*where $\mu$ is rolling mean spread and $\sigma$ is rolling standard deviation.*

---

## 🏗 System Architecture

```
Market Data Sources (YFinance / Exchange APIs)
       │
       ▼
Data Cleaning & Synchronization Engine
       │
       ▼
Cointegration & OLS Beta Calculation Module
       │
       ▼
Rolling Z-Score Signal Generation Engine
       │
       ▼
Portfolio Position Sizer & Dollar-Neutral Allocator
       │
       ▼
Risk Management & Automated Stop-Loss Verification
       │
       ▼
Tick/Bar-by-Bar Backtesting & Streamlit Visual Dashboard
```

---

## 📂 Project Structure

```text
stat_arb_engine/
├── config/
│   └── settings.py           # Strategy parameters (Z-thresholds, fees, initial capital)
├── data/
│   ├── generator.py          # Synthetic cointegrated price series generator
│   └── real_data.py          # Real market Yahoo Finance fetcher module
├── strategy/
│   ├── cointegration.py      # OLS Beta and ADF stationarity test
│   └── signal_engine.py      # Residual spread, Z-score, trading signals
├── backtest/
│   └── backtester.py         # Performance simulation & Sharpe/Drawdown engine
├── monitoring/
│   └── app.py                # Streamlit UI dashboard interface
├── main.py                   # Master entry-point runner script
├── PROJECT_DOCUMENTATION.md  # Detailed project report & Viva Q&A
└── requirements.txt          # Python project dependencies
```

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/statistical-arbitrage-engine.git
cd statistical-arbitrage-engine
pip install -r requirements.txt
```

### 2. Run Terminal Backtest Pipeline
Execute the master runner script:
```bash
python main.py
```

### 3. Launch Interactive Streamlit Dashboard
Start the web dashboard interface:
```bash
python -m streamlit run monitoring/app.py
```

---

## 📊 Sample Performance Output

```text
=================================================================
                     PERFORMANCE REPORT
=================================================================
  Initial Capital ($)      : 1,000.00
  Final Capital ($)        : 1,130.68
  Net Profit ($)           : 130.68
  ROI (%)                  : 13.07 %
  Sharpe Ratio             : 2.59
  Max Drawdown (%)         : -0.39 %
  Total Trades             : 18
  Win Rate (%)             : 94.44 %
  Profit Factor            : 30.77
=================================================================
```

---

## 📜 Educational Disclaimer

This software is developed strictly for educational, research, and paper-trading simulation purposes. It does not constitute financial advice or guarantee trading profits.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

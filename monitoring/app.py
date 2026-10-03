import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import settings
from data.generator import generate_cointegrated_pairs
from data.real_data import fetch_real_pairs
from strategy.cointegration import run_engle_granger_test
from backtest.engine import WalkForwardBacktester
from analytics.robustness import run_parameter_sensitivity

st.set_page_config(page_title="Statistical Arbitrage Research Engine", layout="wide")

st.title("📈 Statistical Arbitrage Research Engine")
st.markdown("Quant-Grade Walk-Forward Event-Driven Backtester with Zero Look-Ahead Bias & Transaction Friction Simulation")

# Sidebar Configuration
st.sidebar.header("1. Data Source & Universe Selection")
data_mode = st.sidebar.selectbox(
    "Data Source Mode",
    ["Synthetic Data Simulation", "Real Market Data (YFinance)"]
)

if data_mode == "Synthetic Data Simulation":
    symbol_a_name = "Stock A"
    symbol_b_name = "Stock B"
else:
    preset_pair = st.sidebar.selectbox(
        "Select Real Market Asset Pair",
        [
            "US Stocks: Coca-Cola (KO) vs PepsiCo (PEP)",
            "US Tech: Visa (V) vs Mastercard (MA)",
            "Indian Banking: HDFC Bank vs ICICI Bank",
            "Crypto: Ethereum (ETH-USD) vs Bitcoin (BTC-USD)",
            "Custom Tickers"
        ]
    )
    
    if preset_pair == "US Stocks: Coca-Cola (KO) vs PepsiCo (PEP)":
        symbol_a_name, symbol_b_name = "KO", "PEP"
    elif preset_pair == "US Tech: Visa (V) vs Mastercard (MA)":
        symbol_a_name, symbol_b_name = "V", "MA"
    elif preset_pair == "Indian Banking: HDFC Bank vs ICICI Bank":
        symbol_a_name, symbol_b_name = "HDFCBANK.NS", "ICICIBANK.NS"
    elif preset_pair == "Crypto: Ethereum (ETH-USD) vs Bitcoin (BTC-USD)":
        symbol_a_name, symbol_b_name = "ETH-USD", "BTC-USD"
    else:
        symbol_a_name = st.sidebar.text_input("Ticker A", "KO")
        symbol_b_name = st.sidebar.text_input("Ticker B", "PEP")

st.sidebar.header("2. Capital & Frictions")
initial_capital = st.sidebar.number_input("Initial Portfolio Equity ($)", min_value=100.0, max_value=100000.0, value=10000.0, step=500.0)
commission_pct = st.sidebar.slider("Commission Fee (%)", 0.0, 0.5, 0.10, 0.01) / 100.0
slippage_pct = st.sidebar.slider("Slippage Cost (%)", 0.0, 0.5, 0.05, 0.01) / 100.0

st.sidebar.header("3. Walk-Forward & Strategy Parameters")
training_window = st.sidebar.slider("In-Sample Training Window (bars)", 60, 250, 120)
lookback = st.sidebar.slider("Rolling Z-Score Lookback Window", 10, 50, 20)
entry_z = st.sidebar.slider("Entry Z-Score Threshold", 1.5, 3.0, 2.0, 0.1)
stop_z = st.sidebar.slider("Stop-Loss Z-Score Threshold", 3.0, 5.0, 3.5, 0.1)

# Generate & Run
if st.sidebar.button("🚀 Run Walk-Forward Research Engine"):
    with st.spinner("Fetching market data and running event-driven backtest..."):
        if data_mode == "Synthetic Data Simulation":
            df = generate_cointegrated_pairs(n_bars=500, beta=1.2, seed=42)
        else:
            df = fetch_real_pairs(symbol_a=symbol_a_name, symbol_b=symbol_b_name, period="2y")

        if df.empty or len(df) < training_window + 10:
            st.error("Error: Not enough data points returned for the selected training window.")
            st.stop()
            
        coint_res = run_engle_granger_test(df['Stock_A'], df['Stock_B'])
        
        status_msg = "PASSED (p < 0.05)" if coint_res['is_cointegrated'] else "FAILED (p >= 0.05)"
        st.info(f"Asset Pair: **{symbol_a_name}** vs **{symbol_b_name}** | Full Sample Cointegration Status: **{status_msg}** | OLS Beta (Ref): **{coint_res['beta']:.4f}** | Half-Life: **{coint_res['half_life_bars']:.1f} bars** | p-value: **{coint_res['p_value']:.5f}**")
        
        backtester = WalkForwardBacktester(
            initial_capital=initial_capital,
            training_window=training_window,
            lookback_window=lookback,
            entry_z=entry_z,
            exit_z=0.2,
            stop_z=stop_z,
            commission_pct=commission_pct,
            slippage_pct=slippage_pct
        )
        
        metrics, trade_log, df_results = backtester.run(df)
        
        # Key Performance Indicator Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Net Profit", f"${metrics['Net Profit ($)']:,.2f}", f"ROI: {metrics['ROI (%)']:.2f}%")
        col2.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}", f"Sortino: {metrics['Sortino Ratio']:.2f}")
        col3.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']:.2f}%", f"{metrics['Max Drawdown Duration (bars)']} bars")
        col4.metric("Win Rate", f"{metrics['Win Rate (%)']:.1f}%", f"Trades: {metrics['Total Trades']}")
        col5.metric("Profit Factor", f"{metrics['Profit Factor']:.2f}", f"Expectancy: ${metrics['Expectancy ($)']:.2f}")
        
        # Plotly Charts
        fig = make_subplots(
            rows=4, cols=1, shared_xaxes=True, 
            subplot_titles=(
                f'Prices: {symbol_a_name} vs {symbol_b_name}',
                'Walk-Forward Rolling Spread & Z-Score',
                'Mark-to-Market Portfolio Equity ($)',
                'Gross Exposure ($) & Friction Breakdown'
            ),
            vertical_spacing=0.06
        )
        
        # Stock Prices
        fig.add_trace(go.Scatter(x=df_results.index, y=df_results['Stock_A'], name=symbol_a_name), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_results.index, y=df_results['Stock_B'], name=symbol_b_name), row=1, col=1)
        
        # Z-Score
        fig.add_trace(go.Scatter(x=df_results.index, y=df_results['Z_Score'], name='Z-Score', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=entry_z, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=-entry_z, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=0, line_dash="solid", line_color="gray", row=2, col=1)
        
        # Equity Curve
        fig.add_trace(go.Scatter(x=df_results.index, y=df_results['Equity'], name='Equity ($)', line=dict(color='green')), row=3, col=1)
        
        # Exposure
        fig.add_trace(go.Scatter(x=df_results.index, y=df_results['Gross_Exposure'], name='Gross Exposure ($)', line=dict(color='orange')), row=4, col=1)
        
        fig.update_layout(height=1000, title_text=f"Quantitative Walk-Forward Research Engine Results ({symbol_a_name} / {symbol_b_name})")
        st.plotly_chart(fig, use_container_width=True)
        
        # Frictions Breakdown
        f_col1, f_col2, f_col3 = st.columns(3)
        f_col1.metric("Gross Profit", f"${metrics['Gross Profit ($)']:,.2f}")
        f_col2.metric("Total Commissions Paid", f"${metrics['Total Commissions ($)']:,.2f}")
        f_col3.metric("Total Slippage & Spread Cost", f"${metrics['Total Slippage ($)']:,.2f}")
        
        # Trade Log Table
        st.subheader("📋 Executed Trade Audit Ledger")
        st.dataframe(trade_log, use_container_width=True)
        
        # Robustness Analysis Tab
        st.subheader("⚙️ Parameter Sensitivity Matrix")
        with st.spinner("Running parameter grid search..."):
            sens_df = run_parameter_sensitivity(df, initial_capital=initial_capital)
            st.dataframe(sens_df, use_container_width=True)

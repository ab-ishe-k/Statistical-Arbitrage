"""
Streamlit Web Dashboard for Statistical Arbitrage Engine
Supports both Synthetic Simulation Data and Real Market Data (YFinance).
Run with: python -m streamlit run monitoring/app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data.generator import generate_cointegrated_pairs
from data.real_data import fetch_real_pairs
from strategy.cointegration import test_cointegration
from strategy.signal_engine import generate_signals
from backtest.backtester import StatArbBacktester

st.set_page_config(page_title="Statistical Arbitrage Engine", layout="wide")

st.title("📈 Statistical Arbitrage Engine - Interactive Dashboard")
st.markdown("Automated Quantitative Market-Neutral Pairs Trading Platform")

# Sidebar Configuration
st.sidebar.header("Data Source & Pair Selection")
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

st.sidebar.header("Strategy & Capital Settings")
initial_capital = st.sidebar.number_input("Initial Portfolio Capital ($)", min_value=100.0, max_value=100000.0, value=1000.0, step=100.0)
lookback = st.sidebar.slider("Z-Score Lookback Window", 10, 50, 20)
entry_z = st.sidebar.slider("Entry Z-Score Threshold", 1.5, 3.0, 2.0, 0.1)
stop_z = st.sidebar.slider("Stop-Loss Z-Score Threshold", 3.0, 5.0, 3.5, 0.1)

# Generate & Run
if st.sidebar.button("🚀 Run Backtest Simulation"):
    with st.spinner("Fetching data and calculating statistical models..."):
        if data_mode == "Synthetic Data Simulation":
            df = generate_cointegrated_pairs(n_bars=500, beta=1.2, seed=42)
        else:
            df = fetch_real_pairs(symbol_a=symbol_a_name, symbol_b=symbol_b_name, period="1y")

        if df.empty or len(df) < 30:
            st.error("Error: Not enough data points returned for the selected asset pair.")
            st.stop()
            
        p_val, beta, is_coint = test_cointegration(df['Stock_A'], df['Stock_B'])
        
        status_msg = "PASSED (p < 0.05)" if is_coint else "FAILED (p >= 0.05)"
        st.info(f"Asset Pair: **{symbol_a_name}** vs **{symbol_b_name}** | Cointegration Status: **{status_msg}** | Hedge Ratio ($\beta$): **{beta:.4f}** | p-value: **{p_val:.5f}**")
        
        df_signals = generate_signals(df, beta)
        backtester = StatArbBacktester(df_signals, beta, initial_capital=initial_capital)
        metrics, trade_log, df_results = backtester.run_backtest()
        
        # Key Performance Indicator Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Net Profit", f"${metrics['Net Profit ($)']:,.2f}")
        col2.metric("ROI", f"{metrics['ROI (%)']:.2f}%")
        col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
        col4.metric("Max Drawdown", f"{metrics['Max Drawdown (%)']:.2f}%")
        col5.metric("Win Rate", f"{metrics['Win Rate (%)']:.1f}%")
        
        # Plotly Charts
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            subplot_titles=(f'Prices: {symbol_a_name} vs {symbol_b_name}', 'Residual Spread & Z-Score', 'Portfolio Equity Curve ($)'))
        
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
        
        fig.update_layout(height=850, title_text=f"Quantitative Performance Analysis for {symbol_a_name} / {symbol_b_name}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Trade Log
        st.subheader("Executed Trade Log")
        st.dataframe(trade_log)

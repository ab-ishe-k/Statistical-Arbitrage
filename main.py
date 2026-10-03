"""
Statistical Arbitrage Engine - Main Runner Script
"""
import sys
import pandas as pd
from data.generator import generate_cointegrated_pairs
from strategy.cointegration import test_cointegration
from strategy.signal_engine import generate_signals
from backtest.backtester import StatArbBacktester

def main():
    print("=" * 65)
    print("      STATISTICAL ARBITRAGE ENGINE - DEMO PIPELINE")
    print("=" * 65)
    
    # 1. Generate Synthetic Cointegrated Market Data
    print("\n[Step 1] Fetching & Generating Market Data for Stock A & Stock B...")
    df = generate_cointegrated_pairs(n_bars=500, beta=1.2, noise_std=1.5, seed=42)
    print(f"-> Generated {len(df)} bars of historical daily price data.")
    print(df.head())
    
    # 2. Run Cointegration Test & Calculate Hedge Ratio
    print("\n[Step 2] Testing Cointegration & Calculating Hedge Ratio (Beta)...")
    p_value, beta, is_cointegrated = test_cointegration(df['Stock_A'], df['Stock_B'])
    
    print(f"-> Calculated Hedge Ratio (Beta): {beta:.4f}")
    print(f"-> Engle-Granger ADF Test p-value: {p_value:.5f}")
    print(f"-> Cointegrated Status: {'PASSED (p < 0.05)' if is_cointegrated else 'FAILED'}")
    
    if not is_cointegrated:
        print("[Warning] Pair is not cointegrated! Strategy will not run.")
        sys.exit(0)
        
    # 3. Generate Spread & Z-Score Trading Signals
    print("\n[Step 3] Computing Spread, Rolling Z-Score & Signals...")
    df_signals = generate_signals(df, beta)
    
    active_signals = df_signals[df_signals['Signal'].isin([1, -1, 99])]
    print(f"-> Total Signals Generated: {len(active_signals)}")
    print(df_signals[['Stock_A', 'Stock_B', 'Spread', 'Z_Score', 'Signal']].tail(10))
    
    # 4. Run Backtest Simulation
    print("\n[Step 4] Running Backtest Simulation...")
    backtester = StatArbBacktester(df_signals, beta)
    metrics, trade_log, _ = backtester.run_backtest()
    
    # 5. Display Performance Report
    print("\n" + "=" * 65)
    print("                     PERFORMANCE REPORT")
    print("=" * 65)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key:<25}: {value:,.2f}")
        else:
            print(f"  {key:<25}: {value}")
    print("=" * 65)
    
    if not trade_log.empty:
        print("\n[Trade Executions Sample]")
        print(trade_log.head(10).to_string(index=False))
        
    print("\n[SUCCESS] Statistical Arbitrage Pipeline execution completed successfully!")

if __name__ == '__main__':
    main()

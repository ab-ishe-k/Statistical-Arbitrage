"""
Statistical Arbitrage Engine - Main Runner Script
Executes Walk-Forward Backtest Simulation with No Look-Ahead Data Leakage.
"""
import sys
import pandas as pd
from config import settings
from data.generator import generate_cointegrated_pairs
from data.real_data import fetch_real_pairs
from strategy.cointegration import run_engle_granger_test
from backtest.engine import WalkForwardBacktester

def main():
    print("=" * 70)
    print("   STATISTICAL ARBITRAGE RESEARCH ENGINE - WALK-FORWARD BACKTEST")
    print("=" * 70)
    
    # 1. Load Data
    print("\n[Step 1] Ingesting Market Data...")
    use_real_data = False  # Set to True to run on real market data (KO / PEP)
    
    if use_real_data:
        print("-> Ingesting Real Market Data (Coca-Cola KO vs PepsiCo PEP)...")
        df = fetch_real_pairs(symbol_a="KO", symbol_b="PEP", period="2y")
    else:
        print("-> Generating Deterministic Synthetic Cointegrated Market Data...")
        df = generate_cointegrated_pairs(n_bars=500, beta=1.2, seed=42)
        
    print(f"-> Ingested {len(df)} price bars. Range: {df.index[0].date()} to {df.index[-1].date()}")
    print(df.head())
    
    # 2. Run Cointegration & Half-Life Diagnostics over initial sample
    print("\n[Step 2] Full Dataset Cointegration Diagnostics (Reference Only)...")
    coint_diag = run_engle_granger_test(df['Stock_A'], df['Stock_B'])
    print(f"-> Full Dataset OLS Beta (Ref): {coint_diag['beta']:.4f}")
    print(f"-> ADF Test p-value: {coint_diag['p_value']:.5f}")
    print(f"-> Half-Life of Mean Reversion: {coint_diag['half_life_bars']:.1f} bars")
    print(f"-> Cointegration Status: {'PASSED (p < 0.05)' if coint_diag['is_cointegrated'] else 'FAILED'}")
    
    # 3. Initialize Walk-Forward Backtester (Strict Zero Look-Ahead)
    print("\n[Step 3] Executing Walk-Forward Event-Driven Backtest...")
    print(f"   - Training Window: {settings.TRAINING_WINDOW} bars")
    print(f"   - Refit Frequency: Every {settings.REFIT_FREQUENCY} bars")
    print(f"   - Lookback Window: {settings.LOOKBACK_WINDOW} bars (Shifted for zero leakage)")
    print(f"   - Execution Delay: {settings.EXECUTION_DELAY_BARS} bar (Signal at t -> Execute at t+1)")
    print(f"   - Transaction Cost: {settings.COMMISSION_PCT*100:.2f}% Commission, {settings.BID_ASK_SPREAD_PCT*100:.2f}% Spread, {settings.SLIPPAGE_PCT*100:.2f}% Slippage")
    
    backtester = WalkForwardBacktester(
        initial_capital=settings.INITIAL_CAPITAL,
        training_window=settings.TRAINING_WINDOW,
        refit_frequency=settings.REFIT_FREQUENCY,
        lookback_window=settings.LOOKBACK_WINDOW,
        entry_z=settings.ENTRY_Z_SCORE,
        exit_z=settings.EXIT_Z_SCORE,
        stop_z=settings.STOP_LOSS_Z_SCORE,
        commission_pct=settings.COMMISSION_PCT,
        bid_ask_spread_pct=settings.BID_ASK_SPREAD_PCT,
        slippage_pct=settings.SLIPPAGE_PCT,
        pair_allocation_pct=settings.PAIR_ALLOCATION_PCT,
        max_gross_exposure_pct=settings.MAX_GROSS_EXPOSURE_PCT,
        max_drawdown_pct=settings.MAX_TOTAL_DRAWDOWN_PCT
    )
    
    metrics, ledger_df, equity_df = backtester.run(df)
    
    # 4. Display Honest Performance Report
    print("\n" + "=" * 70)
    print("           HONEST WALK-FORWARD PERFORMANCE REPORT")
    print("=" * 70)
    for key, val in metrics.items():
        if isinstance(val, float):
            print(f"  {key:<32}: {val:,.2f}")
        else:
            print(f"  {key:<32}: {val}")
    print("=" * 70)
    
    if not ledger_df.empty:
        print("\n[Executed Trade Ledger Sample (First 5 Trades)]")
        print(ledger_df.head(5).to_string(index=False))
    else:
        print("\n[Trade Ledger] No trades executed under walk-forward rules.")
        
    print("\n[SUCCESS] Quantitative Walk-Forward Research Pipeline Completed.")

if __name__ == '__main__':
    main()

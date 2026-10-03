"""
Real Market Data Fetcher Module using yfinance
Fetches real stock market OHLCV price series for pair analysis.
"""
import pandas as pd
import yfinance as yf

def fetch_real_pairs(symbol_a="RELIANCE.NS", symbol_b="TCS.NS", period="1y", interval="1d"):
    """
    Fetches real price data from Yahoo Finance for two Indian/US stocks.
    Example: RELIANCE.NS & TCS.NS, or KO (Coca-Cola) & PEP (Pepsi).
    """
    print(f"[Real Data] Fetching real market data for {symbol_a} and {symbol_b}...")
    
    ticker_a = yf.Ticker(symbol_a)
    ticker_b = yf.Ticker(symbol_b)
    
    data_a = ticker_a.history(period=period, interval=interval)['Close']
    data_b = ticker_b.history(period=period, interval=interval)['Close']
    
    df = pd.DataFrame({
        'Stock_A': data_a,
        'Stock_B': data_b
    }).dropna()
    
    return df

def fetch_crypto_pairs(symbol_a="ETH-USD", symbol_b="BTC-USD", period="60d", interval="1h"):
    """
    Fetches real crypto price data (e.g. ETH & BTC).
    """
    df_a = yf.Ticker(symbol_a).history(period=period, interval=interval)['Close']
    df_b = yf.Ticker(symbol_b).history(period=period, interval=interval)['Close']
    
    df = pd.DataFrame({
        'Stock_A': df_a,
        'Stock_B': df_b
    }).dropna()
    
    return df

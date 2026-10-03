"""
Real Market Data Fetcher Module using yfinance.
Fetches real asset price series for equities and cryptocurrencies.
"""
import pandas as pd
import yfinance as yf
from data.validation import validate_price_series

def fetch_real_pairs(symbol_a: str = "KO", symbol_b: str = "PEP", period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches real price data from Yahoo Finance for two assets.
    Returns cleaned, synchronized DataFrame with 'Stock_A' and 'Stock_B' columns.
    """
    try:
        ticker_a = yf.Ticker(symbol_a)
        ticker_b = yf.Ticker(symbol_b)
        
        data_a = ticker_a.history(period=period, interval=interval)['Close']
        data_b = ticker_b.history(period=period, interval=interval)['Close']
        
        # Remove timezone offset if present
        if hasattr(data_a.index, 'tz') and data_a.index.tz is not None:
            data_a.index = data_a.index.tz_localize(None)
        if hasattr(data_b.index, 'tz') and data_b.index.tz is not None:
            data_b.index = data_b.index.tz_localize(None)
            
        df = pd.DataFrame({
            'Stock_A': data_a,
            'Stock_B': data_b
        })
        
        return validate_price_series(df, min_bars=30)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch real price data for {symbol_a} / {symbol_b}: {e}")

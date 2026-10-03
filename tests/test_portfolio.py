"""
Unit Tests for Portfolio Accounting and Mark-to-Market Tracking.
"""
import pytest
import pandas as pd
from portfolio.accounting import PortfolioTracker
from execution.simulator import Fill

def test_portfolio_mark_to_market():
    port = PortfolioTracker(initial_capital=10000.0)
    
    # Fill BUY Stock_A 10 units @ $100
    fill = Fill(
        fill_id="F1", order_id="O1", fill_timestamp=pd.Timestamp.now(),
        symbol="Stock_A", side="BUY", quantity=10.0, fill_price=100.0,
        commission=1.0, slippage_cost=0.5, notional=1000.0
    )
    port.process_fill(fill)
    
    # Cash should be 10000 - 1000 - 1 = 8999
    assert port.cash == 8999.0
    
    # Mark-to-market at price $110
    mtm = port.get_mark_to_market(price_a=110.0, price_b=50.0)
    # Total equity = 8999 + 10 * 110 = 10099
    assert mtm['total_equity'] == 10099.0
    assert mtm['unrealized_pnl'] == 100.0

"""
Unit Tests for Execution Simulator and Transaction Friction Modeling.
"""
import pytest
import pandas as pd
from execution.simulator import ExecutionSimulator, Order, Fill

def test_execution_simulator_frictions():
    sim = ExecutionSimulator(commission_pct=0.001, bid_ask_spread_pct=0.0004, slippage_pct=0.0005)
    
    order_buy = Order(order_id="ORD01", timestamp=pd.Timestamp.now(), symbol="Stock_A", side="BUY", quantity=100.0)
    fill_buy = sim.execute_order(order_buy, fill_timestamp=pd.Timestamp.now(), base_price=100.0)
    
    # BUY fill price must be HIGHER than base price due to spread + slippage
    assert fill_buy.fill_price > 100.0
    assert fill_buy.commission > 0.0
    assert fill_buy.slippage_cost > 0.0
    
    order_sell = Order(order_id="ORD02", timestamp=pd.Timestamp.now(), symbol="Stock_A", side="SELL", quantity=100.0)
    fill_sell = sim.execute_order(order_sell, fill_timestamp=pd.Timestamp.now(), base_price=100.0)
    
    # SELL fill price must be LOWER than base price due to spread + slippage
    assert fill_sell.fill_price < 100.0

"""
Unit Tests for Risk Management Module.
"""
import pytest
from risk.manager import RiskManager

def test_risk_manager_position_sizing():
    rm = RiskManager(pair_allocation_pct=0.40)
    qty_a, qty_b = rm.calculate_position_sizes(equity=10000.0, price_a=100.0, price_b=50.0, beta=1.2, signal=1)
    
    # Target capital for Stock A = 4000 -> Qty A = 40
    assert qty_a == 40.0
    # Qty B = 1.2 * 40 = 48
    assert qty_b == 48.0

def test_risk_manager_kill_switch():
    rm = RiskManager(max_drawdown_pct=0.10)
    
    # Equity drops from 10,000 peak to 8,500 (15% drawdown > 10% max)
    approved = rm.check_risk_limits(current_equity=8500.0, peak_equity=10000.0, gross_exposure=5000.0)
    assert approved is False
    assert rm.kill_switch_active is True

"""
Risk Management Module.
Enforces pre-trade and post-trade risk controls: Max Exposure, Drawdown Limits, Position Sizing, and Kill Switch.
"""
import numpy as np
from typing import Tuple, Dict, Any

class RiskManager:
    def __init__(
        self,
        max_gross_exposure_pct: float = 1.0,
        max_drawdown_pct: float = 0.15,
        pair_allocation_pct: float = 0.40
    ):
        self.max_gross_exposure_pct = max_gross_exposure_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.pair_allocation_pct = pair_allocation_pct
        self.kill_switch_active = False
        
    def calculate_position_sizes(
        self,
        equity: float,
        price_a: float,
        price_b: float,
        beta: float,
        signal: int
    ) -> Tuple[float, float]:
        """
        Calculates market-neutral position quantities for Asset A and Asset B.
        Quantity_A = (Equity * Pair_Allocation_Pct) / Price_A
        Quantity_B = Beta * Quantity_A
        
        If signal is LONG_SPREAD (1):  BUY Stock A, SELL Stock B
        If signal is SHORT_SPREAD (-1): SELL Stock A, BUY Stock B
        """
        if signal == 0 or self.kill_switch_active or equity <= 0:
            return 0.0, 0.0
            
        target_capital_a = equity * self.pair_allocation_pct
        qty_a = target_capital_a / price_a
        qty_b = abs(beta) * qty_a
        
        if signal == 1:
            # Long A, Short B
            return qty_a, qty_b
        elif signal == -1:
            # Short A, Long B
            return qty_a, qty_b
            
        return 0.0, 0.0

    def check_risk_limits(self, current_equity: float, peak_equity: float, gross_exposure: float) -> bool:
        """
        Evaluates risk constraints. Returns True if order is approved, False if risk breached.
        """
        if self.kill_switch_active:
            return False
            
        # Drawdown check
        if peak_equity > 0:
            drawdown = (peak_equity - current_equity) / peak_equity
            if drawdown >= self.max_drawdown_pct:
                self.kill_switch_active = True
                return False
                
        # Gross exposure check
        if current_equity > 0:
            exposure_ratio = gross_exposure / current_equity
            if exposure_ratio > self.max_gross_exposure_pct * 1.05:  # 5% buffer
                return False
                
        return True

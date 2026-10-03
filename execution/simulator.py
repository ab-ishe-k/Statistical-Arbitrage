"""
Execution Simulator Module.
Emulates order routing, execution latency (next-bar execution), bid-ask spread, slippage, and brokerage commissions.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class Order:
    order_id: str
    timestamp: pd.Timestamp
    symbol: str
    side: str            # 'BUY' or 'SELL'
    quantity: float
    order_type: str = 'MARKET'

@dataclass
class Fill:
    fill_id: str
    order_id: str
    fill_timestamp: pd.Timestamp
    symbol: str
    side: str
    quantity: float
    fill_price: float
    commission: float
    slippage_cost: float
    notional: float

class ExecutionSimulator:
    def __init__(
        self,
        commission_pct: float = 0.0010,
        bid_ask_spread_pct: float = 0.0005,
        slippage_pct: float = 0.0005
    ):
        self.commission_pct = commission_pct
        self.bid_ask_spread_pct = bid_ask_spread_pct
        self.slippage_pct = slippage_pct
        self.fill_count = 0
        
    def execute_order(self, order: Order, fill_timestamp: pd.Timestamp, base_price: float) -> Fill:
        """
        Executes an order on the specified fill timestamp at base_price adjusted for
        bid-ask spread, slippage, and commission.
        
        For BUY:  Fill Price = base_price * (1 + half_spread + slippage)
        For SELL: Fill Price = base_price * (1 - half_spread - slippage)
        """
        self.fill_count += 1
        half_spread = self.bid_ask_spread_pct / 2.0
        
        if order.side.upper() == 'BUY':
            frictions = half_spread + self.slippage_pct
            fill_price = base_price * (1.0 + frictions)
        else:
            frictions = half_spread + self.slippage_pct
            fill_price = base_price * (1.0 - frictions)
            
        notional = fill_price * order.quantity
        commission = notional * self.commission_pct
        slippage_cost = abs(fill_price - base_price) * order.quantity
        
        return Fill(
            fill_id=f"FILL_{self.fill_count:06d}",
            order_id=order.order_id,
            fill_timestamp=fill_timestamp,
            symbol=order.symbol,
            side=order.side.upper(),
            quantity=order.quantity,
            fill_price=fill_price,
            commission=commission,
            slippage_cost=slippage_cost,
            notional=notional
        )

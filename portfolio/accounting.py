"""
Portfolio Accounting & Position Sizing Module.
Tracks Cash, Positions, Realized PnL, Unrealized PnL (Mark-to-Market), Gross/Net Exposure, and Total Equity.
"""
from dataclasses import dataclass
from typing import Dict, Any
from execution.simulator import Fill

@dataclass
class Position:
    symbol: str
    quantity: float      # Positive for Long, Negative for Short
    average_entry_price: float = 0.0

class PortfolioTracker:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position_a = Position(symbol="Stock_A", quantity=0.0, average_entry_price=0.0)
        self.position_b = Position(symbol="Stock_B", quantity=0.0, average_entry_price=0.0)
        
        self.realized_pnl = 0.0
        self.total_commissions = 0.0
        self.total_slippage = 0.0
        
    def process_fill(self, fill: Fill):
        """
        Updates cash, positions, realized PnL, and transaction fees upon execution of a Fill.
        """
        self.total_commissions += fill.commission
        self.total_slippage += fill.slippage_cost
        
        target_pos = self.position_a if fill.symbol == "Stock_A" else self.position_b
        
        qty_change = fill.quantity if fill.side == "BUY" else -fill.quantity
        cash_flow = - (qty_change * fill.fill_price) - fill.commission
        self.cash += cash_flow
        
        # Position logic
        if target_pos.quantity == 0.0:
            target_pos.quantity = qty_change
            target_pos.average_entry_price = fill.fill_price
        elif (target_pos.quantity > 0 and qty_change > 0) or (target_pos.quantity < 0 and qty_change < 0):
            # Adding to existing position
            new_qty = target_pos.quantity + qty_change
            target_pos.average_entry_price = (
                (target_pos.quantity * target_pos.average_entry_price) + (qty_change * fill.fill_price)
            ) / new_qty
            target_pos.quantity = new_qty
        else:
            # Closing or reversing position
            if abs(qty_change) >= abs(target_pos.quantity):
                # Full close
                closed_qty = target_pos.quantity
                trade_pnl = closed_qty * (fill.fill_price - target_pos.average_entry_price)
                self.realized_pnl += trade_pnl
                
                remaining_qty = target_pos.quantity + qty_change
                target_pos.quantity = remaining_qty
                target_pos.average_entry_price = fill.fill_price if remaining_qty != 0 else 0.0
            else:
                # Partial close
                trade_pnl = (-qty_change) * (fill.fill_price - target_pos.average_entry_price)
                self.realized_pnl += trade_pnl
                target_pos.quantity += qty_change

    def get_mark_to_market(self, price_a: float, price_b: float) -> Dict[str, float]:
        """
        Calculates bar-by-bar Mark-to-Market Total Equity, Unrealized PnL, and Gross/Net Exposure.
        """
        val_a = self.position_a.quantity * price_a
        val_b = self.position_b.quantity * price_b
        
        unrealized_pnl_a = (
            self.position_a.quantity * (price_a - self.position_a.average_entry_price)
            if self.position_a.quantity != 0 else 0.0
        )
        unrealized_pnl_b = (
            self.position_b.quantity * (price_b - self.position_b.average_entry_price)
            if self.position_b.quantity != 0 else 0.0
        )
        unrealized_pnl = unrealized_pnl_a + unrealized_pnl_b
        
        total_equity = self.cash + val_a + val_b
        gross_exposure = abs(val_a) + abs(val_b)
        net_exposure = val_a + val_b
        
        return {
            'cash': self.cash,
            'total_equity': total_equity,
            'unrealized_pnl': unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'gross_exposure': gross_exposure,
            'net_exposure': net_exposure,
            'total_commissions': self.total_commissions,
            'total_slippage': self.total_slippage,
            'qty_a': self.position_a.quantity,
            'qty_b': self.position_b.quantity,
            'entry_price_a': self.position_a.average_entry_price,
            'entry_price_b': self.position_b.average_entry_price
        }

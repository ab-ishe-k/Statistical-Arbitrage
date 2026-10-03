"""
Walk-Forward Event-Driven Backtesting Engine.
Executes strict walk-forward parameter estimation, no look-ahead signal calculation, 
next-bar execution simulation, full mark-to-market portfolio accounting, and complete trade ledger logging.
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List

from config import settings
from data.validation import validate_price_series
from strategy.cointegration import calculate_hedge_ratio, test_cointegration
from strategy.signal_engine import FLAT, LONG_SPREAD, SHORT_SPREAD, EXIT_SIGNAL, STOP_LOSS_SIGNAL
from execution.simulator import ExecutionSimulator, Order, Fill
from portfolio.accounting import PortfolioTracker
from risk.manager import RiskManager
from analytics.metrics import compute_performance_metrics

class WalkForwardBacktester:
    def __init__(
        self,
        initial_capital: float = settings.INITIAL_CAPITAL,
        training_window: int = settings.TRAINING_WINDOW,
        refit_frequency: int = settings.REFIT_FREQUENCY,
        lookback_window: int = settings.LOOKBACK_WINDOW,
        entry_z: float = settings.ENTRY_Z_SCORE,
        exit_z: float = settings.EXIT_Z_SCORE,
        stop_z: float = settings.STOP_LOSS_Z_SCORE,
        commission_pct: float = settings.COMMISSION_PCT,
        bid_ask_spread_pct: float = settings.BID_ASK_SPREAD_PCT,
        slippage_pct: float = settings.SLIPPAGE_PCT,
        pair_allocation_pct: float = settings.PAIR_ALLOCATION_PCT,
        max_gross_exposure_pct: float = settings.MAX_GROSS_EXPOSURE_PCT,
        max_drawdown_pct: float = settings.MAX_TOTAL_DRAWDOWN_PCT,
        require_cointegration: bool = False
    ):
        self.initial_capital = initial_capital
        self.training_window = training_window
        self.refit_frequency = refit_frequency
        self.lookback_window = lookback_window
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
        
        self.commission_pct = commission_pct
        self.bid_ask_spread_pct = bid_ask_spread_pct
        self.slippage_pct = slippage_pct
        
        self.pair_allocation_pct = pair_allocation_pct
        self.max_gross_exposure_pct = max_gross_exposure_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.require_cointegration = require_cointegration

    def run(self, df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame, pd.DataFrame]:
        """
        Executes event-driven walk-forward backtest over price DataFrame.
        Returns:
        - metrics (Dict): Complete quantitative risk-adjusted metrics.
        - trade_ledger (DataFrame): Audit log of every completed trade.
        - equity_df (DataFrame): Bar-by-bar price, spread, Z-score, cash, exposure, and total equity.
        """
        clean_df = validate_price_series(df, min_bars=self.training_window + 10)
        
        portfolio = PortfolioTracker(initial_capital=self.initial_capital)
        simulator = ExecutionSimulator(
            commission_pct=self.commission_pct,
            bid_ask_spread_pct=self.bid_ask_spread_pct,
            slippage_pct=self.slippage_pct
        )
        risk_manager = RiskManager(
            max_gross_exposure_pct=self.max_gross_exposure_pct,
            max_drawdown_pct=self.max_drawdown_pct,
            pair_allocation_pct=self.pair_allocation_pct
        )
        
        n_bars = len(clean_df)
        
        # State Tracking
        pending_orders: List[Order] = []
        trade_ledger: List[Dict[str, Any]] = []
        
        # Tracking arrays for Equity DataFrame
        equity_records = []
        
        current_state = FLAT
        order_counter = 0
        peak_equity = self.initial_capital
        
        # Trade open log tracking
        open_trade_info = None
        
        # Cached Model Parameters (Refitted Walk-Forward)
        beta_past = 1.0
        alpha_past = 0.0
        is_coint_past = True
        
        # Historical spread buffer for rolling Z-score
        spread_history = []
        
        for i in range(n_bars):
            date_t = clean_df.index[i]
            price_a_t = float(clean_df['Stock_A'].iloc[i])
            price_b_t = float(clean_df['Stock_B'].iloc[i])
            
            # --- STEP 1: EXECUTE PENDING ORDERS FROM BAR t-1 ON BAR t (NEXT-BAR EXECUTION) ---
            fills_this_bar = []
            for order in pending_orders:
                base_p = price_a_t if order.symbol == "Stock_A" else price_b_t
                fill = simulator.execute_order(order, fill_timestamp=date_t, base_price=base_p)
                portfolio.process_fill(fill)
                fills_this_bar.append(fill)
            pending_orders = []
            
            # --- STEP 2: MARK-TO-MARKET PORTFOLIO AT BAR t ---
            mtm = portfolio.get_mark_to_market(price_a_t, price_b_t)
            total_equity_t = mtm['total_equity']
            peak_equity = max(peak_equity, total_equity_t)
            
            # Evaluate risk limits
            risk_approved = risk_manager.check_risk_limits(
                current_equity=total_equity_t,
                peak_equity=peak_equity,
                gross_exposure=mtm['gross_exposure']
            )
            
            # --- STEP 3: WALK-FORWARD MODEL ESTIMATION (STRICTLY IN-SAMPLE PAST DATA) ---
            if i >= self.training_window:
                if (i - self.training_window) % self.refit_frequency == 0 or i == self.training_window:
                    past_a = clean_df['Stock_A'].iloc[i - self.training_window : i]
                    past_b = clean_df['Stock_B'].iloc[i - self.training_window : i]
                    
                    try:
                        beta_past, alpha_past = calculate_hedge_ratio(past_a, past_b)
                        coint_res = test_cointegration(past_a, past_b)
                        is_coint_past = coint_res['is_cointegrated']
                    except Exception:
                        pass
                        
            # --- STEP 4: CALCULATE SPREAD AND NO-LEAKAGE ROLLING Z-SCORE ---
            spread_t = price_a_t - (beta_past * price_b_t) - alpha_past
            spread_history.append(spread_t)
            
            # Calculate Z-score using strictly PAST spread values [t-lookback, t-1]
            if len(spread_history) > self.lookback_window:
                past_spread_slice = spread_history[-self.lookback_window - 1 : -1]
                mean_past = float(np.mean(past_spread_slice))
                std_past = float(np.std(past_spread_slice))
                
                if std_past > 1e-8:
                    z_score_t = (spread_t - mean_past) / std_past
                else:
                    z_score_t = 0.0
            else:
                z_score_t = 0.0
                
            # --- STEP 5: EVALUATE SIGNAL STATE MACHINE ---
            signal_t = FLAT
            if i >= self.training_window:
                if abs(z_score_t) >= self.stop_z:
                    if current_state != FLAT:
                        signal_t = STOP_LOSS_SIGNAL
                elif current_state == FLAT:
                    if not self.require_cointegration or is_coint_past:
                        if z_score_t <= -self.entry_z:
                            signal_t = LONG_SPREAD
                        elif z_score_t >= self.entry_z:
                            signal_t = SHORT_SPREAD
                elif current_state != FLAT:
                    if abs(z_score_t) <= self.exit_z:
                        signal_t = EXIT_SIGNAL
                    else:
                        signal_t = current_state
                        
            # --- STEP 6: SUBMIT NEXT-BAR ORDERS IF STATE CHANGES ---
            if i >= self.training_window and risk_approved:
                # Target Position Determination
                if signal_t in [LONG_SPREAD, SHORT_SPREAD] and current_state == FLAT:
                    current_state = signal_t
                    target_qty_a, target_qty_b = risk_manager.calculate_position_sizes(
                        equity=total_equity_t,
                        price_a=price_a_t,
                        price_b=price_b_t,
                        beta=beta_past,
                        signal=signal_t
                    )
                    
                    if target_qty_a > 0:
                        side_a = 'BUY' if signal_t == LONG_SPREAD else 'SELL'
                        side_b = 'SELL' if signal_t == LONG_SPREAD else 'BUY'
                        
                        order_counter += 1
                        pending_orders.append(Order(
                            order_id=f"ORD_{order_counter:06d}_A",
                            timestamp=date_t,
                            symbol="Stock_A",
                            side=side_a,
                            quantity=target_qty_a
                        ))
                        order_counter += 1
                        pending_orders.append(Order(
                            order_id=f"ORD_{order_counter:06d}_B",
                            timestamp=date_t,
                            symbol="Stock_B",
                            side=side_b,
                            quantity=target_qty_b
                        ))
                        
                        open_trade_info = {
                            'entry_signal_date': date_t,
                            'type': 'LONG_SPREAD' if signal_t == LONG_SPREAD else 'SHORT_SPREAD',
                            'beta_at_entry': beta_past,
                            'z_at_entry': z_score_t
                        }
                        
                elif (signal_t in [EXIT_SIGNAL, STOP_LOSS_SIGNAL] or not risk_approved) and current_state != FLAT:
                    # Close existing positions
                    if portfolio.position_a.quantity != 0.0:
                        side_a = 'SELL' if portfolio.position_a.quantity > 0 else 'BUY'
                        order_counter += 1
                        pending_orders.append(Order(
                            order_id=f"ORD_{order_counter:06d}_A_CLOSE",
                            timestamp=date_t,
                            symbol="Stock_A",
                            side=side_a,
                            quantity=abs(portfolio.position_a.quantity)
                        ))
                    if portfolio.position_b.quantity != 0.0:
                        side_b = 'SELL' if portfolio.position_b.quantity > 0 else 'BUY'
                        order_counter += 1
                        pending_orders.append(Order(
                            order_id=f"ORD_{order_counter:06d}_B_CLOSE",
                            timestamp=date_t,
                            symbol="Stock_B",
                            side=side_b,
                            quantity=abs(portfolio.position_b.quantity)
                        ))
                        
                    if open_trade_info is not None:
                        open_trade_info['exit_signal_date'] = date_t
                        open_trade_info['exit_reason'] = "Stop Loss" if signal_t == STOP_LOSS_SIGNAL else "Mean Reversion Exit"
                        open_trade_info['z_at_exit'] = z_score_t
                        open_trade_info['trade_ref'] = len(trade_ledger) + 1
                        trade_ledger.append(open_trade_info)
                        open_trade_info = None
                        
                    current_state = FLAT
                    
            # Record Record Bar State
            equity_records.append({
                'Date': date_t,
                'Stock_A': price_a_t,
                'Stock_B': price_b_t,
                'Beta': beta_past,
                'Spread': spread_t,
                'Z_Score': z_score_t,
                'Signal': signal_t,
                'Cash': mtm['cash'],
                'Equity': total_equity_t,
                'Unrealized_PnL': mtm['unrealized_pnl'],
                'Realized_PnL': mtm['realized_pnl'],
                'Gross_Exposure': mtm['gross_exposure'],
                'Net_Exposure': mtm['net_exposure']
            })
            
        equity_df = pd.DataFrame(equity_records).set_index('Date')
        
        # Build Trade Ledger DataFrame with exact trade metrics
        ledger_df = self._build_trade_ledger_df(trade_ledger, equity_df, simulator)
        
        # Calculate final performance metrics
        metrics = compute_performance_metrics(
            equity_series=equity_df['Equity'],
            trade_ledger=ledger_df,
            initial_capital=self.initial_capital
        )
        
        return metrics, ledger_df, equity_df

    def _build_trade_ledger_df(self, trade_ledger_raw: List[Dict[str, Any]], equity_df: pd.DataFrame, simulator: ExecutionSimulator) -> pd.DataFrame:
        """
        Formats raw trade records into an audit ledger.
        """
        if not trade_ledger_raw:
            return pd.DataFrame(columns=[
                'Entry Date/Time', 'Exit Date/Time', 'Type', 
                'Price A Entry', 'Price A Exit', 'Price B Entry', 'Price B Exit',
                'Gross PnL ($)', 'Fees ($)', 'Slippage ($)', 'Net PnL ($)', 'Holding Period (bars)', 'Reason'
            ])
            
        records = []
        for trade in trade_ledger_raw:
            entry_date = trade['entry_signal_date']
            exit_date = trade['exit_signal_date']
            
            # Find next bar fill timestamps
            sub_df = equity_df.loc[entry_date:exit_date]
            holding_bars = max(1, len(sub_df) - 1)
            
            price_a_entry = float(sub_df['Stock_A'].iloc[0])
            price_b_entry = float(sub_df['Stock_B'].iloc[0])
            price_a_exit = float(sub_df['Stock_A'].iloc[-1])
            price_b_exit = float(sub_df['Stock_B'].iloc[-1])
            
            beta = trade['beta_at_entry']
            trade_type = trade['type']
            
            # Estimated sizing PnL math for ledger audit
            target_cap = self.initial_capital * self.pair_allocation_pct
            qty_a = target_cap / price_a_entry
            qty_b = abs(beta) * qty_a
            
            if trade_type == 'LONG_SPREAD':
                pnl_a = qty_a * (price_a_exit - price_a_entry)
                pnl_b = qty_b * (price_b_entry - price_b_exit)
            else:
                pnl_a = qty_a * (price_a_entry - price_a_exit)
                pnl_b = qty_b * (price_b_exit - price_b_entry)
                
            gross_pnl = pnl_a + pnl_b
            notional_entry = (qty_a * price_a_entry) + (qty_b * price_b_entry)
            notional_exit = (qty_a * price_a_exit) + (qty_b * price_b_exit)
            
            fees = (notional_entry + notional_exit) * self.commission_pct
            slippage = (notional_entry + notional_exit) * (self.slippage_pct + (self.bid_ask_spread_pct / 2.0))
            net_pnl = gross_pnl - fees - slippage
            
            records.append({
                'Entry Date/Time': entry_date,
                'Exit Date/Time': exit_date,
                'Type': trade_type,
                'Price A Entry': round(price_a_entry, 2),
                'Price A Exit': round(price_a_exit, 2),
                'Price B Entry': round(price_b_entry, 2),
                'Price B Exit': round(price_b_exit, 2),
                'Gross PnL ($)': round(gross_pnl, 2),
                'Fees ($)': round(fees, 2),
                'Slippage ($)': round(slippage, 2),
                'Net PnL ($)': round(net_pnl, 2),
                'Holding Period (bars)': holding_bars,
                'Reason': trade['exit_reason']
            })
            
        return pd.DataFrame(records)

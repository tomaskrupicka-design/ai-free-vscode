"""Educational historical spot-market simulator.

No API keys, order endpoints, exchange accounts, leverage or live order execution.
All hypothetical decisions use the PRIOR completed candle; fills use NEXT candle open.
"""
from dataclasses import dataclass
import math

import pandas as pd


@dataclass(frozen=True)
class SimulationSettings:
    initial_balance: float = 10_000.0
    allocation: float = 0.25
    fee_bps: float = 10.0
    slippage_bps: float = 5.0


def simulate_ema_history(market: pd.DataFrame, settings: SimulationSettings | None = None):
    """Simulate hypothetical long/flat positions from historical, closed OHLC candles.

    Previous candle's EMA20/EMA50 relation is observed at the close.
    Portfolio adjustments use the *next* candle's open (no look-ahead).
    No shorting, leverage, derivatives, real account access or exchange execution.
    """
    settings = settings or SimulationSettings()
    if not (settings.initial_balance > 0
            and 0 < settings.allocation <= 1
            and 0 <= settings.fee_bps <= 1000
            and 0 <= settings.slippage_bps <= 1000):
        raise ValueError("Neplatne nastaveni simulace.")

    required = {"open_time", "open", "close"}
    if not required.issubset(market.columns):
        raise ValueError("Chybi sloupce: " + ", ".join(sorted(required - set(market.columns))))

    frame = market.copy().sort_values("open_time").drop_duplicates("open_time")
    frame = frame.reset_index(drop=True)
    if len(frame) < 60:
        raise ValueError("Pro simulaci je potreba alespon 60 dokoncenych svicek.")
    for col in ("open", "close"):
        frame[col] = pd.to_numeric(frame[col], errors="raise")
        if (not frame[col].map(math.isfinite).all()) or (frame[col] <= 0).any():
            raise ValueError("Ceny musi byt kladna konecna cisla.")

    close = frame["close"]
    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()

    balance = float(settings.initial_balance)
    units = 0.0
    paid_entry = 0.0
    total_fees = 0.0
    closed_pnls = []
    trades = []
    history = []
    fee = settings.fee_bps / 10_000.0
    slip = settings.slippage_bps / 10_000.0
    reference_start_price = float(frame.loc[0, "close"])

    for idx, bar in frame.iterrows():
        timestamp = bar["open_time"]
        bar_open = float(bar["open"])
        bar_close = float(bar["close"])

        # Signal based ONLY on earlier closed bars. Current bar close is never used.
        if idx >= 50:
            hypothetical_exposure = bool(ema20.iloc[idx - 1] > ema50.iloc[idx - 1])
            if hypothetical_exposure and units == 0.0:
                budget = balance * settings.allocation
                fill = bar_open * (1 + slip)
                bought = budget / (fill * (1 + fee))
                cost = bought * fill * (1 + fee)
                balance -= cost
                units = bought
                paid_entry = cost
                total_fees += bought * fill * fee
                trades.append({
                    "time": timestamp, "event": "sim_open",
                    "price": fill, "units": bought,
                    "simulated_cash_after": balance,
                    "realized_pnl": None
                })
            elif not hypothetical_exposure and units > 0.0:
                fill = bar_open * (1 - slip)
                proceeds = units * fill * (1 - fee)
                realized = proceeds - paid_entry
                total_fees += units * fill * fee
                balance += proceeds
                closed_pnls.append(realized)
                trades.append({
                    "time": timestamp, "event": "sim_close",
                    "price": fill, "units": units,
                    "simulated_cash_after": balance,
                    "realized_pnl": realized
                })
                units = 0.0
                paid_entry = 0.0

        equity = balance + units * bar_close
        history.append({
            "time": timestamp,
            "simulated_portfolio": equity,
            "buy_hold_reference": settings.initial_balance * bar_close / reference_start_price,
            "cash": balance, "units": units,
        })

    curve = pd.DataFrame(history)
    running_peak = curve["simulated_portfolio"].cummax()
    drawdown = curve["simulated_portfolio"] / running_peak - 1.0
    ending_value = float(curve["simulated_portfolio"].iloc[-1])
    summary = {
        "starting_demo_balance": float(settings.initial_balance),
        "ending_demo_value": ending_value,
        "simulated_return_pct": 100 * (ending_value / settings.initial_balance - 1),
        "reference_return_pct": 100 * (float(curve["buy_hold_reference"].iloc[-1]) / settings.initial_balance - 1),
        "max_drawdown_pct": 100 * float(drawdown.min()),
        "hypothetical_entries": sum(t["event"] == "sim_open" for t in trades),
        "hypothetical_exits": len(closed_pnls),
        "fees_demo_units": total_fees,
        "has_open_simulated_position": units > 0,
        "source_rows": len(frame),
    }
    return {"summary": summary, "equity_curve": curve, "events": pd.DataFrame(trades)}

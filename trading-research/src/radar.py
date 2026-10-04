from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class RadarConfig:
    trend_weight: float = 45.0
    momentum_weight: float = 25.0
    volatility_weight: float = 15.0
    regime_weight: float = 15.0
    long_threshold: float = 30.0
    short_threshold: float = -30.0


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def add_radar_score(
    frame: pd.DataFrame,
    config: RadarConfig | None = None,
) -> pd.DataFrame:
    """Add an explainable research score from -100 to +100.

    Expected columns are produced by the existing signal/regime pipeline:
    - close
    - sma_fast
    - sma_slow
    - rolling_vol
    - trend_regime
    - vol_regime

    This is for historical research/backtesting only.
    """
    cfg = config or RadarConfig()
    required = {
        "close",
        "sma_fast",
        "sma_slow",
        "rolling_vol",
        "trend_regime",
        "vol_regime",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns for radar: {sorted(missing)}")

    out = frame.copy()

    trend_raw = (out["sma_fast"] / out["sma_slow"] - 1.0).fillna(0.0)
    trend_scale = trend_raw.abs().rolling(100, min_periods=20).median()
    trend_scale = trend_scale.replace(0.0, pd.NA).fillna(0.01)
    out["radar_trend_component"] = (
        (trend_raw / trend_scale).clip(-1.0, 1.0) * cfg.trend_weight
    )

    momentum = out["close"].pct_change(20).fillna(0.0)
    momentum_scale = momentum.abs().rolling(100, min_periods=20).median()
    momentum_scale = momentum_scale.replace(0.0, pd.NA).fillna(0.02)
    out["radar_momentum_component"] = (
        (momentum / momentum_scale).clip(-1.0, 1.0) * cfg.momentum_weight
    )

    vol_median = out["rolling_vol"].rolling(100, min_periods=20).median()
    vol_ratio = (out["rolling_vol"] / vol_median).replace([float("inf")], pd.NA)
    vol_penalty = (vol_ratio - 1.0).fillna(0.0).clip(0.0, 1.0)
    direction = (out["radar_trend_component"] + out["radar_momentum_component"]).apply(
        lambda x: 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)
    )
    out["radar_volatility_component"] = (
        -vol_penalty * direction * cfg.volatility_weight
    )

    regime_component = pd.Series(0.0, index=out.index)
    regime_component = regime_component.mask(
        (out["trend_regime"] == "trend") & (direction > 0),
        cfg.regime_weight,
    )
    regime_component = regime_component.mask(
        (out["trend_regime"] == "trend") & (direction < 0),
        -cfg.regime_weight,
    )
    out["radar_regime_component"] = regime_component

    component_cols = [
        "radar_trend_component",
        "radar_momentum_component",
        "radar_volatility_component",
        "radar_regime_component",
    ]
    out["radar_score"] = out[component_cols].sum(axis=1).clip(-100.0, 100.0)

    out["radar_signal"] = "WAIT"
    out.loc[out["radar_score"] >= cfg.long_threshold, "radar_signal"] = "LONG"
    out.loc[out["radar_score"] <= cfg.short_threshold, "radar_signal"] = "SHORT"

    out["radar_reason"] = out.apply(_build_reason, axis=1)
    return out


def _build_reason(row: pd.Series) -> str:
    reasons: list[str] = []

    trend = float(row.get("radar_trend_component", 0.0) or 0.0)
    momentum = float(row.get("radar_momentum_component", 0.0) or 0.0)
    volatility = float(row.get("radar_volatility_component", 0.0) or 0.0)
    regime = float(row.get("radar_regime_component", 0.0) or 0.0)

    if abs(trend) >= 5:
        reasons.append("trend+" if trend > 0 else "trend-")
    if abs(momentum) >= 5:
        reasons.append("momentum+" if momentum > 0 else "momentum-")
    if abs(volatility) >= 2:
        reasons.append("volatility_penalty")
    if abs(regime) >= 5:
        reasons.append("trend_regime")

    return ", ".join(reasons) if reasons else "no_strong_component"


def latest_radar_snapshot(frame: pd.DataFrame) -> dict[str, Any]:
    """Return the last row as a compact explainable snapshot."""
    if frame.empty:
        raise ValueError("Radar frame is empty.")
    required = {
        "radar_score",
        "radar_signal",
        "radar_reason",
        "radar_trend_component",
        "radar_momentum_component",
        "radar_volatility_component",
        "radar_regime_component",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing radar columns: {sorted(missing)}")

    row = frame.iloc[-1]
    return {
        "score": float(row["radar_score"]),
        "signal": str(row["radar_signal"]),
        "reason": str(row["radar_reason"]),
        "components": {
            "trend": float(row["radar_trend_component"]),
            "momentum": float(row["radar_momentum_component"]),
            "volatility": float(row["radar_volatility_component"]),
            "regime": float(row["radar_regime_component"]),
        },
    }

from datetime import UTC, datetime
from typing import List, Dict, Any

from cadr.data.models import DivergenceSignal, StrategySpec
from cadr.analysis.regime import MarketRegime
import cadr.strategy.risk_manager as rm
import cadr.config as cfg

def generate_strategy(
    signals: List[DivergenceSignal], 
    regime: MarketRegime,
    market_context: Dict[str, Any]
) -> StrategySpec:
    """Generate a complete strategy spec from the best signal."""
    if not signals:
        raise ValueError("No divergence signals found to generate strategy.")
        
    # Pick the strongest signal (highest conviction/magnitude)
    best_signal = max(signals, key=lambda s: abs(s.z_score))
    
    pos_size = rm.position_size(regime, best_signal.conviction_score)
    sl_pct = rm.stop_loss_pct(regime)
    thresholds = {
        "entry_zscore": cfg.Z_SCORE_ENTRY_THRESHOLD,
        "exit_zscore": cfg.Z_SCORE_EXIT_THRESHOLD,
        "stop_zscore": cfg.Z_SCORE_STOP_THRESHOLD
    }
    
    # Formulate rules
    entry_rule = f"{best_signal.asset_a}/{best_signal.asset_b} spread z-score magnitude >= {thresholds['entry_zscore']}"
    exit_rule = f"Spread z-score magnitude <= {thresholds['exit_zscore']}"
    sl_rule = f"Spread z-score magnitude >= {thresholds['stop_zscore']} OR {sl_pct*100:.1f}% position loss"
    
    return StrategySpec(
        generated_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        strategy={
            "name": f"CADR_{best_signal.asset_a}_{best_signal.asset_b}_divergence",
            "type": "cross_asset_divergence",
            "pair": {"asset_a": best_signal.asset_a, "asset_b": best_signal.asset_b},
            "direction": best_signal.direction,
            "conviction_score": best_signal.conviction_score,
            "market_regime": regime.value
        },
        analysis={
            "spread_zscore": round(best_signal.z_score, 2),
            "thresholds": thresholds,
            "metadata": best_signal.metadata
        },
        rules={
            "entry": entry_rule,
            "exit": exit_rule,
            "stop_loss": sl_rule,
            "take_profit": f"Mean reversion overshoot (z-score opposite sign)"
        },
        risk_management={
            "position_size_pct": round(pos_size * 100, 2),
            "max_portfolio_risk_pct": round(cfg.DEFAULT_MAX_PORTFOLIO_RISK_PCT * 100, 2),
            "stop_loss_pct": round(sl_pct * 100, 2),
            "take_profit_pct": round(cfg.DEFAULT_TAKE_PROFIT_PCT * 100, 2)
        },
        market_context=market_context
    )

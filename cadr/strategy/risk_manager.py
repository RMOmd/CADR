from cadr.analysis.regime import MarketRegime
import cadr.config as cfg

def position_size(regime: MarketRegime, conviction: int) -> float:
    """Calculate position size % based on regime and conviction score (1-5)."""
    base_size = cfg.DEFAULT_POSITION_SIZE_PCT
    
    # Adjust for regime
    if regime == MarketRegime.RISK_OFF:
        base_size *= 0.5
    elif regime == MarketRegime.CRISIS:
        base_size *= 0.2
    elif regime == MarketRegime.RISK_ON:
        base_size *= 1.2
        
    # Adjust for conviction (1 to 5)
    conviction_multiplier = conviction / 3.0  # conviction 3 is neutral
    
    final_size = base_size * conviction_multiplier
    
    # Cap size
    return min(final_size, 0.15)  # Max 15% per trade

def stop_loss_pct(regime: MarketRegime) -> float:
    """Calculate stop loss % based on regime."""
    if regime == MarketRegime.CRISIS:
        return cfg.DEFAULT_STOP_LOSS_PCT * 0.5
    elif regime == MarketRegime.RISK_OFF:
        return cfg.DEFAULT_STOP_LOSS_PCT * 0.8
    else:
        return cfg.DEFAULT_STOP_LOSS_PCT

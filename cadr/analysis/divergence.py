import pandas as pd
import numpy as np
from typing import List

from cadr.data.models import DivergenceSignal
from cadr.analysis.correlation import rolling_correlation, detect_correlation_breakdown

def compute_spread(prices_a: pd.Series, prices_b: pd.Series, method: str = 'ratio') -> pd.Series:
    """Compute spread between two assets. Method can be 'ratio' or 'difference'."""
    df = pd.concat([prices_a, prices_b], axis=1).dropna()
    if df.empty:
        return pd.Series(dtype=float)
        
    if method == 'ratio':
        return df.iloc[:, 0] / df.iloc[:, 1]
    elif method == 'difference':
        # Simple difference (might need scaling for assets with vastly different prices)
        # Better to normalize first if using difference
        norm_a = df.iloc[:, 0] / df.iloc[0, 0]
        norm_b = df.iloc[:, 1] / df.iloc[0, 1]
        return norm_a - norm_b
    else:
        raise ValueError("Method must be 'ratio' or 'difference'")

def spread_zscore(spread: pd.Series, lookback: int = 30) -> pd.Series:
    """Calculate rolling z-score of the spread."""
    if spread.empty or len(spread) < lookback:
        return pd.Series(index=spread.index, dtype=float)
        
    rolling_mean = spread.rolling(window=lookback).mean()
    rolling_std = spread.rolling(window=lookback).std()
    
    # Avoid division by zero
    rolling_std = rolling_std.replace(0, np.nan)
    
    return (spread - rolling_mean) / rolling_std

def detect_divergences(
    pairs_data: dict,
    threshold: float = 2.0,
    lookback: int = 30,
    require_correlation_breakdown: bool = True
) -> List[DivergenceSignal]:
    """
    Detect divergences across multiple pairs.
    pairs_data: dict of (asset_a, asset_b) -> tuple of (prices_a_series, prices_b_series)
    """
    signals = []
    
    for (asset_a, asset_b), (prices_a, prices_b) in pairs_data.items():
        corr_series = rolling_correlation(prices_a, prices_b, window=lookback)
        correlation_breakdown = bool(detect_correlation_breakdown(corr_series))

        if require_correlation_breakdown and not correlation_breakdown:
            continue

        spread = compute_spread(prices_a, prices_b, method='ratio')
        zscores = spread_zscore(spread, lookback=lookback)
        
        if zscores.empty or pd.isna(zscores.iloc[-1]):
            continue
            
        current_zscore = zscores.iloc[-1]
        
        # Determine if there's a significant divergence
        if abs(current_zscore) >= threshold:
            # If ratio A/B is high (z > threshold), A is overvalued relative to B -> short A, long B
            # If ratio A/B is low (z < -threshold), A is undervalued relative to B -> long A, short B
            direction = f"long_{asset_b}_short_{asset_a}" if current_zscore > 0 else f"long_{asset_a}_short_{asset_b}"
            
            # Simple conviction score based on how far past the threshold it is
            magnitude = abs(current_zscore)
            conviction = min(5, max(1, int((magnitude - threshold) / 0.5) + 1))
            
            signals.append(DivergenceSignal(
                asset_a=asset_a,
                asset_b=asset_b,
                z_score=current_zscore,
                direction=direction,
                conviction_score=conviction,
                metadata={
                    "spread_method": "ratio",
                    "lookback": lookback,
                    "current_ratio": spread.iloc[-1],
                    "correlation_breakdown": correlation_breakdown,
                    "current_correlation": corr_series.iloc[-1] if not corr_series.empty else None
                }
            ))
            
    return signals

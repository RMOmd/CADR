import pytest
import pandas as pd
import numpy as np
from cadr.analysis.divergence import compute_spread, spread_zscore, detect_divergences

def test_compute_spread():
    a = pd.Series([100, 110, 120])
    b = pd.Series([10, 11, 12])
    
    ratio = compute_spread(a, b, method='ratio')
    assert np.isclose(ratio.iloc[0], 10.0)
    assert np.isclose(ratio.iloc[-1], 10.0)
    
def test_spread_zscore():
    spread = pd.Series([10]*30 + [12]) # Sudden jump
    z = spread_zscore(spread, lookback=30)
    
    # The last value should have a high positive z-score
    assert z.iloc[-1] > 2.0

def test_detect_divergences_requires_correlation_breakdown():
    asset_b = pd.Series(np.arange(1, 91, dtype=float))
    asset_a = pd.Series(np.concatenate([
        np.arange(1, 81, dtype=float),
        np.arange(90, 80, -1, dtype=float)
    ]))

    signals = detect_divergences(
        {("AAA", "BBB"): (asset_a, asset_b)},
        threshold=2.0,
        lookback=30,
        require_correlation_breakdown=True
    )

    assert len(signals) == 1
    assert signals[0].metadata["correlation_breakdown"] is True
    assert signals[0].metadata["current_correlation"] is not None

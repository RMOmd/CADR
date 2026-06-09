import pytest
import pandas as pd
import numpy as np
from cadr.analysis.divergence import compute_spread, spread_zscore

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

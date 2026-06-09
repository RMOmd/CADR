import pytest
import pandas as pd
import numpy as np
from cadr.analysis.correlation import rolling_correlation, correlation_zscore, detect_correlation_breakdown

def test_rolling_correlation():
    # Perfectly correlated
    a = pd.Series([1, 2, 3, 4, 5] * 10)
    b = pd.Series([2, 4, 6, 8, 10] * 10)
    corr = rolling_correlation(a, b, window=10)
    assert np.isclose(corr.iloc[-1], 1.0)

    # Inversely correlated
    c = pd.Series([5, 4, 3, 2, 1] * 10)
    corr2 = rolling_correlation(a, c, window=10)
    assert np.isclose(corr2.iloc[-1], -1.0)

def test_correlation_zscore():
    hist = pd.Series([0.8, 0.82, 0.79, 0.81, 0.8])
    current = 0.5 # significant drop
    z = correlation_zscore(current, hist)
    assert z < -2.0 # Should be very negative

def test_detect_breakdown():
    corr = pd.Series([0.9, 0.91, 0.89, 0.9, 0.92, 0.88, 0.4]) # Sudden drop at the end
    assert detect_correlation_breakdown(corr, z_threshold=-2.0) == True

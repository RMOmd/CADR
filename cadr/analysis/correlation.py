import pandas as pd
import numpy as np

def rolling_correlation(series_a: pd.Series, series_b: pd.Series, window: int = 30) -> pd.Series:
    """Calculate rolling Pearson correlation between two pandas Series."""
    # Ensure aligned indices
    df = pd.concat([series_a, series_b], axis=1).dropna()
    if df.empty or len(df) < window:
        return pd.Series(dtype=float)
        
    return df.iloc[:, 0].rolling(window=window).corr(df.iloc[:, 1])

def correlation_zscore(current_corr: float, historical_corr: pd.Series) -> float:
    """Calculate how unusual the current correlation is compared to its history."""
    if historical_corr.empty or len(historical_corr) < 5:
        return 0.0
        
    mean_corr = historical_corr.mean()
    std_corr = historical_corr.std()
    
    if std_corr == 0 or pd.isna(std_corr):
        return 0.0
        
    return (current_corr - mean_corr) / std_corr

def detect_correlation_breakdown(corr_series: pd.Series, z_threshold: float = -2.0) -> bool:
    """Detect if the correlation has significantly broken down."""
    if corr_series.empty:
        return False
        
    current = corr_series.iloc[-1]
    z_score = correlation_zscore(current, corr_series.iloc[:-1])
    
    # Negative z-score means correlation dropped below historical average
    return z_score < z_threshold

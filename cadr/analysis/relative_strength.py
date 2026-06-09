import pandas as pd
from typing import Dict, List, Tuple

def rank_by_momentum(assets_returns: Dict[str, float]) -> List[Tuple[str, float]]:
    """Rank assets by their returns over a period."""
    if not assets_returns:
        return []
        
    # Sort descending by return
    ranked = sorted(assets_returns.items(), key=lambda x: x[1], reverse=True)
    return ranked

def detect_rotation_signal(current_ranks: List[Tuple[str, float]], prev_ranks: List[Tuple[str, float]]) -> List[Dict]:
    """Detect significant changes in ranking (sector rotation)."""
    if not current_ranks or not prev_ranks:
        return []
        
    prev_positions = {asset: idx for idx, (asset, _) in enumerate(prev_ranks)}
    
    signals = []
    for current_idx, (asset, current_ret) in enumerate(current_ranks):
        if asset in prev_positions:
            prev_idx = prev_positions[asset]
            rank_change = prev_idx - current_idx  # Positive means it moved up in rank
            
            # If moved up significantly (e.g., jump of >= 3 spots in a top 10)
            if rank_change >= 3:
                signals.append({
                    "asset": asset,
                    "signal": "gaining_strength",
                    "rank_change": rank_change,
                    "current_rank": current_idx + 1,
                    "prev_rank": prev_idx + 1
                })
            # If moved down significantly
            elif rank_change <= -3:
                signals.append({
                    "asset": asset,
                    "signal": "losing_strength",
                    "rank_change": rank_change,
                    "current_rank": current_idx + 1,
                    "prev_rank": prev_idx + 1
                })
                
    return signals

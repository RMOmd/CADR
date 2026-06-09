import pandas as pd
import numpy as np

def calculate_metrics(equity_curve: pd.Series, trades: list) -> dict:
    """Calculate standard performance metrics from equity curve and trades log."""
    if equity_curve.empty or len(trades) == 0:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_profit_per_trade_pct": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown_pct": 0.0,
            "profit_factor": 0.0,
            "calmar_ratio": 0.0
        }
        
    # Trade metrics
    winning_trades = [t for t in trades if t['pnl_pct'] > 0]
    losing_trades = [t for t in trades if t['pnl_pct'] <= 0]
    
    win_rate = len(winning_trades) / len(trades) if trades else 0.0
    
    avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0.0
    avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0.0
    
    profit_factor = abs(sum([t['pnl_pct'] for t in winning_trades]) / sum([t['pnl_pct'] for t in losing_trades])) if sum([t['pnl_pct'] for t in losing_trades]) != 0 else float('inf')
    
    avg_profit_per_trade = np.mean([t['pnl_pct'] for t in trades])
    
    # Equity curve metrics
    daily_returns = equity_curve.pct_change().dropna()
    
    if len(daily_returns) > 0:
        sharpe_ratio = np.sqrt(365) * daily_returns.mean() / daily_returns.std() if daily_returns.std() != 0 else 0.0
    else:
        sharpe_ratio = 0.0
        
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = abs(drawdown.min())
    
    calmar_ratio = (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) / max_drawdown if max_drawdown != 0 else 0.0
    
    return {
        "total_trades": len(trades),
        "win_rate": round(win_rate, 4),
        "avg_profit_per_trade_pct": round(avg_profit_per_trade * 100, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
        "profit_factor": round(profit_factor, 2),
        "calmar_ratio": round(calmar_ratio, 2)
    }

import pandas as pd

from cadr.data.models import StrategySpec, BacktestResult
from cadr.analysis.divergence import compute_spread, spread_zscore
import cadr.strategy.signals as sig
import cadr.backtest.metrics as metrics
import cadr.config as cfg

def run_backtest(df_a: pd.DataFrame, df_b: pd.DataFrame, spec: StrategySpec) -> BacktestResult:
    """Run a vectorized/iterative backtest based on the strategy spec."""
    
    if df_a.empty or df_b.empty:
        raise ValueError("DataFrames cannot be empty for backtesting.")
        
    # 1. Prepare data
    df = pd.DataFrame({
        'price_a': df_a['close'],
        'price_b': df_b['close']
    }).dropna()
    
    if len(df) < 30:
        raise ValueError("Not enough overlapping data for backtesting.")
        
    df['spread'] = compute_spread(df['price_a'], df['price_b'])
    df['zscore'] = spread_zscore(df['spread'], lookback=30)
    
    # 2. Extract strategy params
    direction = spec.strategy['direction']
    pos_size_pct = spec.risk_management['position_size_pct'] / 100.0
    stop_loss_pct = spec.risk_management['stop_loss_pct'] / 100.0
    thresholds = spec.analysis.get('thresholds', {})
    entry_threshold = thresholds.get('entry_zscore', cfg.Z_SCORE_ENTRY_THRESHOLD)
    exit_threshold = thresholds.get('exit_zscore', cfg.Z_SCORE_EXIT_THRESHOLD)
    stop_threshold = thresholds.get('stop_zscore', cfg.Z_SCORE_STOP_THRESHOLD)
    
    # Simple state machine for trades
    in_position = False
    entry_zscore = 0.0
    entry_price_a = 0.0
    entry_price_b = 0.0
    entry_date = None
    
    trades = []
    realized_equity = 1.0
    equity_curve = pd.Series(index=df.index, dtype=float)
    
    for i, (idx, row) in enumerate(df.iterrows()):
        z = row['zscore']
        
        if pd.isna(z):
            equity_curve.iloc[i] = realized_equity
            continue
            
        if not in_position:
            # Check entry
            # If long_a_short_b, we want z < -ENTRY_THRESHOLD
            # If long_b_short_a, we want z > ENTRY_THRESHOLD
            entered = False
            if direction.startswith("long_" + spec.strategy['pair']['asset_a']):
                if z <= -entry_threshold:
                    entered = True
            else:
                if z >= entry_threshold:
                    entered = True
                    
            if entered:
                in_position = True
                entry_zscore = z
                entry_price_a = row['price_a']
                entry_price_b = row['price_b']
                entry_date = idx
            equity_curve.iloc[i] = realized_equity
        else:
            # Calculate current PnL
            ret_a = (row['price_a'] / entry_price_a) - 1
            ret_b = (row['price_b'] / entry_price_b) - 1
            
            if direction.startswith("long_" + spec.strategy['pair']['asset_a']):
                trade_pnl_pct = ret_a - ret_b
            else:
                trade_pnl_pct = ret_b - ret_a

            mtm_equity = realized_equity * (1 + trade_pnl_pct * pos_size_pct)
                
            # Check exit
            hit_stop = trade_pnl_pct <= -stop_loss_pct or abs(z) >= stop_threshold
            hit_tp = sig.exit_signal(z, entry_zscore, exit_threshold)
            
            if hit_stop or hit_tp:
                # Close position
                in_position = False
                realized_equity = mtm_equity
                
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': idx,
                    'pnl_pct': trade_pnl_pct * pos_size_pct,
                    'reason': 'stop_loss' if hit_stop else 'take_profit'
                })

            equity_curve.iloc[i] = mtm_equity
            
    if in_position:
        last_idx = df.index[-1]
        last_row = df.iloc[-1]
        ret_a = (last_row['price_a'] / entry_price_a) - 1
        ret_b = (last_row['price_b'] / entry_price_b) - 1

        if direction.startswith("long_" + spec.strategy['pair']['asset_a']):
            trade_pnl_pct = ret_a - ret_b
        else:
            trade_pnl_pct = ret_b - ret_a

        realized_equity *= (1 + trade_pnl_pct * pos_size_pct)
        equity_curve.iloc[-1] = realized_equity
        trades.append({
            'entry_date': entry_date,
            'exit_date': last_idx,
            'pnl_pct': trade_pnl_pct * pos_size_pct,
            'reason': 'end_of_period'
        })
        
    # Calculate metrics
    results = metrics.calculate_metrics(equity_curve, trades)
    
    # Fill in start/end dates
    start_date = df.index[0].strftime('%Y-%m-%d')
    end_date = df.index[-1].strftime('%Y-%m-%d')
    
    return BacktestResult(
        period=f"{start_date} to {end_date}",
        total_trades=results['total_trades'],
        win_rate=results['win_rate'],
        avg_profit_per_trade_pct=results['avg_profit_per_trade_pct'],
        sharpe_ratio=results['sharpe_ratio'],
        max_drawdown_pct=results['max_drawdown_pct'],
        profit_factor=results['profit_factor'],
        calmar_ratio=results['calmar_ratio']
    )

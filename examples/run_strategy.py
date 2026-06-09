import sys
import os
import json
import logging

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cadr.config as cfg
from cadr.data.cmc_client import CMCClient
from cadr.analysis.regime import classify_regime
from cadr.analysis.divergence import detect_divergences
from cadr.strategy.generator import generate_strategy
from cadr.backtest.engine import run_backtest

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    # 1. Initialize client
    api_key = os.getenv("CMC_API_KEY", cfg.DEFAULT_SANDBOX_API_KEY)
    using_sandbox = (not api_key) or api_key == cfg.DEFAULT_SANDBOX_API_KEY

    if using_sandbox:
        logging.warning("No custom CMC_API_KEY found. Using sandbox key (data will be mock/random).")
    else:
        logging.info("Using production CMC API.")
        
    client = CMCClient()
    
    pairs_to_analyze = cfg.DEFAULT_PAIRS
    
    logging.info("--- CADR Strategy Generator ---")
    
    # 2. Get global context
    logging.info("Fetching global market context...")
    try:
        global_metrics = client.get_global_metrics()
        fear_greed = client.get_fear_greed()
        regime = classify_regime(global_metrics, fear_greed)
        logging.info(f"Market Regime classified as: {regime.name}")
    except Exception as e:
        logging.error(f"Failed to fetch context: {e}")
        return

    market_context = {
        "btc_dominance": global_metrics.btc_dominance,
        "fear_greed_index": fear_greed.value if fear_greed else None,
        "regime": regime.value
    }
    
    # 3. Fetch historical data and find divergences
    pairs_data = {}
    historical_frames = {}
    for asset_a, asset_b in pairs_to_analyze:
        logging.info(f"Fetching 90-day OHLCV data for {asset_a} and {asset_b}...")
        try:
            df_a = client.get_historical_ohlcv(asset_a, days=90)
            df_b = client.get_historical_ohlcv(asset_b, days=90)
            
            if not df_a.empty and not df_b.empty:
                pairs_data[(asset_a, asset_b)] = (df_a['close'], df_b['close'])
                historical_frames[asset_a] = df_a
                historical_frames[asset_b] = df_b
            else:
                logging.warning(f"Insufficient data for {asset_a}/{asset_b}")
        except Exception as e:
            logging.error(f"Error fetching data for {asset_a}/{asset_b}: {e}")
            
    if not pairs_data:
        logging.error("No valid pair data retrieved. Exiting.")
        return
        
    logging.info("Analyzing correlations and detecting divergences...")
    signals = detect_divergences(
        pairs_data,
        threshold=cfg.Z_SCORE_ENTRY_THRESHOLD,
        lookback=30,
        require_correlation_breakdown=True
    )
    
    if not signals:
        logging.info("No significant divergences found right now.")
        # For the sake of the example, we'll force a signal if running in sandbox
        if using_sandbox:
            from cadr.data.models import DivergenceSignal
            signals = [DivergenceSignal(
                asset_a="BTC", asset_b="ETH", z_score=2.3, direction="long_ETH_short_BTC",
                conviction_score=4, metadata={"forced": True, "correlation_breakdown": True}
            )]
        else:
            return
            
    # 4. Generate Strategy Spec
    logging.info(f"Found {len(signals)} signals. Generating strategy spec...")
    spec = generate_strategy(signals, regime, market_context)
    
    # 5. Run Backtest
    best_signal = max(signals, key=lambda s: abs(s.z_score))
    asset_a, asset_b = best_signal.asset_a, best_signal.asset_b
    logging.info(f"Running backtest for {asset_a}/{asset_b} strategy...")
    
    df_a = historical_frames[asset_a]
    df_b = historical_frames[asset_b]
    
    try:
        backtest_res = run_backtest(df_a, df_b, spec)
        spec.backtest_results = backtest_res.model_dump()
        logging.info(f"Backtest complete. Win rate: {backtest_res.win_rate*100:.1f}%, Sharpe: {backtest_res.sharpe_ratio}")
    except Exception as e:
        logging.error(f"Backtest failed: {e}")
        
    # 6. Output JSON
    output_path = os.path.join(os.path.dirname(__file__), "sample_output.json")
    with open(output_path, "w") as f:
        json.dump(spec.model_dump(), f, indent=2)
        
    logging.info(f"Strategy specification saved to {output_path}")
    print("\n--- Generated Strategy Spec ---")
    print(json.dumps(spec.model_dump(), indent=2))

if __name__ == "__main__":
    main()

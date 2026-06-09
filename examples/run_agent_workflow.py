import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cadr.agent.orchestrator import build_asset_context, build_market_snapshot, generate_agent_strategy


def main():
    btc = build_asset_context(
        {"id": 1, "symbol": "BTC", "name": "Bitcoin"},
        {
            "quote": {
                "USD": {
                    "price": 105000.0,
                    "market_cap": 2_000_000_000_000.0,
                    "volume_24h": 40_000_000_000.0,
                    "percent_change_1h": 0.5,
                    "percent_change_24h": 4.2,
                    "percent_change_7d": 11.8,
                    "percent_change_30d": 24.0,
                }
            }
        },
        {"rsi": 72.0, "macd": {"signal": "bearish_cross"}},
        {"tags": ["macro", "store-of-value"]},
        [{"title": "BTC extends ETF-led run but momentum cools"}],
    )
    eth = build_asset_context(
        {"id": 1027, "symbol": "ETH", "name": "Ethereum"},
        {
            "quote": {
                "USD": {
                    "price": 3900.0,
                    "market_cap": 480_000_000_000.0,
                    "volume_24h": 22_000_000_000.0,
                    "percent_change_1h": -0.3,
                    "percent_change_24h": -2.7,
                    "percent_change_7d": -4.4,
                    "percent_change_30d": 1.5,
                }
            }
        },
        {"rsi": 35.0, "macd": {"signal": "bullish_cross"}},
        {"tags": ["macro", "smart-contracts"]},
        [{"title": "ETH lags BTC despite steady staking demand"}],
    )

    market_snapshot = build_market_snapshot(
        {
            "btc_dominance": 61.2,
            "eth_dominance": 9.1,
            "altcoin_season_index": 33.0,
            "fear_greed_index": 29.0,
            "quote": {"USD": {"total_market_cap": 2_750_000_000_000.0}},
        },
        {"open_interest_change_24h": -9.8, "funding_bias": "risk_off"},
        {"rsi": 43.0, "macd": {"signal": "bearish_cross"}},
        [{"name": "Major Rotation"}],
        [{"title": "Fed rate decision"}],
    )

    spec = generate_agent_strategy([btc, eth], market_snapshot)
    print(json.dumps(spec.model_dump(), indent=2))


if __name__ == "__main__":
    main()

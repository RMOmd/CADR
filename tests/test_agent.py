from cadr.agent.orchestrator import (
    build_asset_context,
    build_market_snapshot,
    generate_agent_strategy,
    select_best_agent_signal,
)


def test_select_best_agent_signal_uses_multifactor_proxy():
    btc = build_asset_context(
        {"id": 1, "symbol": "BTC", "name": "Bitcoin"},
        {
            "quote": {
                "USD": {
                    "price": 105000.0,
                    "market_cap": 2_000_000_000_000.0,
                    "volume_24h": 40_000_000_000.0,
                    "percent_change_1h": 0.4,
                    "percent_change_24h": 4.5,
                    "percent_change_7d": 12.0,
                    "percent_change_30d": 25.0,
                }
            }
        },
        {"rsi": 73.0, "macd": {"signal": "bearish_cross"}},
        {"tags": ["store-of-value", "macro"]},
        [{"title": "BTC cools after strong ETF bid"}],
    )
    eth = build_asset_context(
        {"id": 1027, "symbol": "ETH", "name": "Ethereum"},
        {
            "quote": {
                "USD": {
                    "price": 3900.0,
                    "market_cap": 480_000_000_000.0,
                    "volume_24h": 22_000_000_000.0,
                    "percent_change_1h": -0.2,
                    "percent_change_24h": -3.0,
                    "percent_change_7d": -5.0,
                    "percent_change_30d": 2.0,
                }
            }
        },
        {"rsi": 33.0, "macd": {"signal": "bullish_cross"}},
        {"tags": ["smart-contracts", "macro"]},
        [{"title": "ETH lags majors despite stable staking flows"}],
    )

    signal = select_best_agent_signal([btc, eth])

    assert signal.direction == "long_ETH_short_BTC"
    assert signal.metadata["signal_method"] == "cmc_agent_hub_multifactor_proxy"
    assert signal.conviction_score >= 3


def test_generate_agent_strategy_includes_agent_hub_context():
    sol = build_asset_context(
        {"id": 5426, "symbol": "SOL", "name": "Solana"},
        {
            "quote": {
                "USD": {
                    "price": 185.0,
                    "market_cap": 90_000_000_000.0,
                    "volume_24h": 4_000_000_000.0,
                    "percent_change_1h": 0.8,
                    "percent_change_24h": 6.0,
                    "percent_change_7d": 18.0,
                    "percent_change_30d": 30.0,
                }
            }
        },
        {"rsi": 75.0, "macd": {"signal": "bearish_cross"}},
        {"tags": ["layer-1", "memes"]},
        [{"title": "SOL outperforms on high retail activity"}],
    )
    avax = build_asset_context(
        {"id": 5805, "symbol": "AVAX", "name": "Avalanche"},
        {
            "quote": {
                "USD": {
                    "price": 42.0,
                    "market_cap": 17_000_000_000.0,
                    "volume_24h": 600_000_000.0,
                    "percent_change_1h": -0.3,
                    "percent_change_24h": -4.0,
                    "percent_change_7d": -8.5,
                    "percent_change_30d": 1.0,
                }
            }
        },
        {"rsi": 31.0, "macd": {"signal": "bullish_cross"}},
        {"tags": ["layer-1", "memes"]},
        [{"title": "AVAX underperforms despite subnet narrative"}],
    )
    market_snapshot = build_market_snapshot(
        {
            "btc_dominance": 61.0,
            "eth_dominance": 9.0,
            "altcoin_season_index": 34.0,
            "fear_greed_index": 28.0,
            "quote": {"USD": {"total_market_cap": 2_800_000_000_000.0}},
        },
        {"open_interest_change_24h": -12.0, "funding_bias": "risk_off"},
        {"rsi": 41.0, "macd": {"signal": "bearish_cross"}},
        [{"name": "Layer 1 Rotation"}],
        [{"title": "Fed rate decision"}],
    )

    spec = generate_agent_strategy([sol, avax], market_snapshot)

    assert spec.strategy["execution_style"] == "agent_hub_mcp_first"
    assert spec.analysis["signal_method"] == "cmc_agent_hub_multifactor_proxy"
    assert "Layer 1 Rotation" in spec.market_context["trending_narratives"]
    assert spec.market_context["derivatives"]["funding_bias"] == "risk_off"

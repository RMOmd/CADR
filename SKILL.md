---
name: cross-asset-divergence-rotation
description: Detect cross-asset divergences between crypto pairs and generate backtestable mean-reversion strategy specs with entry/exit rules, risk management, and historical performance metrics.
allowed-tools: [search_cryptos, get_crypto_quotes_latest, get_crypto_technical_analysis, get_global_metrics_latest, get_global_crypto_derivatives_metrics, trending_crypto_narratives, get_upcoming_macro_events]
---

# Cross-Asset Divergence & Rotation (CADR) Strategy Skill

Use this skill when the user asks for a statistical arbitrage, pair trading, mean-reversion, or divergence strategy between two or more crypto assets (e.g., BTC vs ETH, SOL vs AVAX).

## Workflow

Follow these steps strictly to generate the strategy specification:

1. **Asset Universe Setup**
   - Identify the assets the user wants to trade (e.g., "BTC and ETH" or "top Layer 1s").
   - Call `search_cryptos` to resolve the symbols to their numeric CMC IDs.

2. **Data Collection**
   - Call `get_crypto_quotes_latest` with the resolved IDs to get current market prices and 1h/24h/7d changes.
   - Call `get_crypto_technical_analysis` for each asset to get RSI and MACD levels for confirmation.
   - Call `get_global_metrics_latest` to understand current BTC/ETH dominance and the Altcoin Season Index.

3. **Context Gathering**
   - Call `trending_crypto_narratives` to see if the assets belong to a hot sector.
   - Call `get_global_crypto_derivatives_metrics` to assess systemic risk (funding rates, open interest).

4. **Analysis & Strategy Generation**
   - Using the data gathered, identify the laggard and the leader.
   - If the assets historically move together but have diverged significantly (e.g., one is up 10% on the week, the other is down 2%), this is a divergence signal.
   - The strategy is to **LONG the undervalued asset** and **SHORT the overvalued asset** (or simply LONG the undervalued one if shorting isn't preferred).
   - Set the entry condition: Wait for the divergence z-score to reach extreme levels (> 2.0).
   - Set the exit condition: Mean reversion (z-score returning to < 0.5).

5. **Generate Output Specification**
   - Output the strategy strictly in the standard JSON format as shown below.

## Guidelines

- **Risk Management**: Always include a hard stop-loss based on further divergence (e.g., if z-score > 3.5, the correlation is broken, exit the trade).
- **Regime Awareness**: If `get_global_metrics_latest` shows high fear or `get_global_crypto_derivatives_metrics` shows extreme negative funding, reduce position sizes in the spec by 50%.
- Do not output Python code unless explicitly asked. The primary deliverable is the JSON Strategy Specification.

## Output Format

Your final response MUST be a valid JSON block inside markdown:

```json
{
  "skill": "cadr",
  "version": "1.0.0",
  "strategy": {
    "name": "CADR_[ASSET_A]_[ASSET_B]_divergence",
    "type": "cross_asset_divergence",
    "pair": {"asset_a": "[ASSET_A]", "asset_b": "[ASSET_B]"},
    "direction": "long_[ASSET_A]_short_[ASSET_B]"
  },
  "analysis": {
    "spread_zscore": 2.5,
    "rsi_divergence": {"[ASSET_A]": 35, "[ASSET_B]": 72}
  },
  "rules": {
    "entry": "Spread z-score > 2.0 AND [ASSET_A] RSI < 40",
    "exit": "Spread z-score < 0.5",
    "stop_loss": "Spread z-score > 3.5 OR 5% loss"
  },
  "risk_management": {
    "position_size_pct": 5.0,
    "stop_loss_pct": 5.0,
    "take_profit_pct": 8.0
  },
  "market_context": {
    "btc_dominance": 54.2,
    "trending_narratives": ["AI", "DePIN"]
  }
}
```

---
name: cross-asset-divergence-rotation
description: CMC Agent Hub-first crypto analyst skill that uses CoinMarketCap MCP tools to detect cross-asset divergences, rank pair-trade opportunities, and generate regime-aware strategy specs with evidence, catalysts, and optional backtests.
allowed-tools: [search_cryptos, get_crypto_quotes_latest, get_crypto_info, get_crypto_technical_analysis, get_crypto_latest_news, search_crypto_info, get_global_metrics_latest, get_crypto_marketcap_technical_analysis, get_global_crypto_derivatives_metrics, trending_crypto_narratives, get_upcoming_macro_events]
---

# Cross-Asset Divergence & Rotation (CADR) Agent Skill

Use this skill when the user asks for a crypto pair trade, relative-strength dislocation, laggard vs leader setup, mean-reversion idea, or an agentic market decision framework.

This skill is designed for **CoinMarketCap Agent Hub / CMC MCP first** operation. Prefer structured CMC MCP tools over stitching raw REST endpoints manually.

## MCP Prerequisite

Before using the workflow below, make sure the agent has the CoinMarketCap MCP server configured.

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": {
        "X-CMC-MCP-API-KEY": "your-api-key"
      }
    }
  }
}
```

If the CMC tools are unavailable or return connection errors, stop and ask for the MCP connection to be fixed before improvising with partial data.

## Core Principle

Err on the side of collecting **more structured CMC context**, not less. This skill should behave like a market analyst:

- Search first, then batch IDs
- Pull both market-wide and asset-specific signals
- Prefer pre-computed indicators from CMC Agent Hub over raw in-context calculation
- Explain not only the trade, but also the evidence, invalidation, and catalysts

## Workflow

### 1. Resolve the Universe

- If the user names exact assets, call `search_cryptos` for each one and capture the CMC IDs.
- If the user asks for a theme such as "top L1s" or "AI majors", call `trending_crypto_narratives` first to identify the relevant sector and then `search_cryptos` for the chosen assets.
- Batch IDs whenever possible.

### 2. Build the Global Decision Frame

Call these tools before deciding on any trade:

- `get_global_metrics_latest`
- `get_crypto_marketcap_technical_analysis`
- `get_global_crypto_derivatives_metrics`
- `trending_crypto_narratives`
- `get_upcoming_macro_events`

Use them to answer:

- Is this a risk-on, risk-off, or crisis regime?
- Is leverage supportive or dangerous?
- Are there macro catalysts that could invalidate a mean-reversion setup?
- Are we trading with or against the dominant narrative?

### 3. Collect Asset Intelligence

For each candidate asset:

- Call `get_crypto_quotes_latest`
- Call `get_crypto_technical_analysis`
- Call `get_crypto_info`
- Call `get_crypto_latest_news`
- Call `search_crypto_info` when the project, sector, tokenomics, or risk profile is unclear

### 4. Score Divergence Opportunities

When comparing two assets, use the CMC Agent Hub data to measure:

- Relative performance spread across 24h, 7d, and 30d
- RSI dislocation
- MACD asymmetry
- Narrative overlap or narrative divergence
- News/catalyst pressure
- Global market regime and derivatives pressure

Prioritize pairs where:

- Assets usually live in the same macro bucket or narrative cluster
- One asset is stretched/overbought and the other is washed out/underowned
- The regime does not make mean reversion obviously unsafe

### 5. Generate the Strategy

The strategy should usually be:

- **LONG the laggard / undervalued asset**
- **SHORT the leader / overextended asset**

Or, if the user does not want short exposure:

- LONG-only on the laggard with reduced conviction and explicit note that the hedge leg is missing

Always include:

- Entry logic
- Exit logic
- Stop/invalidation logic
- Position size adjusted for regime
- Confidence score
- Evidence block
- Macro and narrative context

### 6. Backtesting Guidance

- If a historical close series is available, you may attach an optional backtest.
- If the user’s API plan does not support the necessary historical endpoint, do **not** invent a backtest. Mark it as unavailable and continue with the agent-driven live thesis.

## Output Rules

- Prefer a compact, structured JSON strategy spec
- Include data-backed evidence, not vague prose
- Mention if the signal is `CMC Agent Hub` derived rather than pure spread-history derived
- When confidence is low, say so explicitly

## Output Format

Your final response MUST be a valid JSON block inside markdown:

```json
{
  "skill": "cadr",
  "version": "2.0.0",
  "strategy": {
    "name": "CADR_[ASSET_A]_[ASSET_B]_agent_hub",
    "type": "cross_asset_divergence",
    "execution_style": "agent_hub_mcp_first",
    "pair": {"asset_a": "[ASSET_A]", "asset_b": "[ASSET_B]"},
    "direction": "long_[ASSET_A]_short_[ASSET_B]",
    "conviction_score": 4
  },
  "analysis": {
    "signal_method": "cmc_agent_hub_multifactor_proxy",
    "spread_zscore": 2.4,
    "rsi_divergence": {"[ASSET_A]": 34, "[ASSET_B]": 72},
    "macd_context": {"[ASSET_A]": "bullish_cross", "[ASSET_B]": "bearish_cross"},
    "evidence": {
      "performance_gap_pct": {"24h": -7.2, "7d": -15.4, "30d": -11.8},
      "shared_narratives": ["Layer 1"],
      "supporting_news": {"[ASSET_A]": ["headline 1"], "[ASSET_B]": ["headline 2"]}
    }
  },
  "rules": {
    "entry": "Agent Hub divergence proxy >= 2.0 with confirming RSI/MACD context",
    "exit": "Relative spread normalizes and RSI divergence compresses",
    "stop_loss": "Divergence proxy > 3.5 or 5% position loss",
    "invalidation": "Macro regime flip, leverage shock, or thesis-breaking news"
  },
  "risk_management": {
    "position_size_pct": 3.0,
    "stop_loss_pct": 4.0,
    "take_profit_pct": 8.0
  },
  "market_context": {
    "regime": "risk_off",
    "btc_dominance": 60.8,
    "fear_greed_index": 31,
    "trending_narratives": ["Layer 1 Rotation"],
    "macro_events": ["Fed rate decision"],
    "derivatives": {"funding_bias": "risk_off"}
  }
}
```

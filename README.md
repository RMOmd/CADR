# Cross-Asset Divergence & Rotation (CADR) Strategy Skill

This repository contains the **CADR** strategy skill for AI Agents, built for the **BNB Hack 2026**.

## Overview

The CADR skill allows AI agents to detect cross-asset divergences between cryptocurrency pairs (e.g., BTC/ETH) and generate robust, backtestable mean-reversion trading strategy specifications. It relies entirely on CoinMarketCap data via the CMC API and MCP Server.

## Features

- **Divergence Detection**: Identifies when historically correlated assets break their correlation using z-scores of their price spread.
- **Regime Awareness**: Classifies market regimes (Risk On, Risk Off, Crisis) using Fear & Greed indices and Bitcoin dominance.
- **Dynamic Risk Management**: Adjusts position sizing and stop-loss levels based on market regime and signal conviction.
- **Backtesting Engine**: Simulates the generated strategy against historical OHLCV data to provide performance metrics (Win Rate, Sharpe Ratio, Max Drawdown).
- **JSON Strategy Spec**: Outputs a structured JSON specification that can be consumed by trading executors.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your CoinMarketCap Pro API Key. If you don't provide one, the sandbox API will be used.
   ```bash
   cp .env.example .env
   ```

## Usage

Agents can trigger this skill using the workflow defined in `SKILL.md`.

To run a manual test and see the full pipeline in action:

```bash
python examples/run_strategy.py
```

## Project Structure

- `SKILL.md`: The manifest and instructions for the AI Agent Hub.
- `cadr/`: The core Python package containing the data layer, analysis engine, strategy generator, and backtester.
- `examples/`: Example scripts showing how to use the package.
- `tests/`: Unit tests for the core logic.

## License
MIT

# Cross-Asset Divergence & Rotation (CADR) Strategy Skill

English: see [English](#english)

Русский: см. [Русский](#русский)

## English

### Overview

This repository contains the **CADR** strategy skill for AI agents, built for the **BNB Hack 2026**.

CADR detects cross-asset divergences between cryptocurrency pairs such as `BTC/ETH` and turns them into backtestable or live-thesis mean-reversion strategy specifications. The project is designed **CoinMarketCap Agent Hub / CMC MCP first**, with direct REST usage kept as a fallback and for validation workflows.

### Features

- **CMC Agent Hub First**: Uses CMC MCP tools for quotes, technicals, narratives, macro events, news, derivatives, and market-wide context.
- **Agentic Pair Selection**: Scores divergence opportunities using relative performance, RSI/MACD dislocation, narrative overlap, and macro regime.
- **Regime Awareness**: Classifies market regimes such as Risk On, Risk Off, and Crisis using Fear & Greed and Bitcoin dominance heuristics.
- **Dynamic Risk Management**: Adjusts position sizing and stop-loss levels based on market regime and signal conviction.
- **More Realistic Backtests**: Includes configurable fees, slippage, short borrow drag, holding-period tracking, and cost drag reporting.
- **Structured Output**: Emits strategy specs with evidence, invalidation criteria, catalysts, thresholds, and market context.
- **Background Watchlist Monitoring**: Tracks a configurable default pair set every few minutes and keeps the latest signal state warm in the dashboard.
- **Forecast Journal**: Saves real entry checkpoints for strong signals, exports them to JSON, and supports next-day validation of whether the pair call actually worked.
- **Resilient Data Transport**: Adds retry/backoff-aware CMC REST and Skill Hub calls so scans fail less often under temporary API issues.
- **Local Control Room**: Includes a FastAPI + SQLite dashboard for signal monitoring, watchlist management, and forecast review.

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

The project expects `pydantic` v2 APIs.

2. Configure CoinMarketCap Agent Hub / CMC MCP using the example config in [cmc_mcp_config.example.json](/D:/CADR/cmc_mcp_config.example.json:1).

CMC MCP endpoint example:

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

3. Copy `.env.example` to `.env` and fill in the keys you actually use:

```bash
cp .env.example .env
```

### Environment Variables

Core API and transport:

- `CMC_SKILL_HUB_API_KEY`
- `CMC_SKILL_HUB_URL`
- `CMC_SKILL_HUB_TOOL_TIMEOUT_SEC`
- `CMC_SKILL_HUB_RETRY_COUNT`
- `CMC_SKILL_HUB_RETRY_BACKOFF_SEC`
- `CMC_API_KEY`
- `CMC_API_BASE_URL`
- `CMC_API_TIMEOUT_SEC`
- `CMC_API_RETRY_COUNT`
- `CMC_API_RETRY_BACKOFF_SEC`
- `CMC_API_MIN_INTERVAL_SEC`

Dashboard and monitoring:

- `CADR_DASHBOARD_DB_PATH`
- `CADR_DASHBOARD_HOST`
- `CADR_DASHBOARD_PORT`
- `CADR_MONITOR_ENABLED`
- `CADR_MONITOR_INTERVAL_SEC`
- `CADR_MONITOR_LOOKBACK_DAYS`
- `CADR_MONITOR_POLL_SEC`
- `CADR_FORECAST_HORIZON_HOURS`
- `CADR_FORECAST_EXPORT_PATH`

Backtest realism:

- `BACKTEST_FEE_BPS_PER_LEG`
- `BACKTEST_SLIPPAGE_BPS_PER_LEG`
- `BACKTEST_BORROW_BPS_DAILY`

### Usage

Agents can trigger this skill using the workflow defined in [SKILL.md](/D:/CADR/SKILL.md:1).

Agent-native demonstration that mirrors CMC MCP payloads:

```bash
python examples/run_agent_workflow.py
```

Live CoinMarketCap Skill Hub run using `find_skill` + `execute_skill`:

```bash
python examples/run_skill_hub_daily_market.py
```

Local monitoring and control dashboard:

```bash
python examples/run_dashboard.py
```

Then open `http://127.0.0.1:8010`.

The dashboard supports:

- Editing the default watchlist directly from the UI.
- Background monitoring every `CADR_MONITOR_INTERVAL_SEC` seconds.
- Saving entry checkpoints for strong signals into `CADR_FORECAST_EXPORT_PATH`.
- Re-checking due forecasts after `CADR_FORECAST_HORIZON_HOURS`.
- Reviewing recent forecasts and latest pair states in one screen.

REST fallback pipeline:

```bash
python examples/run_strategy.py
```

### Forecast Workflow

The current monitoring flow is built for ongoing observation rather than one-off scans:

1. Configure a default watchlist.
2. Let the background monitor scan it every few minutes.
3. Save entry checkpoints automatically for sufficiently strong signals.
4. Export those checkpoints to JSON.
5. Re-evaluate them the next day and compare expected versus realized pair behavior.

The forecast export file is written to [log/cadr_forecasts.json](/D:/CADR/log/cadr_forecasts.json:1) when forecasts exist.

### Project Structure

- `SKILL.md`: MCP-first skill manifest and workflow for CoinMarketCap Agent Hub.
- `cmc_mcp_config.example.json`: Example MCP client configuration for the CMC endpoint.
- `cadr/`: Core Python package containing the data layer, analysis engine, strategy generator, and backtester.
- `cadr/skill_hub/`: Skill Hub client and pipeline layer for `find_skill` / `execute_skill`.
- `cadr/agent/`: Agent orchestration layer that converts CMC MCP snapshots into strategy specs.
- `cadr/dashboard/`: FastAPI, SQLite, background monitor, and local web UI for monitoring runs and controlling scans.
- `examples/`: Example scripts showing how to use the package.
- `tests/`: Unit tests for the core logic.

### License

MIT

## Русский

### Обзор

Этот репозиторий содержит стратегический skill **CADR** для AI-агентов, созданный для **BNB Hack 2026**.

CADR находит кросс-активные расхождения между криптовалютными парами, например `BTC/ETH`, и превращает их в спецификации mean-reversion стратегий, пригодные для бэктеста или живой аналитической гипотезы. Проект построен по принципу **CoinMarketCap Agent Hub / CMC MCP first**, а прямой REST-режим используется как fallback и для валидации.

### Возможности

- **CMC Agent Hub First**: Использует CMC MCP-инструменты для котировок, теханализа, нарративов, макро-событий, новостей, деривативов и общего рыночного контекста.
- **Агентный выбор пар**: Оценивает расхождения по относительной динамике, RSI/MACD dislocation, совпадению нарративов и макрорежиму.
- **Учет рыночного режима**: Классифицирует состояния рынка вроде Risk On, Risk Off и Crisis на основе Fear & Greed и доминации Bitcoin.
- **Динамическое управление риском**: Подстраивает размер позиции и stop-loss под режим рынка и силу сигнала.
- **Более реалистичный бэктест**: Учитывает настраиваемые комиссии, проскальзывание, издержки шорта, длительность удержания и суммарный cost drag.
- **Структурированный выход**: Формирует strategy spec с доказательной базой, invalidation-критериями, катализаторами, порогами и market context.
- **Фоновый мониторинг watchlist**: Следит за настраиваемым набором пар каждые несколько минут и поддерживает актуальное состояние сигналов в дашборде.
- **Журнал прогнозов**: Сохраняет реальные точки входа для сильных сигналов, экспортирует их в JSON и позволяет проверить на следующий день, отработала ли идея.
- **Устойчивый транспортный слой**: Добавляет retry/backoff для CMC REST и Skill Hub вызовов, чтобы пайплайн реже падал на временных проблемах API.
- **Локальная панель управления**: Включает FastAPI + SQLite дашборд для мониторинга сигналов, управления watchlist и просмотра прогнозов.

### Установка

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

Проект использует API из `pydantic` v2.

2. Настрой CoinMarketCap Agent Hub / CMC MCP через пример в [cmc_mcp_config.example.json](/D:/CADR/cmc_mcp_config.example.json:1).

Пример конфигурации CMC MCP:

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

3. Скопируй `.env.example` в `.env` и заполни только те ключи, которые реально используешь:

```bash
cp .env.example .env
```

### Переменные окружения

Основные API и transport-настройки:

- `CMC_SKILL_HUB_API_KEY`
- `CMC_SKILL_HUB_URL`
- `CMC_SKILL_HUB_TOOL_TIMEOUT_SEC`
- `CMC_SKILL_HUB_RETRY_COUNT`
- `CMC_SKILL_HUB_RETRY_BACKOFF_SEC`
- `CMC_API_KEY`
- `CMC_API_BASE_URL`
- `CMC_API_TIMEOUT_SEC`
- `CMC_API_RETRY_COUNT`
- `CMC_API_RETRY_BACKOFF_SEC`
- `CMC_API_MIN_INTERVAL_SEC`

Дашборд и мониторинг:

- `CADR_DASHBOARD_DB_PATH`
- `CADR_DASHBOARD_HOST`
- `CADR_DASHBOARD_PORT`
- `CADR_MONITOR_ENABLED`
- `CADR_MONITOR_INTERVAL_SEC`
- `CADR_MONITOR_LOOKBACK_DAYS`
- `CADR_MONITOR_POLL_SEC`
- `CADR_FORECAST_HORIZON_HOURS`
- `CADR_FORECAST_EXPORT_PATH`

Реализм бэктеста:

- `BACKTEST_FEE_BPS_PER_LEG`
- `BACKTEST_SLIPPAGE_BPS_PER_LEG`
- `BACKTEST_BORROW_BPS_DAILY`

### Использование

Агенты могут вызывать этот skill по workflow, описанному в [SKILL.md](/D:/CADR/SKILL.md:1).

Агентный демонстрационный сценарий, повторяющий структуру CMC MCP payload:

```bash
python examples/run_agent_workflow.py
```

Живой запуск CoinMarketCap Skill Hub через `find_skill` + `execute_skill`:

```bash
python examples/run_skill_hub_daily_market.py
```

Локальный дашборд мониторинга и управления:

```bash
python examples/run_dashboard.py
```

После запуска открой `http://127.0.0.1:8010`.

Дашборд поддерживает:

- Редактирование watchlist прямо из интерфейса.
- Фоновый мониторинг каждые `CADR_MONITOR_INTERVAL_SEC` секунд.
- Сохранение точек входа для сильных сигналов в `CADR_FORECAST_EXPORT_PATH`.
- Повторную проверку прогнозов через `CADR_FORECAST_HORIZON_HOURS`.
- Просмотр последних прогнозов и текущих состояний пар в одном окне.

REST fallback pipeline:

```bash
python examples/run_strategy.py
```

### Сценарий работы с прогнозами

Текущий monitoring workflow рассчитан не на разовый запуск, а на постоянное наблюдение:

1. Настраивается базовый watchlist.
2. Фоновый монитор сканирует его каждые несколько минут.
3. Для достаточно сильных сигналов автоматически сохраняются точки входа.
4. Эти точки экспортируются в JSON.
5. На следующий день они переоцениваются, и можно сравнить ожидаемое движение пары с фактическим.

Файл экспорта прогнозов записывается в [log/cadr_forecasts.json](/D:/CADR/log/cadr_forecasts.json:1), когда прогнозы уже сохранены.

### Структура проекта

- `SKILL.md`: MCP-first manifest и workflow для CoinMarketCap Agent Hub.
- `cmc_mcp_config.example.json`: Пример конфигурации MCP-клиента для CMC endpoint.
- `cadr/`: Основной Python-пакет с data layer, analysis engine, strategy generator и backtester.
- `cadr/skill_hub/`: Клиент Skill Hub и pipeline-слой для `find_skill` / `execute_skill`.
- `cadr/agent/`: Слой агентной оркестрации, который превращает CMC MCP snapshots в strategy specs.
- `cadr/dashboard/`: FastAPI, SQLite, фоновый монитор и локальный web UI для мониторинга запусков и управления сканами.
- `examples/`: Примерные скрипты использования.
- `tests/`: Unit-тесты для ключевой логики.

### Лицензия

MIT

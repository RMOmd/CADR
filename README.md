# CADR: Cross-Asset Divergence & Rotation

English and Russian product overview for the current CADR build.

## EN

### What CADR is

CADR is a crypto cross-asset divergence research and monitoring system built for mean-reversion pair setups. It combines CoinMarketCap market context, pair-level divergence analysis, a backtest layer, a local dashboard, and a forecast journal so the team can move from idea generation to evidence-based validation.

![CADR Dashboard](screenshot.png)

### Core capabilities

- MCP-first and CMC-centric workflow for quotes, market context, technical context, and Skill Hub runs.
- Pair divergence detection for liquid crypto assets such as `BTC/ETH`, `ETH/SOL`, and `SOL/AVAX`.
- Local signal scoring with spread z-score, correlation, conviction, divergence state, and macro regime overlays.
- Backtesting with configurable fees, slippage, and short borrow drag.
- Forecast journaling that stores real entry checkpoints and later evaluates whether a call worked.
- FastAPI + SQLite dashboard for watchlist control, scans, runs, snapshots, evaluations, and job status.
- Snapshot export/evaluation flow for hackathon demos and operator review.
- Bilingual-ready operator UI with watchlist editing, monitoring controls, and compact signal summaries.

### Major upgrades in this version

- Background jobs and polling:
  long scans, snapshot export, and evaluation can run asynchronously instead of blocking the UI.
- Cost-aware forecast evaluation:
  forecast outcomes now consider fees, slippage, and borrow drag, not only raw spread movement.
- Stronger forecast gating:
  the system blocks unstable setups such as stablecoin legs, extreme z-scores, weak correlation, low aligned history, and volatility imbalance.
- Dynamic forecast horizon:
  horizon selection can adapt instead of relying on a single fixed holding window.
- Snapshot cohort split:
  CADR now separates raw pair coverage from execution-ready candidates.
- Demo and confirmed cohorts:
  snapshots now track `demo_shortlist` and `confirmed_shortlist` instead of pretending every signal is trade-ready.
- Safer JSON and storage handling:
  non-finite metrics are sanitized before they reach the API or saved snapshot files.
- Cleaner live monitoring universe:
  the default live watchlist was narrowed to the highest-quality core pairs to accumulate cleaner evidence.

### Current default live watchlist

Execution-focused pairs:

- `BTC/ETH`
- `ETH/SOL`
- `SOL/AVAX`
- `BTC/SOL`
- `ETH/AVAX`

Research-only extensions:

- `BTC/BNB`
- `ETH/BNB`
- `BTC/XRP`
- `ETH/ADA`

### How the decision flow works

1. CADR collects pair context and market context from CoinMarketCap-driven sources.
2. It builds a divergence strategy specification for a pair.
3. It applies local quality gates before creating a forecast.
4. The dashboard stores the signal, forecast checkpoint, and supporting metadata.
5. Snapshot export captures the current state of all tracked pairs.
6. Snapshot evaluation checks later performance and separates research coverage from execution-grade evidence.

### Dashboard features

- Editable watchlist from the browser UI.
- Background monitoring on a configurable interval.
- Manual pair scan, default scan, daily overview, snapshot export, and snapshot evaluation.
- Recent signals panel with signal state, z-score, correlation, and direction.
- Snapshot cards for:
  raw pair count, execution-ready count, demo shortlist, confirmed shortlist, and latest evaluation status.
- Forecast summary with pending vs evaluated calls.
- Background job status with queued/running/completed states.

### Repository structure

- `cadr/analysis/`: spread, divergence, and signal math.
- `cadr/backtest/`: backtest engine and metrics.
- `cadr/dashboard/`: FastAPI app, SQLite storage, snapshot/evaluation logic, and web UI.
- `cadr/data/`: CoinMarketCap REST client and models.
- `cadr/skill_hub/`: Skill Hub orchestration and CADR strategy generation.
- `examples/`: runnable local entry points.
- `tests/`: dashboard, strategy, and behavior coverage.

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure MCP access with [cmc_mcp_config.example.json](/D:/CADR/cmc_mcp_config.example.json:1).

3. For REST fallback mode, copy `.env.example` to `.env` and provide your CoinMarketCap API key.

```bash
cp .env.example .env
```

### Running locally

Dashboard:

```bash
python examples/run_dashboard.py
```

Agent workflow demo:

```bash
python examples/run_agent_workflow.py
```

Skill Hub daily market run:

```bash
python examples/run_skill_hub_daily_market.py
```

REST fallback strategy run:

```bash
python examples/run_strategy.py
```

Default dashboard URL:

```text
http://127.0.0.1:8010
```

### Important environment controls

- `CADR_MONITOR_INTERVAL_SEC`
- `CADR_MONITOR_LOOKBACK_DAYS`
- `CADR_FORECAST_HORIZON_HOURS`
- `CADR_FORECAST_MIN_CONVICTION`
- `CADR_FORECAST_MIN_CORRELATION`
- `CADR_FORECAST_MAX_ABS_ZSCORE`
- `CADR_FORECAST_MAX_VOL_RATIO`
- `CADR_DEMO_TARGET_WIN_RATE`
- `CADR_CONFIRMED_TARGET_WIN_RATE`
- `BACKTEST_FEE_BPS_PER_LEG`
- `BACKTEST_SLIPPAGE_BPS_PER_LEG`
- `BACKTEST_BORROW_BPS_DAILY`

### Current operational note

CADR now shows a cleaner separation between:

- research coverage,
- demo-grade candidates,
- confirmed execution-grade candidates.

This is intentional. The system is designed to prove quality with stored evidence, not to fabricate high win rates before enough observations exist.

## RU

### Что такое CADR

CADR — это система исследования и мониторинга кросс-ассетных дивергенций на крипторынке для поиска mean-reversion сетапов в парах. Она объединяет рыночный контекст CoinMarketCap, анализ пар, слой бэктеста, локальный дашборд и журнал прогнозов, чтобы команда могла перейти от идеи к проверке на реальных данных.

![CADR Dashboard](screenshot.png)

### Основные возможности

- MCP-first и CMC-centric workflow для котировок, рыночного контекста, технического контекста и запусков Skill Hub.
- Поиск дивергенций по ликвидным криптопарам, например `BTC/ETH`, `ETH/SOL`, `SOL/AVAX`.
- Локальная оценка сигналов по spread z-score, корреляции, conviction, состоянию дивергенции и макрорежиму.
- Бэктест с учетом комиссий, проскальзывания и стоимости шорта.
- Журнал прогнозов, который сохраняет реальные точки входа и потом проверяет, сработал прогноз или нет.
- Дашборд на FastAPI + SQLite для управления watchlist, сканами, запусками, snapshot, проверками и фоновыми задачами.
- Цикл snapshot export/evaluation для хакатон-демо и операторской проверки.
- Подготовленный к двуязычной работе UI с редактированием watchlist, управлением мониторингом и компактными карточками сигналов.

### Крупные улучшения в этой версии

- Фоновые задачи и polling:
  долгие сканы, экспорт snapshot и evaluation теперь выполняются асинхронно и не блокируют UI.
- Cost-aware оценка прогнозов:
  результаты прогнозов теперь учитывают комиссии, проскальзывание и borrow drag, а не только движение спрэда.
- Более строгий gating прогнозов:
  система отсекает нестабильные сетапы вроде stablecoin legs, экстремальных z-score, слабой корреляции, короткой общей истории и дисбаланса волатильности.
- Динамический горизонт прогноза:
  горизонт удержания теперь можно подбирать гибко, а не держать всегда фиксированным.
- Разделение snapshot cohort:
  CADR теперь отделяет просто покрытые пары от execution-ready кандидатов.
- Demo и confirmed cohorts:
  snapshot теперь ведет `demo_shortlist` и `confirmed_shortlist`, а не делает вид, что любой сигнал уже готов к торговле.
- Более безопасная работа с JSON и storage:
  невалидные числовые значения санитизируются до попадания в API и snapshot-файлы.
- Более чистый live monitoring universe:
  дефолтный watchlist сужен до набора более качественных core-пар, чтобы быстрее накапливать чистую статистику.

### Текущий боевой watchlist по умолчанию

Пары для execution-фокуса:

- `BTC/ETH`
- `ETH/SOL`
- `SOL/AVAX`
- `BTC/SOL`
- `ETH/AVAX`

Пары для research-слоя:

- `BTC/BNB`
- `ETH/BNB`
- `BTC/XRP`
- `ETH/ADA`

### Как работает логика принятия решения

1. CADR собирает pair context и market context из CoinMarketCap-ориентированных источников.
2. Система строит divergence strategy specification для пары.
3. Перед созданием прогноза применяются локальные quality gates.
4. Дашборд сохраняет сигнал, checkpoint прогноза и сопроводительные метаданные.
5. Snapshot export фиксирует текущее состояние по всем отслеживаемым парам.
6. Snapshot evaluation позже проверяет результат и разделяет research coverage и execution-grade evidence.

### Возможности дашборда

- Редактируемый watchlist прямо из браузера.
- Фоновый мониторинг с настраиваемым интервалом.
- Ручной запуск pair scan, default scan, daily overview, snapshot export и snapshot evaluation.
- Панель последних сигналов с состоянием, z-score, корреляцией и направлением.
- Snapshot-карточки для:
  общего числа пар, execution-ready count, demo shortlist, confirmed shortlist и статуса последней проверки.
- Сводка прогнозов с разделением на pending и evaluated.
- Статусы фоновых задач с состояниями queued/running/completed.

### Структура репозитория

- `cadr/analysis/`: математика спрэда, дивергенций и сигналов.
- `cadr/backtest/`: движок бэктеста и метрики.
- `cadr/dashboard/`: FastAPI-приложение, SQLite storage, логика snapshot/evaluation и web UI.
- `cadr/data/`: REST-клиент CoinMarketCap и модели.
- `cadr/skill_hub/`: orchestration для Skill Hub и генерация CADR-стратегий.
- `examples/`: локальные точки запуска.
- `tests/`: покрытие dashboard, strategy и поведенческой логики.

### Установка

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Настроить MCP-доступ через [cmc_mcp_config.example.json](/D:/CADR/cmc_mcp_config.example.json:1).

3. Для REST fallback режима скопировать `.env.example` в `.env` и добавить API key CoinMarketCap.

```bash
cp .env.example .env
```

### Локальный запуск

Дашборд:

```bash
python examples/run_dashboard.py
```

Демо agent workflow:

```bash
python examples/run_agent_workflow.py
```

Daily market запуск через Skill Hub:

```bash
python examples/run_skill_hub_daily_market.py
```

REST fallback запуск стратегии:

```bash
python examples/run_strategy.py
```

Адрес дашборда по умолчанию:

```text
http://127.0.0.1:8010
```

### Важные настройки окружения

- `CADR_MONITOR_INTERVAL_SEC`
- `CADR_MONITOR_LOOKBACK_DAYS`
- `CADR_FORECAST_HORIZON_HOURS`
- `CADR_FORECAST_MIN_CONVICTION`
- `CADR_FORECAST_MIN_CORRELATION`
- `CADR_FORECAST_MAX_ABS_ZSCORE`
- `CADR_FORECAST_MAX_VOL_RATIO`
- `CADR_DEMO_TARGET_WIN_RATE`
- `CADR_CONFIRMED_TARGET_WIN_RATE`
- `BACKTEST_FEE_BPS_PER_LEG`
- `BACKTEST_SLIPPAGE_BPS_PER_LEG`
- `BACKTEST_BORROW_BPS_DAILY`

### Важная текущая оговорка

Теперь CADR явно разделяет:

- research coverage,
- demo-grade candidates,
- confirmed execution-grade candidates.

Это сделано специально. Система должна доказывать качество накопленными данными, а не рисовать высокий win rate до того, как появится достаточное число наблюдений.

## License

MIT

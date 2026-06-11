import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_API_BASE_URL = os.getenv("CMC_API_BASE_URL", "https://pro-api.coinmarketcap.com")
CMC_API_TIMEOUT_SEC = int(os.getenv("CMC_API_TIMEOUT_SEC", "30"))
CMC_API_RETRY_COUNT = int(os.getenv("CMC_API_RETRY_COUNT", "3"))
CMC_API_RETRY_BACKOFF_SEC = float(os.getenv("CMC_API_RETRY_BACKOFF_SEC", "1.5"))
CMC_API_MIN_INTERVAL_SEC = float(os.getenv("CMC_API_MIN_INTERVAL_SEC", "1.2"))
CMC_SKILL_HUB_API_KEY = os.getenv("CMC_SKILL_HUB_API_KEY")
CMC_SKILL_HUB_URL = os.getenv("CMC_SKILL_HUB_URL", "https://mcp.coinmarketcap.com/skill-hub/stream")
CMC_SKILL_HUB_TOOL_TIMEOUT_SEC = int(os.getenv("CMC_SKILL_HUB_TOOL_TIMEOUT_SEC", "300"))
CMC_SKILL_HUB_RETRY_COUNT = int(os.getenv("CMC_SKILL_HUB_RETRY_COUNT", "2"))
CMC_SKILL_HUB_RETRY_BACKOFF_SEC = float(os.getenv("CMC_SKILL_HUB_RETRY_BACKOFF_SEC", "2.0"))

# Strategy Configuration
DEFAULT_PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "BNB"),
    ("SOL", "AVAX"),
]

# Confirmed watchlist focuses on the tightest liquid major pairs where we have
# the best chance to accumulate repeatable evidence instead of noisy one-offs.
CONFIRMED_MONITORING_PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("SOL", "AVAX"),
    ("BTC", "SOL"),
    ("ETH", "AVAX"),
]

# Broader research universe stays available for manual scans, but the dashboard
# defaults to the tighter confirmed set so the live monitor compounds cleaner data.
RESEARCH_MONITORING_PAIRS = [
    ("BTC", "BNB"),
    ("ETH", "BNB"),
    ("BTC", "XRP"),
    ("ETH", "ADA"),
]

# Expanded experiment set built from current top-cap CoinMarketCap majors while
# skipping stablecoin legs that CADR blocks by design.
TOP20_CAP_MONITORING_PAIRS = [
    ("BTC", "ETH"),
    ("BTC", "BNB"),
    ("BTC", "XRP"),
    ("BTC", "SOL"),
    ("BTC", "TRX"),
    ("BTC", "DOGE"),
    ("ETH", "BNB"),
    ("ETH", "XRP"),
    ("ETH", "SOL"),
    ("ETH", "TRX"),
    ("ETH", "DOGE"),
    ("BNB", "SOL"),
    ("BNB", "XRP"),
    ("SOL", "XRP"),
    ("SOL", "ADA"),
    ("SOL", "LINK"),
    ("TRX", "TON"),
    ("DOGE", "XRP"),
    ("XMR", "ZEC"),
    ("LTC", "BCH"),
]

MONITORING_PAIRS = list(TOP20_CAP_MONITORING_PAIRS)
CADR_DASHBOARD_DB_PATH = os.getenv("CADR_DASHBOARD_DB_PATH", "log/cadr_dashboard.db")
CADR_DASHBOARD_HOST = os.getenv("CADR_DASHBOARD_HOST", "127.0.0.1")
CADR_DASHBOARD_PORT = int(os.getenv("CADR_DASHBOARD_PORT", "8010"))
CADR_MONITOR_ENABLED = os.getenv("CADR_MONITOR_ENABLED", "1") == "1"
CADR_MONITOR_INTERVAL_SEC = int(os.getenv("CADR_MONITOR_INTERVAL_SEC", "300"))
CADR_MONITOR_LOOKBACK_DAYS = int(os.getenv("CADR_MONITOR_LOOKBACK_DAYS", "90"))
CADR_MONITOR_POLL_SEC = int(os.getenv("CADR_MONITOR_POLL_SEC", "10"))
CADR_FORECAST_HORIZON_HOURS = int(os.getenv("CADR_FORECAST_HORIZON_HOURS", "24"))
CADR_FORECAST_MIN_HORIZON_HOURS = int(os.getenv("CADR_FORECAST_MIN_HORIZON_HOURS", "12"))
CADR_FORECAST_MAX_HORIZON_HOURS = int(os.getenv("CADR_FORECAST_MAX_HORIZON_HOURS", "72"))
CADR_FORECAST_EXPORT_PATH = os.getenv("CADR_FORECAST_EXPORT_PATH", "log/cadr_forecasts.json")
CADR_FORECAST_MIN_CONVICTION = int(os.getenv("CADR_FORECAST_MIN_CONVICTION", "4"))
CADR_FORECAST_MIN_CORRELATION = float(os.getenv("CADR_FORECAST_MIN_CORRELATION", "0.7"))
CADR_FORECAST_MIN_ALIGNED_DAYS = int(os.getenv("CADR_FORECAST_MIN_ALIGNED_DAYS", "60"))
CADR_FORECAST_REQUIRE_NON_DEFENSIVE = os.getenv("CADR_FORECAST_REQUIRE_NON_DEFENSIVE", "1") == "1"
CADR_FORECAST_FLAT_BAND_PCT = float(os.getenv("CADR_FORECAST_FLAT_BAND_PCT", "0.05"))
CADR_FORECAST_MAX_ABS_ZSCORE = float(os.getenv("CADR_FORECAST_MAX_ABS_ZSCORE", "8.0"))
CADR_FORECAST_MAX_VOL_RATIO = float(os.getenv("CADR_FORECAST_MAX_VOL_RATIO", "8.0"))
CADR_FORECAST_BLOCK_STABLE_LEGS = os.getenv("CADR_FORECAST_BLOCK_STABLE_LEGS", "1") == "1"
CADR_SNAPSHOT_MAX_SIGNAL_AGE_HOURS = int(os.getenv("CADR_SNAPSHOT_MAX_SIGNAL_AGE_HOURS", "48"))
CADR_SNAPSHOT_INCLUDE_NON_WATCHLIST = os.getenv("CADR_SNAPSHOT_INCLUDE_NON_WATCHLIST", "0") == "1"
CADR_SNAPSHOT_REQUIRE_OK_STATUS = os.getenv("CADR_SNAPSHOT_REQUIRE_OK_STATUS", "1") == "1"
CADR_DEMO_TARGET_WIN_RATE = float(os.getenv("CADR_DEMO_TARGET_WIN_RATE", "0.75"))
CADR_DEMO_STRETCH_WIN_RATE = float(os.getenv("CADR_DEMO_STRETCH_WIN_RATE", "0.85"))
CADR_DEMO_SHORTLIST_LIMIT = int(os.getenv("CADR_DEMO_SHORTLIST_LIMIT", "4"))
CADR_DEMO_MIN_TRADES = int(os.getenv("CADR_DEMO_MIN_TRADES", "2"))
CADR_DEMO_MIN_CORRELATION = float(os.getenv("CADR_DEMO_MIN_CORRELATION", "0.8"))
CADR_DEMO_MAX_ABS_ZSCORE = float(os.getenv("CADR_DEMO_MAX_ABS_ZSCORE", "6.5"))
CADR_DEMO_MIN_ABS_ZSCORE = float(os.getenv("CADR_DEMO_MIN_ABS_ZSCORE", "2.0"))
CADR_CONFIRMED_TARGET_WIN_RATE = float(os.getenv("CADR_CONFIRMED_TARGET_WIN_RATE", "0.75"))
CADR_CONFIRMED_STRETCH_WIN_RATE = float(os.getenv("CADR_CONFIRMED_STRETCH_WIN_RATE", "0.85"))
CADR_CONFIRMED_MIN_EVIDENCE_SAMPLES = int(os.getenv("CADR_CONFIRMED_MIN_EVIDENCE_SAMPLES", "6"))
CADR_CONFIRMED_SHORTLIST_LIMIT = int(os.getenv("CADR_CONFIRMED_SHORTLIST_LIMIT", "3"))

# Divergence detection thresholds
Z_SCORE_ENTRY_THRESHOLD = 2.0
Z_SCORE_EXIT_THRESHOLD = 0.5
Z_SCORE_STOP_THRESHOLD = 3.5

# RSI thresholds for confirmation
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Risk Management
DEFAULT_POSITION_SIZE_PCT = 0.05  # 5%
DEFAULT_MAX_PORTFOLIO_RISK_PCT = 0.02  # 2%
DEFAULT_STOP_LOSS_PCT = 0.05  # 5%
DEFAULT_TAKE_PROFIT_PCT = 0.08  # 8%
BACKTEST_FEE_BPS_PER_LEG = float(os.getenv("BACKTEST_FEE_BPS_PER_LEG", "6"))
BACKTEST_SLIPPAGE_BPS_PER_LEG = float(os.getenv("BACKTEST_SLIPPAGE_BPS_PER_LEG", "4"))
BACKTEST_BORROW_BPS_DAILY = float(os.getenv("BACKTEST_BORROW_BPS_DAILY", "1.5"))

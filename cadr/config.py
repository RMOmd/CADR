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
    ("SOL", "AVAX")
]
MONITORING_PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "BNB"),
    ("ETH", "BNB"),
    ("BTC", "XRP"),
    ("SOL", "AVAX"),
    ("BTC", "SOL"),
    ("ETH", "AVAX"),
    ("ETH", "ADA"),
]
CADR_DASHBOARD_DB_PATH = os.getenv("CADR_DASHBOARD_DB_PATH", "log/cadr_dashboard.db")
CADR_DASHBOARD_HOST = os.getenv("CADR_DASHBOARD_HOST", "127.0.0.1")
CADR_DASHBOARD_PORT = int(os.getenv("CADR_DASHBOARD_PORT", "8010"))
CADR_MONITOR_ENABLED = os.getenv("CADR_MONITOR_ENABLED", "1") == "1"
CADR_MONITOR_INTERVAL_SEC = int(os.getenv("CADR_MONITOR_INTERVAL_SEC", "300"))
CADR_MONITOR_LOOKBACK_DAYS = int(os.getenv("CADR_MONITOR_LOOKBACK_DAYS", "90"))
CADR_MONITOR_POLL_SEC = int(os.getenv("CADR_MONITOR_POLL_SEC", "10"))
CADR_FORECAST_HORIZON_HOURS = int(os.getenv("CADR_FORECAST_HORIZON_HOURS", "24"))
CADR_FORECAST_EXPORT_PATH = os.getenv("CADR_FORECAST_EXPORT_PATH", "log/cadr_forecasts.json")

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

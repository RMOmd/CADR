import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
DEFAULT_SANDBOX_API_KEY = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"
CMC_API_KEY = os.getenv("CMC_API_KEY", DEFAULT_SANDBOX_API_KEY)
CMC_API_BASE_URL = os.getenv("CMC_API_BASE_URL", "https://sandbox-api.coinmarketcap.com")
CMC_SKILL_HUB_API_KEY = os.getenv("CMC_SKILL_HUB_API_KEY")
CMC_SKILL_HUB_URL = os.getenv("CMC_SKILL_HUB_URL", "https://mcp.coinmarketcap.com/skill-hub/stream")
CMC_SKILL_HUB_TOOL_TIMEOUT_SEC = int(os.getenv("CMC_SKILL_HUB_TOOL_TIMEOUT_SEC", "300"))

# Strategy Configuration
DEFAULT_PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "BNB"),
    ("SOL", "AVAX")
]

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

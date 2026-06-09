import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from cadr.config import (
    CMC_API_BASE_URL,
    CMC_API_KEY,
    CMC_API_MIN_INTERVAL_SEC,
    CMC_API_RETRY_BACKOFF_SEC,
    CMC_API_RETRY_COUNT,
    CMC_API_TIMEOUT_SEC,
)
from cadr.data.models import AssetQuote, FearGreedEntry, GlobalMetrics


def _coalesce_value(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


class CMCClient:
    """Client for the CoinMarketCap REST API with basic retries and pacing."""

    def __init__(
        self,
        api_key: Optional[str] = CMC_API_KEY,
        base_url: str = CMC_API_BASE_URL,
        timeout_sec: int = CMC_API_TIMEOUT_SEC,
        retry_count: int = CMC_API_RETRY_COUNT,
        retry_backoff_sec: float = CMC_API_RETRY_BACKOFF_SEC,
        min_interval_sec: float = CMC_API_MIN_INTERVAL_SEC,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = max(5, int(timeout_sec))
        self.retry_count = max(0, int(retry_count))
        self.retry_backoff_sec = max(0.1, float(retry_backoff_sec))
        self.min_interval_sec = max(0.0, float(min_interval_sec))
        self.session = requests.Session()
        self._symbol_to_id_cache: Dict[str, int] = {}
        self._last_request_at = 0.0

        if self.api_key:
            self.session.headers.update({
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json",
            })

    def _ensure_api_key(self) -> None:
        if not self.api_key:
            raise ValueError("CMC_API_KEY is required for CoinMarketCap REST requests.")

    def _apply_rate_limit(self) -> None:
        if self.min_interval_sec <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait_for = self.min_interval_sec - elapsed
        if wait_for > 0:
            time.sleep(wait_for)

    def _request(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self._ensure_api_key()
        url = f"{self.base_url}{endpoint}"
        attempts = self.retry_count + 1
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                self._apply_rate_limit()
                response = self.session.get(url, params=params, timeout=self.timeout_sec)
                self._last_request_at = time.monotonic()

                if response.status_code == 200:
                    return response.json().get("data", {})

                retryable = response.status_code == 429 or response.status_code >= 500
                try:
                    error_msg = response.json().get("status", {}).get("error_message", response.text)
                except ValueError:
                    error_msg = response.text

                if retryable and attempt < attempts:
                    time.sleep(self.retry_backoff_sec * attempt)
                    continue

                raise RuntimeError(f"CMC API Error ({response.status_code}): {error_msg}")
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= attempts:
                    break
                time.sleep(self.retry_backoff_sec * attempt)

        if last_error is not None:
            raise RuntimeError(f"CMC API transport error after {attempts} attempts: {last_error}") from last_error
        raise RuntimeError("CMC API request failed without a detailed error.")

    def get_id_map(self, symbols: List[str]) -> Dict[str, int]:
        uncached = [symbol for symbol in symbols if symbol not in self._symbol_to_id_cache]

        if uncached:
            data = self._request("/v1/cryptocurrency/map", {"symbol": ",".join(uncached)})
            if isinstance(data, list):
                sorted_data = sorted(
                    data,
                    key=lambda item: (
                        item.get("rank") is None,
                        item.get("rank") if item.get("rank") is not None else 999999,
                    ),
                )
                for item in sorted_data:
                    symbol = item["symbol"]
                    if symbol in uncached and symbol not in self._symbol_to_id_cache:
                        self._symbol_to_id_cache[symbol] = item["id"]

        return {
            symbol: self._symbol_to_id_cache.get(symbol)
            for symbol in symbols
            if self._symbol_to_id_cache.get(symbol) is not None
        }

    def get_quotes(self, symbols: List[str]) -> Dict[str, AssetQuote]:
        id_map = self.get_id_map(symbols)
        ids = list(id_map.values())
        if not ids:
            return {}

        data = self._request("/v3/cryptocurrency/quotes/latest", {"id": ",".join(map(str, ids))})
        if isinstance(data, list):
            data = {
                str(item.get("id")): item
                for item in data
                if isinstance(item, dict) and item.get("id") is not None
            }
        result = {}
        for symbol, cmc_id in id_map.items():
            info = data.get(str(cmc_id))
            if not info:
                continue
            quote_block = info.get("quote")
            if isinstance(quote_block, dict):
                quote = quote_block["USD"]
            elif isinstance(quote_block, list):
                usd_quote = next(
                    (
                        item for item in quote_block
                        if isinstance(item, dict) and item.get("symbol") == "USD"
                    ),
                    None,
                )
                if usd_quote is None:
                    continue
                quote = usd_quote
            else:
                continue
            result[symbol] = AssetQuote(
                id=cmc_id,
                symbol=symbol,
                price=quote["price"],
                market_cap=quote["market_cap"],
                volume_24h=quote.get("volume_24h", 0),
                percent_change_1h=quote.get("percent_change_1h", 0),
                percent_change_24h=quote.get("percent_change_24h", 0),
                percent_change_7d=quote.get("percent_change_7d", 0),
                percent_change_30d=quote.get("percent_change_30d", 0),
            )
        return result

    def get_historical_ohlcv(self, symbol: str, days: int = 90) -> pd.DataFrame:
        id_map = self.get_id_map([symbol])
        if symbol not in id_map:
            raise ValueError(f"Could not resolve CMC ID for {symbol}")

        cmc_id = id_map[symbol]
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        data = self._request(
            "/v3/cryptocurrency/quotes/historical",
            {
                "id": cmc_id,
                "interval": "1d",
                "time_start": start_time.strftime("%Y-%m-%d"),
                "time_end": end_time.strftime("%Y-%m-%d"),
            },
        )

        bars = []
        quote_container = None
        if isinstance(data, dict):
            if str(cmc_id) in data:
                quote_container = data[str(cmc_id)]
            elif "quotes" in data:
                quote_container = data

        quote_points = quote_container.get("quotes", []) if isinstance(quote_container, dict) else []
        for item in quote_points:
            quote = item.get("quote", {}).get("USD", {})
            timestamp = (
                item.get("timestamp")
                or item.get("time_open")
                or quote.get("timestamp")
                or quote.get("last_updated")
            )
            close_price = quote.get("price")
            if timestamp is None or close_price is None:
                continue

            bars.append(
                {
                    "timestamp": pd.to_datetime(timestamp),
                    "open": close_price,
                    "high": close_price,
                    "low": close_price,
                    "close": close_price,
                    "volume": _coalesce_value(quote.get("volume_24h"), quote.get("volume"), 0.0),
                }
            )

        df = pd.DataFrame(bars)
        if not df.empty:
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)
        return df

    def get_global_metrics(self) -> GlobalMetrics:
        data = self._request("/v1/global-metrics/quotes/latest")
        if "quote" in data and "USD" in data["quote"]:
            quote = data["quote"]["USD"]
            return GlobalMetrics(
                total_market_cap=quote.get("total_market_cap", 0),
                btc_dominance=data.get("btc_dominance", 0),
                eth_dominance=data.get("eth_dominance", 0),
            )
        return GlobalMetrics(total_market_cap=0, btc_dominance=0, eth_dominance=0)

    def get_fear_greed(self) -> Optional[FearGreedEntry]:
        data = self._request("/v3/fear-and-greed/latest")
        if not data:
            return None
        return FearGreedEntry(
            timestamp=datetime.fromtimestamp(int(data.get("timestamp", time.time()))),
            value=data.get("value", 50),
            classification=data.get("value_classification", "Neutral"),
        )

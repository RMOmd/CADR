import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from cadr.config import CMC_API_BASE_URL, CMC_API_KEY
from cadr.data.models import OHLCVBar, AssetQuote, GlobalMetrics, FearGreedEntry


def _coalesce_value(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


class CMCClient:
    """Client for CoinMarketCap REST API."""
    
    def __init__(self, api_key: str = CMC_API_KEY, base_url: str = CMC_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json"
            })
            
        self._symbol_to_id_cache = {}
            
    def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a rate-limited request to the CMC API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        
        # Simple rate limit handling (50 req/min for free tier)
        time.sleep(1.2)
        
        if response.status_code != 200:
            # Raise exception with API error message if available
            try:
                error_msg = response.json().get('status', {}).get('error_message', response.text)
                raise Exception(f"CMC API Error ({response.status_code}): {error_msg}")
            except ValueError:
                response.raise_for_status()
                
        return response.json().get('data', {})
        
    def get_id_map(self, symbols: List[str]) -> Dict[str, int]:
        """Resolve symbols to CMC IDs."""
        uncached = [s for s in symbols if s not in self._symbol_to_id_cache]
        
        if uncached:
            endpoint = "/v1/cryptocurrency/map"
            params = {"symbol": ",".join(uncached)}
            data = self._request(endpoint, params)
            
            # API returns a list of matching coins. We take the highest rank one for each symbol.
            if isinstance(data, list):
                # Sort by rank to prioritize major coins (e.g. SOL = Solana, not some random token)
                sorted_data = sorted(
                    data,
                    key=lambda x: (
                        x.get('rank') is None,
                        x.get('rank') if x.get('rank') is not None else 999999
                    )
                )
                for item in sorted_data:
                    sym = item['symbol']
                    if sym in uncached and sym not in self._symbol_to_id_cache:
                        self._symbol_to_id_cache[sym] = item['id']
                        
        return {sym: self._symbol_to_id_cache.get(sym) for sym in symbols if self._symbol_to_id_cache.get(sym) is not None}

    def get_quotes(self, symbols: List[str]) -> Dict[str, AssetQuote]:
        """Get latest quotes for a list of symbols."""
        id_map = self.get_id_map(symbols)
        ids = list(id_map.values())
        
        if not ids:
            return {}
            
        endpoint = "/v3/cryptocurrency/quotes/latest"
        params = {"id": ",".join(map(str, ids))}
        data = self._request(endpoint, params)
        
        result = {}
        for sym, cmc_id in id_map.items():
            str_id = str(cmc_id)
            if str_id in data:
                info = data[str_id]
                quote = info['quote']['USD']
                
                result[sym] = AssetQuote(
                    id=cmc_id,
                    symbol=sym,
                    price=quote['price'],
                    market_cap=quote['market_cap'],
                    volume_24h=quote.get('volume_24h', 0),
                    percent_change_1h=quote.get('percent_change_1h', 0),
                    percent_change_24h=quote.get('percent_change_24h', 0),
                    percent_change_7d=quote.get('percent_change_7d', 0),
                    percent_change_30d=quote.get('percent_change_30d', 0)
                )
        return result
        
    def get_historical_ohlcv(self, symbol: str, days: int = 90) -> pd.DataFrame:
        """Get historical daily price series as a DataFrame.

        We prefer quotes/historical because it is available on more CMC API plans
        than ohlcv/historical while still providing the close series this project uses.
        """
        id_map = self.get_id_map([symbol])
        if symbol not in id_map:
            raise ValueError(f"Could not resolve CMC ID for {symbol}")
            
        cmc_id = id_map[symbol]
        endpoint = "/v3/cryptocurrency/quotes/historical"
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        params = {
            "id": cmc_id,
            "interval": "1d",
            "time_start": start_time.strftime("%Y-%m-%d"),
            "time_end": end_time.strftime("%Y-%m-%d"),
        }
        
        data = self._request(endpoint, params)
        
        bars = []
        quote_container = None
        if isinstance(data, dict):
            if str(cmc_id) in data:
                quote_container = data[str(cmc_id)]
            elif "quotes" in data:
                quote_container = data

        quote_points = []
        if isinstance(quote_container, dict):
            quote_points = quote_container.get("quotes", [])

        for item in quote_points:
            quote = item.get("quote", {}).get("USD", {})
            timestamp = (
                item.get("timestamp") or
                item.get("time_open") or
                quote.get("timestamp") or
                quote.get("last_updated")
            )
            close_price = quote.get("price")
            if timestamp is None or close_price is None:
                continue

            volume = _coalesce_value(
                quote.get("volume_24h"),
                quote.get("volume"),
                0.0
            )
            bars.append({
                'timestamp': pd.to_datetime(timestamp),
                'open': close_price,
                'high': close_price,
                'low': close_price,
                'close': close_price,
                'volume': volume
            })
                
        df = pd.DataFrame(bars)
        if not df.empty:
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
        return df

    def get_global_metrics(self) -> GlobalMetrics:
        """Get global market metrics."""
        endpoint = "/v1/global-metrics/quotes/latest"
        data = self._request(endpoint)
        
        if 'quote' in data and 'USD' in data['quote']:
            quote = data['quote']['USD']
            return GlobalMetrics(
                total_market_cap=quote.get('total_market_cap', 0),
                btc_dominance=data.get('btc_dominance', 0),
                eth_dominance=data.get('eth_dominance', 0)
            )
        return GlobalMetrics(total_market_cap=0, btc_dominance=0, eth_dominance=0)
        
    def get_fear_greed(self) -> Optional[FearGreedEntry]:
        """Get current Fear and Greed index."""
        endpoint = "/v3/fear-and-greed/latest"
        data = self._request(endpoint)
        
        if data:
            return FearGreedEntry(
                timestamp=datetime.fromtimestamp(int(data.get('timestamp', time.time()))),
                value=data.get('value', 50),
                classification=data.get('value_classification', 'Neutral')
            )
        return None

from cadr.data.cmc_client import CMCClient


def test_get_quotes_uses_mocked_cmc_responses(monkeypatch):
    client = CMCClient(api_key="test-key", base_url="https://example.test")
    calls = []

    def fake_request(endpoint, params=None):
        calls.append((endpoint, params))
        if endpoint == "/v1/cryptocurrency/map":
            return [{"id": 1, "symbol": "BTC", "rank": 1}]
        if endpoint == "/v3/cryptocurrency/quotes/latest":
            return {
                "1": {
                    "quote": {
                        "USD": {
                            "price": 65000.0,
                            "market_cap": 1_200_000_000_000.0,
                            "volume_24h": 25_000_000_000.0,
                            "percent_change_1h": 0.5,
                            "percent_change_24h": 1.2,
                            "percent_change_7d": 4.8,
                            "percent_change_30d": 9.1
                        }
                    }
                }
            }
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr(client, "_request", fake_request)

    quotes = client.get_quotes(["BTC"])

    assert "BTC" in quotes
    assert quotes["BTC"].price == 65000.0
    assert calls[0][0] == "/v1/cryptocurrency/map"
    assert calls[1][0] == "/v3/cryptocurrency/quotes/latest"


def test_get_id_map_handles_none_rank_and_prefers_ranked_asset(monkeypatch):
    client = CMCClient(api_key="test-key", base_url="https://example.test")

    def fake_request(endpoint, params=None):
        if endpoint == "/v1/cryptocurrency/map":
            return [
                {"id": 999, "symbol": "SOL", "rank": None},
                {"id": 5426, "symbol": "SOL", "rank": 5},
            ]
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr(client, "_request", fake_request)

    id_map = client.get_id_map(["SOL"])

    assert id_map["SOL"] == 5426


def test_get_historical_ohlcv_uses_quotes_historical_shape(monkeypatch):
    client = CMCClient(api_key="test-key", base_url="https://example.test")

    def fake_request(endpoint, params=None):
        if endpoint == "/v1/cryptocurrency/map":
            return [{"id": 1, "symbol": "BTC", "rank": 1}]
        if endpoint == "/v3/cryptocurrency/quotes/historical":
            return {
                "1": {
                    "quotes": [
                        {
                            "timestamp": "2024-01-01T00:00:00.000Z",
                            "quote": {
                                "USD": {
                                    "price": 42000.0,
                                    "volume_24h": 10_000_000.0,
                                    "market_cap": 800_000_000_000.0,
                                }
                            },
                        },
                        {
                            "timestamp": "2024-01-02T00:00:00.000Z",
                            "quote": {
                                "USD": {
                                    "price": 43000.0,
                                    "volume_24h": 12_000_000.0,
                                    "market_cap": 820_000_000_000.0,
                                }
                            },
                        },
                    ]
                }
            }
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr(client, "_request", fake_request)

    df = client.get_historical_ohlcv("BTC", days=2)

    assert list(df["close"]) == [42000.0, 43000.0]
    assert list(df["open"]) == [42000.0, 43000.0]
    assert list(df["volume"]) == [10_000_000.0, 12_000_000.0]

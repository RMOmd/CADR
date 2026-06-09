import pytest

from cadr.data.cmc_client import CMCClient


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def test_cmc_client_retries_retryable_http_errors(monkeypatch):
    attempts = {"count": 0}

    def fake_get(url, params=None, timeout=None):
        attempts["count"] += 1
        if attempts["count"] < 3:
            return FakeResponse(500, {"status": {"error_message": "temporary"}})
        return FakeResponse(200, {"data": {"1": {"quote": {"USD": {"price": 100, "market_cap": 1, "volume_24h": 1}}}}})

    client = CMCClient(api_key="test-key", retry_count=2, retry_backoff_sec=0.0, min_interval_sec=0.0)
    client._symbol_to_id_cache["BTC"] = 1
    monkeypatch.setattr(client.session, "get", fake_get)

    result = client.get_quotes(["BTC"])

    assert attempts["count"] == 3
    assert result["BTC"].price == 100


def test_cmc_client_requires_api_key_before_request():
    client = CMCClient(api_key=None, retry_count=0, min_interval_sec=0.0)

    with pytest.raises(ValueError, match="CMC_API_KEY"):
        client.get_global_metrics()


def test_cmc_client_accepts_list_shape_for_quotes_payload(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return FakeResponse(
            200,
            {
                "data": [
                    {
                        "id": 1,
                        "quote": {
                            "USD": {
                                "price": 101,
                                "market_cap": 11,
                                "volume_24h": 7,
                                "percent_change_1h": 0.1,
                                "percent_change_24h": 0.2,
                                "percent_change_7d": 0.3,
                                "percent_change_30d": 0.4,
                            }
                        },
                    }
                ]
            },
        )

    client = CMCClient(api_key="test-key", retry_count=0, min_interval_sec=0.0)
    client._symbol_to_id_cache["BTC"] = 1
    monkeypatch.setattr(client.session, "get", fake_get)

    result = client.get_quotes(["BTC"])

    assert result["BTC"].price == 101

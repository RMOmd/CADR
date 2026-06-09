from itertools import combinations
from typing import Any, Dict, Iterable, List, Optional

import cadr.config as cfg
from cadr.agent.models import AssetContext, MarketContextSnapshot
from cadr.analysis.regime import classify_regime
from cadr.data.models import DivergenceSignal, GlobalMetrics, StrategySpec
from cadr.strategy.generator import generate_strategy


def _coalesce(*values: Any, default: Any = None) -> Any:
    for value in values:
        if value is not None:
            return value
    return default


def _read_nested(mapping: Any, *paths: Iterable[str], default: Any = None) -> Any:
    for path in paths:
        current = mapping
        found = True
        for key in path:
            if not isinstance(current, dict) or key not in current:
                found = False
                break
            current = current[key]
        if found and current is not None:
            return current
    return default


def _extract_headlines(items: Optional[List[Dict[str, Any]]]) -> List[str]:
    if not items:
        return []

    headlines = []
    for item in items[:5]:
        title = _coalesce(
            item.get("title"),
            item.get("headline"),
            item.get("name"),
        )
        if title:
            headlines.append(str(title))
    return headlines


def build_asset_context(
    search_result: Dict[str, Any],
    quote_payload: Dict[str, Any],
    technical_payload: Optional[Dict[str, Any]] = None,
    info_payload: Optional[Dict[str, Any]] = None,
    news_payload: Optional[List[Dict[str, Any]]] = None,
) -> AssetContext:
    quote = _coalesce(
        _read_nested(quote_payload, ("quote", "USD")),
        _read_nested(quote_payload, ("quotes", "USD")),
        quote_payload,
        default={},
    )

    technical_payload = technical_payload or {}
    info_payload = info_payload or {}

    return AssetContext(
        id=int(search_result["id"]),
        symbol=search_result["symbol"],
        name=_coalesce(search_result.get("name"), info_payload.get("name")),
        price=float(_coalesce(quote.get("price"), quote_payload.get("price"), default=0.0)),
        market_cap=float(_coalesce(quote.get("market_cap"), quote_payload.get("market_cap"), default=0.0)),
        volume_24h=float(_coalesce(quote.get("volume_24h"), quote_payload.get("volume_24h"), default=0.0)),
        percent_change_1h=float(_coalesce(quote.get("percent_change_1h"), quote_payload.get("percent_change_1h"), default=0.0)),
        percent_change_24h=float(_coalesce(quote.get("percent_change_24h"), quote_payload.get("percent_change_24h"), default=0.0)),
        percent_change_7d=float(_coalesce(quote.get("percent_change_7d"), quote_payload.get("percent_change_7d"), default=0.0)),
        percent_change_30d=float(_coalesce(quote.get("percent_change_30d"), quote_payload.get("percent_change_30d"), default=0.0)),
        rsi=_coalesce(
            _read_nested(technical_payload, ("rsi",)),
            _read_nested(technical_payload, ("indicators", "rsi")),
        ),
        macd_signal=_coalesce(
            _read_nested(technical_payload, ("macd", "signal")),
            _read_nested(technical_payload, ("indicators", "macd_signal")),
            _read_nested(technical_payload, ("signals", "macd")),
        ),
        thesis_tags=list(_coalesce(info_payload.get("tags"), info_payload.get("categories"), default=[])),
        latest_news=_extract_headlines(news_payload),
    )


def build_market_snapshot(
    global_metrics_payload: Dict[str, Any],
    derivatives_payload: Optional[Dict[str, Any]] = None,
    marketcap_ta_payload: Optional[Dict[str, Any]] = None,
    narratives_payload: Optional[List[Dict[str, Any]]] = None,
    macro_events_payload: Optional[List[Dict[str, Any]]] = None,
) -> MarketContextSnapshot:
    derivatives_payload = derivatives_payload or {}
    marketcap_ta_payload = marketcap_ta_payload or {}

    global_usd = _coalesce(
        _read_nested(global_metrics_payload, ("quote", "USD")),
        global_metrics_payload,
        default={},
    )

    narratives = []
    for item in narratives_payload or []:
        label = _coalesce(item.get("name"), item.get("title"), item.get("narrative"))
        if label:
            narratives.append(str(label))

    macro_events = []
    for item in macro_events_payload or []:
        label = _coalesce(item.get("title"), item.get("event"), item.get("name"))
        if label:
            macro_events.append(str(label))

    return MarketContextSnapshot(
        btc_dominance=float(_coalesce(global_metrics_payload.get("btc_dominance"), default=0.0)),
        eth_dominance=float(_coalesce(global_metrics_payload.get("eth_dominance"), default=0.0)),
        total_market_cap=float(_coalesce(global_usd.get("total_market_cap"), global_metrics_payload.get("total_market_cap"), default=0.0)),
        total_volume_24h=_coalesce(global_usd.get("total_volume_24h"), global_metrics_payload.get("total_volume_24h")),
        altcoin_season_index=_coalesce(global_metrics_payload.get("altcoin_season_index"), global_metrics_payload.get("altcoin_season")),
        fear_greed_index=_coalesce(global_metrics_payload.get("fear_greed_index"), _read_nested(global_metrics_payload, ("fear_and_greed", "value"))),
        marketcap_rsi=_coalesce(_read_nested(marketcap_ta_payload, ("rsi",)), _read_nested(marketcap_ta_payload, ("indicators", "rsi"))),
        marketcap_macd_signal=_coalesce(
            _read_nested(marketcap_ta_payload, ("macd", "signal")),
            _read_nested(marketcap_ta_payload, ("signals", "macd")),
        ),
        open_interest_change_24h=_coalesce(
            derivatives_payload.get("open_interest_change_24h"),
            _read_nested(derivatives_payload, ("open_interest", "change_24h")),
        ),
        funding_bias=_coalesce(
            derivatives_payload.get("funding_bias"),
            _read_nested(derivatives_payload, ("funding_rates", "bias")),
        ),
        trending_narratives=narratives,
        macro_events=macro_events,
    )


def _shared_tags(asset_a: AssetContext, asset_b: AssetContext) -> List[str]:
    return sorted(set(asset_a.thesis_tags).intersection(asset_b.thesis_tags))


def _direction_from_proxy(asset_a: AssetContext, asset_b: AssetContext, z_proxy: float) -> str:
    if z_proxy > 0:
        return f"long_{asset_b.symbol}_short_{asset_a.symbol}"
    return f"long_{asset_a.symbol}_short_{asset_b.symbol}"


def _macd_alignment_score(asset: AssetContext) -> float:
    if not asset.macd_signal:
        return 0.0
    value = asset.macd_signal.lower()
    if "bull" in value:
        return 0.35
    if "bear" in value:
        return -0.35
    return 0.0


def _agent_divergence_proxy(asset_a: AssetContext, asset_b: AssetContext) -> Dict[str, Any]:
    perf_gap = (
        (asset_a.percent_change_7d - asset_b.percent_change_7d) * 0.55 +
        (asset_a.percent_change_24h - asset_b.percent_change_24h) * 0.30 +
        (asset_a.percent_change_30d - asset_b.percent_change_30d) * 0.15
    )
    rsi_gap = 0.0
    if asset_a.rsi is not None and asset_b.rsi is not None:
        rsi_gap = (asset_a.rsi - asset_b.rsi) / 12.0

    macd_gap = _macd_alignment_score(asset_a) - _macd_alignment_score(asset_b)
    shared_narratives = _shared_tags(asset_a, asset_b)
    shared_tag_bonus = min(len(shared_narratives), 3) * 0.2

    z_proxy = (perf_gap / 4.5) + rsi_gap + macd_gap
    conviction = min(5, max(1, int(abs(z_proxy) / 0.75) + 1))

    return {
        "z_proxy": round(z_proxy, 2),
        "conviction": conviction,
        "perf_gap_24h": round(asset_a.percent_change_24h - asset_b.percent_change_24h, 2),
        "perf_gap_7d": round(asset_a.percent_change_7d - asset_b.percent_change_7d, 2),
        "perf_gap_30d": round(asset_a.percent_change_30d - asset_b.percent_change_30d, 2),
        "rsi_gap": round(rsi_gap * 12.0, 2),
        "shared_narratives": shared_narratives,
        "shared_tag_bonus": shared_tag_bonus,
    }


def select_best_agent_signal(asset_contexts: List[AssetContext]) -> DivergenceSignal:
    if len(asset_contexts) < 2:
        raise ValueError("At least two assets are required to build an agent-driven pair trade signal.")

    candidate_signals: List[DivergenceSignal] = []
    for asset_a, asset_b in combinations(asset_contexts, 2):
        metrics = _agent_divergence_proxy(asset_a, asset_b)
        z_proxy = metrics["z_proxy"]
        if abs(z_proxy) < cfg.Z_SCORE_ENTRY_THRESHOLD:
            continue

        candidate_signals.append(DivergenceSignal(
            asset_a=asset_a.symbol,
            asset_b=asset_b.symbol,
            z_score=z_proxy,
            direction=_direction_from_proxy(asset_a, asset_b, z_proxy),
            conviction_score=metrics["conviction"],
            metadata={
                "signal_method": "cmc_agent_hub_multifactor_proxy",
                "proxy_inputs": metrics,
                "source": "cmc_agent_hub",
                "supporting_news": {
                    asset_a.symbol: asset_a.latest_news[:3],
                    asset_b.symbol: asset_b.latest_news[:3],
                },
            },
        ))

    if not candidate_signals:
        raise ValueError("CMC Agent Hub inputs did not produce a high-conviction divergence signal.")

    return max(candidate_signals, key=lambda signal: (abs(signal.z_score), signal.conviction_score))


def generate_agent_strategy(
    asset_contexts: List[AssetContext],
    market_snapshot: MarketContextSnapshot,
) -> StrategySpec:
    best_signal = select_best_agent_signal(asset_contexts)
    regime = classify_regime(
        GlobalMetrics(
            total_market_cap=market_snapshot.total_market_cap,
            btc_dominance=market_snapshot.btc_dominance,
            eth_dominance=market_snapshot.eth_dominance,
            altcoin_season_index=market_snapshot.altcoin_season_index,
            fear_greed_index=market_snapshot.fear_greed_index,
        )
    )

    spec = generate_strategy(
        [best_signal],
        regime,
        {
            "btc_dominance": market_snapshot.btc_dominance,
            "eth_dominance": market_snapshot.eth_dominance,
            "fear_greed_index": market_snapshot.fear_greed_index,
            "altcoin_season_index": market_snapshot.altcoin_season_index,
            "regime": regime.value,
            "source": market_snapshot.source,
        },
    )

    asset_map = {asset.symbol: asset for asset in asset_contexts}
    asset_a = asset_map[best_signal.asset_a]
    asset_b = asset_map[best_signal.asset_b]
    proxy_inputs = best_signal.metadata["proxy_inputs"]

    spec.strategy["execution_style"] = "agent_hub_mcp_first"
    spec.analysis["signal_method"] = "cmc_agent_hub_multifactor_proxy"
    spec.analysis["rsi_divergence"] = {
        asset_a.symbol: asset_a.rsi,
        asset_b.symbol: asset_b.rsi,
    }
    spec.analysis["macd_context"] = {
        asset_a.symbol: asset_a.macd_signal,
        asset_b.symbol: asset_b.macd_signal,
        "marketcap": market_snapshot.marketcap_macd_signal,
    }
    spec.analysis["evidence"] = {
        "performance_gap_pct": {
            "1h": round(asset_a.percent_change_1h - asset_b.percent_change_1h, 2),
            "24h": proxy_inputs["perf_gap_24h"],
            "7d": proxy_inputs["perf_gap_7d"],
            "30d": proxy_inputs["perf_gap_30d"],
        },
        "shared_narratives": proxy_inputs["shared_narratives"],
        "supporting_news": best_signal.metadata["supporting_news"],
    }
    spec.rules["entry"] = (
        f"Agent Hub divergence proxy >= {cfg.Z_SCORE_ENTRY_THRESHOLD} "
        f"with confirming RSI/MACD context on {asset_a.symbol}/{asset_b.symbol}"
    )
    spec.rules["take_profit"] = "Mean reversion in relative performance spread or RSI normalization"
    spec.rules["invalidation"] = (
        "Macro/event regime flips, negative funding shock, or proxy divergence expands beyond stop threshold"
    )
    spec.market_context.update({
        "trending_narratives": market_snapshot.trending_narratives,
        "macro_events": market_snapshot.macro_events,
        "derivatives": {
            "open_interest_change_24h": market_snapshot.open_interest_change_24h,
            "funding_bias": market_snapshot.funding_bias,
        },
        "marketcap_technical_analysis": {
            "rsi": market_snapshot.marketcap_rsi,
            "macd_signal": market_snapshot.marketcap_macd_signal,
        },
    })

    return spec

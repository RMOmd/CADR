import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cadr.skill_hub import generate_cadr_strategy_from_skill_hub


def main():
    spec = generate_cadr_strategy_from_skill_hub(
        base_asset="BTC",
        quote_assets=["ETH"],
        lookback_days=90,
    )
    print(json.dumps(spec.model_dump(), indent=2))


if __name__ == "__main__":
    main()

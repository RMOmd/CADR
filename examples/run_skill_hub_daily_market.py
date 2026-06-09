import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cadr.skill_hub import SkillHubClient, discover_skill, run_daily_market_overview_preview


def main():
    client = SkillHubClient()
    candidate = discover_skill(
        client,
        query="daily market overview",
        unique_name="daily_market_overview",
        top_k=10,
    )
    overview = run_daily_market_overview_preview(client)

    payload = {
        "server_info": client.server_info,
        "skill": {
            "unique_name": candidate.unique_name,
            "input_schema": candidate.input_schema,
            "result_type": candidate.result_type,
            "domain": candidate.domain,
        },
        "overview": overview.model_dump(),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

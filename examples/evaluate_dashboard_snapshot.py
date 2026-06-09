import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cadr.dashboard.snapshots import evaluate_dashboard_snapshot
from cadr.data.cmc_client import CMCClient


def main() -> None:
    snapshot_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    result = evaluate_dashboard_snapshot(snapshot_path, CMCClient())
    print(json.dumps({
        "snapshot_path": result["snapshot_path"],
        "evaluated_at": result["evaluated_at"],
        "summary": result["summary"],
        "output_path": result["output_path"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

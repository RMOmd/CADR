import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cadr.dashboard.snapshots import export_dashboard_snapshot
from cadr.dashboard.storage import DashboardStorage
from cadr.data.cmc_client import CMCClient


def main() -> None:
    storage = DashboardStorage("log/cadr_dashboard.db")
    result = export_dashboard_snapshot(storage, CMCClient(), db_path="log/cadr_dashboard.db")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

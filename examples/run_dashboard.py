import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvicorn

import cadr.config as cfg
from cadr.dashboard import create_app


def main():
    uvicorn.run(
        create_app(),
        host=cfg.CADR_DASHBOARD_HOST,
        port=cfg.CADR_DASHBOARD_PORT,
    )


if __name__ == "__main__":
    main()

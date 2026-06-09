from threading import Event, Thread
from typing import Optional

import cadr.config as cfg
from cadr.dashboard.service import DashboardService


class DashboardMonitor:
    def __init__(self, service: DashboardService, poll_interval_sec: Optional[int] = None):
        self.service = service
        self.poll_interval_sec = max(2, int(poll_interval_sec or cfg.CADR_MONITOR_POLL_SEC))
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run, name="cadr-dashboard-monitor", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.poll_interval_sec + 2)

    def _run(self) -> None:
        while not self._stop_event.wait(self.poll_interval_sec):
            try:
                settings = self.service.storage.get_monitor_settings()
                if not settings["enabled"]:
                    continue
                next_run_at = settings.get("next_run_at")
                if next_run_at:
                    from datetime import datetime

                    due = datetime.fromisoformat(next_run_at.replace("Z", "+00:00"))
                    now = datetime.now(due.tzinfo)
                    if now < due:
                        continue
                self.service.run_monitor_cycle(force=False)
            except Exception:
                # Keep the monitor alive even if one cycle fails.
                continue

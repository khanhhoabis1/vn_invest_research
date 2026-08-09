"""Worker + Scheduler — chay connector theo lich bang APScheduler.

Chay: python -m vnir.worker.main
Doc lich tu chinh connector (thuoc tinh `schedule`, dang cron).
"""
from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("worker")

ROOT = Path(os.environ.get("VNIR_ROOT", "/workspace"))
if not (ROOT / "vnir").exists():
    ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

RUNLOG = ROOT / "logs" / "runs.jsonl"


def record(info: dict) -> None:
    RUNLOG.parent.mkdir(parents=True, exist_ok=True)
    with RUNLOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(info, ensure_ascii=False) + "\n")


def run_connector(key: str) -> None:
    from vnir.connectors.registry import get
    log.info("Bat dau chay connector %s", key)
    try:
        info = get(key)().run()
    except Exception as exc:  # noqa: BLE001
        log.exception("Connector %s hong", key)
        info = {"source_id": key, "status": "failed", "error": str(exc),
                "ended_at": _dt.datetime.now(_dt.timezone.utc).isoformat()}
    record(info)
    level = log.info if info.get("status") == "success" else log.error
    level("Ket thuc %s: %s (%s dong)", key, info.get("status"), info.get("rows", 0))


def main() -> int:
    from vnir.connectors.registry import list_connectors

    sched = BackgroundScheduler(timezone=os.environ.get("TZ", "Asia/Ho_Chi_Minh"))
    conns = list_connectors()
    if not conns:
        log.warning("Chua co connector nao duoc dang ky")
    for c in conns:
        try:
            sched.add_job(
                run_connector, CronTrigger.from_crontab(c["schedule"]),
                args=[c["key"]], id=c["key"], replace_existing=True,
                misfire_grace_time=3600, coalesce=True, max_instances=1,
            )
            log.info("Da len lich %-32s cron=%s  (rui ro phap ly: %s)",
                     c["key"], c["schedule"], c["legal_risk"])
        except Exception as exc:  # noqa: BLE001
            log.error("Khong len lich duoc %s: %s", c["key"], exc)

    sched.start()
    log.info("Worker san sang — %d connector da len lich. Ctrl+C de dung.", len(sched.get_jobs()))

    stop = False

    def _handle(signum, frame):  # noqa: ANN001, ARG001
        nonlocal stop
        log.info("Nhan tin hieu %s, dang dung...", signum)
        stop = True

    signal.signal(signal.SIGTERM, _handle)
    signal.signal(signal.SIGINT, _handle)
    while not stop:
        time.sleep(2)
    sched.shutdown(wait=True)
    log.info("Worker da dung sach")
    return 0


if __name__ == "__main__":
    sys.exit(main())

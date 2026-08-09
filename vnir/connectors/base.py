"""Lop co so cho moi connector thu thap du lieu.

Hop dong bat buoc (P2 trong CHARTER):
  - Bronze BAT BIEN: moi lan tai la mot thu muc dt=<ngay> moi, khong ghi de.
  - Moi lan tai deu sinh _manifest.json: url, http_status, sha256, fetched_at, rows.
  - Idempotent: chay lai cung ngay -> khong nhan doi du lieu.
  - Ton trong nguon: User-Agent dinh danh, delay, retry co backoff.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger("connector")

ROOT = Path(os.environ.get("VNIR_ROOT", "/workspace"))
if not ROOT.exists():
    ROOT = Path(__file__).resolve().parent.parent.parent

BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"

USER_AGENT = os.environ.get(
    "VNIR_USER_AGENT",
    "vn-invest-research/0.1 (nghien cuu ca nhan; lien he qua GitHub khanhhoabis1)",
)


@dataclass
class FetchResult:
    """Ket qua mot lan tai — luon di kem bang chung nguon goc."""
    content: bytes
    url: str
    http_status: int
    fetched_at: str
    content_type: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


class ConnectorError(RuntimeError):
    pass


class BaseConnector:
    """Ke thua lop nay de viet connector moi.

    Bat buoc khai bao:
        source_id, dataset, title, schedule, legal_risk
    Bat buoc cai dat:
        fetch() -> FetchResult | list[FetchResult]
        parse(results) -> list[dict]        # ban ghi da chuan hoa
    """

    source_id: str = ""
    dataset: str = ""
    title: str = ""
    homepage: str = ""
    schedule: str = "0 7 * * *"          # cron
    legal_risk: str = "low"               # low | medium | high
    requires_key: bool = False
    freshness_sla_days: int = 45          # QA canh bao neu du lieu cu hon nguong nay
    unit: str = ""
    description: str = ""

    timeout: float = 30.0
    max_retries: int = 3
    delay_between_requests: float = 1.0

    def __init__(self, dry_run: bool = False) -> None:
        if not self.source_id or not self.dataset:
            raise ConnectorError(f"{type(self).__name__}: thieu source_id hoac dataset")
        self.dry_run = dry_run
        self.log = logging.getLogger(f"connector.{self.source_id}.{self.dataset}")

    # ------------------------------------------------------------ http
    def http_get(self, url: str, **kwargs: Any) -> FetchResult:
        """GET co retry/backoff, luon tra ve bang chung nguon."""
        headers = {"User-Agent": USER_AGENT, **kwargs.pop("headers", {})}
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    resp = client.get(url, headers=headers, **kwargs)
                if resp.status_code >= 500:
                    raise ConnectorError(f"HTTP {resp.status_code} tu {url}")
                resp.raise_for_status()
                time.sleep(self.delay_between_requests)
                return FetchResult(
                    content=resp.content,
                    url=str(resp.url),
                    http_status=resp.status_code,
                    fetched_at=_dt.datetime.now(_dt.UTC).isoformat(),
                    content_type=resp.headers.get("content-type", ""),
                )
            except Exception as exc:
                last_exc = exc
                wait = 2 ** attempt
                self.log.warning("Lan %d/%d that bai (%s), doi %ds", attempt, self.max_retries, exc, wait)
                if attempt < self.max_retries:
                    time.sleep(wait)
        raise ConnectorError(f"Tai that bai sau {self.max_retries} lan: {url}") from last_exc

    # ------------------------------------------------------------ bronze
    def bronze_dir(self, dt: str | None = None) -> Path:
        dt = dt or _dt.date.today().isoformat()
        return BRONZE / self.source_id / self.dataset / f"dt={dt}"

    def write_bronze(self, results: list[FetchResult], rows: int = 0) -> Path:
        """Ghi du lieu tho + manifest. KHONG BAO GIO sua file da co."""
        d = self.bronze_dir()
        if self.dry_run:
            self.log.info("[dry-run] se ghi %d file vao %s", len(results), d)
            return d
        d.mkdir(parents=True, exist_ok=True)
        files = []
        for i, r in enumerate(results):
            ext = "json" if "json" in r.content_type else ("csv" if "csv" in r.content_type else "bin")
            if r.content[:1] in (b"{", b"["):
                ext = "json"
            name = f"data_{i:02d}.{ext}" if len(results) > 1 else f"data.{ext}"
            (d / name).write_bytes(r.content)
            files.append({
                "file": name, "url": r.url, "http_status": r.http_status,
                "sha256": r.sha256, "bytes": len(r.content),
                "content_type": r.content_type, "fetched_at": r.fetched_at,
            })
        manifest = {
            "source_id": self.source_id, "dataset": self.dataset, "title": self.title,
            "homepage": self.homepage, "legal_risk": self.legal_risk,
            "connector": type(self).__name__,
            "fetched_at": _dt.datetime.now(_dt.UTC).isoformat(),
            "rows": rows, "files": files,
        }
        (d / "_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log.info("Da ghi bronze: %s (%d file, %d dong)", d, len(files), rows)
        return d

    # ------------------------------------------------------------ silver
    def write_silver(self, records: list[dict], domain: str = "macro") -> Path | None:
        import pandas as pd
        if not records:
            self.log.warning("Khong co ban ghi nao de ghi silver")
            return None
        df = pd.DataFrame(records)
        df["_source_id"] = self.source_id
        df["_dataset"] = self.dataset
        df["_ingested_at"] = _dt.datetime.now(_dt.UTC).isoformat()
        out = SILVER / domain / f"{self.source_id}__{self.dataset}.parquet"
        if self.dry_run:
            self.log.info("[dry-run] se ghi %d dong vao %s", len(df), out)
            return out
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out, index=False)
        self.log.info("Da ghi silver: %s (%d dong)", out, len(df))
        return out

    # ------------------------------------------------------------ hooks
    def fetch(self) -> FetchResult | list[FetchResult]:
        raise NotImplementedError

    def parse(self, results: list[FetchResult]) -> list[dict]:
        raise NotImplementedError

    # ------------------------------------------------------------ run
    def run(self) -> dict:
        started = _dt.datetime.now(_dt.UTC)
        info: dict[str, Any] = {
            "source_id": self.source_id, "dataset": self.dataset,
            "started_at": started.isoformat(), "status": "running",
        }
        try:
            raw = self.fetch()
            results = raw if isinstance(raw, list) else [raw]
            records = self.parse(results)
            self.write_bronze(results, rows=len(records))
            self.write_silver(records)
            info.update(status="success", rows=len(records),
                        urls=[r.url for r in results],
                        http_status=[r.http_status for r in results])
        except Exception as exc:
            self.log.exception("Connector that bai")
            info.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        finally:
            ended = _dt.datetime.now(_dt.UTC)
            info["ended_at"] = ended.isoformat()
            info["duration_seconds"] = round((ended - started).total_seconds(), 2)
        return info

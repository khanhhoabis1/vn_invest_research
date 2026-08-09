"""API FastAPI — phuc vu ca Build plane va Ops plane.

Chay: uvicorn vnir.api.main:app --host 0.0.0.0 --port 8000
Tai lieu tu sinh: http://localhost:8000/docs  (AI agent doc OpenAPI o day)
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(os.environ.get("VNIR_ROOT", "/workspace"))
if not (ROOT / "specs").exists():
    ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

app = FastAPI(
    title="VN Invest Research Platform API",
    description=(
        "API cuc bo cho nen tang du lieu kinh te Viet Nam.\n\n"
        "- **Build plane** (`/specs`, `/intake`): quan ly yeu cau va nang cap nen tang\n"
        "- **Ops plane** (`/sources`, `/runs`, `/query`): van hanh thu thap va tra cuu du lieu"
    ),
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


# ==================================================================== health
@app.get("/health", tags=["he-thong"])
def health() -> dict:
    """Kiem tra suc khoe — dung boi docker healthcheck."""
    return {
        "status": "ok",
        "time": _dt.datetime.now(_dt.UTC).isoformat(),
        "root": str(ROOT),
        "specs_dir_exists": (ROOT / "specs").exists(),
        "data_dir_exists": (ROOT / "data").exists(),
    }


# ==================================================================== BUILD PLANE
class SpecOut(BaseModel):
    id: str
    title: str
    status: str
    extra: dict[str, Any] = Field(default_factory=dict)


def _load_specs(kind: str) -> list[dict]:
    from spec_lib import load_all
    return load_all(kind.upper())


@app.get("/specs/{kind}", tags=["build-plane"])
def list_specs(kind: str, status: str | None = None) -> list[dict]:
    """Liet ke REQ / COMP / TASK / ASSESS / BRIEF."""
    kind = kind.upper()
    if kind not in {"REQ", "COMP", "TASK", "ASSESS", "BRIEF"}:
        raise HTTPException(400, "kind khong hop le")
    items = _load_specs(kind)
    if status:
        items = [s for s in items if s.get("status") == status]
    return sorted(items, key=lambda x: x["id"])


@app.get("/specs/item/{spec_id}", tags=["build-plane"])
def get_spec(spec_id: str) -> dict:
    """Lay chi tiet mot spec theo ID."""
    from spec_lib import load
    try:
        return load(spec_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


class ConcludeIn(BaseModel):
    ket_luan: str
    bang_chung: list[str] | None = None


@app.post("/specs/assess/{spec_id}/conclude", tags=["build-plane"])
def conclude_assess(spec_id: str, body: ConcludeIn) -> dict:
    """Ghi nhan ket luan tham dinh. BAT BUOC co bang chung neu chua dap ung/dap ung mot phan."""
    from spec_lib import load, save
    try:
        s = load(spec_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    if s.get("ket_luan") not in ("chua_tham_dinh", None):
        pass  # cho phep ghi de (vi du sua ket luan)
    if body.ket_luan in ("chua_dap_ung", "dap_ung_mot_phan") and not s.get("bang_chung") and not body.bang_chung:
        raise HTTPException(400, "Thieu bang chung that — khong duoc phong doan")
    s["ket_luan"] = body.ket_luan
    s["status"] = "xong"
    if body.bang_chung:
        s.setdefault("bang_chung", []).append({
            "kiem_tra": body.bang_chung[0],
            "ket_qua": body.bang_chung[1] if len(body.bang_chung) > 1 else "",
            "ngay": _dt.date.today().isoformat(),
        })
    save(s)
    return {"ok": True, "id": spec_id, "ket_luan": body.ket_luan}


@app.get("/specs/validate", tags=["build-plane"])
def validate_specs() -> dict:
    """Kiem dinh toan bo spec (3 tang: schema, lien ket, luat AI)."""
    from spec_validate import validate_all
    errors, stats = validate_all()
    return {"ok": not errors, "errors": errors, "stats": stats}


class IntakeIn(BaseModel):
    text: str = Field(..., min_length=10, description="Yeu cau bang tieng Viet, van xuoi")
    requested_by: str = "nha-dau-tu"
    channel: str = "ui-build"
    kind: str | None = None          # "brief" neu la de bai phan tich (Track 2)
    loai: str | None = None
    doi_tuong: list[str] | None = None
    cau_hoi: list[str] | None = None


@app.post("/intake", tags=["build-plane"])
def create_intake(body: IntakeIn) -> dict:
    """Nhan yeu cau tho. Neu kind=brief thi tao luon BRIEF (Track 2),
    nguoc lai luu vao intake/inbox de PO phan ra thanh REQ (Track 1)."""
    from spec_lib import next_id, save, today
    if body.kind == "brief":
        bid = next_id("BRIEF")
        spec = {
            "id": bid, "title": body.text[:70], "status": "moi", "created": today(),
            "origin": {"raw_request": body.text, "requested_by": body.requested_by,
                       "requested_at": today(), "channel": body.channel},
            "loai_phan_tich": body.loai or "khac",
            "doi_tuong": body.doi_tuong or [],
            "cau_hoi_dau_tu": body.cau_hoi or [],
        }
        save(spec)
        return {"ok": True, "brief_id": bid, "next": "Doi dau tu kiem ke du lieu"}
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    d = ROOT / "intake" / "inbox"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{ts}-{body.channel}.md"
    f.write_text(
        f"---\nreceived: {_dt.datetime.now().isoformat()}\n"
        f"requested_by: {body.requested_by}\nchannel: {body.channel}\nstatus: new\n---\n\n"
        f"{body.text}\n",
        encoding="utf-8",
    )
    return {"ok": True, "file": str(f.relative_to(ROOT)), "next": "PO phan ra thanh REQ"}


@app.get("/intake", tags=["build-plane"])
def list_intake() -> list[dict]:
    """Danh sach yeu cau tho chua xu ly."""
    d = ROOT / "intake" / "inbox"
    if not d.exists():
        return []
    out = []
    for f in sorted(d.glob("*.md"), reverse=True):
        text = f.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1].strip() if text.startswith("---") else text
        out.append({"file": f.name, "preview": body[:300],
                    "modified": _dt.datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
    return out


# ==================================================================== OPS PLANE
@app.get("/sources", tags=["ops-plane"])
def list_sources() -> list[dict]:
    """Danh sach connector da dang ky."""
    from vnir.connectors.registry import list_connectors
    return list_connectors()


@app.get("/runs", tags=["ops-plane"])
def list_runs(limit: int = 50) -> list[dict]:
    """Lich su cac lan chay thu thap."""
    f = ROOT / "logs" / "runs.jsonl"
    if not f.exists():
        return []
    lines = f.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(x) for x in lines[-limit:]][::-1]


class RunIn(BaseModel):
    key: str = Field(..., description="Dinh dang: <source_id>.<dataset>")
    dry_run: bool = False


@app.post("/runs", tags=["ops-plane"])
def trigger_run(body: RunIn) -> dict:
    """Chay mot connector ngay lap tuc."""
    from vnir.connectors.registry import get
    try:
        cls = get(body.key)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    info = cls(dry_run=body.dry_run).run()
    if not body.dry_run:
        logf = ROOT / "logs" / "runs.jsonl"
        logf.parent.mkdir(parents=True, exist_ok=True)
        with logf.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(info, ensure_ascii=False) + "\n")
    return info


@app.get("/datasets", tags=["ops-plane"])
def list_datasets() -> list[dict]:
    """Cac bang du lieu da co trong silver/gold."""
    out = []
    for layer in ("silver", "gold"):
        d = ROOT / "data" / layer
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.parquet")):
            st = p.stat()
            out.append({
                "layer": layer, "name": p.stem,
                "path": str(p.relative_to(ROOT)),
                "size_kb": round(st.st_size / 1024, 1),
                "modified": _dt.datetime.fromtimestamp(st.st_mtime).isoformat(),
            })
    return out


class QueryIn(BaseModel):
    sql: str = Field(..., description="Cau SQL DuckDB. Chi cho phep SELECT.")
    limit: int = 1000


@app.post("/query", tags=["ops-plane"])
def run_query(body: QueryIn) -> dict:
    """Truy van du lieu bang DuckDB (chi doc)."""
    sql = body.sql.strip().rstrip(";")
    low = sql.lower()
    forbidden = ("insert", "update", "delete", "drop", "create", "alter", "attach", "copy", "install")
    if not low.startswith(("select", "with", "describe", "show", "summarize")):
        raise HTTPException(400, "Chi cho phep SELECT / WITH / DESCRIBE / SHOW / SUMMARIZE")
    if any(f" {k} " in f" {low} " for k in forbidden):
        raise HTTPException(400, f"Cau lenh chua tu khoa bi cam: {forbidden}")
    import duckdb
    con = duckdb.connect(":memory:")
    try:
        con.execute(f"SET file_search_path='{ROOT}'")
        df = con.execute(f"SELECT * FROM ({sql}) LIMIT {int(body.limit)}").fetchdf()
        return {"ok": True, "rows": len(df), "columns": list(df.columns),
                "data": json.loads(df.to_json(orient="records", date_format="iso"))}
    except Exception as exc:
        raise HTTPException(400, f"Loi SQL: {exc}") from exc
    finally:
        con.close()

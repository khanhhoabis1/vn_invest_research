"""Phan kiem dinh (validate) cho he thong spec.

Kiem 3 tang:
  1. JSON Schema  - dung cau truc
  2. Toan ven lien ket - REQ<->COMP<->TASK tro dung nhau
  3. Luat cho AI  - task phai du nho va du ro de model nho thuc thi
"""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from spec_lib import KINDS, ROOT, SCHEMAS, load_all

MAX_SMALL_MODEL_TOKENS = 6000
MAX_FILES_PER_TASK = 8


def _schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate_schemas() -> list[str]:
    errs: list[str] = []
    for kind, cfg in KINDS.items():
        validator = Draft202012Validator(_schema(cfg["schema"]))
        for spec in load_all(kind):
            for e in sorted(validator.iter_errors(spec), key=lambda x: list(x.path)):
                loc = ".".join(str(p) for p in e.path) or "(root)"
                errs.append(f"[SCHEMA] {spec.get('id', '?')} :: {loc}: {e.message}")
    return errs


def validate_links() -> list[str]:
    errs: list[str] = []
    reqs = {s["id"]: s for s in load_all("REQ")}
    comps = {s["id"]: s for s in load_all("COMP")}
    tasks = {s["id"]: s for s in load_all("TASK")}

    for cid, c in comps.items():
        for rid in c.get("requirements", []):
            if rid not in reqs:
                errs.append(f"[LINK] {cid} tro toi {rid} khong ton tai")
        for dep in c.get("depends_on", []):
            if dep not in comps:
                errs.append(f"[LINK] {cid} phu thuoc {dep} khong ton tai")

    for tid, t in tasks.items():
        if t["req_id"] not in reqs:
            errs.append(f"[LINK] {tid} tro toi req {t['req_id']} khong ton tai")
        if t["comp_id"] not in comps:
            errs.append(f"[LINK] {tid} tro toi comp {t['comp_id']} khong ton tai")
        for dep in t.get("depends_on", []):
            if dep not in tasks:
                errs.append(f"[LINK] {tid} phu thuoc {dep} khong ton tai")

    for rid, r in reqs.items():
        for cid in r.get("components", []):
            if cid not in comps:
                errs.append(f"[LINK] {rid} tro toi {cid} khong ton tai")
        sb = r.get("superseded_by")
        if sb and sb not in reqs:
            errs.append(f"[LINK] {rid} superseded_by {sb} khong ton tai")
    return errs


def validate_ai_rules() -> list[str]:
    """Luat bao dam model AI NHO van thuc thi duoc."""
    errs: list[str] = []
    for t in load_all("TASK"):
        tid = t["id"]
        budget = t.get("context_budget_tokens", 0)
        if budget > MAX_SMALL_MODEL_TOKENS and t.get("model_hint") != "large":
            errs.append(
                f"[AI] {tid} context_budget_tokens={budget} > {MAX_SMALL_MODEL_TOKENS}. "
                "Che nho task hoac dat model_hint: large"
            )
        files = t.get("files_to_touch", [])
        if len(files) > MAX_FILES_PER_TASK:
            errs.append(f"[AI] {tid} dung toi {len(files)} file (toi da {MAX_FILES_PER_TASK}). Che nho task.")
        writable = [f for f in files if f.get("action") in {"create", "modify", "delete"}]
        if not writable:
            errs.append(f"[AI] {tid} khong co file nao duoc ghi -> task khong lam gi ca")
        if not t.get("verify_commands"):
            errs.append(f"[AI] {tid} thieu verify_commands -> khong the chung minh hoan thanh")
        for f in files:
            p = f.get("path", "")
            if f.get("action") in {"modify", "delete", "read-only"} and "*" not in p:
                if not (ROOT / p).exists():
                    errs.append(f"[AI] {tid} tham chieu file khong ton tai: {p} (action={f.get('action')})")
        if t.get("status") in {"approved", "in_progress"} and len(t.get("intent", "")) < 40:
            errs.append(f"[AI] {tid} intent qua ngan/mo ho de model tu thuc thi")
    return errs


def validate_all() -> tuple[list[str], dict]:
    errs = validate_schemas() + validate_links() + validate_ai_rules()
    stats = {k: len(load_all(k)) for k in KINDS}
    return errs, stats

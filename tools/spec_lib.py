"""Thu vien loi cho he thong spec REQ/COMP/TASK.

Dung chung boi specctl.py, ghsync.py, api va CI.
Khong phu thuoc gi ngoai pyyaml + jsonschema.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
from pathlib import Path

import yaml

# ---------------------------------------------------------------- paths
ROOT = Path(os.environ.get("VNIR_ROOT", Path(__file__).resolve().parent.parent))
SPECS = ROOT / "specs"
SCHEMAS = SPECS / "_schemas"

KINDS = {
    # Track 1 — phat trien nen tang
    "ASSESS": {"dir": SPECS / "assessments", "schema": "assess.schema.json"},
    "REQ": {"dir": SPECS / "requirements", "schema": "requirement.schema.json"},
    "COMP": {"dir": SPECS / "components", "schema": "component.schema.json"},
    "TASK": {"dir": SPECS / "tasks", "schema": "task.schema.json"},
    # Track 2 — thu thap du lieu & phan tich dau tu
    "BRIEF": {"dir": SPECS / "briefs", "schema": "brief.schema.json"},
}

ID_RE = re.compile(r"^(ASSESS|REQ|COMP|TASK|BRIEF)-(\d{4})$")


def today() -> str:
    return _dt.date.today().isoformat()


def slugify(text: str, maxlen: int = 48) -> str:
    """Bo dau tieng Viet, ve dang a-z0-9-."""
    table = {
        "aàáạảãâầấậẩẫăằắặẳẵ": "a", "eèéẹẻẽêềếệểễ": "e",
        "iìíịỉĩ": "i", "oòóọỏõôồốộổỗơờớợởỡ": "o",
        "uùúụủũưừứựửữ": "u", "yỳýỵỷỹ": "y", "dđ": "d",
    }
    out = []
    for ch in text.lower():
        mapped = ch
        for group, rep in table.items():
            if ch in group:
                mapped = rep
                break
        out.append(mapped)
    s = "".join(out)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:maxlen].strip("-") or "untitled"


# ---------------------------------------------------------------- io
def ensure_dirs() -> None:
    for cfg in KINDS.values():
        cfg["dir"].mkdir(parents=True, exist_ok=True)


def kind_of(spec_id: str) -> str:
    m = ID_RE.match(spec_id)
    if not m:
        raise ValueError(f"ID khong hop le: {spec_id!r} (can dang REQ-0001)")
    return m.group(1)


def path_for(spec_id: str) -> Path | None:
    """Tim file cua mot spec id (ten file co the kem slug)."""
    d = KINDS[kind_of(spec_id)]["dir"]
    if not d.exists():
        return None
    hits = sorted(d.glob(f"{spec_id}*.yaml"))
    return hits[0] if hits else None


def load(spec_id: str) -> dict:
    p = path_for(spec_id)
    if p is None:
        raise FileNotFoundError(f"Khong tim thay spec {spec_id}")
    with p.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_all(kind: str) -> list[dict]:
    d = KINDS[kind]["dir"]
    if not d.exists():
        return []
    items = []
    for p in sorted(d.glob("*.yaml")):
        with p.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and data.get("id"):
            items.append(data)
    return items


def save(spec: dict, *, rename_slug: bool = False) -> Path:
    spec_id = spec["id"]
    kind = kind_of(spec_id)
    d = KINDS[kind]["dir"]
    d.mkdir(parents=True, exist_ok=True)
    existing = path_for(spec_id)
    if existing is not None and not rename_slug:
        target = existing
    else:
        title = spec.get("title") or spec.get("name") or spec_id
        target = d / f"{spec_id}-{slugify(title)}.yaml"
        if existing is not None and existing != target:
            existing.unlink()
    spec.setdefault("created", today())
    spec["updated"] = today()
    with target.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(spec, fh, allow_unicode=True, sort_keys=False, width=100)
    return target


def next_id(kind: str) -> str:
    """Cap ID moi. KHONG bao gio tai su dung ID cu (quet ca file da xoa qua ledger)."""
    kind = kind.upper()
    used = set()
    d = KINDS[kind]["dir"]
    if d.exists():
        for p in d.glob(f"{kind}-*.yaml"):
            m = re.match(rf"^{kind}-(\d{{4}})", p.name)
            if m:
                used.add(int(m.group(1)))
    ledger = SPECS / "_ledger.json"
    if ledger.exists():
        data = json.loads(ledger.read_text(encoding="utf-8"))
        used |= {int(x) for x in data.get(kind, [])}
    n = 1
    while n in used:
        n += 1
    used.add(n)
    data = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else {}
    data[kind] = sorted(used)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return f"{kind}-{n:04d}"

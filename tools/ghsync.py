#!/usr/bin/env python3
"""ghsync — dong bo spec (REQ/COMP/TASK) voi GitHub Issue.

Vi sao can: spec la nguon su that nam trong git, nhung con nguoi va CI lam viec
tren GitHub Issue. Cong cu nay giu hai ben khop nhau MOT CHIEU:

    spec (nguon su that)  ---->  GitHub Issue (ban hien thi)

Khong bao gio doc nguoc tu Issue ve ghi de spec — tranh mat du lieu khi ai do
sua tay tren web.

Lenh:
    python tools/ghsync.py push            # day moi spec chua co issue len
    python tools/ghsync.py push --dry-run  # xem truoc, khong goi API
    python tools/ghsync.py push --id REQ-0001
    python tools/ghsync.py status          # doi chieu spec <-> issue

Yeu cau: `gh` da dang nhap (gh auth status).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spec_lib import kind_of, load_all, path_for, save

OK, BAD, WARN, DIM = "\033[92m", "\033[91m", "\033[93m", "\033[2m"
END = "\033[0m"

# Nhan mau tren GitHub — tao tu dong neu chua co
LABELS = {
    "spec:req":   ("0E8A16", "Yeu cau — can gi va vi sao"),
    "spec:comp":  ("1D76DB", "Thanh phan — sua o dau"),
    "spec:task":  ("5319E7", "Nhiem vu — lam chinh xac gi"),
    "plane:build": ("D93F0B", "Thuoc Build plane (nang cap nen tang)"),
    "plane:ops":   ("FBCA04", "Thuoc Ops plane (van hanh du lieu)"),
    "ai-ready":   ("C2E0C6", "Model AI nho co the tu thuc thi"),
    "blocked":    ("B60205", "Dang bi chan boi spec khac"),
}


def run(cmd: list[str], check: bool = True) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"Lenh that bai: {' '.join(cmd[:3])}…\n{p.stderr.strip()}")
    return p.returncode, (p.stdout or p.stderr).strip()


def require_gh() -> None:
    if not shutil.which("gh"):
        sys.exit(f"{BAD}Chua cai `gh`. Cai bang: brew install gh{END}")
    rc, _ = run(["gh", "auth", "status"], check=False)
    if rc != 0:
        sys.exit(f"{BAD}`gh` chua dang nhap. Chay: gh auth login{END}")


def ensure_labels() -> None:
    """Tao nhan con thieu. Bo qua neu da ton tai."""
    rc, out = run(["gh", "label", "list", "--limit", "100", "--json", "name"], check=False)
    existing = {x["name"] for x in json.loads(out)} if rc == 0 and out.startswith("[") else set()
    for name, (color, desc) in LABELS.items():
        if name in existing:
            continue
        rc, _ = run(["gh", "label", "create", name, "--color", color,
                     "--description", desc], check=False)
        print(f"  {OK}+{END} tao nhan {name}" if rc == 0 else f"  {DIM}~ bo qua {name}{END}")


def labels_for(spec: dict) -> list[str]:
    k = kind_of(spec["id"])
    out = [f"spec:{k.lower()}"]
    plane = spec.get("plane")
    if plane in ("build", "ops"):
        out.append(f"plane:{plane}")
    elif plane == "both":
        out += ["plane:build", "plane:ops"]
    if k == "TASK" and spec.get("model_size_hint") in ("small", "tiny"):
        out.append("ai-ready")
    if spec.get("blocked_by"):
        out.append("blocked")
    return out


def body_for(spec: dict, path: Path | None) -> str:
    """Sinh phan than issue. Ngan gon — spec day du nam trong git."""
    sid, k = spec["id"], kind_of(spec["id"])
    rel = path.name if path else f"{sid}.yaml"
    L = [f"> 🔗 **Nguon su that: `specs/.../{rel}`** trong repo.",
         "> Issue nay chi la **ban hien thi**. Sua spec trong git, dung sua o day.", ""]

    if spec.get("rationale"):
        L += ["## Vi sao can", "", spec["rationale"], ""]
    if spec.get("description"):
        L += ["## Mo ta", "", spec["description"], ""]

    if k == "REQ":
        if spec.get("origin", {}).get("raw_request"):
            L += ["## Nguyen van yeu cau", "",
                  "```", spec["origin"]["raw_request"].strip(), "```", ""]
        if spec.get("acceptance_criteria"):
            L += ["## Tieu chi nghiem thu", ""]
            L += [f"- [ ] {c}" for c in spec["acceptance_criteria"]] + [""]
    elif k == "TASK":
        if spec.get("files_to_change"):
            L += ["## File duoc phep sua", ""]
            L += [f"- `{f}`" for f in spec["files_to_change"]] + [""]
        if spec.get("files_forbidden"):
            L += ["## File CAM dung", ""]
            L += [f"- `{f}`" for f in spec["files_forbidden"]] + [""]
        if spec.get("verify_command"):
            L += ["## Lenh kiem chung", "", "```bash", spec["verify_command"], "```", ""]

    meta = []
    for key in ("status", "plane", "owner_role", "model_size_hint"):
        if spec.get(key) is not None:
            meta.append(f"`{key}: {spec[key]}`")
    pr = spec.get("priority")
    if isinstance(pr, dict):
        meta.append(f"`diem uu tien: {pr.get('score', '?')}` "
                    f"(tac dong {pr.get('impact', '?')}/5 · "
                    f"tu tin {pr.get('confidence', '?')}/5 · "
                    f"cong suc {pr.get('effort', '?')}/5)")
    elif pr is not None:
        meta.append(f"`priority: {pr}`")
    if meta:
        L += ["---", "", " · ".join(meta), ""]

    for key, title in (("depends_on", "Phu thuoc"), ("blocked_by", "Bi chan boi"),
                       ("parent", "Thuoc ve")):
        v = spec.get(key)
        if v:
            v = v if isinstance(v, list) else [v]
            L.append(f"**{title}:** " + ", ".join(f"`{x}`" for x in v))

    L += ["", f"{DIM}<!-- ghsync:{sid} -->{END}".replace(DIM, "").replace(END, "")]
    return "\n".join(L)


def cmd_push(args: argparse.Namespace) -> int:
    require_gh()
    print("Kiem tra nhan GitHub…")
    if not args.dry_run:
        ensure_labels()

    specs = [s for k in ("REQ", "COMP", "TASK") for s in load_all(k)]
    if args.id:
        specs = [s for s in specs if s["id"] == args.id.upper()]
        if not specs:
            sys.exit(f"{BAD}Khong tim thay spec {args.id}{END}")

    created = skipped = 0
    for spec in sorted(specs, key=lambda s: s["id"]):
        sid = spec["id"]
        if spec.get("github", {}).get("issue"):
            print(f"  {DIM}~ {sid} da co issue #{spec['github']['issue']}{END}")
            skipped += 1
            continue

        path = path_for(sid)
        title = f"[{sid}] {spec.get('title') or spec.get('name', '')}"
        body = body_for(spec, path)
        labels = labels_for(spec)

        if args.dry_run:
            print(f"  {WARN}DRY{END} se tao: {title}")
            print(f"      nhan: {', '.join(labels)}")
            created += 1
            continue

        cmd = ["gh", "issue", "create", "--title", title, "--body", body]
        for lb in labels:
            cmd += ["--label", lb]
        rc, out = run(cmd, check=False)
        if rc != 0:
            print(f"  {BAD}✗ {sid}: {out[:120]}{END}")
            continue

        num = out.rstrip("/").split("/")[-1]
        spec.setdefault("github", {})["issue"] = int(num)
        spec["github"]["url"] = out.strip()
        save(spec)
        print(f"  {OK}✓{END} {sid} → issue #{num}")
        created += 1

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Tao {created} issue, bo qua {skipped}.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    require_gh()
    specs = [s for k in ("REQ", "COMP", "TASK") for s in load_all(k)]
    rc, out = run(["gh", "issue", "list", "--limit", "200", "--state", "all",
                   "--json", "number,title,state"], check=False)
    issues = json.loads(out) if rc == 0 and out.startswith("[") else []
    by_num = {i["number"]: i for i in issues}

    print(f"\n{'SPEC':<12} {'ISSUE':>7}  {'TRANG THAI GH':<10} TIEU DE")
    print("-" * 76)
    linked = orphan = 0
    for s in sorted(specs, key=lambda x: x["id"]):
        num = s.get("github", {}).get("issue")
        title = (s.get("title") or s.get("name", ""))[:40]
        if num:
            gh_state = by_num.get(num, {}).get("state", "KHONG THAY")
            mark = OK if gh_state == "OPEN" else (DIM if gh_state == "CLOSED" else BAD)
            print(f"{s['id']:<12} {'#'+str(num):>7}  {mark}{gh_state:<10}{END} {title}")
            linked += 1
        else:
            print(f"{s['id']:<12} {'—':>7}  {WARN}chua day{END}    {title}")
            orphan += 1
    print("-" * 76)
    print(f"Da lien ket: {linked}  |  Chua day len GitHub: {orphan}\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Dong bo spec voi GitHub Issue (mot chieu)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("push", help="Day spec chua co issue len GitHub")
    p.add_argument("--dry-run", action="store_true", help="Xem truoc, khong goi API")
    p.add_argument("--id", help="Chi day mot spec cu the")
    p.set_defaults(func=cmd_push)

    p = sub.add_parser("status", help="Doi chieu spec voi issue")
    p.set_defaults(func=cmd_status)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

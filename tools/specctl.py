#!/usr/bin/env python3
"""specctl - quan ly vong doi spec REQ/COMP/TASK.

Dung duoc ca tren host lan trong container.

  specctl new req   --title "..." --problem "..." --outcome "..."
  specctl new comp  --title "..." --kind service --paths a b
  specctl new task  --title "..." --req REQ-0001 --comp COMP-0001
  specctl validate                 # kiem dinh toan bo (CI dung lenh nay)
  specctl list [req|comp|task] [--status approved]
  specctl show TASK-0001           # in goi thuc thi cho AI
  specctl set TASK-0001 status=done
  specctl index                    # sinh specs/SPEC-INDEX.md
  specctl next                     # goi y task ke tiep AI nen lam
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml
from spec_lib import SPECS, ensure_dirs, kind_of, load, load_all, next_id, save, today
from spec_validate import validate_all

OK, BAD, WARN = "\033[92m", "\033[91m", "\033[93m"
DIM, END = "\033[2m", "\033[0m"


# ------------------------------------------------------------------ new
def cmd_new(a: argparse.Namespace) -> int:
    ensure_dirs()
    kind = {"req": "REQ", "comp": "COMP", "task": "TASK"}[a.kind]
    sid = next_id(kind)

    if kind == "REQ":
        spec = {
            "id": sid, "title": a.title, "status": "draft", "created": today(),
            "origin": {"channel": a.channel, "raw_request": a.raw or a.title,
                       "requested_by": a.by or "unknown"},
            "problem": a.problem or "TODO: mo ta van de hien tai (>=20 ky tu)",
            "outcome": a.outcome or "TODO: mo ta ket qua mong muon (>=20 ky tu)",
            "priority": {"impact": a.impact, "confidence": a.confidence, "effort": a.effort,
                         "score": round(a.impact * a.confidence / max(a.effort, 1), 2)},
            "acceptance": a.acceptance or ["TODO: tieu chi nghiem thu kiem chung duoc"],
            "plane": a.plane, "components": [], "tags": a.tags or [],
        }
        if a.question:
            spec["investment_question"] = a.question
    elif kind == "COMP":
        spec = {
            "id": sid, "name": a.title, "kind": a.comp_kind, "status": "planned",
            "created": today(), "owner_role": a.owner, "plane": a.plane_comp,
            "purpose": a.purpose or "TODO: muc dich cua component (>=15 ky tu)",
            "paths": a.paths or ["TODO/"], "tech": a.tech or [],
            "requirements": ([a.req] if a.req else []), "risk": a.risk,
        }
    else:
        spec = {
            "id": sid, "title": a.title, "status": "draft", "created": today(),
            "req_id": a.req, "comp_id": a.comp,
            "intent": a.intent or "TODO: mo ta chinh xac phai lam gi, viet cho model AI doc (>=20 ky tu)",
            "files_to_touch": [{"path": p, "action": "modify"} for p in (a.files or ["TODO"])],
            "forbidden": ["data/bronze/**", ".env", "specs/_ledger.json"],
            "acceptance": a.acceptance or ["TODO: tieu chi nghiem thu"],
            "verify_commands": a.verify or ["python tools/specctl.py validate"],
            "context_refs": a.context or [],
            "context_budget_tokens": a.budget, "model_hint": a.model,
            "estimate_minutes": a.minutes,
        }

    p = save(spec, rename_slug=True)
    print(f"{OK}Da tao {sid}{END} -> {p.relative_to(Path.cwd()) if str(p).startswith(str(Path.cwd())) else p}")
    print(f"{DIM}Sua file roi chay: python tools/specctl.py validate{END}")
    return 0


# ------------------------------------------------------------------ validate
def cmd_validate(a: argparse.Namespace) -> int:
    errs, stats = validate_all()
    tally = "  ".join(f"{k}={v}" for k, v in stats.items())
    if errs:
        print(f"{BAD}KIEM DINH THAT BAI{END} — {len(errs)} loi   ({tally})\n")
        for e in errs:
            print(f"  {BAD}x{END} {e}")
        return 1
    print(f"{OK}KIEM DINH OK{END} — moi spec hop le   ({tally})")
    return 0


# ------------------------------------------------------------------ list / show
def cmd_list(a: argparse.Namespace) -> int:
    kinds = [a.kind.upper()] if a.kind else ["REQ", "COMP", "TASK"]
    for kind in kinds:
        items = load_all(kind)
        if a.status:
            items = [s for s in items if s.get("status") == a.status]
        if not items:
            continue
        print(f"\n{kind} ({len(items)})")
        print("-" * 78)
        for s in sorted(items, key=lambda x: x["id"]):
            name = s.get("title") or s.get("name") or ""
            st = s.get("status", "?")
            colour = OK if st in {"done", "active", "approved"} else (WARN if st in {"draft", "planned"} else "")
            extra = ""
            if kind == "TASK":
                extra = f" {DIM}[{s.get('model_hint','?')}/{s.get('context_budget_tokens','?')}tok]{END}"
            print(f"  {s['id']}  {colour}{st:<12}{END} {name[:52]}{extra}")
    print()
    return 0


def cmd_show(a: argparse.Namespace) -> int:
    spec = load(a.id)
    if a.raw or kind_of(a.id) != "TASK":
        print(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, width=100))
        return 0

    req = load(spec["req_id"]) if spec.get("req_id") else {}
    comp = load(spec["comp_id"]) if spec.get("comp_id") else {}
    L = []
    L.append("=" * 78)
    L.append(f"GOI THUC THI — {spec['id']}: {spec['title']}")
    L.append("=" * 78)
    L.append(f"Trang thai : {spec.get('status')}   Model goi y: {spec.get('model_hint')}   "
             f"Ngan sach: {spec.get('context_budget_tokens')} token")
    L.append("")
    L.append(f"BOI CANH GOC ({spec.get('req_id')}): {req.get('title','?')}")
    if req.get("problem"):
        L.append(f"  Van de : {req['problem']}")
    if req.get("outcome"):
        L.append(f"  Mong doi: {req['outcome']}")
    L.append(f"COMPONENT ({spec.get('comp_id')}): {comp.get('name','?')} [{comp.get('kind','?')}]")
    for p in comp.get("paths", []):
        L.append(f"  - {p}")
    L.append("")
    L.append("VIEC PHAI LAM")
    L.append(f"  {spec.get('intent')}")
    L.append("")
    L.append("FILE DUOC PHEP SUA")
    for f in spec.get("files_to_touch", []):
        hint = f"  # {f['hint']}" if f.get("hint") else ""
        L.append(f"  [{f['action']:<9}] {f['path']}{hint}")
    if spec.get("forbidden"):
        L.append("")
        L.append("TUYET DOI KHONG DUNG VAO")
        for f in spec["forbidden"]:
            L.append(f"  ! {f}")
    if spec.get("interfaces"):
        L.append("")
        L.append("CHU KY PHAI TUAN THU")
        for i in spec["interfaces"]:
            L.append(f"  {i}")
    L.append("")
    L.append("TIEU CHI NGHIEM THU")
    for c in spec.get("acceptance", []):
        L.append(f"  [ ] {c}")
    L.append("")
    L.append("LENH VERIFY (phai chay that va pass)")
    for c in spec.get("verify_commands", []):
        L.append(f"  $ {c}")
    if spec.get("context_refs"):
        L.append("")
        L.append("DOC TRUOC")
        for c in spec["context_refs"]:
            L.append(f"  - {c}")
    L.append("=" * 78)
    print("\n".join(L))
    return 0


# ------------------------------------------------------------------ set
def cmd_set(a: argparse.Namespace) -> int:
    spec = load(a.id)
    for pair in a.pairs:
        if "=" not in pair:
            print(f"{BAD}Bo qua {pair!r} — can dang key=value{END}")
            continue
        k, v = pair.split("=", 1)
        if v.lower() in {"true", "false"}:
            val: object = v.lower() == "true"
        elif v.isdigit():
            val = int(v)
        elif "," in v:
            val = [x.strip() for x in v.split(",") if x.strip()]
        else:
            val = v
        cur = spec
        keys = k.split(".")
        for kk in keys[:-1]:
            cur = cur.setdefault(kk, {})
        cur[keys[-1]] = val
        print(f"{OK}{a.id}{END}  {k} = {val}")
    save(spec)
    return 0


# ------------------------------------------------------------------ index
def cmd_index(a: argparse.Namespace) -> int:
    reqs, comps, tasks = load_all("REQ"), load_all("COMP"), load_all("TASK")
    L = ["# CHI MUC SPEC — ban do 1 trang cho nguoi va AI", "",
         "> Sinh tu dong boi `python tools/specctl.py index`. **Khong sua tay.**",
         f"> Cap nhat: {today()}  |  REQ={len(reqs)}  COMP={len(comps)}  TASK={len(tasks)}", "",
         "Doc file nay truoc khi lam bat cu viec gi. Moi ID la vinh vien, khong tai su dung.", ""]

    L += ["## Yeu cau (REQ) — can gi & vi sao", "",
          "| ID | Tieu de | Trang thai | Uu tien | Mat phang | Component |",
          "|---|---|---|---|---|---|"]
    for s in sorted(reqs, key=lambda x: x["id"]):
        pr = s.get("priority", {})
        L.append(f"| `{s['id']}` | {s.get('title','')} | {s.get('status','')} | "
                 f"{pr.get('score','-')} | {s.get('plane','-')} | {', '.join(s.get('components', [])) or '-'} |")

    L += ["", "## Thanh phan (COMP) — sua o dau", "",
          "| ID | Ten | Loai | Trang thai | Chu | Duong dan chinh |", "|---|---|---|---|---|---|"]
    for s in sorted(comps, key=lambda x: x["id"]):
        paths = ", ".join(f"`{p}`" for p in s.get("paths", [])[:3])
        L.append(f"| `{s['id']}` | {s.get('name','')} | {s.get('kind','')} | {s.get('status','')} | "
                 f"{s.get('owner_role','')} | {paths} |")

    L += ["", "## Cong viec (TASK) — lam chinh xac gi", "",
          "| ID | Tieu de | Trang thai | REQ | COMP | Model | Token |", "|---|---|---|---|---|---|---|"]
    for s in sorted(tasks, key=lambda x: x["id"]):
        L.append(f"| `{s['id']}` | {s.get('title','')} | {s.get('status','')} | `{s.get('req_id','')}` | "
                 f"`{s.get('comp_id','')}` | {s.get('model_hint','-')} | {s.get('context_budget_tokens','-')} |")

    L += ["", "## Cach dung cho AI agent", "",
          "```bash",
          "python tools/specctl.py next              # task nao nen lam tiep",
          "python tools/specctl.py show TASK-0001    # goi thuc thi tu du",
          "python tools/specctl.py validate          # bat buoc pass truoc khi commit",
          "```", "",
          "Commit phai co trailer:", "", "```", "Task-Id: TASK-xxxx", "Req-Id: REQ-xxxx", "```", ""]

    out = SPECS / "SPEC-INDEX.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"{OK}Da sinh{END} {out}  ({len(reqs)} REQ, {len(comps)} COMP, {len(tasks)} TASK)")
    return 0


# ------------------------------------------------------------------ next
def cmd_next(a: argparse.Namespace) -> int:
    tasks = load_all("TASK")
    done = {t["id"] for t in tasks if t.get("status") == "done"}
    ready = []
    for t in tasks:
        if t.get("status") not in {"approved", "draft"}:
            continue
        if all(d in done for d in t.get("depends_on", [])):
            ready.append(t)
    if a.model:
        order = {"small": 0, "medium": 1, "large": 2}
        ready = [t for t in ready if order.get(t.get("model_hint", "medium"), 1) <= order[a.model]]
    if not ready:
        print(f"{WARN}Khong co task nao san sang.{END} Tao task moi hoac go block phu thuoc.")
        return 0
    ready.sort(key=lambda t: (t.get("status") != "approved", t.get("context_budget_tokens", 9999)))
    print(f"{OK}{len(ready)} task san sang{END} (de nhat truoc):\n")
    for t in ready[:10]:
        print(f"  {t['id']}  [{t.get('model_hint','?'):<6} {t.get('context_budget_tokens','?'):>5}tok]  {t.get('title','')}")
    print(f"\n{DIM}Xem chi tiet: python tools/specctl.py show {ready[0]['id']}{END}")
    return 0


# ------------------------------------------------------------------ cli
def main() -> int:
    ap = argparse.ArgumentParser(prog="specctl", description="Quan ly spec REQ/COMP/TASK")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="Tao spec moi")
    n.add_argument("kind", choices=["req", "comp", "task"])
    n.add_argument("--title", required=True)
    n.add_argument("--problem")
    n.add_argument("--outcome")
    n.add_argument("--question")
    n.add_argument("--raw")
    n.add_argument("--by")
    n.add_argument("--channel", default="cli",
                   choices=["ui-build", "cli", "intake-file", "chat", "cron", "incident"])
    n.add_argument("--impact", type=int, default=3)
    n.add_argument("--confidence", type=int, default=3)
    n.add_argument("--effort", type=int, default=3)
    n.add_argument("--plane", default="both", choices=["build", "ops", "both"])
    n.add_argument("--plane-comp", default="shared", choices=["build", "ops", "shared"])
    n.add_argument("--comp-kind", default="service",
                   choices=["service", "connector", "ui", "library", "schema", "pipeline", "infra", "docs", "workflow"])
    n.add_argument("--owner", default="ARCH", choices=["PO", "BA", "ARCH", "DE", "RES", "AIE", "QA", "DOC"])
    n.add_argument("--risk", default="low", choices=["low", "medium", "high"])
    n.add_argument("--purpose")
    n.add_argument("--paths", nargs="*")
    n.add_argument("--tech", nargs="*")
    n.add_argument("--req")
    n.add_argument("--comp")
    n.add_argument("--intent")
    n.add_argument("--files", nargs="*")
    n.add_argument("--verify", nargs="*")
    n.add_argument("--context", nargs="*")
    n.add_argument("--acceptance", nargs="*")
    n.add_argument("--tags", nargs="*")
    n.add_argument("--budget", type=int, default=2500)
    n.add_argument("--model", default="small", choices=["small", "medium", "large"])
    n.add_argument("--minutes", type=int, default=30)
    n.set_defaults(func=cmd_new)

    v = sub.add_parser("validate", help="Kiem dinh toan bo spec")
    v.set_defaults(func=cmd_validate)

    lst = sub.add_parser("list", help="Liet ke spec")
    lst.add_argument("kind", nargs="?", choices=["req", "comp", "task"])
    lst.add_argument("--status")
    lst.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="In goi thuc thi cho AI")
    s.add_argument("id")
    s.add_argument("--raw", action="store_true")
    s.set_defaults(func=cmd_show)

    st = sub.add_parser("set", help="Gan gia tri: specctl set TASK-0001 status=done")
    st.add_argument("id")
    st.add_argument("pairs", nargs="+")
    st.set_defaults(func=cmd_set)

    i = sub.add_parser("index", help="Sinh specs/SPEC-INDEX.md")
    i.set_defaults(func=cmd_index)

    nx = sub.add_parser("next", help="Goi y task ke tiep")
    nx.add_argument("--model", choices=["small", "medium", "large"])
    nx.set_defaults(func=cmd_next)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

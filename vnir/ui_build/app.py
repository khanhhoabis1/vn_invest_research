"""UI NHOM A — BUILD PLANE: Xuong nang cap nen tang.

Nguoi dung: nguoi dua yeu cau cai thien/nang cap, PO, kien truc su, AI agent.
Chay: streamlit run vnir/ui_build/app.py --server.port=8601
"""
from __future__ import annotations

import os
from pathlib import Path

import httpx
import streamlit as st

API = os.environ.get("VNIR_API", "http://api:8000")
ROOT = Path(os.environ.get("VNIR_ROOT", "/workspace"))

st.set_page_config(page_title="Build Plane — Nang cap nen tang",
                   page_icon="🛠", layout="wide")


def api_get(path: str, **params):
    try:
        r = httpx.get(f"{API}{path}", params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Khong goi duoc API {path}: {exc}")
        return None


def api_post(path: str, payload: dict):
    try:
        r = httpx.post(f"{API}{path}", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Khong goi duoc API {path}: {exc}")
        return None


# ---------------------------------------------------------------- header
st.title("🛠 Build Plane — Xuong nang cap nen tang")
st.caption("Nhom A · Noi tiep nhan yeu cau cai thien, phan ra thanh spec, dong bo GitHub. "
           "Xem du lieu da thu thap tai **Ops Plane :8602**.")

health = api_get("/health")
c1, c2, c3 = st.columns(3)
c1.metric("API", "OK" if health else "MAT KET NOI")
if health:
    c2.metric("Thu muc goc", health["root"])
    c3.metric("Spec sẵn sàng", "co" if health["specs_dir_exists"] else "chua")

tabs = st.tabs(["📥 Gui yeu cau", "📋 Yeu cau (REQ)", "🧩 Thanh phan (COMP)",
                "✅ Cong viec (TASK)", "🔍 Kiem dinh", "📖 Huong dan AI"])

# ---------------------------------------------------------------- tab: gui yeu cau
with tabs[0]:
    st.subheader("Gui yeu cau cai thien / nang cap nen tang")
    st.info("Viet bang tieng Viet binh thuong. He thong se luu nguyen van, "
            "sau do PO phan ra thanh REQ → COMP → TASK de AI thuc thi.")
    with st.form("intake"):
        text = st.text_area("Yeu cau cua ban", height=180,
                            placeholder="Vi du: Toi muon theo doi lai suat lien ngan hang hang ngay "
                                        "va canh bao khi tang qua 5%...")
        who = st.text_input("Nguoi yeu cau", value="nha-dau-tu")
        if st.form_submit_button("Gui yeu cau", type="primary"):
            if len(text.strip()) < 10:
                st.warning("Yeu cau qua ngan, hay mo ta ro hon.")
            else:
                res = api_post("/intake", {"text": text, "requested_by": who, "channel": "ui-build"})
                if res:
                    st.success(f"Da ghi nhan → `{res['file']}`")
                    st.caption("Buoc tiep theo: chay `python tools/specctl.py new req ...` "
                               "hoac de PO agent phan ra.")

    st.divider()
    st.subheader("Hop thu yeu cau chua xu ly")
    inbox = api_get("/intake") or []
    if not inbox:
        st.caption("Hop thu trong.")
    for item in inbox:
        with st.expander(f"{item['file']}  ·  {item['modified'][:16]}"):
            st.text(item["preview"])

# ---------------------------------------------------------------- tab: REQ
with tabs[1]:
    st.subheader("Yeu cau — can gi va vi sao")
    reqs = api_get("/specs/req") or []
    if reqs:
        st.dataframe(
            [{"ID": r["id"], "Tieu de": r["title"], "Trang thai": r["status"],
              "Uu tien": (r.get("priority") or {}).get("score"),
              "Mat phang": r.get("plane"), "Component": len(r.get("components", []))}
             for r in reqs],
            use_container_width=True, hide_index=True)
        pick = st.selectbox("Xem chi tiet", [r["id"] for r in reqs])
        detail = api_get(f"/specs/item/{pick}")
        if detail:
            cA, cB = st.columns(2)
            with cA:
                st.markdown("**Van de**"); st.write(detail.get("problem", "—"))
                st.markdown("**Cau hoi dau tu**"); st.write(detail.get("investment_question", "—"))
            with cB:
                st.markdown("**Ket qua mong doi**"); st.write(detail.get("outcome", "—"))
                st.markdown("**Tieu chi nghiem thu**")
                for a in detail.get("acceptance", []):
                    st.write(f"- {a}")
            st.markdown("**Nguyen van yeu cau goc** _(khong bao gio bi sua)_")
            st.code((detail.get("origin") or {}).get("raw_request", "—"), language=None)
    else:
        st.caption("Chua co REQ nao.")

# ---------------------------------------------------------------- tab: COMP
with tabs[2]:
    st.subheader("Thanh phan kien truc — sua o dau")
    comps = api_get("/specs/comp") or []
    if comps:
        st.dataframe(
            [{"ID": c["id"], "Ten": c["name"], "Loai": c["kind"], "Trang thai": c["status"],
              "Chu": c.get("owner_role"), "Mat phang": c.get("plane"),
              "Rui ro": c.get("risk"), "Duong dan": ", ".join(c.get("paths", [])[:2])}
             for c in comps],
            use_container_width=True, hide_index=True)
    else:
        st.caption("Chua co COMP nao.")

# ---------------------------------------------------------------- tab: TASK
with tabs[3]:
    st.subheader("Cong viec — goi thuc thi cho AI")
    tasks = api_get("/specs/task") or []
    if tasks:
        st.dataframe(
            [{"ID": t["id"], "Tieu de": t["title"], "Trang thai": t["status"],
              "REQ": t.get("req_id"), "COMP": t.get("comp_id"),
              "Model": t.get("model_hint"), "Token": t.get("context_budget_tokens")}
             for t in tasks],
            use_container_width=True, hide_index=True)
        pick = st.selectbox("Xem goi thuc thi", [t["id"] for t in tasks])
        d = api_get(f"/specs/item/{pick}")
        if d:
            st.markdown("**Viec phai lam**"); st.write(d.get("intent"))
            st.markdown("**File duoc phep sua**")
            for f in d.get("files_to_touch", []):
                st.write(f"- `{f['path']}` — **{f['action']}** {f.get('hint','')}")
            st.markdown("**Lenh verify**")
            st.code("\n".join(d.get("verify_commands", [])), language="bash")
    else:
        st.caption("Chua co TASK nao. Tao bang: `python tools/specctl.py new task ...`")

# ---------------------------------------------------------------- tab: kiem dinh
with tabs[4]:
    st.subheader("Kiem dinh spec (3 tang)")
    st.caption("Tang 1: JSON Schema · Tang 2: toan ven lien ket · Tang 3: luat cho model AI nho")
    if st.button("Chay kiem dinh", type="primary"):
        res = api_get("/specs/validate")
        if res:
            if res["ok"]:
                st.success(f"Tat ca hop le — {res['stats']}")
            else:
                st.error(f"{len(res['errors'])} loi")
                for e in res["errors"]:
                    st.write(f"- {e}")

# ---------------------------------------------------------------- tab: huong dan AI
with tabs[5]:
    st.subheader("Cach AI lam viec voi kho nay")
    st.markdown("""
**Quy trinh chuan cho bat ky AI agent nao (ke ca model 3B):**

```bash
python tools/specctl.py next --model small   # tim task vua suc
python tools/specctl.py show TASK-0001       # doc goi thuc thi tu du
# ... sua dung nhung file duoc liet ke ...
python tools/specctl.py validate             # bat buoc pass
git commit -m "feat(comp): ...

Task-Id: TASK-0001
Req-Id: REQ-0001"
```

**Vi sao model nho van lam duoc:**
- Moi TASK gioi han duoi 6.000 token ngu canh (CI chan neu vuot).
- TASK liet ke chinh xac file duoc sua va file cam dung.
- Moi TASK co lenh verify chay that de tu kiem chung.
- `specs/SPEC-INDEX.md` la ban do 1 trang, khong can quet ca repo.
- ID vinh vien khong tai su dung → truy vet nguoc ve yeu cau goc bat cu luc nao.
""")
    idx = ROOT / "specs" / "SPEC-INDEX.md"
    if idx.exists():
        with st.expander("Xem SPEC-INDEX.md"):
            st.markdown(idx.read_text(encoding="utf-8"))

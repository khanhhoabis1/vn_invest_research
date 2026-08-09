"""UI NHOM A — BUILD PLANE / TRACK 1: Phát triển nền tảng.

Nguoi dung: nguoi dua yeu cau cai thien/nang cap, PO, kien truc su, AI agent.
Chay: streamlit run vnir/ui_build/app.py --server.port=8601

Luong Track 1:
  Ban neu yeu cau -> ASSESS (doi phan tich tham dinh) -> REQ -> COMP -> TASK -> release
"""
from __future__ import annotations

import os
from pathlib import Path

import httpx
import streamlit as st

API = os.environ.get("VNIR_API", "http://api:8000")
ROOT = Path(os.environ.get("VNIR_ROOT", "/workspace"))

st.set_page_config(page_title="Track 1 — Phat trien nen tang",
                   page_icon="🛠", layout="wide")


def api_get(path: str, **params):
    try:
        r = httpx.get(f"{API}{path}", params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"Khong goi duoc API {path}: {exc}")
        return None


def api_post(path: str, payload: dict):
    try:
        r = httpx.post(f"{API}{path}", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"Khong goi duoc API {path}: {exc}")
        return None


# ---------------------------------------------------------------- header
st.title("🛠 TRACK 1 — Phát triển nền tảng")
st.caption("Nơi bạn nêu yêu cầu. Đội phân tích sẽ **thẩm định** xem nền tảng hiện tại "
           "đã đáp ứng chưa — trước khi đội phát triển làm gì đó. "
           "Phân tích đầu tư & vận hành dữ liệu nằm ở **Track 2 :8602**.")

health = api_get("/health")
c1, c2, c3 = st.columns(3)
c1.metric("API", "OK" if health else "MAT KET NOI")
if health:
    c2.metric("Thu muc goc", health["root"])
    c3.metric("Spec sẵn sàng", "co" if health["specs_dir_exists"] else "chua")

tabs = st.tabs(["📥 Yêu cầu của bạn", "🔎 Thẩm định (ASSESS)", "📋 Yêu cầu (REQ)",
                "🧩 Thành phần (COMP)", "✅ Công việc (TASK)", "🔗 Liên kết 2 track",
                "🔍 Kiểm định", "📖 Hướng dẫn AI"])

# ---------------------------------------------------------------- tab 0: gui yeu cau
with tabs[0]:
    st.subheader("Gửi yêu cầu cải thiện / nâng cấp nền tảng")
    st.info("Viết bằng tiếng Việt bình thường. Hệ thống lưu nguyên văn, rồi đội phân tích "
             "**thẩm định** xem đã làm được chưa — bạn không cần tự phán đoán.")
    with st.form("intake"):
        text = st.text_area("Yêu cầu của bạn", height=180,
                            placeholder="Ví dụ: Tôi muốn xem lãi suất liên ngân hàng qua đêm "
                                        "và cảnh báo khi tăng quá 5%...")
        who = st.text_input("Người yêu cầu", value="nha-dau-tu")
        if st.form_submit_button("Gửi yêu cầu", type="primary"):
            if len(text.strip()) < 10:
                st.warning("Yêu cầu quá ngắn, hãy mô tả rõ hơn.")
            else:
                res = api_post("/intake", {"text": text, "requested_by": who, "channel": "ui-build"})
                if res:
                    st.success("Đã ghi nhận. Tiếp theo: đội phân tích sẽ thẩm định "
                               "(xem tab 🔎 Thẩm định).")

    st.divider()
    st.subheader("Hộp thư yêu cầu chưa xử lý")
    inbox = api_get("/intake") or []
    if not inbox:
        st.caption("Hộp thư trống.")
    for item in inbox:
        with st.expander(f"{item['file']}  ·  {item['modified'][:16]}"):
            st.text(item["preview"])

# ---------------------------------------------------------------- tab 1: ASSESS
with tabs[1]:
    st.subheader("🔎 Thẩm định — nền tảng hiện tại đã đáp ứng chưa?")
    st.caption("Bước bắt buộc của Track 1: đội phân tích đánh giá so với bản hiện tại. "
               "Kết luận phải có bằng chứng thật (lệnh đã chạy), không được phán đoán.")
    asm = api_get("/specs/assess") or []
    if not asm:
        st.info("Chưa có yêu cầu nào cần thẩm định. Hãy gửi yêu cầu ở tab '📥 Yêu cầu của bạn'.")
    else:
        mau = {"da_dap_ung": "🟢", "dap_ung_mot_phan": "🟡",
               "chua_dap_ung": "🔴", "khong_kha_thi": "⛔", "chua_tham_dinh": "⚪"}
        st.dataframe(
            [{"ID": a["id"], "Tiêu đề": a["title"], "Kết luận": mau.get(a.get("ket_luan"), "⚪"),
               "Thẩm định bởi": a.get("nguoi_tham_dinh"),
               "REQ sinh ra": len(a.get("sinh_ra_req", []))}
             for a in asm], use_container_width=True, hide_index=True)
        pick = st.selectbox("Xem / ghi nhận thẩm định", [a["id"] for a in asm])
        d = api_get(f"/specs/item/{pick}")
        if d:
            st.markdown("**📝 Nguyên văn yêu cầu gốc** _(không bao giờ bị sửa)_")
            st.code((d.get("origin") or {}).get("raw_request", "—"), language=None)
            if d.get("bang_chung"):
                st.markdown("**🔬 Bằng chứng đã chạy**")
                for b in d["bang_chung"]:
                    st.write(f"- `{b['kiem_tra']}` → {b['ket_qua']}")
            if d.get("phan_thieu"):
                st.markdown("**❌ Phần còn thiếu**")
                for t in d["phan_thieu"]:
                    st.write(f"- {t}")
            if d.get("huong_dan_su_dung"):
                st.success(f"Đã đáp ứng — hướng dẫn: {d['huong_dan_su_dung']}")
            kl = st.selectbox("Ghi nhận kết luận",
                             ["chua_tham_dinh", "da_dap_ung", "dap_ung_mot_phan",
                              "chua_dap_ung", "khong_kha_thi"],
                             index=["chua_tham_dinh", "da_dap_ung", "dap_ung_mot_phan",
                                    "chua_dap_ung", "khong_kha_thi"].index(
                                 d.get("ket_luan", "chua_tham_dinh")))
            with st.form("ghinhanketluan"):
                bc_kiemtra = st.text_input("Lệnh đã chạy (bắt buộc nếu chưa đáp ứng)")
                bc_ketqua = st.text_input("Kết quả thật")
                if st.form_submit_button("Lưu thẩm định", type="primary"):
                    payload = {"ket_luan": kl}
                    if bc_kiemtra:
                        payload["bang_chung"] = [bc_kiemtra, bc_ketqua]
                    res = api_post(f"/specs/assess/{pick}/conclude", payload)
                    if res and res.get("ok"):
                        st.success(f"Đã lưu kết luận: {kl}. "
                                   f"Nếu cần phát triển, sinh REQ ở tab 📋 Yêu cầu (REQ).")
                        st.rerun()

# ---------------------------------------------------------------- tab 2: REQ
with tabs[2]:
    st.subheader("Yêu cầu — cần gì và vì sao")
    reqs = api_get("/specs/req") or []
    if reqs:
        st.dataframe(
            [{"ID": r["id"], "Tiêu đề": r["title"], "Trạng thái": r["status"],
              "Ưu tiên": (r.get("priority") or {}).get("score"),
              "Mặt phẳng": r.get("plane"), "Component": len(r.get("components", [])),
              "Từ ASSESS": r.get("tu_assess", "")}
             for r in reqs],
            use_container_width=True, hide_index=True)
        pick = st.selectbox("Xem chi tiết", [r["id"] for r in reqs], key="req")
        detail = api_get(f"/specs/item/{pick}")
        if detail:
            cA, cB = st.columns(2)
            with cA:
                st.markdown("**Vấn đề**")
                st.write(detail.get("problem", "—"))
                st.markdown("**Câu hỏi đầu tư**")
                st.write(detail.get("investment_question", "—"))
            with cB:
                st.markdown("**Kết quả mong đợi**")
                st.write(detail.get("outcome", "—"))
                st.markdown("**Tiêu chí nghiệm thu**")
                for a in detail.get("acceptance", []):
                    st.write(f"- {a}")
            st.markdown("**Nguyên văn yêu cầu gốc** _(không bao giờ bị sửa)_")
            st.code((detail.get("origin") or {}).get("raw_request", "—"), language=None)
    else:
        st.caption("Chưa có REQ nào.")

# ---------------------------------------------------------------- tab 3: COMP
with tabs[3]:
    st.subheader("Thành phần kiến trúc — sửa ở đâu")
    comps = api_get("/specs/comp") or []
    if comps:
        st.dataframe(
            [{"ID": c["id"], "Tên": c["name"], "Loại": c["kind"], "Trạng thái": c["status"],
              "Chủ": c.get("owner_role"), "Mặt phẳng": c.get("plane"),
              "Rủi ro": c.get("risk"), "Đường dẫn": ", ".join(c.get("paths", [])[:2])}
             for c in comps],
            use_container_width=True, hide_index=True)
    else:
        st.caption("Chưa có COMP nào.")

# ---------------------------------------------------------------- tab 4: TASK
with tabs[4]:
    st.subheader("Công việc — gói thực thi cho AI")
    tasks = api_get("/specs/task") or []
    if tasks:
        st.dataframe(
            [{"ID": t["id"], "Tiêu đề": t["title"], "Trạng thái": t["status"],
              "REQ": t.get("req_id"), "COMP": t.get("comp_id"),
              "Model": t.get("model_hint"), "Token": t.get("context_budget_tokens")}
             for t in tasks],
            use_container_width=True, hide_index=True)
        pick = st.selectbox("Xem gói thực thi", [t["id"] for t in tasks], key="task")
        d = api_get(f"/specs/item/{pick}")
        if d:
            st.markdown("**Việc phải làm**")
            st.write(d.get("intent"))
            st.markdown("**File được phép sửa**")
            for f in d.get("files_to_touch", []):
                st.write(f"- `{f['path']}` — **{f['action']}** {f.get('hint', '')}")
            st.markdown("**Lệnh verify**")
            st.code("\n".join(d.get("verify_commands", [])), language="bash")
    else:
        st.caption("Chưa có TASK nào. Tạo bằng: `python tools/specctl.py new task ...`")

# ---------------------------------------------------------------- tab 5: lien ket 2 track
with tabs[5]:
    st.subheader("🔗 Liên kết hai track")
    st.caption("BRIEF (Track 2) → ASSESS (thẩm định) → REQ (Track 1). "
               "Mũi tên ngược: thiếu luồng dữ liệu thì đẩy từ Track 2 sang Track 1.")
    briefs = api_get("/specs/brief") or []
    asm_all = api_get("/specs/assess") or []
    reqs = api_get("/specs/req") or []
    for b in briefs:
        st.markdown(f"**📊 {b['id']}** — {b['title']}  _[{b.get('status')}]_")
        for sid in b.get("sinh_ra_assess", []):
            a = next((x for x in asm_all if x["id"] == sid), None)
            if not a:
                continue
            st.markdown(f"&nbsp;&nbsp;↳ 🔎 {sid} — {a.get('ket_luan')}")
            for rid in a.get("sinh_ra_req", []):
                r = next((x for x in reqs if x["id"] == rid), None)
                if not r:
                    continue
                done = "✅" if r.get("status") == "done" else "🔧"
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ 📋 {rid} {done} {r['status']} — {r['title'][:48]}")
    if not briefs:
        st.info("Chưa có đề bài phân tích nào (Track 2). Tạo tại Ops Plane :8602.")

# ---------------------------------------------------------------- tab 6: kiem dinh
with tabs[6]:
    st.subheader("Kiểm định spec (3 tầng)")
    st.caption("Tầng 1: JSON Schema · Tầng 2: toàn vẹn liên kết · Tầng 3: luật cho model AI nhỏ")
    if st.button("Chạy kiểm định", type="primary"):
        res = api_get("/specs/validate")
        if res:
            if res["ok"]:
                st.success(f"Tất cả hợp lệ — {res['stats']}")
            else:
                st.error(f"{len(res['errors'])} lỗi")
                for e in res["errors"]:
                    st.write(f"- {e}")

# ---------------------------------------------------------------- tab 7: huong dan AI
with tabs[7]:
    st.subheader("Cách AI làm việc với kho này")
    st.markdown("""
**Quy trình chuẩn cho bất kỳ AI agent nào (kể cả model 3B):**

```bash
python tools/specctl.py next --model small   # tìm task vừa sức
python tools/specctl.py show TASK-0001       # đọc gói thực thi tự đủ
# ... sửa dùng những file được liệt kê ...
python tools/specctl.py validate             # bắt buộc pass
git commit -m "feat(comp): ...

Task-Id: TASK-0001
Req-Id: REQ-0001"
```

**Vì sao model nhỏ vẫn làm được:**
- Mỗi TASK giới hạn dưới 6.000 token ngữ cảnh (CI chặn nếu vượt).
- TASK liệt kê chính xác file được sửa và file cấm đụng.
- Mỗi TASK có lệnh verify chạy thật để tự kiểm chứng.
- `specs/SPEC-INDEX.md` là bản đồ 1 trang, không cần quét cả repo.
- ID vĩnh viễn không tái sử dụng → truy vết ngược về yêu cầu gốc bất cứ lúc nào.
""")
    idx = ROOT / "specs" / "SPEC-INDEX.md"
    if idx.exists():
        with st.expander("Xem SPEC-INDEX.md"):
            st.markdown(idx.read_text(encoding="utf-8"))

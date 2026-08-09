"""UI NHOM B — OPS PLANE: Trung tam van hanh du lieu.

Nguoi dung: nguoi phan tich, nha dau tu.
Chay: streamlit run vnir/ui_ops/app.py --server.port=8602
"""
from __future__ import annotations

import os
from pathlib import Path

import httpx
import pandas as pd
import plotly.express as px
import streamlit as st

API = os.environ.get("VNIR_API", "http://api:8000")
ROOT = Path(os.environ.get("VNIR_ROOT", "/workspace"))

st.set_page_config(page_title="Ops Plane — Van hanh du lieu",
                   page_icon="📊", layout="wide")


def api_get(path: str, **params):
    try:
        r = httpx.get(f"{API}{path}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"Khong goi duoc API {path}: {exc}")
        return None


def api_post(path: str, payload: dict, timeout: int = 300):
    try:
        r = httpx.post(f"{API}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        st.error(f"Loi goi API {path}: {exc}")
        return None


st.title("📊 TRACK 2 — Thu thập & Phân tích đầu tư")
st.caption("Nơi bạn giao đề bài phân tích (cổ phiếu, ngành, vĩ mô). Đội đầu tư sẽ "
           "kiểm kê dữ liệu, cập nhật/lấy mới qua nền tảng, rồi báo cáo có trích dẫn nguồn. "
           "Thiếu luồng dữ liệu thì tự động đẩy sang **Track 1 :8601**.")

health = api_get("/health")
if not health:
    st.stop()

tabs = st.tabs(["🎯 Đề bài phân tích", "📋 Danh sách (BRIEF)", "🔌 Nguồn dữ liệu",
                "▶️ Chạy & lịch sử", "🗃 Bộ dữ liệu", "📈 Khám phá", "🔎 Truy vấn SQL"])

# ---------------------------------------------------------------- tab 0: de bai
with tabs[0]:
    st.subheader("🎯 Giao đề bài phân tích")
    st.info("Viết đề bài bằng tiếng Việt. Đội đầu tư sẽ kiểm kê dữ liệu — "
            "nếu thiếu luồng lấy, họ đẩy sang Track 1 thay vì tự bịa số.")
    with st.form("brief"):
        text = st.text_area("Đề bài của bạn", height=140,
                            placeholder="Phân tích cổ phiếu VNM: có nên mua ở vùng giá hiện tại?")
        loai = st.selectbox("Loại phân tích", ["co_phieu", "nganh", "vi_mo",
                                               "bat_dong_san", "danh_muc", "so_sanh", "khac"])
        doi_tuong = st.text_input("Đối tượng (mã CK, tên ngành...)", "VNM")
        cau_hoi = st.text_input("Câu hỏi đầu tư chính", "Định giá hiện tại đắt hay rẻ?")
        if st.form_submit_button("Giao đề bài", type="primary"):
            if len(text.strip()) < 10:
                st.warning("Đề bài quá ngắn.")
            else:
                res = api_post("/intake", {"text": text, "requested_by": "nha-dau-tu",
                                           "channel": "ui-ops",
                                           "kind": "brief", "loai": loai,
                                           "doi_tuong": [x.strip() for x in doi_tuong.split(",") if x.strip()],
                                           "cau_hoi": [cau_hoi]})
                if res and res.get("ok"):
                    st.success(f"Đã ghi nhận {res.get('brief_id')}. "
                               f"Mở tab '📋 Danh sách (BRIEF)' để theo dõi.")

# ---------------------------------------------------------------- tab 1: danh sach BRIEF
with tabs[1]:
    st.subheader("📋 Đề bài đang xử lý (Track 2)")
    briefs = api_get("/specs/brief") or []
    if not briefs:
        st.info("Chưa có đề bài nào. Tạo ở tab '🎯 Giao đề bài phân tích'.")
    else:
        mau = {"moi": "⚪", "kiem_ke_du_lieu": "🔍", "cho_track_1": "⚠️",
               "dang_thu_thap": "⬇️", "dang_phan_tich": "🧮", "xong": "✅", "huy": "🗑️"}
        st.dataframe(
            [{"ID": b["id"], "Đề bài": b["title"], "Trạng thái": mau.get(b.get("status"), "⚪"),
               "Loại": b.get("loai_phan_tich"), "Đối tượng": ", ".join(b.get("doi_tuong", [])),
               "Đang chờ T1": len(b.get("cho_req", []))}
             for b in briefs], use_container_width=True, hide_index=True)
        pick = st.selectbox("Xem chi tiết", [b["id"] for b in briefs], key="bbsel")
        d = api_get(f"/specs/item/{pick}")
        if d:
            st.markdown("**📝 Đề bài gốc**")
            st.code((d.get("origin") or {}).get("raw_request", "—"), language=None)
            if d.get("cau_hoi_dau_tu"):
                st.markdown("**❓ Câu hỏi đầu tư**")
                for q in d["cau_hoi_dau_tu"]:
                    st.write(f"- {q}")
            ke = d.get("kiem_ke", [])
            if ke:
                st.markdown("**🧾 Kiểm kê dữ liệu**")
                c = {"co_du": "✅", "co_nhung_cu": "⚠️", "chua_co_luong": "❌"}
                for k in ke:
                    st.write(f"- {c.get(k['trang_thai'], '')} {k['du_lieu_can']} "
                             f"→ {k.get('hanh_dong', '')}")
            if d.get("sinh_ra_assess"):
                st.warning("⚠️ Thiếu luồng dữ liệu — đã đẩy sang Track 1: "
                           + ", ".join(d["sinh_ra_assess"]))
            bc = d.get("bao_cao")
            if bc:
                st.markdown("**📑 Báo cáo**")
                if bc.get("luan_diem"):
                    st.success(f"**Luận điểm:** {bc['luan_diem']}")
                if bc.get("so_nguon_trich_dan"):
                    st.write(f"Nguồn trích dẫn: {bc['so_nguon_trich_dan']}")
                if bc.get("rui_ro"):
                    st.write("**Rủi ro:** " + "; ".join(bc["rui_ro"]))
                if bc.get("dieu_chua_biet"):
                    st.write("**Chưa biết:** " + "; ".join(bc["dieu_chua_biet"]))

# ---------------------------------------------------------------- tab 2: nguon
with tabs[2]:
    st.subheader("Các nguồn đã đăng ký")
    sources = api_get("/sources") or []
    if not sources:
        st.warning("Chưa có connector nào. Thêm vào `vnir/connectors/`.")
    else:
        risk_colour = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        st.dataframe(
            [{"Nguon": s["key"], "Ten": s["title"],
              "Lich (cron)": s["schedule"],
              "Rui ro phap ly": f"{risk_colour.get(s['legal_risk'],'')} {s['legal_risk']}",
              "Can API key": "co" if s["requires_key"] else "khong",
              "SLA do tuoi (ngay)": s["freshness_sla_days"]}
             for s in sources],
            use_container_width=True, hide_index=True)
        for s in sources:
            with st.expander(f"{s['key']} — {s['title']}"):
                st.write(s["description"])
                st.write(f"Trang chu: {s['homepage']}")
                st.caption(f"Lop: `{s['class']}`")

# ---------------------------------------------------------------- tab 3: chay & lich su
with tabs[3]:
    st.subheader("Chạy thu thập thủ công")
    sources = api_get("/sources") or []
    if sources:
        col1, col2, col3 = st.columns([3, 1, 1])
        key = col1.selectbox("Chọn nguồn", [s["key"] for s in sources])
        dry = col2.checkbox("Chạy thử (dry-run)", value=False)
        if col3.button("Chạy ngay", type="primary"):
            with st.spinner(f"Dang thu thap {key}..."):
                res = api_post("/runs", {"key": key, "dry_run": dry})
            if res:
                if res.get("status") == "success":
                    st.success(f"Thanh cong — {res.get('rows', 0)} dong "
                               f"trong {res.get('duration_seconds')}s")
                else:
                    st.error(f"That bai: {res.get('error')}")
                st.json(res)

    st.divider()
    st.subheader("Lich su cac lan chay")
    runs = api_get("/runs", limit=50) or []
    if runs:
        st.dataframe(
            [{"Thoi diem": r.get("started_at", "")[:19].replace("T", " "),
              "Nguon": f"{r.get('source_id')}.{r.get('dataset')}",
              "Ket qua": "✅" if r.get("status") == "success" else "❌",
              "So dong": r.get("rows", 0),
              "Thoi gian (s)": r.get("duration_seconds"),
              "Loi": (r.get("error") or "")[:60]}
             for r in runs],
            use_container_width=True, hide_index=True)
    else:
        st.caption("Chua co lan chay nao.")

# ---------------------------------------------------------------- tab 4: bo du lieu
with tabs[4]:
    st.subheader("Bo du lieu da chuan hoa")
    ds = api_get("/datasets") or []
    if ds:
        st.dataframe(ds, use_container_width=True, hide_index=True)
    else:
        st.caption("Chua co bang nao trong silver/gold. Hay chay mot connector.")

    st.divider()
    st.subheader("Du lieu tho (bronze) — bang chung nguon goc")
    bronze = ROOT / "data" / "bronze"
    if bronze.exists():
        rows = []
        import json as _json
        for man in sorted(bronze.rglob("_manifest.json"))[-30:]:
            m = _json.loads(man.read_text(encoding="utf-8"))
            rows.append({"Nguon": m.get("source_id"), "Bo": m.get("dataset"),
                         "Tai luc": m.get("fetched_at", "")[:19],
                         "So dong": m.get("rows"), "So file": len(m.get("files", [])),
                         "Thu muc": str(man.parent.relative_to(ROOT))})
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.caption("Chua co snapshot bronze nao.")
    else:
        st.caption("Chua co thu muc bronze.")

# ---------------------------------------------------------------- tab 5: kham pha
with tabs[5]:
    st.subheader("Kham pha & bieu dien du lieu")
    ds = api_get("/datasets") or []
    if not ds:
        st.info("Chua co du lieu. Vao tab **Chay & lich su** de thu thap truoc.")
    else:
        pick = st.selectbox("Chon bang", [d["path"] for d in ds])
        res = api_post("/query", {"sql": f"SELECT * FROM '{pick}'", "limit": 20000})
        if res and res.get("ok"):
            df = pd.DataFrame(res["data"])
            st.caption(f"{len(df):,} dong · {len(df.columns)} cot")

            if {"indicator_vi", "year", "value"}.issubset(df.columns):
                inds = sorted(df["indicator_vi"].dropna().unique())
                chosen = st.multiselect("Chon chi so", inds, default=inds[:2])
                sub = df[df["indicator_vi"].isin(chosen)]
                if not sub.empty:
                    fig = px.line(sub.sort_values("year"), x="year", y="value",
                                  color="indicator_vi", markers=True,
                                  title="Dien bien chi so theo nam")
                    fig.update_layout(height=460, legend_title="", hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                    latest = (sub.sort_values("year").groupby("indicator_vi").tail(1))
                    cols = st.columns(min(len(latest), 4) or 1)
                    for i, (_, r) in enumerate(latest.iterrows()):
                        cols[i % len(cols)].metric(
                            r["indicator_vi"][:28], f"{r['value']:,.2f}", f"nam {int(r['year'])}")
            else:
                num = df.select_dtypes("number").columns.tolist()
                if num:
                    ycol = st.selectbox("Cot gia tri", num)
                    st.bar_chart(df[ycol].head(200))
            with st.expander("Xem bang du lieu"):
                st.dataframe(df.head(500), use_container_width=True)

# ---------------------------------------------------------------- tab 6: SQL
with tabs[6]:
    st.subheader("Truy van SQL (DuckDB, chi doc)")
    st.caption("Doc truc tiep file Parquet. Vi du: "
               "`SELECT * FROM 'data/silver/macro/worldbank__vn_macro_indicators.parquet' LIMIT 20`")
    sql = st.text_area("Cau SQL", height=130,
                       value="SELECT indicator_vi, year, value\n"
                             "FROM 'data/silver/macro/worldbank__vn_macro_indicators.parquet'\n"
                             "WHERE indicator_code = 'NY.GDP.MKTP.CD'\n"
                             "ORDER BY year DESC LIMIT 15")
    if st.button("Chay truy van", type="primary"):
        res = api_post("/query", {"sql": sql, "limit": 5000})
        if res and res.get("ok"):
            st.success(f"{res['rows']} dong")
            st.dataframe(pd.DataFrame(res["data"]), use_container_width=True)

st.caption("Nơi bạn giao đề bài phân tích (cổ phiếu, ngành, vĩ mô). Đội đầu tư sẽ "
           "kiểm kê dữ liệu, cập nhật/lấy mới qua nền tảng, rồi báo cáo có trích dẫn nguồn. "
           "Thiếu luồng dữ liệu thì tự động đẩy sang **Track 1 :8601**.")

health = api_get("/health")
if not health:
    st.stop()


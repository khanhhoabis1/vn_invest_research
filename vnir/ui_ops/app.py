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


st.title("📊 Ops Plane — Trung tam van hanh du lieu")
st.caption("Nhom B · Thu thap, kiem tra va kham pha du lieu kinh te Viet Nam. "
           "Gui yeu cau nang cap nen tang tai **Build Plane :8601**.")

health = api_get("/health")
if not health:
    st.stop()

tabs = st.tabs(["🔌 Nguon du lieu", "▶️ Chay & lich su", "🗃 Bo du lieu",
                "📈 Kham pha", "🔎 Truy van SQL"])

# ---------------------------------------------------------------- nguon
with tabs[0]:
    st.subheader("Cac nguon da dang ky")
    sources = api_get("/sources") or []
    if not sources:
        st.warning("Chua co connector nao. Them vao `vnir/connectors/`.")
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

# ---------------------------------------------------------------- chay
with tabs[1]:
    st.subheader("Chay thu thap thu cong")
    sources = api_get("/sources") or []
    if sources:
        col1, col2, col3 = st.columns([3, 1, 1])
        key = col1.selectbox("Chon nguon", [s["key"] for s in sources])
        dry = col2.checkbox("Chay thu (dry-run)", value=False)
        if col3.button("Chay ngay", type="primary"):
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

# ---------------------------------------------------------------- bo du lieu
with tabs[2]:
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
        for man in sorted(bronze.rglob("_manifest.json"))[-30:]:
            import json as _json
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

# ---------------------------------------------------------------- kham pha
with tabs[3]:
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

# ---------------------------------------------------------------- SQL
with tabs[4]:
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

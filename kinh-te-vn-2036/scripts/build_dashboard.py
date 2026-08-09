#!/usr/bin/env python3
"""Sinh Dashboard HTML từ master-data.json."""
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data-nguon", "master-data.json")
OUT = os.path.join(ROOT, "docs-bao-cao", "dashboard-kinh-te-vn-2036.html")

with open(DATA, encoding="utf-8") as f:
    d = json.load(f)

def esc(s): return html.escape(str(s))

# Headline cards
hl = "".join(
    f'<div class="kpi"><div class="kpi-v">{esc(x["v"])}</div>'
    f'<div class="kpi-k">{esc(x["k"])}</div>'
    f'<div class="kpi-s">{esc(x["s"])}</div></div>'
    for x in d["headline"]
)

# Branch cards
def branch_card(b):
    rows = "".join(
        f'<tr><td class="m">{esc(c[0])}</td><td class="v">{esc(c[1])}</td>'
        f'<td class="s">{esc(c[2])}</td></tr>'
        for c in b["chi_so"]
    )
    subs = b.get("subs", [])
    sub_html = ""
    if subs:
        sub_html = '<div class="subs">' + " ".join(
            f'<span class="tag">{esc(s)}</span>' for s in subs) + '</div>'
    return f'''
    <section class="card" style="--accent:{esc(b['color'])}">
      <header>
        <span class="dot"></span>
        <h2>{esc(b["title"])}</h2>
        <code>{esc(b["folder"])}</code>
      </header>
      <p class="desc">{esc(b["mo_ta"])}</p>
      <table>
        <thead><tr><th>Chỉ số</th><th>Giá trị (2024–2025)</th><th>Nguồn</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
      {sub_html}
    </section>'''

cards = "".join(branch_card(b) for b in d["branches"])

# Ma trận theo dõi (blank inputs) - build from branches' first indicator
track_rows = ""
tr_idx = 0
for b in d["branches"]:
    for c in b["chi_so"]:
        tr_idx += 1
        track_rows += (f'<tr><td>{tr_idx}</td><td>{esc(b["title"])}</td>'
                       f'<td>{esc(c[0])}</td>'
                       f'<td><input type="text" placeholder="…"></td>'
                       f'<td><input type="text" placeholder="…"></td>'
                       f'<td><input type="text" placeholder="…"></td>'
                       f'<td><input type="text" placeholder="…"></td>'
                       f'<td><input type="text" placeholder="…"></td></tr>')

doc = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Kinh tế Việt Nam 2026–2036</title>
<style>
  :root {{ --bg:#f4f6fa; --ink:#1a2233; --muted:#64748b; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,"Noto Sans",sans-serif;
         background:var(--bg); color:var(--ink); line-height:1.5; }}
  header.top {{ background:linear-gradient(120deg,#0b2545,#13315c); color:#fff; padding:34px 28px 26px; }}
  header.top h1 {{ margin:0 0 6px; font-size:26px; }}
  header.top p {{ margin:2px 0; font-size:13px; opacity:.85; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:22px 18px 60px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:18px 0 28px; }}
  .kpi {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px;
          box-shadow:0 1px 3px rgba(15,23,42,.06); }}
  .kpi-v {{ font-size:21px; font-weight:700; color:#0b2545; }}
  .kpi-k {{ font-size:12.5px; margin-top:3px; color:var(--ink); }}
  .kpi-s {{ font-size:11px; color:var(--muted); margin-top:2px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:18px; }}
  .card {{ background:#fff; border:1px solid #e2e8f0; border-top:4px solid var(--accent,#1F4E78);
          border-radius:12px; padding:16px 16px 14px; box-shadow:0 1px 3px rgba(15,23,42,.05); }}
  .card header {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
  .card .dot {{ width:10px; height:10px; border-radius:50%; background:var(--accent,#1F4E78); }}
  .card h2 {{ font-size:16px; margin:0; }}
  .card code {{ font-size:11px; color:var(--muted); background:#f1f5f9; padding:2px 6px; border-radius:5px; margin-left:auto; }}
  .card .desc {{ font-size:12.5px; color:var(--muted); margin:8px 0 10px; }}
  table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
  th,td {{ text-align:left; padding:6px 8px; border-bottom:1px solid #eef2f7; vertical-align:top; }}
  th {{ font-size:11px; text-transform:uppercase; letter-spacing:.03em; color:var(--muted); }}
  td.v {{ font-weight:600; color:#0b2545; }}
  td.s {{ color:var(--muted); font-size:11px; white-space:nowrap; }}
  .subs {{ margin-top:10px; }}
  .tag {{ display:inline-block; background:#eef2ff; color:#3730a3; font-size:11px;
          padding:3px 8px; border-radius:20px; margin:2px 4px 2px 0; }}
  .matrix {{ margin-top:34px; }}
  .matrix h2 {{ font-size:18px; color:#0b2545; }}
  .matrix table {{ background:#fff; border:1px solid #e2e8f0; border-radius:10px; overflow:hidden; }}
  .matrix input {{ width:100%; border:1px solid #d4dae3; border-radius:6px; padding:5px 7px; font-size:12px; }}
  .note {{ font-size:11.5px; color:var(--muted); margin-top:14px; }}
</style>
</head>
<body>
<header class="top">
  <h1>📊 Dashboard Kinh tế Việt Nam 10 năm tới (2026–2036)</h1>
  <p>Kỳ dữ liệu: {esc(d["meta"]["ky_cap_nhat"])}</p>
  <p>Nguồn: {esc(d["meta"]["nguon_chung"])}</p>
</header>
<div class="wrap">
  <div class="kpis">{hl}</div>
  <div class="grid">{cards}</div>

  <div class="matrix">
    <h2>Ma trận theo dõi chỉ số (cập nhật định kỳ)</h2>
    <table>
      <thead><tr><th>#</th><th>Nhánh</th><th>Chỉ số</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Năm</th></tr></thead>
      <tbody>{track_rows}</tbody>
    </table>
    <p class="note">⚠ {esc(d["meta"]["luu_y"])}</p>
  </div>
</div>
</body>
</html>'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("WROTE", OUT, len(doc), "bytes")

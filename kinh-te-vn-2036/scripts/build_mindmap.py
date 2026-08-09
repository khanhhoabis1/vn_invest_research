#!/usr/bin/env python3
"""Sinh Mind-map HTML từ master-data.json (layout radial, thuần CSS/SVG, không phụ thuộc ngoài)."""
import json, os, math, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # thu muc kinh-te-vn-2036

LEGACY_BANNER = """<div style="background:#7f1d1d;color:#fff;padding:12px 18px;font-family:system-ui,sans-serif;font-size:14px;line-height:1.55;border-bottom:3px solid #dc2626">
<strong>&#9888; ẢNH CHỤP LỊCH SỬ — 2024/2025, KHÔNG CÒN CẬP NHẬT</strong><br>
Số liệu trang này thu thập thủ công, phần lớn dẫn nguồn báo chí thứ cấp, <b>không có URL gốc và ngày truy cập</b>.
Không dùng làm căn cứ ra quyết định đầu tư. Dữ liệu chính thức có kiểm chứng: mở <b>Ops Plane — http://localhost:8602</b>.
</div>"""
DATA = os.path.join(ROOT, "data-nguon", "master-data.json")
OUT = os.path.join(ROOT, "docs-bao-cao", "mindmap-kinh-te-vn-2036.html")

with open(DATA, encoding="utf-8") as f:
    d = json.load(f)

def esc(s): return html.escape(str(s))

branches = d["branches"]
N = len(branches)
cx, cy = 460, 430          # tâm
R = 300                    # bán kính node nhánh
r_node = 86                # bán kính node

# Tọa độ node nhánh (phân bố tròn)
positions = []
for i, b in enumerate(branches):
    ang = -math.pi/2 + 2*math.pi*i/N
    x = cx + R*math.cos(ang)
    y = cy + R*math.sin(ang)
    positions.append((x, y, ang))

# Đường nối SVG
lines = ""
for (x, y, ang) in positions:
    dx, dy = math.cos(ang), math.sin(ang)
    x1, y1 = cx + 14*dx, cy + 14*dy
    x2, y2 = x - r_node*0.95*dx, y - r_node*0.95*dy
    lines += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{esc(branches[positions.index((x,y,ang))]["color"])}" stroke-width="3" opacity="0.55"/>'

# Node trung tâm
center = f'''
  <div class="node center" style="left:{cx}px;top:{cy}px;width:170px;height:170px;margin:-85px 0 0 -85px;">
    <div class="c-title">KINH TẾ<br>VIỆT NAM</div>
    <div class="c-sub">2026 – 2036</div>
  </div>'''

# Node nhánh
nodes = ""
for i, b in enumerate(branches):
    x, y, ang = positions[i]
    dx, dy = math.cos(ang), math.sin(ang)
    # panel chi tiết mở rộng về phía ngoài
    px, py = x + dx*150, y + dy*150
    n_left, n_top = x - r_node, y - r_node
    # hướng text-align
    align = "left" if dx >= 0 else "right"
    nodes += f'''
  <div class="node branch" style="left:{x:.1f}px;top:{y:.1f}px;width:{2*r_node}px;height:{2*r_node}px;
       margin:-{r_node}px 0 0 -{r_node}px;border-color:{esc(b['color'])};--accent:{esc(b['color'])};">
    <div class="b-num">{i+1:02d}</div>
    <div class="b-title">{esc(b["title"])}</div>
    <div class="b-folder">{esc(b["folder"])}</div>
  </div>
  <div class="panel" style="left:{px:.1f}px;top:{py:.1f}px;--accent:{esc(b['color'])};text-align:{align};">
    <div class="p-head" style="color:{esc(b['color'])}">{esc(b["title"])}</div>
    <ul>{''.join(f'<li>{esc(c[0])} — <b>{esc(c[1])}</b></li>' for c in b["chi_so"])}</ul>
  </div>'''

doc = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mind-map Kinh tế Việt Nam 2026–2036</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:#0b1220; color:#e7edf5; font-family:-apple-system,"Segoe UI",Roboto,Arial,"Noto Sans",sans-serif; }}
  header {{ padding:18px 24px 6px; }}
  header h1 {{ margin:0; font-size:20px; }}
  header p {{ margin:4px 0 0; font-size:12px; color:#93a4bd; }}
  .stage {{ position:relative; width:920px; height:860px; margin:8px auto 30px; }}
  svg {{ position:absolute; inset:0; }}
  .node {{ position:absolute; border-radius:50%; display:flex; flex-direction:column;
           align-items:center; justify-content:center; text-align:center; padding:8px; }}
  .node.center {{ background:radial-gradient(circle at 30% 30%,#1f4e78,#0b2545); border:2px solid #5b8dd9;
                 box-shadow:0 0 30px rgba(43,108,214,.5); }}
  .c-title {{ font-size:16px; font-weight:800; letter-spacing:.5px; }}
  .c-sub {{ font-size:12px; color:#9fc1f5; margin-top:4px; }}
  .node.branch {{ background:#121d33; border:2px solid #1F4E78; cursor:default;
                 box-shadow:0 4px 14px rgba(0,0,0,.45); transition:transform .15s; }}
  .node.branch:hover {{ transform:scale(1.06); }}
  .b-num {{ font-size:13px; font-weight:800; color:var(--accent); }}
  .b-title {{ font-size:13px; font-weight:700; line-height:1.15; margin-top:2px; }}
  .b-folder {{ font-size:9.5px; color:#7e90ad; margin-top:3px; }}
  .panel {{ position:absolute; width:210px; transform:translate(-50%,-50%); background:rgba(18,29,51,.92);
            border-left:3px solid var(--accent); border-radius:8px; padding:9px 11px; font-size:11px;
            box-shadow:0 6px 18px rgba(0,0,0,.5); }}
  .p-head {{ font-weight:700; font-size:12px; margin-bottom:5px; }}
  .panel ul {{ margin:0; padding-left:14px; }}
  .panel li {{ margin:3px 0; color:#c7d3e6; }}
  .panel b {{ color:#fff; }}
  footer {{ text-align:center; font-size:11px; color:#64748b; padding-bottom:26px; }}
</style>
</head>
<body>{LEGACY_BANNER}
<header>
  <h1>🧠 Mind-map nghiên cứu Kinh tế Việt Nam 10 năm tới (2026–2036)</h1>
  <p>10 nhánh chính · dữ liệu cập nhật {esc(d["meta"]["ky_cap_nhat"])} · nguồn: {esc(d["meta"]["nguon_chung"])}</p>
</header>
<div class="stage">
  <svg width="920" height="860">{lines}</svg>
  {center}
  {nodes}
</div>
<footer>Trượt để xem đầy đủ · sinh tự động từ data-nguon/master-data.json</footer>
</body>
</html>'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("WROTE", OUT, len(doc), "bytes")

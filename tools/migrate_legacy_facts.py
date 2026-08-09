#!/usr/bin/env python3
"""Chuyen so lieu cu (master-data.json) thanh facts co nhan do tin cay.

Vi sao can: so lieu cu dan nguon bao chi (VietnamNet, Statista...) khong co URL,
khong co ngay truy cap -> vi pham P1 cua CHARTER. Khong vut di, nhung phai
HA CAP: danh dau ro la tham khao, chua kiem chung, kem goi y connector thay the.

Chay: python tools/migrate_legacy_facts.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "kinh-te-vn-2036" / "data-nguon" / "master-data.json"
SRC2 = ROOT / "kinh-te-vn-2036" / "data-nguon" / "chi-so-2024-2025.json"
OUT = ROOT / "context" / "facts" / "legacy-2024-2025.md"

# Nguon so cap dang tin vs nguon bao chi thu cap
PRIMARY = {"TCTK", "GSO", "World Bank", "IMF", "AMRO", "UNFPA", "SBV", "NHNN", "IEA"}

# Chi so cu -> connector se thay the trong tuong lai
REPLACEMENT = {
    "GDP": "worldbank.vn_macro_indicators (NY.GDP.MKTP.CD) + GSO PX-Web",
    "Tăng trưởng GDP": "worldbank.vn_macro_indicators (NY.GDP.MKTP.KD.ZG)",
    "GDP/người": "worldbank.vn_macro_indicators (NY.GDP.PCAP.CD)",
    "Lạm phát": "worldbank.vn_macro_indicators (FP.CPI.TOTL.ZG) + GSO CPI thang",
    "CPI": "worldbank.vn_macro_indicators (FP.CPI.TOTL.ZG)",
    "Dân số": "worldbank.vn_macro_indicators (SP.POP.TOTL)",
    "đô thị hóa": "worldbank.vn_macro_indicators (SP.URB.TOTL.IN.ZS)",
    "Nợ công": "worldbank.vn_macro_indicators (GC.DOD.TOTL.GD.ZS) + MOF",
    "FDI": "worldbank.vn_macro_indicators (BX.KLT.DINV.WD.GD.ZS) + MPI",
    "XNK": "Tổng cục Hải quan (chưa có connector)",
    "Tỷ giá": "SBV (chưa có connector)",
    "nợ xấu": "SBV + BCTC ngân hàng (chưa có connector)",
    "Tín dụng": "SBV (chưa có connector)",
}


def find_replacement(metric: str) -> str:
    for key, conn in REPLACEMENT.items():
        if key.lower() in metric.lower():
            return conn
    return "chưa xác định"


def confidence(source: str, value: str) -> tuple[str, str]:
    """Tra ve (muc_do_tin_cay, ly_do)."""
    if "*" in value:
        return "thấp", "tự đánh dấu là ước tính"
    if any(p.lower() in source.lower() for p in PRIMARY):
        return "trung bình", "nguồn sơ cấp nhưng thiếu URL và ngày truy cập"
    return "thấp", "nguồn báo chí thứ cấp, không có URL"


def main() -> int:
    if not SRC.exists():
        print(f"Khong tim thay {SRC}", file=sys.stderr)
        return 1

    data = json.loads(SRC.read_text(encoding="utf-8"))
    extra = json.loads(SRC2.read_text(encoding="utf-8")) if SRC2.exists() else {"branches": {}}
    extra_branches = extra.get("branches", {})

    L: list[str] = []
    L += ["---",
          "title: Số liệu kế thừa 2024–2025 (chưa kiểm chứng)",
          "doc_type: source-note",
          "status: active",
          "do_tin_cay: thap",
          "can_kiem_chung_lai: true",
          "as_of: 2024-2025",
          "created: 2026-08-09",
          "nguon_goc: kinh-te-vn-2036/data-nguon/master-data.json",
          "---", "",
          "# Số liệu kế thừa 2024–2025 — THAM KHẢO, CHƯA KIỂM CHỨNG", "",
          "> ⚠️ **Cảnh báo cho người đọc và cho LLM.**",
          "> Toàn bộ số liệu dưới đây được thu thập thủ công trước khi có nền tảng tự động.",
          "> Chúng **không có URL nguồn, không có ngày truy cập**, phần lớn dẫn từ báo chí thứ cấp.",
          "> **Không dùng làm căn cứ ra quyết định đầu tư.** Chỉ dùng để định hướng nghiên cứu",
          "> và để đối chiếu khi connector chính thức đã lấy được số liệu thật.", "",
          "Quy ước độ tin cậy:", "",
          "| Mức | Nghĩa |", "|---|---|",
          "| trung bình | Nguồn sơ cấp (TCTK, World Bank, IMF…) nhưng thiếu URL/ngày |",
          "| thấp | Nguồn báo chí thứ cấp, hoặc tự đánh dấu là ước tính (`*`) |", ""]

    # Headline
    if data.get("headline"):
        L += ["## Chỉ số tổng quan", "",
              "| Chỉ số | Giá trị | Nguồn ghi nhận | Độ tin cậy | Lý do | Connector sẽ thay thế |",
              "|---|---|---|---|---|---|"]
        for h in data["headline"]:
            conf, reason = confidence(h.get("s", ""), h.get("v", ""))
            L.append(f"| {h.get('k','')} | {h.get('v','')} | {h.get('s','')} | "
                     f"**{conf}** | {reason} | `{find_replacement(h.get('k',''))}` |")
        L.append("")

    # Theo nhanh
    L += ["## Chỉ số theo nhánh nghiên cứu", ""]
    total = 0
    for br in data.get("branches", []):
        folder = br.get("folder", "")
        L += [f"### {br.get('title','')} (`{folder}`)", ""]
        if br.get("mo_ta"):
            L += [f"_{br['mo_ta']}_", ""]
        L += ["| Chỉ số | Giá trị | Nguồn | Độ tin cậy | Connector sẽ thay thế |",
              "|---|---|---|---|---|"]
        seen = set()
        rows = list(br.get("chi_so") or [])
        for row in (extra_branches.get(folder) or []):
            if tuple(row) not in {tuple(r) for r in rows}:
                rows.append(row)          # hop nhat phan chi co o file thu 2
        for c in rows:
            if len(c) < 3:
                continue
            key = (c[0], c[1])
            if key in seen:
                continue
            seen.add(key)
            conf, _ = confidence(c[2], c[1])
            L.append(f"| {c[0]} | {c[1]} | {c[2]} | **{conf}** | `{find_replacement(c[0])}` |")
            total += 1
        L.append("")

    L += ["---", "",
          f"**Tổng cộng {total} chỉ số kế thừa.** Mỗi chỉ số cần được thay thế bằng dữ liệu",
          "từ connector có kiểm chứng trước khi dùng trong báo cáo chính thức.", "",
          "Xem tiến độ thay thế: `vnir/registry/` và `python tools/specctl.py list task`."]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"Da tao {OUT.relative_to(ROOT)} — {total} chi so ke thua da duoc gan nhan do tin cay")
    return 0


if __name__ == "__main__":
    sys.exit(main())

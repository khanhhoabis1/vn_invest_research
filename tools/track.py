#!/usr/bin/env python3
"""track.py — dieu phoi hai track lam viec.

TRACK 1 (phat trien nen tang):
    yeu-cau           Nguoi dung gui yeu cau      -> tao ASSESS
    tham-dinh         Doi phan tich tham dinh     -> ghi ket luan + bang chung
    chuyen-phat-trien Chuyen sang doi phat trien  -> sinh REQ tu ASSESS

TRACK 2 (thu thap & phan tich dau tu):
    de-bai            Nguoi dung giao de bai      -> tao BRIEF
    kiem-ke           Kiem ke du lieu can vs co
    day-track-1       Thieu luong lay du lieu     -> day nguoc sang Track 1
    bao-cao           Ghi nhan ket qua phan tich

CHUNG:
    hang-doi          Xem viec dang o dau
    lien-ket          Ve so do lien ket ASSESS/REQ/BRIEF

Doc them: squad/00-charter/HAI-TRACK.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spec_lib import KINDS, load, load_all, next_id, save, today

OK, BAD, WARN, DIM, B = "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[1m"
END = "\033[0m"

KET_LUAN = {
    "da_dap_ung": "Da dap ung — chi can huong dan cach dung",
    "dap_ung_mot_phan": "Dap ung mot phan — con thieu vai thu",
    "chua_dap_ung": "Chua dap ung — phai phat trien moi",
    "khong_kha_thi": "Khong kha thi — nguon khong co hoac bi chan",
}


def _diem(tac_dong: int, tu_tin: int, cong_suc: int) -> float:
    return round(tac_dong * tu_tin / max(cong_suc, 1), 2)


# ------------------------------------------------------------------ TRACK 1
def cmd_yeu_cau(a: argparse.Namespace) -> int:
    """Nguoi dung gui yeu cau -> tao ASSESS de doi phan tich tham dinh."""
    sid = next_id("ASSESS")
    spec = {
        "id": sid,
        "title": a.tieu_de or a.noi_dung[:70],
        "status": "moi",
        "created": today(),
        "origin": {
            "raw_request": a.noi_dung,          # NGUYEN VAN, khong dien giai
            "requested_by": a.nguoi_gui,
            "requested_at": today(),
            "channel": a.kenh,
        },
        "ket_luan": "chua_tham_dinh",
        "bang_chung": [],
        "nguoi_tham_dinh": a.giao_cho,
    }
    if a.tu_brief:
        spec["tu_brief"] = a.tu_brief.upper()
    p = save(spec)
    print(f"{OK}✓{END} Da tao {B}{sid}{END} — {spec['title']}")
    print(f"  {DIM}{p}{END}")
    print(f"\n{WARN}Buoc tiep theo:{END} doi phan tich dau tu tham dinh")
    print(f"  python tools/track.py tham-dinh {sid} --ket-luan <ket_luan> \\")
    print('      --bang-chung "<lenh da chay>" "<output that>"')
    return 0


def cmd_tham_dinh(a: argparse.Namespace) -> int:
    """Doi phan tich ghi ket luan tham dinh. BAT BUOC co bang chung that."""
    spec = load(a.id.upper())
    if a.ket_luan and not a.bang_chung and not spec.get("bang_chung"):
        print(f"{BAD}✗ Khong the ket luan '{a.ket_luan}' ma khong co bang chung.{END}")
        print(f"  {DIM}Nguyen tac P1: khong duoc phong doan. Phai chay lenh that.{END}")
        print('  Vi du: --bang-chung "GET /sources" "chi tra ve worldbank"')
        return 1

    if a.bang_chung:
        spec.setdefault("bang_chung", []).append({
            "kiem_tra": a.bang_chung[0],
            "ket_qua": a.bang_chung[1] if len(a.bang_chung) > 1 else "",
            "ngay": today(),
        })
    if a.thieu:
        spec.setdefault("phan_thieu", []).extend(a.thieu)
    if a.huong_dan:
        spec["huong_dan_su_dung"] = a.huong_dan
    if a.thay_the:
        spec["phuong_an_thay_the"] = a.thay_the
    if a.uu_tien:
        t, c, e = a.uu_tien
        spec["uu_tien"] = {"tac_dong": t, "tu_tin": c, "cong_suc": e, "diem": _diem(t, c, e)}
    if a.ket_luan:
        spec["ket_luan"] = a.ket_luan
        spec["status"] = "xong"
    else:
        spec["status"] = "dang_tham_dinh"

    save(spec)
    kl = spec["ket_luan"]
    mau = OK if kl == "da_dap_ung" else (WARN if kl == "dap_ung_mot_phan" else BAD)
    print(f"{OK}✓{END} {spec['id']}: {mau}{KET_LUAN.get(kl, kl)}{END}")

    if kl in ("chua_dap_ung", "dap_ung_mot_phan"):
        print(f"\n{WARN}Buoc tiep theo:{END} chuyen cho doi phat trien")
        print(f"  python tools/track.py chuyen-phat-trien {spec['id']}")
    elif kl == "da_dap_ung":
        print(f"\n{OK}Ket thuc Track 1.{END} Tra loi nguoi dung cach dung tinh nang co san.")
        if spec.get("huong_dan_su_dung"):
            print(f"  {spec['huong_dan_su_dung']}")
    elif kl == "khong_kha_thi":
        print(f"\n{BAD}Ket thuc Track 1.{END} Bao nguoi dung ly do va phuong an thay the.")
    return 0


def cmd_chuyen_phat_trien(a: argparse.Namespace) -> int:
    """ASSESS -> REQ. Giu nguyen van yeu cau goc, khong dien giai lai."""
    asm = load(a.id.upper())
    if asm.get("ket_luan") not in ("chua_dap_ung", "dap_ung_mot_phan"):
        print(f"{BAD}✗ {asm['id']} co ket luan '{asm.get('ket_luan')}' "
              f"— khong can phat trien.{END}")
        return 1

    rid = next_id("REQ")
    thieu = asm.get("phan_thieu") or []
    ut = asm.get("uu_tien") or {}
    req = {
        "id": rid,
        "title": asm["title"],
        "status": "draft",
        "created": today(),
        "origin": {
            "raw_request": asm["origin"]["raw_request"],   # giu NGUYEN VAN
            "requested_by": asm["origin"].get("requested_by", ""),
            "requested_at": asm["origin"].get("requested_at", today()),
            "channel": "track-cli",
        },
        "problem": ("Nen tang chua dap ung: " + "; ".join(thieu)) if thieu
                   else "Nen tang chua dap ung yeu cau nay (xem " + asm["id"] + ")",
        "outcome": a.ket_qua or f"Nguoi dung thuc hien duoc: {asm['title']}",
        "acceptance": [f"Da co: {t}" for t in thieu] or ["Yeu cau goc duoc dap ung day du"],
        "priority": {
            "impact": ut.get("tac_dong", 3),
            "confidence": ut.get("tu_tin", 3),
            "effort": ut.get("cong_suc", 3),
            "score": ut.get("diem", 3.0),
        },
        "plane": a.plane,
        "tu_assess": asm["id"],
    }
    if asm.get("tu_brief"):
        req["cho_brief"] = [asm["tu_brief"]]

    save(req)
    asm.setdefault("sinh_ra_req", []).append(rid)
    save(asm)

    print(f"{OK}✓{END} {asm['id']} → {B}{rid}{END}")
    print(f"  {DIM}Nguyen van yeu cau da duoc giu lai trong origin.raw_request{END}")
    if req.get("cho_brief"):
        print(f"  {WARN}⚠ {req['cho_brief'][0]} (Track 2) dang cho REQ nay{END}")
    print(f"\n{WARN}Buoc tiep theo:{END} doi phat trien tach thanh COMP/TASK")
    print(f"  python tools/specctl.py show {rid}")
    return 0


# ------------------------------------------------------------------ TRACK 2
def cmd_de_bai(a: argparse.Namespace) -> int:
    """Nguoi dung giao de bai phan tich -> tao BRIEF."""
    bid = next_id("BRIEF")
    spec = {
        "id": bid,
        "title": a.tieu_de or a.noi_dung[:70],
        "status": "moi",
        "created": today(),
        "origin": {
            "raw_request": a.noi_dung,
            "requested_by": a.nguoi_gui,
            "requested_at": today(),
        },
        "loai_phan_tich": a.loai,
        "doi_tuong": a.doi_tuong or [],
        "cau_hoi_dau_tu": a.cau_hoi or [],
    }
    if a.han_chot:
        spec["origin"]["han_chot"] = a.han_chot
    p = save(spec)
    print(f"{OK}✓{END} Da tao {B}{bid}{END} — {spec['title']}")
    print(f"  {DIM}{p}{END}")
    print(f"\n{WARN}Buoc tiep theo:{END} doi dau tu kiem ke du lieu")
    print(f"  python tools/track.py kiem-ke {bid} --can \"<du lieu>\" --trang-thai <tt>")
    return 0


def cmd_kiem_ke(a: argparse.Namespace) -> int:
    """Ghi mot dong kiem ke du lieu can vs co."""
    spec = load(a.id.upper())
    if a.can:
        dong = {"du_lieu_can": a.can, "trang_thai": a.trang_thai}
        for k, v in (("nguon", a.nguon), ("cap_nhat_lan_cuoi", a.cap_nhat),
                     ("hanh_dong", a.hanh_dong)):
            if v:
                dong[k] = v
        spec.setdefault("kiem_ke", []).append(dong)
    if spec.get("status") == "moi":
        spec["status"] = "kiem_ke_du_lieu"

    ke = spec.get("kiem_ke", [])
    thieu = [k for k in ke if k["trang_thai"] == "chua_co_luong"]
    cu = [k for k in ke if k["trang_thai"] == "co_nhung_cu"]
    if ke and not thieu:
        spec["status"] = "dang_thu_thap" if cu else "dang_phan_tich"
    save(spec)

    print(f"\n{B}KIEM KE DU LIEU — {spec['id']}{END}  {spec['title']}")
    print("-" * 74)
    icon = {"co_du": f"{OK}✅ co du{END}", "co_nhung_cu": f"{WARN}⚠️  cu{END}",
            "chua_co_luong": f"{BAD}❌ chua co luong{END}"}
    for k in ke:
        print(f"  {icon.get(k['trang_thai'], k['trang_thai']):<28} {k['du_lieu_can']}")
        if k.get("hanh_dong"):
            print(f"       {DIM}→ {k['hanh_dong']}{END}")
    print("-" * 74)
    print(f"Tong {len(ke)} muc — du: {len(ke)-len(thieu)-len(cu)}, "
          f"cu: {len(cu)}, thieu luong: {len(thieu)}")

    if thieu:
        print(f"\n{BAD}⚠ Co {len(thieu)} muc chua co luong lay du lieu.{END}")
        print(f"  {DIM}KHONG duoc tu bia so. Phai day sang Track 1:{END}")
        for k in thieu:
            print(f"  python tools/track.py day-track-1 {spec['id']} "
                  f'--du-lieu "{k["du_lieu_can"]}"')
    elif cu:
        print(f"\n{WARN}Co {len(cu)} muc du lieu cu — chay cap nhat:{END}")
        print('  curl -X POST localhost:8000/runs -d \'{"key":"<source>.<dataset>"}\'')
    else:
        print(f"\n{OK}Du du lieu — co the phan tich.{END}")
    return 0


def cmd_day_track_1(a: argparse.Namespace) -> int:
    """Track 2 thieu luong lay du lieu -> day nguoc sang Track 1."""
    brief = load(a.id.upper())
    sid = next_id("ASSESS")
    asm = {
        "id": sid,
        "title": f"Can luong lay du lieu: {a.du_lieu}",
        "status": "moi",
        "created": today(),
        "origin": {
            "raw_request": (f"[Day tu {brief['id']}] De bai phan tich "
                            f"\"{brief['title']}\" can du lieu: {a.du_lieu}. "
                            f"Yeu cau goc: {brief['origin']['raw_request']}"),
            "requested_by": brief["origin"].get("requested_by", ""),
            "requested_at": today(),
            "channel": "khac",
        },
        "ket_luan": "chua_tham_dinh",
        "bang_chung": [],
        "tu_brief": brief["id"],
        "nguoi_tham_dinh": "BA",
    }
    save(asm)
    brief.setdefault("sinh_ra_assess", []).append(sid)
    brief["status"] = "cho_track_1"
    save(brief)

    print(f"{OK}✓{END} {brief['id']} → {B}{sid}{END} (day sang Track 1)")
    print(f"  {brief['id']} chuyen trang thai → {WARN}cho_track_1{END}")
    print(f"\n{WARN}Track 1 tiep nhan:{END}")
    print(f"  python tools/track.py tham-dinh {sid} --ket-luan chua_dap_ung \\")
    print(f'      --bang-chung "GET /sources" "chua co nguon cho {a.du_lieu}"')
    return 0


def cmd_bao_cao(a: argparse.Namespace) -> int:
    """Ghi nhan ket qua phan tich. Bat buoc co so nguon trich dan."""
    spec = load(a.id.upper())
    bc = spec.setdefault("bao_cao", {})
    for k, v in (("duong_dan", a.duong_dan), ("luan_diem", a.luan_diem)):
        if v:
            bc[k] = v
    if a.so_nguon is not None:
        bc["so_nguon_trich_dan"] = a.so_nguon
    if a.rui_ro:
        bc.setdefault("rui_ro", []).extend(a.rui_ro)
    if a.chua_biet:
        bc.setdefault("dieu_chua_biet", []).extend(a.chua_biet)

    thieu = []
    if not bc.get("luan_diem"):
        thieu.append("luan diem")
    if not bc.get("so_nguon_trich_dan"):
        thieu.append("nguon trich dan")
    if not bc.get("rui_ro"):
        thieu.append("rui ro & phan bien")
    if not bc.get("dieu_chua_biet"):
        thieu.append("dieu chua biet")

    if thieu:
        print(f"{WARN}⚠ Bao cao chua du 4 phan bat buoc. Con thieu: "
              f"{', '.join(thieu)}{END}")
        spec["status"] = "dang_phan_tich"
    else:
        spec["status"] = "xong"
        print(f"{OK}✓ Bao cao day du 4 phan — {spec['id']} hoan thanh.{END}")
    save(spec)
    return 0 if not thieu else 1


# ------------------------------------------------------------------ CHUNG
def cmd_hang_doi(a: argparse.Namespace) -> int:
    t = a.track
    if t in (None, 1, "1"):
        print(f"\n{B}━━ TRACK 1 — PHAT TRIEN NEN TANG ━━{END}")
        asm = load_all("ASSESS")
        cho_td = [s for s in asm if s.get("ket_luan") == "chua_tham_dinh"]
        print(f"\n{WARN}Cho tham dinh ({len(cho_td)}){END}")
        for s in cho_td:
            print(f"  {s['id']}  {s['title'][:56]}")
        xong = [s for s in asm if s.get("ket_luan") not in (None, "chua_tham_dinh")]
        print(f"\n{DIM}Da tham dinh ({len(xong)}){END}")
        for s in xong:
            n = len(s.get("sinh_ra_req", []))
            print(f"  {s['id']}  {KET_LUAN.get(s['ket_luan'], '')[:34]:<36}"
                  f"{'→ ' + str(n) + ' REQ' if n else ''}")
        reqs = [r for r in load_all("REQ") if r.get("status") != "done"]
        print(f"\n{WARN}REQ dang mo ({len(reqs)}){END}")
        for r in sorted(reqs, key=lambda x: -(x.get("priority", {}).get("score", 0)))[:10]:
            sc = r.get("priority", {}).get("score", 0)
            cho = f" {BAD}[{len(r['cho_brief'])} BRIEF cho]{END}" if r.get("cho_brief") else ""
            print(f"  {r['id']}  diem {sc:>5}  {r['title'][:44]}{cho}")

    if t in (None, 2, "2"):
        print(f"\n{B}━━ TRACK 2 — THU THAP & PHAN TICH ━━{END}")
        for st, nhan in (("moi", "Moi nhan"), ("kiem_ke_du_lieu", "Dang kiem ke"),
                         ("cho_track_1", "⚠ CHO TRACK 1"), ("dang_thu_thap", "Dang thu thap"),
                         ("dang_phan_tich", "Dang phan tich"), ("xong", "Xong")):
            items = [b for b in load_all("BRIEF") if b.get("status") == st]
            if not items:
                continue
            mau = BAD if st == "cho_track_1" else (OK if st == "xong" else WARN)
            print(f"\n{mau}{nhan} ({len(items)}){END}")
            for b in items:
                cho = ""
                if b.get("sinh_ra_assess"):
                    cho = f"  {DIM}← {', '.join(b['sinh_ra_assess'])}{END}"
                print(f"  {b['id']}  {b['title'][:52]}{cho}")
    print()
    return 0


def cmd_lien_ket(a: argparse.Namespace) -> int:
    print(f"\n{B}SO DO LIEN KET HAI TRACK{END}\n")
    for b in load_all("BRIEF"):
        print(f"{B}{b['id']}{END} {b['title'][:54]}  {DIM}[{b.get('status')}]{END}")
        for sid in b.get("sinh_ra_assess", []):
            try:
                asm = load(sid)
            except FileNotFoundError:
                continue
            print(f"  └─ {sid}  {KET_LUAN.get(asm.get('ket_luan'), asm.get('ket_luan'))}")
            for rid in asm.get("sinh_ra_req", []):
                try:
                    r = load(rid)
                except FileNotFoundError:
                    continue
                mau = OK if r.get("status") == "done" else WARN
                print(f"      └─ {rid}  {mau}{r.get('status')}{END}  {r['title'][:40]}")
    doc_lap = [s for s in load_all("ASSESS") if not s.get("tu_brief")]
    if doc_lap:
        print(f"\n{DIM}Tham dinh doc lap (khong tu Track 2):{END}")
        for s in doc_lap:
            print(f"  {s['id']}  {s['title'][:56]}")
    print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Dieu phoi hai track — xem squad/00-charter/HAI-TRACK.md")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("yeu-cau", help="[T1] Gui yeu cau phat trien nen tang")
    p.add_argument("noi_dung", help="Nguyen van yeu cau, tieng Viet tu nhien")
    p.add_argument("--tieu-de")
    p.add_argument("--nguoi-gui", default="PO")
    p.add_argument("--kenh", default="chat",
                   choices=["chat", "github", "ui_build", "email", "khac"])
    p.add_argument("--giao-cho", default="BA",
                   choices=["BA", "RES", "ARCH", "PO", "QA", "AIE", "DE", "DOC"])
    p.add_argument("--tu-brief", help="Neu day nguoc tu Track 2")
    p.set_defaults(func=cmd_yeu_cau)

    p = sub.add_parser("tham-dinh", help="[T1] Doi phan tich tham dinh")
    p.add_argument("id")
    p.add_argument("--ket-luan", choices=list(KET_LUAN))
    p.add_argument("--bang-chung", nargs="+", metavar=("LENH", "KET_QUA"))
    p.add_argument("--thieu", nargs="+")
    p.add_argument("--huong-dan")
    p.add_argument("--thay-the")
    p.add_argument("--uu-tien", nargs=3, type=int,
                   metavar=("TAC_DONG", "TU_TIN", "CONG_SUC"))
    p.set_defaults(func=cmd_tham_dinh)

    p = sub.add_parser("chuyen-phat-trien", help="[T1] ASSESS -> REQ")
    p.add_argument("id")
    p.add_argument("--ket-qua", help="Ket qua mong doi")
    p.add_argument("--plane", default="ops", choices=["build", "ops", "both"])
    p.set_defaults(func=cmd_chuyen_phat_trien)

    p = sub.add_parser("de-bai", help="[T2] Giao de bai phan tich")
    p.add_argument("noi_dung")
    p.add_argument("--tieu-de")
    p.add_argument("--nguoi-gui", default="PO")
    p.add_argument("--loai", default="khac",
                   choices=["co_phieu", "nganh", "vi_mo", "bat_dong_san",
                            "danh_muc", "so_sanh", "khac"])
    p.add_argument("--doi-tuong", nargs="+")
    p.add_argument("--cau-hoi", nargs="+")
    p.add_argument("--han-chot")
    p.set_defaults(func=cmd_de_bai)

    p = sub.add_parser("kiem-ke", help="[T2] Kiem ke du lieu can vs co")
    p.add_argument("id")
    p.add_argument("--can", help="Ten du lieu can")
    p.add_argument("--trang-thai", default="chua_co_luong",
                   choices=["co_du", "co_nhung_cu", "chua_co_luong"])
    p.add_argument("--nguon")
    p.add_argument("--cap-nhat")
    p.add_argument("--hanh-dong")
    p.set_defaults(func=cmd_kiem_ke)

    p = sub.add_parser("day-track-1", help="[T2] Thieu luong -> day sang Track 1")
    p.add_argument("id")
    p.add_argument("--du-lieu", required=True)
    p.set_defaults(func=cmd_day_track_1)

    p = sub.add_parser("bao-cao", help="[T2] Ghi nhan ket qua phan tich")
    p.add_argument("id")
    p.add_argument("--duong-dan")
    p.add_argument("--luan-diem")
    p.add_argument("--so-nguon", type=int)
    p.add_argument("--rui-ro", nargs="+")
    p.add_argument("--chua-biet", nargs="+")
    p.set_defaults(func=cmd_bao_cao)

    p = sub.add_parser("hang-doi", help="Xem viec dang o dau")
    p.add_argument("--track", choices=["1", "2"])
    p.set_defaults(func=cmd_hang_doi)

    p = sub.add_parser("lien-ket", help="So do lien ket ASSESS/REQ/BRIEF")
    p.set_defaults(func=cmd_lien_ket)

    args = ap.parse_args()
    for d in KINDS.values():
        d["dir"].mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

"""Kiem thu hoi quy — moi test o day tuong ung MOT loi da xay ra that.

Chay duoc ca tren host (thieu httpx/fastapi thi tu bo qua) lan trong container.
    .venv/bin/python -m pytest tests/ -q
    docker compose exec -T api pytest tests/ -q
"""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

PY = sys.executable

# Module chuan cua Python — dat thu muc trung ten se pha vo import he thong
STDLIB_NAMES = {"platform", "types", "json", "io", "code", "test", "string",
                "select", "signal", "socket", "queue", "random", "copy"}


class TestKhongXungDotTenModule:
    """Package tung ten 'platform' -> pandas goi platform.system() bi hong."""

    def test_khong_co_thu_muc_trung_ten_module_chuan(self):
        vi_pham = [d.name for d in ROOT.iterdir()
                   if d.is_dir() and d.name in STDLIB_NAMES]
        assert not vi_pham, f"Thu muc trung ten module chuan: {vi_pham}"

    def test_platform_van_la_module_chuan(self):
        import platform as p
        assert p.system(), "platform.system() phai tra ve ten he dieu hanh"


class TestRegistryNapConnector:
    """f-string tro sai module + 'except: continue' -> khong connector nao duoc nap,
    nhung API van tra [] nhu the binh thuong. Loi im lang, rat kho tim."""

    def test_discover_tim_duoc_it_nhat_mot_connector(self):
        pytest.importorskip("httpx", reason="chi chay trong container co httpx")
        from vnir.connectors.registry import discover
        found = discover()
        assert found, "discover() rong — kiem tra ten module trong registry.py"
        assert "worldbank.vn_macro_indicators" in found

    def test_registry_khong_nuot_loi_im_lang(self):
        """Khoi except phai ghi log, khong duoc chi co 'continue'."""
        src = (ROOT / "vnir" / "connectors" / "registry.py").read_text(encoding="utf-8")
        i = src.find("except Exception")
        assert i != -1
        khoi = src[i:i + 400]
        assert "log" in khoi.lower(), "except phai ghi log truoc khi bo qua"

    def test_registry_tro_dung_ten_package(self):
        src = (ROOT / "vnir" / "connectors" / "registry.py").read_text(encoding="utf-8")
        assert "platform.connectors" not in src, "con tro toi package 'platform' da doi ten"
        assert "vnir.connectors" in src


class TestConnectorWorldBank:
    """World Bank timeout voi date= va per_page>100, tra 502 chap chon."""

    def test_khong_dung_tham_so_date_gay_timeout(self):
        """Chi cam `date` trong params cua request, khong lien quan row["date"] khi parse."""
        src = (ROOT / "vnir" / "connectors" / "worldbank_vn.py").read_text(encoding="utf-8")
        for ln in src.splitlines():
            if ln.lstrip().startswith("#") or "params" not in ln:
                continue
            assert '"date"' not in ln, f"tham so date= gay ReadTimeout: {ln.strip()}"

    def test_per_page_khong_vuot_100(self):
        src = (ROOT / "vnir" / "connectors" / "worldbank_vn.py").read_text(encoding="utf-8")
        for ln in src.splitlines():
            if '"per_page"' in ln and not ln.lstrip().startswith("#"):
                so = int(ln.split('"per_page"')[1].split(":")[1].split("}")[0].strip(" ,"))
                assert so <= 100, f"per_page={so} gay ReadTimeout, toi da 100"

    def test_chiu_loi_tung_phan_khi_mot_chi_so_hong(self):
        """Mot chi so tra 502 khong duoc lam hong ca lan chay."""
        src = (ROOT / "vnir" / "connectors" / "worldbank_vn.py").read_text(encoding="utf-8")
        assert "failed" in src and "continue" in src, "phai bo qua chi so hong"
        assert "if not results" in src, "phai bao loi khi TAT CA chi so that bai"


class TestSpecHopLe:
    def test_moi_spec_qua_duoc_kiem_dinh(self):
        r = subprocess.run([PY, "tools/spec_validate.py"],
                           cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, f"spec khong hop le:\n{r.stdout}{r.stderr}"

    def test_chi_muc_spec_dong_bo(self):
        """SPEC-INDEX.md sinh tu dong — sua tay se lech."""
        idx = ROOT / "specs" / "SPEC-INDEX.md"
        truoc = idx.read_text(encoding="utf-8") if idx.exists() else ""
        subprocess.run([PY, "tools/specctl.py", "index"],
                       cwd=ROOT, capture_output=True, text=True, check=True)
        assert idx.read_text(encoding="utf-8") == truoc, \
            "SPEC-INDEX.md lech — chay 'specctl.py index' roi commit lai"

    def test_moi_spec_co_id_duy_nhat(self):
        ids = []
        for f in (ROOT / "specs").rglob("*.yaml"):
            if "_schemas" in f.parts:
                continue
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
            if isinstance(d, dict) and d.get("id"):
                ids.append(d["id"])
        assert len(ids) == len(set(ids)), "co ID spec bi trung"

    def test_schema_component_cho_phep_field_github(self):
        """ghsync ghi nguoc so issue vao spec — schema phai chap nhan."""
        for ten in ("requirement", "component", "task"):
            s = json.loads((ROOT / "specs" / "_schemas" / f"{ten}.schema.json")
                           .read_text(encoding="utf-8"))
            assert "github" in s["properties"], f"{ten}.schema.json thieu field github"


class TestCongCuChayDuoc:
    @pytest.mark.parametrize("mod", ["spec_lib", "spec_validate", "specctl", "ghsync",
                                     "migrate_legacy_facts"])
    def test_import_duoc_moi_cong_cu(self, mod):
        importlib.import_module(mod)

    @pytest.mark.parametrize("args", [["validate"], ["list", "req"], ["list", "assess"], ["list", "brief"], ["index"]])
    def test_specctl_chay_khong_crash(self, args):
        r = subprocess.run([PY, "tools/specctl.py", *args],
                           cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 0, f"specctl {args} loi:\n{r.stdout}{r.stderr}"


class TestScriptBaoCaoCu:
    """ROOT tro vao scripts/ thay vi thu muc cha -> script chua bao gio chay duoc."""

    @pytest.mark.parametrize("ten", ["build_dashboard.py", "build_mindmap.py"])
    def test_script_cu_van_chay_va_giu_banner(self, ten):
        d = ROOT / "kinh-te-vn-2036"
        if not (d / "scripts" / ten).exists():
            pytest.skip("khong co script ke thua")
        r = subprocess.run([PY, f"scripts/{ten}"], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, f"{ten} loi:\n{r.stderr}"
        out = r.stdout + r.stderr
        f = next((Path(w) for w in out.split() if w.endswith(".html")), None)
        if f and f.exists():
            assert "ẢNH CHỤP LỊCH SỬ" in f.read_text(encoding="utf-8"), \
                "banner canh bao bi mat khi sinh lai HTML"


class TestDuLieuKeThua:
    def test_facts_ke_thua_co_canh_bao_do_tin_cay(self):
        f = ROOT / "context" / "facts" / "legacy-2024-2025.md"
        if not f.exists():
            pytest.skip("chua migrate")
        t = f.read_text(encoding="utf-8")
        assert "do_tin_cay: thap" in t
        assert "can_kiem_chung_lai: true" in t
        assert "CHƯA KIỂM CHỨNG" in t

    def test_bronze_co_manifest_truy_vet(self):
        """Moi lo du lieu tho phai co URL + sha256 + HTTP status."""
        ms = list((ROOT / "data" / "bronze").rglob("_manifest.json"))
        if not ms:
            pytest.skip("chua thu thap du lieu")
        m = json.loads(ms[0].read_text(encoding="utf-8"))
        assert m["files"], "manifest khong co file nao"
        for k in ("url", "sha256", "http_status"):
            assert k in m["files"][0], f"manifest thieu {k} — khong truy vet duoc"
        assert m["files"][0]["http_status"] == 200

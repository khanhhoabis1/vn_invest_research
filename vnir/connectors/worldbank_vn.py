"""Connector World Bank Open Data — chi so vi mo Viet Nam.

Endpoint DA KIEM CHUNG bang curl (HTTP 200):
    https://api.worldbank.org/v2/country/VNM/indicator/NY.GDP.MKTP.CD?format=json&per_page=200

Giay phep: CC BY 4.0 — duoc dung lai, chi can ghi nguon. legal_risk = low.
Khong can API key.
"""
from __future__ import annotations

import json

from vnir.connectors.base import BaseConnector, ConnectorError, FetchResult

# Bo chi so vi mo cot loi cho phan tich dau tu VN
INDICATORS: dict[str, tuple[str, str]] = {
    "NY.GDP.MKTP.CD":     ("GDP danh nghia", "USD hien hanh"),
    "NY.GDP.MKTP.KD.ZG":  ("Tang truong GDP thuc", "% nam"),
    "NY.GDP.PCAP.CD":     ("GDP binh quan dau nguoi", "USD"),
    "FP.CPI.TOTL.ZG":     ("Lam phat CPI", "% nam"),
    "FR.INR.LEND":        ("Lai suat cho vay", "%"),
    "NE.EXP.GNFS.ZS":     ("Xuat khau hang hoa & dich vu", "% GDP"),
    "NE.IMP.GNFS.ZS":     ("Nhap khau hang hoa & dich vu", "% GDP"),
    "BX.KLT.DINV.WD.GD.ZS": ("Von FDI vao rong", "% GDP"),
    "SP.POP.TOTL":        ("Dan so", "nguoi"),
    "SP.URB.TOTL.IN.ZS":  ("Ty le do thi hoa", "% dan so"),
    "SL.UEM.TOTL.ZS":     ("Ty le that nghiep", "% luc luong lao dong"),
    "GC.DOD.TOTL.GD.ZS":  ("No chinh phu", "% GDP"),
    "NY.GDS.TOTL.ZS":     ("Tiet kiem trong nuoc", "% GDP"),
    "NE.GDI.TOTL.ZS":     ("Tich luy tai san co dinh", "% GDP"),
}

BASE = "https://api.worldbank.org/v2/country/VNM/indicator/{code}"


class WorldBankVietnamConnector(BaseConnector):
    source_id = "worldbank"
    dataset = "vn_macro_indicators"
    title = "World Bank — Chi so vi mo Viet Nam"
    homepage = "https://data.worldbank.org/country/vietnam"
    schedule = "0 7 * * 1"            # thu 2 hang tuan (WB cap nhat theo quy/nam)
    legal_risk = "low"                 # CC BY 4.0
    requires_key = False
    freshness_sla_days = 400           # du lieu nam, do tre cong bo ~1 nam
    unit = "hon hop (xem tung chi so)"
    description = "14 chi so vi mo cot loi cua Viet Nam tu World Bank Open Data API v2."

    def fetch(self) -> list[FetchResult]:
        results: list[FetchResult] = []
        for code in INDICATORS:
            url = BASE.format(code=code)
            # Luu y: KHONG dung tham so `date=` — da kiem chung thuc te la
            # World Bank API bi timeout khi loc theo khoang nam. Lay het roi loc o parse().
            r = self.http_get(url, params={"format": "json", "per_page": 200})
            r.extra["indicator_code"] = code
            results.append(r)
        return results

    def parse(self, results: list[FetchResult]) -> list[dict]:
        records: list[dict] = []
        for r in results:
            code = r.extra.get("indicator_code", "?")
            try:
                payload = json.loads(r.content)
            except json.JSONDecodeError as exc:
                raise ConnectorError(f"Khong doc duoc JSON cho {code}: {exc}") from exc
            if not isinstance(payload, list) or len(payload) < 2:
                self.log.warning("Chi so %s khong co du lieu, bo qua", code)
                continue
            name_vi, unit = INDICATORS.get(code, (code, ""))
            for row in payload[1] or []:
                if row.get("value") is None:
                    continue
                records.append({
                    "indicator_code": code,
                    "indicator_vi": name_vi,
                    "indicator_en": (row.get("indicator") or {}).get("value", ""),
                    "unit": unit,
                    "country": "VNM",
                    "year": int(row["date"]),
                    "value": float(row["value"]),
                    "source_url": r.url,
                })
        records.sort(key=lambda x: (x["indicator_code"], x["year"]))
        self.log.info("Da phan tich %d quan sat tu %d chi so", len(records), len(INDICATORS))
        return records

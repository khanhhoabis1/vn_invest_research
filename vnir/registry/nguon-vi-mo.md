# Danh mục nguồn dữ liệu kinh tế vĩ mô Việt Nam

> Lập 09/08/2026, kiểm chứng bằng `curl` thực tế (HTTP status ghi trung thực).
> Không bịa endpoint nào; nguồn không API đều xác nhận bằng HTTP status trang gốc.

## 1. Bảng tổng hợp (catalog)

| # | Nguồn | Loại dữ liệu | Endpoint cơ sở | API? | HTTP status thực | Độ khó |
|---|-------|--------------|----------------|------|------------------|--------|
| 1 | **GSO PX-Web** | Dân số, CPI, thương mại, lao động | `pxweb.nso.gov.vn/api/v1/vi/` | ✅ POST JSON | 200 (dân số 2024 = 101.343,75 nghìn người) | 🟢 Thấp |
| 2 | **World Bank** | GDP, lạm phát, dân số, thương mại | `api.worldbank.org/v2/country/VNM/indicator/{code}` | ✅ | 200 (GDP VN 2022 = 413,4 tỷ USD) | 🟡 TB (hay 502) |
| 3 | **ADB KIDB** | GDP nội tệ, vĩ mô châu Á | `api.adb.org/data` (dataflow `ADB,KIDB`) | ✅ | 200 | 🟢 Thấp |
| 4 | **Our World in Data** | CO₂, dân số, GDP, năng lượng | `ourworldindata.org/grapher/{series}.csv` | ✅ CSV | 200 | 🟢 Thấp |
| 5 | **FRED** | Tỷ giá VND/USD (`DEXVNKUS`), lãi suất US | `api.stlouisfed.org/fred/series/observations` | ✅ cần key free | 400 (host sống, thiếu key) | 🟢 Thấp(sau key) |
| 6 | **Trading Economics** | Vĩ mô VN tổng hợp | `api.tradingeconomics.com` | ✅ cần token | 401 (cần token) | 🟡 TB |
| 7 | **UN Comtrade** | Thương mại quốc tế | `comtradeplus.un.org` | ✅ cần key free | 302→Comtrade+ (cần key) | 🟡 TB |
| 8 | **OECD SDMX** | So sánh quốc tế | `sdmx.oecd.org` | ✅ | 404 (sai dataflow) | 🟡 TB |
| 9 | **SBV (Ngân hàng Nhà nước)** | Tỷ giá, tín dụng, CSTT | `www.sbv.gov.vn` | ❌ HTML/XLSX | 200 | 🟡 TB (scrape) |
| 10 | **Bộ Tài chính** | Thuế, ngân sách, trái phiếu CP | `mof.gov.vn` | ❌ HTML/XLSX | 200 | 🟡 TB |
| 11 | **Tổng cục Hải quan** | Xuất nhập khẩu | `customs.gov.vn` | ❌ HTML/XLSX | 200 | 🟡 TB |
| 12 | **MOF FDI cổng** | Đầu tư trực tiếp nước ngoài | `vietnaminvest.mof.gov.vn` | ❌ HTML | 200 | 🟡 TB |
| 13 | **IMF SDMX** | Cơ sở tiền tệ, IFS | `sdmxrest.imf.org` | ✅ | 000 (không tới được từ IP test) | 🔴 Cao |
| 14 | **data.gov.vn** | Cổng dữ liệu quốc gia | `data.gov.vn` | ✅ (một phần) | 000 (có thể bị chặn ngoài VN) | 🔴 Cao |
| 15 | **MPI (Bộ KH&ĐT)** | Đầu tư, FDI | `mpi.gov.vn` | ❌ | 000 (dùng cổng MOF thay) | 🔴 Cao |

## 2. Điểm kỹ thuật

- **GSO PX-Web** là API chuẩn nhất nội địa: `POST` JSON chọn từng chiều (table, variable, time).
  Dễ tự động hóa nhất. VD lấy dân số: POST `pxweb.nso.gov.vn/api/v1/vi/.../Dân số`.
- **World Bank** phân trang `per_page`/`page` (dùng `per_page=100` ổn định; `200/300` timeout);
  mã VN: `NY.GDP.MKTP.CD`, `FP.CPI.TOTL.ZG`, `SP.POP.TOTL`. Hay trả 502 ngẫu nhiên → cần retry.
- Đồng nhất mã quốc gia khi gộp: `VNM` (WB/IMF), `VIE` (ADB/OECD), `704` (Comtrade).

## 3. Khuyến nghị vận hành

- Tự động hóa ngay: **GSO / World Bank / ADB / OWID** (API sẵn, không key).
- Đăng ký key free: **FRED** (tỷ giá VND/USD chuẩn), **UN Comtrade**, **Trading Economics** (nếu cần).
- Scrape XLSX/HTML: **SBV / Tài chính / Hải quan / FDI-MOF** (tần suất thấp, hàng tuần/tháng).
- Crawl vĩ mô VN chậm → mỗi tuần 1 lần là đủ.

## 4. Rủi ro

- IMF SDMX & data.gov.vn không bắt được từ IP test (000) → thử lại từ VPS/IP Việt Nam.
- World Bank 502 chập chờn → connector phải có retry + chịu lỗi từng phần.
- Bản quyền: số liệu tổng hợp nhà nước dùng được nghiên cứu; ghi rõ nguồn.

---
*Nguồn: squad khảo sát nguồn vĩ mô (kiểm chứng curl thực tế 15 nguồn), 09/08/2026.*

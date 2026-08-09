# Danh mục nguồn dữ liệu thị trường Chứng khoán & Bất động sản Việt Nam

> Lập 09/08/2026, kiểm chứng bằng `curl` thực tế. Nguồn trả `403 Cloudflare`/`000`
> là endpoint thật nhưng bị chặn tại IP máy test — thử lại từ VPS/IP Việt Nam.
> Nguồn chính chủ hợp pháp được ưu tiên làm backend.

## 1. Bảng tổng hợp (catalog)

| # | Nguồn | Loại dữ liệu | Endpoint cơ sở | API JSON? | Ví dụ endpoint | Độ khó |
|---|-------|--------------|----------------|-----------|----------------|--------|
| 1 | **KBS (KB Securities)** | Giá lịch sử, chỉ số, NN ròng, bảng giá | `kbbuddywts.kbsec.com.vn/iis-server/investment/` | ✅ 200 (cần header) | `/stocks/VND/data_day`, `/index/VNINDEX/data_day`, `/rtranking/foreignTotal` | 🟢 Thấp–TB |
| 2 | **VCI (Vietcap)** | Bảng giá realtime, chỉ số, BCTC, ICB | `trading.vietcap.com.vn/api/` + `iq.vietcap.com.vn/api/iq-insight-service/v1/` | ✅ gzip | `/price/symbols/getAll`, `/v1/market-indices`, `/v1/company/VNM/financial-statement` | 🟡 TB |
| 3 | **SSI FastConnect Data (chính chủ)** | Giá ngày, intraday, thông tin CK, NN ròng | `fc-data.ssi.com.vn/api/v2/Market/` | ✅ cần Bearer (free) | `/DailyStockPrice`, `/IntradayOhlc`, `/Securities` | 🟢 Thấp(sau đăng ký) |
| 4 | **FMarket** | Quỹ mở, NAV, top holding | `api.fmarket.vn/res/products/` | ✅ POST | `/filter`, `/get-nav-history` | 🟡 TB |
| 5 | **TCBS apipubaws** | Giá, công ty, intraday | `apipubaws.tcbs.com.vn/stock/v1/` | ✅ cộng đồng | `/company/VND`, `/intraday/VND/1` | 🟡 TB (CF 403) |
| 6 | **VNDirect (finfo/dchart)** | Giá lịch sử, chart | `finfo-api.vndirect.com.vn/v4/`, `dchart.vndirect.com.vn/du-lieu/` | ✅ cộng đồng | `/stock_prices/?q=code:VND`, `/LichSuGia/VND` | 🟡 TB (host không tới) |
| 7 | **MSN (Microsoft Money)** | Giá QT, crypto, forex | `assets.msn.com/service/Finance/` | ✅ (vnstock) | `/Charts/TimeRange` | 🟡 TB |
| 8 | **SJC / BTMC (vàng)** | Giá vàng | `sjc.com.vn/GoldPrice/Services/PriceService.ashx` | ⚠️ 403 CF | cùng URL | 🔴 Cao (CF) |
| 9 | **HOSE** | CBTT, giá, chỉ số | `www.hose.vn/` | ❌ web ASPX | `/Modules/...` | 🔴 Cao |
| 10 | **HNX / bond.hnx.vn** | CBTT, trái phiếu, giá HNX/UPCoM | `www.hnx.vn/`, `bond.hnx.vn/` | ❌ web | `/vi-vn/` | 🔴 Cao |
| 11 | **UBCKNN (SSC)** | CBTT chính thức | `www.ssc.gov.vn/` | ❌ web | `/` | 🔴 Cao |
| 12 | **VBMA** | Trái phiếu DN | `www.vbma.org.vn/` | ❌ web | `/` | 🔴 Cao |
| 13 | **batdongsan.com.vn** | Tin đăng BĐS, giá, dự án | `batdongsan.com.vn/` | ❌ scrape | listing | 🔴 Cao (CF) |
| 14 | **nhatot.com** | Tin đăng BĐS, xe | `www.nhatot.com/` | ❌ scrape | listing | 🔴 Cao (CF) |
| 15 | **cafeland.vn** | Tin đăng, dự án, bảng giá | `cafeland.vn/` | ❌ scrape | tin/dự án | 🟢 Thấp–TB |
| 16 | **vietstock.vn** | CK, BCTC, tin | `vietstock.vn/` | ❌ web | `/` | 🟡 TB |
| 17 | **fireant.vn** | CK, cộng đồng | `fireant.vn/` | ❌ web | `/` | 🟡 TB |
| 18 | **vnstock (thư viện PyPI)** | Tổng hợp | `pip install vnstock` | ✅ wrapper | `Market().equity.ohlcv(...)` | 🟢 Thấp |

## 2. Ghi chú kỹ thuật

- **KBS** ✅ tốt nhất, không key. Cần header `Referer/Origin: https://kbbuddywts.kbsec.com.vn`, response gzip (`--compressed`).
  - Lịch sử: `GET /iis-server/investment/stocks/{symbol}/data_day`
  - NN ròng: `GET /rtranking/foreignTotal` → `{FB,FS,FT}` (FT ròng)
- **VCI (Vietcap)** ✅ gzip. `GET trading.vietcap.com.vn/api/price/symbols/getAll`. BCTC: `iq.vietcap.com.vn/api/iq-insight-service/v1/company/{symbol}/financial-statement?section=income_statement`
- **SSI FastConnect** ✅ chính chủ, cần token free (đăng ký ssi.com.vn). Nguồn ổn định nhất cho warehouse dài hạn. `/DailyStockPrice?symbol=&market=&Fromdate=&Todate=` có `NetBuySellVal` (NN ròng chuẩn).
- **vnstock 4.0.5** (Requires-Python>=3.10): `Market().equity.ohlcv(symbol='VNM', start=..., end=...)`. Dùng prototype; warehouse lớn gọi trực tiếp KBS/VCI/SSI để kiểm soát rate-limit & lưu raw.

## 3. Cảnh báo pháp lý

1. KBS/VCI/TCBS/VNDirect/FMarket/SJC/MSN là API **không chính thức**; dữ liệu có bản quyền HOSE/HNX/SSC — chỉ dùng nghiên cứu cá nhân.
2. **SSI FastConnect** là nguồn **chính chủ hợp pháp** (có ToS) — ưu tiên backend.
3. Tôn trọng `Disallow`/`ToS` (vietstock cấm `/export`, fireant có điều khoản riêng, cafeland cấm `/ajax`).
4. Vượt CF (batdongsan/nhatot/SJC/TCBS) có thể vi phạm ToS & luật an ninh mạng.
5. Rate limit: ≤1–2 req/giây/source; crawl ngoài giờ ATC; cache để giảm tải.

## 4. Kiến trúc thu thập đề xuất

- Tầng 1 (giá/chỉ số/NN ròng): **SSI FastConnect** + **KBS** + **VCI** đối soát chéo.
- Tầng 2 (BCTC): **VCI iq-insight-service** + `vnstock Fundamental`.
- Tầng 3 (BĐS): crawler **cafeland.vn** + batdongsan/nhatot qua proxy; parser PDF CBRE/Savills/VBMA.
- Tầng 4: định kỳ lấy CBTT HOSE/HNX/SSC để validate. Lưu raw JSON → chuẩn hóa → warehouse (Postgres) kèm cờ `source`,`fetched_at`.

---
*Nguồn: tổng hợp từ squad khảo sát nguồn (kiểm chứng curl thực tế 30+ endpoint), 09/08/2026.*

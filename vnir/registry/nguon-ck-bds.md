# Danh mục nguồn dữ liệu thị trường Chứng khoán & Bất động sản Việt Nam (thu thập tự động)

> Tài liệu được lập ngày 09/08/2026. Mọi endpoint trong bảng đều được **kiểm chứng thực tế bằng `curl`** từ môi trường kiểm thử (macOS). Kết quả HTTP status và 200 ký tự đầu response được ghi nhận trung thực. Những nguồn trả về `403 Cloudflare` / `000` (không kết nối được từ IP của máy kiểm thử) vẫn là endpoint thật nhưng bị chặn tại mạng này — cần thử lại từ IP/VPS Việt Nam hoặc dùng proxy dân cư.

---

## 1. Bảng tổng hợp (catalog)

| # | Nguồn | Loại dữ liệu | URL / Endpoint cơ sở | API JSON? | Ví dụ endpoint đã thử | Tần suất | Rate limit (ghi nhận) | robots.txt / ToS | Độ khó |
|---|-------|--------------|----------------------|-----------|------------------------|----------|------------------------|------------------|--------|
| 1 | **KBS (KB Securities)** | Giá lịch sử, chỉ số, nước ngoài mua bán ròng, bảng giá | `https://kbbuddywts.kbsec.com.vn/iis-server/investment/` | ✅ Có (HTTP 200) | `/stocks/VND/data_day`, `/index/VNINDEX/data_day`, `/rtranking/foreignTotal` | Thực tế/ngày | Không rõ (thử nhiều request OK) | Không có robots ở host này | 🟢 Thấp–TB |
| 2 | **VCI (Vietcap)** | Bảng giá realtime, chỉ số, BCTC, ICB | `https://trading.vietcap.com.vn/api/` + `https://iq.vietcap.com.vn/api/iq-insight-service/v1/` | ✅ Có (gzip) | `/price/symbols/getAll`, `/v1/market-indices`, `/v1/company/VNM/financial-statement?section=` | Thực tế/ngày | Không rõ | Không có robots rõ ràng | 🟡 TB |
| 3 | **SSI FastConnect Data (chính thức)** | Giá ngày, intraday, thông tin CK, **nước ngoài mua bán ròng** | `https://fc-data.ssi.com.vn/api/v2/Market/` | ✅ Có (cần Bearer token) | `/DailyStockPrice`, `/IntradayOhlc`, `/Securities` | Ngày/intraday | Quota theo gói (miễn phí có hạn) | Chính thức, có ToS | 🟢 Thấp (sau đăng ký free) |
| 4 | **FMarket** | Quỹ mở, NAV, top holding | `https://api.fmarket.vn/res/products/` | ✅ Có (POST) | `/filter`, `/{fundId}`, `/get-nav-history` | Ngày | Không rõ | Không có | 🟡 TB |
| 5 | **TCBS apipubaws** | Giá, công ty, intraday | `https://apipubaws.tcbs.com.vn/stock/v1/` | ✅ (cộng đồng) | `/company/VND`, `/intraday/VND/1?page=0&size=5` | Thực tế/ngày | Không rõ | Không có | 🟡 TB (CF 403) |
| 6 | **VNDirect (finfo / dchart)** | Giá lịch sử, chart | `https://finfo-api.vndirect.com.vn/v4/`, `https://dchart.vndirect.com.vn/du-lieu/` | ✅ (cộng đồng) | `/stock_prices/?q=code:VND~from:..~to:..`, `/LichSuGia/VND?from=&to=` | Ngày | Không rõ | `www.vndirect.com.vn` 403 | 🟡 TB (host không tới được từ đây) |
| 7 | **MSN (Microsoft Money)** | Giá QT, crypto, forex (tham chiếu) | `https://assets.msn.com/service/Finance/` | ✅ (vnstock dùng) | `/Charts/TimeRange`, `/Cryptocurrency/chart` | Ngày | Có giới hạn ẩn | Không có | 🟡 TB |
| 8 | **SJC / BTMC (vàng)** | Giá vàng | `https://sjc.com.vn/GoldPrice/Services/PriceService.ashx` | ⚠️ (403 CF) | cùng URL | Ngày | Không rõ | `sjc.com.vn` 403 | 🔴 Cao (CF) |
| 9 | **HOSE** | CBTT, giá, chỉ số (nguồn gốc) | `https://www.hose.vn/` | ❌ (web ASPX) | `/Modules/...` | Ngày | InfoConnect (trả phí) | 302 Cloudflare | 🔴 Cao |
| 10 | **HNX** | CBTT, trái phiếu, giá HNX/UPCoM | `https://www.hnx.vn/`, `https://bond.hnx.vn/` | ❌ (web) | `/vi-vn/` | Ngày | Không có API public | không có robots (404) | 🔴 Cao |
| 11 | **UBCKNN (SSC)** | CBTT chính thức toàn thị trường | `https://www.ssc.gov.vn/` | ❌ (web) | `/` | Ngày | Không có API | 302 nginx | 🔴 Cao |
| 12 | **VBMA** | Trái phiếu doanh nghiệp | `https://www.vbma.org.vn/` | ❌ (web) | `/` | Tuần | Không có API | 526 tại thời điểm test | 🔴 Cao |
| 13 | **batdongsan.com.vn** | Tin đăng BĐS, giá, dự án | `https://batdongsan.com.vn/` | ❌ (scrape) | trang listing/chi tiết | Theo lịch | Cloudflare | `Allow: /` (có disallow 1 vài path) | 🔴 Cao (CF) |
| 14 | **nhatot.com** | Tin đăng BĐS, xe | `https://www.nhatot.com/` | ❌ (scrape) | trang listing | Theo lịch | Cloudflare | `Allow: /` (có disallow) | 🔴 Cao (CF) |
| 15 | **cafeland.vn** | Tin đăng, dự án, bảng giá | `https://cafeland.vn/` | ❌ (scrape) | trang tin/dự án | Theo lịch | Không có CF | `Allow: /` (disallow ajax/tìm kiếm) | 🟢 Thấp–TB |
| 16 | **vietstock.vn** | CK, BCTC, tin tức | `https://vietstock.vn/` | ❌ (web) | `/` | Ngày | Không có API public | `Disallow: /export /cache` ⚠️ | 🟡 TB |
| 17 | **fireant.vn** | CK, cộng đồng | `https://fireant.vn/` | ❌ (web) | `/` | Ngày | Không có API public | Content-Signal đặc biệt ⚠️ | 🟡 TB |
| 18 | **vnstock (thư viện)** | Tổng hợp tất cả above | PyPI `vnstock` | ✅ (wrapper) | `Market().equity.ohlcv(...)` | Theo lệnh | Phụ thuộc nguồn gốc | MIT (thư viện) | 🟢 Thấp |

---

## 2. Ghi chú kỹ thuật từng nguồn (đã curl thực tế)

### 2.1 KBS (KB Securities) — ✅ hoạt động tốt nhất, không cần key
Host `kbbuddywts.kbsec.com.vn` trả JSON trực tiếp, **không bị Cloudflare** tại môi trường test.
- Lịch sử cổ phiếu: `GET /iis-server/investment/stocks/{symbol}/data_day` (các khung: `data_1P,3P,5P,10P,15P,30P,45P,60P,120P,180P,240P,data_day,data_week,data_month`). Response thực tế: `{"symbol":"VND","data_day":[{"t":"2026-08-07 07:00","o":16600,"h":16900,"l":16600,"c":16650,"v":6884600}]}`.
- Chỉ số: `GET /iis-server/investment/index/{symbol}/data_day` (VD `VNINDEX`, `HNXINDEX`). Giá trả về dạng chuỗi.
- Nước ngoài mua bán ròng: `GET /iis-server/investment/rtranking/foreignTotal` → mảng `{SB,EX,FB,FS,FT,...}` (FB=mua, FS=bán, FT=ròng). **Đây là nguồn net foreign flow dễ lấy nhất.**
- Khớp theo giá / lịch sử khớp: `GET /iis-server/investment/trade/history/{symbol}` (tick tape).
- POST: `/stockinfo`, `/stock/iss`, `/stock/matched-by-price`, `/sector/stock`, `/stock/search/data`.
- SAS (dữ liệu công ty): `https://kbbuddywts.kbsec.com.vn/sas/kbsv-stock-data-store/stock/{symbol}/historical-quotes`.
- **Header gợi ý**: `Referer/Origin: https://kbbuddywts.kbsec.com.vn`. Response thường gzip → thêm `--compressed`.

### 2.2 VCI (Vietcap) — ✅ hoạt động, response gzip
- Bảng giá toàn thị trường: `GET https://trading.vietcap.com.vn/api/price/symbols/getAll` → mảng JSON khổng lồ (symbol, board HOSE/HNX/UPCOM, tên). **Phải `-H "Accept-Encoding: gzip"` hoặc `--compressed`** nếu không sẽ nhận bytes nén.
- Theo nhóm: `/price/symbols/getByGroup?group=...`; intraday: `/market-watch/LEData/getAll`.
- Chart OHLC: `POST /chart/OHLCChart/gap-chart`.
- **BCTC & định giá (quan trọng)**: `https://iq.vietcap.com.vn/api/iq-insight-service/v1/`
  - `/company/{symbol}/financial-statement?section=<balance_sheet|income_statement|cash_flow>` (lỗi 400 nếu thiếu `section`).
  - `/sectors/icb-codes` (phân ngành ICB), `/market-indices`, `/events`, `/v1/company/{symbol}/statistics-financial`.
- Header: `Referer/Origin: https://trading.vietcap.com.vn/`.

### 2.3 SSI FastConnect Data — ✅ chính thức, cần token miễn phí
API công bố tại `guide.ssi.com.vn/ssi-products/fastconnect-data/api-specs`. Base `https://fc-data.ssi.com.vn/api/v2/Market/`.
- `/Securities?pageIndex=&pageSize=&market=hose|hnx|upcom` (danh sách mã).
- `/DailyStockPrice?...&symbol=&market=&Fromdate=dd/mm/yyyy&Todate=` → **có `ForeignBuyVolTotal`, `ForeignSellVolTotal`, `NetBuySellVol/Val`** (nước ngoài ròng chuẩn).
- `/IntradayOhlc?Symbol=&Fromdate=&Todate=`.
- `/SecuritiesDetails?symbol=`.
- **Đều trả `{"message":"Missing Authorization header","status":401}`** khi không có token → endpoint thật, chỉ cần `Authorization: Bearer <token>` đăng ký free tại ssi.com.vn (Fast Connect). Đây là nguồn chính chủ, ổn định nhất cho kho dữ liệu dài hạn.

### 2.4 FMarket (quỹ mở)
`GET/POST https://api.fmarket.vn/res/products/filter` với body `{"page":0,"size":20,...}` trả 400 nếu thiếu tham số, nhưng host sống. Dùng lấy NAV, top holding, phân bổ ngành của quỹ. Quan trọng cho mảng "fund/ETF".

### 2.5 TCBS apipubaws, VNDirect finfo/dchart — ⚠️ bị chặn tại IP test
- TCBS: `https://apipubaws.tcbs.com.vn/stock/v1/company/VND` trả **403 Cloudflare** kể cả khi giả User-Agent/Referer. Từ IP Việt Nam bình thường endpoint này hoạt động và là chuẩn cộng đồng (vnstock các bản cũ dùng). Thử lại từ VPS VN.
- VNDirect `finfo-api.vndirect.com.vn` và `finfo.vndirect.com.vn` trả **000 (không phân giải/không kết nối** từ môi trường này) — có thể do firewall mạng test, không chứng tỏ endpoint sai. `dchart.vndirect.com.vn/du-lieu/LichSuGia/VND?from=2024-01-01&to=2024-01-05` trả **200** nhưng là SPA (dữ liệu nạp qua JSON nội bộ). Dùng làm nguồn dự phòng.

### 2.6 Sàn & cơ quan quản lý (HOSE/HNX/UPCoM/SSC/VBMA)
- `www.hose.vn` → 302 Cloudflare; `www.hnx.vn` → 302 redirect `/vi-vn/`; `www.upcom.vn` → 301 Cloudflare; `www.ssc.gov.vn` → 302 nginx; `www.vbma.org.vn` → 526 (origin lỗi tại test); `bond.hnx.vn` → 000.
- Các trang này là **nguồn gốc pháp lý** (CBTT, BCTC, TPDN) nhưng không mở API public; thu thập bằng crawler trang ASPX hoặc mua API chính chủ (HOSE InfoConnect, HNX Datafeed) — chi phí cao, độ khó lớn. Khuyên: lấy dữ liệu thô từ KBS/VCI/SSI, dùng sàn làm đối soát (reconcile) định kỳ.

### 2.7 Bất động sản
- **batdongsan.com.vn**, **nhatot.com**: site 403 Cloudflare, nhưng `robots.txt` (`www.nhatot.com/robots.txt`, `batdongsan.com.vn/robots.txt`) đều `Allow: /` → về nguyên tắc được phép crawl trang công khai, nhưng CF bắt buộc dùng proxy dân cư/headless browser. Trích xuất: tiêu đề, giá, diện tích, quận/huyện, tọa độ.
- **cafeland.vn**: truy cập **200**, `robots.txt Allow:/` (chỉ cấm `/ajax/*`, `/tim-kiem/`) → **mục tiêu scrape dễ nhất** hiện nay cho BĐS VN.
- **Không có API giá nhà chuẩn**. Chỉ số giá (repeat-sales) chỉ có ở báo cáo quý của **CBRE, Savills, JLL, Colliers, Batdongsan Insight** (PDF) → thu thập bán tự động qua email/DocParser.
- **Giá đất nhà nước**: "Bảng giá đất" 5 năm của từng tỉnh/thành phố công bố dạng **quyết định/PDF** trên Cổng TTĐT tỉnh & Sở TNMT → không có API trung ương; cần crawler theo tỉnh.
- **Quy hoạch**: một số tỉnh có cổng "thông tin quy hoạch" (dạng bản đồ số), dữ liệu không gian thường không mở API → crawl ảnh/GeoJSON thủ công.

### 2.8 robots.txt đã kiểm tra (thực tế)
| Site | Status | Nội dung chính |
|------|--------|----------------|
| cafef.vn | 200 | `User-agent: * Allow: /` (cho phép toàn bộ) |
| batdongsan.com.vn | 200 | `Allow: /`, disallow vài path HandlerWeb |
| www.nhatot.com | 200 | `Allow: /`, disallow `/user/`, `/nhan/`, param `q=` |
| vietstock.vn | 200 | `Disallow: /export /cache /manager` ⚠️ (cấm lấy data export) |
| cafeland.vn | 200 | `Allow: /`, disallow `/ajax/*`, `/tim-kiem/` |
| fireant.vn | 200 | Điều khoản "Content-Signal" đặc biệt ⚠️ (có điều kiện) |
| hnx.vn | 404 | Không có robots.txt |
| hose.vn | 302 | Bị Cloudflare, không đọc được |

---

## 3. Thư viện `vnstock` (PyPI) — khuyên dùng làm tầng truy cập

- **Phiên bản mới nhất đã xác thực**: **4.0.5** (PyPI, `Requires-Python >=3.10`). Tóm tắt: "beginner-friendly yet powerful Python toolkit for financial analysis".
- **Cài đặt**: `pip install vnstock` (hoặc `uv pip install vnstock`).
- **Cách dùng cơ bản (Unified UI)**:
  ```python
  from vnstock import Market, Reference, Fundamental

  # Lịch sử giá (OHLCV)
  df = Market().equity.ohlcv(symbol='VNM', start='2024-01-01', end='2024-05-01')
  # Bảng giá realtime / intraday
  df_q = Market().equity.quote(symbol='VND')
  # Hồ sơ công ty
  df_info = Reference().company.info(symbol='FPT')
  # Báo cáo tài chính
  df_bs = Fundamental().equity.balance_sheet(symbol='TCB', period='year')
  df_is = Fundamental().equity.income_statement(symbol='TCB', period='quarter')
  # Chỉ số, ETF, trái phiếu, vàng, tỷ giá, crypto đều có sẵn
  ```
- **Nguồn dữ liệu thực tế bên dưới (trích từ source v4.0.5)**: KBS, VCI (Vietcap), MSN (Microsoft Money), FMarket, DNSE, SJC, Vietcombank, BTMC. Một số nguồn mới yêu cầu API key miễn phí tại `vnstocks.com`.
- **Lời khuyên kho dữ liệu**: Dùng `vnstock` để prototype nhanh, nhưng với warehouse quy mô lớn hãy gọi **trực tiếp** các endpoint §2.1–2.3 (KBS/VCI/SSI) để kiểm soát rate-limit, lưu raw JSON, và không phụ thuộc vào chuẩn đổi tên của thư viện.

---

## 4. Cảnh báo pháp lý & tuân thủ

1. **Không phải nguồn chính chủ**: KBS, VCI, TCBS, VNDirect, FMarket, SJC, MSN đều là API **không chính thức / không được cấp phép công bố** dữ liệu chứng khoán. Dữ liệu có bản quyền của HOSE/HNX/UBCKNN. Chỉ dùng cho **nghiên cứu cá nhân**, không dùng thương mại hay phân phối lại mà chưa có giấy phép từ đơn vị quản lý.
2. **SSI FastConnect** là nguồn **chính chủ, hợp pháp** (có ToS, cần token) — ưu tiên dùng làm backend pháp lý vững chắc.
3. **robots.txt & ToS**: đã ghi nhận `vietstock.vn` cấm `/export`, `fireant.vn` có điều khoản Content-Signal riêng, `cafeland.vn` cấm `/ajax`. Tôn trọng `Disallow` và `ToS` của từng site; nếu crawl, giữ tốc độ thấp, có User-Agent nhận diện, và cung cấp cách liên hệ.
4. **Cloudflare / anti-bot**: vượt CF (batdongsan, nhatot, SJC, TCBS) bằng proxy dân cư hoặc headless browser có thể vi phạm ToS của họ và luật an ninh mạng — cân nhắc rủi ro trước khi triển khai quy mô lớn.
5. **Dữ liệu BĐS**: tin đăng là nội dung người dùng (UGC) có bản quyền của sàn; trích xuất để phân tích nội bộ thường được chấp nhận, nhưng đăng tải lại/monetize cần xin phép.
6. **Báo cáo CBRE/Savills/JLL/Colliers/VBMA**: tài liệu có bản quyền, chỉ dùng trích dẫn/trích xuất số liệu cho nghiên cứu, ghi rõ nguồn.
7. **Rate limit & lịch trình**: không gọi quá 1–2 req/giây/source; đặt crawl vào ngoài giờ ATC (sau 15:00 và cuối tuần cho dữ liệu ngày); cache để giảm tải.

---

## 5. Khuyến nghị kiến trúc thu thập

- **Tầng 1 (giá & chỉ số & foreign flow)**: ưu tiên **SSI FastConnect (chính chủ)** + **KBS (không key)** + **VCI** làm đối soát chéo.
- **Tầng 2 (BCTC, công ty)**: **VCI iq-insight-service** (`/financial-statement`, `/statistics-financial`) + `vnstock Fundamental`.
- **Tầng 3 (BĐS)**: crawler **cafeland.vn** (dễ) + **batdongsan/nhatot** qua proxy dân cư; parsing PDF báo cáo CBRE/Savills/VBMA.
- **Tầng 4 (đối soát)**: định kỳ lấy CBTT từ HOSE/HNX/SSC để validate.
- Lưu raw JSON → chuẩn hóa → warehouse (Parquet/Postgres); thêm cờ `source` và `fetched_at` để truy xuất nguồn.

*Kết quả curl gốc (HTTP status + 200 ký tự đầu) của mọi endpoint trên có thể tái hiện bằng các script đã chạy trong quá trình kiểm thử (`verify*.sh` tại thư mục làm việc).*

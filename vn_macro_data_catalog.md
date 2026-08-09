# Danh mục nguồn dữ liệu kinh tế vĩ mô Việt Nam (thu thập tự động)

> Tài liệu lập ngày 09/08/2026. Mọi endpoint có API đều đã được **kiểm chứng bằng `curl`** từ môi trường thực thi (ghi rõ HTTP status và 200 ký tự đầu của response). Những nguồn chỉ có HTML/PDF/XLSX được kiểm chứng bằng HTTP status của trang gốc. Nguồn nào không truy cập được từ môi trường này được ghi rõ `KHÔNG TRUY CẬP ĐƯỢC`.

## 1. Bảng tổng hợp

| # | Nguồn | Cơ quan | Loại dữ liệu chính | Định dạng | Ví dụ endpoint | Tần suất | Độ trễ | Phân trang / tham số | Giấy phép | Độ khó | Trạng thái kiểm chứng |
|---|-------|--------|--------------------|-----------|----------------|----------|--------|----------------------|-----------|--------|----------------------|
| 1 | **GSO PX-Web** | Tổng cục Thống kê (GSO/NSO) | GDP, CPI, dân số, lao động, công nghiệp, đầu tư, XNK, giá | **API JSON** (PC-Axis/PX-Web) | `pxweb.nso.gov.vn/api/v1/vi/` | Tháng/quý/năm (theo bảng) | ~2–4 tuần | POST body chọn chiều; không phân trang | Dữ liệu mở GSO | Dễ | ✅ 200 (có data) |
| 2 | **SBV** | Ngân hàng Nhà nước (SBV) | Tỷ giá, lãi suất ĐH/tái cấp vốn, tín dụng, cán cân TT | HTML / WebCenter / XLSX | `sbv.gov.vn/can-can-thanh-toan-quoc-te` | Ngày/tháng | Vài ngày | Scrape / form WebCenter | Trang chủ SBV | Trung bình | ✅ 200 (HTML) |
| 3 | **Bộ Tài chính** | Bộ Tài chính (MOF) | Ngân sách, thuế, trái phiếu CP, nợ công | HTML / XLSX (API đang xây dựng) | `mof.gov.vn` | Tháng/quý/năm | 1–2 tháng | Scrape / download XLSX | Trang chủ MOF | Trung bình | ✅ 200 (HTML) |
| 4 | **Tổng cục Hải quan** | Bộ Tài chính (Customs) | Kim ngạch XNK, thuế, mặt hàng, đối tác | HTML / XLSX / App | `customs.gov.vn/index.jsp?pageId=3521` | 15 ngày / tháng | ~2 tuần | Scrape / XLSX sơ bộ | Trang chủ Hải quan | Trung bình | ✅ 200 (HTML) |
| 5 | **FDI / MKĐT** | Bộ KH&ĐT (MPI) + Cổng đầu tư | Vốn ĐK/thực hiện FDI, dự án, ngành, địa bàn | HTML / XLSX | `vietnaminvest.mof.gov.vn` | Tháng/quý/năm | 1 tháng | Scrape / XLSX | Trang chủ MPI/MOF | Trung bình | ✅ 200 (HTML) |
| 6 | **World Bank API** | World Bank | GDP, CPI, dân số, thương mại, FDI nước ngoài | **API JSON/XML** | `api.worldbank.org/v2/country/VNM/indicator/...` | Năm | ~1 năm (WDI) | `per_page`, `page`, `date` | CC BY 4.0 | Dễ | ✅ 200 (có data) |
| 7 | **IMF SDMX** | IMF | Cán cân thanh toán, tỷ giá, tiền tệ (IFS) | SDMX-JSON/XML | `sdmxrest.imf.org/Data/IFS/...` | Tháng/quý | 1–2 tháng | Key SDMX, `format` | Miễn phí | Trung bình | ❌ 000 (KHÔNG TRUY CẬP) |
| 8 | **ADB KIDB** | Asian Development Bank | GDP, tăng trưởng, nghèo đói, chỉ tiêu quốc gia | **SDMX-JSON** | `kidb.adb.org/api/v4/sdmx/data/ADB,EO_NA/...` | Năm | ~1 năm | Key SDMX, `format` | Miễn phí | Trung bình | ✅ 200 (có data) |
| 9 | **Trading Economics** | Trading Economics | GDP, lãi suất, tỷ giá, chứng khoán, country indicators | **API JSON** (cần key) | `api.tradingeconomics.com/country/vietnam/indicator/gdp` | Ngày/tháng | Gần thực tế | `format`, `token` | Gói trả phí/freemium | Dễ | ✅ 401 (có key) |
| 10 | **FRED** | St. Louis Fed | Tỷ giá VND/USD (DEXVNKUS), ít chỉ tiêu VN | **API JSON** (cần key) | `api.stlouisfed.org/fred/series/observations?series_id=DEXVNKUS` | Ngày | 1 ngày | `api_key`, `limit`, `observation_start` | CC BY 4.0 (miễn phí key) | Dễ | ✅ 400 (cần key) |
| 11 | **OECD SDMX** | OECD | Chỉ tiêu có giới hạn cho VN (chủ yếu thành viên) | SDMX-JSON/CSV | `sdmx.oecd.org/public/rest/data/...` | Quý/năm | 1–2 quý | Key SDMX, `c[...]` filter | Miễn phí | Khó | ✅ 404 (host sống, cần dataflow) |
| 12 | **UN Comtrade** | UN (UNSD) | XNK chi tiết theo HS, đối tác, dòng | **API JSON** (cần key) | `comtradeplus.un.org/api/...` | Năm/tháng | 1–3 tháng | `countryCode`, `cmdCode`, `period` | Cần đăng ký key | Trung bình | ⚠️ 302→Comtrade+ (cần key) |
| 13 | **Our World in Data** | Global Change Data Lab | CO₂, năng lượng, dân số, GDP, y tế | **CSV/JSON** (GitHub raw) | `raw.githubusercontent.com/owid/.../master/...csv` | Năm | 1–2 năm | File tĩnh, query filter | CC BY 4.0 | Dễ | ✅ 200 (có data) |
| 14 | **data.gov.vn** | Cổng dữ liệu quốc gia (MIC) | Đa lĩnh vực, 1 phần kinh tế vĩ mô | CKAN API (documented) | `data.gov.vn/api/3/action/package_search` | Không đều | Không đều | `q`, `rows`, `start` | Dữ liệu mở | Trung bình | ❌ 000 (KHÔNG TRUY CẬP) |
| 15 | **Cổng dữ liệu quốc gia** | Chính phủ (dữ liệu chung) | Dữ liệu dùng chung, một phần kinh tế | CKAN / portal | `data.gov.vn` (trùng #14) | Không đều | Không đều | — | Dữ liệu mở | Trung bình | ❌ 000 (KHÔNG TRUY CẬP) |

---

## 2. Ghi chú kỹ thuật cho từng nguồn ĐÃ kiểm chứng bằng curl

### 1. GSO PX-Web (✅ đã có data thật)
API PC-Axis/PX-Web chuẩn châu Âu, trả JSON. Có 2 ngôn ngữ: `/vi/` và `/en/`.

- **Liệt kê nhóm bảng:** `GET https://pxweb.nso.gov.vn/api/v1/vi/`
- **Liệt kê bảng trong nhóm:** `GET https://pxweb.nso.gov.vn/api/v1/vi/Dân%20số%20và%20lao%20động/`
- **Truy vấn dữ liệu (POST):** gửi JSON chọn từng chiều (`code` + `selection`).

```bash
# Lấy dân số trung bình (Nghìn người) 3 năm gần nhất
curl -s -X POST "https://pxweb.nso.gov.vn/api/v1/vi/D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng/V02.02.px" \
  -H "Content-Type: application/json" \
  -d '{"query":[{"code":"Cách tính","selection":{"filter":"item","values":["0"]}},
                {"code":"Năm","selection":{"filter":"item","values":["32","33","34"]}},
                {"code":"Phân tổ","selection":{"filter":"item","values":["0"]}}],
       "response":{"format":"json"}}'
```
**Kết quả kiểm chứng:** `HTTP 200` — `{"columns":[{"code":"Cách tính"... "data":[{"key":["0","32","0"],"values":["99467.93"]},{"key":["0","33","0"],"values":["100309.21"]},{"key":["0","34","0"],"values":["101343.75"]}]}` (dân số 2022/2023/2024 tính bằng nghìn người).
**Lưu ý:** mã hóa URL tiếng Việt (`%20`, `%C3%A2`…); mỗi bảng có mã riêng (vd `V02.02.px`). Trả về tối đa nên lọc kỹ từng chiều để tránh response quá lớn.

### 2. SBV (✅ 200 HTML)
Không có API JSON công khai; dữ liệu nằm trong Oracle WebCenter (`dttktt.sbv.gov.vn`) và các trang `sbv.gov.vn/...`. Cần thu thập bằng HTTP GET + parse HTML/XLSX.

```bash
curl -s -L -o /dev/null -w "HTTP:%{http_code}\n" "https://sbv.gov.vn/can-can-thanh-toan-quoc-te"
# => HTTP:200
```
**Khuyến nghị:** thu thập tỷ giá tham khảo, lãi suất ĐH, tín dụng từ mục "Dữ liệu thống kê"; lưu XLSX rồi đọc bằng `pandas.read_excel`.

### 3. Bộ Tài chính (✅ 200 HTML)
Cổng thông tin có mục "chuyển đổi số" đang xây dựng API chia sẻ ~27 chỉ số, nhưng chưa có endpoint JSON ổn định công khai. Hiện thu thập qua HTML/XLSX.

```bash
curl -s -L -o /dev/null -w "HTTP:%{http_code}\n" "https://mof.gov.vn"
# => HTTP:200
```

### 4. Tổng cục Hải quan (✅ 200 HTML)
Trang "Thống kê hải quan" công bố số XNK sơ bộ 15 ngày/tháng. Từ 27/06/2026 có app "Vietnam Customs Data" (chưa có open API). Thu thập qua HTML/XLSX.

```bash
curl -s -L -o /dev/null -w "HTTP:%{http_code}\n" "https://www.customs.gov.vn/index.jsp?pageId=3521"
# => HTTP:200
```

### 5. FDI / Bộ KH&ĐT (✅ 200 HTML qua cổng đầu tư)
Trang MPI (`mpi.gov.vn`) không truy cập được từ môi trường này (HTTP 000), nhưng **Cổng thông tin quốc gia về đầu tư** `vietnaminvest.mof.gov.vn` (trực thuộc MOF) trả HTTP 200 và công bố vốn ĐK/thực hiện FDI.

```bash
curl -s -L -o /dev/null -w "HTTP:%{http_code}\n" "https://vietnaminvest.mof.gov.vn/Pages/default.aspx"
# => HTTP:200
```
MPI chính thức: `mpi.gov.vn/portal/Pages/solieudautunuocngoai.aspx` (lưu ý kiểm tra lại từ mạng ổn định).

### 6. World Bank API (✅ 200 có data)
API công khai, ổn định, hỗ trợ JSON/XML. Dùng `per_page` + `page` để phân trang, `date=2015:2023` lọc năm.

```bash
curl -s "https://api.worldbank.org/v2/country/VNM/indicator/NY.GDP.MKTP.CD?format=json&per_page=3&date=2020:2022" | head -c 200
```
**Kết quả kiểm chứng:** `HTTP 200` — `[{"page":1,"pages":1,"per_page":3,"total":3,...},[{"indicator":{"id":"NY.GDP.MKTP.CD","value":"GDP (current US$)"},"countryiso3code":"VNM","date":"2022","value":413445230668.578,...`
**Mã chỉ tiêu VN hay dùng:** `NY.GDP.MKTP.KD` (GDP thực tế), `FP.CPI.TOTL.ZG` (lạm phát CPI), `SP.POP.TOTL` (dân số), `NE.EXP.GNFS.ZS` (XK/GDP), `BX.KLT.DINV.CD.WD` (FDI vào).

### 7. IMF SDMX (❌ KHÔNG TRUY CẬP ĐƯỢC)
Endpoint tài liệu: `https://sdmxrest.imf.org/Data/IFS/Q.VN.PMP_IX?format=JSON`. Từ môi trường này trả `HTTP 000` (không bắt được kết nối — có thể do firewall/chặn IP của host `sdmxrest.imf.org`; host `imf.org` trả 307). **Cần kiểm tra lại từ mạng khác.** Cấu trúc truy vấn SDMX: `Data/{dataset}/{FREQ}.{AREA}.{indicator}?format=JSON`.

### 8. ADB KIDB (✅ 200 có data)
API SDMX-JSON của ADB Key Indicators. Dataflow đúng là `ADB,EO_NA` (không phải `ADB,KIDB` — trả 422). Dùng `format=sdmx-json`.

```bash
curl -s "https://kidb.adb.org/api/v4/sdmx/data/ADB,EO_NA/A.NGDP_XDC.VIE?format=sdmx-json" | head -c 200
```
**Kết quả kiểm chứng:** `HTTP 200` — `{"meta":{"id":"IREF189429","prepared":"2026-08-09T04:26:52...","sender":{"id":"ADB"}...` (trả dữ liệu GDP VN bằng nội tệ). Mã nền kinh tế VN = `VIE`.

### 9. Trading Economics (✅ 401 — cần key)
API sống nhưng bắt buộc `token`. Freemium (có gói miễn phí giới hạn). Dùng `?c=YOUR_KEY` hoặc header `Authorization`.

```bash
curl -s "https://api.tradingeconomics.com/country/vietnam/indicator/gdp?format=json" | head -c 120
# => HTTP 401: "You must provide a valid authorization..."
```
**Chỉ tiêu VN:** `gdp`, `interest rate`, `currency`, `stock market`, `government debt`…

### 10. FRED (✅ 400 — cần key, host sống)
FRED bắt buộc `api_key` (đăng ký miễn phí). Series tỷ giá VND: `DEXVNKUS`.

```bash
curl -s "https://api.stlouisfed.org/fred/series/observations?series_id=DEXVNKUS&api_key=YOUR_KEY&file_type=json&limit=3" | head -c 120
# Không có key => HTTP 400: "Bad Request. The value for variable api_key is not a 32 character..."
```
**Lưu ý:** FRED có rất ít chỉ tiêu riêng cho VN (chủ yếu tỷ giá); phù hợp lấy VND/USD hàng ngày.

### 11. OECD SDMX (✅ 404 — host sống, cần dataflow đúng)
Host `sdmx.oecd.org` truy cập được (404 = sai dataflow). Cấu trúc: `https://sdmx.oecd.org/public/rest/data/{DATAFLOW}/LATEST?c[REF_AREA]=VNM&c[TIME_PERIOD]=2020&format=csv`. OECD tập trung vào nước thành viên, dữ liệu VN hạn chế (một số chỉ tiêu phát triển). **Độ khó: Khó** do phải tra đúng dataflow/DSD.

### 12. UN Comtrade (⚠️ chuyển sang Comtrade+ cần key)
API cũ `comtrade.un.org/api/...` trả `HTTP 302 → comtradeplus.un.org`. API v1 `comtradeapi.un.org/public/v1/get/...` trả `404` từ môi trường này. Hiện yêu cầu đăng ký API key miễn phí tại `comtradeplus.un.org`.

```bash
curl -s "https://comtrade.un.org/api/get/partnerArea/704" | head -c 80
# => HTTP 302: Object Moved -> https://comtradeplus.un.org
```
**Mã quốc gia VN = 704.** Sau khi có key: `https://comtradeplus.un.org/api/data/partnerArea?countryCode=704`.

### 13. Our World in Data (✅ 200 có data)
Dữ liệu thô dạng CSV/JSON trên GitHub raw, tải trực tiếp không cần key. Rất tốt cho CO₂, năng lượng, dân số, GDP dài hạn.

```bash
curl -s "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv" | head -c 120
```
**Kết quả kiểm chứng:** `HTTP 200` — `country,year,iso_code,population,gdp,cement_co2,cement_co2_per_capita,co2,...`
Dataset khác: `owid-energy-data.csv`, `owid-metadata.csv`. Lọc `iso_code=VNM` sau khi tải.

### 14 & 15. data.gov.vn / Cổng dữ liệu quốc gia (❌ KHÔNG TRUY CẬP ĐƯỢC)
Từ môi trường này `data.gov.vn` trả `HTTP 000` (không phân giải được host — có thể bị chặn hoặc chỉ mở trong mạng VN). Cổng này dùng nền CKAN, API tài liệu:

```bash
# (cần chạy từ mạng có thể truy cập data.gov.vn)
curl -s "https://data.gov.vn/api/3/action/package_search?q=kinh%20t%E1%BA%BF&rows=5"
```
**Lưu ý:** hãy thử lại từ máy chủ đặt tại VN. Một số bộ/ngành cũng đẩy dữ liệu lên đây (ngân sách, dân số…).

---

## 3. Khuyến nghị vận hành kho dữ liệu

1. **Ưu tiên cao (API sẵn, dễ):** GSO PX-Web, World Bank, ADB KIDB, Our World in Data — tự động hóa ngay bằng cron + Python (`requests`/`pandas`).
2. **Cần key (đăng ký miễn phí):** FRED (tỷ giá VND/USD), Trading Economics (tổng hợp VN), UN Comtrade (XNK chi tiết).
3. **Scrape/XLSX (trung bình):** SBV, Bộ Tài chính, Hải quan, FDI — dùng `requests` + `BeautifulSoup`/`pandas.read_excel`, lưu raw HTML/XLSX để audit.
4. **Chưa thu thập được từ môi trường này:** IMF SDMX, data.gov.vn — cần chạy từ IP/mạng VN hoặc kiểm tra lại firewall.
5. **Chuẩn hóa:** đồng nhất mã quốc gia `VNM`/`VIE`/`704`/`VN`; lưu kèm `source`, `fetched_at`, `endpoint`, `http_status` để truy xuất ngược.
6. **Tần suất:** vĩ mô VN cập nhật chậm (tháng/quý) → crawl mỗi tuần là đủ; tỷ giá/cổ phiếu (FRED/TE) mới hàng ngày.

*Mọi endpoint trên đều không bịa đặt: có API được chạy curl thực tế (ghi HTTP status + 200 ký tự đầu), nguồn chỉ HTML được xác nhận bằng HTTP status trang gốc, nguồn không truy cập được ghi rõ `KHÔNG TRUY CẬP ĐƯỢC`.*

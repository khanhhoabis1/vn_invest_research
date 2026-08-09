# SQUAD CHARTER — "VN Macro & Market Data Squad"

> Bản hiến chương của đội. Mọi tranh cãi về phạm vi, ưu tiên, quyền quyết định → quay về file này.
> Thay đổi charter phải qua ADR (`squad/03-decisions/`).

## 1. Lý do tồn tại (Mission)

Xây dựng và vận hành **một kho dữ liệu kinh tế Việt Nam (vĩ mô + vi mô) đáng tin cậy, tự cập nhật,
và đọc được bởi cả người lẫn LLM**, phục vụ ra quyết định đầu tư chứng khoán và bất động sản.

Chúng ta không phải team làm báo cáo. Chúng ta là team làm **hạ tầng ra quyết định**:
báo cáo chỉ là output cuối của một dây chuyền dữ liệu có kiểm chứng.

## 2. Nguyên tắc bất di bất dịch (Non-negotiables)

| # | Nguyên tắc | Ý nghĩa vận hành |
|---|-----------|------------------|
| P1 | **Không có số liệu không nguồn** | Mọi con số trong `gold/` và mọi báo cáo phải trace được về `bronze/` + URL gốc + thời điểm tải. Không trace được ⇒ không dùng. |
| P2 | **Bronze là bất biến** | Dữ liệu thô tải về không bao giờ sửa. Sai thì tải lại thành snapshot mới, giữ nguyên bản cũ. |
| P3 | **LLM không được bịa** | Agent chỉ trả lời từ `context/` và `gold/`. Không có dữ liệu ⇒ nói "chưa có", tạo ticket, không suy đoán. |
| P4 | **Mọi yêu cầu đều thành ticket** | Yêu cầu nói mồm/chat không tồn tại. Vào `intake/inbox/` → thành ticket YAML → mới được làm. |
| P5 | **Tài liệu là code** | Docs nằm cùng repo, version bằng git, có template, và được build sang dạng LLM-ready mỗi lần đổi. |
| P6 | **Quyết định phải để lại vết** | Mỗi lựa chọn kiến trúc/nguồn dữ liệu/luận điểm đầu tư ⇒ 1 ADR. Đổi ý ⇒ ADR mới supersede, không xoá ADR cũ. |
| P7 | **Hợp pháp & lịch sự với nguồn** | Tôn trọng robots.txt/ToS, rate limit, có User-Agent định danh, cache để không đập nguồn. Nguồn nào rủi ro pháp lý ⇒ đánh dấu `legal_risk` và phải có ADR mới bật. |
| P8 | **Thất bại phải ồn ào** | Pipeline lỗi/nguồn chết/dữ liệu cũ quá hạn ⇒ báo động, không âm thầm trả số cũ. |

## 3. Phạm vi (In / Out)

**In scope**
- Dữ liệu vĩ mô VN: GDP, CPI, tỷ giá, lãi suất, tín dụng, cung tiền, FDI, XNK, ngân sách, nợ công, dân số, lao động.
- Dữ liệu thị trường: giá & thanh khoản cổ phiếu, chỉ số, khối ngoại, BCTC doanh nghiệp niêm yết, CBTT, trái phiếu DN.
- Dữ liệu BĐS: chỉ số giá/nguồn cung/hấp thụ theo tỉnh & phân khúc, giá đất nhà nước, quy hoạch – hạ tầng.
- Dữ liệu ngành & chuỗi cung ứng (kế thừa `vingroup/`, `sungroup/`, `tong-hop/`).
- Bối cảnh định tính: chính sách, luật, nghị định, quy hoạch, tin ngành — được chuẩn hoá thành fact có nguồn.

**Out of scope (hiện tại)**
- Khuyến nghị đầu tư cho bên thứ ba (đây là kho nghiên cứu cá nhân/nội bộ).
- Giao dịch tự động / kết nối lệnh.
- Dữ liệu cá nhân, dữ liệu mua bán có bản quyền chưa được cấp phép.
- Dữ liệu real-time dưới 1 phút (thiết kế hiện tại là batch + near-real-time theo ngày/giờ).

## 4. Định nghĩa Hoàn thành (Definition of Done)

Một hạng mục chỉ được coi là XONG khi đủ **cả 6**:
1. Có **data contract** trong `platform/contracts/` (schema, khoá, đơn vị, tần suất, SLA độ trễ).
2. Có **connector chạy được** và đã chạy thật ít nhất 1 lần, có log.
3. Dữ liệu đã nằm ở `data/bronze/` (thô, có metadata nguồn) và `data/silver/` (đã chuẩn hoá).
4. Có **quality check** pass (schema, null, freshness, range).
5. Có **tài liệu** mô tả nguồn + cách dùng, đã build vào `context/`.
6. Có **ADR** nếu là quyết định kiến trúc hoặc thêm nguồn mới.

## 5. Định nghĩa Sẵn sàng (Definition of Ready) — cho 1 ticket

- Nêu rõ **câu hỏi đầu tư** phía sau yêu cầu (vì sao cần dữ liệu này?).
- Nêu **chỉ tiêu/trường dữ liệu** cụ thể, không nói chung chung.
- Có **nguồn ứng viên** hoặc yêu cầu rõ ràng là "cần đi tìm nguồn".
- Có **tần suất cập nhật** mong muốn và **độ trễ chấp nhận được**.
- Có **tiêu chí nghiệm thu** (dùng để làm gì, ra hình dạng gì).

## 6. Nhịp làm việc

| Nhịp | Khi nào | Ai chủ trì | Đầu ra |
|------|---------|-----------|--------|
| Daily Data Run | 06:30 hằng ngày (tự động) | Runner (máy) | Log + cảnh báo nguồn lỗi |
| Intake Triage | Khi có file mới trong `intake/inbox/` | Product Owner (AI) | Ticket YAML + ưu tiên |
| Weekly Review | Thứ 2 hằng tuần | Squad Lead | Cập nhật `05-backlog/BACKLOG.md`, ghi note |
| Monthly Architecture | Đầu tháng | Data Architect | ADR mới / rà nợ kỹ thuật |
| Quarterly Research | Đầu quý | Research Analyst | Rà kịch bản, cập nhật `kinh-te-vn-2036/` |

## 7. Ngưỡng leo thang (Escalation)

- Nguồn dữ liệu chết > 3 ngày ⇒ ticket P1, tìm nguồn thay thế.
- Chênh lệch số liệu giữa 2 nguồn > 5% ⇒ dừng dùng, mở ADR để chọn nguồn chuẩn (golden source).
- Bất kỳ nghi ngờ pháp lý nào về nguồn ⇒ dừng thu thập ngay, hỏi người dùng.

## 8. Chủ sở hữu

- **Product Owner cuối cùng: người dùng (nhà đầu tư).** AI squad thực thi, con người quyết.
- Không quyết định đầu tư nào được coi là "của squad" — squad chỉ cung cấp bằng chứng.

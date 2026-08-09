# ADR-0001 — Xử lý tài sản nghiên cứu cũ khi chuyển sang nền tảng mới

- **Trạng thái:** đã chấp thuận
- **Ngày:** 2026-08-09
- **Vai trò đề xuất:** ARCH + QA
- **Liên quan:** REQ-0005, REQ-0006, `squad/03-decisions/KIEM-KE-TAI-SAN-CU.md`

## Bối cảnh

Trước khi có nền tảng `vnir/`, thư mục chứa nghiên cứu thủ công tích luỹ từ trước:

- `kinh-te-vn-2036/` — khung 10 nhánh nghiên cứu + 41 chỉ số + 4 báo cáo HTML
- `vingroup/`, `sungroup/`, `tong-hop/` — nghiên cứu chuỗi cung ứng
- `IDEA.md` — ý tưởng dashboard sentiment chưa triển khai

Kiểm kê thực tế phát hiện ba vấn đề:

1. **Số liệu không truy vết được.** Nguồn ghi là `VietnamNet`, `Statista`, `VnExpress`, `VIR` —
   không URL, không ngày truy cập. Vi phạm nguyên tắc P1 của CHARTER.
2. **Ước tính trộn lẫn số liệu công bố.** File JSON đánh dấu `*` cho ước tính nhưng dashboard
   HTML hiển thị ngang hàng với số chính thức.
3. **Hai nguồn sự thật.** `master-data.json` và `chi-so-2024-2025.json` mô tả cùng 10 nhánh,
   khác nhau ở 9/10 nhánh — chắc chắn lệch nhau khi cập nhật.

## Các phương án đã cân nhắc

| Phương án | Ưu | Nhược | Kết luận |
|---|---|---|---|
| A. Xoá sạch, làm lại từ đầu | Sạch, không nợ | Mất khung nghiên cứu 10 nhánh — tài sản trí tuệ thật | ❌ Từ chối |
| B. Giữ nguyên, chạy song song | Không mất gì | Hai nguồn sự thật, người đọc nhầm số cũ là số chính thức | ❌ Từ chối |
| C. **Hạ cấp có kiểm soát** | Giữ giá trị, chặn rủi ro dùng nhầm | Tốn công phân loại | ✅ **Chọn** |

## Quyết định

Áp dụng phương án C — **phân biệt tài sản trí tuệ với dữ liệu chưa kiểm chứng**:

### Giữ nguyên (tài sản trí tuệ, nền mới chưa thay thế được)
- `kinh-te-vn-2036/KHUNG-NGHIEN-CUU.md` và 10 README nhánh — khung tư duy nghiên cứu
- `00-tong-quan-va-phuong-phap/PHUONG-PHAP.md` — 3 kịch bản Baseline/Upside/Downside
- `vingroup/`, `sungroup/`, `tong-hop/` — phân tích định tính, đã tự ghi rõ "cần xác minh"

### Hạ cấp (dữ liệu chưa kiểm chứng)
- 41 chỉ số từ 2 file JSON → hợp nhất vào `context/facts/legacy-2024-2025.md`
- Mỗi chỉ số gắn `do_tin_cay`: **trung bình** (nguồn sơ cấp thiếu URL) hoặc **thấp**
  (báo chí thứ cấp / tự đánh dấu ước tính)
- Mỗi chỉ số ghi rõ **connector nào sẽ thay thế nó**
- Front-matter có `can_kiem_chung_lai: true` để LLM biết không được trích dẫn như sự thật

### Đóng băng
- 4 file HTML nhận banner đỏ "ẢNH CHỤP LỊCH SỬ — KHÔNG CÒN CẬP NHẬT"
- Banner được nhúng vào **script sinh HTML**, không chỉ vào file output — nên chạy lại
  `build_dashboard.py` vẫn giữ banner (đã kiểm chứng thực tế)

### Xoá (tái tạo được, không mất mát)
- `kinh-te-vn-2036/.venv/` — 2,9 MB, không được git track, nền mới dùng Docker
- `kinh-te-vn-2036/docs/` — thư mục rỗng
- 7 file `verify*.sh` do subagent để lại ở thư mục cha

### Di chuyển
- `vn_macro_data_catalog.md` → `vnir/registry/nguon-vi-mo.md` (15 nguồn vĩ mô, curl-verified)
- `catalog_nguon_du_lieu_VN.md` → `vnir/registry/nguon-ck-bds.md` (nguồn CK/BĐS, curl-verified)
- `IDEA.md` → `archive/IDEA-sentiment-dashboard.md`
- `chi-so-2024-2025.json` → `archive/legacy-data/` (sau khi hợp nhất)

## Hệ quả

**Tích cực**
- Không con số chưa kiểm chứng nào có thể lọt vào báo cáo mà không có cảnh báo.
- LLM đọc `context/facts/` sẽ thấy nhãn độ tin cậy và biết phải thận trọng.
- Khung nghiên cứu 10 nhánh vẫn dùng được để định hướng connector nào cần xây trước.
- Giảm 2,9 MB rác, còn 30 KB catalog nguồn đã kiểm chứng thay thế.

**Tiêu cực / nợ phải trả**
- 41 chỉ số kế thừa vẫn nằm đó chờ được thay thế bằng dữ liệu thật. Đây là **nợ dữ liệu**,
  cần theo dõi qua task.
- Báo cáo HTML cũ vẫn hiển thị số cũ (đã có banner, nhưng người đọc vội có thể bỏ qua).

**Bằng chứng thực tế sau khi áp dụng**
- Connector World Bank đã chạy thật: **325 quan sát**, 7/14 chỉ số (7 chỉ số còn lại bị
  World Bank trả HTTP 502 chập chờn — đã xử lý bằng cơ chế chịu lỗi từng phần).
- Đối chiếu ngay được: GDP/người 2025 cũ ghi 5.066 USD ↔ World Bank thật 5.065,99 USD (khớp);
  GDP 2024 cũ ghi ~470 tỷ USD ↔ thật 476,3 tỷ USD (lệch +1,3%).

## Cách đảo ngược

Toàn bộ trạng thái trước khi dọn được gắn tag git:

```bash
git checkout truoc-don-dep        # xem lại toàn bộ trạng thái cũ
git checkout truoc-don-dep -- kinh-te-vn-2036/   # khôi phục riêng thư mục
```

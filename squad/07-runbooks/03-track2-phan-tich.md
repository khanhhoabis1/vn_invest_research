# Runbook 03 — TRACK 2: Thu thập & Phân tích đầu tư

**Dành cho:** Bạn và đội phân tích đầu tư.
**Mục tiêu:** Giao đề bài phân tích (cổ phiếu/ngành/vĩ mô) → kiểm kê dữ liệu →
thu thập/cập nhật → báo cáo có trích dẫn nguồn.

---

## Nguyên lý cốt lõi

> **Thiếu dữ liệu thì nói "chưa có", không tự bịa.** Nếu chưa có luồng lấy dữ liệu,
> hệ thống tự động đẩy sang Track 1 (chứ không chế biến số bừa).

Luồng:
```
Đề bài ──▶ BRIEF ──▶ kiểm kê dữ liệu
                    ├── đủ         → phân tích → báo cáo
                    ├── cũ         → chạy cập nhật → phân tích
                    └── thiếu luồng → ⚠ đẩy sang Track 1 (ASSESS)
```

---

## Kịch bản A — Qua giao diện (khuyên dùng)

1. Mở **http://localhost:8602**
2. Tab **🎯 Đề bài phân tích**:
   - Chọn **Loại phân tích** (cổ phiếu / ngành / vĩ mô / BĐS...)
   - Gõ **Đề bài** và **Câu hỏi đầu tư chính**
   - Nhấn **Giao đề bài** → tạo BRIEF
3. Tab **📋 Danh sách (BRIEF)**:
   - Theo dõi cột **Trạng thái**:
     - ⚪ Mới → 🔍 Đang kiểm kê → ⬇️ Đang thu thập → 🧮 Đang phân tích → ✅ Xong
     - ⚠️ **Đang chờ Track 1** = thiếu luồng lấy dữ liệu, đã đẩy sang Track 1
   - Mở rộng để xem: đề bài gốc, câu hỏi, kiểm kê dữ liệu, báo cáo
4. Tab **🔌 Nguồn dữ liệu** → xem connector có sẵn
5. Tab **▶️ Chạy & lịch sử** → chạy thu thập thủ công (nếu cần cập nhật)
6. Tab **🔎 Truy vấn SQL** → hỏi dữ liệu trực tiếp bằng DuckDB

---

## Kịch bản B — Qua dòng lệnh

### B1. Giao đề bài
```bash
.venv/bin/python tools/track.py de-bai "Phân tích cổ phiếu VNM, có nên mua không" \
    --loai co_phieu --doi-tuong VNM \
    --cau-hoi "Định giá hiện tại đắt hay rẻ?" "Biên lợi nhuận có cải thiện không?"
# → BRIEF-xxxx
```

### B2. Kiểm kê dữ liệu (cần gì / có gì)
```bash
.venv/bin/python tools/track.py kiem-ke BRIEF-0001 \
    --can "GDP và lạm phát vĩ mô" --trang-thai co_du --hanh-dong "dùng luôn"

.venv/bin/python tools/track.py kiem-ke BRIEF-0001 \
    --can "Giá cổ phiếu VNM theo ngày" --trang-thai chua_co_luong
```
Kết quả hiển thị bảng:
- ✅ `co_du` — có sẵn, dùng luôn
- ⚠️ `co_nhung_cu` — có nhưng cũ, nên chạy cập nhật
- ❌ `chua_co_luong` — chưa có luồng lấy → phải đẩy Track 1

### B3. Nếu thiếu luồng → đẩy sang Track 1
```bash
.venv/bin/python tools/track.py day-track-1 BRIEF-0001 \
    --du-lieu "Giá cổ phiếu VNM theo ngày"
# → ASSESS-xxxx, BRIEF chuyển trạng thái "cho_track_1"
```
Sau đó sang Runbook 02 (Track 1) để xử lý ASSESS đó.

### B4. Chạy thu thập / cập nhật (nếu có luồng)
```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"key":"worldbank.vn_macro_indicators","dry_run":false}'
```
Hoặc qua UI Ops tab ▶️ chọn nguồn → **Chạy ngay**.

### B5. Ghi nhận báo cáo (bắt buộc 4 phần)
```bash
.venv/bin/python tools/track.py bao-cao BRIEF-0001 \
    --luan-diem "VNM định giá đang rẻ so với trung bình 5 năm" \
    --so-nguon 5 \
    --rui-ro "Biên lợi nhuận suy giảm nếu chi phí đầu vào tăng" \
    --chua-biet "Chưa có dữ liệu BCTC quý gần nhất"
```
> Thiếu 1 trong 4 phần (luận điểm / nguồn / rủi ro / chưa biết) → báo cáo chưa đạt.

---

## Chạy thu thập định kỳ

Worker tự động chạy theo lịch (`schedule` của mỗi connector). Xem lịch sử:
- UI Ops tab **▶️ Chạy & lịch sử**
- API: `curl http://localhost:8000/runs`

---

## Dấu hiệu thành công

- [ ] BRIEF được tạo với loại & câu hỏi rõ ràng
- [ ] Có bảng kiểm kê dữ liệu (cần vs có)
- [ ] Nếu thiếu luồng → đã đẩy Track 1 (trạng thái `cho_track_1`)
- [ ] Báo cáo có đủ 4 phần, mỗi số liệu trace được về nguồn

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Xử lý |
|---|---|---|
| BRIEF tạo nhưng không hiện trên UI | UI chưa reload | `docker compose restart ui-ops` |
| Thu thập báo 502 | Nguồn chập chờn (ví dụ World Bank) | Chạy lại; connector đã chịu lỗi từng phần |
| Báo cáo không lưu | Thiếu 1 trong 4 phần | Bổ sung `--luan-diem`/`--so-nguon`/`--rui-ro`/`--chua-biet` |
| Dữ liệu cũ | Chưa chạy cập nhật | Tab ▶️ Chạy & lịch sử → Chạy ngay |

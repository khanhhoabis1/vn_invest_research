# Runbook 02 — TRACK 1: Phát triển nền tảng

**Dành cho:** Bạn (người đề xuất) và đội phân tích/phát triển.
**Mục tiêu:** Tiếp nhận yêu cầu cải tiến → thẩm định xem đã làm được chưa → phát triển nếu thiếu.

---

## Nguyên lý cốt lõi

> Bạn **không cần biết** nền tảng hiện tại làm được gì. Cứ nêu yêu cầu, đội phân tích
> (BA) sẽ **thẩm định** và trả lời. Chỉ khi chưa đáp ứng, đội phát triển mới vào cuộc.

Luồng:
```
Yêu cầu ──▶ ASSESS (thẩm định) ──đã đáp ứng?──▶ trả lời bạn
                            └──chưa?──▶ REQ ──COMP──TASK──▶ release
```

---

## Kịch bản A — Qua giao diện (khuyên dùng)

1. Mở **http://localhost:8601**
2. Tab **📥 Yêu cầu của bạn**:
   - Gõ yêu cầu tiếng Việt tự nhiên (ví dụ: "Tôi muốn theo dõi lãi suất liên ngân hàng qua đêm")
   - Nhấn **Gửi yêu cầu**
3. Tab **🔎 Thẩm định (ASSESS)**:
   - Xem cột **Kết luận**:
     - 🟢 `da_dap_ung` → đã có, hướng dẫn dùng hiện ngay
     - 🟡 `dap_ung_mot_phan` → thiếu một phần, xem "Phần còn thiếu"
     - 🔴 `chua_dap_ung` → chưa có, đã sinh REQ
     - ⛔ `khong_kha_thi` → nguồn không tồn tại/bị chặn, có phương án thay thế
   - Mở rộng một ASSESS để xem **Nguyên văn yêu cầu gốc** (không bao giờ bị sửa)
     và **Bằng chứng đã chạy**
4. Tab **📋 Yêu cầu (REQ)** → xem REQ được sinh ra từ thẩm định

---

## Kịch bản B — Qua dòng lệnh

### B1. Gửi yêu cầu
```bash
.venv/bin/python tools/track.py yeu-cau "Tôi muốn xem lãi suất liên ngân hàng qua đêm" \
    --giao-cho BA
# → ASSESS-xxxx được tạo
```

### B2. Đội phân tích thẩm định (BẮT BUỘC có bằng chứng)
```bash
.venv/bin/python tools/track.py tham-dinh ASSESS-0001 \
    --ket-luan chua_dap_ung \
    --bang-chung "GET http://localhost:8000/sources" "chỉ trả về worldbank" \
    --thieu "connector lãi suất (SBV hoặc Vietcap)" \
    --uu-tien 5 4 3
```
> **Sẽ bị chặn** nếu kết luận `chua_dap_ung`/`dap_ung_mot_phan` mà **không có `--bang-chung`**.
> Đây là cơ chế chống bịa số — không được phán đoán.

### B3. Chuyển cho đội phát triển (tự sinh REQ)
```bash
.venv/bin/python tools/track.py chuyen-phat-trien ASSESS-0001 \
    --ket-qua "Người dùng xem được lãi suất qua đêm trên Ops plane" \
    --plane ops
# → REQ-xxxx, giữ nguyên văn yêu cầu gốc
```

### B4. Đội phát triển tách thành phần & công việc
```bash
.venv/bin/python tools/specctl.py show REQ-xxxx    # xem gói thực thi
.venv/bin/python tools/specctl.py new comp ...     # tạo COMP
.venv/bin/python tools/specctl.py new task ...      # tạo TASK
```

---

## Theo dõi hàng đợi Track 1

```bash
.venv/bin/python tools/track.py hang-doi --track 1
.venv/bin/python tools/track.py lien-ket           # sơ đồ ASSESS → REQ ↔ BRIEF
```

---

## Dấu hiệu thành công

- [ ] Yêu cầu của bạn đã thành ASSESS (có ID)
- [ ] ASSESS có kết luận + ít nhất 1 bằng chứng thật
- [ ] Nếu chưa đáp ứng → có REQ tương ứng, nối với ASSESS qua `tu_assess`
- [ ] REQ có `priority.score` để xếp hàng

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Xử lý |
|---|---|---|
| `tham-dinh` báo "thiếu bằng chứng" | Kết luận chưa đáp ứng mà không có `--bang-chung` | Chạy lệnh thật, dán output vào `--bang-chung` |
| Tạo ASSESS nhưng không thấy trên UI | UI chưa reload / container cũ | `docker compose restart ui-build` |
| REQ sinh ra không có nội dung | Quên `chuyen-phat-trien` | Chạy B3 |

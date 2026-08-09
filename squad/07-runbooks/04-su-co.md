# Runbook 04 — Xử lý sự cố

Bảng tra cứu nhanh. Mỗi mục: triệu chứng → nguyên nhân → xử lý.

---

## Bảng sự cố

| # | Triệu chứng | Nguyên nhân có thể | Xử lý |
|---|---|---|---|
| S1 | Mở :8601 / :8602 không được (timeout) | Stack chưa chạy | `make up`, chờ ~40s, rồi `curl /health` |
| S2 | `curl /health` báo connection refused | `api` chết hoặc chưa lên | `docker compose ps` → nếu api Exit → `docker compose restart api` |
| S3 | UI báo "MAT KET NOI" / API | biến `VNIR_API` sai trong container | Mặc định `http://api:8000` (nội bộ Docker). Chỉ sửa nếu chạy UI ngoài container |
| S4 | Tab Nguồn dữ liệu **rỗng** | API không nạp được connector | Xem S5 |
| S5 | API log: `Khong nap duoc connector` | import lỗi / sai package | `docker compose logs api` xem chi tiết; chạy `make verify` (có test bắt lỗi này) |
| S6 | Thu thập báo `HTTP 502` từ nguồn | Nguồn chập chờn (World Bank hay gặp) | Chạy lại; connector đã chịu lỗi từng phần (bỏ qua chỉ số hỏng) |
| S7 | `track.py tham-dinh` báo "thiếu bằng chứng" | Kết luận chưa đáp ứng không có `--bang-chung` | Chạy lệnh thật, dán output vào `--bang-chung` |
| S8 | Dữ liệu hiển thị **cũ** | Chưa chạy thu thập lại | UI Ops tab ▶️ → Chạy ngay cho nguồn đó |
| S9 | `make bootstrap` lỗi `pip: command not found` | Máy có PEP 668 | Makefile đã dùng `uv pip`. Không dùng `pip` toàn cục |
| S10 | `make verify` báo fail ở bước Docker | Container cũ / image chưa build | `docker compose build` rồi `make up` |
| S11 | BRIEF/ASSESS tạo nhưng không hiện trên UI | UI container chưa reload code mới | `docker compose restart ui-build ui-ops` |
| S12 | `docker compose up` báo port đã dùng | Port 8000/8601/8602/5433 bị chiếm | Đổi port trong `.env` (`API_PORT`, `UI_BUILD_PORT`...) hoặc tắt app chiếm port |

---

## Các lệnh chẩn đoán

```bash
# Trạng thái container
docker compose ps

# Log từng service
docker compose logs api           # log API
docker compose logs ui-ops        # log UI Track 2
docker compose logs worker        # log thu thập

# Sức khỏe API
curl -s --max-time 8 http://localhost:8000/health

# Nguồn đã nạp được
curl -s --max-time 8 http://localhost:8000/sources | python3 -m json.tool

# Kiểm chứng toàn diện trước khi báo lỗi
make verify
```

---

## Quy tắc báo lỗi (P8: thất bại phải ồn ào)

- Không sửa số liệu thô (`data/bronze/`) để "cho đẹp".
- Nếu nguồn chết > 3 ngày → đánh dấu rủi ro, tìm nguồn thay (theo Charter mục 7).
- Nếu chênh lệch số liệu 2 nguồn > 5% → dừng, mở ADR chọn nguồn chuẩn.
- Mọi sửa kiến trúc → 1 ADR trong `squad/03-decisions/`.

---

## Khi nào cần hỏi người dùng

- Nghi ngờ vi phạm pháp lý nguồn (robots.txt / ToS / bản quyền).
- Yêu cầu dữ liệu cá nhân hoặc có bản quyền chưa cấp phép.
- Quyết định đầu tư (squad chỉ cung cấp bằng chứng, không quyết thay).

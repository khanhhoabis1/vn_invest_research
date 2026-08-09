# Runbook 01 — Khởi động & tắt nền tảng

**Mục tiêu:** Đưa toàn bộ stack (DB, API, worker, 2 UI) từ trạng thái tắt sang sẵn sàng phục vụ.

---

## Yêu cầu trước

- Docker Desktop đang chạy (menu bar có biểu tượng Docker xanh)
- Đã cài `uv`: `brew install uv` (hoặc xem https://docs.astral.sh/uv/)
- Đã clone repo và đứng trong thư mục repo

```bash
cd /Users/hoanhk5/Documents/HERMES/dau-tu
```

---

## Bước 1 — Tạo môi trường (chỉ lần đầu, hoặc sau khi pull code mới)

```bash
make bootstrap
```
Lệnh này:
- Tạo `.venv/` (Python 3.11)
- Cài thư viện từ `requirements.txt` + `pytest` + `ruff`

> Nếu gặp lỗi `pip: command not found` → bình thường, Makefile đã dùng `uv pip`.
> Tuyệt đối **không** chạy `pip install` toàn cục (máy có PEP 668).

---

## Bước 2 — Khởi chạy stack

```bash
make up
```

Tương đương `docker compose up -d`. Khởi tạo:
- `db` (PostgreSQL) — cần ~20s để healthy
- `api` (FastAPI :8000) — phụ thuộc db healthy
- `worker` — chạy scheduler thu thập
- `ui-build` (Track 1 :8601)
- `ui-ops` (Track 2 :8602)

---

## Bước 3 — Chờ sẵn sàng

Stack mất **khoảng 40 giây** lần đầu (build image + khởi DB). Kiểm tra:

```bash
make verify
```

Hoặc kiểm tra nhanh:
```bash
curl -s --max-time 8 http://localhost:8000/health
# kỳ vọng: {"status":"ok",...}
```

Mở trình duyệt:
- Track 1: http://localhost:8601
- Track 2: http://localhost:8602

---

## Bước 4 — Xác nhận 2 UI & nguồn

Trên Track 2 (http://localhost:8602):
- Tab **🔌 Nguồn dữ liệu** → phải thấy ít nhất 1 connector (ví dụ `worldbank.vn_macro_indicators`)

Nếu rỗng → xem `squad/07-runbooks/04-su-co.md` mục "API không nạp được connector".

---

## Tắt & bật lại

```bash
make down     # tắt hết các container (dữ liệu vẫn còn trên ổ đĩa)
make up       # bật lại
```

> Dữ liệu `data/bronze/`, `data/silver/`, `specs/` đều nằm ngoài container (mount volume),
> nên tắt/bật không làm mất dữ liệu đã thu thập.

---

## Chế độ AI local (tùy chọn, tốn RAM)

```bash
docker compose --profile ai up -d
```
Thêm `qdrant` (:6333) và `ollama` (:11434). Tốn thêm ~4.8GB RAM. Chỉ bật khi cần
embedding/LLM local. Xem `.env.example` để cấu hình model.

---

## Dọn log / file tạm

```bash
make clean    # xóa __pycache__, .pytest_cache, .ruff_cache
```

---

## Dấu hiệu thành công

- [ ] `curl /health` trả `{"status":"ok"}`
- [ ] Mở :8601 thấy tiêu đề "🛠 TRACK 1 — Phát triển nền tảng"
- [ ] Mở :8602 thấy tiêu đề "📊 TRACK 2 — Thu thập & Phân tích đầu tư"
- [ ] Tab Nguồn dữ liệu có ≥1 connector
- [ ] `make verify` báo "TẤT CẢ ĐẠT"

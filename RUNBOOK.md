# RUNBOOK — Hướng dẫn vận hành VN Invest Research Platform

> Tài liệu này dành cho **người dùng cuối** (bạn, PO, đội phân tích). Đọc hết 5 phút là
> biết cách chạy nền tảng và thao tác 2 track. AI agent đọc `AGENTS.md`, người đọc file này.

---

## 0. Sơ đồ nhanh

```
Bạn ──yêu cầu──▶ TRACK 1 (Build :8601) ──ASSESS──▶ REQ ──COMP──▶ TASK ──release
  │
  └─đề bài────▶ TRACK 2 (Ops :8602) ──BRIEF──▶ kiểm kê ──▶ thiếu luồng? ──▶ đẩy ngược T1
```

| Giao diện | Port | Dành cho |
|---|---|---|
| **Track 1 — Phát triển nền tảng** | http://localhost:8601 | Gửi yêu cầu cải tiến, xem thẩm định |
| **Track 2 — Thu thập & Phân tích** | http://localhost:8602 | Giao đề bài phân tích, chạy thu thập |
| API (nội bộ / gọi lệnh) | http://localhost:8000 | Kết nối 2 UI với dữ liệu |
| PostgreSQL (chỉ nội bộ) | localhost:5433 | Lưu trữ, không cần mở trực tiếp |

---

## 1. Khởi động lần đầu

Yêu cầu: Docker Desktop đang chạy, đã cài `uv` (`brew install uv`).

```bash
cd /Users/hoanhk5/Documents/HERMES/dau-tu

# 1. Tạo môi trường ảo + cài thư viện
make bootstrap

# 2. Khởi chạy toàn bộ stack (DB, API, worker, 2 UI)
make up

# 3. Chờ ~40s rồi kiểm tra
make verify          # hoặc mở http://localhost:8601
```

Mở trình duyệt:
- **Track 1:** http://localhost:8601
- **Track 2:** http://localhost:8602

> Cấu hình nâng cao (thêm Qdrant + Ollama cho AI local): `docker compose --profile ai up -d`
> (tốn thêm ~4.8GB RAM). Xem `docker-compose.yml` và `.env.example`.

---

## 2. Tắt / bật lại

```bash
make down     # tắt hết
make up       # bật lại (dữ liệu bronze/silver nằm trên ổ đĩa, không mất)
make logs     # xem log worker (thu thập dữ liệu)
```

---

## 3. TRACK 1 — Bạn có ý tưởng cải thiện nền tảng

**Quy tắc vàng:** Bạn **không cần biết** nền tảng đã làm được gì. Cứ nêu yêu cầu,
đội phân tích sẽ thẩm định hộ.

### Cách A — Qua giao diện (khuyên dùng)
1. Mở http://localhost:8601
2. Tab **📥 Yêu cầu của bạn** → gõ yêu cầu tiếng Việt → **Gửi yêu cầu**
3. Tab **🔎 Thẩm định (ASSESS)** → xem đội phân tích đã kết luận chưa:
   - 🟢 Đã đáp ứng → hướng dẫn dùng hiện ra
   - 🔴 Chưa đáp ứng → sinh REQ, đội phát triển lên kế hoạch

### Cách B — Qua dòng lệnh
```bash
# 1. Bạn gửi yêu cầu
.venv/bin/python tools/track.py yeu-cau "Tôi muốn xem lãi suất liên ngân hàng qua đêm"

# 2. Đội phân tích thẩm định (cần bằng chứng thật, không được đoán)
.venv/bin/python tools/track.py tham-dinh ASSESS-0001 \
    --ket-luan chua_dap_ung \
    --bang-chung "GET http://localhost:8000/sources" "chỉ có worldbank"

# 3. Chuyển cho đội phát triển (tự sinh REQ giữ nguyên văn yêu cầu)
.venv/bin/python tools/track.py chuyen-phat-trien ASSESS-0001
```

---

## 4. TRACK 2 — Bạn muốn phân tích một cổ phiếu / ngành

**Quy tắc vàng:** Thiếu dữ liệu thì báo **"chưa có"**, tuyệt đối không bịa số.
Nền tảng sẽ tự đẩy thiếu sót sang Track 1.

### Cách A — Qua giao diện (khuyên dùng)
1. Mở http://localhost:8602
2. Tab **🎯 Đề bài phân tích** → chọn loại, gõ đề bài, câu hỏi đầu tư → **Giao đề bài**
3. Tab **📋 Danh sách (BRIEF)** → theo dõi trạng thái:
   - ⚪ Mới → 🔍 Đang kiểm kê → ⬇️ Đang thu thập → 🧮 Đang phân tích → ✅ Xong
   - ⚠️ **Đang chờ Track 1** = thiếu luồng lấy dữ liệu, đã đẩy sang Track 1 xử lý
4. Tab **🔌 Nguồn dữ liệu** / **▶️ Chạy & lịch sử** → chạy thu thập thủ công
5. Tab **🔎 Truy vấn SQL** → hỏi dữ liệu trực tiếp

### Cách B — Qua dòng lệnh
```bash
# 1. Giao đề bài
.venv/bin/python tools/track.py de-bai "Phân tích cổ phiếu VNM" \
    --loai co_phieu --doi-tuong VNM --cau-hoi "Định giá hiện tại đắt hay rẻ?"

# 2. Kiểm kê dữ liệu (cần gì / có gì)
.venv/bin/python tools/track.py kiem-ke BRIEF-0001 \
    --can "Giá cổ phiếu VNM theo ngày" --trang-thai chua_co_luong

# 3. Nếu thiếu luồng → đẩy sang Track 1 (tự sinh ASSESS)
.venv/bin/python tools/track.py day-track-1 BRIEF-0001 --du-lieu "Giá cổ phiếu VNM"

# 4. Ghi nhận báo cáo (bắt buộc 4 phần)
.venv/bin/python tools/track.py bao-cao BRIEF-0001 \
    --luan-diem "..." --so-nguon 5 --rui-ro "..." --chua-biet "..."
```

---

## 5. Chạy thu thập dữ liệu thủ công

Qua UI Ops (tab 🔌 / ▶️) hoặc API:
```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"key":"worldbank.vn_macro_indicators","dry_run":false}'
```
Xem lịch sử: tab **▶️ Chạy & lịch sử** trên Ops plane, hoặc `curl http://localhost:8000/runs`.

> Dữ liệu thô lưu tại `data/bronze/<nguồn>/dt=<ngày>/` kèm `_manifest.json`
> (URL gốc + sha256 + HTTP status) — là bằng chứng truy vết.

---

## 6. Theo dõi trạng thái mọi việc

```bash
.venv/bin/python tools/track.py hang-doi          # cả 2 track
.venv/bin/python tools/track.py hang-doi --track 1 # chỉ Track 1
.venv/bin/python tools/track.py hang-doi --track 2 # chỉ Track 2
.venv/bin/python tools/track.py lien-ket          # sơ đồ ASSESS→REQ↔BRIEF
```

---

## 7. Xác minh trước khi commit (dành cho người sửa code)

```bash
make verify     # 6 bước: biên dịch, lint, spec, test, tên module, Docker sống
```

---

## 8. Sự cố thường gặp

| Triệu chứng | Nguyên nhân có thể | Xử lý |
|---|---|---|
| Mở :8601/:8602 không được | Stack chưa chạy | `make up`, chờ 40s |
| API báo lỗi kết nối | `api` chết | `docker compose restart api` |
| Thu thập báo 502 từ nguồn | Nguồn chập chờn (ví dụ World Bank) | Chạy lại; connector đã chịu lỗi từng phần |
| `track.py` báo thiếu bằng chứng | Bạn kết luận mà chưa chạy lệnh kiểm chứng | Chạy lệnh thật, thêm `--bang-chung` |
| Dữ liệu cũ | Chưa chạy thu thập lại | Tab ▶️ Chạy & lịch sử → Chạy ngay |
| `make bootstrap` lỗi pip | Máy có PEP 668 | Dùng `uv` (Makefile đã làm sẵn), không dùng `pip` toàn cục |

---

## 9. Cấu trúc thư mục quan trọng

```
dau-tu/
├── docker-compose.yml      # định nghĩa stack
├── Makefile                # lệnh chuẩn (make up / verify / test)
├── tools/
│   ├── track.py            # điều phối 2 track (Track 1 & 2)
│   ├── specctl.py          # quản lý spec REQ/COMP/TASK/ASSESS/BRIEF
│   ├── ghsync.py           # đồng bộ spec ↔ GitHub Issue
│   └── verify.sh           # kiểm chứng trước commit
├── vnir/
│   ├── api/main.py         # API (endpoints /specs, /runs, /intake...)
│   ├── connectors/         # framework thu thập (thêm connector tại đây)
│   ├── ui_build/app.py     # Track 1 UI (:8601)
│   └── ui_ops/app.py       # Track 2 UI (:8602)
├── specs/                  # REQ/COMP/TASK/ASSESS/BRIEF (machine-readable)
├── data/bronze|silver|gold # dữ liệu theo lớp
└── squad/                  # charter, roles, runbooks, quyết định (ADR)
```

---

## 10. Tài liệu liên quan

- `README.md` — tổng quan kho
- `AGENTS.md` — hợp đồng cho AI agent làm việc trên repo
- `squad/00-charter/HAI-TRACK.md` — thiết kế chi tiết 2 track
- `squad/07-runbooks/` — runbook chuyên biệt (khởi động, Track 1, Track 2, sự cố)
- `GIT_WORKFLOW.md` — quy trình commit / PR / GitHub

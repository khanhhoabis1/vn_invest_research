# KIẾN TRÚC NỀN TẢNG — VN Invest Research Platform

> Chạy 100% cục bộ bằng **Docker Desktop**, toàn bộ thành phần là **open source**.
> Máy đích: macOS arm64, Docker được cấp ~8GB RAM ⇒ thiết kế phải **gọn**, không JVM nặng, không cluster.

---

## 1. Hai mặt phẳng (Two Planes) — đúng theo yêu cầu tách giao diện

Nền tảng được chia làm **2 mặt phẳng độc lập**, mỗi mặt phẳng có UI riêng, cổng riêng, người dùng riêng:

```
┌──────────────────────────────── BUILD PLANE (Nhóm A) ────────────────────────────────┐
│  "Xưởng nâng cấp nền tảng"            UI: http://localhost:8601                       │
│                                                                                       │
│  Ai dùng: người đưa yêu cầu cải tiến, PO, kiến trúc sư, AI coding agent               │
│  Làm gì:  gửi yêu cầu bằng tiếng Việt → AI phân rã → REQ/COMP/TASK → GitHub Issue/PR  │
│                                                                                       │
│   [Gửi yêu cầu] → [Phân rã bằng AI] → [Duyệt spec] → [Đồng bộ GitHub] → [Theo dõi PR] │
└───────────────────────────────────────┬───────────────────────────────────────────────┘
                                        │  spec đã duyệt = hợp đồng thay đổi
                                        ▼
┌──────────────────────────────── OPS PLANE (Nhóm B) ──────────────────────────────────┐
│  "Trung tâm vận hành dữ liệu"          UI: http://localhost:8602                      │
│                                                                                       │
│  Ai dùng: người phân tích, nhà đầu tư                                                 │
│  Làm gì:  bật/tắt nguồn, chạy thu thập, xem lịch, xem chất lượng, tra cứu & vẽ biểu đồ│
│                                                                                       │
│   [Nguồn dữ liệu] [Lịch & lần chạy] [Chất lượng] [Khám phá dữ liệu] [Bảng theo dõi]   │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**Vì sao tách:** hai nhóm này có nhịp làm việc, rủi ro và người dùng hoàn toàn khác nhau.
Sửa nền tảng là việc **có thể gây hỏng**; vận hành thu thập là việc **phải luôn chạy**.
Tách UI để người vận hành không vô tình đổi kiến trúc, và người phát triển không phải lội qua biểu đồ.

Điểm giao duy nhất: **spec đã duyệt**. Build plane sinh ra spec → Ops plane đọc registry/contract sinh từ spec.

---

## 2. Sơ đồ thành phần Docker

```
                              Docker Desktop (arm64)
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ui-build :8601 ──┐                              ┌── ui-ops :8602           │
│   (Streamlit)      │                              │   (Streamlit)            │
│                    ▼                              ▼                          │
│              ┌─────────────────────────────────────────┐                     │
│              │        api :8000  (FastAPI)             │                     │
│              │  /specs /intake /sources /runs /query   │                     │
│              └───────┬─────────────────────┬───────────┘                     │
│                      │                     │                                 │
│         ┌────────────▼──────┐   ┌──────────▼─────────┐                       │
│         │  db :5433         │   │  worker            │                       │
│         │  postgres:16-alp  │   │  APScheduler +     │                       │
│         │  metadata, tickets│   │  connector runner  │                       │
│         │  runs, audit      │   └──────────┬─────────┘                       │
│         └───────────────────┘              │                                 │
│                                            ▼                                 │
│   ┌──────────────────────── bind mount: /workspace ────────────────────────┐ │
│   │  specs/   data/bronze  data/silver  data/gold  context/  platform/     │ │
│   │  (DuckDB + Parquet + YAML + Markdown — không cần service riêng)        │ │
│   └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│   ── profile "ai" (bật khi cần, tốn RAM) ──────────────────────────────────  │
│   qdrant :6333 (vector, Apache-2.0)      ollama :11434 (LLM nhỏ cục bộ)      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Vì sao chọn từng thứ (tất cả open source, chạy cục bộ)

| Thành phần | Công nghệ | Giấy phép | Lý do chọn / vì sao không chọn cái khác |
|---|---|---|---|
| API | **FastAPI + Uvicorn** | MIT/BSD | Nhẹ, tự sinh OpenAPI → AI agent đọc được API mà không cần docs riêng |
| CSDL metadata | **PostgreSQL 16-alpine** | PostgreSQL License | ~200MB RAM. Cần giao dịch cho ticket/run. *Không dùng SQLite vì nhiều container ghi song song.* |
| Kho phân tích | **DuckDB + Parquet** (nhúng) | MIT | Truy vấn cột cực nhanh trên file, **không tốn container**. *Không dùng ClickHouse/Spark — thừa cho quy mô MB–GB.* |
| Lịch chạy | **APScheduler** trong worker | MIT | ~50MB. *Không dùng Airflow (JVM-free nhưng ~2GB + scheduler + webserver) hay Prefect server — quá nặng cho 8GB.* |
| UI | **Streamlit** ×2 | Apache-2.0 | Python thuần, dựng UI dữ liệu nhanh, 2 app tách rời. *Không dùng Metabase/Superset — JVM/nặng, và không làm được Build plane.* |
| Biểu đồ | **Plotly / Altair** | MIT/BSD | Tương tác, offline, không gọi CDN ngoài |
| Vector store | **Qdrant** (profile `ai`) | Apache-2.0 | Rust, nhẹ, arm64 native |
| LLM cục bộ | **Ollama** (profile `ai`) | MIT | Chạy model nhỏ (qwen2.5:3b, llama3.2:3b) để phân rã yêu cầu offline |
| Kiểm định spec | **jsonschema** | MIT | Spec sai schema là fail CI, không cho merge |
| CI | **GitHub Actions** | — | Đã có sẵn với repo |

**Nguyên tắc phụ thuộc:** mọi thứ phải chạy được **khi rút mạng**, trừ (a) thu thập dữ liệu từ nguồn ngoài và (b) đồng bộ GitHub. Không có SaaS bắt buộc, không cần API key thương mại để nền tảng khởi động.

---

## 3. Luồng dữ liệu — kiến trúc Medallion trên file

```
NGUỒN NGOÀI                BRONZE                SILVER               GOLD              CONTEXT
(GSO, SBV, WB,     →   thô, bất biến,    →   chuẩn hoá,      →   sẵn dùng,     →   cho LLM
 HOSE, vnstock…)       kèm manifest          1 schema/chủ đề     metric/báo cáo    chunk + fact
                       (json+raw)            (Parquet)           (Parquet/DuckDB)  (md + jsonl)
```

Quy ước đường dẫn (bất biến, connector không được tự chế):

```
data/bronze/<source_id>/<dataset>/dt=<YYYY-MM-DD>/data.<ext>
data/bronze/<source_id>/<dataset>/dt=<YYYY-MM-DD>/_manifest.json   ← url, http_status, sha256, fetched_at, rows
data/silver/<domain>/<dataset>.parquet
data/gold/<metric_group>.parquet
context/chunks/*.jsonl        context/facts/*.md        context/index/llms.txt
```

**P2 – Bronze bất biến:** không sửa, không ghi đè. Tải lại = thư mục `dt=` mới. Xoá sạch silver/gold rồi build lại từ bronze phải luôn thành công (`make rebuild`).

---

## 4. Chuỗi spec — để **model AI nhỏ** cũng hiểu và thực thi được

Đây là phần cốt lõi trả lời yêu cầu: *"đảm bảo các phiên bản điều chỉnh có thể được model AI đủ hiểu và thực thi thật; model nhỏ vẫn truy xuất được yêu cầu từ nền tảng cũ để phát triển tiếp."*

```
 Yêu cầu tiếng Việt        REQ-0007            COMP-0003             TASK-0042           GitHub
 (intake/inbox)      →   Requirement    →    Component        →    Task (nguyên tử)  →   Issue → PR
   văn xuôi              YAML có ID          YAML có ID             YAML có ID            tự động
                         "cần gì & vì sao"   "sửa ở đâu"            "làm chính xác gì"
```

### Vì sao model nhỏ vẫn làm được

1. **ID ổn định, không bao giờ tái sử dụng.** `REQ-0007` mãi mãi là yêu cầu đó. Model chỉ cần grep ID.
2. **Mỗi TASK là một "gói thực thi tự đủ"** (self-contained execution packet). Không cần đọc cả repo:
   - `files_to_touch`: danh sách file chính xác được phép sửa
   - `interfaces`: chữ ký hàm/endpoint phải tuân
   - `acceptance`: lệnh test cụ thể phải pass
   - `commands`: lệnh chạy để verify
   - `context_refs`: đường dẫn chunk tài liệu liên quan (đã trích sẵn)
   - `forbidden`: những gì tuyệt đối không được đụng
3. **Ngân sách ngữ cảnh khai báo sẵn** (`context_budget_tokens`). Task nào vượt ~6k token phải bị chẻ nhỏ tiếp — CI chặn.
4. **`specs/SPEC-INDEX.md` + `context/index/llms.txt`**: bản đồ 1 trang để model định vị mà không quét repo.
5. **Truy vết ngược đầy đủ:** mỗi commit/PR bắt buộc mang `TASK-xxxx`; mỗi TASK trỏ về COMP → REQ → yêu cầu gốc. Model tương lai hỏi *"vì sao có hàm này?"* → lần ngược 3 bước là ra bối cảnh gốc, kể cả sau nhiều năm.
6. **Spec là nguồn sự thật, code là dẫn xuất.** Đổi hành vi mà không đổi spec ⇒ CI fail (kiểm tra `drift`).

### Vòng đời trạng thái

```
draft → proposed → approved → in_progress → in_review → done
                        └→ rejected          └→ blocked
```
Chỉ spec `approved` mới được tạo Issue. Chỉ TASK `done` + PR merged mới đóng REQ.

---

## 5. Tự động hoá GitHub

| Việc | Cơ chế | Kích hoạt |
|---|---|---|
| Yêu cầu → spec | `tools/specctl.py decompose` (LLM: Ollama cục bộ hoặc Hermes) | Build plane UI / CLI |
| Kiểm tra spec hợp lệ | `specctl validate` (JSON Schema) | pre-commit + CI |
| Spec → GitHub Issue | `tools/ghsync.py push` (gh CLI) | UI hoặc CI khi spec `approved` |
| Issue → nhánh | `feat/TASK-0042-slug` | `ghsync branch` |
| PR → kiểm tra | Actions: validate spec, lint, test, kiểm tra trailer `Task-Id` | mọi PR |
| Merge → cập nhật | Actions: đổi trạng thái spec, cập nhật CHANGELOG, rebuild context | push `main` |
| Nhật ký cho AI | `context/index/DECISIONS.jsonl` — mỗi merge ghi 1 dòng | post-merge |

Quy ước commit (bắt buộc, CI kiểm):
```
<type>(<comp>): <mô tả ngắn>

Task-Id: TASK-0042
Req-Id: REQ-0007
```

---

## 6. Cổng dịch vụ

| Dịch vụ | Cổng host | Ghi chú |
|---|---|---|
| ui-build (Nhóm A) | 8601 | Xưởng nâng cấp nền tảng |
| ui-ops (Nhóm B) | 8602 | Trung tâm vận hành dữ liệu |
| api | 8000 | `/docs` có OpenAPI cho AI agent |
| db | 5433 | Tránh đụng Postgres cài sẵn ở 5432 |
| qdrant | 6333 | profile `ai` |
| ollama | 11434 | profile `ai` |

## 7. Giới hạn tài nguyên (bắt buộc, vì chỉ có 8GB)

| Container | mem_limit | Ghi chú |
|---|---|---|
| db | 512m | |
| api | 768m | |
| worker | 1g | Nơi chạy pandas/duckdb |
| ui-build | 512m | |
| ui-ops | 640m | Vẽ biểu đồ |
| **Tổng lõi** | **~3.4g** | Còn dư cho Docker + profile `ai` |

## 8. Điều kiện chấp nhận của chính kiến trúc này

- [ ] `docker compose up -d` từ máy sạch → toàn bộ lõi `healthy` trong < 3 phút.
- [ ] Rút mạng → 2 UI vẫn mở được, vẫn tra cứu được dữ liệu đã có.
- [ ] `specctl validate` chạy được cả trong container lẫn trên host.
- [ ] Xoá `data/silver` + `data/gold` → `make rebuild` dựng lại đầy đủ từ bronze.
- [ ] Một model 3B đọc `TASK-*.yaml` bất kỳ là biết chính xác phải sửa file nào.

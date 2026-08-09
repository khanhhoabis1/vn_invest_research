# AGENTS.md — hợp đồng làm việc cho AI agent

> File này dành cho **model AI** làm việc trên repo. Đọc hết trước khi sửa bất cứ thứ gì.
> Người đọc: xem `README.md` và `vnir/ARCHITECTURE.md`.

## Repo này là gì

Nền tảng thu thập dữ liệu kinh tế Việt Nam phục vụ đầu tư chứng khoán và bất động sản.
Chạy cục bộ bằng Docker, toàn bộ mã nguồn mở.

**Ngôn ngữ giao tiếp: tiếng Việt.** Commit, comment, tài liệu, thông báo lỗi — tất cả tiếng Việt.
Mã nguồn (tên biến, hàm) dùng tiếng Anh không dấu.

## Quy tắc tuyệt đối

### 1. Không bao giờ bịa số liệu
Đây là repo tài chính. Một con số bịa có thể dẫn tới quyết định đầu tư sai.

- Không có dữ liệu → nói **"chưa có dữ liệu"**, không suy đoán, không nội suy.
- Không dán output tưởng tượng vào PR. Chạy thật, dán output thật.
- Mọi con số phải trace được về `data/bronze/.../_manifest.json` (có URL + sha256 + HTTP status).

### 2. Bronze là bất biến
`data/bronze/` chỉ được **ghi thêm**, không sửa, không ghi đè, không xoá.
Mỗi lần tải tạo thư mục `dt=<ngày>` mới. Sai sót thì tải lại vào ngày mới, không sửa ngày cũ.

### 3. Thất bại phải ồn ào
Không `except: pass`. Không âm thầm trả dữ liệu cũ khi lấy mới thất bại.

```python
# SAI — nuốt lỗi, không ai biết connector chết
try:
    m = importlib.import_module(name)
except Exception:
    continue

# ĐÚNG — ghi log rõ ràng rồi mới bỏ qua
try:
    m = importlib.import_module(name)
except Exception as exc:
    log.error("Khong nap duoc connector %s: %s", name, exc)
    continue
```

Đây là lỗi có thật đã xảy ra trong repo này: một f-string trỏ sai module khiến **không
connector nào được nạp**, nhưng `except: continue` nuốt lỗi nên API vẫn trả `[]` như thể
bình thường. Mất nhiều bước debug mới tìm ra.

### 4. Không đặt tên trùng module chuẩn Python
Package từng tên `platform` → làm hỏng `platform.system()` mà pandas/streamlit gọi bên trong.
Đã đổi thành `vnir`. CI có bước chặn việc này tái diễn.

Cấm dùng làm tên thư mục gốc: `platform`, `types`, `json`, `io`, `code`, `test`, `string`.

## Luồng làm việc bắt buộc

```
Yêu cầu người dùng
   ↓
REQ-xxxx  (cần gì & vì sao)      specs/requirements/
   ↓
COMP-xxxx (sửa ở đâu)            specs/components/
   ↓
TASK-xxxx (làm chính xác gì)     specs/tasks/
   ↓
Nhánh git → commit có trailer → PR → CI xanh → merge
```

**Không được nhảy cóc.** Không sửa code khi chưa có TASK. Không tạo TASK khi chưa có REQ.

### Lệnh bạn cần

```bash
python tools/specctl.py next --model small   # tìm task vừa sức model nhỏ
python tools/specctl.py show TASK-0001       # gói thực thi tự đủ, <6000 token
python tools/specctl.py validate             # BẮT BUỘC pass trước khi commit
python tools/specctl.py index                # sinh lại SPEC-INDEX.md, phải commit kèm
python tools/ghsync.py push                  # đẩy spec mới lên GitHub Issue
python tools/ghsync.py status                # đối chiếu spec ↔ issue
```

### Commit phải truy vết được

```
feat(connector): them connector GSO PX-Web cho dan so

Lay bang V02.02 qua POST PX-Web API, luu bronze theo dt=<ngay>.
Da chay that: 1.245 dong, HTTP 200.

Task-Id: TASK-0007
Req-Id: REQ-0005
```

Tiền tố: `feat` `fix` `refactor` `docs` `test` `chore` `data`.

## Model nhỏ: bắt đầu từ đâu

Nếu bạn là model 3B–8B, **đừng quét cả repo**. Làm đúng ba bước:

1. `python tools/specctl.py next --model small` → chọn một TASK
2. `python tools/specctl.py show <TASK-ID>` → gói này **tự đủ**, gồm:
   - `files_to_change` — file duy nhất bạn được sửa
   - `files_forbidden` — file cấm đụng
   - `function_signature` — chữ ký phải tuân đúng
   - `acceptance_criteria` — tiêu chí nghiệm thu
   - `verify_command` — lệnh chứng minh bạn làm xong
3. Sửa đúng file được phép → chạy `verify_command` → commit kèm trailer

Không cần đọc file nào ngoài danh sách trong TASK. Nếu thấy thiếu thông tin, **dừng lại và
báo**, đừng đoán.

## Ranh giới hai mặt phẳng

| | Build plane :8601 | Ops plane :8602 |
|---|---|---|
| Việc | Nâng cấp nền tảng | Vận hành thu thập dữ liệu |
| Sửa được | `vnir/`, `tools/`, `specs/` | Bật/tắt nguồn, chạy thu thập |
| Rủi ro | Có thể làm hỏng | Phải luôn chạy |

Thay đổi ở Build plane **không được** làm gián đoạn Ops plane đang chạy.

## Trước khi mở PR

```bash
python tools/spec_validate.py          # spec hợp lệ
python tools/specctl.py index          # chỉ mục đồng bộ
ruff check vnir/ tools/                # lint sạch
python -m compileall -q vnir tools     # biên dịch được
docker compose up -d && docker compose ps   # stack còn chạy
```

Nếu sửa connector, bắt buộc chạy thật và dán output:

```bash
curl -s -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"key":"<source>.<dataset>","dry_run":false}'
```

## Cạm bẫy đã gặp thật trong repo này

| Cạm bẫy | Hậu quả | Cách tránh |
|---|---|---|
| Package tên `platform` | Hỏng `platform.system()` của pandas | Dùng `vnir` |
| `except: continue` khi import | Connector chết âm thầm, API trả `[]` | Luôn log lỗi |
| World Bank `date=1990:2030` | ReadTimeout | Bỏ tham số, lọc ở `parse()` |
| World Bank `per_page=300` | ReadTimeout | Dùng `per_page=100` |
| World Bank trả 502 chập chờn | Cả lần chạy thất bại | Chịu lỗi từng phần |
| `ROOT = dirname(__file__)` trong `scripts/` | Trỏ sai thư mục | Dùng `dirname(dirname(...))` |
| Thêm field mới vào spec | Schema chặn, CI đỏ | Sửa `specs/_schemas/*.json` trước |

## Bảo mật

- Không commit token, API key, mật khẩu. Dùng `.env` (đã gitignore), mẫu ở `.env.example`.
- Không commit dữ liệu thô lớn — `data/` đã gitignore.
- Tôn trọng `robots.txt` và rate limit của nguồn. Nguồn nào cấm scrape thì ghi rõ trong
  registry và **không** viết connector cho nó.

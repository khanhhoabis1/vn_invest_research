# Kho dữ liệu & nghiên cứu kinh tế Việt Nam

Nơi tập trung thu thập dữ liệu kinh tế Việt Nam — **vĩ mô và vi mô** — phục vụ phân tích và
ra quyết định đầu tư **chứng khoán** và **bất động sản**.

Toàn bộ nền tảng chạy **cục bộ bằng Docker Desktop**, dùng **100% công cụ mã nguồn mở**.

---

## Khởi động nhanh

```bash
cp .env.example .env          # lần đầu
docker compose up -d          # dựng toàn bộ nền tảng
docker compose ps             # kiểm tra: db + api phải "healthy"
```

Mở trình duyệt:

| Giao diện | Địa chỉ | Dành cho ai |
|---|---|---|
| 🛠 **Build Plane** | http://localhost:8601 | Người **gửi yêu cầu cải thiện / nâng cấp nền tảng** |
| 📊 **Ops Plane** | http://localhost:8602 | Người **vận hành thu thập & xem dữ liệu đã thu thập** |
| 📖 API (OpenAPI) | http://localhost:8000/docs | AI agent và tích hợp |

Dừng: `docker compose down` · Xem log: `docker compose logs -f worker`

---

## Hai mặt phẳng — vì sao tách đôi

```
BUILD PLANE :8601                         OPS PLANE :8602
"Xưởng nâng cấp nền tảng"                 "Trung tâm vận hành dữ liệu"
                                        
gửi yêu cầu tiếng Việt                    bật/tắt nguồn dữ liệu
   ↓ AI phân rã                           chạy thu thập, xem lịch sử
REQ → COMP → TASK                         kiểm tra chất lượng
   ↓ đồng bộ                              khám phá & vẽ biểu đồ
GitHub Issue → PR                         truy vấn SQL (DuckDB)
```

Sửa nền tảng là việc **có thể gây hỏng**; vận hành thu thập là việc **phải luôn chạy**.
Tách hai UI để người vận hành không vô tình đổi kiến trúc, người phát triển không phải lội qua biểu đồ.
Điểm giao duy nhất: **spec đã được duyệt**.

---

## Cấu trúc thư mục

```
.
├── docker-compose.yml         # Toàn bộ stack, một lệnh dựng lên
├── Dockerfile / requirements.txt
│
├── vnir/                      # ★ NỀN TẢNG (mã nguồn)
│   ├── ARCHITECTURE.md        #   Kiến trúc — đọc file này trước
│   ├── api/                   #   FastAPI phục vụ cả 2 UI
│   ├── worker/                #   Scheduler chạy connector theo lịch
│   ├── connectors/            #   Bộ thu thập dữ liệu (base + từng nguồn)
│   ├── ui_build/              #   Giao diện nhóm A :8601
│   ├── ui_ops/                #   Giao diện nhóm B :8602
│   ├── registry/              #   Danh mục nguồn đã kiểm chứng
│   └── quality/               #   Kiểm định chất lượng dữ liệu
│
├── specs/                     # ★ SPEC — nguồn sự thật của mọi thay đổi
│   ├── SPEC-INDEX.md          #   Bản đồ 1 trang cho người và AI
│   ├── requirements/          #   REQ-xxxx  cần gì & vì sao
│   ├── components/            #   COMP-xxxx sửa ở đâu
│   ├── tasks/                 #   TASK-xxxx làm chính xác gì
│   └── _schemas/              #   JSON Schema kiểm định
│
├── squad/                     # ★ CÁCH ĐỘI LÀM VIỆC
│   ├── 00-charter/            #   Hiến chương, 8 nguyên tắc bất di bất dịch
│   ├── 01-roles/              #   8 vai trò + prompt AI + RACI
│   └── 03-decisions/          #   ADR & biên bản kiểm kê
│
├── tools/                     # specctl (quản lý spec), migrate, ghsync
├── data/                      # bronze (thô, bất biến) → silver → gold
├── context/                   # Dạng LLM đọc hiệu quả: facts, chunks, index
├── intake/                    # Hộp thư yêu cầu thô
│
├── kinh-te-vn-2036/           # Khung nghiên cứu 10 nhánh (kế thừa, còn giá trị)
├── vingroup/ sungroup/ tong-hop/   # Nghiên cứu chuỗi cung ứng (kế thừa)
└── archive/                   # Tài liệu cũ đã lưu trữ, không xoá
```

---

## Tám nguyên tắc bất di bất dịch

Chi tiết trong `squad/00-charter/CHARTER.md`. Tóm tắt:

1. **Không có số liệu không nguồn** — mọi con số trace được về URL gốc + ngày lấy.
2. **Bronze bất biến** — dữ liệu thô không bao giờ bị sửa hay ghi đè.
3. **LLM không được bịa** — không có dữ liệu thì nói "chưa có", không suy đoán.
4. **Mọi yêu cầu đều thành ticket** — nói mồm không tính.
5. **Tài liệu là code** — version bằng git, build sang dạng LLM đọc được.
6. **Quyết định để lại vết** — ADR, không xoá, chỉ supersede.
7. **Hợp pháp & lịch sự với nguồn** — tôn trọng robots.txt, rate limit.
8. **Thất bại phải ồn ào** — không âm thầm trả số cũ.

---

## Dành cho AI agent

```bash
python tools/specctl.py next --model small   # task nào vừa sức
python tools/specctl.py show TASK-0001       # gói thực thi tự đủ
python tools/specctl.py validate             # bắt buộc pass trước commit
```

Mỗi TASK là một **gói tự đủ dưới 6.000 token**: nêu chính xác file được sửa, file cấm đụng,
chữ ký hàm phải tuân, tiêu chí nghiệm thu và lệnh verify. Model 3B đọc là làm được,
không cần quét cả repo. Chi tiết: `vnir/ARCHITECTURE.md` mục 4.

Commit bắt buộc có trailer `Task-Id:` và `Req-Id:`.

---

## Lưu ý về dữ liệu kế thừa

Số liệu thu thập trước khi có nền tảng (2024–2025) đã được chuyển vào
`context/facts/legacy-2024-2025.md` và **gắn nhãn độ tin cậy thấp/trung bình** —
phần lớn dẫn nguồn báo chí thứ cấp, không có URL và ngày truy cập.
Các báo cáo HTML cũ trong `kinh-te-vn-2036/docs-bao-cao/` đã gắn banner cảnh báo.

**Không dùng số liệu kế thừa làm căn cứ ra quyết định đầu tư.**
Chúng chỉ để định hướng nghiên cứu và đối chiếu khi connector chính thức đã lấy được số liệu thật.

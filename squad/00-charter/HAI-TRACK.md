# HAI TRACK LÀM VIỆC

> Đây là tài liệu vận hành chính. Mọi yêu cầu của bạn đều đi vào **một trong hai track**.
> Bạn không cần biết trước nó thuộc track nào — bước phân loại là việc của Squad.

---

## Vì sao phải tách hai track

Bạn đưa ra yêu cầu, nhưng **một mình bạn không thể biết hết** nền tảng đã đáp ứng được chưa.
Nếu để bạn tự phán đoán, sẽ xảy ra hai lỗi tốn kém:

- Yêu cầu xây thứ **đã có sẵn** → lãng phí
- Giao đề bài phân tích khi **chưa có dữ liệu** → đội phân tích bịa số hoặc bế tắc

Nên chèn một **bước thẩm định bắt buộc** giữa bạn và đội thực thi.

```
                    BẠN (người đặt yêu cầu)
                            │
                ┌───────────┴───────────┐
                │                       │
      "Tôi muốn nền tảng          "Phân tích giúp tôi
       làm được X"                  ngành/cổ phiếu Y"
                │                       │
                ▼                       ▼
        ┌───────────────┐       ┌───────────────┐
        │   TRACK 1     │       │   TRACK 2     │
        │ Phát triển    │◄──────│ Thu thập &    │
        │ nền tảng      │ thiếu │ phân tích     │
        └───────────────┘ luồng └───────────────┘
                │         lấy DL         │
                ▼                       ▼
        Phiên bản mới           Báo cáo đầu tư
        được release            có trích dẫn nguồn
```

Mũi tên ngược từ Track 2 sang Track 1 là điểm mấu chốt: khi đội phân tích phát hiện
**chưa có luồng lấy dữ liệu**, họ không tự chế biến số liệu mà **đẩy ngược** thành yêu cầu
phát triển.

---

# TRACK 1 — Phát triển nền tảng

**Kích hoạt khi:** bạn nói "tôi muốn nền tảng làm được X".

## Luồng đầy đủ

```
① BẠN nêu yêu cầu (tiếng Việt tự nhiên, không cần kỹ thuật)
        │
        ▼
② ĐỘI PHÂN TÍCH ĐẦU TƯ thẩm định  ──►  ASSESS-xxxx
   "Phiên bản hiện tại đã đáp ứng chưa?"
        │
        ├──► ĐÃ ĐÁP ỨNG      → trả lời bạn ngay + hướng dẫn dùng. HẾT.
        ├──► ĐÁP ỨNG MỘT PHẦN → nêu rõ phần thiếu → sang ③
        └──► CHƯA ĐÁP ỨNG    → sang ③
        │
        ▼
③ ĐỘI PHÁT TRIỂN phân tích & lập kế hoạch
   REQ-xxxx → COMP-xxxx → TASK-xxxx
        │
        ▼
④ Thực thi (người hoặc AI) → PR → CI xanh → merge
        │
        ▼
⑤ RELEASE phiên bản mới (gắn tag, ghi CHANGELOG)
        │
        ▼
⑥ Báo lại bạn: "Yêu cầu của anh giờ dùng được, cách dùng như sau…"
```

## Bước ② — Thẩm định, chi tiết

Đây là bước bạn yêu cầu bổ sung, và là bước **quan trọng nhất** của Track 1.

Người chịu trách nhiệm: **BA (Business Analyst đầu tư)**, tham vấn **RES** và **ARCH**.

Bốn câu hỏi phải trả lời, **có bằng chứng thật**:

| # | Câu hỏi | Bằng chứng bắt buộc |
|---|---|---|
| 1 | Nền tảng hiện tại đã làm được chưa? | Lệnh đã chạy + output thật, hoặc `GET /sources`, `GET /datasets` |
| 2 | Nếu chưa, thiếu chính xác cái gì? | Liệt kê: thiếu connector / thiếu chỉ số / thiếu giao diện / thiếu tính năng |
| 3 | Có nguồn dữ liệu hợp pháp không? | Đối chiếu `vnir/registry/nguon-*.md`, kiểm chứng bằng `curl` |
| 4 | Đáng làm không? | Điểm ưu tiên = tác động × tự tin ÷ công sức |

**Kết luận thẩm định chỉ có 4 giá trị:**

- `da_dap_ung` — đã có, chỉ cần hướng dẫn bạn dùng
- `dap_ung_mot_phan` — có một phần, nêu rõ phần thiếu
- `chua_dap_ung` — phải phát triển mới
- `khong_kha_thi` — nguồn không tồn tại / bị chặn / vi phạm pháp lý (nêu phương án thay thế)

> **Quy tắc chống bịa:** không được kết luận "đã đáp ứng" nếu chưa chạy lệnh kiểm chứng thật.
> Câu "chắc là có rồi" không được chấp nhận.

## Lệnh Track 1

```bash
# Bạn gửi yêu cầu
python tools/track.py yeu-cau "Tôi muốn xem lãi suất liên ngân hàng qua đêm"

# Đội phân tích thẩm định
python tools/track.py tham-dinh ASSESS-0001 --ket-luan chua_dap_ung \
    --thieu "connector SBV" --bang-chung "GET /sources chỉ có worldbank"

# Chuyển sang đội phát triển (tự sinh REQ nối vào ASSESS)
python tools/track.py chuyen-phat-trien ASSESS-0001

# Xem hàng đợi
python tools/track.py hang-doi --track 1
```

---

# TRACK 2 — Thu thập dữ liệu & phân tích đầu tư

**Kích hoạt khi:** bạn giao đề bài "phân tích ngành X" hoặc "phân tích cổ phiếu Y".

## Luồng đầy đủ

```
① BẠN giao đề bài  ──►  BRIEF-xxxx
        │
        ▼
② ĐỘI ĐẦU TƯ kiểm kê dữ liệu
   "Cần dữ liệu gì? Nền tảng có sẵn không?"
        │
        ├──► CÓ ĐỦ          → sang ④
        ├──► CÓ NHƯNG CŨ    → chạy cập nhật (POST /runs) → sang ④
        └──► CHƯA CÓ LUỒNG  → ⚠ ĐẨY SANG TRACK 1, ghi rõ đang chờ gì
        │
        ▼
③ Thu thập / cập nhật dữ liệu (bronze → silver → gold)
        │
        ▼
④ PHÂN TÍCH — mọi con số phải trích dẫn được về manifest
        │
        ▼
⑤ BÁO CÁO gửi bạn: luận điểm + bằng chứng + rủi ro + điều chưa biết
```

## Bước ② — Kiểm kê dữ liệu, chi tiết

```bash
python tools/track.py kiem-ke BRIEF-0001
```

Sinh ra bảng đối chiếu **dữ liệu cần** ↔ **dữ liệu có**:

| Dữ liệu cần | Trạng thái | Hành động |
|---|---|---|
| GDP theo quý | ✅ có, cập nhật 09/08 | dùng luôn |
| CPI theo tháng | ⚠️ có, cũ 45 ngày | `POST /runs` cập nhật |
| Lãi suất liên NH | ❌ chưa có luồng | **đẩy Track 1** → REQ mới |

## Quy tắc báo cáo đầu tư

Báo cáo **bắt buộc** có 4 phần, thiếu phần nào là không đạt:

1. **Luận điểm** — kết luận đầu tư, nêu thẳng
2. **Bằng chứng** — mỗi số liệu kèm nguồn + ngày + link manifest
3. **Rủi ro & phản biện** — điều gì làm luận điểm sai
4. **Điều chưa biết** — dữ liệu còn thiếu, độ tin cậy thấp ở đâu

> **Quy tắc chống bịa:** thiếu dữ liệu thì ghi **"chưa có dữ liệu"**, tuyệt đối không nội suy,
> không lấy số từ trí nhớ, không dùng số kế thừa chưa kiểm chứng làm căn cứ chính.

---

## Ai làm gì

| Bước | Vai trò chính | Hỗ trợ |
|---|---|---|
| T1 ② Thẩm định | **BA** | RES, ARCH |
| T1 ③ Lập kế hoạch | **ARCH** | DE, AIE |
| T1 ④ Thực thi | **DE / AIE** | QA |
| T1 ⑤ Release | **ARCH** | DOC |
| T2 ② Kiểm kê | **RES** | DE |
| T2 ③ Thu thập | **DE** | QA |
| T2 ④ Phân tích | **RES** | BA |
| T2 ⑤ Báo cáo | **RES** | DOC, QA |

Chi tiết vai trò: `squad/01-roles/ROLES.md`. Prompt cho AI: `squad/01-roles/prompts/`.

---

## Trạng thái vòng đời

**ASSESS** (thẩm định — Track 1)
```
moi → dang_tham_dinh → xong
                        ├── da_dap_ung        (kết thúc, trả lời bạn)
                        ├── dap_ung_mot_phan  → sinh REQ
                        ├── chua_dap_ung      → sinh REQ
                        └── khong_kha_thi     (kết thúc, nêu lý do)
```

**BRIEF** (đề bài phân tích — Track 2)
```
moi → kiem_ke_du_lieu → ├── du_du_lieu    → dang_phan_tich → xong
                        └── thieu_du_lieu → cho_track_1 ──┐
                                                ▲          │
                                                └──────────┘
                                            (REQ xong thì quay lại)
```

Trạng thái `cho_track_1` là **điểm nối** giữa hai track. Khi REQ tương ứng được release,
BRIEF tự động được nhắc để tiếp tục.

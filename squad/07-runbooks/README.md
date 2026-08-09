# Runbooks — Thư mục vận hành chi tiết

Mỗi runbook là một kịch bản thao tác cụ thể, viết theo thứ tự bước. RUNBOOK.md (thư mục gốc)
là bản tóm tắt; đây là bản đầy đủ cho từng luồng công việc.

| File | Dành cho | Khi nào đọc |
|---|---|---|
| `01-khoi-dong.md` | Mọi người | Lần đầu chạy, hoặc stack bị tắt |
| `02-track1-phat-trien.md` | Người đề xuất cải tiến | Muốn nền tảng làm được gì đó |
| `03-track2-phan-tich.md` | Nhà phân tích / bạn | Giao đề bài, thu thập, báo cáo |
| `04-su-co.md` | Khi có lỗi | Một trong các triệu chứng ở bảng sự cố |

**Nguyên tắc chung (P1–P8 trong Charter vẫn áp dụng):**
- Không có số liệu không nguồn.
- Bronze bất biến (không sửa dữ liệu thô).
- LLM/agent không được bịa — thiếu dữ liệu thì nói "chưa có".
- Thất bại phải ồn ào (báo lỗi, không trả số cũ).

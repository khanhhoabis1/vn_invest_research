# KHUNG NGHIÊN CỨU KINH TẾ VIỆT NAM 10 NĂM TỚI (2026–2036)

> Bộ khung phân nhánh nghiên cứu vĩ mô – ngành cho chiến lược đầu tư và hoạch định chính sách.
> Mỗi nhánh tương ứng một thư mục trong repo này, chứa `README.md` mô tả chi tiết, câu hỏi nghiên cứu, chỉ số và nguồn dữ liệu.

## Mục tiêu
1. Xác định các lực đẩy (drivers) và rủi ro (risks) lớn nhất của kinh tế Việt Nam giai đoạn 2026–2036.
2. Xây dựng hệ chỉ số theo dõi (KPI/dashboard) cho từng chủ đề.
3. Làm cơ sở đánh giá kịch bản tăng trưởng và cơ hội đầu tư dài hạn.

## Phương pháp luận (tóm tắt)
- **Góc nhìn đa tầng:** Vĩ mô (chu kỳ) → Cơ cấu (ngành) → Vi mô (doanh nghiệp/người dân).
- **Kịch bản:** Baseline / Lạc quan / Bi quan cho mỗi nhánh lớn.
- **Cập nhật:** Quý — rà soát chỉ số; Năm — rà soát câu hỏi nghiên cứu và kịch bản.
- Chi tiết xem `00-tong-quan-va-phuong-phap/PHUONG-PHAP.md`.

## Cây 10 nhánh nghiên cứu chính

| # | Nhánh | Thư mục | Trọng tâm |
|---|-------|---------|-----------|
| 1 | Vĩ mô & Tăng trưởng | `01-vi-mo-tang-truong/` | GDP, TFP, lạm phát, tỷ giá, nợ công |
| 2 | Dân số & Lao động | `02-dan-so-lao-dong/` | Già hóa, kỹ năng, đô thị hóa |
| 3 | Công nghiệp & Chuỗi cung ứng | `03-cong-nghiep-chuoi-cung-ung/` | China+1, FDI, bán dẫn, logistics |
| 4 | Chuyển đổi số & AI | `04-chuyen-doi-so-ai/` | AI, kinh tế số, fintech, chính phủ số |
| 5 | Năng lượng & Chuyển đổi xanh | `05-nang-luong-xanh/` | Net Zero, điện tái tạo, tài chính xanh |
| 6 | Bất động sản & Đô thị | `06-bat-dong-san-do-thi/` | Chu kỳ BĐS, nhà ở xã hội, hạ tầng |
| 7 | Tài chính & Ngân hàng | `07-tai-chinh-ngan-hang/` | Nợ xấu, thị trường vốn, fintech |
| 8 | Nông nghiệp & Bền vững | `08-nong-nghiep-ben-vung/` | Nông nghiệp công nghệ cao, khí hậu |
| 9 | Thương mại & Hội nhập | `09-thuong-mai-hoi-nhap/` | EVFTA/CPTPP/RCEP, Mỹ–Trung |
| 10 | Doanh nghiệp & Khởi nghiệp | `10-doanh-nghiep-khoi-nghiep/` | Khu vực tư nhân, startup, đổi mới |

## Cấu trúc thư mục
```
kinh-te-vn-2036/
├── KHUNG-NGHIEN-CUU.md          # Tài liệu này
├── 00-tong-quan-va-phuong-phap/ # Mục tiêu, phương pháp, kịch bản
├── 01-vi-mo-tang-truong/        # + sub: gdp-nang-suat, lam-phat-ty-gia, ngan-sach-no-cong
├── 02-dan-so-lao-dong/          # + sub: gia-hoa-dan-so, viec-lam-ky-nang, do-thi-hoa
├── 03-cong-nghiep-chuoi-cung-ung/ # + sub: china-plus-1-fdi, ban-dan-dien-tu, logistics
├── 04-chuyen-doi-so-ai/         # + sub: ai-cong-nghe, ecommerce-fintech, chinh-phu-so
├── 05-nang-luong-xanh/          # + sub: dien-tai-tao, net-zero, tai-chinh-xanh
├── 06-bat-dong-san-do-thi/
├── 07-tai-chinh-ngan-hang/      # + sub: ngan-hang-tin-dung, chung-khoan, fintech
├── 08-nong-nghiep-ben-vung/
├── 09-thuong-mai-hoi-nhap/      # + sub: hiep-dinh-fta, my-trung
├── 10-doanh-nghiep-khoi-nghiep/
├── data-nguon/                  # Dữ liệu thô và bộ sưu tập nguồn
├── docs/                        # Tài liệu tham khảo, bài báo, báo cáo
└── docs-bao-cao/                # Báo cáo tổng hợp theo kỳ
```

## Cách sử dụng
- Mỗi nhánh: đọc `README.md` → cập nhật chỉ số vào dashboard → ghi chú phát hiện vào `docs-bao-cao/`.
- Thêm dữ liệu thô vào `data-nguon/<tên-nhánh>/`.
- Mở rộng nhánh bằng cách tạo sub-folder và bổ sung câu hỏi nghiên cứu tương ứng.

---
*Tạo bởi Hermes Agent — khung sườn, cần bổ sung số liệu thực tế và cập nhật định kỳ.*

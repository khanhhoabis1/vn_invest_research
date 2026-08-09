# KIỂM KÊ & ĐÁNH GIÁ TÀI SẢN CŨ — trước khi dọn dẹp

> Lập ngày 09/08/2026, sau khi nền tảng mới (`vnir/` + Docker) đã chạy được.
> **Nguyên tắc: không xoá thứ gì chưa đánh giá.** Mọi số liệu dưới đây lấy từ kiểm tra thực tế trên đĩa.

## 1. Bảng kiểm kê

| Đường dẫn | Kích thước | Nội dung | Chất lượng nguồn | Kết luận |
|---|---|---|---|---|
| `kinh-te-vn-2036/KHUNG-NGHIEN-CUU.md` | 2.5 KB | Khung 10 nhánh nghiên cứu vĩ mô | Khung tư duy, không phải số liệu | **GIỮ** — đây là tài sản trí tuệ, nền mới chưa có |
| `kinh-te-vn-2036/00-…/PHUONG-PHAP.md` | ~1 KB | Phương pháp luận, 3 kịch bản | Không cần nguồn | **GIỮ** |
| `kinh-te-vn-2036/0X-…/README.md` × 10 | 1.3–1.8 KB mỗi file | Câu hỏi nghiên cứu từng nhánh | Định tính, có giá trị | **GIỮ** |
| `kinh-te-vn-2036/data-nguon/master-data.json` | 8 KB | 10 nhánh + 10 chỉ số headline | ⚠️ Nguồn thứ cấp | **GIỮ CÓ ĐIỀU KIỆN** → chuyển thành `legacy_facts` |
| `kinh-te-vn-2036/data-nguon/chi-so-2024-2025.json` | 8 KB | Trùng 9/10 nhánh với file trên, khác ở chú thích dài hơn | ⚠️ Nguồn thứ cấp | **HỢP NHẤT** vào file trên rồi bỏ |
| `kinh-te-vn-2036/docs-bao-cao/*.html` × 4 | 57 KB | Dashboard, mindmap, báo cáo lịch sử | Sinh từ JSON, có hardcode số | **GIỮ** như ảnh chụp lịch sử (đóng băng) |
| `kinh-te-vn-2036/scripts/build_*.py` × 2 | 16 KB | Sinh HTML từ `master-data.json` | Chạy được, độc lập | **GIỮ** — vẫn dùng được |
| `kinh-te-vn-2036/docs/` | 0 file | Thư mục rỗng | — | **XOÁ** |
| `kinh-te-vn-2036/.venv/` | **2.9 MB** | venv thừa, không được git track | — | **XOÁ** (nền mới dùng Docker) |
| `vingroup/nha-cung-ung.md` | 3.1 KB | Chuỗi cung ứng Vingroup | Định tính, ghi rõ "cần xác minh" | **GIỮ** |
| `sungroup/nha-cung-ung.md` | 3.0 KB | Chuỗi cung ứng Sun Group | Định tính | **GIỮ** |
| `tong-hop/tong-hop.md` | 3.1 KB | Bảng đối chiếu HVH/CTD/HBC + luận điểm | Có mục "Rủi ro/Lưu ý" trung thực | **GIỮ** |
| `IDEA.md` | 524 B | Ý tưởng dashboard sentiment (tiếng Anh) | Chưa triển khai, lạc khỏi hướng hiện tại | **LƯU TRỮ** vào `archive/` |
| `GIT_WORKFLOW.md` | 2.7 KB | Quy trình git thủ công cho nghiên cứu | Vẫn đúng, nhưng nền mới có CI/spec | **GỘP** vào tài liệu mới |
| `README.md` (gốc) | 1.2 KB | Mô tả cũ, chưa biết gì về nền tảng | Lỗi thời | **VIẾT LẠI** |
| `vn_macro_data_catalog.md` | 14.4 KB | Catalog nguồn vĩ mô, endpoint đã curl | ✅ Có kiểm chứng | **CHUYỂN** vào `vnir/registry/` |

## 2. Ba vấn đề chất lượng phát hiện được

### 2.1 Số liệu cũ dẫn nguồn báo chí, không truy vết được
Trong `master-data.json`, nguồn được ghi là `VietnamNet`, `VnExpress`, `Statista`, `VIR`, `Reuters` — **không có URL, không có ngày truy cập**. Ví dụ:

```json
{"k": "Lạm phát CPI 2024", "v": "3,63%",  "s": "VietnamNet"}
{"k": "Tỷ lệ đô thị hóa 2024", "v": "38,5%", "s": "Statista"}
```

Vi phạm **P1 (không có số liệu không nguồn)** của charter mới. Không thể dùng làm dữ liệu gold.

### 2.2 Số liệu ước tính trộn lẫn với số liệu công bố
File tự đánh dấu `*` cho ước tính (`Tín dụng/GDP ~125%*`, `NPL ~4,5%*`) nhưng dashboard HTML hiển thị **ngang hàng** với số liệu chính thức. Người đọc không phân biệt được.

### 2.3 Trùng lặp dữ liệu ở hai nơi
`master-data.json` và `chi-so-2024-2025.json` mô tả cùng 10 nhánh, khác nhau ở 9/10 nhánh nhưng chỉ ở phần chú thích. Hai nguồn sự thật ⇒ chắc chắn sẽ lệch nhau khi cập nhật.

## 3. Quyết định xử lý

| Hành động | Đối tượng | Lý do |
|---|---|---|
| **XOÁ** | `kinh-te-vn-2036/.venv/` (2.9 MB) | Nền tảng mới chạy Docker, venv này không được track |
| **XOÁ** | `kinh-te-vn-2036/docs/` | Thư mục rỗng |
| **CHUYỂN** | `vn_macro_data_catalog.md` → `vnir/registry/` | Thuộc về registry nguồn của nền tảng mới |
| **CHUYỂN** | `IDEA.md` → `archive/` | Ý tưởng chưa dùng, giữ lại nhưng không để ở gốc |
| **CHUYỂN ĐỔI** | 2 file JSON → `context/facts/legacy-2024-2025.md` | Giữ giá trị tham khảo, nhưng **đánh dấu rõ là số liệu chưa kiểm chứng** |
| **ĐÓNG BĂNG** | 4 file HTML | Thêm banner "ảnh chụp lịch sử", không cập nhật nữa |
| **GIỮ NGUYÊN** | Khung nghiên cứu, 10 README nhánh, 3 file chuỗi cung ứng | Tài sản trí tuệ định tính, nền mới chưa thay thế được |
| **VIẾT LẠI** | `README.md` gốc | Phải mô tả nền tảng mới |

## 4. Nguyên tắc áp dụng khi dọn

1. **Không xoá nội dung nghiên cứu** — chỉ xoá thứ tái tạo được (`.venv`, thư mục rỗng).
2. **Số liệu cũ không bị vứt đi** mà bị *hạ cấp*: chuyển sang `context/facts/` với nhãn
   `do_tin_cay: thap` và `can_kiem_chung_lai: true`, để LLM biết đây là tham khảo chứ không phải sự thật.
3. **Git giữ toàn bộ lịch sử** — kể cả khi xoá, `git log` vẫn khôi phục được.
4. Mỗi chỉ số cũ đều được ghi kèm **connector nào sẽ thay thế nó** trong tương lai.

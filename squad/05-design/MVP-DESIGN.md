# THIẾT KẾ MVP — VN Invest Research Platform (tự động khuyến nghị)

> Tổng hợp từ 3 squad brainstorm (Kiến trúc / Dữ liệu / Engine) + 2 catalog nguồn thực tế.
> Lập 09/08/2026. Mục tiêu: platform local, open-source, ≤8GB RAM, tự động từ dữ liệu →
> khuyến nghị danh mục cổ phiếu VN + giá mục tiêu, có bằng chứng, chống bịa số.

## 1. Quyết định cốt lõi: KEEP + REFACTOR

Giữ lại IP cốt lõi hiện có, xây thêm "thịt" (engine tự động), sửa hạ tầng boot:

- **GIỮ:** hệ spec machine-readable (REQ/COMP/TASK/ASSESS/BRIEF), mô hình 2 track,
  cơ chế chống bịa số liệu, stack Postgres+FastAPI+Streamlit, connector framework.
- **SỬA:** lỗi boot (container mồ côi Dev sập/UAT lửng) → chuẩn hóa Docker Compose,
  healthcheck, depends_on, network chung.
- **THÊM:** AnalyticsEngine, RecommendEngine, EvidenceLedger, ReviewGate, Scheduler, AlertNotifier.
- **THAY:** World Bank connector (hay 502) → thêm retry + fallback nguồn VN (GSO PX-Web, SSI, KBS).

## 2. Ranh giới TRONG / NGOÀI platform

**TRONG (tự động, local, OSS):**
1. Thu thập & lưu raw từ nguồn MIỄN PHÍ (GSO, SSI, KBS, VNDirect scrape, vnstock).
2. Làm sạch, tính định giá, scoring, backtest (pure compute, offline).
3. Sinh khuyến nghị + giá mục tiêu từ evidence (engine cốt lõi).
4. Lưu trữ, API, scheduler, UI, EvidenceLedger (chống bịa).
5. ReviewGate chờ duyệt (phần mềm, dừng ở đây).

**NGOÀI (con người / trả phí / broker):**
1. Con người duyệt khuyến nghị (trách nhiệm pháp lý).
2. Thực thi qua broker (không có SDK trả phí, rủi ro do người quyết).
3. Data trả phí (Bloomberg, Refinitiv, FiinPro) — vi phạm ràng buộc không thuê bao.
4. Quyết định mua/bán cuối & quản trị rủi ro.

---

*(tiếp theo: phần 3 luồng dữ liệu & module — xem MVP-DESIGN-2.md)*

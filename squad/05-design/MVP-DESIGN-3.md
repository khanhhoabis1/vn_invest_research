# MVP DESIGN — phần 3: Lộ trình 4 pha & Spec MVP

## 6. Lộ trình 4 pha

**PHA 1 — MVP (Boot sạch + 1 luồng thật)**
- Fix Docker Compose (Dev/UAT, healthcheck, network).
- World Bank connector retry → đạt ≥12/14 chỉ số; thêm GSO PX-Web làm fallback.
- ingest → RawStore → CleanTransform → Postgres chạy end-to-end với 1-2 mã VN mẫu.
- EvidenceLedger áp dụng.
- **Chạy được:** platform boot sạch, có data thật lưu DB.

**PHA 2 — Engine định giá**
- AnalyticsEngine (P/E, P/B, ROE, DCF đơn giản, Gordon) + RecommendEngine.
- Sinh khuyến nghị mã đơn lẻ + giá mục tiêu, mọi số có evidence.
- **Chạy được:** từ data → 1 khuyến nghị có bằng chứng cho 1 mã.

**PHA 3 — Tự động hóa & đa mã**
- Scheduler (daily/weekly), mở rộng toàn bộ mã HSX/HNX (scrape VNDirect/CafeF).
- Danh mục top-N + trọng số + stop-loss, ReviewGate + AlertNotifier.
- **Chạy được:** mỗi sáng có draft danh mục tự động chờ duyệt + thông báo.

**PHA 4 — Vững chắc**
- Backtest quy tắc, scoring đa yếu tố, UI drill-down evidence, export báo cáo.
- Thêm nguồn dự phòng, giám sát RAM/health.
- **Chạy được:** hệ thống đầu tư tự động ổn định, có bằng chứng, duyệt-by-human.

## 7. Spec MVP (từ 5 issue còn mở)

| Issue | Spec mới | Pha | Nội dung |
|-------|----------|-----|----------|
| #17 REQ-0005 | REQ-MVP-01 | P1 | Thu thập tự động CK/BĐS VN (GSO/SSI/KBS/VNDirect, thay WB) |
| #12 COMP-0010 | COMP-MVP-01 | P1 | Data Quality + EvidenceLedger (chống bịa, trace→raw) |
| #11 COMP-0009 | COMP-MVP-02 | P1 | Context Builder (chuẩn hóa raw → curated cho engine) |
| #16 REQ-0004 | REQ-MVP-02 | P2 | AnalyticsEngine + RecommendEngine (định giá, scoring, PT) |
| #18 REQ-0006 | REQ-MVP-03 | P2 | Ghi nhận tài liệu → LLM context (tri thức nền) |

**Nguyên tắc chung:** mọi khuyến nghị phải có evidence (source_id + ngày + dòng gốc).
Thiếu >40% tín hiệu → loại mã. Upside >±50% → bắt buộc người duyệt.

---

*Chi tiết engine (khung tín hiệu 6 nhóm, scoring 0-100, portfolio 10-15 mã, giá mục tiêu
P/E+DCF) xem MVP-ENGINE.md. Catalog nguồn: vnir/registry/nguon-vi-mo.md, nguon-ck-bds.md.*

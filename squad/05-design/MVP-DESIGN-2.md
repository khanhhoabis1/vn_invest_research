# MVP DESIGN — phần 2: Luồng dữ liệu, Module, Công nghệ

## 3. Luồng dữ liệu (data flow)

```
Sources(miễn phí) → [DataIngestConnector] → RawStore(+provenance)
  → [CleanTransform] → CuratedDB(Postgres)
  → [AnalyticsEngine: valuation/scoring/backtest]
  → [RecommendEngine + EvidenceLedger check]
  → DraftRecommendation → [ReviewGate: chờ người duyệt]
  → PublishedRecommendation → [ApiService] → [PresentationUI + AlertNotifier]
```

- Chạy định kỳ qua Scheduler; mọi node xuất số phải pass EvidenceLedger (trace → raw).
- Nếu data gap (vd World Bank 502) → pipeline đánh dấu thiếu, bỏ qua chỉ số đó, KHÔNG tự sinh.

## 4. Module (11)

| # | Module | Trách nhiệm |
|---|--------|-------------|
| 1 | DataIngestConnector | Thu thập raw, retry/backoff, ghi provenance |
| 2 | RawStore | Lưu raw bất biến (parquet) + metadata + checksum |
| 3 | EvidenceLedger | Chống bịa: mọi số trace → raw + source URL |
| 4 | CleanTransform | Làm sạch, chuẩn hóa, tính chỉ số phái sinh |
| 5 | AnalyticsEngine | Định giá (DCF/Gordon/PE), scoring, backtest |
| 6 | RecommendEngine | Tổng hợp khuyến nghị, trọng số, giá mục tiêu |
| 7 | Scheduler | Lên lịch ingest/analyze (daily/weekly) |
| 8 | ApiService | REST API nội bộ: /recommendations, /evidence, /status |
| 9 | PresentationUI | Dashboard 1 (quản trị) + Dashboard 2 (đầu tư) |
| 10 | ReviewGate | Chốt draft chờ người duyệt, ghi log phê duyệt |
| 11 | AlertNotifier | Thông báo khuyến nghị mới / data gap |

## 5. Công nghệ

- **Ngôn ngữ:** Python 3.11 (đồng nhất ingest/analytics/API/UI).
- **DB:** PostgreSQL 16 (curated + EvidenceLedger); raw lưu parquet trên volume Docker.
- **Scheduler:** APScheduler trong container Python (nhẹ, không Airflow).
- **API:** FastAPI (đã có). **UI:** Streamlit (đã có 2 dashboard).
- **Scraping:** httpx + BeautifulSoup/lxml cho nguồn VN miễn phí.
- **Compute:** pandas, numpy, scipy (z-score), statsmodels (Beta) — KHÔNG LLM/ML nặng.
- **Container:** Docker Compose macOS arm64, giới hạn memory mỗi service.

---

*(tiếp theo: phần 3 roadmap 4 pha + spec MVP — xem MVP-DESIGN-3.md)*

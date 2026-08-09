# MVP ENGINE — Khung phân tích & khuyến nghị (từ Squad 2)

## A. Khung tín hiệu 6 nhóm (mọi thứ từ dữ liệu gốc, không sinh số)

1. **VALUATION** — P/E = Giá/EPS_ttm; P/B = Giá/BVPS; EV/EBITDA.
   Điểm = z-score(P/E) so trung vị ngành (thấp=tốt). Loại nếu EPS≤0.
2. **MOMENTUM** — ROC_3M, ROC_12M, RSI_14. Điểm = z(ROC_12M)+0.5*z(ROC_3M).
3. **QUALITY** — ROE, ROA, Biên LN, D/E. Điểm = z(ROE)+z(ROA)+z(Biên)-z(D/E).
4. **GROWTH** — g_revenue, g_eps (YoY). Điểm = z(g_rev)+z(g_eps). Cần ≥4 quý.
5. **RISK** — Volatility_annual = std(returns)*√252; Beta vs VNINDEX (hồi quy 1 năm);
   Liquidity = trung bình giá trị GD 20 phiên.
6. **(mở rộng)** — Sentiment từ cafeland/vietstock nếu có.

## B. Chấm điểm & xếp hạng (0-100)

- Trọng số: Valuation 25%, Quality 25%, Momentum 20%, Growth 20%, Risk 10%.
- Tín hiệu NULL → bỏ qua, renormalize trọng số còn lại.
- Composite = 100 × Σ(w_i × norm(score_i)).
- Tier: A (≥70), B (55-70), C (40-55), D (<40).
- Vào danh mục: chỉ tier A/B và Valuation+Quality ≠ NULL.

## C. Cấu trúc danh mục

- 10-15 mã (tối đa 20). Mặc định EQUAL-WEIGHT; tùy chọn SCORE-WEIGHT (cap 2×equal).
- Sector cap 30% (theo ICB/VN10).
- Tái cân bằng: QUÝ + sự kiện (mã rơi tier D hoặc score đổi >20).

## D. Giá mục tiêu

- **PT1 (P/E mục tiêu, 70%):** P/E_mục = trung vị 3 năm −1σ; EPS_proj = EPS_ttm×(1+g_eps_3y).
- **PT2 (DCF đơn giản, 30%):** FCF 3 năm, g_term 3%, WACC 12% (ghi rõ giả định).
- PT = trung bình 2 phương pháp. Upside = (PT−Giá)/Giá. Mọi giả định phải in ra.

## E. Guardrail chống bịa

1. Mọi số lưu kèm source_id (file + ngày + dòng gốc). Thiếu → không xuất.
2. NULL bị bỏ qua (availability weighting), KHÔNG điền ước lượng. >40% NULL → loại mã.
3. Sanity cứng: P/E>100 hoặc <0, EPS≤0, giá≤0 → lỗi, không chấm.
4. Cần người duyệt: mua mã mới, upside >+50%/<-30%, tin sự kiện chưa có data → `pending_review.json`.
5. Versioning: snapshot input+config+output mỗi lần chạy để audit.
6. Confidence flag: % tín hiệu có data; <60% → gắn "thấp tin cậy".

## F. Giới hạn local & xử lý

- 1500+ mã × 5 năm → pandas vector hóa, parquet, chạy cuối ngày không realtime.
- RAM 8GB đủ nếu giữ 1 năm giá float32 + BCTC quý. Thiếu RAM → tính lô 100 mã.
- Forward-fill tối đa 5 phiên, sau đó NULL; loại mã <250 phiên/năm.
- Fallback: nguồn lỗi → dừng, báo "dữ liệu cũ từ <ngày>", KHÔNG sinh số thay.

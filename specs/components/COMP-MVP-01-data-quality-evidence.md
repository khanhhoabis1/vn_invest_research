id: COMP-MVP-01
title: Data Quality & EvidenceLedger (chong bias so lieu)
status: planned
priority: 9
plane: ops
tags: [mvp, p1, quality, evidence]
created: 2026-08-09
mo_ta: |
  Xay dung lop Data Quality + EvidenceLedger dam bao moi so lieu dau ra deu trace
  nguoc duoc ve raw record + source URL. Tu choi so khong co bang chung.
acceptance:
  - Moi ban ghi vao CuratedDB phai co source_id (file + ngay + dong goc).
  - Sanity check cung: PE>100 hoac <0, EPS<=0, gia<=0 -> bao loi, khong cham diem.
  - NULL bi bo qua (availability weighting), khong dien uoc luong tuy y.
  - >40% tin hieu cua ma la NULL -> loai ma khoi universe.
can:
  - connector framework + RawStore (parquet)
  - co che cham diem o MVP-ENGINE.md (guardrail)
khong_duoc:
  - Sinh so thay the khi nguon loi

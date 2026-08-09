id: COMP-MVP-02
title: Context Builder (chuan hoa raw -> curated)
status: planned
priority: 7
plane: ops
tags: [mvp, p1, context, transform]
created: 2026-08-09
mo_ta: |
  Module CleanTransform chuan hoa du lieu thao tu nhieu nguon ve schema chung,
  tinh chi so phai sinh (PE/PB/ROE/tang truong), ghi log day du.
acceptance:
  - Raw da thu (COMP-MVP-01) duoc chuan hoa thanh bang curated trong Postgres.
  - Chi so phai sinh tinh tu raw co that, co the truy van qua API /evidence.
  - Chay duoc voi 1-2 ma VN mau (VNM, VND) end-to-end.
can:
  - Postgres hien tai
  - RawStore parquet tu REQ-MVP-01
khong_duoc:
  - Ghi de raw tu dong

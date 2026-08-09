## Thay đổi gì

<!-- Mô tả ngắn gọn. Nếu sửa nhiều thứ, cân nhắc tách PR. -->

## Truy vết về spec

<!-- BẮT BUỘC. CI kiểm tra commit có trailer Task-Id/Req-Id. -->

- Đóng: #
- Spec: `REQ-` / `COMP-` / `TASK-`

## Bằng chứng đã chạy thật

<!-- Dán output THẬT. Không mô tả suông "đã test ok". -->

```
$ 
```

## Tự kiểm

- [ ] `python tools/specctl.py validate` — pass
- [ ] `python tools/specctl.py index` — đã chạy và commit `SPEC-INDEX.md`
- [ ] `ruff check vnir/ tools/` — sạch
- [ ] Đã chạy thật và dán output ở trên (không phải output tưởng tượng)
- [ ] Không commit credential, token, hay dữ liệu thô lớn
- [ ] Nếu sửa connector: đã chạy `POST /runs` và dữ liệu về đúng `data/bronze/`

## Ảnh hưởng

- [ ] Không phá vỡ tương thích ngược
- [ ] Có thay đổi schema dữ liệu → đã mô tả cách migrate

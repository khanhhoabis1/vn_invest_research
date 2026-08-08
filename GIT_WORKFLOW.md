# Quy trình quản lý phiên bản nghiên cứu (Git)

Mục tiêu: lưu lại từng bước nghiên cứu để **rollback** (quay lại) bất cứ lúc nào,
đồng thời thử nghiệm các luận điểm trái chiều mà không làm hỏng bản chính.

## Nguyên tắc chung
- **`main`** = bản nghiên cứu ổn định, đang dùng. Chỉ commit vào đây khi nội dung đã "chín".
- **Commit thường xuyên** = checkpoint. Mỗi lần cập nhật số liệu / thêm luận điểm → 1 commit.
- **Tag** = mốc quan trọng (vd: sau khi tải BCTC, sau khi chốt watchlist).
- **Branch** = khi thử một hướng nghiên cứu khác biệt (luận điểm trái chiều, kịch bản giá khác).

## 1. Khởi tạo (đã làm 1 lần)
```bash
git init
git add .
git commit -m "init: snapshot nghiên cứu ban đầu"
```

## 2. Làm việc hàng ngày
```bash
# Xem trạng thái
git status

# Lưu checkpoint sau mỗi thay đổi đáng kể
git add -A
git commit -m "update: bổ sung BCTC Q2 HVH, cập nhật biên LN"

# Đánh mốc (milestone)
git tag -a v1-bctc-q2 -m "Đã rà soát BCTC quý 2 các mã chính"
```

## 3. ROLLBACK — quay lại phiên bản cũ
```bash
# Xem lịch sử commit (để lấy mã hash)
git log --oneline

# Quay lại 1 commit trước (an toàn, giữ thay đổi trong working tree)
git reset --soft HEAD~1          # giữ file, bỏ commit
git reset --hard HEAD~1          # XÓA luôn thay đổi — cẩn thận

# Quay về 1 commit cụ thể bằng hash (vd abc123)
git checkout abc123 -- tong-hop/tong-hop.md   # chỉ rollback 1 file
git reset --hard abc123                        # rollback toàn bộ repo

# Quay về 1 tag đã đánh dấu
git checkout v1-bctc-q2
```

## 4. Thử nghiệm luận điểm trái chiều (branch)
```bash
# Tạo nhánh thử kịch bản "Vingroup suy giảm 2026"
git checkout -b thi-nghiem/vg-suy-giam

# ... sửa file, commit bình thường ...
git add -A && git commit -m "thử: kịch bản VG giảm tốc"

# Khi nào chốt được thì merge vào main
git checkout main
git merge thi-nghiem/vg-suy-giam

# Bỏ nhánh thử nghiệm không dùng nữa
git branch -d thi-nghiem/vg-suy-giam
```

## 5. Xem sự khác biệt giữa các phiên bản
```bash
git diff HEAD~3 HEAD -- tong-hop/tong-hop.md   # so 3 phiên bản trước với hiện tại
git diff v1-bctc-q2 HEAD                       # so với mốc tag
```

## Mẹo an toàn
- Trước khi `reset --hard` hoặc `checkout` sang commit cũ, luôn `git tag` hoặc `git branch backup-truoc-rollback` để không mất công sức.
- `git stash` để tạm cất thay đổi dở dang: `git stash` / `git stash pop`.

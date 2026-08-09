# CHI MUC SPEC — ban do 1 trang cho nguoi va AI

> Sinh tu dong boi `python tools/specctl.py index`. **Khong sua tay.**
> Cap nhat: 2026-08-09  |  REQ=10  COMP=13  TASK=0

Doc file nay truoc khi lam bat cu viec gi. Moi ID la vinh vien, khong tai su dung.

## Yeu cau (REQ) — can gi & vi sao

| ID | Tieu de | Trang thai | Uu tien | Mat phang | Component |
|---|---|---|---|---|---|
| `REQ-0001` | Nen tang chay tren Docker Desktop, toan bo open source cuc bo | done | 6.25 | both | - |
| `REQ-0002` | Tach giao dien thanh 2 nhom: Build plane va Ops plane | done | 8.33 | both | - |
| `REQ-0003` | Quan ly codebase tu dong voi GitHub theo chuoi spec REQ-COMP-TASK | done | 5.0 | build | - |
| `REQ-0004` | Model AI nho truy xuat duoc yeu cau cu de phat trien tiep | draft | 6.67 | build | - |
| `REQ-0005` | Thu thap tu dong du lieu kinh te vi mo va thi truong CK/BDS Viet Nam | draft | 4.0 | ops | - |
| `REQ-0006` | Co che ghi nhan tai lieu va chuyen doi sang dang LLM su dung hieu qua | draft | 5.33 | both | - |
| `REQ-0007` | Can luong lay du lieu: Gia co phieu VNM theo ngay | draft | 6.67 | ops | - |
| `REQ-0008` | Thu thap tu dong du lieu thi truong CK/BDS Viet Nam | draft | - | ops | COMP-0012, COMP-0013 |
| `REQ-0009` | AnalyticsEngine va RecommendEngine (dinh gia, scoring, gia muc tieu) | draft | - | build | COMP-0012 |
| `REQ-0010` | Co che ghi nhan tai lieu va chuyen doi sang dang LLM | draft | - | build | - |

## Thanh phan (COMP) — sua o dau

| ID | Ten | Loai | Trang thai | Chu | Duong dan chinh |
|---|---|---|---|---|---|
| `COMP-0001` | Docker Compose Stack | infra | done | ARCH | `docker-compose.yml`, `Dockerfile`, `Makefile` |
| `COMP-0002` | Worker & Scheduler | service | done | DE | `vnir/worker/` |
| `COMP-0003` | Connector Framework | library | done | DE | `vnir/connectors/` |
| `COMP-0004` | Source Registry | schema | done | QA | `vnir/registry/` |
| `COMP-0005` | UI Build Plane | ui | done | AIE | `vnir/ui_build/` |
| `COMP-0006` | UI Ops Plane | ui | done | DE | `vnir/ui_ops/` |
| `COMP-0007` | Spec System | library | done | ARCH | `tools/spec_lib.py`, `tools/specctl.py`, `tools/spec_validate.py` |
| `COMP-0008` | GitHub Automation | workflow | done | ARCH | `tools/ghsync.py`, `.github/` |
| `COMP-0009` | Context Builder | pipeline | planned | AIE | `vnir/context_build.py`, `context/` |
| `COMP-0010` | Data Quality | library | planned | QA | `vnir/quality/` |
| `COMP-0011` | API Service | service | done | ARCH | `vnir/api/` |
| `COMP-0012` | Data Quality & EvidenceLedger | service | planned | QA | `vnir/evidence/` |
| `COMP-0013` | Context Builder (raw -> curated) | service | planned | DE | `vnir/context_build.py` |

## Cong viec (TASK) — lam chinh xac gi

| ID | Tieu de | Trang thai | REQ | COMP | Model | Token |
|---|---|---|---|---|---|---|

## Cach dung cho AI agent

```bash
python tools/specctl.py next              # task nao nen lam tiep
python tools/specctl.py show TASK-0001    # goi thuc thi tu du
python tools/specctl.py validate          # bat buoc pass truoc khi commit
```

Commit phai co trailer:

```
Task-Id: TASK-xxxx
Req-Id: REQ-xxxx
```

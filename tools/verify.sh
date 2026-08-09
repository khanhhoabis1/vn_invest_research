#!/usr/bin/env bash
# Kiem chung toan bo nen tang — chay TRUOC MOI COMMIT.
#
# Vi sao co file nay: `hermes verify` tu doan sai (goi `pip` toan cuc trong khi may
# co PEP 668, va doan app o `main:app` trong khi that ra o `vnir.api.main:app`).
# File nay ghi dung lenh that cua du an.
#
#   bash tools/verify.sh          # day du
#   bash tools/verify.sh --nhanh  # bo qua Docker (nhanh hon nhieu)

set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
NHANH="${1:-}"
FAIL=0

buoc() { printf "\n\033[1m▶ %s\033[0m\n" "$1"; }
dat()  { printf "  \033[92m✓\033[0m %s\n" "$1"; }
hong() { printf "  \033[91m✗ %s\033[0m\n" "$1"; FAIL=1; }

[ -x "$PY" ] || { echo "Chua co .venv — chay: uv venv .venv --python 3.11"; exit 1; }

buoc "1/6  Bien dich toan bo ma nguon"
$PY -m compileall -q vnir tools tests && dat "moi file Python bien dich duoc" || hong "loi cu phap"

buoc "2/6  Lint (ruff — bat loi that, khong bat phong cach vun vat)"
$PY -m ruff check vnir/ tools/ tests/ && dat "khong con loi" || hong "ruff bao loi"

buoc "3/6  Kiem dinh spec + chi muc dong bo"
$PY tools/spec_validate.py && dat "moi spec hop le" || hong "spec khong hop le"
$PY tools/specctl.py index >/dev/null
git diff --quiet specs/SPEC-INDEX.md 2>/dev/null \
  && dat "SPEC-INDEX.md dong bo" \
  || hong "SPEC-INDEX.md lech — commit lai sau khi chay 'specctl.py index'"

buoc "4/6  Kiem thu hoi quy"
$PY -m pytest tests/ -q && dat "toan bo test pass" || hong "co test that bai"

buoc "5/6  Khong xung dot ten module chuan Python"
x=$(ls -d platform types json io code test string 2>/dev/null || true)
[ -z "$x" ] && dat "khong co thu muc trung ten stdlib" || hong "xung dot: $x"

if [ "$NHANH" = "--nhanh" ]; then
  printf "\n\033[93m(bo qua Docker theo yeu cau --nhanh)\033[0m\n"
else
  buoc "6/6  Docker stack song va tra du lieu that"
  if docker compose ps --status running --format '{{.Service}}' 2>/dev/null | grep -q api; then
    curl -fsS --max-time 10 http://localhost:8000/health >/dev/null \
      && dat "/health tra loi" || hong "/health khong tra loi"
    n=$(curl -fsS --max-time 10 http://localhost:8000/sources | $PY -c 'import json,sys; print(len(json.load(sys.stdin)))')
    [ "$n" -gt 0 ] && dat "nap duoc $n connector" || hong "khong nap duoc connector nao"
    for p in 8601:Build 8602:Ops; do
      curl -fsS -o /dev/null --max-time 10 "http://localhost:${p%%:*}" \
        && dat "UI ${p##*:} (:${p%%:*}) song" || hong "UI ${p##*:} khong truy cap duoc"
    done
  else
    printf "  \033[93m~\033[0m stack chua chay — bo qua (chay 'docker compose up -d' de kiem tra day du)\n"
  fi
fi

if [ $FAIL -eq 0 ]; then
  printf "\n\033[92m━━ TAT CA DAT — san sang commit ━━\033[0m\n"
else
  printf "\n\033[91m━━ CO BUOC THAT BAI — sua truoc khi commit ━━\033[0m\n"
fi
exit $FAIL

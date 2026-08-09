# Lenh chuan cua du an. Chay `make` de xem danh sach.
#
# Vi sao co file nay: cong cu tu dong doan sai lenh cua du an (goi `pip` toan cuc
# trong khi may co PEP 668, va doan app o `main:app` thay vi `vnir.api.main:app`).
# Makefile la noi duy nhat ghi lenh that.

PY := .venv/bin/python
PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help bootstrap build test lint start verify up down logs clean

help: ## Hien danh sach lenh
	@grep -hE '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*##' '{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Dung moi truong (venv + thu vien)
	uv venv .venv --python 3.11 --allow-existing
	uv pip install --python $(PY) -q -r requirements.txt pytest ruff

build: ## Bien dich + lint
	$(PY) -m compileall -q vnir tools tests
	$(PY) -m ruff check vnir/ tools/ tests/

test: ## Kiem thu hoi quy + kiem dinh spec
	$(PY) -m pytest tests/ -q
	$(PY) tools/spec_validate.py

lint: ## Chi lint
	$(PY) -m ruff check vnir/ tools/ tests/

start: ## Chay API tu ma nguon (khong qua Docker)
	$(PY) -m uvicorn vnir.api.main:app --host 127.0.0.1 --port $(PORT)

verify: ## Kiem chung day du truoc khi commit
	bash tools/verify.sh

up: ## Dung toan bo stack bang Docker
	docker compose up -d

down: ## Dung stack
	docker compose down

logs: ## Xem log worker
	docker compose logs -f worker

clean: ## Xoa file tam
	find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache

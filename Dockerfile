# VN Invest Research Platform — image dung chung cho api / worker / 2 UI
# Base: python slim (arm64 native tren Apple Silicon)

FROM python:3.11-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Ho_Chi_Minh

# Chi cai thu that su can (giu image nho)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates tzdata git \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------- deps
FROM base AS deps
WORKDIR /tmp/build
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------------------------------------------------------------- runtime
FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Nguoi dung khong phai root
RUN useradd -m -u 1000 vnir
WORKDIR /workspace

# Code duoc bind-mount luc chay (docker compose), copy vao day de image tu chay duoc doc lap
COPY --chown=vnir:vnir . /workspace

RUN mkdir -p /workspace/data/bronze /workspace/data/silver /workspace/data/gold \
             /workspace/context /workspace/intake/inbox /workspace/logs \
    && chown -R vnir:vnir /workspace

USER vnir
ENV PYTHONPATH=/workspace

EXPOSE 8000 8601 8602
CMD ["python", "-c", "print('Chi dinh command trong docker-compose.yml')"]

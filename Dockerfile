# 阶段一: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 阶段二: Runner
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

# 把阶段一的虚拟环境复制到阶段二
COPY --from=builder --chown=appuser:appgroup /app/venv /app/venv

COPY --chown=appuser:appgroup ./app /app/app

USER appuser

EXPOSE 8000

CMD ["python", "app/main.py"]

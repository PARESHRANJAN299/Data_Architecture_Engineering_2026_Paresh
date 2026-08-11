FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt \
    && useradd --create-home --uid 10001 adapter \
    && mkdir --parents /app/output \
    && chown --recursive adapter:adapter /app

COPY --chown=adapter:adapter src ./src

USER adapter

CMD ["python", "-m", "coinbase_adapter.main", "--output", "/app/output/market_trades.jsonl"]

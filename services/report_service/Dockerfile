FROM python:3.11-slim

WORKDIR /app

COPY common /app/common
COPY services/report_service /app/service

RUN apt-get update && apt-get install -y --no-install-recommends libfreetype6 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r /app/service/requirements.txt

ENV PYTHONPATH=/app
WORKDIR /app/service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]







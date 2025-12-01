FROM python:3.11-slim

WORKDIR /app

COPY common /app/common
COPY services/provider_service /app/service

RUN pip install --no-cache-dir -r /app/service/requirements.txt

ENV PYTHONPATH=/app
WORKDIR /app/service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]







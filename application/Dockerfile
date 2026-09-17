FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY pyproject.toml .

EXPOSE 8081

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]

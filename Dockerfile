FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=demo \
    DEBUG=true

WORKDIR /app

# Test defect for primary scan: additional OS packages increase the attack surface
# and give Trivy more package metadata to analyze.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        openssh-client \
    && python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# Test defect for primary scan: container runs as root by default.
USER root

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

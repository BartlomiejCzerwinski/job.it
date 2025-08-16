    
FROM python:3.12

LABEL maintainer="Job.it"
LABEL description="Job.it - Jobboard platform with AI features"
LABEL version="1.0"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=jobit.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . .
RUN mkdir -p /app/staticfiles /app/media

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]

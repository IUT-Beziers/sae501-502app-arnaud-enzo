FROM python:3.13.2-slim AS builder

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13.2-slim

# Install runtime dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
ENV PATH="/usr/local/bin:${PATH}"
WORKDIR /app
COPY --chown=appuser:appuser . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create cron job for scheduled tasks every 10 minutes
RUN echo "*/10 * * * * /usr/local/bin/python /app/manage.py processpackets >> /var/log/cron.log 2>&1" > /etc/cron.d/cronjob

USER appuser
EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py makemigrations API && python manage.py migrate && python manage.py createadminuser && gunicorn --bind 0.0.0.0:8000 -k gevent App.wsgi:application"]
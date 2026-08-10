# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# SQL Server driver required by pyodbc and SQLAlchemy's mssql+pyodbc dialect.
RUN apt-get update \
     && apt-get install --no-install-recommends -y ca-certificates curl unixodbc unixodbc-dev \
     && curl -fsSL -o /tmp/packages-microsoft-prod.deb \
         https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
     && dpkg -i /tmp/packages-microsoft-prod.deb \
     && rm /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install --no-install-recommends -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /data/rag-uploads \
    && chown -R appuser:appuser /app /data
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "180", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]

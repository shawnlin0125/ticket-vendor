FROM python:3.12-alpine

WORKDIR /app

# Install system deps
RUN apk add --no-cache gcc musl-dev

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir pip setuptools wheel && \
    pip install --no-cache-dir git+https://github.com/shawnlin0125/plugin-hub.git#subdirectory=platform-plugin-sdk && \
    pip install --no-cache-dir -e /app/unified-ticket-api

# Copy proxy + plugins
COPY proxy/ proxy/
COPY plugins/ plugins/
COPY unified-ticket-api/ unified-ticket-api/

# Install proxy deps + unified-ticket-api
RUN pip install --no-cache-dir fastapi uvicorn aiohttp apscheduler && \
    pip install --no-cache-dir /app/unified-ticket-api

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "proxy.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Vedic Astro — production image for Northflank (free Sandbox).
# Mirrors render.yaml: Python 3.12, uvicorn on $PORT, health check /health.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# System libraries for WeasyPrint (Pango/HarfBuzz) + fontconfig for the
# bundled Devanagari fonts used in PDF reports. No build tools needed:
# pyswisseph, uharfbuzz and the rest ship manylinux wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        fontconfig \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Northflank injects PORT at runtime; the default (8080) is for local runs.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]

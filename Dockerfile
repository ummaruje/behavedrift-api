FROM python:3.11-slim

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Install Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application ----
COPY . .

# ---- Non-root user for security ----
RUN addgroup --system behavedrift && adduser --system --ingroup behavedrift behavedrift
USER behavedrift

# ---- Expose port ----
EXPOSE 8000

# ---- Entrypoint ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

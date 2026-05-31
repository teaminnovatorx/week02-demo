# UDARA AI — Week 02 Demo
# Single container: FastAPI + static frontend
FROM python:3.11-slim

WORKDIR /app

# Install deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create data directory for SQLite
RUN mkdir -p /data

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:////data/udara.db
ENV STATIC_DIR=/app/frontend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

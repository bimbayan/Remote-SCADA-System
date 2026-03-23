FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create dirs and fix permissions
RUN mkdir -p /app/data/live /app/data/logs && \
    chmod +x /app/run.sh

# Railway dynamically assigns $PORT — default 8501 if not set
ENV PORT=8501

# Expose port (Railway will override via $PORT env var)
EXPOSE 8501

# run.sh: starts simulator in background, then starts Streamlit on $PORT
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/bin/bash", "-c", "python src/simulator.py & sleep 8 && streamlit run src/app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]

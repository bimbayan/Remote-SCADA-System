FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create dirs and fix permissions
RUN mkdir -p /app/data/live /app/data/logs && \
    chmod -R 777 /app/data && \
    chmod +x /app/run.sh

# Railway dynamically assigns $PORT — default 8501 if not set
ENV PORT=8501
ENV PYTHONUNBUFFERED=1

# Expose port (Railway will override via $PORT env var)
EXPOSE 8501

# Entrypoint script will start the simulator and the streamlit app
ENTRYPOINT ["/app/run.sh"]

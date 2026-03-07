FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos '' scada_user && \
    mkdir -p /app/data && \
    chown -R scada_user:scada_user /app

USER scada_user

# Expose Streamlit default port
EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

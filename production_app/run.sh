#!/bin/bash

# Start the simulator in the background
echo "Starting SCADA Simulator Thread..."
python src/simulator.py &

# Wait a moment for the DB to be created
sleep 2

# Start the Streamlit application
echo "Starting SCADA Streamlit UI..."
streamlit run src/app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.enableWebsocketCompression=false

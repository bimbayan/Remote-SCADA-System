#!/bin/bash
# deploy.sh
# Run this script on a fresh VPS (Ubuntu 22.04 LTS recommended) to deploy the SCADA system.

echo ">>> Setting up Remote SCADA System Deployment..."

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo ">>> Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

# Ensure docker compose plugin is installed
if ! docker compose version &> /dev/null; then
    echo ">>> Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Set up .env if it doesn't exist
if [ ! -f .env ]; then
    echo ">>> Creating .env file..."
    echo "ADMIN_PASSWORD_HASH='\$2b\$12\$wMve7Ow3/Lf99w.wDrfdmewxzBj87SjE8OTSv6PwEc4oFQ23KpPdq'" > .env
    echo "COOKIE_KEY='scada_secure_signature_production_$(date +%s)'" >> .env
    echo ">>> Note: Please update ADMIN_PASSWORD_HASH in .env for real deployments using bcrypt!"
fi

echo ">>> Building and starting Docker containers..."
sudo docker compose up -d --build

echo ">>> Deployment successful! The containers are running in the background."
echo ">>> View logs with 'sudo docker compose logs -f'"

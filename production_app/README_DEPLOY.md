# MVP Production Deployment Guide

This repository contains everything you need to run the Remote SCADA application on a production server (VPS) with a custom domain name and automatic HTTPS. We use **Docker Compose** to containerize the app, and **Caddy** to route incoming traffic securely.

## 1. Setup Your VPS
Buy a standard compute VPS from a provider (e.g., DigitalOcean, AWS EC2, or Hetzner). We recommend **Ubuntu 22.04 LTS**.

## 2. Buy and Point Your Domain
1. In your domain registrar (Namecheap, GoDaddy, Route53, etc.), create an `A` Record.
2. Point the `@` (and/or `www`) record to the **Public IPv4 Address** of your VPS.

## 3. Clone This Code to Your VPS
SSH into your server:
```bash
ssh root@your_server_ip
```
Clone your repository:
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo/production_app
```

## 4. Configure Caddy for SSL
Open the `Caddyfile` and replace the placeholder `:80` configuration with your newly purchased domain.

```caddyfile
# Change this file to:

your-domain.com {
    reverse_proxy dashboard:8501
}
```

## 5. First Time Deployment
Make the deployment script executable, and run it:
```bash
chmod +x deploy.sh
./deploy.sh
```

### What does `deploy.sh` do?
1. Installs Docker and Docker Compose automatically if they are missing.
2. Generates a `.env` file with placeholder API keys and hashes so your app doesn't crash on secrets.
3. Builds the Docker images and starts the `caddy`, `simulator`, and `dashboard` containers in the background.

## 6. Security (Changing the Password)
By default, the `.env` file is generated with a default encrypted password for `admin` (the password is `password`).
To secure your MVP, you should change this hash to a secure password.

In Python, create a new bcrypt hash:
```python
import streamlit_authenticator as stauth
hashed_password = stauth.Hasher(['YourSuperSecretPassword']).generate()[0]
print(hashed_password)
```
Then, update the `.env` file on your server:
```env
ADMIN_PASSWORD_HASH='<YOUR_NEW_HASH>'
```
Restart the application:
```bash
sudo docker compose restart dashboard
```

## Troubleshooting
View the application logs to see what's going wrong:
```bash
sudo docker compose logs -f
```

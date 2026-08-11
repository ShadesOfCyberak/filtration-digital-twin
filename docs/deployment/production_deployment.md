# Production Deployment Guide (Docker & AWS EC2 Scaffold)

## AWS EC2 / Linux Deployment Steps:

1. **Provision EC2 Instance**:
   - Ubuntu 22.04 LTS (t3.medium recommended)
   - Security Group Inbound Rules:
     - TCP 80 / 443 (HTTP/HTTPS)
     - TCP 8000 (Backend FastAPI)
     - TCP 1883 (MQTT Broker)

2. **Install Docker & Docker Compose**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   sudo systemctl enable --now docker
   ```

3. **Deploy Application Stack**:
   ```bash
   git clone https://github.com/your-org/filtration-digital-twin.git
   cd filtration-digital-twin
   cp .env.docker.example .env
   # Update passwords and JWT secret key in .env
   docker-compose -f docker-compose.yml up -d --build
   ```

4. **Verify Deployment**:
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

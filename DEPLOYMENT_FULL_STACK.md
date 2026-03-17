# Full Stack Deployment Guide - Flask Backend + React Frontend

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│                   (Vite + Tailwind)                          │
│                   Port: 3000 (dev)                           │
│                   Port: 5173 (prod)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
                    API Requests
                   (axios/fetch)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Flask API Backend                           │
│           Port: 5000 (dev/prod)                             │
│        Endpoints: /api/health, /api/process-*              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
              ┌──────────┴──────────┐
              │                     │
         ML Model           Document Parser
      (ensemble_phase3)      (PyPDF, CSV)
```

---

## 🚀 QUICK START (Local Development)

### Terminal 1: Run Flask Backend API

```bash
cd c:\Fintech
python api.py
```

**Output:**
```
 * Running on http://127.0.0.1:5000
 * WARNING: This is a development server. Do not use it in production.
```

### Terminal 2: Run React Frontend Development Server

```bash
cd c:\Fintech\frontend
npm install          # First time only
npm run dev
```

**Output:**
```
  VITE v5.0.0  ready in 123 ms
  ➜  Local:   http://localhost:5173/
```

### Access Application

**Frontend:** http://localhost:5173/  
**API Health:** http://localhost:5000/api/health

---

## 🏗️ PRODUCTION DEPLOYMENT

### Option A: Docker Compose (Recommended - Easiest)

**Step 1: Create `docker-compose.yml`**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - API_PORT=5000
    volumes:
      - ./uploads:/app/uploads
      - ./credit_engine/data:/app/credit_engine/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:3000"
    environment:
      - VITE_API_URL=http://localhost:5000
    depends_on:
      - backend
    restart: unless-stopped
```

**Step 2: Create Backend Dockerfile**

```dockerfile
# Dockerfile.backend
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY credit_engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

ENV FLASK_APP=api.py
ENV FLASK_ENV=production

CMD ["python", "api.py"]
```

**Step 3: Create Frontend Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build
COPY . .
RUN npm run build

# Production server
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
```

**Step 4: Deploy with Docker Compose**

```bash
cd c:\Fintech

# Build and start both services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### Option B: Separate Cloud Deployments

#### **Backend on Azure App Service**

```bash
# 1. Create resource group
az group create --name credit-engine-rg --location eastus

# 2. Create App Service Plan
az appservice plan create --name credit-engine-plan --resource-group credit-engine-rg --sku B1 --is-linux

# 3. Create Web App
az webapp create --resource-group credit-engine-rg --plan credit-engine-plan --name credit-engine-api --runtime "PYTHON|3.9"

# 4. Configure deployment
az webapp deployment source config-zip --resource-group credit-engine-rg --name credit-engine-api --src deployment.zip

# 5. Set environment variables
az webapp config appsettings set --resource-group credit-engine-rg --name credit-engine-api \
  --settings FLASK_ENV=production API_PORT=5000
```

#### **Frontend on Azure Static Web Apps**

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Deploy to Static Web Apps
az staticwebapp create \
  --name credit-engine-frontend \
  --resource-group credit-engine-rg \
  --source . \
  --location westus2 \
  --branch main \
  --app-location "frontend/dist"
```

#### **Configure CORS and API URL**

Create `.env.production` in frontend:

```env
VITE_API_URL=https://credit-engine-api.azurewebsites.net
```

---

### Option C: AWS Deployment (EC2 + S3)

#### **Backend on EC2**

```bash
# SSH into EC2 instance
ssh -i key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip nginx
cd /app
pip install -r credit_engine/requirements.txt

# Configure Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/default > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Start Flask with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Start Nginx
sudo systemctl start nginx
```

#### **Frontend on S3 + CloudFront**

```bash
# Build frontend
cd frontend
npm run build

# Upload to S3
aws s3 cp dist/ s3://credit-engine-frontend --recursive

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name credit-engine-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

---

## 🔧 Environment Configuration

### Backend (.env)

```env
FLASK_ENV=production
API_PORT=5000
API_HOST=0.0.0.0
DEBUG=False
LOG_LEVEL=INFO
UPLOAD_MAX_MB=16
```

### Frontend (.env.production)

```env
VITE_API_URL=https://api.yourdomain.com
VITE_API_TIMEOUT=30000
VITE_LOG_LEVEL=info
```

---

## 📊 Testing Deployment

### Backend Health Check

```bash
curl -X GET http://localhost:5000/api/health

# Expected response:
# {"status": "healthy", "message": "Credit Engine API is running"}
```

### Frontend Load Test

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:3000/

# Using k6
k6 run load-test.js
```

### End-to-End Test

```bash
curl -X POST http://localhost:5000/api/process-application \
  -F "applicant_name=Test User" \
  -F "revenue=50000" \
  -F "net_profit=5000"
```

---

## 🚨 Production Checklist

### Backend
- [ ] Set `FLASK_ENV=production`
- [ ] Disable debug mode
- [ ] Use Gunicorn/uWSGI instead of development server
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up SSL/TLS certificate
- [ ] Configure CORS properly for frontend domain
- [ ] Set up logging and monitoring
- [ ] Configure database backups

### Frontend
- [ ] Build optimized production bundle (`npm run build`)
- [ ] Set correct API endpoint in `.env.production`
- [ ] Enable GZIP compression
- [ ] Configure caching headers
- [ ] Set up CDN (CloudFront, Cloudflare)
- [ ] Configure security headers
- [ ] Set up monitoring and error tracking

---

## 📈 Scaling Considerations

### Horizontal Scaling (Multiple Instances)

```yaml
# docker-compose.yml with load balancing
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend1
      - backend2

  backend1:
    build: .
    environment:
      - INSTANCE=1

  backend2:
    build: .
    environment:
      - INSTANCE=2

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

### Database/Cache Layer

```bash
# Add Redis for caching
docker run -d --name redis -p 6379:6379 redis:alpine

# Add PostgreSQL for data persistence
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
```

---

## 🔒 Security Best Practices

1. **HTTPS/SSL:**
   ```bash
   # Generate self-signed certificate
   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
   ```

2. **API Authentication:**
   ```python
   # Add to api.py
   from flask_httpauth import HTTPBearerAuth
   auth = HTTPBearerAuth()
   
   @auth.verify_token
   def verify_token(token):
       return validate_api_token(token)
   
   @app.route('/api/process-application', methods=['POST'])
   @auth.login_required
   def process_application():
       ...
   ```

3. **Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   
   @app.route('/api/process-application', methods=['POST'])
   @limiter.limit("10 per minute")
   def process_application():
       ...
   ```

---

## 📊 Monitoring & Logs

### Backend Logging

```python
# In api.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
```

### Frontend Error Tracking

```typescript
// In frontend
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "https://your-sentry-url",
  environment: "production",
});
```

---

## 🚀 Recommended Production Setup

```
┌─────────────────────────────────────────────────────────┐
│                   Cloudflare/CDN                        │
│                    (caching)                            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Load Balancer (ALB/NLB)                    │
│              SSL/TLS Termination                        │
└────────────────────────┬────────────────────────────────┘
        ┌───────────────┼───────────────┐
        │               │               │
    ┌───▼──┐       ┌───▼──┐       ┌───▼──┐
    │API-1 │       │API-2 │       │API-3 │  (Auto-scaling)
    └──────┘       └──────┘       └──────┘
        │               │               │
    ┌───▼─────────────────────────────▼┐
    │        PostgreSQL Database        │
    │      (with replication)           │
    └──────────────────────────────────┘
        │
    ┌───▼──────────────┐
    │  Redis Cache     │
    └──────────────────┘
```

---

## ✅ Quick Reference Commands

### Local Development
```bash
# Backend
python api.py

# Frontend
cd frontend && npm run dev
```

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down
```

### Testing
```bash
# API health
curl http://localhost:5000/api/health

# Frontend
open http://localhost:3000/
```

---

**Start with Docker Compose for easiest production deployment!**

Next Steps:
1. Run locally first (`npm run dev` + `python api.py`)
2. Test the integration
3. Build Docker images (`docker-compose up`)
4. Deploy to cloud platform of choice

Which deployment method would you prefer?

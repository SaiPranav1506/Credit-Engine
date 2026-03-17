# 🚀 Full Stack Deployment Guide

## Quick Start (Choose One)

### Option 1: Development (Local Testing)
```bash
# Windows
.\deploy.ps1 -Mode dev

# Linux/Mac
bash deploy.sh dev
```

### Option 2: Docker (Production Ready)
```bash
# Windows
.\deploy.ps1 -Mode docker

# Linux/Mac
bash deploy.sh docker
```

### Option 3: Manual Setup
```bash
# Terminal 1: Backend API
python api.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## 📁 Project Structure

```
Fintech/
├── api.py                          # Flask backend
├── frontend/                        # React + Vite
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile                 # Frontend container
│   ├── package.json
│   └── vite.config.ts
├── credit_engine/                 # ML engine
│   ├── model_loader.py           # Load production models
│   ├── deployment_config.py       # Config management
│   ├── data/
│   │   ├── ensemble_phase3_optimized.pkl  # Production model
│   │   └── phase3_threshold.npy
│   └── requirements.txt
├── docker-compose.yml             # Full-stack deployment
├── Dockerfile.backend             # Backend container
├── deploy.ps1                      # Windows deployment script
├── deploy.sh                       # Linux/Mac deployment script
└── DEPLOYMENT_FULL_STACK.md       # Detailed deployment guide
```

---

## 🔧 Configuration

### Backend (.env or environment variables)
```bash
FLASK_ENV=production
API_PORT=5000
API_HOST=0.0.0.0
DEBUG=False
```

### Frontend (.env.local)
```bash
VITE_API_URL=http://localhost:5000
VITE_API_TIMEOUT=30000
```

---

## ✅ Pre-Deployment Checklist

- [x] Model file: `ensemble_phase3_optimized.pkl` (16.2 MB)
- [x] Threshold file: `phase3_threshold.npy`
- [x] Requirements updated with Flask + Gunicorn
- [x] Docker files created
- [x] Docker Compose configured
- [x] Deployment scripts ready
- [ ] Test locally first
- [ ] Configure for your cloud platform

---

## 🧪 Testing

### Test Health Endpoint
```bash
curl http://localhost:5000/api/health

# Expected response:
# {"status": "healthy", "message": "Credit Engine API is running"}
```

### Test Full Application
```bash
# Windows
.\deploy.ps1 -Mode test

# Linux/Mac
bash deploy.sh test
```

---

## 📊 What's Running

### Backend API (Port 5000)
- **Health Check**: `GET /api/health`
- **Process Application**: `POST /api/process-application`
- **File Uploads**: Max 16MB (PDF, CSV)
- **Model**: Ensemble classifier (77.98% accuracy)

### Frontend (Port 3000/5173)
- **React 18** with TypeScript
- **Vite** for fast builds
- **Tailwind CSS** for styling
- **Charts** with Recharts
- **Icons** with Lucide React

---

## 🐳 Docker Commands Reference

```bash
# Build images
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop containers
docker-compose down

# Remove images
docker-compose down -v

# Restart services
docker-compose restart

# SSH into running container
docker exec -it fintech_backend_1 /bin/bash
```

---

## 🌐 Cloud Deployment

### Azure
```bash
az webapp up --name credit-engine-api --runtime "PYTHON:3.9"
```

### AWS
```bash
# EC2 with backend
# S3 + CloudFront for frontend
aws s3 cp frontend/dist s3://credit-engine-frontend --recursive
```

### Google Cloud
```bash
gcloud run deploy credit-engine \
  --source . \
  --platform managed \
  --region us-central1
```

### Heroku
```bash
heroku create credit-engine-app
git push heroku main
```

---

## 🚨 Troubleshooting

### Backend Port Already in Use
```bash
# Windows - Find process on port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Frontend Not Connecting to API
```bash
# Check .env.local
cat frontend/.env.local

# Should have:
VITE_API_URL=http://localhost:5000
```

### Docker Issues
```bash
# Clean up all containers
docker-compose down -v

# Rebuild
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

### Model Loading Issues
```bash
# Test model loader
python -c "from credit_engine.model_loader import load_production_model; loader = load_production_model(); print('Model loaded:', loader.get_model_info())"
```

---

## 📈 Scaling

### For Production Deployments

1. **Add Load Balancer** (AWS ALB / Azure LB)
2. **Multiple Backend Instances** (Auto-scaling)
3. **Redis Cache** (for session/model caching)
4. **PostgreSQL** (for data persistence)
5. **CDN** (Cloudflare/CloudFront for frontend)

### Docker Compose Production Example
```yaml
services:
  backend1:
    build: .
  backend2:
    build: .
  nginx:
    image: nginx:alpine
    # Load balance between backend1, backend2
```

---

## 🔒 Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Set strong API credentials
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up API authentication
- [ ] Use environment variables for secrets
- [ ] Enable GZIP compression
- [ ] Set security headers

---

## 📊 Performance Monitoring

### Key Metrics
- API Response Time: < 100ms target
- Frontend Load Time: < 2s target
- Model Prediction Latency: < 500ms target
- Uptime: 99.9%+

### Tools
- **Backend**: Flask logging, Prometheus
- **Frontend**: Sentry, Google Analytics
- **Infrastructure**: CloudWatch, Datadog

---

## 📝 Next Steps

1. **Test Locally** 
   ```bash
   .\deploy.ps1 -Mode dev
   ```

2. **Build Docker Images**
   ```bash
   .\deploy.ps1 -Mode docker
   ```

3. **Push to Docker Registry** (optional)
   ```bash
   docker tag credit-engine:latest myregistry/credit-engine:latest
   docker push myregistry/credit-engine:latest
   ```

4. **Deploy to Cloud**
   - Choose your platform (Azure, AWS, GCP, etc.)
   - Follow cloud-specific deployment steps
   - Configure DNS and SSL

5. **Monitor & Scale**
   - Set up monitoring dashboards
   - Configure auto-scaling if needed
   - Enable error tracking

---

## 🆘 Support

For deployment issues:
1. Check [DEPLOYMENT_FULL_STACK.md](DEPLOYMENT_FULL_STACK.md) for detailed guide
2. Review [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md) for model info
3. Check Docker logs: `docker-compose logs -f`
4. Test API: `curl http://localhost:5000/api/health`
5. Check frontend console for errors

---

## 📞 Quick Links

- **API Docs**: [See api.py](api.py)
- **Model Info**: [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)
- **Full Guide**: [DEPLOYMENT_FULL_STACK.md](DEPLOYMENT_FULL_STACK.md)
- **Model Loader**: [credit_engine/model_loader.py](credit_engine/model_loader.py)
- **Frontend**: [frontend/src/App.tsx](frontend/src/App.tsx)

---

**Status**: ✅ Ready for Deployment

**Model Accuracy**: 77.98%  
**Backend**: Flask + Gunicorn  
**Frontend**: React + Vite  
**Containers**: Docker + Docker Compose  
**Deployment**: Multi-cloud ready (Azure, AWS, GCP)

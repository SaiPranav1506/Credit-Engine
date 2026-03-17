# Vercel + Render Deployment Guide

## 🚀 Architecture

```
┌──────────────────────────┐
│   React Frontend         │
│   (Vercel)               │
│   vercel.app/credit-*    │
└────────────┬─────────────┘
             │ API Requests
             ↓
┌──────────────────────────┐
│   Flask Backend          │
│   (Render)               │
│   *.onrender.com         │
│   (Python 3.9 + Gunicorn)│
└──────────────────────────┘
```

---

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Connect your GitHub repository

### Step 2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Select your GitHub repository: `Credit-Engine`
3. Fill in the configuration:

| Setting | Value |
|---------|-------|
| Name | `credit-engine-backend` |
| Environment | `Python 3` |
| Region | `Oregon` (or your choice) |
| Branch | `main` |
| Build Command | `pip install -r credit_engine/requirements.txt` |
| Start Command | `gunicorn -w 4 -b 0.0.0.0:$PORT api:app` |

### Step 3: Configure Environment Variables

Go to **Settings** → **Environment** and add:

```
FLASK_ENV=production
FLASK_DEBUG=0
DEBUG=False
PYTHONUNBUFFERED=1
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render automatically deploys when you push to `main`
3. Wait for deployment to complete
4. Note your backend URL: `https://credit-engine-backend.onrender.com`

### Step 5: Test Backend

```bash
curl https://credit-engine-backend.onrender.com/api/health

# Should return:
# {"status": "healthy", "message": "Credit Engine API is running"}
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub
3. Connect your GitHub repository

### Step 2: Create New Project

1. Click **"Add New"** → **"Project"**
2. Select your GitHub repository: `Credit-Engine`
3. Import the project

### Step 3: Configure Build Settings

**Important**: Set the root directory to `frontend`

| Setting | Value |
|---------|-------|
| Framework | `Vite` (auto-detected) |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

### Step 4: Add Environment Variables

Go to **Settings** → **Environment Variables** and add:

**For Production** (vercel.com domain):
```
VITE_API_URL=https://credit-engine-backend.onrender.com
VITE_LOG_LEVEL=info
VITE_ENABLE_ANALYTICS=true
```

**For Preview** (PR previews):
```
VITE_API_URL=https://credit-engine-backend.onrender.com
VITE_LOG_LEVEL=debug
VITE_ENABLE_ANALYTICS=false
```

### Step 5: Deploy

1. Click **"Deploy"**
2. Vercel automatically builds and deploys
3. Wait for deployment to complete
4. Your frontend URL: `https://credit-engine.vercel.app` (or custom domain)

### Step 6: Test Frontend

1. Open your Vercel URL
2. Fill in test data
3. Submit form
4. Should see results from Render backend

---

## ✅ Post-Deployment Verification

### Test 1: Backend is Running
```bash
curl https://credit-engine-backend.onrender.com/api/health
```
Expected: `{"status": "healthy", ...}`

### Test 2: Frontend Loads
Open: https://credit-engine.vercel.app/

### Test 3: Frontend Connects to Backend
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Fill form and submit
4. Should see request to `credit-engine-backend.onrender.com`
5. Response should have `decision: "APPROVE"` or `"REJECT"`

### Test 4: Full End-to-End
1. Go to frontend
2. Enter applicant details:
   - Name: "Test User"
   - Revenue: 50000
   - Net Profit: 5000
   - Debt-to-Equity: 0.5
   - Fraud Score: 0.2
   - Avg Balance: 10000
3. Click "Analyze"
4. Should see decision and confidence score

---

## 🔧 Configuration Files Reference

### Frontend (Vercel)

**vercel.json** - Already created:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [{"source": "/(.*)", "destination": "/index.html"}],
  "env": {"VITE_API_URL": "@vite_api_url"}
}
```

**.env.production** - Already created:
```
VITE_API_URL=https://credit-engine-backend.onrender.com
VITE_LOG_LEVEL=info
```

### Backend (Render)

**render.yaml** - Already created:
```yaml
services:
  - type: web
    name: credit-engine-backend
    env: python
    pythonVersion: 3.9
    buildCommand: pip install -r credit_engine/requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT api:app
```

---

## 🚨 Common Issues & Solutions

### Issue: Frontend can't connect to backend

**Solution**: Check environment variable
```bash
# Check in Vercel project settings:
# Settings > Environment Variables > VITE_API_URL

# Should be: https://credit-engine-backend.onrender.com
# (without trailing slash)
```

### Issue: CORS errors in console

**Solution**: Backend CORS is already configured in `api.py`
```python
CORS(app)  # Allows all origins
```

If you see CORS errors, the backend isn't responding. Check:
1. Render deployment status
2. `curl https://credit-engine-backend.onrender.com/api/health`

### Issue: Render backend not found after deployment

**Solution**: 
1. Go to Render.com dashboard
2. Check deployment logs
3. Look for errors in "Deploy" tab

Common errors:
- Missing dependencies: Check `credit_engine/requirements.txt`
- Model file missing: Ensure `ensemble_phase3_optimized.pkl` exists
- Python version: Should be 3.9

### Issue: Frontend shows "loading forever"

**Solution**:
1. Open DevTools (F12)
2. Check **Console** for errors
3. Check **Network** tab for API calls
4. Common causes:
   - API URL is wrong (check `.env.production`)
   - Backend is sleeping (Render free tier sleeps after 15 min inactivity)
   - Backend crashed (check Render logs)

### Issue: Render backend spins down

**Note**: Render free tier spins down after 15 minutes of inactivity
- First request takes 30+ seconds (spin-up time)
- Subsequent requests are fast
- **Solution**: Upgrade to paid plan, or accept spin-down behavior

---

## 🔄 Update Workflow

### When you push changes to GitHub:

**Backend changes** (automatically deployed by Render):
1. Push to `main` branch
2. Render detects change
3. Pulls latest code
4. Runs build command: `pip install -r credit_engine/requirements.txt`
5. Restarts with latest model

**Frontend changes** (automatically deployed by Vercel):
1. Push to `main` branch
2. Vercel detects change
3. Deploys to preview URL first
4. Tests
5. Auto-deploys to production

---

## 📊 Monitoring Deployments

### Render Dashboard
- Go to https://dashboard.render.com
- Click your service
- View **Logs** tab for error messages
- Monitor **CPU/Memory** usage

### Vercel Dashboard
- Go to https://vercel.com/dashboard
- Click your project
- View **Deployments** for history
- Click deployment to see logs

---

## 🎯 Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Vercel Project → Settings → Domains
2. Add your domain
3. Update DNS records (Vercel shows instructions)
4. SSL automatically configured

### Add Custom Domain to Render

1. Render Service → Settings → Custom Domain
2. Add your domain
3. Update DNS records
4. SSL automatically configured

---

## 📈 Performance Tips

### Render (Backend)
- Model inference: ~200-300ms per request
- Cached predictions speed up repeated requests
- Database queries add ~50-100ms

### Vercel (Frontend)
- Builds with Vite: ~30 seconds
- Bundle size: ~300KB (gzipped)
- CDN distributed globally for <100ms response

---

## 💰 Cost Breakdown

### Vercel (Frontend)
- **Free tier**: Unlimited deployments, auto-scaling
- **Pro**: $20/month for team collaboration
- This project: Free tier sufficient

### Render (Backend)
- **Free tier**: 750 free hours/month (1 instance), spins down after 15 min
- **Starter**: $7/month per instance (always running)
- **Standard**: $12/month per instance (more resources)

**Recommendation for Production**: Upgrade Render to Starter ($7/month) for always-on backend

---

## 🔐 Security Checklist

- [x] CORS configured
- [x] FLASK_ENV=production
- [x] DEBUG=False
- [ ] Add rate limiting (if needed)
- [ ] Add API authentication (if needed)
- [ ] Use custom domain with HTTPS (auto by Vercel/Render)
- [ ] Monitor error logs regularly
- [ ] Set up alerts for failures

---

## 📞 Support & Troubleshooting

### Render Support
- Dashboard: https://dashboard.render.com/support
- Docs: https://render.com/docs
- Status: https://status.render.com/

### Vercel Support
- Dashboard: https://vercel.com/support
- Docs: https://vercel.com/docs
- Status: https://www.vercelstatus.com/

### Credit Engine Specific
- GitHub Issues: https://github.com/SaiPranav1506/Credit-Engine/issues
- Model Info: [DEPLOYMENT_READY.md](../DEPLOYMENT_READY.md)
- API Docs: [API_DOCUMENTATION.md](../API_DOCUMENTATION.md)

---

## ✅ Deployment Checklist

### Before Deploying

- [x] Code committed to GitHub (`main` branch)
- [x] Model file exists: `ensemble_phase3_optimized.pkl`
- [x] Requirements updated: `credit_engine/requirements.txt`
- [x] Frontend `.env.production` configured
- [x] Render.yaml created
- [x] Vercel.json created

### Render Deployment

- [ ] Create Render account
- [ ] Create Web Service
- [ ] Configure build command
- [ ] Set environment variables
- [ ] Deploy
- [ ] Test API health endpoint
- [ ] Note backend URL

### Vercel Deployment

- [ ] Create Vercel account
- [ ] Create project from GitHub
- [ ] Set root directory to `frontend`
- [ ] Set `VITE_API_URL` environment variable
- [ ] Deploy
- [ ] Test frontend loads
- [ ] Test API connection

### Post-Deployment

- [ ] Test health endpoint
- [ ] Fill and submit form
- [ ] Verify decision appears
- [ ] Check browser console for errors
- [ ] Monitor Render/Vercel dashboards

---

## 🚀 Quick Deploy Commands

```bash
# 1. Ensure everything is committed
git add .
git commit -m "Deploy: Configure Vercel + Render"
git push origin main

# 2. Render deploys automatically
# 3. Vercel deploys automatically
# 4. Both should be live within 2-5 minutes

# Check deployment status:
# Render: https://dashboard.render.com
# Vercel: https://vercel.com/dashboard
```

---

## 📊 Expected Timeline

| Step | Time | Platform |
|------|------|----------|
| Create account | 5 min | Both |
| Connect GitHub | 2 min | Both |
| Create service | 2 min | Both |
| Configure settings | 5 min | Both |
| Deploy | 2-3 min | Render |
| Deploy | 1-2 min | Vercel |
| **Total** | **~20 min** | - |

---

## 🎉 You're Ready!

Your application is configured for:
- ✅ **Vercel**: Frontend (React + Vite)
- ✅ **Render**: Backend (Flask + Gunicorn)
- ✅ **GitHub**: Source control (automatic deployments)
- ✅ **Communication**: Frontend → Backend API

**Next steps**: Follow Part 1 and Part 2 above to deploy! 🚀

---

**Note**: First request to Render backend may take 30+ seconds (spin-up). Subsequent requests are fast.

For always-on backend, upgrade Render to "Starter" plan ($7/month).

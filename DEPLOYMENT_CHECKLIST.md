# 🚀 Quick Deployment Checklist

**Status**: Ready for Vercel + Render deployment

**Last updated**: Today  
**Model accuracy**: 77.98%  
**Backend framework**: Flask 3.0 + Gunicorn  
**Frontend framework**: React 18 + Vite + TypeScript  

---

## 📋 Pre-Deployment (10 minutes)

Before starting deployment, verify these are complete:

- [x] Model trained: `credit_engine/ensemble_phase3_optimized.pkl`
- [x] Backend code ready: `api.py` and `credit_engine/`
- [x] Frontend code ready: `frontend/src/` and `frontend/index.html`
- [x] All files committed to GitHub (main branch)
- [x] `render.yaml` created in root directory
- [x] `frontend/vercel.json` created
- [x] `frontend/.env.production` configured with backend URL
- [x] Requirements updated: `credit_engine/requirements.txt`

**Status**: ✅ All pre-deployment items complete

---

## 🔴 Render Backend Deployment (5 minutes)

### Step 1: Create Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize repository access
- [ ] Repository selected: `Credit-Engine` (or your fork)

**Status**: ⏳ Pending

### Step 2: Create Web Service
- [ ] Click "New +" in Render dashboard
- [ ] Select "Web Service"
- [ ] Choose your GitHub repository
- [ ] Confirm these settings:
  - [ ] **Name**: `credit-engine-backend`
  - [ ] **Environment**: `Python 3`
  - [ ] **Region**: `Oregon` (or your region)
  - [ ] **Branch**: `main`
  - [ ] **Build Command**: `pip install -r credit_engine/requirements.txt`
  - [ ] **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`

**Status**: ⏳ Pending

### Step 3: Add Environment Variables
In Render dashboard → Your Service → Environment:
- [ ] `FLASK_ENV` = `production`
- [ ] `FLASK_DEBUG` = `0`
- [ ] `DEBUG` = `False`
- [ ] `PYTHONUNBUFFERED` = `1`

**Status**: ⏳ Pending

### Step 4: Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-3 minutes)
- [ ] ✅ Deployment successful status shown
- [ ] Note your backend URL: `https://credit-engine-backend.onrender.com`

**Backend URL**: 
```
https://credit-engine-backend.onrender.com
```

**Status**: ⏳ Pending

### Step 5: Test Backend
- [ ] Run: `curl https://credit-engine-backend.onrender.com/api/health`
- [ ] Expected response: `{"status": "healthy", ...}`
- [ ] ✅ Health check passed

**Status**: ⏳ Pending

---

## 🔵 Vercel Frontend Deployment (5 minutes)

### Step 1: Create Vercel Account
- [ ] Go to https://vercel.com
- [ ] Sign up with GitHub
- [ ] Authorize repository access
- [ ] Repository selected: `Credit-Engine`

**Status**: ⏳ Pending

### Step 2: Create New Project
- [ ] Click "Add New" → "Project"
- [ ] Select your GitHub repository
- [ ] Click "Import"

**Status**: ⏳ Pending

### Step 3: Configure Build Settings
- [ ] **Framework preset**: Should auto-detect "Vite"
- [ ] **Root directory**: Set to `./frontend` (⚠️ Important!)
- [ ] **Build command**: Should be `npm run build`
- [ ] **Output directory**: Should be `dist`

**Status**: ⏳ Pending

### Step 4: Add Environment Variables
Go to Settings → Environment Variables and add:

**For Production**:
- [ ] `VITE_API_URL` = `https://credit-engine-backend.onrender.com`
- [ ] `VITE_LOG_LEVEL` = `info`

**For Preview** (Pull requests):
- [ ] `VITE_API_URL` = `https://credit-engine-backend.onrender.com`
- [ ] `VITE_LOG_LEVEL` = `debug`

**Status**: ⏳ Pending

### Step 5: Deploy
- [ ] Click "Deploy"
- [ ] Wait for build and deployment (1-2 minutes)
- [ ] ✅ Deployment successful status shown
- [ ] Note your frontend URL: `https://credit-engine.vercel.app`

**Frontend URL**:
```
https://credit-engine.vercel.app
```

**Status**: ⏳ Pending

---

## ✅ Post-Deployment Tests (5 minutes)

### Test 1: Backend Health
```bash
curl https://credit-engine-backend.onrender.com/api/health
```
Expected:
```json
{"status": "healthy", "message": "Credit Engine API is running"}
```
- [ ] ✅ Test passed

**Status**: ⏳ Pending

### Test 2: Frontend Loads
- [ ] Open https://credit-engine.vercel.app in browser
- [ ] ✅ Page loads without errors
- [ ] ✅ Form fields visible
- [ ] ✅ Submit button visible

**Status**: ⏳ Pending

### Test 3: API Connection
- [ ] Open browser DevTools (F12)
- [ ] Go to Network tab
- [ ] Fill in test form:
  - Applicant Name: "Test User"
  - Annual Revenue: "50000"
  - Net Profit: "5000"
  - Debt-to-Equity Ratio: "0.5"
  - Fraud Score: "0.2"
  - Average Balance: "10000"
- [ ] Click "Analyze"
- [ ] Check Network tab:
  - [ ] ✅ Request to `/api/predict` visible
  - [ ] ✅ Response status: 200
  - [ ] ✅ Response contains `decision` and `confidence`

**Status**: ⏳ Pending

### Test 4: Full Decision Display
- [ ] Form submission completes
- [ ] Results section shows:
  - [ ] ✅ Decision: `APPROVE` or `REJECT`
  - [ ] ✅ Confidence: percentage value
  - [ ] ✅ Feature contributions chart
  - [ ] ✅ Risk assessment text

**Status**: ⏳ Pending

### Test 5: Error Handling
- [ ] Clear form (leave empty)
- [ ] Click "Analyze"
- [ ] Should show validation error message
- [ ] [ ] ✅ Error message displayed

**Status**: ⏳ Pending

---

## 🔧 Configuration Summary

### Backend Configuration
```
Service: credit-engine-backend
Platform: Render
Runtime: Python 3.9
Port: $PORT (auto-assigned, ~5000)
URL: https://credit-engine-backend.onrender.com
Model: ensemble_phase3_optimized.pkl (77.98% accuracy)
```

### Frontend Configuration
```
Project: credit-engine
Platform: Vercel
Runtime: Node.js
Build tool: Vite
URL: https://credit-engine.vercel.app
API Endpoint: https://credit-engine-backend.onrender.com
```

### Environment
```
Production: FLASK_ENV=production, VITE_API_URL=https://credit-engine-backend.onrender.com
Development: FLASK_ENV=development, VITE_API_URL=http://localhost:5000
```

---

## 📊 Performance Notes

| Metric | Value | Notes |
|--------|-------|-------|
| Model Accuracy | 77.98% | Test set (10K samples) |
| Inference Time | 200-300ms | Per prediction |
| Frontend Bundle | ~300KB | Gzipped |
| Vercel Deploy Time | 1-2 min | Automated |
| Render Deploy Time | 2-3 min | Automated |
| **First Backend Request** | **30+ seconds** | Render spins up (free tier) |
| Subsequent Requests | <500ms | Normal response time |

---

## 💰 Cost

| Service | Plan | Cost | Notes |
|---------|------|------|-------|
| Vercel | Free | $0 | Unlimited deployments |
| Render | Free | $0 | Sleeps after 15 min idle |
| **Total** | - | **$0** | Free tier tested |

**Upgrade path**: $7/month (Render Starter) for always-on backend

---

## 🆘 Troubleshooting

### ❌ Backend not responding
```bash
# Check Render logs
# https://dashboard.render.com → Your Service → Logs
# Look for: "Gunicorn started successfully"
```

### ❌ Frontend shows blank page
```bash
# Check Vercel logs
# https://vercel.com/dashboard → Your Project → Deployments
# Most recent deployment should show green checkmark
```

### ❌ API returns 404
```bash
# Verify backend URL in .env.production
# Should be: https://credit-engine-backend.onrender.com
# Check DevTools Network tab for actual request URL
```

### ❌ CORS errors
```bash
# Backend already has CORS enabled in api.py
# If errors persist, check:
# 1. Backend is responding (curl test above)
# 2. Frontend environment variable is correct
# 3. Render backend service is running
```

### ❌ Render backend keeps spinning down
```bash
# This is normal on free tier (sleeps after 15 min)
# Solutions:
# 1. Upgrade to Starter plan ($7/month)
# 2. Accept 30-second spin-up time on first request
# 3. Use monitoring service to keep it awake (external)
```

---

## 📞 Support URLs

| Service | Dashboard | Docs | Status |
|---------|-----------|------|--------|
| Render | https://dashboard.render.com | https://render.com/docs | https://status.render.com |
| Vercel | https://vercel.com/dashboard | https://vercel.com/docs | https://www.vercelstatus.com |
| GitHub | https://github.com/settings/apps | https://docs.github.com | https://www.githubstatus.com |

---

## 📋 Completion Checklist

### Overall Status
- [ ] Read this entire checklist
- [ ] Render backend deployed and tested
- [ ] Vercel frontend deployed and tested
- [ ] End-to-end prediction works (test form)
- [ ] Browser DevTools shows no errors
- [ ] Render dashboard shows healthy service
- [ ] Vercel dashboard shows all green

### Post-Deployment Tasks
- [ ] Save URLs for reference
- [ ] Share URLs with team
- [ ] Monitor first 24 hours for issues
- [ ] Set up alerts (optional, in Render/Vercel dashboards)
- [ ] Plan for upgrade to paid tier (if needed)

---

## 🎉 You're Deployed!

Your application is now live:

🌐 **Frontend**: https://credit-engine.vercel.app  
🔌 **API Backend**: https://credit-engine-backend.onrender.com  
📊 **Model**: 77.98% accuracy, production-ready  

### Next Steps
1. Share URLs with stakeholders
2. Gather user feedback
3. Monitor production metrics
4. Plan Phase 4 improvements (additional features)

---

**Questions?** Check [DEPLOY_VERCEL_RENDER.md](./DEPLOY_VERCEL_RENDER.md) for detailed setup guide.

**Ready to deploy?** Follow the steps above! 🚀

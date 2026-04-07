# 🚀 DEPLOYMENT GUIDE - FPV Nexus (React + FastAPI)

## Why React + FastAPI Instead of Streamlit?

| Feature | Streamlit | React + FastAPI |
|---------|-----------|----------------|
| Hosting | Limited | ✅ Any cloud |
| Scalability | Single server | ✅ Distributed |
| SEO | ❌ No | ✅ Yes |
| Mobile responsive | Limited | ✅ Perfect |
| Custom styling | Limited | ✅ Full control |
| Production | Not ideal | ✅ Industry standard |
| Cost | Higher | ✅ Lower at scale |

---

## 🏗️ PROJECT ARCHITECTURE

```
Frontend (React on port 3000)
   ↓
   ↓ API calls (HTTP)
   ↓
Backend (FastAPI on port 8000)
   ↓
   ↓ Computation
   ↓
Python computation modules
```

---

## 🐳 QUICK START WITH DOCKER

### Option 1: Local Development (Docker)

```bash
# Install Docker & Docker Compose
# https://www.docker.com/products/docker-desktop

# Clone/navigate to project
cd c:\Users\AMITESH\hydro\fpv_project

# Start both services
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Setup (Without Docker)

#### Backend:
```bash
cd c:\Users\AMITESH\hydro\fpv_project\backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Backend runs at http://localhost:8000
```

#### Frontend (new terminal):
```bash
cd c:\Users\AMITESH\hydro\fpv_project\frontend
npm install
npm start
# Frontend runs at http://localhost:3000
```

---

## ☁️ CLOUD DEPLOYMENT OPTIONS

### Option 1: Heroku (FREE TIER DISCONTINUED - Use alternatives)

### Option 2: **Render** ⭐ RECOMMENDED

Free tier available, easy deployment.

#### Backend Deployment:

1. **Create account** on https://render.com
2. **Connect GitHub** (push your code there first)
3. **Create Web Service**:
   - Select Repository: fpv-project
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 10000`
   - Environment: Python 3.11
   - Add environment variable: `PORT=10000`

4. **Deploy**
5. **Get URL:** e.g., `https://fpv-backend-xxxxx.onrender.com`

#### Frontend Deployment:

1. **Create another Web Service** on Render
2. **Select Repository:** fpv-project
3. **Build Command:** `cd frontend && npm install && npm run build`
4. **Start Command:** `npm install -g serve && serve -s build -l 3000`
5. **Environment Variable:**
   - `REACT_APP_API_URL=https://fpv-backend-xxxxx.onrender.com`

6. **Deploy**
7. **Access:** https://fpv-frontend-xxxxx.onrender.com

---

### Option 3: Railway.app ⭐ ALTERNATIVE

Similar to Render, slightly better UX.

```bash
# Install railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

---

### Option 4: **AWS + Elastic Beanstalk**

```bash
# Install AWS CLI
pip install awsebcli

# Initialize
eb init

# Create environment
eb create fpv-env

# Deploy backend
eb deploy

# Deploy frontend to CloudFront + S3
# See AWS documentation for React apps
```

---

### Option 5: **Google Cloud Run** (CHEAPEST)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/fpv-backend

# Deploy
gcloud run deploy fpv-backend \
  --image gcr.io/PROJECT_ID/fpv-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Same for frontend
```

---

## 📋 Production Checklist

### Backend Security
- ✅ Add API authentication (JWT tokens)
- ✅ Rate limiting (prevent abuse)
- ✅ Input validation (already in Pydantic)
- ✅ CORS properly configured
- ✅ HTTPS enforced

### Frontend
- ✅ Environment variables for API URL
- ✅ Build optimization (done by create-react-app)
- ✅ Error handling
- ✅ Loading states

### Infrastructure
- ✅ Database optional (currently CSV-based)
- ✅ Caching (use Redis if needed)
- ✅ Monitoring (Sentry, LogRocket)
- ✅ CDN for frontend (CloudFlare)

---

## 🔒 Environment Configuration

### Backend (.env file):
```
API_HOST=0.0.0.0
API_PORT=8000
PYTHONUNBUFFERED=1
```

### Frontend (.env file):
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## 📊 Performance Tips

### Backend
- Use caching for climate data
- Implement request queuing
- Add database for historical data
- Use CDN for static files

### Frontend
- Code splitting for routes
- Image optimization
- Lazy loading
- CSS minification (done by build)

---

## 🧪 Testing Before Deploy

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# Integration test
curl http://localhost:8000/reservoirs
```

---

## 🚨 Common Deployment Issues

### Issue: CORS Error
**Fix:** Update `main.py` CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
)
```

### Issue: API URL Wrong in Frontend
**Fix:** Set environment variable:
```bash
REACT_APP_API_URL=https://api.yourdomain.com
```

### Issue: Port Conflicts
**Fix:** Change port in docker-compose.yml or uvicorn command

---

## 📞 RECOMMENDED SETUP FOR BEGINNERS

**Choose this if you're new:**

1. **Render.app** for hosting
2. **GitHub** for version control
3. **CloudFlare** for domain + SSL
4. **Free tier** to start

**Total Cost:** ~$15/month domain (free for .tk)

---

## 🎯 NEXT STEPS

1. Push code to GitHub
2. Create Render account
3. Connect GitHub repos
4. Deploy backend & frontend
5. Set environment variables
6. Test live at https://yourdomain.com

---

## 📈 SCALING

When you get more users:

1. **Database:** PostgreSQL on managed service
2. **API:** Multiple instances with load balancer
3. **Frontend:** Static hosting + CDN
4. **Cache:** Redis for expensive computations
5. **Monitoring:** Sentry + LogRocket

---

**Ready to deploy? Start with Render!** 🚀

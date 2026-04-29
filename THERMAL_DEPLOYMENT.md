# 🌡️ Thermal Mapping - Live Deployment Guide

## ✅ What's Ready to Deploy

- ✅ Backend FastAPI with thermal API endpoints
  - `GET /thermal/data` - Real NASA thermal data
  - `GET /thermal/legend` - Color legend
  - All dam endpoints working

- ✅ Frontend React with thermal overlay
  - Toggle button on map
  - Real-time thermal visualization
  - All dam analysis features

---

## 🚀 FASTEST DEPLOYMENT (15 mins)

### **Option A: Heroku + Vercel (RECOMMENDED - FREE)**

#### **Step 1: Deploy Backend to Heroku**

```bash
# 1. Install Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# Or: choco install heroku-cli

# 2. Login
heroku login

# 3. Create Heroku app
cd c:\Users\AMITESH\hydro9
heroku create fpv-nexus-api

# 4. Create Procfile (if not exists)
echo "web: cd backend && uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 5. Create runtime.txt
echo "python-3.11.10" > runtime.txt

# 6. Initialize git (if not done)
git init
git add .
git commit -m "Initial commit - thermal mapping"

# 7. Deploy
git push heroku main

# 8. Get your backend URL
heroku apps
# -> https://fpv-nexus-api.herokuapp.com
```

#### **Step 2: Deploy Frontend to Vercel**

```bash
# 1. Update API URL for production
# Edit: frontend/src/components/DamMap.js (line 5)
# Change: const API_BASE = 'http://localhost:8000';
# To: const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

# 2. Create .env.production in frontend folder
cat > frontend/.env.production << EOF
REACT_APP_API_URL=https://fpv-nexus-api.herokuapp.com
EOF

# 3. Install Vercel CLI
npm install -g vercel

# 4. Deploy frontend
cd frontend
vercel
# Select: current folder as root
# Build: npm run build
# Output: build

# 5. Your frontend URL - will be printed
# -> https://fpv-nexus-[random].vercel.app
```

#### **Step 3: Enable CORS on Backend**

```bash
# 1. Edit backend/main.py (line ~40)
# Replace CORS configuration with:

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3003",
        "https://fpv-nexus-*.vercel.app",
        "https://vercel.app",
        "*"  # Allow all
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Deploy updated backend
git add backend/main.py
git commit -m "Enable CORS for Vercel frontend"
git push heroku main

# 3. Verify
heroku logs --tail
```

---

## 🎯 **TESTING LIVE DEPLOYMENT**

```bash
# Test backend endpoints
curl https://fpv-nexus-api.herokuapp.com/dams
curl https://fpv-nexus-api.herokuapp.com/thermal/data
curl https://fpv-nexus-api.herokuapp.com/thermal/legend

# Test frontend - open in browser
https://fpv-nexus-[random].vercel.app

# Toggle thermal map - should work!
```

---

## **Option B: Railway.app (EASIER - Recommended)**

### **Deploy Backend**
```bash
npm i -g @railway/cli
railway login
cd c:\Users\AMITESH\hydro9
railway init
# Select Python
railway up
# Get URL from dashboard
```

### **Deploy Frontend**
```bash
cd frontend
railway init
# Select Node.js
railway up
```

---

## **Option C: Docker (Self-hosted)**

```bash
# 1. Create docker-compose.yml in project root

version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    command: uvicorn main:app --host 0.0.0.0 --port 8000
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

# 2. Create Dockerfile in backend/
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 3. Create Dockerfile in frontend/
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]

# 4. Build and run
docker-compose up --build

# Access: http://localhost:3000
```

---

## 📋 **QUICK CHECKLIST**

### Before Deployment:
- [ ] Thermal overlay working locally
- [ ] npm run build succeeds
- [ ] No console errors
- [ ] Backend API responds
- [ ] Test in multiple browsers

### After Deployment:
- [ ] Backend URL accessible
- [ ] Frontend loads
- [ ] API calls work (check Network tab)
- [ ] Thermal toggle button works
- [ ] Real thermal data displays

### Troubleshooting:
```
❌ CORS Error → Add frontend URL to backend CORS origins
❌ API 404 → Check API_BASE URL in frontend .env
❌ Thermal blank → Check /thermal/data endpoint
❌ Heroku error → heroku logs --tail
```

---

## 🔗 **YOUR LIVE URLs WILL BE:**

After deployment:
```
🌐 Frontend: https://fpv-nexus-[random].vercel.app
🔌 Backend:  https://fpv-nexus-api.herokuapp.com
📊 API Docs: https://fpv-nexus-api.herokuapp.com/docs
🌡️ Thermal:  https://fpv-nexus-api.herokuapp.com/thermal/data
```

---

## 💡 **RECOMMENDED PATH**

1. **Heroku for Backend** - Simple Python deployment, free tier available
2. **Vercel for Frontend** - Zero-config React deployment, GitHub integration
3. **Add Custom Domain** (optional) - Later via DNS settings

**Total Time**: ~15-20 minutes
**Cost**: $0 (free tier) or ~$7-12/month if scaling

---

## 🎓 NEXT STEPS

1. Test deployment commands locally first
2. Choose hosting (Heroku + Vercel recommended)
3. Deploy backend first
4. Deploy frontend second
5. Share public URLs with team!

**Need help?** Check:
- Heroku docs: https://devcenter.heroku.com
- Vercel docs: https://vercel.com/docs
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/

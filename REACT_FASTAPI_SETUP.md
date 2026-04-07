# 🚀 REACT + FASTAPI SETUP GUIDE

## What You Get

✅ **Production-grade** architecture  
✅ **Separately scalable** frontend + backend  
✅ **Hostable anywhere** (AWS, Heroku, Render, Google Cloud, etc.)  
✅ **Professional UI** with React  
✅ **REST API** for any client  
✅ **Docker-ready** for deployment  

---

## 📦 Project Structure

```
fpv_project/
├── backend/                    # FastAPI server
│   ├── main.py                # API endpoints
│   └── requirements.txt        # Python deps
│
├── frontend/                  # React dashboard
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.js   # Main component
│   │   ├── styles/
│   │   │   └── Dashboard.css
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
│
├── models/                    # Computation modules
│   ├── fpv.py
│   ├── hydro.py
│   ├── evaporation.py
│   └── co2.py
│
├── utils/
│   └── data_loader.py
│
├── data/
│   ├── reservoir.csv
│   └── climate.csv
│
├── docker-compose.yml         # Run both services
├── Dockerfile.backend         # Backend container
├── Dockerfile.frontend        # Frontend container
├── DEPLOYMENT_GUIDE.md        # Hosting guide
└── README.md
```

---

## 🚀 OPTION 1: DOCKER (RECOMMENDED)

### What is Docker?
"Docker" packages your application and all dependencies into a **container** that runs anywhere.

Think of it as: **Ship it like a package**

### Setup

```bash
# 1. Install Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. Navigate to project
cd c:\Users\AMITESH\hydro\fpv_project

# 3. Verify Docker installed
docker --version

# 4. Start everything!
docker-compose up --build
```

### Access Services

- **Frontend:** http://localhost:3000 ← Use this! 🎨
- **Backend API:** http://localhost:8000 📡
- **API Docs:** http://localhost:8000/docs 📚

### Stop Services
```bash
docker-compose down
```

---

## 🖥️ OPTION 2: LOCAL SETUP (NO DOCKER)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m uvicorn main:app --reload

# Output:
# Uvicorn running on http://127.0.0.1:8000
# API docs at http://127.0.0.1:8000/docs
```

Keep this terminal open!

### Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Browser opens automatically at http://localhost:3000
```

Keep this terminal open too!

---

## 🌐 API ENDPOINTS

The **backend** provides these endpoints:

### Health Check
```bash
GET /health
```

### Get Preset Reservoirs
```bash
GET /reservoirs

# Response:
[
  {"name": "Bhaira Reservoir", "area_km2": 45.0, ...},
  {"name": "Rana Pratap Sagar", "area_km2": 89.5, ...},
  ...
]
```

### Get Monthly Climate Data
```bash
GET /climate

# Returns 12 months of temperature, irradiance, evaporation
```

### Get Annual Averages
```bash
GET /climate/averages

# Response:
{
  "avg_temp": 28.0,
  "avg_solar_irradiance": 4.69,
  "avg_evaporation": 3.18,
  "total_solar_irradiance": 56.28
}
```

### **MAIN ENDPOINT: Compute Scenario**
```bash
POST /compute

# Request body:
{
  "area_km2": 45.0,
  "coverage": 0.15,        # 15%
  "efficiency": 0.18,
  "head_m": 28.5,
  "avg_irradiance": 4.69,
  "avg_evaporation": 3.18,
  "avg_temp": 28,
  "wind_speed": 2.0,
  ...
}

# Response: All KPIs and results (see below)
```

### Quick Compute
```bash
POST /compute/quick?area_km2=45&coverage=0.15&avg_irradiance=4.69&head_m=28.5
```

---

## 🎨 REACT FRONTEND

### Features

**Interactive Sliders:**
- FPV Coverage (1-50%) 🎚️
- Panel Efficiency (10-25%)
- Climate parameters
- Economic inputs

**Real-time KPIs:**
- 🔆 FPV Capacity (MWp)
- 💧 Water Saved (Million m³)
- ⚡ Extra Hydro (MWh)
- 🌍 CO₂ Avoided (tonnes)

**Visualizations:**
- Energy Mix Bar Chart
- CO₂ Breakdown Pie Chart
- Environmental Impact Cards

**Export:**
- Download Reports as .txt

---

## 🛠️ DEVELOPMENT

### Editing Backend

Edit `backend/main.py`:
- Add new endpoints
- Modify computation logic
- Change API responses

Changes auto-reload!

### Editing Frontend

Edit `frontend/src/components/Dashboard.js`:
- Modify form inputs
- Change UI layout
- Add new charts
- Update styles

Changes auto-refresh in browser!

---

## 📊 TESTING

### Test Backend API

```bash
# Using curl (all platforms)
curl http://localhost:8000/health

# Using Python
import requests
response = requests.post(
    'http://localhost:8000/compute',
    json={
        'area_km2': 45,
        'coverage': 0.15,
        'efficiency': 0.18,
        'head_m': 28.5,
        'avg_irradiance': 4.69,
        'avg_evaporation': 3.18,
        'avg_temp': 28,
        'wind_speed': 2.0
    }
)
print(response.json())
```

### Test Frontend

```bash
# Already running at http://localhost:3000
# Just use the browser interface!
```

---

## 🔧 TROUBLESHOOTING

### Port Already in Use

```bash
# If port 3000 is busy
cd frontend
npm start -- --port 3001

# If port 8000 is busy
cd backend
uvicorn main:app --port 8001
```

### Dependencies Not Installing

```bash
# Backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Frontend
npm install --legacy-peer-deps
```

### CORS Errors in Browser

Check `backend/main.py` CORS settings:
```python
allow_origins=["*"]  # Development only!
```

### API URL Not Found

Edit `frontend/src/components/Dashboard.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

Or set environment variable:
```bash
set REACT_APP_API_URL=http://localhost:8000
```

---

## 📦 BUILDING FOR PRODUCTION

### Backend
```bash
cd backend
pip install -r requirements.txt
# Run with gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
# Creates `build/` folder with optimized files
```

---

## 🚀 DEPLOYING TO RENDER

1. **Push code to GitHub**
```bash
git init
git add -A
git commit -m "Initial commit"
git push -u origin main
```

2. **Create Backend Service on Render**
   - Connect your GitHub repo
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker`
   - Runtime: Python 3.11

3. **Create Frontend Service on Render**
   - Build command: `cd frontend && npm install && npm run build`
   - Start command: `npm install -g serve && serve -s build`
   - Environment: `REACT_APP_API_URL=<your-backend-url>`

4. **Access:**
   - Frontend: https://yourdomain.onrender.com
   - Backend API: https://api.yourdomain.onrender.com/docs

---

## 🎁 What You Can Now Do

✅ Simple local testing
✅ Share with friends (ngrok tunneling)
✅ Deploy to any cloud provider
✅ Scale to millions of users
✅ Add authentication
✅ Add database
✅ Add real-time updates
✅ Build mobile app from same API

---

## 📚 NEXT STEPS

1. **Test locally:** Run `docker-compose up` ✓
2. **Explore API:** Visit http://localhost:8000/docs
3. **Adjust UI:** Edit `Dashboard.js`
4. **Deploy:** Follow DEPLOYMENT_GUIDE.md
5. **Share:** Get unique URL and share!

---

## 🆘 HELP

**Stuck?** Check:
- `DEPLOYMENT_GUIDE.md` - Full hosting options
- `backend/main.py` - API definitions
- `frontend/src/components/Dashboard.js` - React component
- FastAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/

---

**Ready to launch?** 🚀

```bash
cd c:\Users\AMITESH\hydro\fpv_project
docker-compose up --build
```

**Then open http://localhost:3000** ✨

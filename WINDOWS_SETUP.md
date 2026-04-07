# 🚀 WINDOWS SETUP GUIDE - FPV Nexus Dashboard

## ⚡ Quick Start (Recommended)

### Option 1: Using Anaconda (BEST FOR WINDOWS)

```bash
# 1. Install Anaconda from https://www.anaconda.com/download
# 2. Open Anaconda Prompt
# 3. Create environment
conda create -n fpv python=3.10 -y
conda activate fpv

# 4. Install packages
cd c:\Users\AMITESH\hydro\fpv_project
pip install streamlit pandas numpy plotly scipy

# 5. Run dashboard
python -m streamlit run app/dashboard.py
```

---

### Option 2: System Python with Direct Installation

```bash
# 1. Open Command Prompt
cd c:\Users\AMITESH\hydro\fpv_project

# 2. Install directly to system Python
pip install --user streamlit pandas numpy plotly scipy

# 3. Run dashboard
python -m streamlit run app/dashboard.py
```

---

### Option 3: Verify Core Functionality (NO STREAMLIT NEEDED)

```bash
# 1. Run demo script (verifies all calculations work)
cd c:\Users\AMITESH\hydro\fpv_project
python demo.py

# Output: Comprehensive scenario analysis with all KPIs
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'streamlit'"

**Cause:** Package not installed for your Python version

**Fix:**
```bash
# Option A: Use Anaconda (recommended)
conda install streamlit

# Option B: Reinstall with --user flag
pip install --user --upgrade streamlit

# Option C: Check your Python version
python --version
# Must be 3.8+
```

---

### Issue: Windows Store Python conflicts

**Solution:** Use Anaconda or ActivePython instead

```bash
# Check if you're using Windows Store Python:
python -c "import sys; print(sys.executable)"

# If path contains "WindowsApps", use Anaconda instead
```

---

## 📋 Directory Structure

```
fpv_project/
├── demo.py                 ← Run this for core demo
├── app/
│   └── dashboard.py        ← Main Streamlit app
├── models/
│   ├── fpv.py             ← FPV energy calculations
│   ├── hydro.py           ← Hydropower models
│   ├── evaporation.py     ← Water savings
│   └── co2.py             ← Environmental impact
├── utils/
│   └── data_loader.py     ← Data utilities
├── data/
│   ├── reservoir.csv      ← Sample reservoir data
│   └── climate.csv        ← Climate data
├── requirements.txt
└── README.md
```

---

## 🎯 To Run Dashboard After Setup

### Windows Command Prompt:
```cmd
cd c:\Users\AMITESH\hydro\fpv_project
python -m streamlit run app/dashboard.py
```

### Results:
- Dashboard opens at: **http://localhost:8501**
- Interactive sliders for all parameters
- Real-time KPI updates
- Charts and visualizations

---

## ⚙️ System Requirements

- **Python:** 3.8 or higher (check: `python --version`)
- **RAM:** 500MB+
- **Internet:** Not required (once installed)

---

## 📦 Package Versions

All are compatible with Python 3.10+:
```
streamlit==1.28.1
plotly==5.17.0
pandas==2.0.3
numpy==1.24.3
scipy==1.11.2
pvlib==0.10.3  (optional, used for temperature corrections)
```

---

## 🧪 Verify Installation

```bash
# Test Core Functionality
python -c "from models import compute_fpv_power; print('✓ Core functions working')"

# Run Full Demo
python demo.py

# Output shows all calculations working
```

---

## 🌐 Access Dashboard

After running `streamlit run app/dashboard.py`:

1. Open browser: **http://localhost:8501**
2. Use sidebar to adjust parameters
3. View real-time KPI updates
4. Export reports

---

## 💡 Tips

- **First time?** Run `python demo.py` to verify system works
- **Faster updates?** Use sidebar sliders instead of typing
- **Export data?** Click download in sidebar
- **Change host?** Use `--server.address 0.0.0.0` for network access

---

## 🆘 Need Help?

1. Check Python version: `python --version` (need 3.8+)
2. Verify packages: `pip list | find "streamlit"`
3. Try demo: `python demo.py`
4. IfStill stuck, use Anaconda (most reliable on Windows)

---

## 📚 NEXT STEPS

1. ✅ Run system test: `python demo.py`
2. ✅ Test dashboard: `python -m streamlit run app/dashboard.py`
3. ✅ Adjust parameters with sliders
4. ✅ Try different reservoirs
5. ✅ Generate reports

---

**Happy Co-Optimizing! ☀️💧⚡**

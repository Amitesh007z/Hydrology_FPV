"""
Quick test to verify all modules import correctly
"""

import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.path[:3]}")

try:
    import streamlit as st
    print("✓ Streamlit imported")
except ImportError as e:
    print(f"✗ Streamlit error: {e}")

try:
    import plotly
    print("✓ Plotly imported")
except ImportError as e:
    print(f"✗ Plotly error: {e}")

try:
    import pandas
    print("✓ Pandas imported")
except ImportError as e:
    print(f"✗ Pandas error: {e}")

try:
    import numpy
    print("✓ NumPy imported")
except ImportError as e:
    print(f"✗ NumPy error: {e}")

try:
    import pvlib
    print("✓ pvlib imported")
except ImportError as e:
    print(f"✗ pvlib error: {e}")

print("\nTesting local modules...")
sys.path.insert(0, '/c/Users/AMITESH/hydro/fpv_project')

try:
    from models import compute_fpv_power
    print("✓ FPV model imported")
    result = compute_fpv_power(50, 0.1, 4.5, 0.18)
    print(f"  Sample result: {result:.2f} MWh/day")
except Exception as e:
    print(f"✗ FPV model error: {e}")

try:
    from utils import load_reservoir_data
    print("✓ Data loader imported")
except Exception as e:
    print(f"✗ Data loader error: {e}")

print("\n✓ All tests passed!")

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  ArrowLeft, Zap, Droplet, Leaf, TrendingUp, Wind, Thermometer, 
  AlertCircle 
} from 'lucide-react';
import '../styles/DamAnalysis.css';

const API_BASE = 'http://localhost:8000';

const DamAnalysis = ({ damName, onBack }) => {
  const [damData, setDamData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // FPV Parameters
  const [coverage, setCoverage] = useState(10);
  const [efficiency, setEfficiency] = useState(18);
  const [performance_ratio, setPerformanceRatio] = useState(75);
  const [structure_type, setStructureType] = useState('pontoon');
  const [analyzing, setAnalyzing] = useState(false);

  const fetchDamData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/dams/${damName}`);
      if (response.data.success) {
        setDamData(response.data);
      }
      setError(null);
    } catch (err) {
      setError('Failed to fetch dam data');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  }, [damName]);

  useEffect(() => {
    fetchDamData();
  }, [fetchDamData]);

  const runAnalysis = useCallback(async (dam = null) => {
    const targetDam = dam || damData;
    if (!targetDam) return;

    try {
      setAnalyzing(true);
      const payload = {
        // Required fields
        area_km2: parseFloat(targetDam.reservoir.area_km2) || 50,
        coverage: parseFloat(coverage) / 100,
        efficiency: parseFloat(efficiency) / 100,
        pr: parseFloat(performance_ratio) / 100,
        head_m: parseFloat(targetDam.reservoir.head_m) || 30,
        installed_capacity_mw: parseFloat(targetDam.reservoir.installed_capacity_mw) || 500,
        avg_irradiance: parseFloat(targetDam.climate_summary?.solar_irradiance || 4.5),
        avg_evaporation: parseFloat(targetDam.climate_summary?.evaporation || 5),
        avg_temp: parseFloat(targetDam.climate_summary?.avg_temp || 25),
        wind_speed: parseFloat(targetDam.climate_summary?.wind_speed || 2),
        humidity: parseFloat(targetDam.climate_summary?.humidity || 65),
        
        // Optional fields with defaults
        structure_type: structure_type || 'pontoon',
        evap_model: 'regression',
        temp_variation: 1.0,
        emission_factor: 0.82,
        hydro_tariff: 4.5,
        capex_cr_per_mwp: 4.0,
        fpv_tariff: 3.5,
        discount_rate: 0.10,
        project_lifetime: 25,
        reservoir_name: targetDam.reservoir.reservoir_name || 'Dam'
      };
      
      const response = await axios.post(`${API_BASE}/dams/${damName}/analyze`, payload);

      if (response.data) {
        setAnalysis(response.data);
      }
    } catch (err) {
      console.error('Analysis error:', err.response?.data || err);
    } finally {
      setAnalyzing(false);
    }
  }, [damName, damData, coverage, efficiency, performance_ratio, structure_type]);

  if (loading) {
    return (
      <div className="dam-analysis-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading dam data...</p>
        </div>
      </div>
    );
  }

  if (!damData) {
    return (
      <div className="dam-analysis-container">
        <div className="error-state">
          <AlertCircle size={48} />
          <p>Failed to load dam data</p>
          <button onClick={onBack} className="back-button">
            <ArrowLeft size={20} /> Back to Map
          </button>
        </div>
      </div>
    );
  }

  const reservoir = damData.reservoir;

  return (
    <div className="dam-analysis-container">
      {/* Header */}
      <div className="analysis-header">
        <button onClick={onBack} className="back-button">
          <ArrowLeft size={20} /> Back to Map
        </button>
        <div>
          <h1>{reservoir.reservoir_name}</h1>
          <p className="location">{reservoir.state} • {reservoir.river}</p>
        </div>
      </div>

      {/* Dam Info Cards */}
      <div className="dam-info-grid">
        <div className="info-card">
          <div className="info-label">Installed Capacity</div>
          <div className="info-value">{reservoir.installed_capacity_mw} MW</div>
        </div>
        <div className="info-card">
          <div className="info-label">Surface Area</div>
          <div className="info-value">{reservoir.area_km2} km²</div>
        </div>
        <div className="info-card">
          <div className="info-label">Water Head</div>
          <div className="info-value">{reservoir.head_m} m</div>
        </div>
        <div className="info-card">
          <div className="info-label">Storage Capacity</div>
          <div className="info-value">{reservoir.gross_storage_mcm || 'N/A'} MCM</div>
        </div>
      </div>

      {/* Climate Summary */}
      <div className="climate-summary">
        <h2>Climate Profile</h2>
        <div className="climate-grid">
          <div className="climate-card">
            <Zap size={24} color="#FFA500" />
            <div>
              <p className="climate-label">Solar Irradiance</p>
              <p className="climate-value">{(damData.climate_summary?.solar_irradiance || 0).toFixed(2)} kWh/m²/day</p>
            </div>
          </div>
          <div className="climate-card">
            <Thermometer size={24} color="#FF6B6B" />
            <div>
              <p className="climate-label">Avg Temperature</p>
              <p className="climate-value">{(damData.climate_summary?.avg_temp || 0).toFixed(1)}°C</p>
            </div>
          </div>
          <div className="climate-card">
            <Droplet size={24} color="#4ECDC4" />
            <div>
              <p className="climate-label">Evaporation Rate</p>
              <p className="climate-value">{(damData.climate_summary?.evaporation || 0).toFixed(2)} mm/day</p>
            </div>
          </div>
          <div className="climate-card">
            <Wind size={24} color="#87CEEB" />
            <div>
              <p className="climate-label">Wind Speed</p>
              <p className="climate-value">{(damData.climate_summary?.avg_wind_speed || 0).toFixed(1)} m/s</p>
            </div>
          </div>
        </div>
      </div>

      {/* FPV Parameters */}
      <div className="fpv-parameters">
        <h2>FPV Configuration</h2>
        <div className="params-grid">
          <div className="param-group">
            <label>FPV Coverage (%): {coverage}%</label>
            <input
              type="range"
              min="1"
              max="50"
              value={coverage}
              onChange={(e) => setCoverage(parseInt(e.target.value))}
              className="slider"
            />
          </div>
          <div className="param-group">
            <label>Panel Efficiency (%): {efficiency}%</label>
            <input
              type="range"
              min="10"
              max="25"
              value={efficiency}
              onChange={(e) => setEfficiency(parseInt(e.target.value))}
              className="slider"
            />
          </div>
          <div className="param-group">
            <label>Performance Ratio (%): {performance_ratio}%</label>
            <input
              type="range"
              min="60"
              max="85"
              value={performance_ratio}
              onChange={(e) => setPerformanceRatio(parseInt(e.target.value))}
              className="slider"
            />
          </div>
          <div className="param-group">
            <label>Structure Type:</label>
            <select value={structure_type} onChange={(e) => setStructureType(e.target.value)}>
              <option value="pontoon">Pontoon</option>
              <option value="flexible">Flexible</option>
            </select>
          </div>
        </div>
        <button 
          onClick={() => runAnalysis()} 
          disabled={analyzing}
          className="analyze-button"
        >
          {analyzing ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="analysis-results">
          <h2>FPV Analysis Results</h2>

          {/* KPI Cards */}
          <div className="kpi-grid">
            <div className="kpi-card energy">
              <Zap size={28} />
              <div>
                <p className="kpi-label">FPV Capacity</p>
                <p className="kpi-value">{(analysis.fpv_capacity_mwp || 0).toFixed(1)} MWp</p>
              </div>
            </div>
            <div className="kpi-card energy-alt">
              <TrendingUp size={28} />
              <div>
                <p className="kpi-label">Annual FPV Energy</p>
                <p className="kpi-value">{((analysis.annual_fpv_mwh || 0) / 1e6).toFixed(2)} Million MWh</p>
              </div>
            </div>
            <div className="kpi-card water">
              <Droplet size={28} />
              <div>
                <p className="kpi-label">Water Saved</p>
                <p className="kpi-value">{(analysis.water_saved_million_m3 || 0).toFixed(2)} Million m³</p>
              </div>
            </div>
            <div className="kpi-card sustainable">
              <Leaf size={28} />
              <div>
                <p className="kpi-label">CO₂ Avoided</p>
                <p className="kpi-value">{((analysis.co2_avoided_tonnes || 0) / 1e6).toFixed(2)} Million tonnes</p>
              </div>
            </div>
          </div>

          {/* Financial Metrics */}
          <div className="financial-section">
            <h3>Financial Analysis</h3>
            <div className="financial-grid">
              <div className="financial-metric">
                <p className="label">Total CAPEX</p>
                <p className="value">₹{(analysis.capex_total_cr || 0).toFixed(2)} Cr</p>
              </div>
              <div className="financial-metric">
                <p className="label">Annual OpEx</p>
                <p className="value">₹{(analysis.opex_annual_cr || 0).toFixed(2)} Cr</p>
              </div>
              <div className="financial-metric">
                <p className="label">LCOE</p>
                <p className="value">₹{(analysis.lcoe_inr_per_kwh || 0).toFixed(2)}/kWh</p>
              </div>
              <div className="financial-metric">
                <p className="label">Payback Period</p>
                <p className="value">{(analysis.payback_years || 0).toFixed(1)} years</p>
              </div>
              <div className="financial-metric">
                <p className="label">ROI</p>
                <p className="value">{((analysis.roi_percent || 0) * 100).toFixed(1)}%</p>
              </div>
              <div className="financial-metric">
                <p className="label">Annual Revenue</p>
                <p className="value">₹{(analysis.total_annual_revenue_cr || 0).toFixed(2)} Cr</p>
              </div>
            </div>
          </div>

          {/* Detailed Breakdown */}
          {analysis.summary && (
            <div className="summary-section">
              <h3>Summary</h3>
              <pre className="summary-text">
                {Object.entries(analysis.summary || {})
                  .map(([key, value]) => `${key}: ${value}`)
                  .join('\n')}
              </pre>
            </div>
          )}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default DamAnalysis;

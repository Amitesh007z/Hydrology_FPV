import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Sun, Droplets, Zap, Leaf, TrendingUp, Download, RefreshCw
} from 'lucide-react';
import '../styles/Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  // State management
  const [reservoirs, setReservoirs] = useState([]);
  const [climateData, setClimateData] = useState([]);
  const [climateAvg, setClimateAvg] = useState({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  // Form inputs
  const [inputs, setInputs] = useState({
    reservoir_name: 'Bhaira Reservoir',
    area_km2: 45.0,
    coverage: 10,
    efficiency: 0.18,
    pr: 0.75,
    head_m: 28.5,
    installed_capacity_mw: 85.0,
    avg_irradiance: 4.69,
    avg_evaporation: 3.18,
    avg_temp: 28,
    wind_speed: 2.0,
    temp_variation: 1.0,
    emission_factor: 0.82,
    hydro_tariff: 4.5
  });

  // Load initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [reservoirRes, climateRes, avgRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/reservoirs`),
          axios.get(`${API_BASE_URL}/climate`),
          axios.get(`${API_BASE_URL}/climate/averages`)
        ]);

        setReservoirs(reservoirRes.data);
        setClimateData(climateRes.data);
        setClimateAvg(avgRes.data);

        // Auto-compute with defaults
        computeScenario();
      } catch (error) {
        console.error('Failed to load data:', error);
      }
    };

    fetchInitialData();
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    const numValue = parseFloat(value);
    setInputs(prev => ({
      ...prev,
      [name]: isNaN(numValue) ? value : numValue
    }));
  };

  // Compute scenario
  const computeScenario = async (params = inputs) => {
    setLoading(true);
    try {
      const payload = {
        ...params,
        coverage: params.coverage / 100  // Convert to fraction
      };

      const response = await axios.post(`${API_BASE_URL}/compute`, payload);
      setResults(response.data);
    } catch (error) {
      console.error('Computation failed:', error);
      alert('Error computing scenario: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Debounced compute on input change
  useEffect(() => {
    const timer = setTimeout(() => {
      computeScenario();
    }, 500);
    return () => clearTimeout(timer);
  }, [inputs]);

  // Download report
  const downloadReport = () => {
    if (!results) return;

    const report = `
FPV NEXUS DASHBOARD - SCENARIO REPORT
Generated: ${new Date().toLocaleString()}

SCENARIO CONFIGURATION:
${Object.entries(inputs).map(([key, val]) => `${key}: ${val}`).join('\n')}

RESULTS:
${Object.entries(results.summary).map(([key, val]) => `${key}: ${val}`).join('\n')}

ENVIRONMENTAL IMPACT:
- CO2 Avoided: ${results.co2_avoided_tonnes.toLocaleString()} tonnes
- Trees Equivalent: ${results.trees_equivalent.toLocaleString()}
- Cars Offset: ${results.cars_offset.toLocaleString()}

ECONOMIC ANALYSIS:
- Hydro Revenue: ₹${results.hydro_revenue_crore.toFixed(2)} Crores/year
    `;

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(report));
    element.setAttribute('download', `fpv_report_${new Date().getTime()}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Chart data
  const energyChartData = results ? [
    { name: 'FPV Solar', value: results.annual_fpv_mwh },
    { name: 'Extra Hydro', value: results.extra_hydro_mwh_annual }
  ] : [];

  const co2ChartData = results ? [
    { name: 'FPV', value: results.co2_fpv_tonnes },
    { name: 'Hydro', value: results.co2_hydro_tonnes }
  ] : [];

  const COLORS = ['#FDB462', '#80B1D3'];

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>☀️ FPV NEXUS DASHBOARD</h1>
          <p>Floating Solar-Hydro Co-Optimization System</p>
        </div>
      </header>

      <div className="container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <h2>⚙️ Configuration</h2>

            {/* Reservoir Selection */}
            <div className="form-group">
              <label>Reservoir</label>
              <select name="reservoir_name" value={inputs.reservoir_name} onChange={handleChange}>
                {reservoirs.map(r => (
                  <option key={r.name} value={r.name}>{r.name}</option>
                ))}
              </select>
            </div>

            {/* Or Custom */}
            <div className="form-group">
              <label>Area (km²)</label>
              <input type="number" name="area_km2" value={inputs.area_km2} onChange={handleChange} />
            </div>

            {/* FPV Parameters */}
            <h3>📊 FPV Parameters</h3>
            <div className="form-group">
              <label>Coverage (%): {inputs.coverage}%</label>
              <input type="range" name="coverage" min="1" max="50" value={inputs.coverage} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Efficiency: {(inputs.efficiency * 100).toFixed(1)}%</label>
              <input type="range" name="efficiency" min="0.10" max="0.25" step="0.01" value={inputs.efficiency} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Performance Ratio: {inputs.pr.toFixed(2)}</label>
              <input type="range" name="pr" min="0.60" max="0.85" step="0.01" value={inputs.pr} onChange={handleChange} />
            </div>

            {/* Climate Parameters */}
            <h3>🌦️ Climate</h3>
            <div className="form-group">
              <label>Irradiance (kWh/m²/day): {inputs.avg_irradiance.toFixed(1)}</label>
              <input type="range" name="avg_irradiance" min="2" max="6" step="0.1" value={inputs.avg_irradiance} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Evaporation (mm/day): {inputs.avg_evaporation.toFixed(1)}</label>
              <input type="range" name="avg_evaporation" min="1" max="6" step="0.1" value={inputs.avg_evaporation} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label>Temperature (°C): {inputs.avg_temp}</label>
              <input type="range" name="avg_temp" min="15" max="40" step="1" value={inputs.avg_temp} onChange={handleChange} />
            </div>

            {/* Hydro Parameters */}
            <div className="form-group">
              <label>Head (m): {inputs.head_m}</label>
              <input type="number" name="head_m" value={inputs.head_m} onChange={handleChange} />
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {/* KPI Cards */}
          {results && (
            <div className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-icon sun">
                  <Sun size={24} />
                </div>
                <div className="kpi-content">
                  <h3>FPV Capacity</h3>
                  <p className="kpi-value">{results.fpv_capacity_mwp.toFixed(1)} MWp</p>
                  <span className="kpi-label">Coverage: {inputs.coverage}%</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon water">
                  <Droplets size={24} />
                </div>
                <div className="kpi-content">
                  <h3>Water Saved</h3>
                  <p className="kpi-value">{results.water_saved_million_m3.toFixed(2)}M m³</p>
                  <span className="kpi-label">Annual savings</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon energy">
                  <Zap size={24} />
                </div>
                <div className="kpi-content">
                  <h3>Extra Hydro</h3>
                  <p className="kpi-value">{results.extra_hydro_mwh_annual.toLocaleString(undefined, { maximumFractionDigits: 0 })} MWh</p>
                  <span className="kpi-label">Annual generation</span>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon co2">
                  <Leaf size={24} />
                </div>
                <div className="kpi-content">
                  <h3>CO₂ Avoided</h3>
                  <p className="kpi-value">{results.co2_avoided_tonnes.toLocaleString(undefined, { maximumFractionDigits: 0 })} tonnes</p>
                  <span className="kpi-label">Annual impact</span>
                </div>
              </div>
            </div>
          )}

          {/* Charts */}
          {results && (
            <div className="charts-section">
              <div className="chart-container">
                <h2>📈 Energy Mix</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={energyChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#80B1D3">
                      {energyChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-container">
                <h2>🌍 CO₂ Breakdown</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={co2ChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toLocaleString()}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {co2ChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Environmental Impact */}
          {results && (
            <div className="impact-section">
              <h2>🌍 Environmental Impact</h2>
              <div className="impact-grid">
                <div className="impact-card">
                  <h3>🌳 Trees Equivalent</h3>
                  <p>{results.trees_equivalent.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
                </div>
                <div className="impact-card">
                  <h3>🚗 Cars Offset</h3>
                  <p>{results.cars_offset.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
                </div>
                <div className="impact-card">
                  <h3>💧 Drinking Water</h3>
                  <p>{(results.water_saved_liters / 100).toLocaleString(undefined, { maximumFractionDigits: 0 })} people/year</p>
                </div>
              </div>
            </div>
          )}

          {/* Summary Table */}
          {results && (
            <div className="summary-section">
              <div className="summary-header">
                <h2>📋 Scenario Summary</h2>
                <button className="btn-download" onClick={downloadReport}>
                  <Download size={16} /> Download Report
                </button>
              </div>
              <div className="summary-table">
                <table>
                  <thead>
                    <tr>
                      <th>Parameter</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(results.summary).map(([key, value]) => (
                      <tr key={key}>
                        <td>{key}</td>
                        <td>{typeof value === 'number' ? value.toLocaleString() : value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {loading && <div className="loading">Computing...</div>}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;

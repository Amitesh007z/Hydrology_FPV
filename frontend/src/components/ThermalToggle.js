import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ThermalMap from './ThermalMap';
import { API_BASE, hasApiBase } from '../config/api';
import '../styles/ThermalToggle.css';

const ThermalToggle = () => {
  const [showThermal, setShowThermal] = useState(false);
  const [thermalData, setThermalData] = useState(null);
  const [legend, setLegend] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch thermal data when toggle is enabled
  useEffect(() => {
    if (showThermal && !thermalData) {
      fetchThermalData();
    }
  }, [showThermal]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchThermalData = async () => {
    if (!hasApiBase) {
      setError('API URL not configured. Set REACT_APP_API_URL in frontend environment variables.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [thermalRes, legendRes] = await Promise.all([
        axios.get(`${API_BASE}/thermal/data`),
        axios.get(`${API_BASE}/thermal/legend`)
      ]);
      
      setThermalData(thermalRes.data);
      setLegend(legendRes.data);
    } catch (err) {
      console.error('Error fetching thermal data:', err);
      setError('Failed to load thermal data');
      setShowThermal(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="thermal-toggle-container">
      <div className="thermal-toggle-header">
        <button 
          className={`thermal-toggle-btn ${showThermal ? 'active' : ''}`}
          onClick={() => setShowThermal(!showThermal)}
        >
          <span className="toggle-icon">🌡️</span>
          <span className="toggle-text">
            {showThermal ? 'Hide Thermal Map' : 'Show Thermal Map'}
          </span>
        </button>
      </div>

      {showThermal && (
        <div className="thermal-panel">
          {loading && (
            <div className="thermal-loading">
              <div className="spinner"></div>
              <p>Loading NASA thermal data...</p>
            </div>
          )}

          {error && (
            <div className="thermal-error">
              <p>{error}</p>
              <button onClick={() => { setShowThermal(false); setError(null); }}>
                Close
              </button>
            </div>
          )}

          {thermalData && legend && !loading && (
            <div className="thermal-content">
              <div className="thermal-map-wrapper">
                <ThermalMap thermalData={thermalData} legend={legend} />
              </div>

              <div className="thermal-legend">
                <h3>Temperature Legend (NASA POWER API)</h3>
                <div className="legend-items">
                  {legend.legend.map((item, idx) => (
                    <div key={idx} className="legend-item">
                      <div 
                        className="legend-color" 
                        style={{ backgroundColor: item.color }}
                      ></div>
                      <span className="legend-label">{item.label}</span>
                    </div>
                  ))}
                </div>
                <p className="legend-unit">Unit: {legend.unit}</p>
              </div>

              <div className="thermal-info-box">
                <h4>About Thermal Mapping</h4>
                <p>
                  This real-time thermal map shows surface temperature variations across India,
                  derived from NASA POWER API satellite data. Temperature data helps identify:
                </p>
                <ul>
                  <li>Optimal locations for FPV installations (cooler zones)</li>
                  <li>Regional climate patterns and desert hotspots</li>
                  <li>Seasonal temperature variations</li>
                  <li>Efficiency impact regions (higher temp = lower efficiency)</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ThermalToggle;

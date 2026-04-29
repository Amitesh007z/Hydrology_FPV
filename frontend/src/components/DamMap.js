import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import axios from 'axios';
import ThermalOverlay from './ThermalOverlay';
import { API_BASE, hasApiBase } from '../config/api';
import '../styles/DamMap.css';

const DamMap = ({ onSelectDam, selectedDam }) => {
  const [dams, setDams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterCapacity, setFilterCapacity] = useState('all');
  const [showThermal, setShowThermal] = useState(true); // DEFAULT ON
  const [thermalData, setThermalData] = useState(null);
  const [thermalLoading, setThermalLoading] = useState(false);

  useEffect(() => {
    fetchDams();
  }, []);

  const fetchDams = async () => {
    try {
      if (!hasApiBase) {
        setError('API URL not configured. Set REACT_APP_API_URL in frontend environment variables.');
        setLoading(false);
        return;
      }
      setLoading(true);
      const response = await axios.get(`${API_BASE}/dams`);
      if (response.data.dams) {
        setDams(response.data.dams);
      }
      setError(null);
    } catch (err) {
      setError('Failed to fetch dams data');
      console.error('Error fetching dams:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch thermal data when toggle is enabled
  useEffect(() => {
    if (showThermal && !thermalData) {
      fetchThermalData();
    }
  }, [showThermal]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchThermalData = async () => {
    setThermalLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/thermal/data`);
      setThermalData(response.data);
    } catch (err) {
      console.error('Error fetching thermal data:', err);
    } finally {
      setThermalLoading(false);
    }
  };

  const getMarkerColor = (capacity) => {
    if (capacity > 1000) return '#FF4444'; // Red - Major
    if (capacity > 200) return '#FF9933'; // Orange - Medium
    return '#4444FF'; // Blue - Small
  };

  const getMarkerSize = (capacity) => {
    if (capacity > 1000) return 15;
    if (capacity > 200) return 12;
    return 10;
  };

  const filteredDams = dams.filter(dam => {
    if (filterCapacity === 'major') return dam.capacity_mw > 1000;
    if (filterCapacity === 'medium') return dam.capacity_mw > 200 && dam.capacity_mw <= 1000;
    if (filterCapacity === 'small') return dam.capacity_mw <= 200;
    return true;
  });

  if (loading) {
    return (
      <div className="dam-map-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading dams data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dam-map-container">
      <div className="map-header">
        <h1>
         FPV Nexus - Multi-Dam India Map
        </h1>
        <p className="subtitle">
          {filteredDams.length} dams available • Click on a marker to analyze
        </p>
      </div>

      <div className="map-controls">
        <div className="capacity-filter">
          <label>Filter by Capacity:</label>
          <select value={filterCapacity} onChange={(e) => setFilterCapacity(e.target.value)}>
            <option value="all">All Dams ({dams.length})</option>
            <option value="major">Major (&gt;1000 MW) - {dams.filter(d => d.capacity_mw > 1000).length}</option>
            <option value="medium">Medium (200-1000 MW) - {dams.filter(d => d.capacity_mw > 200 && d.capacity_mw <= 1000).length}</option>
            <option value="small">Small (&lt;200 MW) - {dams.filter(d => d.capacity_mw <= 200).length}</option>
          </select>
        </div>

        <div className="thermal-toggle-btn-wrapper">
          <button 
            className={`thermal-btn ${showThermal ? 'active' : ''}`}
            onClick={() => setShowThermal(!showThermal)}
            disabled={thermalLoading}
          >
            <span className="thermal-icon">🌡️</span>
            {thermalLoading ? 'Loading...' : showThermal ? 'Hide Thermal Map' : 'Show Thermal Map'}
          </button>
        </div>

        <div className="legend">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#FF4444' }}></div>
            <span>Major (&gt;1000 MW)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#FF9933' }}></div>
            <span>Medium (200-1000 MW)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#4444FF' }}></div>
            <span>Small (&lt;200 MW)</span>
          </div>
        </div>
      </div>

      <div className="map-wrapper">
        {error && <div className="error-message">{error}</div>}
        
        <MapContainer center={[20.5937, 78.9629]} zoom={5} className="leaflet-container" style={{ height: '500px', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          
          <ThermalOverlay thermalData={thermalData} opacity={0.5} enabled={showThermal} />
          
          {filteredDams.map((dam) => (
            <CircleMarker
              key={dam.folder}
              center={[dam.latitude, dam.longitude]}
              radius={getMarkerSize(dam.capacity_mw)}
              color={getMarkerColor(dam.capacity_mw)}
              fillColor={getMarkerColor(dam.capacity_mw)}
              fillOpacity={0.7}
              weight={2}
              onClick={() => onSelectDam(dam.folder)}
            >
              <Popup>
                <div className="dam-popup">
                  <h3>{dam.name}</h3>
                  <p><strong>State:</strong> {dam.state}</p>
                  <p><strong>River:</strong> {dam.river}</p>
                  <p><strong>Capacity:</strong> {dam.capacity_mw} MW</p>
                  <p><strong>Area:</strong> {dam.area_km2} km²</p>
                  <p><strong>Head:</strong> {dam.head_m} m</p>
                  <button 
                    className="analyze-btn"
                    onClick={() => onSelectDam(dam.folder)}
                  >
                    Analyze FPV
                  </button>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="dam-list">
        <h2>Available Dams ({filteredDams.length})</h2>
        <div className="dam-grid">
          {filteredDams.map((dam) => (
            <div
              key={dam.folder}
              className={`dam-card ${selectedDam === dam.folder ? 'selected' : ''}`}
              onClick={() => onSelectDam(dam.folder)}
            >
              <div className="dam-card-header">
                <h3>{dam.name}</h3>
                <div className="capacity-badge" style={{ backgroundColor: getMarkerColor(dam.capacity_mw) }}>
                  {dam.capacity_mw} MW
                </div>
              </div>
              <div className="dam-card-info">
                <p><strong>{dam.state}</strong></p>
                <p>{dam.river}</p>
                <p className="area">{dam.area_km2} km² • {dam.head_m}m head</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DamMap;

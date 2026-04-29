import React from 'react';
import '../styles/ThermalMap.css';

const ThermalMap = ({ thermalData, legend }) => {
  if (!thermalData || !thermalData.points) {
    return <div className="thermal-loading">Loading thermal data...</div>;
  }

  // Convert thermal data to canvas heatmap
  const renderThermalHeatmap = () => {
    const canvasWidth = 400;
    const canvasHeight = 300;
    
    // Get temperature range
    const minTemp = thermalData.temperature_range.min;
    const maxTemp = thermalData.temperature_range.max;
    const tempRange = maxTemp - minTemp;

    // Create grid image data
    const imageData = new ImageData(canvasWidth, canvasHeight);
    const data = imageData.data;

    // Grid resolution
    const gridResX = 30;
    const gridResY = 24;

    // Fill with thermal data
    for (let py = 0; py < canvasHeight; py++) {
      for (let px = 0; px < canvasWidth; px++) {
        // Map pixel to grid cell
        const gridX = Math.floor((px / canvasWidth) * gridResX);
        const gridY = Math.floor((py / canvasHeight) * gridResY);
        
        // Find nearest temperature point
        let temp = minTemp;
        let minDist = Infinity;
        
        thermalData.points.forEach(point => {
          const pointGridX = ((point.lon - thermalData.bounds.west) / (thermalData.bounds.east - thermalData.bounds.west)) * gridResX;
          const pointGridY = ((thermalData.bounds.north - point.lat) / (thermalData.bounds.north - thermalData.bounds.south)) * gridResY;
          
          const dist = Math.sqrt(Math.pow(pointGridX - gridX, 2) + Math.pow(pointGridY - gridY, 2));
          if (dist < minDist) {
            minDist = dist;
            temp = point.temperature;
          }
        });

        // Convert temperature to color (0-1 range)
        const tempNormalized = (temp - minTemp) / (tempRange || 1);
        const color = temperatureToColor(tempNormalized);

        const pixelIndex = (py * canvasWidth + px) * 4;
        data[pixelIndex] = color[0];     // R
        data[pixelIndex + 1] = color[1]; // G
        data[pixelIndex + 2] = color[2]; // B
        data[pixelIndex + 3] = 150;      // Alpha
      }
    }

    return imageData;
  };

  const temperatureToColor = (normalized) => {
    // Blue -> Cyan -> Green -> Yellow -> Orange -> Red
    if (normalized < 0.16) {
      // Blue
      return [0, 0, Math.min(255, normalized * 1600)];
    } else if (normalized < 0.33) {
      // Cyan
      const t = (normalized - 0.16) / 0.17;
      return [0, Math.min(255, t * 255), 255];
    } else if (normalized < 0.5) {
      // Green
      const t = (normalized - 0.33) / 0.17;
      return [0, 255, Math.max(0, 255 - t * 255)];
    } else if (normalized < 0.66) {
      // Yellow
      const t = (normalized - 0.5) / 0.16;
      return [Math.min(255, t * 255), 255, 0];
    } else if (normalized < 0.83) {
      // Orange
      const t = (normalized - 0.66) / 0.17;
      return [255, Math.max(0, 255 - t * 255), 0];
    } else {
      // Red
      return [255, 0, 0];
    }
  };

  const drawHeatmap = (canvas) => {
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const imageData = renderThermalHeatmap();
    ctx.putImageData(imageData, 0, 0);
    
    // Draw grid overlay
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 0.5;
    const step = 50;
    for (let i = 0; i < canvas.width; i += step) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, canvas.height);
      ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += step) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(canvas.width, i);
      ctx.stroke();
    }
  };

  return (
    <div className="thermal-map-container">
      <canvas
        ref={drawHeatmap}
        width={400}
        height={300}
        className="thermal-canvas"
      />
      <div className="thermal-info">
        <p><strong>Thermal Range:</strong></p>
        <p>{thermalData.temperature_range.min}°C - {thermalData.temperature_range.max}°C</p>
        <p className="source">Source: {thermalData.source}</p>
      </div>
    </div>
  );
};

export default ThermalMap;

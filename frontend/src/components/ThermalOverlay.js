import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import indiaBoundary from '../data/indiaBoundary.json';

/**
 * ThermalOverlay Component
 * Creates smooth, professional-grade thermal heatmap visualization
 * using bilinear interpolation for realistic satellite thermal imagery appearance
 */
const ThermalOverlay = ({ thermalData, opacity = 0.6, enabled = true }) => {
  const map = useMap();
  const overlayRef = useRef(null);
  const objectUrlRef = useRef(null);
  const objectUrlIsBlobRef = useRef(false);
  const lastThermalDataRef = useRef(null);
  const renderTokenRef = useRef(0);

  useEffect(() => {
    const hasThermal =
      thermalData &&
      thermalData.points &&
      Array.isArray(thermalData.points) &&
      thermalData.points.length > 0;

    // Toggle OFF: remove layer but keep cached image URL for quick toggle ON.
    if (!enabled || !hasThermal) {
      if (overlayRef.current) {
        try {
          map.removeLayer(overlayRef.current);
        } catch (e) {
          // ignore removal errors
        }
        overlayRef.current = null;
      }
      return;
    }

    const bounds = [
      [thermalData.bounds.south, thermalData.bounds.west],
      [thermalData.bounds.north, thermalData.bounds.east],
    ];

    // If the layer already exists, just update opacity.
    if (overlayRef.current) {
      overlayRef.current.setOpacity(opacity);
      return;
    }

    // If we already rendered for the same thermalData object, re-add using cached image.
    if (lastThermalDataRef.current === thermalData && objectUrlRef.current) {
      const overlay = new L.ImageOverlay(objectUrlRef.current, bounds, {
        opacity: opacity,
        interactive: false,
        className: 'thermal-overlay-heatmap',
      });
      overlay.addTo(map);
      overlayRef.current = overlay;
      return;
    }

    // New thermalData: revoke previous cached URL.
    if (objectUrlRef.current && objectUrlIsBlobRef.current) {
      try {
        URL.revokeObjectURL(objectUrlRef.current);
      } catch (e) {
        // ignore revoke errors
      }
    }
    objectUrlRef.current = null;
    objectUrlIsBlobRef.current = false;
    lastThermalDataRef.current = null;

    renderTokenRef.current += 1;
    const token = renderTokenRef.current;
    let cancelled = false;

    const render = async () => {
      try {
        const canvas = await createSmoothThermalCanvas(thermalData, {
          shouldCancel: () => cancelled || token !== renderTokenRef.current,
        });
        if (!canvas) return;

        const { src, isBlobUrl } = await canvasToImageSource(canvas);
        if (!src) return;

        if (token !== renderTokenRef.current) {
          if (isBlobUrl) URL.revokeObjectURL(src);
          return;
        }

        objectUrlRef.current = src;
        objectUrlIsBlobRef.current = isBlobUrl;
        lastThermalDataRef.current = thermalData;

        const overlay = new L.ImageOverlay(src, bounds, {
          opacity: opacity,
          interactive: false,
          className: 'thermal-overlay-heatmap',
        });
        overlay.addTo(map);
        overlayRef.current = overlay;
      } catch (error) {
        console.error('Error creating thermal overlay:', error);
      }
    };

    // Kick off async render so the UI stays responsive.
    render();

    return () => {
      cancelled = true;
      // Invalidate any in-flight render.
      renderTokenRef.current += 1;
    };
  }, [enabled, thermalData, opacity, map]);

  useEffect(() => {
    return () => {
      if (overlayRef.current) {
        try {
          map.removeLayer(overlayRef.current);
        } catch (e) {
          // ignore removal errors
        }
      }
      overlayRef.current = null;

      if (objectUrlRef.current && objectUrlIsBlobRef.current) {
        try {
          URL.revokeObjectURL(objectUrlRef.current);
        } catch (e) {
          // ignore revoke errors
        }
      }
      objectUrlRef.current = null;
      objectUrlIsBlobRef.current = false;
    };
  }, [map]);

  return null;
};

const canvasToImageSource = async (canvas) => {
  // Prefer async Blob URLs to avoid blocking the main thread.
  if (typeof canvas.toBlob === 'function') {
    const result = await new Promise((resolve) => {
      canvas.toBlob(
        (blob) => {
          if (!blob) return resolve({ src: null, isBlobUrl: false });
          resolve({ src: URL.createObjectURL(blob), isBlobUrl: true });
        },
        'image/png',
        0.85
      );
    });
    return result;
  }

  // Fallback: data URL (cannot revoke).
  try {
    return { src: canvas.toDataURL('image/png', 0.85), isBlobUrl: false };
  } catch {
    return { src: null, isBlobUrl: false };
  }
};

const getIndiaBoundaryCoordinates = () => {
  const feature = indiaBoundary?.features?.[0];
  const geometry = feature?.geometry;
  if (!geometry) return [];

  if (geometry.type === 'Polygon' && Array.isArray(geometry.coordinates)) {
    return geometry.coordinates; // Array of rings
  }

  if (geometry.type === 'MultiPolygon' && Array.isArray(geometry.coordinates)) {
    return geometry.coordinates.flat(); // Flatten polygons -> rings
  }

  return [];
};

const applyIndiaMask = (ctx, canvas, bounds) => {
  const coords = getIndiaBoundaryCoordinates();
  if (!coords.length) return;

  const west = bounds.west;
  const east = bounds.east;
  const north = bounds.north;
  const south = bounds.south;
  const spanLon = east - west || 1;
  const spanLat = north - south || 1;

  ctx.save();
  ctx.globalCompositeOperation = 'destination-in';
  ctx.beginPath();

  coords.forEach((ring) => {
    if (!Array.isArray(ring) || ring.length < 3) return;
    ring.forEach(([lon, lat], index) => {
      const x = ((lon - west) / spanLon) * canvas.width;
      const y = ((north - lat) / spanLat) * canvas.height;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();
  });

  ctx.fillStyle = '#000';
  ctx.fill('evenodd');
  ctx.restore();
};

/**
 * Create a smooth thermal canvas without doing O(pixels * points) interpolation.
 * Strategy:
 * - Bin incoming points into a coarse grid by bounds
 * - Bilinearly interpolate that grid for each pixel
 * - Render in chunks so the UI stays responsive
 */
const createSmoothThermalCanvas = async (thermalData, { shouldCancel }) => {
  // Moderate resolution; Leaflet will scale it.
  const width = 520;
  const height = 390;

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d', { alpha: true });
  const imageData = ctx.createImageData(width, height);
  const out = imageData.data;

  const bounds = thermalData.bounds;
  const tempRange = thermalData.temperature_range || { min: 8, max: 48 };
  const fallbackTemp = (Number(tempRange.min) + Number(tempRange.max)) / 2 || 25;
  let minT = Number(tempRange.min ?? 8);
  let maxT = Number(tempRange.max ?? 48);

  const useGrid =
    thermalData &&
    thermalData.grid &&
    Array.isArray(thermalData.grid.lats) &&
    Array.isArray(thermalData.grid.lons) &&
    Array.isArray(thermalData.grid.data) &&
    thermalData.grid.data.length > 0;

  const denomW = width - 1;
  const denomH = height - 1;
  const totalPixels = width * height;
  const pixelsPerChunk = Math.max(2500, Math.floor(totalPixels / 24)); // ~24 chunks

  const yieldToUI = () =>
    new Promise((resolve) => {
      if (typeof requestAnimationFrame === 'function') {
        requestAnimationFrame(() => resolve());
      } else {
        setTimeout(() => resolve(), 0);
      }
    });

  if (useGrid) {
    // Prefer backend-provided grid for accurate geospatial mapping.
    const gridLats = thermalData.grid.lats;
    const gridLons = thermalData.grid.lons;
    const gridData = thermalData.grid.data; // gridData[lonIndex][latIndex]

    const nLon = gridLons.length;
    const nLat = gridLats.length;

    // Compute a neutral fallback from the grid in case there are NaNs.
    let sum = 0;
    let count = 0;
    const values = [];
    for (let xi = 0; xi < nLon; xi++) {
      const col = gridData[xi] || [];
      for (let yi = 0; yi < nLat; yi++) {
        const v = col[yi];
        if (typeof v === 'number' && Number.isFinite(v)) {
          sum += v;
          count += 1;
          values.push(v);
        }
      }
    }
    const gridFallback = count > 0 ? sum / count : fallbackTemp;

    // Robust scaling: avoid single outliers flattening the whole color map.
    if (values.length > 10) {
      values.sort((a, b) => a - b);
      const p05 = values[Math.floor(values.length * 0.05)];
      const p95 = values[Math.floor(values.length * 0.95)];
      if (Number.isFinite(p05) && Number.isFinite(p95) && p95 > p05) {
        minT = p05;
        maxT = p95;
      }
    }

    const gridDenomX = nLon - 1;
    const gridDenomY = nLat - 1;

    for (let start = 0; start < totalPixels; start += pixelsPerChunk) {
      if (shouldCancel && shouldCancel()) return null;

      const end = Math.min(start + pixelsPerChunk, totalPixels);
      for (let pixelIdx = start; pixelIdx < end; pixelIdx++) {
        const px = pixelIdx % width;
        const py = Math.floor(pixelIdx / width);

        // px increases west->east; py decreases north->south.
        const xFloat = (px / denomW) * gridDenomX;
        const yFloat = (1 - py / denomH) * gridDenomY;

        const x0 = Math.max(0, Math.min(gridDenomX, Math.floor(xFloat)));
        const y0 = Math.max(0, Math.min(gridDenomY, Math.floor(yFloat)));
        const x1 = Math.min(gridDenomX, x0 + 1);
        const y1 = Math.min(gridDenomY, y0 + 1);

        const tx = xFloat - x0;
        const ty = yFloat - y0;

        const t00raw = gridData[x0]?.[y0];
        const t10raw = gridData[x1]?.[y0];
        const t01raw = gridData[x0]?.[y1];
        const t11raw = gridData[x1]?.[y1];

        const t00 = Number.isFinite(t00raw) ? t00raw : gridFallback;
        const t10 = Number.isFinite(t10raw) ? t10raw : gridFallback;
        const t01 = Number.isFinite(t01raw) ? t01raw : gridFallback;
        const t11 = Number.isFinite(t11raw) ? t11raw : gridFallback;

        const top = t00 * (1 - tx) + t10 * tx;
        const bottom = t01 * (1 - tx) + t11 * tx;
        const tempValue = top * (1 - ty) + bottom * ty;

        const color = getTemperatureColorWithScale(tempValue, minT, maxT);
        const idx = pixelIdx * 4;
        out[idx] = color.r;
        out[idx + 1] = color.g;
        out[idx + 2] = color.b;
        out[idx + 3] = 200;
      }

      await yieldToUI();
    }

    ctx.putImageData(imageData, 0, 0);
    applyIndiaMask(ctx, canvas, bounds);
    return canvas;
  }

  // Fallback: bin points into a coarse grid, then bilinearly interpolate.
  const points = thermalData.points || [];
  const gridResX = 60;
  const gridResY = 45;

  const spanLon = bounds.east - bounds.west || 1;
  const spanLat = bounds.north - bounds.south || 1;

  const cellSums = new Float32Array(gridResX * gridResY);
  const cellCounts = new Uint32Array(gridResX * gridResY);

  for (let i = 0; i < points.length; i++) {
    const p = points[i];
    if (!p || !Number.isFinite(p.lat) || !Number.isFinite(p.lon) || !Number.isFinite(p.temperature)) continue;

    const gxRaw = ((p.lon - bounds.west) / spanLon) * (gridResX - 1);
    const gyRaw = ((bounds.north - p.lat) / spanLat) * (gridResY - 1);
    const gx = Math.max(0, Math.min(gridResX - 1, Math.floor(gxRaw)));
    const gy = Math.max(0, Math.min(gridResY - 1, Math.floor(gyRaw)));
    const idx = gy * gridResX + gx;
    cellSums[idx] += p.temperature;
    cellCounts[idx] += 1;
  }

  const cellTemps = new Float32Array(gridResX * gridResY);
  for (let i = 0; i < cellTemps.length; i++) {
    const count = cellCounts[i];
    cellTemps[i] = count > 0 ? cellSums[i] / count : fallbackTemp;
  }

  const gridDenomX = gridResX - 1;
  const gridDenomY = gridResY - 1;

  for (let start = 0; start < totalPixels; start += pixelsPerChunk) {
    if (shouldCancel && shouldCancel()) return null;

    const end = Math.min(start + pixelsPerChunk, totalPixels);
    for (let pixelIdx = start; pixelIdx < end; pixelIdx++) {
      const px = pixelIdx % width;
      const py = Math.floor(pixelIdx / width);

      const gx = (px / denomW) * gridDenomX;
      const gy = (py / denomH) * gridDenomY;

      const x0 = Math.max(0, Math.min(gridResX - 1, Math.floor(gx)));
      const y0 = Math.max(0, Math.min(gridResY - 1, Math.floor(gy)));
      const x1 = Math.min(gridResX - 1, x0 + 1);
      const y1 = Math.min(gridResY - 1, y0 + 1);

      const tx = gx - x0;
      const ty = gy - y0;

      const idx00 = y0 * gridResX + x0;
      const idx10 = y0 * gridResX + x1;
      const idx01 = y1 * gridResX + x0;
      const idx11 = y1 * gridResX + x1;

      const t00 = cellTemps[idx00];
      const t10 = cellTemps[idx10];
      const t01 = cellTemps[idx01];
      const t11 = cellTemps[idx11];

      const top = t00 * (1 - tx) + t10 * tx;
      const bottom = t01 * (1 - tx) + t11 * tx;
      const tempValue = top * (1 - ty) + bottom * ty;

      const color = getTemperatureColorWithScale(tempValue, minT, maxT);
      const idx = pixelIdx * 4;
      out[idx] = color.r;
      out[idx + 1] = color.g;
      out[idx + 2] = color.b;
      out[idx + 3] = 200;
    }

    await yieldToUI();
  }

  ctx.putImageData(imageData, 0, 0);
  applyIndiaMask(ctx, canvas, bounds);
  return canvas;
};

const getTemperatureColorWithScale = (temperature, minTemp, maxTemp) => {
  const span = (maxTemp - minTemp) || 1;
  const clamped = Math.max(minTemp, Math.min(maxTemp, temperature));

  // Normalize to 0-1 scale
  const normalized = (clamped - minTemp) / span;

  let r, g, b;

  // Seven-point smooth gradient matching professional thermal maps
  
  if (normalized <= 0.12) {
    // Deep Blue (8-12°C)
    r = 0;
    g = 0;
    b = Math.round(200 + 55 * normalized / 0.12);
  } 
  else if (normalized <= 0.24) {
    // Blue to Cyan (12-20°C)
    const t = (normalized - 0.12) / 0.12;
    r = 0;
    g = Math.round(150 * t);
    b = 255;
  } 
  else if (normalized <= 0.36) {
    // Cyan to Green (20-28°C)
    const t = (normalized - 0.24) / 0.12;
    r = 0;
    g = 255;
    b = Math.round(255 * (1 - t * 0.8));
  } 
  else if (normalized <= 0.48) {
    // Green to Yellow (28-36°C)
    const t = (normalized - 0.36) / 0.12;
    r = Math.round(255 * t);
    g = 255;
    b = 0;
  } 
  else if (normalized <= 0.64) {
    // Yellow to Orange (36-40°C)
    const t = (normalized - 0.48) / 0.16;
    r = 255;
    g = Math.round(255 * (1 - t * 0.4));
    b = 0;
  } 
  else if (normalized <= 0.80) {
    // Orange to Dark Red (40-44°C)
    const t = (normalized - 0.64) / 0.16;
    r = 255;
    g = Math.round(150 * (1 - t * 0.7));
    b = 0;
  } 
  else {
    // Deep Red (44-48°C)
    r = 255;
    g = Math.round(50 * (1 - (normalized - 0.80) / 0.20));
    b = 0;
  }

  return {
    r: Math.max(0, Math.min(255, r)),
    g: Math.max(0, Math.min(255, g)),
    b: Math.max(0, Math.min(255, b))
  };
};

export default ThermalOverlay;

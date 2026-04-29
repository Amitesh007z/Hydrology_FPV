const rawApiBase = process.env.REACT_APP_API_URL || '';
const normalizedApiBase = rawApiBase.replace(/\/+$/, '');

const isProduction = process.env.NODE_ENV === 'production';

// In dev, keep a localhost fallback. In production, require explicit env var.
export const API_BASE =
  normalizedApiBase || (isProduction ? '' : 'http://localhost:8001');

export const hasApiBase = Boolean(API_BASE);


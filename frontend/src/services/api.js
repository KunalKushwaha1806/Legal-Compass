/**
 * Legal Compass — Axios Service
 * All API calls go through this instance.
 * Vite proxies /api → http://localhost:3001/api (no CORS issues in dev).
 */
import axios from 'axios';

const rawApiUrl = import.meta.env.VITE_API_URL;
let resolvedBaseUrl = '/api';

if (rawApiUrl) {
  const trimmed = rawApiUrl.trim().replace(/\/$/, '');
  resolvedBaseUrl = trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
}

const api = axios.create({
  baseURL: resolvedBaseUrl,
  timeout: 90_000, // 90s — fine-tuned model on Colab can be slow
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('lc_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle token expiry globally — redirect to login (only for authenticated users with a token, never in guest/demo mode)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const isGuest = !!localStorage.getItem('lc_guest_user');
      if (!isGuest) {
        localStorage.removeItem('lc_token');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(err);
  }
);

export default api;

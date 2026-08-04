/**
 * Legal Compass — Axios Service
 * All API calls go through this instance.
 * Vite proxies /api → http://localhost:3001/api (no CORS issues in dev).
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 90_000, // 90s — fine-tuned model on Colab can be slow
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('lc_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle token expiry globally — redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('lc_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

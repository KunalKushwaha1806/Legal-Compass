/**
 * Legal Compass — Auth Context
 * Provides: user, token, loading, login(), register(), logout()
 */
import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const guestUser = localStorage.getItem('lc_guest_user');
    if (guestUser) {
      try {
        return JSON.parse(guestUser);
      } catch {}
    }
    return null;
  });

  const [loading, setLoading] = useState(() => {
    // Guest mode needs no token validation
    if (localStorage.getItem('lc_guest_user')) return false;
    // No token stored means unauthenticated
    if (!localStorage.getItem('lc_token')) return false;
    return true; // Verify existing token
  });

  // On mount: verify the stored JWT token if one exists (and not in guest mode)
  useEffect(() => {
    if (localStorage.getItem('lc_guest_user')) {
      setLoading(false);
      return;
    }

    const token = localStorage.getItem('lc_token');
    if (!token) {
      setLoading(false);
      return;
    }
    // Attach token and verify it's still valid
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    api.get('/auth/me')
      .then((res) => setUser(res.data.user))
      .catch(() => {
        // Token invalid or expired
        localStorage.removeItem('lc_token');
        delete api.defaults.headers.common['Authorization'];
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  /** POST /api/auth/login — returns user object */
  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { token, user: newUser } = res.data || {};
    if (!token || !newUser) {
      throw new Error(
        typeof res.data === 'string' && res.data.includes('<!doctype html>')
          ? 'Backend API not reachable (HTML returned). Check VITE_API_URL in Vercel settings.'
          : 'Invalid response from backend server.'
      );
    }
    localStorage.removeItem('lc_guest_user');
    localStorage.setItem('lc_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(newUser);
    return newUser;
  };

  /** POST /api/auth/register — returns user object */
  const register = async (name, email, password) => {
    const res = await api.post('/auth/register', { name, email, password });
    const { token, user: newUser } = res.data || {};
    if (!token || !newUser) {
      throw new Error(
        typeof res.data === 'string' && res.data.includes('<!doctype html>')
          ? 'Backend API not reachable (HTML returned). Check VITE_API_URL in Vercel settings.'
          : 'Invalid response from backend server.'
      );
    }
    localStorage.removeItem('lc_guest_user');
    localStorage.setItem('lc_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(newUser);
    return newUser;
  };

  /** Instant Guest / Demo Mode (no backend connection required) */
  const continueAsGuest = () => {
    const guest = { id: 'guest', name: 'Guest Explorer', email: 'guest@legalcompass.local', isGuest: true };
    localStorage.setItem('lc_guest_user', JSON.stringify(guest));
    localStorage.removeItem('lc_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(guest);
    return guest;
  };

  /** Clear token and user */
  const logout = () => {
    localStorage.removeItem('lc_token');
    localStorage.removeItem('lc_guest_user');
    localStorage.removeItem('lc_guest_history');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, continueAsGuest, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/** Hook — use inside any component */
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};

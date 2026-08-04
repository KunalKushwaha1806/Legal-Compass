/**
 * Legal Compass — Auth Context
 * Provides: user, token, loading, login(), register(), logout()
 */
import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true); // true until we verify the stored token

  // On mount: verify the stored JWT token
  useEffect(() => {
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
      })
      .finally(() => setLoading(false));
  }, []);

  /** POST /api/auth/login — returns user object */
  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { token, user: newUser } = res.data;
    localStorage.setItem('lc_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(newUser);
    return newUser;
  };

  /** POST /api/auth/register — returns user object */
  const register = async (name, email, password) => {
    const res = await api.post('/auth/register', { name, email, password });
    const { token, user: newUser } = res.data;
    localStorage.setItem('lc_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(newUser);
    return newUser;
  };

  /** Clear token and user */
  const logout = () => {
    localStorage.removeItem('lc_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
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

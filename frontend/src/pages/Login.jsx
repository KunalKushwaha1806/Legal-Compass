/**
 * Legal Compass — Login Page
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login, continueAsGuest } = useAuth();
  const navigate  = useNavigate();

  const [form,    setForm]    = useState({ email: '', password: '' });
  const [error,   setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email.trim() || !form.password) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await login(form.email, form.password);
      navigate('/', { replace: true });
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (!err.response) {
        setError('Cannot reach backend server. Make sure the Node backend is running locally, or click "Explore in Demo Mode" below.');
      } else if (err.response.status === 404 || err.response.status === 405 || typeof err.response.data === 'string') {
        setError('Backend API not found on this domain. If hosting on Vercel, set VITE_API_URL to your deployed backend, or use Demo Mode below.');
      } else {
        setError(err.message || 'Login failed. Check your credentials and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Background orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      <div className="auth-page">
        <div className="auth-card">
          {/* Logo */}
          <div className="auth-logo">
            <div className="auth-logo-icon">⚖️</div>
            <div className="auth-logo-text">
              Legal<span>Compass</span>
            </div>
          </div>

          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to your legal assistant</p>

          {/* Global error */}
          {error && <div className="global-error">{error}</div>}

          <form onSubmit={handleSubmit} noValidate>
            <div className="form-group">
              <label className="form-label" htmlFor="login-email">Email Address</label>
              <input
                id="login-email"
                className="form-input"
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="login-password">Password</label>
              <input
                id="login-password"
                className="form-input"
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              id="login-submit"
              disabled={loading}
            >
              {loading ? (
                <><span className="spinner" /> Signing in…</>
              ) : (
                'Sign In →'
              )}
            </button>

            <div className="auth-divider">or explore right now</div>

            <button
              type="button"
              className="btn-demo"
              onClick={() => {
                continueAsGuest();
                navigate('/', { replace: true });
              }}
            >
              ⚡ Explore in Demo / Guest Mode
            </button>
          </form>

          <div className="auth-footer">
            Don't have an account?{' '}
            <Link to="/register">Create one</Link>
          </div>

          <div style={{
            marginTop: '20px', paddingTop: '16px',
            borderTop: '1px solid var(--border)',
            fontSize: '0.75rem', color: 'var(--text-faint)', textAlign: 'center',
          }}>
            ⚠️ For informational use only. Not legal advice.
          </div>
        </div>
      </div>
    </>
  );
}

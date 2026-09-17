/**
 * Legal Compass — Register Page
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { register, continueAsGuest } = useAuth();
  const navigate     = useNavigate();

  const [form, setForm] = useState({
    name: '', email: '', password: '', confirmPassword: '',
  });
  const [error,   setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { name, email, password, confirmPassword } = form;

    if (!name.trim() || !email.trim() || !password) {
      setError('Please fill in all fields.');
      return;
    }
    if (name.trim().length < 2) {
      setError('Name must be at least 2 characters.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await register(name.trim(), email.trim(), password);
      navigate('/', { replace: true });
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (!err.response) {
        setError('Cannot reach backend server. Make sure the Node backend is running locally, or click "Explore in Demo Mode" below.');
      } else if (err.response.status === 404 || err.response.status === 405 || typeof err.response.data === 'string') {
        setError('Backend API not found on this domain. If hosting on Vercel, set VITE_API_URL to your deployed backend, or use Demo Mode below.');
      } else {
        setError(err.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
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

          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Join thousands getting legal clarity</p>

          {error && <div className="global-error">{error}</div>}

          <form onSubmit={handleSubmit} noValidate>
            <div className="form-group">
              <label className="form-label" htmlFor="reg-name">Full Name</label>
              <input
                id="reg-name"
                className="form-input"
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="Kunal Kushwaha"
                autoComplete="name"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="reg-email">Email Address</label>
              <input
                id="reg-email"
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
              <label className="form-label" htmlFor="reg-password">Password</label>
              <input
                id="reg-password"
                className="form-input"
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Min. 6 characters"
                autoComplete="new-password"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="reg-confirm">Confirm Password</label>
              <input
                id="reg-confirm"
                className="form-input"
                type="password"
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                placeholder="Repeat password"
                autoComplete="new-password"
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              id="register-submit"
              disabled={loading}
            >
              {loading ? (
                <><span className="spinner" /> Creating account…</>
              ) : (
                'Create Account →'
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
            Already have an account?{' '}
            <Link to="/login">Sign in</Link>
          </div>

          <div style={{
            marginTop: '20px', paddingTop: '16px',
            borderTop: '1px solid var(--border)',
            fontSize: '0.75rem', color: 'var(--text-faint)', textAlign: 'center',
          }}>
            ⚠️ For informational use only. Not legal advice.<br />
            Free legal aid: <a
              href="https://nalsa.gov.in"
              target="_blank"
              rel="noreferrer"
              style={{ color: 'var(--gold)' }}
            >NALSA</a>
          </div>
        </div>
      </div>
    </>
  );
}

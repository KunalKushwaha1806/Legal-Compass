/**
 * Legal Compass — Top Navigation Bar
 * Shows: logo, model status, username, logout button.
 */
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ apiOnline = false }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      {/* Left: logo + status */}
      <div className="navbar-left">
        <div className="navbar-title">⚖️ Legal<span style={{ color: 'var(--gold)' }}>Compass</span></div>
        <div className="navbar-status">
          <span className="status-dot" />
          {apiOnline ? 'AI Model Online' : 'AI Model Connecting…'}
        </div>
      </div>

      {/* Right: user + logout */}
      <div className="navbar-right">
        {user && (
          <div className="navbar-user">
            Hey, <strong>{user.name.split(' ')[0]}</strong>
            {user.isGuest && (
              <span style={{
                fontSize: '0.72rem',
                background: 'rgba(245,158,11,0.16)',
                color: 'var(--gold-light)',
                padding: '2px 8px',
                borderRadius: '12px',
                marginLeft: '8px',
                border: '1px solid rgba(245,158,11,0.3)',
                fontWeight: 600
              }}>
                Demo Mode
              </span>
            )}
          </div>
        )}
        <button className="btn-logout" onClick={handleLogout}>
          Sign Out
        </button>
      </div>
    </nav>
  );
}

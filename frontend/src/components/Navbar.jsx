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
          </div>
        )}
        <button className="btn-logout" onClick={handleLogout}>
          Sign Out
        </button>
      </div>
    </nav>
  );
}

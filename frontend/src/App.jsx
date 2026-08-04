/**
 * Legal Compass — App Router
 * Protected routes redirect to /login if not authenticated.
 * Public routes redirect to / if already authenticated.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login    from './pages/Login';
import Register from './pages/Register';
import Chat     from './pages/Chat';

/** Redirect unauthenticated users to login */
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <AppLoader />;
  return user ? children : <Navigate to="/login" replace />;
}

/** Redirect logged-in users away from auth pages */
function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <AppLoader />;
  return !user ? children : <Navigate to="/" replace />;
}

/** Full-screen loading screen shown while verifying stored token */
function AppLoader() {
  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      flexDirection: 'column', gap: 18,
      background: 'var(--bg)',
    }}>
      <div style={{
        width: 52, height: 52,
        background: 'linear-gradient(135deg, var(--indigo), var(--gold))',
        borderRadius: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '1.8rem',
        boxShadow: '0 0 30px var(--indigo-glow)',
        animation: 'spin 1.8s linear infinite',
      }}>
        ⚖️
      </div>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        Loading Legal Compass…
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Protected */}
        <Route
          path="/"
          element={<ProtectedRoute><Chat /></ProtectedRoute>}
        />

        {/* Public */}
        <Route
          path="/login"
          element={<PublicRoute><Login /></PublicRoute>}
        />
        <Route
          path="/register"
          element={<PublicRoute><Register /></PublicRoute>}
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

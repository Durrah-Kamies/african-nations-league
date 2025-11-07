// App.js
// NOTE: App shell for the React client. Sets up router, nav, routes, and a tiny auth guard.
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import './style.css';
import HomePage from './HomePage';
import RegisterPage from './RegisterPage';
import BracketPage from './BracketPage';
import StandingsPage from './StandingsPage';
import DashboardPage from './DashboardPage';
import MatchPage from './MatchPage';
import LoginPage from './LoginPage';
import TeamAnalyticsPage from './TeamAnalyticsPage';

function App() {
  // Render the main layout: top nav, routed content, and footer
  return (
    <Router>
      <nav className="navbar">{/* Simple top navigation across pages */}
        <div className="nav-container">
          <div className="nav-logo">
            <i className="fas fa-futbol"></i>
            <span>African Nations League</span>
          </div>
          <div className="nav-menu">
            <Link to="/home" className="nav-link">Home</Link>
            <Link to="/tournament" className="nav-link">Tournament</Link>
            <Link to="/standings" className="nav-link">Standings</Link>
            <Link to="/analytics" className="nav-link">Analytics</Link>
            <Link to="/register" className="nav-link">Register</Link>
            <Link to="/admin" className="nav-link">Admin</Link>
            <button
              type="button"
              className="nav-link"
              onClick={() => { try { window.localStorage.removeItem('authed'); } catch(_) {}; window.location.href = '/'; }}
              style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>
      <main>{/* Route table drives which page renders */}
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/tournament" element={<BracketPage />} />
          <Route path="/standings" element={<StandingsPage />} />
          <Route path="/analytics" element={<TeamAnalyticsPage />} />
          <Route path="/admin" element={<RequireAuth><DashboardPage /></RequireAuth>} />
          <Route path="/match/:matchId" element={<MatchPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer>
        <div className="footer-content">
          <p>&copy; 2025 African Nations League. All rights reserved.</p>
          <p>Built with passion for African football</p>
        </div>
      </footer>
    </Router>
  );
}

export default App;

function RequireAuth({ children }) {
  // Minimal client-side check stored in localStorage (demo only)
  const authed = typeof window !== 'undefined' && window.localStorage.getItem('authed') === '1';
  if (!authed) {
    try { window.localStorage.setItem('redirectTo', window.location.pathname); } catch(_) {}
    return <Navigate to="/" replace />;
  }
  return children;
}


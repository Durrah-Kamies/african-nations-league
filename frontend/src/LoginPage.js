import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
// LoginPage.js
// NOTE: Minimal demo login. Stores a simple auth flag in localStorage.

const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // If already authed, send user to home
    if (window.localStorage.getItem('authed') === '1') {
      navigate('/home', { replace: true });
    }
  }, [navigate]);

  async function handleSubmit(e) {
    // Fake auth for demo: accept admin@anl.com / admin123
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      // Minimal client-side check for demo purposes.
      // Replace with real auth when backend is ready.
      if (email.trim().toLowerCase() === 'admin@anl.com' && password === 'admin123') {
        window.localStorage.setItem('authed', '1');
        navigate('/home');
        return;
      }
      setError('Invalid credentials. Try admin@anl.com / admin123 or browse as visitor.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="form-container" style={{ maxWidth: 520 }}>
      <div className="text-center" style={{ marginBottom: '1rem' }}>
        <div className="avatar" style={{
          width: 64,
          height: 64,
          borderRadius: '50%',
          margin: '0 auto 0.75rem',
          background: 'linear-gradient(135deg, #22c55e, #0ea5e9)',
          display: 'grid',
          placeItems: 'center',
          color: 'white'
        }}>
          <i className="fas fa-trophy"></i>
        </div>
        <h1 style={{ marginBottom: 4 }}>African Nations League</h1>
        <p className="text-muted">Tournament Management System</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="info-box" style={{
          background: '#f5f7fb',
          borderRadius: 8,
          padding: '0.9rem 1rem',
          margin: '0.5rem 0 1rem'
        }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Access Levels:</div>
          <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
            <li><strong>Administrator:</strong> admin@anl.com / admin123</li>
            <li><strong>Federation Rep:</strong> Register a team first</li>
            <li><strong>Visitor:</strong> Browse without login</li>
          </ul>
        </div>

        {error && (
          <div className="error-message" style={{ marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={submitting}>
          {submitting ? 'Signing In…' : 'Sign In'}
        </button>
      </form>

      <div className="text-center" style={{ marginTop: '0.9rem' }}>
        <Link to="/register" className="link" style={{ marginRight: 16 }}>Register Your Team</Link>
        <span style={{ color: '#94a3b8' }}>|</span>
        <Link to="/tournament" className="link" style={{ marginLeft: 16 }}>Browse as Visitor</Link>
      </div>
    </div>
  );
};

export default LoginPage;

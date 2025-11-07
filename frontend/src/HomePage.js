import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
// HomePage.js
// NOTE: Public landing page. Shows hero, features, and quick stats from the API.

const HomePage = () => {
  const [teamsCount, setTeamsCount] = useState(null);

  useEffect(() => {
    // Load number of registered teams for the hero stats
    fetch('/api/teams')
      .then(res => res.json())
      .then(data => setTeamsCount(Array.isArray(data) ? data.length : 0))
      .catch(() => setTeamsCount(0));
  }, []);

  return (
    <>
      <section className="hero">{/* Big intro section with CTA buttons */}
        <div className="hero-content">
          <h1>African Nations League</h1>
          <p className="hero-subtitle">Experience the Future of African Football</p>
          <p className="hero-stats">
            {teamsCount === null ? '…' : teamsCount} Teams Registered
          </p>
          <div className="hero-buttons">
            <Link to="/register" className="btn btn-primary">
              <i className="fas fa-plus-circle"></i> Register Your Team
            </Link>
            <Link to="/tournament" className="btn btn-secondary">
              <i className="fas fa-trophy"></i> View Tournament
            </Link>
          </div>
        </div>
      </section>
      <section className="features">{/* Highlights key app features */}
        <div className="container">
          <h2>Tournament Features</h2>
          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-robot"></i>
              </div>
              <h3>AI-Powered Simulation</h3>
              <p>Realistic match commentary and intelligent player performance simulation</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-brackets-curly"></i>
              </div>
              <h3>Live Tournament Bracket</h3>
              <p>Interactive bracket system tracking every match from quarter-finals to final</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <h3>Advanced Statistics</h3>
              <p>Comprehensive player ratings, goal scorer rankings, and team analytics</p>
            </div>
          </div>
        </div>
      </section>
      <section className="cta-section">{/* Simple call-to-action */}
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Compete?</h2>
            <p>Join the inaugural African Nations League and showcase your football prowess</p>
            <Link to="/register" className="btn btn-large">
              <i className="fas fa-flag"></i> Register Your National Team
            </Link>
          </div>
        </div>
      </section>
    </>
  );
};

export default HomePage;

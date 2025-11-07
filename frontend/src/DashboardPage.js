import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
// DashboardPage.js
// NOTE: Admin dashboard for managing tournament: view teams/matches, create/reset bracket, and trigger simulations.

const DashboardPage = () => {
  const [teams, setTeams] = useState(null);         // Teams list
  const [matches, setMatches] = useState(null);     // Matches list
  const [loading, setLoading] = useState(true);     // Page-level loading flag
  const [error, setError] = useState('');           // Displayable error
  const [creating, setCreating] = useState(false);  // Create bracket busy flag
  const [resetting, setResetting] = useState(false);// Reset busy flag

  async function loadData() {
    // Fetch teams and matches together for faster initial render
    setLoading(true);
    setError('');
    try {
      const [tRes, mRes] = await Promise.all([
        fetch('/api/teams'),
        fetch('/api/matches')
      ]);
      const [tData, mData] = await Promise.all([tRes.json(), mRes.json()]);
      setTeams(Array.isArray(tData) ? tData : []);
      setMatches(Array.isArray(mData) ? mData : []);
    } catch (e) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadData(); }, []);

  const completedCount = (matches || []).filter(m => m.status === 'completed').length; // Simple KPIs
  const pendingCount = (matches || []).filter(m => m.status === 'scheduled').length;

  async function createTournament() {
    // Creates QF matches (8 teams => 4 QFs) and clears previous matches
    if (!teams || teams.length < 8) return;
    setCreating(true);
    try {
      const res = await fetch('/api/admin/create_tournament', { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.error || 'Failed to create tournament');
      await loadData();
      alert('Tournament bracket created successfully!');
    } catch (e) {
      alert(e.message);
    } finally {
      setCreating(false);
    }
  }

  async function resetTournament() {
    // Deletes all matches to start fresh
    if (!window.confirm('Are you sure you want to reset the entire tournament? This will delete all matches.')) return;
    setResetting(true);
    try {
      const res = await fetch('/api/admin/reset_tournament', { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.error || 'Failed to reset tournament');
      await loadData();
      alert('Tournament reset successfully!');
    } catch (e) {
      alert(e.message);
    } finally {
      setResetting(false);
    }
  }

  async function simulateMatch(matchId) {
    // Quick sim: no detailed events/commentary (fast)
    if (!window.confirm('Simulate this match quickly without detailed commentary?')) return;
    try {
      const res = await fetch(`/simulate_match/${matchId}`);
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.error || 'Simulation failed');
      await loadData();
      alert('Match simulated successfully!');
    } catch (e) {
      alert(e.message);
    }
  }

  async function playMatch(matchId) {
    // Full play: detailed timeline + optional AI commentary (slower)
    if (!window.confirm('Play this match with detailed AI commentary? This may take a moment.')) return;
    try {
      const res = await fetch(`/play_match/${matchId}`);
      const data = await res.json();
      if (!res.ok || data.success === false) throw new Error(data.error || 'Play failed');
      await loadData();
      alert('Match played successfully!');
    } catch (e) {
      alert(e.message);
    }
  }

  return (
    <div className="dashboard-container">{/* Page wrapper */}
      <h1>Tournament Administrator Dashboard</h1>

      {/* Statistics */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-number">{teams ? teams.length : 0}</div>
          <div className="stat-label">Teams Registered</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{matches ? matches.length : 0}</div>
          <div className="stat-label">Total Matches</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{completedCount}</div>
          <div className="stat-label">Matches Completed</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{pendingCount}</div>
          <div className="stat-label">Matches Pending</div>
        </div>
      </div>

      {/* Tournament Management */}
      <div className="admin-actions mb-2">
        <h2>Tournament Management</h2>
        <div className="action-buttons">
          <button className="btn btn-primary" onClick={createTournament} disabled={!teams || teams.length < 8 || creating}>
            <i className="fas fa-plus-circle"></i> {creating ? 'Creating…' : 'Create Tournament Bracket'}
          </button>{' '}
          <button className="btn btn-secondary" onClick={resetTournament} disabled={resetting}>
            <i className="fas fa-redo"></i> {resetting ? 'Resetting…' : 'Reset Tournament'}
          </button>{' '}
          <Link to="/tournament" className="btn btn-secondary">
            <i className="fas fa-brackets-curly"></i> View Bracket
          </Link>
        </div>
        <p className="mt-1"><small>Note: You need exactly 8 teams to create a tournament.</small></p>
      </div>

      {/* Errors */}
      {error && (
        <div className="error-message" style={{ marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {/* Teams Section */}
      <div className="teams-section mb-2">
        <h2>Registered Teams</h2>
        <div className="teams-grid" id="teams-grid">
          {loading ? (
            <div className="loading-section">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Loading teams...</p>
            </div>
          ) : teams && teams.length > 0 ? (
            teams.map(team => (
              <div className="team-card" key={team.id}>
                <h3>{team.country}</h3>
                <p><strong>Manager:</strong> {team.manager}</p>
                <p><strong>Representative:</strong> {team.representative}</p>
                <p className="team-rating">Rating: {team.rating}/100</p>
                <p><small>Registered: {new Date(team.registered_at).toLocaleDateString()}</small></p>
              </div>
            ))
          ) : (
            <div className="text-center" style={{ gridColumn: '1 / -1', padding: '2rem' }}>
              <i className="fas fa-users fa-3x" style={{ color: '#ccc', marginBottom: '1rem' }}></i>
              <h3>No Teams Registered</h3>
              <p>Register teams to start the tournament.</p>
              <Link to="/register" className="btn btn-primary">
                <i className="fas fa-plus-circle"></i> Register First Team
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Matches Section */}
      <div className="matches-section">
        <h2>Tournament Matches</h2>
        <div className="matches-grid" id="matches-grid">
          {loading ? (
            <div className="loading-section">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Loading matches...</p>
            </div>
          ) : matches && matches.length > 0 ? (
            matches.map(match => (
              <div className="match-card" key={match.id}>
                <h3>{match.team1.country} vs {match.team2.country}</h3>
                <p><strong>Round:</strong> {match.round}</p>
                <p><strong>Status:</strong> <span className={`match-status ${match.status}`}>{match.status}</span></p>
                {match.status === 'completed' && match.result ? (
                  <>
                    <p><strong>Score:</strong> {match.result.score}</p>
                    <p><strong>Winner:</strong> {match.result.winner}</p>
                  </>
                ) : null}
                <div className="mt-1">
                  <Link to={`/match/${match.id}`} className="btn btn-sm">View Details</Link>{' '}
                  {match.status === 'scheduled' && (
                    <>
                      <button onClick={() => simulateMatch(match.id)} className="btn btn-sm btn-secondary">
                        <i className="fas fa-bolt"></i> Simulate
                      </button>{' '}
                      <button onClick={() => playMatch(match.id)} className="btn btn-sm btn-primary">
                        <i className="fas fa-play"></i> Play
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center" style={{ gridColumn: '1 / -1', padding: '2rem' }}>
              <i className="fas fa-futbol fa-3x" style={{ color: '#ccc', marginBottom: '1rem' }}></i>
              <h3>No Matches Created</h3>
              <p>Create a tournament to generate matches.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

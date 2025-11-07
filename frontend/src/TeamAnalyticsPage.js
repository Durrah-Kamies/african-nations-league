import React, { useEffect, useMemo, useState } from 'react';
import GoBackButton from './GoBackButton';
// TeamAnalyticsPage.js
// NOTE: Pulls aggregated analytics for a selected team from the backend.

const TeamAnalyticsPage = () => {
  const [teams, setTeams] = useState([]);
  const [selected, setSelected] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch team list for the select dropdown
    fetch('/api/teams')
      .then(r => r.json())
      .then(d => setTeams(Array.isArray(d) ? d : []))
      .catch(() => setTeams([]));
  }, []);

  async function loadAnalytics(country) {
    // Request server-side aggregation for the chosen country
    if (!country) return;
    setLoading(true);
    setError('');
    setData(null);
    try {
      const res = await fetch(`/api/team_analytics/${encodeURIComponent(country)}`);
      const json = await res.json();
      if (!res.ok || json.error) throw new Error(json.error || 'Failed to load analytics');
      setData(json);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const topScorers = useMemo(() => data?.top_scorers || [], [data]);
  const vsOpponents = useMemo(() => data?.record_by_opponent || [], [data]);
  const summary = data?.summary; // Quick stats card data

  return (
    <div className="dashboard-container">{/* Wrapper + back button */}
      <GoBackButton fallback="/home" />
      <h1>Team Performance Analytics</h1>
      <p className="mb-2">Review match performance, top scorers, and record vs opponents.</p>

      <div className="form-container" style={{ marginTop: 0 }}>{/* Team select + load */}
        <div className="form-group">
          <label htmlFor="team">Select Team</label>
          <select id="team" value={selected} onChange={e => setSelected(e.target.value)}>
            <option value="">Choose a team…</option>
            {teams.map(t => (
              <option key={t.id} value={t.country}>{t.country}</option>
            ))}
          </select>
        </div>
        <button className="btn btn-primary" onClick={() => loadAnalytics(selected)} disabled={!selected || loading}>
          {loading ? 'Loading…' : 'View Analytics'}
        </button>
      </div>

      {error && (
        <div className="error-message" style={{ marginTop: '1rem' }}>{error}</div>
      )}

      {data && (
        <>
          <div className="dashboard-stats">{/* Summary cards */}
            <div className="stat-card">
              <div className="stat-number">{summary.played}</div>
              <div className="stat-label">Matches Played</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{summary.wins}</div>
              <div className="stat-label">Wins</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{summary.losses}</div>
              <div className="stat-label">Losses</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{summary.goals_for}</div>
              <div className="stat-label">Goals For</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{summary.goals_against}</div>
              <div className="stat-label">Goals Against</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{summary.goal_difference}</div>
              <div className="stat-label">Goal Difference</div>
            </div>
          </div>

          <div className="matches-section">{/* Recent form chips */}
            <h2>Recent Form</h2>
            <div className="text-center" style={{ margin: '0.5rem 0 1rem' }}>
              {summary.recent_form.length === 0 ? (
                <span>No recent matches</span>
              ) : (
                summary.recent_form.map((r, i) => (
                  <span key={i} className="match-status" style={{ marginRight: 8, background: r === 'W' ? '#22c55e' : '#ef4444', color: '#fff' }}>{r}</span>
                ))
              )}
            </div>
          </div>

          <div className="matches-section">
            <h2>Top Scorers</h2>
            <div className="standings-table">
              <div className="table-header">
                <div className="table-row">
                  <div className="rank">#</div>
                  <div className="player-name">Player</div>
                  <div className="goals">Goals</div>
                </div>
              </div>
              <div>
                {topScorers.length === 0 ? (
                  <div className="table-row"><div style={{ gridColumn: '1 / -1' }}>No scorers yet.</div></div>
                ) : (
                  topScorers.map((s, idx) => (
                    <div className="table-row" key={s.player+idx} style={{ gridTemplateColumns: '60px 1fr 120px' }}>
                      <div className="rank">{idx + 1}</div>
                      <div className="player-name">{s.player}</div>
                      <div className="goals">{s.goals}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="matches-section">
            <h2>Record vs Opponents</h2>
            <div className="standings-table">
              <div className="table-header">
                <div className="table-row">
                  <div className="player-name">Opponent</div>
                  <div className="matches">P</div>
                  <div className="goals">W</div>
                  <div className="goals">L</div>
                  <div className="goals">GF</div>
                  <div className="goals">GA</div>
                </div>
              </div>
              <div>
                {vsOpponents.length === 0 ? (
                  <div className="table-row"><div style={{ gridColumn: '1 / -1' }}>No opponent data.</div></div>
                ) : (
                  vsOpponents.map((o, idx) => (
                    <div className="table-row" key={o.opponent+idx} style={{ gridTemplateColumns: '2fr 60px 60px 60px 60px 60px' }}>
                      <div className="player-name">{o.opponent}</div>
                      <div className="matches">{o.played}</div>
                      <div className="goals">{o.wins}</div>
                      <div className="goals">{o.losses}</div>
                      <div className="goals">{o.goals_for}</div>
                      <div className="goals">{o.goals_against}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TeamAnalyticsPage;

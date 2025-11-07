import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
// StandingsPage.js
// NOTE: Golden Boot leaderboard computed from match goal_scorers across all matches.

const StandingsPage = () => {
  const [matches, setMatches] = useState(null);
  const [error, setError] = useState(null);

  // Load all matches once and compute scorers client-side
  useEffect(() => {
    fetch('/api/matches')
      .then(res => res.json())
      .then(data => setMatches(Array.isArray(data) ? data : []))
      .catch(err => setError(err?.message || 'Failed to load standings'));
  }, []);

  // Memoize goal scorers computation to avoid re-computation on every render
  const goalScorers = useMemo(() => {
    // Aggregate goals per player across all matches
    const scorerMap = new Map();
    if (!Array.isArray(matches)) return [];

    for (const match of matches) {
      const events = match?.result?.goal_scorers || [];
      for (const goal of events) {
        const key = goal.player + '|' + goal.team;
        const prev = scorerMap.get(key) || { player: goal.player, team: goal.team, goals: 0, matchesSet: new Set() };
        prev.goals += 1;
        prev.matchesSet.add(match.id);
        scorerMap.set(key, prev);
      }
    }

    return Array.from(scorerMap.values())
      .map(s => ({ player: s.player, team: s.team, goals: s.goals, matches: (s.matchesSet ? s.matchesSet.size : 0) }))
      .sort((a, b) => {
        if (b.goals !== a.goals) return b.goals - a.goals;
        if (a.matches !== b.matches) return a.matches - b.matches;
        return a.player.localeCompare(b.player);
      });
  }, [matches]);

  return (
    <div className="standings-container">
      <h1>Golden Boot Standings</h1>
      <p className="text-center mb-2">Top goal scorers in the African Nations League</p>

      {!matches && !error && (
        <div className="loading-section">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading standings...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading Standings</h3>
          <p>{error}</p>
        </div>
      )}

      <div className="standings-table">
        <div className="table-header">
          <div className="table-row">
            <div className="rank">#</div>
            <div className="player-name">Player</div>
            <div className="team-name">Team</div>
            <div className="goals">Goals</div>
            <div className="matches">Matches</div>
          </div>
        </div>
        <div id="standings-content">
          {goalScorers.length > 0 ? (
            goalScorers.map((scorer, idx) => (
              <div className="table-row" key={scorer.player + scorer.team}>
                <div className="rank">{idx + 1}</div>
                <div className="player-name">{scorer.player}</div>
                <div className="team-name">{scorer.team}</div>
                <div className="goals">{scorer.goals} ⚽</div>
                <div className="matches">{scorer.matches}</div>
              </div>
            ))
          ) : (
            <div className="table-row text-center">
              <div style={{ gridColumn: '1 / -1', padding: '2rem', color: '#666' }}>
                <i className="fas fa-info-circle"></i>
                <p>No goals have been scored yet. Matches need to be played to see standings.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="text-center mt-2">
        <Link to="/tournament" className="btn btn-secondary">
          <i className="fas fa-brackets-curly"></i> View Tournament Bracket
        </Link>
      </div>
    </div>
  );
};

export default StandingsPage;

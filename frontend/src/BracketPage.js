import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
// BracketPage.js
// NOTE: Displays the bracket by grouping matches into rounds; links to match details.

function MatchCard({ match }) {
  // Small card for a single match with scores/winner and a link if scheduled
  const team1Winner = match?.result?.winner === match?.team1?.country;
  const team2Winner = match?.result?.winner === match?.team2?.country;
  return (
    <div className="match">
      <div className={`team ${team1Winner ? 'winner' : ''}`}>
        <span>{match?.team1?.country}</span>
        {match?.result ? <span className="team-score">{match?.result?.team1_goals}</span> : null}
      </div>
      <div className={`team ${team2Winner ? 'winner' : ''}`}>
        <span>{match?.team2?.country}</span>
        {match?.result ? <span className="team-score">{match?.result?.team2_goals}</span> : null}
      </div>
      <div className="text-center mt-1">
        <small className={`match-status ${match?.status}`}>{match?.status}</small>
        {match?.status === 'completed' ? (
          <>
            <br />
            <small>Winner: {match?.result?.winner}</small>
          </>
        ) : null}
      </div>
      {match?.status === 'scheduled' ? (
        <div className="text-center mt-1">
          <Link to={`/match/${match?.id}`} className="btn btn-sm">View Match</Link>
        </div>
      ) : null}
    </div>
  );
}

const BracketPage = () => {
  // Load all matches and group by tournament round
  const [matches, setMatches] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch matches once at mount
    fetch('/api/matches')
      .then(async res => {
        const text = await res.text();
        try {
          const data = JSON.parse(text);
          return data;
        } catch (e) {
          throw new Error(`Invalid JSON response: ${text.substring(0, 100)}`);
        }
      })
      .then(data => setMatches(Array.isArray(data) ? data : []))
      .catch(err => setError(err?.message || 'Failed to load bracket'));
  }, []);

  const rounds = useMemo(() => {
    // Group matches into known rounds for display
    const byRound = { quarterfinal: [], semifinal: [], final: [] };
    if (Array.isArray(matches)) {
      for (const m of matches) {
        if (m?.round && byRound[m.round] !== undefined) byRound[m.round].push(m);
      }
    }
    return byRound;
  }, [matches]);

  return (
    <div className="bracket-container">{/* Wrapper + title + helper links */}
      <h1>Tournament Bracket</h1>
      <p className="text-center mb-2">African Nations League - Road to the Final</p>

      {!matches && !error && (
        <div className="loading-section">
          <i className="fas fa-spinner fa-spin fa-3x"></i>
          <p>Loading tournament bracket...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading Bracket</h3>
          <p>{error}</p>
        </div>
      )}

      {matches && matches.length === 0 && !error && (
        <div className="text-center" style={{ padding: '3rem' }}>
          <i className="fas fa-trophy fa-3x" style={{ color: '#ccc', marginBottom: '1rem' }}></i>
          <h3>No Tournament Created Yet</h3>
          <p>Go to the Admin Dashboard to create a tournament with 8 teams.</p>
          <Link to="/admin" className="btn btn-primary">
            <i className="fas fa-cog"></i> Admin Dashboard
          </Link>
        </div>
      )}

      {matches && matches.length > 0 && (
        <div className="bracket">
          <div className="round">
            <div className="round-title">Quarter Finals</div>
            {rounds.quarterfinal.map(m => <MatchCard key={m.id} match={m} />)}
          </div>
          <div className="round">
            <div className="round-title">Semi Finals</div>
            {rounds.semifinal.map(m => <MatchCard key={m.id} match={m} />)}
          </div>
          <div className="round">
            <div className="round-title">Grand Final</div>
            {rounds.final.map(m => <MatchCard key={m.id} match={m} />)}
          </div>
        </div>
      )}

      <div className="text-center mt-2">
        <Link to="/admin" className="btn btn-primary">
          <i className="fas fa-cog"></i> Admin Dashboard
        </Link>{' '}
        <Link to="/standings" className="btn btn-secondary">
          <i className="fas fa-trophy"></i> View Standings
        </Link>
      </div>
    </div>
  );
};

export default BracketPage;

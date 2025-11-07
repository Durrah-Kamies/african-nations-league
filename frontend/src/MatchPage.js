import React, { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import GoBackButton from './GoBackButton';
// MatchPage.js
// NOTE: Shows details for a single match, optional AI preview/commentary, and per-scorer analysis.

const MatchPage = () => {
  const { matchId } = useParams();
  const [match, setMatch] = useState(null);     // Loaded match doc
  const [loading, setLoading] = useState(true);  // Page-level spinner
  const [error, setError] = useState('');        // Displayable error
  const [preview, setPreview] = useState('');    // AI preview text
  const [analysis, setAnalysis] = useState({});  // Per-player analysis cache

  async function load() {
    // Fetch match details by id
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/match/${matchId}`);
      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || 'Failed to load match');
      setMatch(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [matchId]);

  useEffect(() => {
    // Generate AI preview for scheduled matches
    if (match && match.status === 'scheduled') generatePreview();
  }, [match]);

  async function generatePreview() {
    // Calls backend to generate a match preview (Gemini or fallback)
    try {
      setPreview('');
      const res = await fetch(`/api/match_preview/${matchId}`);
      const data = await res.json();
      if (data.preview) setPreview(data.preview);
    } catch (_) {}
  }

  async function analyzePlayer(playerName) {
    // Per-scorer analysis; memoized by a simple key in state
    const key = playerName.toLowerCase().replace(/ /g, '-');
    setAnalysis(a => ({ ...a, [key]: 'loading' }));
    try {
      const res = await fetch(`/api/player_analysis/${matchId}/${encodeURIComponent(playerName)}`);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to fetch analysis');
      }
      if (data.analysis) {
        setAnalysis(a => ({ ...a, [key]: data.analysis }));
      } else if (data.error) {
        setAnalysis(a => ({ ...a, [key]: `Error: ${data.error}` }));
      } else {
        setAnalysis(a => ({ ...a, [key]: 'Analysis not available for this player.' }));
      }
    } catch (e) {
      console.error('Error analyzing player:', e);
      setAnalysis(a => ({ ...a, [key]: `Error: ${e.message || 'Failed to generate analysis. Please try again.'}` }));
    }
  }

  const events = useMemo(() => match?.result?.events || [], [match]);        // Timeline events
  const goalScorers = useMemo(() => match?.result?.goal_scorers || [], [match]); // For analysis cards

  if (loading) {
    return (
      <div className="match-container">
        <div className="loading-section">
          <i className="fas fa-spinner fa-spin fa-3x"></i>
          <p>Loading match data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="match-container">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!match) return null;

  return (
    <div className="match-container">
      <GoBackButton fallback="/tournament" />
      <div className="match-header">
        <h1>{match.team1.country} vs {match.team2.country}</h1>
        <div className="match-info">
          <span className="match-round">{match.round?.[0]?.toUpperCase()}{match.round?.slice(1)}</span>
          <span className={`match-status ${match.status}`}>{match.status?.[0]?.toUpperCase()}{match.status?.slice(1)}</span>
        </div>
      </div>

      {match.status === 'scheduled' && (
        <div className="ai-preview-section">
          <h2><i className="fas fa-robot"></i> AI Match Preview</h2>
          <div className="ai-content">
            <div id="match-preview">
              {preview ? (
                <div className="ai-generated-content" dangerouslySetInnerHTML={{ __html: preview.replace(/\n/g, '<br>') }} />
              ) : (
                <p><i className="fas fa-spinner fa-spin"></i> Generating AI preview...</p>
              )}
            </div>
            <button onClick={generatePreview} className="btn btn-ai">
              <i className="fas fa-sync-alt"></i> Regenerate Preview
            </button>
          </div>
        </div>
      )}

      {match.status === 'completed' && match.result && (
        <>
          <div className="match-result">
            <div className="score-display">
              <div className="team-score">
                <h3>{match.team1.country}</h3>
                <span className="score">{match.result.team1_goals}</span>
              </div>
              <div className="score-separator">-</div>
              <div className="team-score">
                <h3>{match.team2.country}</h3>
                <span className="score">{match.result.team2_goals}</span>
              </div>
            </div>
            <div className="winner-banner">
              <i className="fas fa-trophy"></i>
              Winner: {match.result.winner}
            </div>
            {match.result.decided_by === 'extra_time' && (
              <p className="text-center" style={{ marginTop: '0.5rem' }}>
                After Extra Time
              </p>
            )}
            {match.result.decided_by === 'penalties' && (
              <p className="text-center" style={{ marginTop: '0.5rem' }}>
                Decided by Penalties{match.result.penalty_score ? ` (${match.result.penalty_score})` : ''}
              </p>
            )}
          </div>

          {events.length > 0 && (
            <div className="match-events-section">
              <h2><i className="fas fa-list"></i> Match Events</h2>
              <div className="events-timeline">
                {events.map((event, idx) => (
                  <div className="event-item" key={idx}>
                    <span className="event-minute">{event.minute}'</span>
                    <span className={`event-type ${event.type}`}>{event.type.toUpperCase()}</span>
                    <span className="event-player">{event.player} ({event.team})</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {match.result.commentary && match.result.commentary.length > 0 && (
            <div className="ai-commentary-section">
              <h2><i className="fas fa-robot"></i> AI Match Commentary</h2>
              <div className="commentary-container">
                {match.result.commentary.map((line, idx) => (
                  <div className="commentary-line" key={idx}>
                    <span className="commentary-text">{line}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {goalScorers.length > 0 && (
            <div className="player-analysis-section">
              <h2><i className="fas fa-chart-line"></i> AI Player Analysis</h2>
              <div className="players-grid">
                {goalScorers.map(goal => {
                  const key = goal.player.toLowerCase().replace(/ /g, '-');
                  const content = analysis[key];
                  return (
                    <div className="player-card" key={key}>
                      <h4>{goal.player}</h4>
                      <p className="goal-info">⚽ {goal.minute}' - {goal.team}</p>
                      <div className="analysis-content">
                        {content === 'loading' ? (
                          <p><i className="fas fa-spinner fa-spin"></i> Analyzing performance...</p>
                        ) : content ? (
                          <div className="ai-generated-content" dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br>') }} />
                        ) : (
                          <p>Click to analyze performance...</p>
                        )}
                      </div>
                      <button onClick={() => analyzePlayer(goal.player)} className="btn btn-sm">
                        <i className="fas fa-chart-bar"></i> Analyze Performance
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MatchPage;

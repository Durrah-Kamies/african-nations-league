import React from 'react';
import { useNavigate } from 'react-router-dom';
// GoBackButton.js
// NOTE: Utility button to navigate back, or to a fallback path if no history.

const GoBackButton = ({ fallback = '/' }) => {
  const navigate = useNavigate();
  function handleClick() {
    // If browser has history, go back one step; otherwise go to provided fallback
    if (window.history.length > 1) navigate(-1);
    else navigate(fallback);
  }
  return (
    <button onClick={handleClick} className="btn btn-sm" style={{ marginBottom: '1rem' }}>
      <i className="fas fa-arrow-left"></i> Go Back
    </button>
  );
};

export default GoBackButton;

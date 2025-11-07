import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
// RegisterPage.js
// NOTE: Team registration form that posts to the backend to create a team + generated squad.

const RegisterPage = () => {
  const navigate = useNavigate();
  const countries = [
    "Nigeria", "Ghana", "Senegal", "Egypt", "Morocco", "Algeria", "Tunisia",
    "Cameroon", "Ivory Coast", "South Africa", "Kenya", "Ethiopia", "Angola",
    "DR Congo", "Tanzania", "Uganda", "Zambia", "Zimbabwe", "Mali", "Burkina Faso"
  ];

  const [form, setForm] = useState({
    country: '',
    manager: '',
    representative: '',
    email: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  function handleChange(e) {
    // Generic input handler for all fields
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  }

  async function handleSubmit(e) {
    // POST to /api/teams; backend creates the squad + rating
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch('/api/teams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok || data.success === false) {
        throw new Error(data.error || 'Registration failed');
      }
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="form-container">{/* Simple stacked form layout */}
      <h1>Register Your National Team</h1>
      <p className="text-center mb-2">Join the inaugural African Nations League tournament</p>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="country">Select Country:</label>
          <select id="country" name="country" required value={form.country} onChange={handleChange}>
            <option value="">Choose your country...</option>
            {countries.map(country => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="manager">Team Manager:</label>
          <input type="text" id="manager" name="manager" required placeholder="Enter manager's full name" value={form.manager} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label htmlFor="representative">Federation Representative:</label>
          <input type="text" id="representative" name="representative" required placeholder="Enter representative's name" value={form.representative} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label htmlFor="email">Contact Email:</label>
          <input type="email" id="email" name="email" required placeholder="Enter contact email" value={form.email} onChange={handleChange} />
        </div>
        {error && (
          <div className="error-message" style={{ marginBottom: '1rem' }}>
            {error}
          </div>
        )}
        <button type="submit" className="btn btn-primary btn-large" style={{ width: '100%' }} disabled={submitting}>
          <i className="fas fa-flag"></i> {submitting ? 'Registering…' : 'Register National Team'}
        </button>
      </form>
      <div className="mt-2 text-center">
        <p>Already have teams registered? <Link to="/admin">Go to Admin Dashboard</Link></p>
      </div>
    </div>
  );
};

export default RegisterPage;

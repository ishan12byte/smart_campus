import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/auth';
import { getRoles } from '../services/incidents';

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const routeUserByRole = async (user) => {
    try {
      const roles = await getRoles();
      const userRole = roles.find((r) => r.id === user.role_id);
      const roleName = userRole ? userRole.name.toUpperCase() : '';

      if (roleName === 'STUDENT') {
        navigate('/student');
      } else if (roleName === 'STAFF') {
        navigate('/staff');
      } else if (roleName === 'SUPER_ADMIN' || roleName === 'ADMIN' || roleName === 'DEPARTMENT_HEAD') {
        navigate('/admin');
      } else {
        navigate('/student');
      }
    } catch {
      // Default navigation if roles endpoint check fails
      navigate('/student');
    }
  };

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await login(email, password);
      if (result && result.user) {
        await routeUserByRole(result.user);
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCredentials = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>SMART CAMPUS</h1>
        <p className="subtitle">Integrated Operations & Incident Management</p>

        {error && (
          <div style={{ padding: '10px 14px', background: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '8px', marginBottom: '16px', fontSize: '13px', fontWeight: '500' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              className="form-input"
              type="email"
              placeholder="e.g. student@campus.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              className="form-input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px', padding: '12px' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="quick-login-section">
          <h4>Demo Test Accounts</h4>
          <div className="quick-buttons">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => fillDemoCredentials('student@campus.edu', 'password123')}
            >
              Student
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => fillDemoCredentials('staff@campus.edu', 'password123')}
            >
              Staff
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => fillDemoCredentials('admin@campus.edu', 'password123')}
            >
              Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getIncidents, performIncidentAction } from '../services/incidents';
import { getStoredUser, logout } from '../services/auth';

function StaffDashboard() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');

  const fetchStaffIncidents = async () => {
    setLoading(true);
    try {
      const data = await getIncidents();
      setIncidents(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load assigned incidents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStaffIncidents();
  }, []);

  const handleAction = async (id, action) => {
    setError('');
    setActionSuccess('');
    try {
      const updated = await performIncidentAction(id, action);
      setActionSuccess(`Incident #${id} moved to ${updated.status}!`);
      fetchStaffIncidents();
    } catch (err) {
      setError(`Action failed: ${err.message}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Metrics
  const assignedCount = incidents.length;
  const inProgressCount = incidents.filter((i) => i.status === 'IN_PROGRESS').length;
  const pendingVerificationCount = incidents.filter((i) => i.status === 'VERIFICATION_PENDING').length;
  const resolvedCount = incidents.filter((i) => ['CLOSED', 'RESOLVED'].includes(i.status)).length;

  return (
    <div>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="nav-brand">
          🎓 <span>Smart Campus</span>
        </div>
        <div className="nav-user">
          <span className="user-badge" style={{ background: '#ecfdf5', color: '#047857' }}>
            🛠 {user?.name || 'Staff Operations'} ({user?.email || 'staff@campus.edu'})
          </span>
          <button className="btn-logout" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-container">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1>Staff Operations Dashboard</h1>
            <p>Manage operational response, acknowledge assignments, and track resolutions.</p>
          </div>
          <button className="btn btn-secondary" onClick={fetchStaffIncidents}>
            🔄 Refresh Tasks
          </button>
        </div>

        {actionSuccess && (
          <div style={{ padding: '14px 18px', background: 'var(--success-bg)', color: 'var(--success)', borderRadius: '10px', fontWeight: '500', border: '1px solid #a7f3d0' }}>
            ✓ {actionSuccess}
          </div>
        )}

        {error && (
          <div style={{ padding: '14px 18px', background: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '10px', fontWeight: '500', border: '1px solid #fecaca' }}>
            ⚠ {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Assigned Incidents</h3>
            <p className="stat-value">{assignedCount}</p>
          </div>
          <div className="stat-card">
            <h3>In Progress</h3>
            <p className="stat-value" style={{ color: 'var(--info)' }}>{inProgressCount}</p>
          </div>
          <div className="stat-card">
            <h3>Pending Verification</h3>
            <p className="stat-value" style={{ color: 'var(--warning)' }}>{pendingVerificationCount}</p>
          </div>
          <div className="stat-card">
            <h3>Resolved</h3>
            <p className="stat-value" style={{ color: 'var(--success)' }}>{resolvedCount}</p>
          </div>
        </div>

        {/* Incidents Table */}
        <div className="content-card">
          <div className="content-card-header">
            <h2>Operational Response Queue</h2>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              {incidents.length} tasks in department queue
            </span>
          </div>

          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title & Description</th>
                  <th>Category</th>
                  <th>Location</th>
                  <th>Priority</th>
                  <th>Escalation</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '32px' }}>
                      Loading operational queue...
                    </td>
                  </tr>
                ) : incidents.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-secondary)' }}>
                      No tasks assigned in your queue.
                    </td>
                  </tr>
                ) : (
                  incidents.map((inc) => (
                    <tr key={inc.id}>
                      <td><strong>#{inc.id}</strong></td>
                      <td>
                        <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{inc.title}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{inc.description}</div>
                        {inc.reopened_count > 0 && (
                          <span style={{ fontSize: '11px', color: 'var(--danger)', fontWeight: '600' }}>
                            ⚠ Reopened {inc.reopened_count} time(s)
                          </span>
                        )}
                      </td>
                      <td>
                        <span style={{ fontWeight: '500' }}>{inc.category}</span>
                        {inc.subcategory && (
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{inc.subcategory}</div>
                        )}
                      </td>
                      <td>{inc.location}</td>
                      <td>
                        <span className={`badge badge-priority-${inc.priority_level || 'LOW'}`}>
                          {inc.priority_level || 'LOW'} ({inc.priority_score ?? '-'})
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-escalation-${inc.escalation_level || 'NONE'}`}>
                          {inc.escalation_level || 'NONE'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-status-${inc.status}`}>
                          {inc.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        {inc.status === 'REPORTED' && (
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => handleAction(inc.id, 'acknowledge')}
                          >
                            Acknowledge
                          </button>
                        )}
                        {(inc.status === 'ACKNOWLEDGED' || inc.status === 'REOPENED') && (
                          <button
                            className="btn btn-primary btn-sm"
                            style={{ background: '#2563eb' }}
                            onClick={() => handleAction(inc.id, 'start')}
                          >
                            Start Work
                          </button>
                        )}
                        {inc.status === 'IN_PROGRESS' && (
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleAction(inc.id, 'resolve')}
                          >
                            Mark Resolved
                          </button>
                        )}
                        {inc.status === 'VERIFICATION_PENDING' && (
                          <span style={{ fontSize: '12px', color: 'var(--warning)', fontWeight: '500' }}>
                            Awaiting verification
                          </span>
                        )}
                        {inc.status === 'CLOSED' && (
                          <span style={{ fontSize: '12px', color: 'var(--success)' }}>
                            ✓ Closed
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

export default StaffDashboard;
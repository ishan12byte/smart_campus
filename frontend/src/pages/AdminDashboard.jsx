import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getIncidents, getDepartments, performIncidentAction } from '../services/incidents';
import { getStoredUser, logout } from '../services/auth';

function AdminDashboard() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const [incidents, setIncidents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('ALL');

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [incData, deptData] = await Promise.all([
        getIncidents(),
        getDepartments(),
      ]);
      setIncidents(incData || []);
      setDepartments(deptData || []);
    } catch (err) {
      setError(err.message || 'Failed to load administration data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleAction = async (id, action) => {
    try {
      await performIncidentAction(id, action);
      fetchAdminData();
    } catch (err) {
      alert(`Action failed: ${err.message}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Metrics
  const totalIncidents = incidents.length;
  const criticalCount = incidents.filter((i) => i.priority_level === 'CRITICAL').length;
  const escalatedCount = incidents.filter((i) => i.escalation_level && i.escalation_level !== 'NONE').length;
  const resolvedCount = incidents.filter((i) => ['CLOSED', 'RESOLVED'].includes(i.status)).length;

  // Filtered list
  const filteredIncidents = incidents.filter((inc) => {
    if (filter === 'CRITICAL') return inc.priority_level === 'CRITICAL';
    if (filter === 'ESCALATED') return inc.escalation_level && inc.escalation_level !== 'NONE';
    if (filter === 'ACTIVE') return !['CLOSED', 'RESOLVED'].includes(inc.status);
    if (filter === 'RESOLVED') return ['CLOSED', 'RESOLVED'].includes(inc.status);
    return true;
  });

  return (
    <div>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="nav-brand">
          🎓 <span>Smart Campus</span>
        </div>
        <div className="nav-user">
          <span className="user-badge" style={{ background: '#fef3c7', color: '#92400e' }}>
            ⚡ {user?.name || 'Administrator'} ({user?.email || 'admin@campus.edu'})
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
            <h1>Executive Operations Command</h1>
            <p>Campus-wide monitoring, SLA compliance, emergency escalations, and workload allocation.</p>
          </div>
          <button className="btn btn-primary" onClick={fetchAdminData}>
            🔄 Sync Live Data
          </button>
        </div>

        {error && (
          <div style={{ padding: '14px 18px', background: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '10px', fontWeight: '500', border: '1px solid #fecaca' }}>
            ⚠ {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Campus Incidents</h3>
            <p className="stat-value">{totalIncidents}</p>
          </div>
          <div className="stat-card">
            <h3>Critical Incidents</h3>
            <p className="stat-value" style={{ color: 'var(--danger)' }}>{criticalCount}</p>
          </div>
          <div className="stat-card">
            <h3>Escalations Triggered</h3>
            <p className="stat-value" style={{ color: '#ea580c' }}>{escalatedCount}</p>
          </div>
          <div className="stat-card">
            <h3>Resolved / Closed</h3>
            <p className="stat-value" style={{ color: 'var(--success)' }}>{resolvedCount}</p>
          </div>
        </div>

        {/* Escalation Alerts Board if any */}
        {escalatedCount > 0 && (
          <div style={{ background: '#fff1f2', border: '1px solid #fecdd3', borderRadius: '12px', padding: '20px' }}>
            <h3 style={{ margin: '0 0 10px', color: '#9f1239', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🚨 Active Incident Escalation Alerts
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {incidents
                .filter((i) => i.escalation_level && i.escalation_level !== 'NONE')
                .map((esc) => (
                  <div key={esc.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#ffffff', padding: '12px 16px', borderRadius: '8px', border: '1px solid #fda4af' }}>
                    <div>
                      <strong>#{esc.id} - {esc.title}</strong> ({esc.location})
                      <div style={{ fontSize: '13px', color: '#881337', marginTop: '2px' }}>
                        Reason: {esc.escalation_reason || 'Policy triggered escalation'}
                      </div>
                    </div>
                    <span className={`badge badge-escalation-${esc.escalation_level}`}>
                      {esc.escalation_level}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Filter Controls & Incidents Table */}
        <div className="content-card">
          <div className="content-card-header">
            <h2>Campus Incident Overview</h2>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['ALL', 'CRITICAL', 'ESCALATED', 'ACTIVE', 'RESOLVED'].map((fKey) => (
                <button
                  key={fKey}
                  className={`btn btn-sm ${filter === fKey ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setFilter(fKey)}
                >
                  {fKey}
                </button>
              ))}
            </div>
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
                  <th>Assigned Staff</th>
                  <th>Escalation</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="9" style={{ textAlign: 'center', padding: '32px' }}>
                      Loading campus records...
                    </td>
                  </tr>
                ) : filteredIncidents.length === 0 ? (
                  <tr>
                    <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-secondary)' }}>
                      No incidents match the selected filter.
                    </td>
                  </tr>
                ) : (
                  filteredIncidents.map((inc) => (
                    <tr key={inc.id}>
                      <td><strong>#{inc.id}</strong></td>
                      <td>
                        <div style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{inc.title}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{inc.description}</div>
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
                        <span style={{ fontSize: '13px', color: '#334155' }}>
                          {inc.assigned_resource_name || 'Unassigned'}
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
                            Ack
                          </button>
                        )}
                        {inc.status === 'VERIFICATION_PENDING' && (
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleAction(inc.id, 'verify')}
                          >
                            Verify
                          </button>
                        )}
                        {inc.status === 'CLOSED' && (
                          <span style={{ fontSize: '12px', color: 'var(--success)' }}>Closed</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Departments Registry */}
        <div className="content-card">
          <div className="content-card-header">
            <h2>Campus Departments Registry</h2>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              {departments.length} Operational Departments
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
            {departments.map((dept) => (
              <div key={dept.id} style={{ border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px', background: '#fafafa' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: 'var(--primary)' }}>{dept.code}</strong>
                  <span className="badge" style={{ background: dept.is_active ? '#dcfce7' : '#fee2e2', color: dept.is_active ? '#166534' : '#991b1b' }}>
                    {dept.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div style={{ fontWeight: '600', marginTop: '6px' }}>{dept.name}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {dept.description || 'Campus operational service unit'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default AdminDashboard;
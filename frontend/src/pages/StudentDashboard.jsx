import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getIncidents, createIncident, getCategories, performIncidentAction } from '../services/incidents';
import { getStoredUser, logout } from '../services/auth';

function StudentDashboard() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const [incidents, setIncidents] = useState([]);
  const [categoriesData, setCategoriesData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [impact, setImpact] = useState(3);
  const [urgency, setUrgency] = useState(3);
  const [safety, setSafety] = useState(3);
  const [isEmergency, setIsEmergency] = useState(false);
  const [emergencyType, setEmergencyType] = useState('FIRE');

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [incData, catData] = await Promise.all([
        getIncidents(),
        getCategories(),
      ]);
      setIncidents(incData || []);
      setCategoriesData(catData || {});
      if (catData && Object.keys(catData).length > 0 && !category) {
        const firstCategory = Object.keys(catData)[0];
        setCategory(firstCategory);
        if (catData[firstCategory]?.subcategories?.length > 0) {
          setSubcategory(catData[firstCategory].subcategories[0]);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to load reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCategoryChange = (e) => {
    const selectedCat = e.target.value;
    setCategory(selectedCat);
    const subs = categoriesData[selectedCat]?.subcategories || [];
    setSubcategory(subs[0] || '');
  };

  const handleCreateReport = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    try {
      const payload = {
        title,
        description,
        location,
        category,
        subcategory,
        impact: Number(impact),
        urgency: Number(urgency),
        safety: Number(safety),
        deadline: 3,
        recurrence: 1,
        incident_type: isEmergency ? emergencyType : null,
      };

      const created = await createIncident(payload);
      setSuccessMessage(`Incident #${created.id} reported! Priority: ${created.priority_level || 'EVALUATING'}, Assigned to: ${created.assigned_resource_name || 'Department Team'}`);
      setShowModal(false);
      // Reset form
      setTitle('');
      setDescription('');
      setLocation('');
      setIsEmergency(false);
      fetchDashboardData();
    } catch (err) {
      setError(err.message || 'Failed to submit report.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAction = async (id, action) => {
    try {
      await performIncidentAction(id, action);
      fetchDashboardData();
    } catch (err) {
      alert(`Action failed: ${err.message}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Compute metrics
  const totalReports = incidents.length;
  const openReports = incidents.filter((i) => ['REPORTED', 'ACKNOWLEDGED', 'IN_PROGRESS'].includes(i.status)).length;
  const pendingVerification = incidents.filter((i) => i.status === 'VERIFICATION_PENDING').length;
  const resolvedReports = incidents.filter((i) => ['CLOSED', 'RESOLVED'].includes(i.status)).length;

  return (
    <div>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="nav-brand">
          🎓 <span>Smart Campus</span>
        </div>
        <div className="nav-user">
          <span className="user-badge">
            👤 {user?.name || 'Student'} ({user?.email || 'student@campus.edu'})
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
            <h1>Student Dashboard</h1>
            <p>Report and track campus operational issues in real time.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + Report New Incident
          </button>
        </div>

        {successMessage && (
          <div style={{ padding: '14px 18px', background: 'var(--success-bg)', color: 'var(--success)', borderRadius: '10px', fontWeight: '500', border: '1px solid #a7f3d0' }}>
            ✓ {successMessage}
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
            <h3>My Reports</h3>
            <p className="stat-value">{totalReports}</p>
          </div>
          <div className="stat-card">
            <h3>Active / In Progress</h3>
            <p className="stat-value" style={{ color: 'var(--info)' }}>{openReports}</p>
          </div>
          <div className="stat-card">
            <h3>Pending Verification</h3>
            <p className="stat-value" style={{ color: 'var(--warning)' }}>{pendingVerification}</p>
          </div>
          <div className="stat-card">
            <h3>Resolved</h3>
            <p className="stat-value" style={{ color: 'var(--success)' }}>{resolvedReports}</p>
          </div>
        </div>

        {/* Incident Reports Table */}
        <div className="content-card">
          <div className="content-card-header">
            <h2>My Incident Reports</h2>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Showing {incidents.length} incidents
            </span>
          </div>

          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Location</th>
                  <th>Priority</th>
                  <th>Assigned To</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '32px' }}>
                      Loading your reported incidents...
                    </td>
                  </tr>
                ) : incidents.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-secondary)' }}>
                      No incident reports yet. Click <strong>Report New Incident</strong> to create one.
                    </td>
                  </tr>
                ) : (
                  incidents.map((inc) => (
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
                          {inc.priority_level || 'LOW'}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '13px', color: '#334155' }}>
                          {inc.assigned_resource_name || 'Unassigned'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge badge-status-${inc.status}`}>
                          {inc.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        {inc.status === 'VERIFICATION_PENDING' ? (
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <button
                              className="btn btn-success btn-sm"
                              onClick={() => handleAction(inc.id, 'verify')}
                            >
                              Verify & Close
                            </button>
                            <button
                              className="btn btn-warning btn-sm"
                              onClick={() => handleAction(inc.id, 'reopen')}
                            >
                              Reopen
                            </button>
                          </div>
                        ) : inc.status === 'CLOSED' ? (
                          <span style={{ fontSize: '12px', color: 'var(--success)' }}>✓ Closed</span>
                        ) : (
                          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>In progress</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Report New Incident Modal */}
        {showModal && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2 style={{ marginTop: 0, marginBottom: '18px' }}>Report Campus Incident</h2>
              
              <form onSubmit={handleCreateReport}>
                <div className="form-group">
                  <label>Incident Title *</label>
                  <input
                    className="form-input"
                    placeholder="Brief description of the issue"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Detailed Description *</label>
                  <textarea
                    className="form-textarea"
                    rows="3"
                    placeholder="Provide details about the issue, affected facilities, or hazards"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Category *</label>
                    <select
                      className="form-select"
                      value={category}
                      onChange={handleCategoryChange}
                      required
                    >
                      {Object.keys(categoriesData).map((catKey) => (
                        <option key={catKey} value={catKey}>
                          {categoriesData[catKey].name || catKey}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Subcategory *</label>
                    <select
                      className="form-select"
                      value={subcategory}
                      onChange={(e) => setSubcategory(e.target.value)}
                      required
                    >
                      {(categoriesData[category]?.subcategories || []).map((sub) => (
                        <option key={sub} value={sub}>
                          {sub.replace(/_/g, ' ')}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Campus Location *</label>
                  <input
                    className="form-input"
                    placeholder="e.g. Block C - Classroom 302 / Library 2nd Floor"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Impact Severity (1-5)</label>
                    <select
                      className="form-select"
                      value={impact}
                      onChange={(e) => setImpact(e.target.value)}
                    >
                      <option value="1">1 - Minimal</option>
                      <option value="2">2 - Low</option>
                      <option value="3">3 - Moderate</option>
                      <option value="4">4 - High</option>
                      <option value="5">5 - Critical Campus Impact</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Urgency (1-5)</label>
                    <select
                      className="form-select"
                      value={urgency}
                      onChange={(e) => setUrgency(e.target.value)}
                    >
                      <option value="1">1 - Flexible</option>
                      <option value="2">2 - Low</option>
                      <option value="3">3 - Normal</option>
                      <option value="4">4 - Immediate</option>
                      <option value="5">5 - Emergency</option>
                    </select>
                  </div>
                </div>

                <div className="form-group" style={{ margin: '14px 0' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={isEmergency}
                      onChange={(e) => setIsEmergency(e.target.checked)}
                    />
                    <span style={{ color: 'var(--danger)', fontWeight: '600' }}>
                      🚨 Mark as Immediate Emergency Hazard
                    </span>
                  </label>
                </div>

                {isEmergency && (
                  <div className="form-group">
                    <label>Emergency Hazard Type</label>
                    <select
                      className="form-select"
                      value={emergencyType}
                      onChange={(e) => setEmergencyType(e.target.value)}
                    >
                      <option value="FIRE">FIRE</option>
                      <option value="MEDICAL_EMERGENCY">MEDICAL EMERGENCY</option>
                      <option value="IMMEDIATE_SECURITY_THREAT">IMMEDIATE SECURITY THREAT</option>
                      <option value="MAJOR_ELECTRICAL_HAZARD">MAJOR ELECTRICAL HAZARD</option>
                      <option value="CRITICAL_CYBER_INCIDENT">CRITICAL CYBER INCIDENT</option>
                    </select>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowModal(false)}
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? 'Submitting & Evaluating...' : 'Submit Incident Report'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default StudentDashboard;
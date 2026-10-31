import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "./StaffDashboard.css";

function getIncidentList(response) {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response?.incidents)) return response.incidents;
  if (Array.isArray(response?.data)) return response.data;
  return [];
}

function formatStatus(status) {
  if (!status) return "Unknown";
  return String(status).replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());
}

function getStatusClass(status) {
  const value = String(status || "").toLowerCase().replaceAll("_", " ").replaceAll("-", " ");
  if (value.includes("progress")) return "in-progress";
  if (value.includes("closed") || value.includes("completed")) return "completed";
  if (value.includes("verification")) return "verification";
  if (value.includes("assign")) return "assigned";
  if (value.includes("reject")) return "rejected";
  return "reported";
}

function getIncidentTitle(incident) {
  return incident.title || incident.subject || incident.name || "Untitled complaint";
}

function getIncidentId(incident) {
  return incident.incident_id || incident.id || "—";
}

function getIncidentDate(incident) {
  const value = incident.created_at || incident.createdAt || incident.date;
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
}

function StaffDashboard() {
  const navigate = useNavigate();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedIncident, setSelectedIncident] = useState(null);

  async function loadIncidents() {
    setLoading(true);
    setError("");

    try {
      const response = await getIncidents();
      setIncidents(getIncidentList(response));
    } catch (err) {
      setError(
        err?.message ||
          "We couldn't load campus complaints. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadIncidents();
  }, []);

  const counts = useMemo(() => {
    const statusOf = incident =>
      String(incident.status || "").toLowerCase().replaceAll("_", " ");

    return {
      total: incidents.length,

      open: incidents.filter(item =>
        ["reported", "acknowledged", "under review"].includes(
          statusOf(item)
        )
      ).length,

      progress: incidents.filter(item =>
        statusOf(item).includes("progress")
      ).length,

      closed: incidents.filter(item =>
        ["closed", "completed"].includes(statusOf(item))
      ).length,
    };
  }, [incidents]);

  const filteredIncidents = useMemo(
    () =>
      incidents.filter(incident => {
        const searchable = [
          getIncidentId(incident),
          getIncidentTitle(incident),
          incident.category,
          incident.location,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();

        const matchesSearch = searchable.includes(search.toLowerCase());

        const matchesStatus =
          statusFilter === "ALL" ||
          String(incident.status || "").toUpperCase() === statusFilter;

        return matchesSearch && matchesStatus;
      }),
    [incidents, search, statusFilter]
  );

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <div className="staff-dashboard">
      <aside className="staff-sidebar">
        <div className="staff-brand">
          <div className="staff-brand-mark">SC</div>
          <span>SMART CAMPUS</span>
        </div>

        <p className="staff-sidebar-label">MAIN MENU</p>

        <nav className="staff-nav">
          <button
            className="staff-nav-link active"
            onClick={() =>
              window.scrollTo({ top: 0, behavior: "smooth" })
            }
          >
            <span className="staff-nav-icon">⌂</span>
            Dashboard
          </button>

          <button
            className="staff-nav-link"
            onClick={() =>
              document
                .getElementById("campus-complaints")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            <span className="staff-nav-icon">▤</span>
            Campus Complaints
          </button>

          <button
            className="staff-nav-link"
            onClick={() =>
              document
                .getElementById("assigned-tasks")
                ?.scrollIntoView({ behavior: "smooth" })
            }
          >
            <span className="staff-nav-icon">✓</span>
            My Assigned Tasks
          </button>
        </nav>

        <div className="staff-sidebar-bottom">
          <div className="staff-help">
            <span className="staff-help-icon">?</span>

            <div>
              <strong>Need assistance?</strong>
              <p>
                Contact your campus administrator for support.
              </p>
            </div>
          </div>

          <button
            className="staff-logout"
            onClick={handleLogout}
          >
            ↪ Logout
          </button>
        </div>
      </aside>

      <main className="staff-main">
        <header className="staff-topbar">
          <div>
            <span className="staff-topbar-label">
              STAFF PORTAL
            </span>

            <strong className="staff-topbar-brand">
              SMART CAMPUS
            </strong>
          </div>

          <div className="staff-avatar">S</div>
        </header>

        <div className="staff-content">
          <section className="staff-welcome">
            <div>
              <span className="staff-eyebrow">
                YOUR WORKSPACE
              </span>

              <h1>Welcome to your Dashboard</h1>

              <p>
                Review campus complaints and keep track of
                responsibilities assigned to you.
              </p>
            </div>
          </section>

          {/* SUMMARY CARDS */}

          <section
            className="staff-summary"
            aria-label="Campus complaint summary"
          >
            <article className="staff-summary-card">
              <span className="staff-card-icon">▤</span>
              <p>Total Complaints</p>
              <h2>{loading ? "—" : counts.total}</h2>
              <small>
                Complaints available to your account
              </small>
            </article>

            <article className="staff-summary-card">
              <span className="staff-card-icon orange">◷</span>
              <p>Open / Under Review</p>
              <h2>{loading ? "—" : counts.open}</h2>
              <small>Awaiting further action</small>
            </article>

            <article className="staff-summary-card">
              <span className="staff-card-icon purple">⌛</span>
              <p>In Progress</p>
              <h2>{loading ? "—" : counts.progress}</h2>
              <small>Currently being handled</small>
            </article>

            <article className="staff-summary-card">
              <span className="staff-card-icon green">✓</span>
              <p>Closed / Completed</p>
              <h2>{loading ? "—" : counts.closed}</h2>
              <small>Marked as completed</small>
            </article>
          </section>

          {/* CAMPUS COMPLAINTS */}

          <section
            className="staff-task-section"
            id="campus-complaints"
          >
            <div className="staff-section-heading">
              <div>
                <h2>Campus Complaints Overview</h2>
                <p>
                  Read-only overview of complaints returned by
                  the incidents service.
                </p>
              </div>

              <button
                className="staff-refresh-btn"
                onClick={loadIncidents}
                disabled={loading}
              >
                {loading ? "Loading..." : "↻ Refresh"}
              </button>
            </div>

            <div className="staff-filters">
              <input
                type="search"
                placeholder="Search by ID, title, category or location..."
                value={search}
                onChange={event => setSearch(event.target.value)}
                aria-label="Search campus complaints"
              />

              <select
                value={statusFilter}
                onChange={event =>
                  setStatusFilter(event.target.value)
                }
                aria-label="Filter complaints by status"
              >
                <option value="ALL">All Statuses</option>
                <option value="REPORTED">Reported</option>
                <option value="ACKNOWLEDGED">
                  Acknowledged
                </option>
                <option value="UNDER_REVIEW">
                  Under Review
                </option>
                <option value="ASSIGNED">Assigned</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="VERIFICATION_PENDING">
                  Verification Pending
                </option>
                <option value="CLOSED">Closed</option>
                <option value="REOPENED">Reopened</option>
              </select>
            </div>

            {loading && (
              <div className="staff-state">
                <div className="staff-spinner"></div>
                <p>Loading campus complaints...</p>
              </div>
            )}

            {!loading && error && (
              <div className="staff-error" role="alert">
                <strong>Unable to load complaints</strong>
                <p>{error}</p>

                <button
                  className="staff-view-btn"
                  onClick={loadIncidents}
                >
                  Try Again
                </button>
              </div>
            )}

            {!loading && !error && incidents.length === 0 && (
              <div className="staff-state">
                <div className="staff-empty-icon">▤</div>
                <h3>No complaints available</h3>
                <p>
                  There are no complaints available to display
                  for this account right now.
                </p>
              </div>
            )}

            {!loading &&
              !error &&
              incidents.length > 0 &&
              filteredIncidents.length === 0 && (
                <div className="staff-state">
                  <h3>No matching complaints</h3>
                  <p>
                    Try changing your search or status filter.
                  </p>
                </div>
              )}

            {!loading &&
              !error &&
              filteredIncidents.length > 0 && (
                <div className="staff-table-wrap">
                  <table className="staff-table">
                    <thead>
                      <tr>
                        <th>Incident</th>
                        <th>Category</th>
                        <th>Location</th>
                        <th>Priority</th>
                        <th>Reported</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredIncidents.map(
                        (incident, index) => (
                          <tr
                            key={
                              getIncidentId(incident) === "—"
                                ? index
                                : getIncidentId(incident)
                            }
                          >
                            <td>
                              <strong>
                                {getIncidentId(incident)}
                              </strong>
                              <small>
                                {getIncidentTitle(incident)}
                              </small>
                            </td>

                            <td>{incident.category || "—"}</td>
                            <td>{incident.location || "—"}</td>

                            <td>
                              <span
                                className={`staff-priority ${String(
                                  incident.priority || "normal"
                                ).toLowerCase()}`}
                              >
                                {incident.priority || "—"}
                              </span>
                            </td>

                            <td>
                              {getIncidentDate(incident)}
                            </td>

                            <td>
                              <span
                                className={`staff-status ${getStatusClass(
                                  incident.status
                                )}`}
                              >
                                {formatStatus(incident.status)}
                              </span>
                            </td>

                            <td>
                              <button
                                className="staff-view-btn"
                                onClick={() =>
                                  setSelectedIncident(incident)
                                }
                              >
                                View
                              </button>
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              )}
          </section>

          {/* MY ASSIGNED TASKS */}

          <section
            className="staff-task-section staff-assigned-section"
            id="assigned-tasks"
          >
            <div className="staff-section-heading">
              <div>
                <h2>My Assigned Tasks</h2>
                <p>
                  Your personal assignments will appear here
                  when a staff-specific endpoint is available.
                </p>
              </div>

              <span className="staff-record-count">
                Not connected
              </span>
            </div>

            <div className="staff-state staff-assignment-note">
              <div className="staff-empty-icon">✓</div>

              <h3>
                Assigned-task data is not connected yet
              </h3>

              <p>
                The current incidents service retrieves incidents,
                but does not identify which tasks are assigned to
                the logged-in staff member. This section is
                intentionally left without demo tasks.
              </p>
            </div>
          </section>

          <footer className="staff-footer">
            SMART CAMPUS · Making campus life better together
          </footer>
        </div>
      </main>

      {/* INCIDENT DETAILS MODAL */}

      {selectedIncident && (
        <div
          className="staff-modal-overlay"
          onClick={() => setSelectedIncident(null)}
        >
          <div
            className="staff-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="staff-modal-title"
            onClick={event => event.stopPropagation()}
          >
            <div className="staff-modal-heading">
              <div>
                <span>INCIDENT DETAILS</span>

                <h2 id="staff-modal-title">
                  {getIncidentId(selectedIncident)}
                </h2>
              </div>

              <button
                aria-label="Close details"
                onClick={() => setSelectedIncident(null)}
              >
                ×
              </button>
            </div>

            <h3>{getIncidentTitle(selectedIncident)}</h3>

            <div className="staff-detail-grid">
              <div>
                <small>Category</small>
                <strong>
                  {selectedIncident.category || "—"}
                </strong>
              </div>

              <div>
                <small>Location</small>
                <strong>
                  {selectedIncident.location || "—"}
                </strong>
              </div>

              <div>
                <small>Priority</small>
                <strong>
                  {selectedIncident.priority || "—"}
                </strong>
              </div>

              <div>
                <small>Reported</small>
                <strong>
                  {getIncidentDate(selectedIncident)}
                </strong>
              </div>

              <div>
                <small>Status</small>
                <strong>
                  {formatStatus(selectedIncident.status)}
                </strong>
              </div>
            </div>

            <div className="staff-detail-block">
              <h4>Description</h4>
              <p>
                {selectedIncident.description ||
                  selectedIncident.complaint ||
                  "No description was provided."}
              </p>
            </div>

            <p className="staff-readonly-note">
              This is a read-only view. Assignment and status
              changes are managed through authorized workflows.
            </p>

            <button
              className="staff-close-btn"
              onClick={() => setSelectedIncident(null)}
            >
              Close Details
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default StaffDashboard;
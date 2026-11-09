import { useEffect, useMemo, useState } from "react";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "./DepartmentHeadDashboard.css";

const navigation = [
  { label: "Overview", path: "overview", icon: "⌂" },
  { label: "Incident Review", path: "incident-review", icon: "▤" },
  { label: "Assignments", path: "assignments", icon: "⇄" },
  { label: "Staff Workload", path: "staff-workload", icon: "◷" },
  { label: "Priority & Escalations", path: "priorities", icon: "⚑" },
  { label: "Resolved Complaints", path: "resolved", icon: "✓" },
  {
    label: "Reports & Analytics",
    path: "analytics",
    icon: "▥",
    to: "/analytics",
    from: "/department/overview",
  },
  { label: "Notifications", path: "notifications", icon: "♧" },
];

function getIncidentList(response) {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response?.incidents)) return response.incidents;
  if (Array.isArray(response?.data)) return response.data;
  if (Array.isArray(response?.items)) return response.items;
  return [];
}

function getIncidentId(incident, index) {
  return (
    incident?.incident_id ??
    incident?.id ??
    incident?._id ??
    `incident-${index + 1}`
  );
}

function getIncidentTitle(incident) {
  return (
    incident?.title ||
    incident?.incident_type ||
    incident?.category ||
    incident?.type ||
    "Untitled incident"
  );
}

function getIncidentLocation(incident) {
  return (
    incident?.location ||
    incident?.building ||
    incident?.block ||
    incident?.place ||
    "Not provided"
  );
}

function getIncidentStatus(incident) {
  return (
    incident?.status ||
    incident?.incident_status ||
    "Status unavailable"
  );
}

function getIncidentPriority(incident) {
  return (
    incident?.priority ||
    incident?.severity ||
    "Not specified"
  );
}

function formatDate(value) {
  if (!value) return "Not available";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function StatusBadge({ value }) {
  const normalized = String(value || "Unknown").toLowerCase();

  let className = "dh-badge-neutral";

  if (
    normalized.includes("resolved") ||
    normalized.includes("closed") ||
    normalized.includes("complete")
  ) {
    className = "dh-badge-success";
  } else if (
    normalized.includes("critical") ||
    normalized.includes("urgent") ||
    normalized.includes("high")
  ) {
    className = "dh-badge-danger";
  } else if (
    normalized.includes("pending") ||
    normalized.includes("review") ||
    normalized.includes("progress")
  ) {
    className = "dh-badge-warning";
  }

  return (
    <span className={`dh-badge ${className}`}>
      {value || "Unknown"}
    </span>
  );
}

function PriorityBadge({ value }) {
  const normalized = String(value || "").toLowerCase();

  let className = "dh-badge-neutral";

  if (normalized.includes("critical") || normalized.includes("high")) {
    className = "dh-badge-danger";
  } else if (normalized.includes("medium")) {
    className = "dh-badge-warning";
  } else if (normalized.includes("low")) {
    className = "dh-badge-success";
  }

  return (
    <span className={`dh-badge ${className}`}>
      {value || "Not specified"}
    </span>
  );
}

function EmptyState({ title, description }) {
  return (
    <div className="dh-empty-state">
      <div className="dh-empty-icon">▤</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function IntegrationNotice({ children }) {
  return (
    <div className="dh-integration-notice">
      <span className="dh-notice-icon">ⓘ</span>
      <p>{children}</p>
    </div>
  );
}

function PageIntro({ eyebrow, title, description }) {
  return (
    <div className="dh-welcome-section">
      <div>
        <span className="dh-eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="dh-feature-card">
      <div className="dh-feature-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <span className="dh-feature-status">
        Backend connection pending
      </span>
    </div>
  );
}

function IncidentTable({ incidents, onSelect, emptyMessage }) {
  if (!incidents.length) {
    return (
      <EmptyState
        title="No incidents to display"
        description={emptyMessage}
      />
    );
  }

  return (
    <div className="dh-table-wrapper">
      <table className="dh-table">
        <thead>
          <tr>
            <th>Incident</th>
            <th>Location</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Date</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident, index) => (
            <tr key={getIncidentId(incident, index)}>
              <td>
                <div className="dh-incident-name">
                  {getIncidentTitle(incident)}
                </div>

                <span className="dh-secondary-text">
                  ID: {getIncidentId(incident, index)}
                </span>
              </td>

              <td>{getIncidentLocation(incident)}</td>

              <td>
                <PriorityBadge value={getIncidentPriority(incident)} />
              </td>

              <td>
                <StatusBadge value={getIncidentStatus(incident)} />
              </td>

              <td>
                {formatDate(
                  incident?.created_at ||
                    incident?.reported_at ||
                    incident?.date
                )}
              </td>

              <td>
                <button
                  type="button"
                  className="dh-view-button"
                  onClick={() => onSelect(incident)}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function IncidentDetails({ incident, onClose }) {
  if (!incident) return null;

  const details = [
    ["Incident ID", incident?.incident_id || incident?.id || incident?._id],
    ["Title / Category", getIncidentTitle(incident)],
    ["Location", getIncidentLocation(incident)],
    ["Priority", getIncidentPriority(incident)],
    ["Status", getIncidentStatus(incident)],
    [
      "Reported date",
      formatDate(
        incident?.created_at ||
          incident?.reported_at ||
          incident?.date
      ),
    ],
    [
      "Description",
      incident?.description || incident?.details || "Not provided",
    ],
  ];

  return (
    <div className="dh-modal-backdrop" onClick={onClose}>
      <div
        className="dh-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="dh-modal-header">
          <div>
            <span className="dh-eyebrow">INCIDENT DETAILS</span>
            <h2>{getIncidentTitle(incident)}</h2>
          </div>

          <button
            type="button"
            className="dh-modal-close"
            onClick={onClose}
            aria-label="Close details"
          >
            ×
          </button>
        </div>

        <div className="dh-detail-list">
          {details.map(([label, value]) => (
            <div className="dh-detail-row" key={label}>
              <span>{label}</span>
              <strong>{value || "Not provided"}</strong>
            </div>
          ))}
        </div>

        <div className="dh-modal-footer">
          <button
            type="button"
            className="dh-primary-button"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function DepartmentHeadDashboard() {
  const location = useLocation();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedIncident, setSelectedIncident] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadIncidents() {
      try {
        setLoading(true);
        setError("");

        const response = await getIncidents();

        if (isMounted) {
          setIncidents(getIncidentList(response));
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err?.message ||
              "Unable to load incidents. Please try again."
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadIncidents();

    return () => {
      isMounted = false;
    };
  }, []);

  const pageTitle = useMemo(() => {
    const currentPath = location.pathname.split("/").filter(Boolean).pop();

    const currentPage = navigation.find(
      (item) => item.path === currentPath
    );

    return currentPage?.label || "Overview";
  }, [location.pathname]);

  const activeIncidents = incidents.filter((incident) => {
    const status = getIncidentStatus(incident).toLowerCase();

    return (
      !status.includes("resolved") &&
      !status.includes("closed") &&
      !status.includes("complete")
    );
  });

  const resolvedIncidents = incidents.filter((incident) => {
    const status = getIncidentStatus(incident).toLowerCase();

    return (
      status.includes("resolved") ||
      status.includes("closed") ||
      status.includes("complete")
    );
  });

  const pendingIncidents = incidents.filter((incident) => {
    const status = getIncidentStatus(incident).toLowerCase();

    return status.includes("pending") || status.includes("review");
  });

  const criticalIncidents = incidents.filter((incident) => {
    return getIncidentPriority(incident)
      .toLowerCase()
      .includes("critical");
  });

  const handleRefresh = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getIncidents();

      setIncidents(getIncidentList(response));
    } catch (err) {
      setError(err?.message || "Unable to refresh incidents.");
    } finally {
      setLoading(false);
    }
  };

  const renderPage = (page) => {
    switch (page) {
      case "overview":
        return (
          <>
            <div className="dh-welcome-section">
              <div>
                <span className="dh-eyebrow">
                  DEPARTMENT CONTROL CENTRE
                </span>

                <h2>Department Overview</h2>

                <p>
                  Review incidents and monitor responsibilities within
                  your department.
                </p>
              </div>

              <button
                type="button"
                className="dh-outline-button"
                onClick={handleRefresh}
              >
                ↻ Refresh data
              </button>
            </div>

            <div className="dh-stats-grid">
              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Total Incidents</span>
                  <span className="dh-stat-icon purple">▤</span>
                </div>

                <strong>{incidents.length}</strong>
                <small>Records returned by the incident service</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Active Incidents</span>
                  <span className="dh-stat-icon blue">◷</span>
                </div>

                <strong>{activeIncidents.length}</strong>
                <small>Not marked as resolved or closed</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Pending Review</span>
                  <span className="dh-stat-icon orange">!</span>
                </div>

                <strong>{pendingIncidents.length}</strong>
                <small>Based on returned incident status</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Resolved</span>
                  <span className="dh-stat-icon green">✓</span>
                </div>

                <strong>{resolvedIncidents.length}</strong>
                <small>Marked resolved, closed or complete</small>
              </div>
            </div>

            <section className="dh-panel">
              <div className="dh-panel-heading">
                <div>
                  <h3>Incidents Requiring Attention</h3>
                  <p>Recently returned active incident records</p>
                </div>

                <span className="dh-count-pill">
                  {activeIncidents.length}
                </span>
              </div>

              <IncidentTable
                incidents={activeIncidents.slice(0, 5)}
                onSelect={setSelectedIncident}
                emptyMessage="There are no active incidents in the returned records."
              />
            </section>
          </>
        );

      case "incident-review":
        return (
          <>
            <PageIntro
              eyebrow="REVIEW CENTRE"
              title="Incident Review"
              description="Review incident reports and inspect the information currently available from the incident service."
            />

            <section className="dh-panel">
              <div className="dh-panel-heading">
                <div>
                  <h3>Incident Review Queue</h3>
                  <p>Incident records returned by the current API</p>
                </div>

                <span className="dh-count-pill">{incidents.length}</span>
              </div>

              <IncidentTable
                incidents={incidents}
                onSelect={setSelectedIncident}
                emptyMessage="No incident records were returned by the service."
              />
            </section>
          </>
        );

      case "assignments":
        return (
          <>
            <PageIntro
              eyebrow="RESPONSIBILITY MANAGEMENT"
              title="Assignments"
              description="Monitor responsibility allocation across department staff."
            />

            <div className="dh-feature-grid">
              <FeatureCard
                icon="⇄"
                title="Assignment Overview"
                description="View which staff members are responsible for each incident once assignment data is provided by the backend."
              />

              <FeatureCard
                icon="＋"
                title="Responsibility Allocation"
                description="Review the assignment workflow. Actual staff allocation must be handled by the authorised backend service."
              />
            </div>

            <IntegrationNotice>
              Staff assignment information is not available through the
              currently confirmed frontend API. This page is ready for the
              assignment service to be connected.
            </IntegrationNotice>
          </>
        );

      case "staff-workload":
        return (
          <>
            <PageIntro
              eyebrow="TEAM MANAGEMENT"
              title="Staff Workload"
              description="Monitor the distribution of responsibilities among department staff."
            />

            <IntegrationNotice>
              Staff lists, assigned task counts and workload calculations
              require department staff and assignment data from the backend.
              No staff names or workload figures have been invented.
            </IntegrationNotice>

            <div className="dh-feature-grid">
              <FeatureCard
                icon="♙"
                title="Department Staff"
                description="A staff directory can appear here when the backend provides department membership and staff details."
              />

              <FeatureCard
                icon="◷"
                title="Workload Distribution"
                description="Assigned, pending and completed task counts can be displayed when assignment records are available."
              />
            </div>
          </>
        );

      case "priorities":
        return (
          <>
            <PageIntro
              eyebrow="PRIORITY CONTROL"
              title="Priority & Escalations"
              description="Keep track of high-priority incidents and cases that may need escalation."
            />

            <div className="dh-stats-grid dh-stats-grid-three">
              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Critical Priority</span>
                  <span className="dh-stat-icon red">!</span>
                </div>

                <strong>{criticalIncidents.length}</strong>
                <small>Records marked Critical</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>High Priority</span>
                  <span className="dh-stat-icon orange">↑</span>
                </div>

                <strong>
                  {
                    incidents.filter((incident) =>
                      getIncidentPriority(incident)
                        .toLowerCase()
                        .includes("high")
                    ).length
                  }
                </strong>

                <small>Records marked High</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Pending Review</span>
                  <span className="dh-stat-icon blue">◷</span>
                </div>

                <strong>{pendingIncidents.length}</strong>
                <small>Pending or review status</small>
              </div>
            </div>

            <section className="dh-panel">
              <div className="dh-panel-heading">
                <div>
                  <h3>Priority Monitoring</h3>
                  <p>Incidents with priority information</p>
                </div>
              </div>

              <IncidentTable
                incidents={incidents.filter((incident) => {
                  const priority =
                    getIncidentPriority(incident).toLowerCase();

                  return (
                    priority.includes("critical") ||
                    priority.includes("high") ||
                    priority.includes("medium")
                  );
                })}
                onSelect={setSelectedIncident}
                emptyMessage="No incidents with Critical, High or Medium priority were returned."
              />
            </section>

            <IntegrationNotice>
              Priority values are displayed from incident records. Priority
              changes and escalation actions require the appropriate backend
              permissions and endpoints.
            </IntegrationNotice>
          </>
        );

      case "resolved":
        return (
          <>
            <PageIntro
              eyebrow="COMPLETED CASES"
              title="Resolved Complaints"
              description="Review incidents that have been marked as resolved or closed."
            />

            <section className="dh-panel">
              <div className="dh-panel-heading">
                <div>
                  <h3>Resolved Incident Records</h3>
                  <p>Based on the status returned by the incident service</p>
                </div>

                <span className="dh-count-pill">
                  {resolvedIncidents.length}
                </span>
              </div>

              <IncidentTable
                incidents={resolvedIncidents}
                onSelect={setSelectedIncident}
                emptyMessage="No resolved incidents were found in the returned records."
              />
            </section>
          </>
        );

      case "analytics":
        return (
          <>
            <PageIntro
              eyebrow="DEPARTMENT INSIGHTS"
              title="Reports & Analytics"
              description="A department-level view of incident trends and performance."
            />

            <div className="dh-stats-grid">
              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Total Records</span>
                  <span className="dh-stat-icon purple">▤</span>
                </div>

                <strong>{incidents.length}</strong>
                <small>Records returned by the API</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Active Records</span>
                  <span className="dh-stat-icon blue">◷</span>
                </div>

                <strong>{activeIncidents.length}</strong>
                <small>Not marked as resolved</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Resolved Records</span>
                  <span className="dh-stat-icon green">✓</span>
                </div>

                <strong>{resolvedIncidents.length}</strong>
                <small>Marked resolved or closed</small>
              </div>

              <div className="dh-stat-card">
                <div className="dh-stat-top">
                  <span>Critical Records</span>
                  <span className="dh-stat-icon red">!</span>
                </div>

                <strong>{criticalIncidents.length}</strong>
                <small>Marked Critical</small>
              </div>
            </div>

            <section className="dh-panel">
              <div className="dh-panel-heading">
                <div>
                  <h3>Analytics Availability</h3>
                  <p>Additional reporting data required</p>
                </div>
              </div>

              <div className="dh-analytics-placeholder">
                <div className="dh-empty-icon">▥</div>

                <h3>Department reports will appear here</h3>

                <p>
                  Trend charts, category breakdowns, resolution time and
                  staff performance can be added when the required backend
                  data is available.
                </p>
              </div>
            </section>

            <IntegrationNotice>
              Reliable department analytics require department identifiers,
              timestamps, incident categories and assignment or resolution
              history from the backend.
            </IntegrationNotice>
          </>
        );

      case "notifications":
        return (
          <>
            <PageIntro
              eyebrow="UPDATES & ALERTS"
              title="Notifications"
              description="A central place for department-level updates and alerts."
            />

            <EmptyState
              title="No notification service connected"
              description="There are no live notifications to display yet. This page is ready for the backend notification feed."
            />

            <IntegrationNotice>
              The current confirmed API does not provide a notifications
              endpoint. Assignment updates, escalation alerts and
              announcements will appear here once the notification service
              is available.
            </IntegrationNotice>
          </>
        );

      default:
        return <Navigate to="/department/overview" replace />;
    }
  };

  return (
    <div className="dh-layout">
      <aside className="dh-sidebar">
        <div className="dh-brand">
          <div className="dh-brand-mark">SC</div>

          <div>
            <h1>SMART CAMPUS</h1>
            <span>Incident Management</span>
          </div>
        </div>

        <div className="dh-role-card">
          <div className="dh-role-avatar">DH</div>

          <div>
            <strong>Department Head</strong>
            <span>Department Portal</span>
          </div>
        </div>

        <div className="dh-nav-label">WORKSPACE</div>

        <nav className="dh-navigation">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.to || `/department/${item.path}`}
              state={{ from: item.from || "/department/overview" }}
              className={({ isActive }) =>
                `dh-nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="dh-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="dh-sidebar-footer">
          <div className="dh-footer-indicator" />
          <span>Department workspace</span>
        </div>
      </aside>

      <main className="dh-main">
        <header className="dh-topbar">
          <div>
            <span className="dh-topbar-label">
              SMART CAMPUS / DEPARTMENT
            </span>

            <h2>{pageTitle}</h2>
          </div>

          <div className="dh-topbar-right">
            <span className="dh-role-chip">Department Head</span>
            <div className="dh-topbar-avatar">DH</div>
          </div>
        </header>

        <div className="dh-page-content">
          {/* API messages are separate from page rendering.
              They no longer replace the selected page. */}

          {loading && (
            <IntegrationNotice>
              Loading incident data...
            </IntegrationNotice>
          )}

          {error && (
            <div className="dh-integration-notice">
              <span className="dh-notice-icon">ⓘ</span>

              <div>
                <p>Incident data could not be loaded: {error}</p>

                <button
                  type="button"
                  className="dh-view-button"
                  onClick={handleRefresh}
                  style={{ marginTop: "10px" }}
                >
                  Retry connection
                </button>
              </div>
            </div>
          )}

          <Routes>
            <Route
              index
              element={<Navigate to="overview" replace />}
            />

            <Route
              path="overview"
              element={renderPage("overview")}
            />

            <Route
              path="incident-review"
              element={renderPage("incident-review")}
            />

            <Route
              path="assignments"
              element={renderPage("assignments")}
            />

            <Route
              path="staff-workload"
              element={renderPage("staff-workload")}
            />

            <Route
              path="priorities"
              element={renderPage("priorities")}
            />

            <Route
              path="resolved"
              element={renderPage("resolved")}
            />

            <Route
              path="analytics"
              element={renderPage("analytics")}
            />

            <Route
              path="notifications"
              element={renderPage("notifications")}
            />

            <Route
              path="*"
              element={<Navigate to="/department/overview" replace />}
            />
          </Routes>
        </div>
      </main>

      {selectedIncident && (
        <IncidentDetails
          incident={selectedIncident}
          onClose={() => setSelectedIncident(null)}
        />
      )}
    </div>
  );
}

export default DepartmentHeadDashboard;
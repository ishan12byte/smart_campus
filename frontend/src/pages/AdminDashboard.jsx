import { useEffect, useMemo, useState } from "react";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";

import { getIncidents } from "../services/incidents";
import "./AdminDashboard.css";

/* -------------------- NAVIGATION -------------------- */

const NAV_ITEMS = [
  { label: "Overview", path: "overview", icon: "▦" },
  { label: "All Complaints", path: "incidents", icon: "▤" },
  { label: "Assignments", path: "assignments", icon: "⇄" },
  { label: "Priority Monitoring", path: "priority", icon: "⚑" },
  { label: "Recurring Complaints", path: "recurring", icon: "↻" },
  { label: "Overdue Complaints", path: "overdue", icon: "◷" },
  { label: "Resolved Complaints", path: "resolved", icon: "✓" },
  { label: "Staff Notifications", path: "notifications", icon: "♧" },
  {
    label: "Analytics",
    path: "analytics",
    icon: "▥",
    to: "/analytics",
    from: "/admin/overview",
  },
];

/* -------------------- DATA HELPERS -------------------- */

function getText(value, fallback = "Not provided") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }

  return String(value);
}

function getIncidentId(incident, index) {
  return (
    incident.id ??
    incident.incident_id ??
    incident.complaint_id ??
    `INC-${String(index + 1).padStart(3, "0")}`
  );
}

function getStatus(incident) {
  return String(
    incident.status ??
    incident.incident_status ??
    "Unknown"
  );
}

function getPriority(incident) {
  return String(
    incident.priority ??
    incident.severity ??
    incident.emergency_level ??
    "Not set"
  );
}

function getDepartment(incident) {
  return (
    incident.department ??
    incident.student_department ??
    incident.programme ??
    incident.course ??
    "Department not provided"
  );
}

function getAssignedStaff(incident) {
  return (
    incident.assigned_to ??
    incident.assigned_staff ??
    incident.staff_name ??
    incident.assignee ??
    null
  );
}

function getCategory(incident) {
  return (
    incident.category ??
    incident.incident_type ??
    incident.type ??
    "Uncategorised"
  );
}

function getDate(incident) {
  return (
    incident.created_at ??
    incident.date ??
    incident.reported_at ??
    null
  );
}

function formatDate(value) {
  if (!value) return "Date unavailable";

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

function isResolved(incident) {
  const status = getStatus(incident).toLowerCase();

  return [
    "resolved",
    "closed",
    "completed",
    "verified",
  ].some((word) => status.includes(word));
}

function isOverdue(incident) {
  if (isResolved(incident)) return false;

  const dueDate =
    incident.due_date ??
    incident.deadline ??
    incident.sla_deadline;

  if (!dueDate) return false;

  const parsedDate = new Date(dueDate);

  return (
    !Number.isNaN(parsedDate.getTime()) &&
    parsedDate.getTime() < Date.now()
  );
}

function isRecurring(incident) {
  return Boolean(
    incident.is_recurring ??
    incident.recurring ??
    incident.recurrence_count > 1
  );
}

function normaliseIncidents(data) {
  if (Array.isArray(data)) return data;

  if (Array.isArray(data?.incidents)) return data.incidents;

  if (Array.isArray(data?.data)) return data.data;

  if (Array.isArray(data?.items)) return data.items;

  return [];
}

/* -------------------- REUSABLE COMPONENTS -------------------- */

function StatCard({ title, value, description, icon }) {
  return (
    <div className="admin-stat-card">
      <div className="admin-stat-icon">{icon}</div>

      <div>
        <p className="admin-stat-title">{title}</p>
        <h2>{value}</h2>
        <p className="admin-stat-description">{description}</p>
      </div>
    </div>
  );
}

function PageHeader({ title, description }) {
  return (
    <div className="admin-page-header">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const value = getText(status, "Unknown");

  return (
    <span
      className={`admin-status-badge ${value
        .toLowerCase()
        .replace(/\s+/g, "-")}`}
    >
      {value}
    </span>
  );
}

function PriorityBadge({ priority }) {
  const value = getText(priority, "Not set");

  return (
    <span
      className={`admin-priority-badge ${value
        .toLowerCase()
        .replace(/\s+/g, "-")}`}
    >
      {value}
    </span>
  );
}

function EmptyState({ message }) {
  return (
    <div className="admin-empty-state">
      <div className="admin-empty-icon">▤</div>
      <h3>No records to display</h3>
      <p>{message}</p>
    </div>
  );
}

function DataNotice({ children }) {
  return (
    <div className="admin-data-notice">
      <strong>Backend data limitation:</strong> {children}
    </div>
  );
}

/* -------------------- INCIDENT TABLE -------------------- */

function IncidentTable({ incidents }) {
  if (!incidents.length) {
    return (
      <EmptyState message="No incidents match this view yet." />
    );
  }

  return (
    <div className="admin-table-wrapper">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Incident ID</th>
            <th>Category</th>
            <th>Department / Programme</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Assigned Staff</th>
            <th>Reported On</th>
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident, index) => (
            <tr key={getIncidentId(incident, index)}>
              <td>
                <strong>{getIncidentId(incident, index)}</strong>
              </td>

              <td>{getText(getCategory(incident))}</td>

              <td>{getText(getDepartment(incident))}</td>

              <td>
                <PriorityBadge priority={getPriority(incident)} />
              </td>

              <td>
                <StatusBadge status={getStatus(incident)} />
              </td>

              <td>
                {getText(getAssignedStaff(incident), "Unassigned")}
              </td>

              <td>{formatDate(getDate(incident))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* -------------------- OVERVIEW PAGE -------------------- */

function OverviewPage({ incidents }) {
  const total = incidents.length;

  const resolved = incidents.filter(isResolved).length;

  const pending = incidents.filter(
    (incident) => !isResolved(incident)
  ).length;

  const overdue = incidents.filter(isOverdue).length;

  const critical = incidents.filter((incident) =>
    ["critical", "emergency"].includes(
      getPriority(incident).toLowerCase()
    )
  ).length;

  const recentIncidents = [...incidents]
    .sort((a, b) => {
      const dateA = new Date(getDate(a) || 0).getTime();
      const dateB = new Date(getDate(b) || 0).getTime();

      return dateB - dateA;
    })
    .slice(0, 5);

  return (
    <>
      <PageHeader
        title="Admin Overview"
        description="Campus-wide incident monitoring and management."
      />

      <div className="admin-stats-grid">
        <StatCard
          title="Total Complaints"
          value={total}
          description="All reported incidents"
          icon="▤"
        />

        <StatCard
          title="Pending Complaints"
          value={pending}
          description="Not yet resolved"
          icon="◷"
        />

        <StatCard
          title="Resolved Complaints"
          value={resolved}
          description="Completed incidents"
          icon="✓"
        />

        <StatCard
          title="Overdue Complaints"
          value={overdue}
          description="Past recorded deadlines"
          icon="!"
        />

        <StatCard
          title="Critical Incidents"
          value={critical}
          description="Marked critical or emergency"
          icon="⚑"
        />
      </div>

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Recent Complaints</h2>
            <p>Latest incidents received by the campus.</p>
          </div>
        </div>

        <IncidentTable incidents={recentIncidents} />
      </section>

      <DataNotice>
        The overview uses records returned by the existing incidents API.
        Counts depend on the fields supplied by the backend.
      </DataNotice>
    </>
  );
}

/* -------------------- ALL COMPLAINTS PAGE -------------------- */

function AllComplaintsPage({ incidents }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const statuses = [
    "All",
    ...new Set(incidents.map(getStatus)),
  ];

  const filteredIncidents = incidents.filter((incident) => {
    const searchableText = [
      getIncidentId(incident),
      getCategory(incident),
      getDepartment(incident),
      getStatus(incident),
      getAssignedStaff(incident),
    ]
      .join(" ")
      .toLowerCase();

    const matchesSearch = searchableText.includes(
      search.toLowerCase()
    );

    const matchesStatus =
      statusFilter === "All" ||
      getStatus(incident) === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <>
      <PageHeader
        title="All Complaints"
        description="View and monitor every incident reported across campus."
      />

      <section className="admin-panel">
        <div className="admin-filter-bar">
          <input
            type="text"
            placeholder="Search by ID, category or department..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status === "All" ? "All Statuses" : status}
              </option>
            ))}
          </select>
        </div>

        <IncidentTable incidents={filteredIncidents} />
      </section>
    </>
  );
}

/* -------------------- ASSIGNMENTS PAGE -------------------- */

function AssignmentsPage({ incidents }) {
  const departments = useMemo(() => {
    const grouped = {};

    incidents.forEach((incident) => {
      const department = getDepartment(incident);

      if (!grouped[department]) {
        grouped[department] = {
          total: 0,
          assigned: 0,
          unassigned: 0,
        };
      }

      grouped[department].total += 1;

      if (getAssignedStaff(incident)) {
        grouped[department].assigned += 1;
      } else {
        grouped[department].unassigned += 1;
      }
    });

    return Object.entries(grouped).sort((a, b) =>
      a[0].localeCompare(b[0])
    );
  }, [incidents]);

  const assigned = incidents.filter(
    (incident) => getAssignedStaff(incident)
  ).length;

  const unassigned = incidents.length - assigned;

  return (
    <>
      <PageHeader
        title="Assignments"
        description="Monitor complaint responsibility across departments and programmes."
      />

      <div className="admin-stats-grid">
        <StatCard
          title="Total Complaints"
          value={incidents.length}
          description="Across all departments"
          icon="▤"
        />

        <StatCard
          title="Assigned"
          value={assigned}
          description="Staff member recorded"
          icon="✓"
        />

        <StatCard
          title="Unassigned"
          value={unassigned}
          description="No assigned staff recorded"
          icon="!"
        />
      </div>

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Department-wise Assignment Summary</h2>
            <p>
              Complaints are grouped using the department or programme
              information returned by the backend.
            </p>
          </div>
        </div>

        {departments.length === 0 ? (
          <EmptyState message="Department information is not available yet." />
        ) : (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Department / Programme</th>
                  <th>Total Complaints</th>
                  <th>Assigned</th>
                  <th>Unassigned</th>
                </tr>
              </thead>

              <tbody>
                {departments.map(([department, values]) => (
                  <tr key={department}>
                    <td><strong>{department}</strong></td>
                    <td>{values.total}</td>
                    <td>{values.assigned}</td>
                    <td>{values.unassigned}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <DataNotice>
        This page displays assignment information already present in
        incident records. Assigning or reassigning staff requires a
        backend assignment endpoint, which is not connected here.
      </DataNotice>
    </>
  );
}

/* -------------------- PRIORITY PAGE -------------------- */

function PriorityPage({ incidents }) {
  const priorityOrder = [
    "Critical",
    "Emergency",
    "High",
    "Medium",
    "Low",
    "Not set",
  ];

  const grouped = priorityOrder.map((priority) => ({
    priority,
    count: incidents.filter(
      (incident) =>
        getPriority(incident).toLowerCase() ===
        priority.toLowerCase()
    ).length,
  }));

  return (
    <>
      <PageHeader
        title="Priority Monitoring"
        description="Monitor incidents according to their recorded urgency."
      />

      <div className="admin-stats-grid">
        {grouped.map((item) => (
          <StatCard
            key={item.priority}
            title={item.priority}
            value={item.count}
            description="Recorded incidents"
            icon="⚑"
          />
        ))}
      </div>

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Priority-wise Incidents</h2>
            <p>Review the priority and current status of complaints.</p>
          </div>
        </div>

        <IncidentTable
          incidents={incidents.filter(
            (incident) =>
              !isResolved(incident) &&
              getPriority(incident).toLowerCase() !== "not set"
          )}
        />
      </section>

      <DataNotice>
        Priority is displayed from the incident record. This page
        does not change priority or trigger escalation.
      </DataNotice>
    </>
  );
}

/* -------------------- RECURRING PAGE -------------------- */

function RecurringPage({ incidents }) {
  const recurringIncidents = incidents.filter(isRecurring);

  return (
    <>
      <PageHeader
        title="Recurring Complaints"
        description="Identify incidents marked as repeated or recurring."
      />

      <div className="admin-stats-grid">
        <StatCard
          title="Recurring Complaints"
          value={recurringIncidents.length}
          description="Records with recurrence information"
          icon="↻"
        />
      </div>

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Recurring Incident Records</h2>
            <p>Complaints identified by recurrence fields.</p>
          </div>
        </div>

        <IncidentTable incidents={recurringIncidents} />
      </section>

      <DataNotice>
        Only records containing a recurring flag or recurrence count
        can appear here. The backend must provide those fields.
      </DataNotice>
    </>
  );
}

/* -------------------- OVERDUE PAGE -------------------- */

function OverduePage({ incidents }) {
  const overdueIncidents = incidents.filter(isOverdue);

  return (
    <>
      <PageHeader
        title="Overdue Complaints"
        description="Monitor unresolved incidents that have passed their recorded deadlines."
      />

      <div className="admin-stats-grid">
        <StatCard
          title="Overdue Complaints"
          value={overdueIncidents.length}
          description="Based on available due dates"
          icon="◷"
        />
      </div>

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Overdue Incident List</h2>
            <p>Unresolved incidents past their recorded deadline.</p>
          </div>
        </div>

        <IncidentTable incidents={overdueIncidents} />
      </section>

      <DataNotice>
        Overdue detection requires a due date, deadline or SLA deadline
        in the incident data. Records without these fields cannot be
        classified as overdue.
      </DataNotice>
    </>
  );
}

/* -------------------- RESOLVED PAGE -------------------- */

function ResolvedPage({ incidents }) {
  const resolvedIncidents = incidents.filter(isResolved);

  return (
    <>
      <PageHeader
        title="Resolved Complaints"
        description="Review incidents marked as resolved, closed or completed."
      />

      <div className="admin-stats-grid">
        <StatCard
          title="Resolved Complaints"
          value={resolvedIncidents.length}
          description="Completed incident records"
          icon="✓"
        />
      </div>

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Resolved Incident Records</h2>
            <p>All incidents currently marked as resolved.</p>
          </div>
        </div>

        <IncidentTable incidents={resolvedIncidents} />
      </section>
    </>
  );
}

/* -------------------- NOTIFICATIONS PAGE -------------------- */

function NotificationsPage() {
  return (
    <>
      <PageHeader
        title="Staff Notifications"
        description="Staff announcements and campus-wide communication."
      />

      <section className="admin-panel">
        <div className="admin-panel-header">
          <div>
            <h2>Announcement Centre</h2>
            <p>
              A dedicated space for important staff announcements.
            </p>
          </div>
        </div>

        <EmptyState message="The announcement service is not connected yet. Notifications can be enabled once the backend endpoint is available." />

        <DataNotice>
          Creating, sending and storing notifications requires a
          backend notifications endpoint.
        </DataNotice>
      </section>
    </>
  );
}

/* -------------------- ANALYTICS PAGE -------------------- */

function AnalyticsPage({ incidents }) {
  const categoryCounts = useMemo(() => {
    const counts = {};

    incidents.forEach((incident) => {
      const category = getCategory(incident);
      counts[category] = (counts[category] || 0) + 1;
    });

    return Object.entries(counts).sort(
      (a, b) => b[1] - a[1]
    );
  }, [incidents]);

  const statusCounts = useMemo(() => {
    const counts = {};

    incidents.forEach((incident) => {
      const status = getStatus(incident);
      counts[status] = (counts[status] || 0) + 1;
    });

    return Object.entries(counts).sort(
      (a, b) => b[1] - a[1]
    );
  }, [incidents]);

  return (
    <>
      <PageHeader
        title="Analytics"
        description="Understand incident patterns across the campus."
      />

      <div className="admin-stats-grid">
        <StatCard
          title="Total Incidents"
          value={incidents.length}
          description="Records available for analysis"
          icon="▥"
        />

        <StatCard
          title="Incident Categories"
          value={categoryCounts.length}
          description="Distinct recorded categories"
          icon="▤"
        />

        <StatCard
          title="Incident Statuses"
          value={statusCounts.length}
          description="Distinct recorded statuses"
          icon="◷"
        />
      </div>

      <div className="admin-analytics-grid">
        <section className="admin-panel">
          <div className="admin-panel-header">
            <div>
              <h2>Incidents by Category</h2>
              <p>Distribution of recorded incident types.</p>
            </div>
          </div>

          {categoryCounts.length === 0 ? (
            <EmptyState message="Category data is not available." />
          ) : (
            categoryCounts.map(([category, count]) => (
              <div className="admin-analytics-row" key={category}>
                <div className="admin-analytics-label">
                  <span>{category}</span>
                  <strong>{count}</strong>
                </div>

                <div className="admin-progress-track">
                  <div
                    className="admin-progress-fill"
                    style={{
                      width: `${(count / incidents.length) * 100}%`,
                    }}
                  />
                </div>
              </div>
            ))
          )}
        </section>

        <section className="admin-panel">
          <div className="admin-panel-header">
            <div>
              <h2>Incidents by Status</h2>
              <p>Current status distribution.</p>
            </div>
          </div>

          {statusCounts.length === 0 ? (
            <EmptyState message="Status data is not available." />
          ) : (
            statusCounts.map(([status, count]) => (
              <div className="admin-analytics-row" key={status}>
                <div className="admin-analytics-label">
                  <span>{status}</span>
                  <strong>{count}</strong>
                </div>

                <div className="admin-progress-track">
                  <div
                    className="admin-progress-fill"
                    style={{
                      width: `${(count / incidents.length) * 100}%`,
                    }}
                  />
                </div>
              </div>
            ))
          )}
        </section>
      </div>

      <DataNotice>
        These summaries are calculated from the incident records
        currently returned by the API. Historical trends and
        department performance require additional backend data.
      </DataNotice>
    </>
  );
}

/* -------------------- MAIN ADMIN DASHBOARD -------------------- */

function AdminDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    async function loadIncidents() {
      try {
        setLoading(true);
        setError("");

        const data = await getIncidents();

        if (isMounted) {
          setIncidents(normaliseIncidents(data));
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err?.message ||
            "Unable to load incidents. Please check the backend connection."
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

  const pageProps = { incidents };

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <div className="admin-brand-icon">SC</div>

          <div>
            <h2>SMART CAMPUS</h2>
            <p>Administration</p>
          </div>
        </div>

        <div className="admin-sidebar-heading">
          MANAGEMENT
        </div>

        <nav className="admin-navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.to || `/admin/${item.path}`}
              state={{ from: item.from || "/admin/overview" }}
              className={({ isActive }) =>
                `admin-nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="admin-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="admin-sidebar-footer">
          <p>SMART CAMPUS</p>
          <span>Incident Management System</span>
        </div>
      </aside>

      <main className="admin-main">
        <header className="admin-topbar">
          <div>
            <p>Campus Administration</p>
            <span>Incident & Responsibility Management</span>
          </div>

          <button
            className="admin-topbar-button"
            onClick={() => navigate("/login")}
          >
            Logout
          </button>
        </header>

        <div className="admin-content">
          {loading && (
            <div className="admin-loading">
              Loading campus incident data...
            </div>
          )}

          {error && (
            <div className="admin-error">
              <strong>Unable to load data</strong>
              <p>{error}</p>

              <button
                onClick={() => window.location.reload()}
              >
                Try Again
              </button>
            </div>
          )}

          <Routes>
            <Route
              index
              element={<Navigate to="overview" replace />}
            />

            <Route
              path="overview"
              element={<OverviewPage {...pageProps} />}
            />

            <Route
              path="incidents"
              element={<AllComplaintsPage {...pageProps} />}
            />

            <Route
              path="assignments"
              element={<AssignmentsPage {...pageProps} />}
            />

            <Route
              path="priority"
              element={<PriorityPage {...pageProps} />}
            />

            <Route
              path="recurring"
              element={<RecurringPage {...pageProps} />}
            />

            <Route
              path="overdue"
              element={<OverduePage {...pageProps} />}
            />

            <Route
              path="resolved"
              element={<ResolvedPage {...pageProps} />}
            />

            <Route
              path="notifications"
              element={<NotificationsPage />}
            />

            <Route
              path="analytics"
              element={<AnalyticsPage {...pageProps} />}
            />

            <Route
              path="*"
              element={<Navigate to="overview" replace />}
            />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default AdminDashboard;
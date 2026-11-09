
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "./StaffDashboard.css";

// Keep false until Member 4 confirms that GET /incidents
// returns only records belonging to the authenticated staff member's department.
const DEPARTMENT_SCOPE_CONFIRMED = false;

const NAV_ITEMS = [
  { label: "Overview", path: "/staff/overview", icon: "⌂" },
  { label: "My Assigned Tasks", path: "/staff/my-tasks", icon: "✓" },
  {
    label: "Department Complaints",
    path: "/staff/department-complaints",
    icon: "▤",
  },
  { label: "Staff Workload", path: "/staff/workload", icon: "♧" },
  { label: "Priority Monitoring", path: "/staff/priorities", icon: "⚑" },
  { label: "Resolved Complaints", path: "/staff/resolved", icon: "◉" },
  { label: "Notifications", path: "/staff/notifications", icon: "♢" },
];

// --------------------------------------------------
// HELPER FUNCTIONS
// --------------------------------------------------

function getIncidentList(response) {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response?.incidents)) return response.incidents;
  if (Array.isArray(response?.data)) return response.data;
  if (Array.isArray(response?.items)) return response.items;
  if (Array.isArray(response?.results)) return response.results;

  return [];
}

function titleOf(item) {
  return item?.title || item?.subject || item?.name || "Untitled complaint";
}

function idOf(item) {
  return item?.incident_id ?? item?.id ?? "—";
}

function clean(value) {
  return String(value ?? "").replaceAll("_", " ").replaceAll("-", " ");
}

function statusOf(item) {
  return clean(item?.status || "Unknown").replace(/\b\w/g, (char) =>
    char.toUpperCase()
  );
}

function statusClass(item) {
  const value = clean(item?.status).toLowerCase();

  if (value.includes("progress")) return "progress";

  if (
    value.includes("closed") ||
    value.includes("resolved") ||
    value.includes("completed")
  ) {
    return "resolved";
  }

  if (value.includes("assign")) return "assigned";
  if (value.includes("reject")) return "rejected";

  return "reported";
}

function priorityOf(item) {
  return item?.priority ?? item?.priority_level ?? item?.urgency ?? null;
}

function priorityClass(value) {
  const priority = String(value || "").toLowerCase();

  if (priority.includes("critical") || priority.includes("emergency")) {
    return "critical";
  }

  if (priority.includes("high")) return "high";
  if (priority.includes("medium")) return "medium";
  if (priority.includes("low")) return "low";

  return "unknown";
}

function dateOf(item) {
  const value = item?.created_at || item?.createdAt || item?.date;

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

function timestampOf(item) {
  const value = item?.created_at || item?.createdAt || item?.date;

  if (!value) return 0;

  const timestamp = new Date(value).getTime();

  return Number.isNaN(timestamp) ? 0 : timestamp;
}

function isResolved(item) {
  const value = clean(item?.status).toLowerCase();

  return (
    value.includes("closed") ||
    value.includes("resolved") ||
    value.includes("completed")
  );
}

// --------------------------------------------------
// REUSABLE UI COMPONENTS
// --------------------------------------------------

function Notice({ title, children }) {
  return (
    <div className="staff-notice">
      <strong>{title}</strong>
      <p>{children}</p>
    </div>
  );
}

function EmptyState({ title, children }) {
  return (
    <div className="staff-empty">
      <span>◇</span>
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}

function PriorityPill({ value }) {
  if (!value) {
    return <span className="staff-priority unknown">Not provided</span>;
  }

  return (
    <span className={`staff-priority ${priorityClass(value)}`}>
      {clean(value)}
    </span>
  );
}

function StatusPill({ item }) {
  return (
    <span className={`staff-status ${statusClass(item)}`}>
      {statusOf(item)}
    </span>
  );
}

function IncidentTable({ items, showPriority = true }) {
  if (!items.length) {
    return (
      <EmptyState title="No complaints to show">
        There are no matching complaints in the data currently available to
        this account.
      </EmptyState>
    );
  }

  return (
    <div className="staff-table-wrap">
      <table className="staff-table">
        <thead>
          <tr>
            <th>Complaint</th>
            <th>Category</th>
            <th>Location</th>
            {showPriority && <th>Priority</th>}
            <th>Reported</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {items.map((item, index) => {
            const id = idOf(item);

            return (
              <tr key={id === "—" ? `incident-${index}` : id}>
                <td>
                  <strong>{id}</strong>
                  <small>{titleOf(item)}</small>
                </td>

                <td>{item?.category || "—"}</td>
                <td>{item?.location || "—"}</td>

                {showPriority && (
                  <td>
                    <PriorityPill value={priorityOf(item)} />
                  </td>
                )}

                <td>{dateOf(item)}</td>

                <td>
                  <StatusPill item={item} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function PageHeading({
  eyebrow = "STAFF WORKSPACE",
  title,
  description,
  action,
}) {
  return (
    <div className="staff-page-heading">
      <div>
        <span className="staff-eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>

      {action}
    </div>
  );
}

// --------------------------------------------------
// OVERVIEW PAGE
// --------------------------------------------------

function Overview({ incidents, loading, error, loadIncidents, counts }) {
  const recentIncidents = useMemo(
    () =>
      [...incidents]
        .sort((a, b) => timestampOf(b) - timestampOf(a))
        .slice(0, 5),
    [incidents]
  );

  return (
    <>
      <PageHeading
        title="Welcome to your workspace"
        description="A summary of the incident records returned by the currently connected service."
        action={
          <button
            className="staff-button secondary"
            onClick={loadIncidents}
            disabled={loading}
            type="button"
          >
            {loading ? "Refreshing…" : "↻ Refresh"}
          </button>
        }
      />

      {error && (
        <Notice title="Complaint data unavailable">
          {error} The dashboard will not substitute sample data.
        </Notice>
      )}

      <div className="staff-metrics">
        <article className="staff-metric">
          <span>Records returned</span>
          <strong>{loading || error ? "—" : counts.total}</strong>
          <small>From the currently connected incidents service</small>
        </article>

        <article className="staff-metric">
          <span>Open / active records</span>
          <strong>{loading || error ? "—" : counts.open}</strong>
          <small>Not marked resolved or closed</small>
        </article>

        <article className="staff-metric">
          <span>High / critical priority</span>
          <strong>{loading || error ? "—" : counts.urgent}</strong>
          <small>Only where priority is supplied by the backend</small>
        </article>

        <article className="staff-metric">
          <span>Resolved records</span>
          <strong>{loading || error ? "—" : counts.resolved}</strong>
          <small>Marked resolved, closed or completed</small>
        </article>
      </div>

      <div className="staff-panel">
        <div className="staff-panel-heading">
          <div>
            <h2>Recent incident records</h2>
            <p>Latest records returned by the current service.</p>
          </div>
        </div>

        {loading ? (
          <EmptyState title="Loading complaints">
            Please wait while complaint data is retrieved.
          </EmptyState>
        ) : error ? (
          <EmptyState title="Activity is unavailable">
            Try refreshing once the incidents service is reachable.
          </EmptyState>
        ) : !DEPARTMENT_SCOPE_CONFIRMED ? (
          <EmptyState title="Department records are awaiting API confirmation">
            Recent complaints will appear here once the backend confirms that
            records are restricted to your department.
          </EmptyState>
        ) : (
          <IncidentTable items={recentIncidents} />
        )}
      </div>

      {!DEPARTMENT_SCOPE_CONFIRMED && (
        <Notice title="Department-specific access is awaiting API confirmation">
          The frontend currently uses the general incidents service. We have
          not yet confirmed that its response is restricted to this staff
          member’s department. Department-specific figures and records are
          therefore withheld until the access scope is verified.
        </Notice>
      )}
    </>
  );
}

// --------------------------------------------------
// MY TASKS PAGE
// --------------------------------------------------

function MyTasks() {
  return (
    <>
      <PageHeading
        title="My Assigned Tasks"
        description="Tasks assigned specifically to your staff account."
      />

      <Notice title="Personal assignment feed not connected">
        The current frontend service has no confirmed staff-specific
        assignments endpoint or verified current-user assignment field. We
        will not guess ownership from names or display another staff
        member’s tasks as yours.
      </Notice>

      <EmptyState title="Your task list is waiting for the assignment API">
        Once Member 4 confirms the staff assignment contract, this page can
        show your assigned complaints and permitted progress actions.
      </EmptyState>
    </>
  );
}

// --------------------------------------------------
// DEPARTMENT COMPLAINTS PAGE
// --------------------------------------------------

function DepartmentComplaints() {
  return (
    <>
      <PageHeading
        title="Department Complaints"
        description="Complaints associated with your department, with read-only access to department activity."
      />

      <Notice title="Department filter needs backend support">
        The current GET /incidents response has not been confirmed to include
        a trusted staff department and department-scoped results. Filtering
        in the browser would not protect other departments’ data, so this
        page will not present general incidents as department-only
        complaints.
      </Notice>

      <EmptyState title="Department complaint data is not available yet">
        This section will display records after the backend provides a
        department-scoped response for the authenticated staff account.
      </EmptyState>
    </>
  );
}

// --------------------------------------------------
// STAFF WORKLOAD PAGE
// --------------------------------------------------

function Workload() {
  return (
    <>
      <PageHeading
        title="Staff Workload"
        description="See how work is distributed among colleagues in your department."
      />

      <Notice title="Staff workload data is not connected">
        This page needs the authenticated department roster and assignment
        data from the backend. Staff will be able to view colleagues’
        assigned work, but only update their own tasks.
      </Notice>

      <EmptyState title="Workload view is awaiting staff data">
        No colleague names, task counts or assignments will be fabricated.
      </EmptyState>
    </>
  );
}

// --------------------------------------------------
// PRIORITY MONITORING PAGE
// --------------------------------------------------

function Priorities({ incidents, loading, error, search, setSearch }) {
  const prioritized = useMemo(() => {
    const rank = (value) => {
      const priority = String(value || "").toLowerCase();

      if (
        priority.includes("critical") ||
        priority.includes("emergency")
      ) {
        return 0;
      }

      if (priority.includes("high")) return 1;
      if (priority.includes("medium")) return 2;
      if (priority.includes("low")) return 3;

      return 4;
    };

    return incidents
      .filter((item) => priorityOf(item))
      .sort((a, b) => rank(priorityOf(a)) - rank(priorityOf(b)));
  }, [incidents]);

  const searched = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return prioritized;

    return prioritized.filter((item) => {
      const text = [
        idOf(item),
        titleOf(item),
        item?.category,
        item?.location,
        priorityOf(item),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return text.includes(query);
    });
  }, [prioritized, search]);

  return (
    <>
      <PageHeading
        title="Priority Monitoring"
        description="Review priorities set by the Admin. Staff can view priorities but cannot change them."
      />

      <div className="staff-priority-key">
        <PriorityPill value="Critical" />
        <PriorityPill value="High" />
        <PriorityPill value="Medium" />
        <PriorityPill value="Low" />
      </div>

      <label className="staff-search">
        <span>Search complaints</span>
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by ID, title, category or location…"
        />
      </label>

      {error && <Notice title="Priority data unavailable">{error}</Notice>}

      {!loading && !error && !DEPARTMENT_SCOPE_CONFIRMED && (
        <Notice title="Department-scoped priority data is awaiting confirmation">
          Priority labels are read-only, but the current incidents response
          has not been confirmed as department-scoped. Records are therefore
          withheld here until that access scope is verified.
        </Notice>
      )}

      {!loading &&
        !error &&
        DEPARTMENT_SCOPE_CONFIRMED &&
        searched.length === 0 && (
          <EmptyState title="No priority values returned">
            Priority labels will appear here once Admin-set priorities are
            included in the department-scoped complaint response.
          </EmptyState>
        )}

      {!loading &&
        !error &&
        DEPARTMENT_SCOPE_CONFIRMED &&
        searched.length > 0 && <IncidentTable items={searched} />}

      {loading && (
        <EmptyState title="Loading priority data">
          Retrieving complaint priorities from the incidents service.
        </EmptyState>
      )}

      <p className="staff-muted">
        Priority is read-only here. Changes remain under Admin control.
      </p>
    </>
  );
}

// --------------------------------------------------
// RESOLVED COMPLAINTS PAGE
// --------------------------------------------------

function Resolved({ incidents, loading, error }) {
  const resolvedIncidents = useMemo(
    () => incidents.filter(isResolved),
    [incidents]
  );

  return (
    <>
      <PageHeading
        title="Resolved Complaints"
        description="Review complaints marked resolved, closed or completed."
      />

      {loading ? (
        <EmptyState title="Loading resolved complaints">
          Please wait…
        </EmptyState>
      ) : error ? (
        <Notice title="Resolved complaints unavailable">{error}</Notice>
      ) : !DEPARTMENT_SCOPE_CONFIRMED ? (
        <Notice title="Department-scoped resolved records are awaiting confirmation">
          The current incidents response has not been confirmed as restricted
          to your department. Resolved records are withheld here until that
          access scope is verified.
        </Notice>
      ) : (
        <IncidentTable items={resolvedIncidents} />
      )}
    </>
  );
}

// --------------------------------------------------
// NOTIFICATIONS PAGE
// --------------------------------------------------

function Notifications() {
  return (
    <>
      <PageHeading
        title="Notifications"
        description="Assignment alerts, complaint updates and campus announcements."
      />

      <Notice title="Notification feed not connected">
        The current API contract does not include a staff notifications or
        announcements endpoint. When available, this page will show updates
        relevant to your department and account.
      </Notice>

      <EmptyState title="No notification feed connected">
        No sample notifications are shown, to avoid confusing demo content
        with real campus updates.
      </EmptyState>
    </>
  );
}

// --------------------------------------------------
// MAIN STAFF DASHBOARD
// --------------------------------------------------

function StaffDashboard() {
  const navigate = useNavigate();
  const location = useLocation();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const loadIncidents = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await getIncidents();
      setIncidents(getIncidentList(response));
    } catch (err) {
      setError(
        err?.message || "Unable to load complaints. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  const counts = useMemo(
    () => ({
      total: incidents.length,
      open: incidents.filter((item) => !isResolved(item)).length,
      resolved: incidents.filter(isResolved).length,
      urgent: incidents.filter((item) => {
        const priority = String(priorityOf(item) || "").toLowerCase();

        return (
          priority.includes("critical") ||
          priority.includes("emergency") ||
          priority.includes("high")
        );
      }).length,
    }),
    [incidents]
  );

  const logout = () => {
    // Confirm the token key with auth.js before changing this.
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  };

  const currentPath = location.pathname.replace(/\/$/, "");

  const pageInfo =
    NAV_ITEMS.find((item) => item.path === currentPath) || NAV_ITEMS[0];

  return (
    <div className="staff-dashboard">
      <aside className="staff-sidebar">
        <div className="staff-brand">
          <div className="staff-brand-mark">SC</div>
          <span>SMART CAMPUS</span>
        </div>

        <p className="staff-sidebar-label">STAFF MENU</p>

        <nav className="staff-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `staff-nav-link${isActive ? " active" : ""}`
              }
            >
              <span className="staff-nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="staff-sidebar-bottom">
          <div className="staff-help">
            <span className="staff-help-icon">?</span>
            <div>
              <strong>Need assistance?</strong>
              <p>Contact your campus administrator for support.</p>
            </div>
          </div>

          <button
            className="staff-logout"
            onClick={logout}
            type="button"
          >
            ↪ Logout
          </button>
        </div>
      </aside>

      <main className="staff-main">
        <header className="staff-topbar">
          <div>
            <span className="staff-topbar-label">STAFF PORTAL</span>
            <strong className="staff-topbar-brand">SMART CAMPUS</strong>
          </div>

          <div className="staff-avatar">S</div>
        </header>

        <div className="staff-content">
          <div className="staff-breadcrumb">
            Staff Portal <span>/</span> {pageInfo.label}
          </div>

          <Routes>
            <Route index element={<Navigate to="overview" replace />} />

            <Route
              path="overview"
              element={
                <Overview
                  incidents={incidents}
                  loading={loading}
                  error={error}
                  loadIncidents={loadIncidents}
                  counts={counts}
                />
              }
            />

            <Route path="my-tasks" element={<MyTasks />} />

            <Route
              path="department-complaints"
              element={<DepartmentComplaints />}
            />

            <Route path="workload" element={<Workload />} />

            <Route
              path="priorities"
              element={
                <Priorities
                  incidents={incidents}
                  loading={loading}
                  error={error}
                  search={search}
                  setSearch={setSearch}
                />
              }
            />

            <Route
              path="resolved"
              element={
                <Resolved
                  incidents={incidents}
                  loading={loading}
                  error={error}
                />
              }
            />

            <Route path="notifications" element={<Notifications />} />

            <Route path="*" element={<Navigate to="overview" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default StaffDashboard;

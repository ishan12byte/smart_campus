
import React, { useState } from "react";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate
} from "react-router-dom";
import "./SuperAdminDashboard.css";

const navigation = [
  { label: "Overview", path: "overview", icon: "▦" },
  { label: "Department Performance", path: "departments", icon: "▤" },
  { label: "Campus Monitoring", path: "monitoring", icon: "◎" },
  { label: "Staff & Resources", path: "resources", icon: "♙" },
  { label: "Analytics", path: "analytics", icon: "▥" },
  { label: "Announcements", path: "announcements", icon: "♢" },
];

function PageHeader({ title, description }) {
  return (
    <div className="super-page-header">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <span className="super-data-label">AWAITING INTEGRATION</span>
    </div>
  );
}

function StatCard({ icon, title }) {
  return (
    <div className="super-stat-card">
      <div className="super-stat-icon">{icon}</div>
      <div>
        <p className="super-stat-title">{title}</p>
        <h2>—</h2>
        <span>Awaiting backend data</span>
      </div>
    </div>
  );
}

function EmptyState({ title, description }) {
  return (
    <div className="super-empty-state">
      <div className="super-empty-icon">▤</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function IncidentTable({ incidents = [], emptyMessage }) {
  return (
    <div className="super-table-wrapper">
      <table className="super-table">
        <thead>
          <tr>
            <th>Incident ID</th>
            <th>Incident</th>
            <th>Department</th>
            <th>Priority</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {incidents.length === 0 ? (
            <tr>
              <td colSpan="5" className="super-table-empty">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            incidents.map((incident, index) => (
              <tr key={incident.id || incident.incident_id || index}>
                <td>{incident.id || incident.incident_id || "—"}</td>
                <td>{incident.title || "—"}</td>
                <td>{incident.department || "—"}</td>
                <td>{incident.priority || "—"}</td>
                <td>{incident.status || "—"}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function Overview() {
  return (
    <>
      <PageHeader
        title="Super Admin Overview"
        description="A campus-wide view of incident management and institutional performance."
      />

      <div className="super-stats-grid">
        <StatCard icon="▣" title="Total Incidents" />
        <StatCard icon="✓" title="Resolved Incidents" />
        <StatCard icon="◷" title="Pending Incidents" />
        <StatCard icon="⚑" title="Overdue Incidents" />
        <StatCard icon="▤" title="Departments" />
        <StatCard icon="♙" title="Staff Members" />
      </div>

      <div className="super-content-grid">
        <section className="super-panel">
          <div className="super-panel-heading">
            <div>
              <h2>Department Snapshot</h2>
              <p>
                Incident distribution and resolution performance by department.
              </p>
            </div>
          </div>

          <EmptyState
            title="Department data unavailable"
            description="Department names, incident counts and resolution progress will appear here after backend integration."
          />
        </section>

        <section className="super-panel">
          <div className="super-panel-heading">
            <div>
              <h2>Incident Summary</h2>
              <p>Campus-wide incident status breakdown.</p>
            </div>
          </div>

          {[
            "Resolved Incidents",
            "Pending Incidents",
            "Overdue Incidents",
            "Total Incidents"
          ].map((label) => (
            <div className="super-summary-row" key={label}>
              <span>{label}</span>
              <strong>—</strong>
            </div>
          ))}

          <p className="super-panel-note">
            Values will be populated from the backend.
          </p>
        </section>
      </div>

      <section className="super-panel super-table-panel">
        <div className="super-panel-heading">
          <div>
            <h2>Recent Campus Incidents</h2>
            <p>Latest incidents received across the campus.</p>
          </div>
        </div>

        <IncidentTable
          emptyMessage="Recent incident records will appear here after API integration."
        />
      </section>
    </>
  );
}

function Departments({ departments = [] }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("name");

  const filteredDepartments = departments
    .filter((department) =>
      String(department.name || "")
        .toLowerCase()
        .includes(searchTerm.trim().toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "incidents") {
        return (
          (Number(b.totalIncidents) || 0) -
          (Number(a.totalIncidents) || 0)
        );
      }

      if (sortBy === "resolution") {
        return (
          (Number(b.resolutionRate) || 0) -
          (Number(a.resolutionRate) || 0)
        );
      }

      return String(a.name || "").localeCompare(String(b.name || ""));
    });

  return (
    <>
      <PageHeader
        title="Department Performance"
        description="Compare incident volume and resolution performance across departments."
      />

      <div className="super-stats-grid">
        <StatCard icon="▤" title="Total Departments" />
        <StatCard icon="▣" title="Total Incidents" />
        <StatCard icon="✓" title="Resolved Incidents" />
      </div>

      <section className="super-panel super-table-panel">
        <div className="super-panel-heading">
          <div>
            <h2>Department Comparison</h2>
            <p>
              Compare workload and resolution performance across departments.
            </p>
          </div>
        </div>

        <div className="super-filter-bar">
          <input
            type="text"
            placeholder="Search department..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="name">Sort by department</option>
            <option value="incidents">Highest incident volume</option>
            <option value="resolution">Highest resolution rate</option>
          </select>

          <button
            type="button"
            className="super-clear-filter"
            onClick={() => {
              setSearchTerm("");
              setSortBy("name");
            }}
            disabled={!searchTerm && sortBy === "name"}
          >
            Reset
          </button>
        </div>

        <div className="super-filter-result">
          Showing {filteredDepartments.length} departments
        </div>

        <div className="super-table-wrapper">
          <table className="super-table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Total Incidents</th>
                <th>Resolved</th>
                <th>Pending</th>
                <th>Overdue</th>
                <th>Resolution Rate</th>
              </tr>
            </thead>

            <tbody>
              {filteredDepartments.length === 0 ? (
                <tr>
                  <td colSpan="6" className="super-table-empty">
                    {departments.length === 0
                      ? "Department performance data will appear here after backend integration."
                      : "No departments match your search."}
                  </td>
                </tr>
              ) : (
                filteredDepartments.map((department, index) => {
                  const rate = Number(department.resolutionRate);

                  return (
                    <tr key={department.id || index}>
                      <td>{department.name || "—"}</td>
                      <td>{department.totalIncidents ?? "—"}</td>
                      <td>{department.resolved ?? "—"}</td>
                      <td>{department.pending ?? "—"}</td>
                      <td>{department.overdue ?? "—"}</td>
                      <td>
                        {Number.isFinite(rate) ? `${rate}%` : "—"}

                        {Number.isFinite(rate) && (
                          <div
                            style={{
                              height: "6px",
                              background: "#edf0f5",
                              borderRadius: "10px",
                              marginTop: "7px",
                              overflow: "hidden",
                              minWidth: "65px",
                            }}
                          >
                            <div
                              style={{
                                height: "100%",
                                width: `${Math.min(100, Math.max(0, rate))}%`,
                                background: "#315ce8",
                                borderRadius: "10px",
                              }}
                            />
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="super-info-note">
          Department comparisons and resolution rates require verified campus-wide data.
          The frontend is prepared to display these values when supplied through integration.
        </div>
      </section>
    </>
  );
}

function Monitoring({ incidents = [] }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredIncidents = incidents.filter((incident) => {
    const searchableText = [
      incident.id,
      incident.incident_id,
      incident.title,
      incident.department,
      incident.priority,
      incident.status,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    const matchesSearch = searchableText.includes(
      searchTerm.trim().toLowerCase()
    );

    const normalizedStatus = String(incident.status || "")
      .toLowerCase()
      .trim();

    return (
      matchesSearch &&
      (statusFilter === "all" || normalizedStatus === statusFilter)
    );
  });

  const hasFilters =
    searchTerm.trim() !== "" || statusFilter !== "all";

  return (
    <>
      <PageHeader
        title="Campus Monitoring"
        description="Monitor incidents and their status across the entire campus."
      />

      <div className="super-stats-grid">
        <StatCard icon="▣" title="Total Incidents" />
        <StatCard icon="⚑" title="Critical Incidents" />
        <StatCard icon="◷" title="In Progress" />
      </div>

      <section className="super-panel super-table-panel">
        <div className="super-panel-heading">
          <div>
            <h2>Campus Incident Register</h2>
            <p>Search and monitor campus-wide incident records.</p>
          </div>
        </div>

        <div className="super-filter-bar">
          <input
            type="text"
            placeholder="Search by ID, incident, department or priority..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All statuses</option>
            <option value="pending">Pending</option>
            <option value="in progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="overdue">Overdue</option>
          </select>

          <button
            type="button"
            className="super-clear-filter"
            onClick={() => {
              setSearchTerm("");
              setStatusFilter("all");
            }}
            disabled={!hasFilters}
          >
            Clear Filters
          </button>
        </div>

        <div className="super-filter-result">
          Showing {filteredIncidents.length} incident
          {filteredIncidents.length !== 1 ? "s" : ""}
        </div>

        <IncidentTable
          incidents={filteredIncidents}
          emptyMessage={
            incidents.length === 0
              ? "Campus incident records will appear here after API integration."
              : "No incidents match your search or selected filters."
          }
        />

        <div className="super-info-note">
          Actual campus incident records will be supplied through backend integration.
        </div>
      </section>
    </>
  );
}

function Resources() {
  return (
    <>
      <PageHeader
        title="Staff & Resources"
        description="Review staff distribution and workload across departments."
      />

      <div className="super-stats-grid">
        <StatCard icon="♙" title="Total Staff" />
        <StatCard icon="▣" title="Assigned Tasks" />
        <StatCard icon="✓" title="Completed Tasks" />
      </div>

      <section className="super-panel super-table-panel">
        <div className="super-panel-heading">
          <div>
            <h2>Department Staff Distribution</h2>
            <p>Staff availability and workload overview.</p>
          </div>
        </div>

        <div className="super-table-wrapper">
          <table className="super-table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Staff Members</th>
                <th>Assigned Tasks</th>
                <th>Completed Tasks</th>
                <th>Workload</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td colSpan="5" className="super-table-empty">
                  Staff and workload information will appear here after backend integration.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="super-info-note">
          Workload and resource information will be displayed using authorized backend data.
        </div>
      </section>
    </>
  );
}

function Analytics() {
  return (
    <>
      <PageHeader
        title="Campus Analytics"
        description="Explore incident trends and resolution performance."
      />

      <div className="super-stats-grid">
        <StatCard icon="▥" title="Total Recorded Incidents" />
        <StatCard icon="↗" title="Average Resolution Rate" />
        <StatCard icon="✓" title="Resolved Incidents" />
      </div>

      <section className="super-panel">
        <div className="super-panel-heading">
          <div>
            <h2>Monthly Incident Trends</h2>
            <p>Historical incident volume and resolution trends.</p>
          </div>
        </div>

        <div className="super-chart-placeholder">
          <div className="super-chart-grid">
            <span>100</span>
            <span>75</span>
            <span>50</span>
            <span>25</span>
            <span>0</span>
          </div>

          <div className="super-chart-message">
            <div className="super-empty-icon">▥</div>
            <h3>Analytics data unavailable</h3>
            <p>
              Monthly incident and resolution data will be visualized here after integration.
            </p>
          </div>
        </div>

        <div className="super-chart-legend">
          <span>
            <i className="legend-total" /> Total incidents
          </span>
          <span>
            <i className="legend-resolved" /> Resolved incidents
          </span>
        </div>
      </section>

      <section className="super-panel">
        <div className="super-panel-heading">
          <div>
            <h2>Resolution Performance</h2>
            <p>Campus-wide resolution performance analysis.</p>
          </div>
        </div>

        <EmptyState
          title="Performance data unavailable"
          description="Resolution time and performance indicators will appear here when the backend provides the required data."
        />
      </section>
    </>
  );
}

function Announcements() {
  const [announcements, setAnnouncements] = useState([]);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(e) {
    e.preventDefault();

    if (!title.trim() || !message.trim()) return;

    setAnnouncements((previous) => [
      {
        id: Date.now(),
        title: title.trim(),
        message: message.trim(),
      },
      ...previous,
    ]);

    setTitle("");
    setMessage("");
  }

  return (
    <>
      <PageHeader
        title="Campus Announcements"
        description="Prepare and manage campus-wide announcements."
      />

      <div className="super-announcement-grid">
        <section className="super-panel">
          <div className="super-panel-heading">
            <div>
              <h2>Create Announcement</h2>
              <p>Write a new campus announcement.</p>
            </div>
          </div>

          <form
            className="super-announcement-form"
            onSubmit={handleSubmit}
          >
            <label htmlFor="announcement-title">
              Announcement Title
            </label>

            <input
              id="announcement-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter announcement title"
              required
            />

            <label htmlFor="announcement-message">
              Announcement Message
            </label>

            <textarea
              id="announcement-message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Write your announcement..."
              rows="5"
              required
            />

            <button type="submit">
              Add Announcement Preview
            </button>
          </form>

          <div className="super-info-note">
            Frontend preview only. Announcements are not saved permanently or distributed to users until a backend announcement service is connected.
          </div>
        </section>

        <section className="super-panel">
          <div className="super-panel-heading">
            <div>
              <h2>Recent Announcements</h2>
              <p>Announcements added during this session.</p>
            </div>
          </div>

          {announcements.length === 0 ? (
            <EmptyState
              title="No announcements yet"
              description="Announcements you create will appear here during this session."
            />
          ) : (
            <div className="super-announcement-list">
              {announcements.map((item) => (
                <article
                  className="super-announcement"
                  key={item.id}
                >
                  <span>Frontend session preview</span>
                  <h3>{item.title}</h3>
                  <p>{item.message}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </>
  );
}

function SuperAdminDashboard() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  }

  return (
    <div className="super-layout">
      <aside className="super-sidebar">
        <div className="super-brand">
          <div className="super-brand-icon">SC</div>
          <div>
            <h2>SMART CAMPUS</h2>
            <p>Super Administration</p>
          </div>
        </div>

        <div className="super-sidebar-heading">
          CAMPUS CONTROL
        </div>

        <nav className="super-navigation">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={`/super-admin/${item.path}`}
              className={({ isActive }) =>
                `super-nav-link ${isActive ? "active" : ""}`
              }
            >
              <span className="super-nav-icon">
                {item.icon}
              </span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="super-sidebar-footer">
          <strong>SMART CAMPUS</strong>
          <span>Incident Management System</span>
        </div>
      </aside>

      <main className="super-main">
        <header className="super-topbar">
          <div>
            <strong>Campus Control Centre</strong>
            <span>Institutional overview and administration</span>
          </div>

          <button
            className="super-logout"
            type="button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </header>

        <div className="super-content">
          <Routes>
            <Route
              index
              element={<Navigate to="overview" replace />}
            />
            <Route
              path="overview"
              element={<Overview />}
            />
            <Route
              path="departments"
              element={<Departments />}
            />
            <Route
              path="monitoring"
              element={<Monitoring />}
            />
            <Route
              path="resources"
              element={<Resources />}
            />
            <Route
              path="analytics"
              element={<Analytics />}
            />
            <Route
              path="announcements"
              element={<Announcements />}
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

export default SuperAdminDashboard;

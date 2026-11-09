import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getIncidents } from "../services/incidents";

import "./StudentDashboard.css";
import "./MyIncidents.css";

function MyIncidents() {
  const navigate = useNavigate();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [categoryFilter, setCategoryFilter] = useState("All");

  // Extract incident records from common API response formats.
  const extractIncidents = (response) => {
    if (Array.isArray(response)) {
      return response;
    }

    const possibleRecords = [
      response?.incidents,
      response?.items,
      response?.results,
      response?.data?.incidents,
      response?.data?.items,
      response?.data?.results,
      response?.data,
    ];

    return possibleRecords.find(Array.isArray) || [];
  };

  // Load incidents from the backend.
  const loadIncidents = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getIncidents();
      const records = extractIncidents(response);

      setIncidents(records);
    } catch (err) {
      setError(
        err?.message || "Unable to load your incidents. Please try again."
      );
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  // Logout.
  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  }

  // Get the incident's unique ID.
  function getIncidentId(incident) {
    return incident?.id ?? incident?.incident_id ?? incident?._id ?? null;
  }

  // Display a readable incident ID.
  function formatIncidentId(incident) {
    const id = getIncidentId(incident);

    if (id == null) {
      return "—";
    }

    return `INC-${String(id).padStart(3, "0")}`;
  }

  // Format status labels.
  function formatStatus(status) {
    if (!status) {
      return "Unknown";
    }

    return String(status)
      .replace(/[_-]+/g, " ")
      .replace(/\b\w/g, (character) => character.toUpperCase());
  }

  // Format dates.
  function formatDate(date) {
    if (!date) {
      return "—";
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return "—";
    }

    return parsedDate.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  // Assign a status style.
  function getStatusClass(status) {
    const value = String(status || "")
      .toLowerCase()
      .replace(/[\s-]+/g, "_");

    if (["closed", "resolved"].includes(value)) {
      return "status-closed";
    }

    if (["rejected", "cancelled"].includes(value)) {
      return "status-reopened";
    }

    if (
      ["in_progress", "under_review", "assigned", "in_review"].includes(value)
    ) {
      return "status-progress";
    }

    if (["open", "pending", "submitted"].includes(value)) {
      return "status-open";
    }

    return "status-default";
  }

  // Open incident details.
  function openIncidentDetails(incident) {
    const id = getIncidentId(incident);

    if (id == null) {
      return;
    }

    navigate(`/incident/${encodeURIComponent(String(id))}`);
  }

  // Available categories.
  const categories = useMemo(() => {
    return [
      ...new Set(
        incidents
          .map((incident) => incident?.category)
          .filter((category) => category != null && String(category).trim())
      ),
    ];
  }, [incidents]);

  // Available statuses.
  const statuses = useMemo(() => {
    return [
      ...new Set(
        incidents
          .map((incident) => incident?.status)
          .filter((status) => status != null && String(status).trim())
      ),
    ];
  }, [incidents]);

  // Search and filter incidents.
  const filteredIncidents = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return incidents.filter((incident) => {
      const searchableValues = [
        getIncidentId(incident),
        incident?.title,
        incident?.category,
        incident?.location,
        incident?.description,
        incident?.status,
      ];

      const matchesSearch =
        !query ||
        searchableValues.some(
          (value) =>
            value != null &&
            String(value).toLowerCase().includes(query)
        );

      const matchesStatus =
        statusFilter === "All" ||
        String(incident?.status || "").toLowerCase() ===
          statusFilter.toLowerCase();

      const matchesCategory =
        categoryFilter === "All" ||
        String(incident?.category || "").toLowerCase() ===
          categoryFilter.toLowerCase();

      return matchesSearch && matchesStatus && matchesCategory;
    });
  }, [incidents, searchTerm, statusFilter, categoryFilter]);

  // Clear all filters.
  function clearFilters() {
    setSearchTerm("");
    setStatusFilter("All");
    setCategoryFilter("All");
  }

  return (
    <div className="student-dashboard">
      {/* Student Sidebar */}
      <aside className="student-sidebar">
        <div className="student-brand">
          <div className="student-brand-mark">SC</div>
          <span>SMART CAMPUS</span>
        </div>

        <div className="sidebar-label">MAIN MENU</div>

        <nav className="student-nav">
          <button
            type="button"
            className="student-nav-link"
            onClick={() => navigate("/student")}
          >
            <span className="nav-icon">⌂</span>
            Dashboard
          </button>

          <button
            type="button"
            className="student-nav-link active"
            onClick={() => navigate("/my-incidents")}
            aria-current="page"
          >
            <span className="nav-icon">▤</span>
            My Incidents
          </button>

          <button
            type="button"
            className="student-nav-link"
            onClick={() => navigate("/report-incident")}
          >
            <span className="nav-icon">＋</span>
            Report Incident
          </button>

          <button
            type="button"
            className="student-nav-link"
            onClick={() => navigate("/student")}
          >
            <span className="nav-icon">⌕</span>
            Check Complaints
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-help">
            <span className="help-icon">?</span>

            <div>
              <strong>Need assistance?</strong>
              <p>Contact your campus administrator.</p>
            </div>
          </div>

          <button
            type="button"
            className="student-logout"
            onClick={handleLogout}
          >
            <span>↪</span>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="student-main">
        <header className="student-topbar">
          <div>
            <p className="topbar-label">STUDENT PORTAL</p>
            <p className="topbar-brand">SMART CAMPUS</p>
          </div>

          <div className="student-avatar">S</div>
        </header>

        <div className="student-content my-incidents-page">
          {/* Page Heading */}
          <section className="my-incidents-welcome">
            <div>
              <p className="welcome-date">STUDENT PORTAL</p>

              <h1>My Incidents</h1>

              <p>
                View and track the incidents you have submitted to the campus
                administration.
              </p>
            </div>

            <button
              type="button"
              className="student-primary-btn"
              onClick={() => navigate("/report-incident")}
            >
              <span>＋</span>
              Report New Incident
            </button>
          </section>

          {/* Incident Count */}
          <section className="my-incidents-count">
            <div>
              <p>Total Reports</p>

              <h2>
                {loading || error ? "—" : incidents.length}
              </h2>

              <span className="count-description">
                Your submitted campus incidents
              </span>
            </div>

            <div className="summary-icon blue-icon">▤</div>
          </section>

          {/* Main Incident Panel */}
          <section className="my-incidents-panel">
            <div className="my-incidents-panel-heading">
              <div>
                <h2>All My Reports</h2>

                <p>
                  A complete record of your submitted incidents.
                </p>
              </div>

              {!loading && !error && (
                <span className="records-count">
                  {filteredIncidents.length} of {incidents.length} reports
                </span>
              )}
            </div>

            {/* Search and Filters */}
            <div className="incident-filters">
              <div className="incident-search">
                <span aria-hidden="true">⌕</span>

                <input
                  type="search"
                  placeholder="Search incidents..."
                  aria-label="Search incidents"
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                />
              </div>

              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                aria-label="Filter by status"
              >
                <option value="All">All Statuses</option>

                {statuses.map((status) => (
                  <option key={status} value={status}>
                    {formatStatus(status)}
                  </option>
                ))}
              </select>

              <select
                value={categoryFilter}
                onChange={(event) => setCategoryFilter(event.target.value)}
                aria-label="Filter by category"
              >
                <option value="All">All Categories</option>

                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>

              <button
                type="button"
                className="clear-filters-btn"
                onClick={clearFilters}
              >
                Clear Filters
              </button>
            </div>

            {/* Loading State */}
            {loading ? (
              <div className="my-incidents-state" role="status">
                <div className="loading-spinner" />
                <h3>Loading your incidents</h3>
                <p>Please wait while we retrieve your reports.</p>
              </div>
            ) : error ? (
              /* Error State */
              <div className="my-incidents-state">
                <div className="my-incidents-error">
                  <p>{error}</p>

                  <button
                    type="button"
                    onClick={loadIncidents}
                    disabled={loading}
                  >
                    Try Again
                  </button>
                </div>
              </div>
            ) : filteredIncidents.length === 0 ? (
              /* Empty State */
              <div className="my-incidents-state">
                <div className="my-incidents-empty-icon">▤</div>

                <h3>
                  {incidents.length === 0
                    ? "No reports yet"
                    : "No matching incidents"}
                </h3>

                <p>
                  {incidents.length === 0
                    ? "Your submitted incidents will appear here."
                    : "Try changing your search term or filters."}
                </p>

                {incidents.length === 0 && (
                  <button
                    type="button"
                    className="student-primary-btn"
                    onClick={() => navigate("/report-incident")}
                  >
                    Report Your First Incident
                  </button>
                )}

                {incidents.length > 0 && (
                  <button
                    type="button"
                    className="clear-filters-btn"
                    onClick={clearFilters}
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            ) : (
              /* Incident Table */
              <div className="my-incidents-table-wrap">
                <table className="my-incidents-table">
                  <thead>
                    <tr>
                      <th>Incident ID</th>
                      <th>Category</th>
                      <th>Location</th>
                      <th>Date Reported</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredIncidents.map((incident, index) => {
                      const id = getIncidentId(incident);

                      return (
                        <tr key={id ?? `incident-${index}`}>
                          <td className="my-incident-id">
                            {formatIncidentId(incident)}
                          </td>

                          <td>{incident.category || "—"}</td>

                          <td>{incident.location || "—"}</td>

                          <td>
                            {formatDate(
                              incident.created_at ||
                                incident.createdAt ||
                                incident.reported_at ||
                                incident.date
                            )}
                          </td>

                          <td>
                            <span
                              className={`my-incident-status ${getStatusClass(
                                incident.status
                              )}`}
                            >
                              {formatStatus(incident.status)}
                            </span>
                          </td>

                          <td>
                            <button
                              type="button"
                              className="student-text-btn"
                              disabled={id == null}
                              onClick={() => openIncidentDetails(incident)}
                            >
                              View Details →
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <footer className="student-footer">
            SMART CAMPUS · Making campus life better together
          </footer>
        </div>
      </main>
    </div>
  );
}

export default MyIncidents;
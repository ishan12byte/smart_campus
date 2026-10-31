
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "./MyIncidents.css";

function MyIncidents() {
    const navigate = useNavigate();

    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("ALL");
    const [categoryFilter, setCategoryFilter] = useState("ALL");

    useEffect(() => {
        async function loadIncidents() {
            try {
                setLoading(true);
                setError("");

                const data = await getIncidents();

                // Accept the common response shapes used by list APIs.
                const records = Array.isArray(data)
                    ? data
                    : Array.isArray(data?.incidents)
                        ? data.incidents
                        : Array.isArray(data?.items)
                            ? data.items
                            : [];

                setIncidents(records);
            } catch (err) {
                setError(err.message || "Unable to load your incidents.");
            } finally {
                setLoading(false);
            }
        }

        loadIncidents();
    }, []);

    const categories = useMemo(() => {
        return [...new Set(
            incidents
                .map((incident) => incident.category)
                .filter(Boolean)
        )].sort();
    }, [incidents]);

    const filteredIncidents = useMemo(() => {
        const query = searchTerm.trim().toLowerCase();

        return incidents.filter((incident) => {
            const incidentId = `INC-${String(incident.id).padStart(3, "0")}`;

            const matchesSearch = !query || [
                incidentId,
                incident.id,
                incident.category,
                incident.location,
                incident.description
            ]
                .filter(Boolean)
                .some((value) =>
                    String(value).toLowerCase().includes(query)
                );

            const matchesStatus =
                statusFilter === "ALL" ||
                incident.status === statusFilter;

            const matchesCategory =
                categoryFilter === "ALL" ||
                incident.category === categoryFilter;

            return matchesSearch && matchesStatus && matchesCategory;
        });
    }, [incidents, searchTerm, statusFilter, categoryFilter]);

    function formatStatus(status) {
        return status
            ? status.replaceAll("_", " ")
            : "Unknown";
    }

    function getStatusClass(status) {
        switch (status) {
            case "REPORTED":
            case "ACKNOWLEDGED":
                return "status-open";

            case "UNDER_REVIEW":
            case "ASSIGNED":
                return "status-review";

            case "IN_PROGRESS":
            case "VERIFICATION_PENDING":
                return "status-progress";

            case "CLOSED":
                return "status-closed";

            case "REOPENED":
                return "status-reopened";

            default:
                return "status-default";
        }
    }

    function formatDate(date) {
        if (!date) return "—";

        const parsedDate = new Date(date);

        return Number.isNaN(parsedDate.getTime())
            ? "—"
            : parsedDate.toLocaleDateString("en-IN", {
                day: "numeric",
                month: "short",
                year: "numeric"
            });
    }

    function handleLogout() {
        localStorage.removeItem("token");
        navigate("/login");
    }

    function openIncidentDetails(incident) {
        navigate(`/incident-details/${incident.id}`);
    }

    function clearFilters() {
        setSearchTerm("");
        setStatusFilter("ALL");
        setCategoryFilter("ALL");
    }

    return (
        <div className="student-dashboard">

            {/* Sidebar */}
            <aside className="student-sidebar">
                <div className="student-brand">
                    <div className="student-brand-mark">SC</div>
                    <span>SMART CAMPUS</span>
                </div>

                <div className="sidebar-label">MAIN MENU</div>

                <nav className="student-nav">
                    <button
                        className="student-nav-link"
                        onClick={() => navigate("/student")}
                    >
                        <span className="nav-icon">⌂</span>
                        Dashboard
                    </button>

                    <button className="student-nav-link active">
                        <span className="nav-icon">▤</span>
                        My Incidents
                    </button>

                    <button
                        className="student-nav-link"
                        onClick={() => navigate("/report-incident")}
                    >
                        <span className="nav-icon">＋</span>
                        Report Incident
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
                        className="student-logout"
                        onClick={handleLogout}
                    >
                        <span>↪</span>
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main content */}
            <main className="student-main">

                <header className="student-topbar">
                    <div>
                        <p className="topbar-label">STUDENT PORTAL</p>
                        <p className="topbar-brand">SMART CAMPUS</p>
                    </div>

                    <div className="student-avatar">S</div>
                </header>

                <div className="student-content">

                    {/* Page heading */}
                    <section className="my-incidents-welcome">
                        <div>
                            <p className="welcome-date">
                                YOUR CAMPUS, YOUR VOICE
                            </p>

                            <h1>My Incidents</h1>

                            <p>
                                View and track the incidents you have reported.
                                Stay updated as your concerns move through the
                                resolution process.
                            </p>
                        </div>

                        <button
                            className="student-primary-btn"
                            onClick={() => navigate("/report-incident")}
                        >
                            <span>＋</span>
                            Report New Incident
                        </button>
                    </section>

                    {/* Incident count */}
                    <section className="my-incidents-count">
                        <div>
                            <span className="count-icon">▤</span>
                            <div>
                                <p>Total incidents</p>
                                <h2>{incidents.length}</h2>
                            </div>
                        </div>

                        <span className="count-description">
                            Your submitted campus reports
                        </span>
                    </section>

                    {/* Filters */}
                    <section className="my-incidents-panel">

                        <div className="my-incidents-panel-heading">
                            <div>
                                <h2>All Reported Incidents</h2>
                                <p>
                                    Search and filter your incident records.
                                </p>
                            </div>

                            <span className="records-count">
                                {filteredIncidents.length} records
                            </span>
                        </div>

                        <div className="incident-filters">

                            <div className="incident-search">
                                <span>⌕</span>
                                <input
                                    type="search"
                                    placeholder="Search by ID, category or location..."
                                    value={searchTerm}
                                    onChange={(event) =>
                                        setSearchTerm(event.target.value)
                                    }
                                />
                            </div>

                            <select
                                value={statusFilter}
                                onChange={(event) =>
                                    setStatusFilter(event.target.value)
                                }
                                aria-label="Filter by status"
                            >
                                <option value="ALL">All Statuses</option>
                                <option value="REPORTED">Reported</option>
                                <option value="ACKNOWLEDGED">Acknowledged</option>
                                <option value="UNDER_REVIEW">Under Review</option>
                                <option value="ASSIGNED">Assigned</option>
                                <option value="IN_PROGRESS">In Progress</option>
                                <option value="VERIFICATION_PENDING">
                                    Verification Pending
                                </option>
                                <option value="CLOSED">Closed</option>
                                <option value="REOPENED">Reopened</option>
                            </select>

                            <select
                                value={categoryFilter}
                                onChange={(event) =>
                                    setCategoryFilter(event.target.value)
                                }
                                aria-label="Filter by category"
                            >
                                <option value="ALL">All Categories</option>

                                {categories.map((category) => (
                                    <option key={category} value={category}>
                                        {category}
                                    </option>
                                ))}
                            </select>

                            {(searchTerm ||
                                statusFilter !== "ALL" ||
                                categoryFilter !== "ALL") && (
                                <button
                                    className="clear-filters-btn"
                                    onClick={clearFilters}
                                >
                                    Clear filters
                                </button>
                            )}
                        </div>

                        {/* Loading state */}
                        {loading && (
                            <div className="my-incidents-state">
                                <div className="loading-spinner"></div>
                                <p>Loading your incidents...</p>
                            </div>
                        )}

                        {/* Error state */}
                        {!loading && error && (
                            <div className="my-incidents-error">
                                <strong>Unable to load incidents</strong>
                                <p>{error}</p>
                                <button
                                    onClick={() => window.location.reload()}
                                >
                                    Try Again
                                </button>
                            </div>
                        )}

                        {/* Empty state */}
                        {!loading && !error && incidents.length === 0 && (
                            <div className="my-incidents-state">
                                <div className="my-incidents-empty-icon">▤</div>
                                <h3>No incidents reported yet</h3>
                                <p>
                                    Your submitted campus concerns will appear
                                    here once they are available.
                                </p>
                                <button
                                    className="student-primary-btn"
                                    onClick={() => navigate("/report-incident")}
                                >
                                    Report Your First Incident
                                </button>
                            </div>
                        )}

                        {/* No filter results */}
                        {!loading && !error &&
                            incidents.length > 0 &&
                            filteredIncidents.length === 0 && (
                                <div className="my-incidents-state">
                                    <div className="my-incidents-empty-icon">⌕</div>
                                    <h3>No matching incidents</h3>
                                    <p>
                                        Try changing your search or filter
                                        selections.
                                    </p>
                                    <button
                                        className="clear-filters-btn"
                                        onClick={clearFilters}
                                    >
                                        Clear filters
                                    </button>
                                </div>
                            )}

                        {/* Incidents table */}
                        {!loading && !error &&
                            filteredIncidents.length > 0 && (
                                <div className="my-incidents-table-wrap">
                                    <table className="my-incidents-table">
                                        <thead>
                                            <tr>
                                                <th>Incident ID</th>
                                                <th>Category</th>
                                                <th>Location</th>
                                                <th>Date Reported</th>
                                                <th>Priority</th>
                                                <th>Status</th>
                                                <th>Action</th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {filteredIncidents.map((incident) => (
                                                <tr key={incident.id}>
                                                    <td className="my-incident-id">
                                                        INC-{String(incident.id).padStart(3, "0")}
                                                    </td>

                                                    <td>
                                                        {incident.category || "—"}
                                                    </td>

                                                    <td>
                                                        {incident.location || "—"}
                                                    </td>

                                                    <td>
                                                        {formatDate(incident.created_at)}
                                                    </td>

                                                    <td>
                                                        {incident.priority || "—"}
                                                    </td>

                                                    <td>
                                                        <span className={`my-incident-status ${getStatusClass(incident.status)}`}>
                                                            {formatStatus(incident.status)}
                                                        </span>
                                                    </td>

                                                    <td>
                                                        <button
                                                            className="view-incident-btn"
                                                            onClick={() => openIncidentDetails(incident)}
                                                        >
                                                            View Details →
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
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

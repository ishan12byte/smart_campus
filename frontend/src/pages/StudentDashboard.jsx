
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "./StudentDashboard.css";

// Keep false until Member 4 confirms that GET /incidents
// returns only incidents belonging to the authenticated student.
const STUDENT_SCOPE_CONFIRMED = false;

// --------------------------------------------------
// HELPER FUNCTIONS
// --------------------------------------------------

function getIncidentList(response) {
    if (Array.isArray(response)) return response;
    if (Array.isArray(response?.incidents)) return response.incidents;
    if (Array.isArray(response?.data)) return response.data;
    if (Array.isArray(response?.items)) return response.items;
    if (Array.isArray(response?.results)) return response.results;

    if (Array.isArray(response?.data?.incidents)) {
        return response.data.incidents;
    }

    return [];
}

function getIncidentId(incident) {
    return incident?.incident_id ?? incident?.id ?? incident?._id ?? null;
}

function getStatus(incident) {
    return String(incident?.status || "Unknown")
        .replaceAll("_", " ")
        .replaceAll("-", " ")
        .toUpperCase();
}

function getDateValue(incident) {
    return (
        incident?.created_at ||
        incident?.createdAt ||
        incident?.date ||
        incident?.incident_date ||
        null
    );
}

function formatDate(value) {
    if (!value) return "—";

    const parsedDate = new Date(value);

    return Number.isNaN(parsedDate.getTime())
        ? "—"
        : parsedDate.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
}

function formatIncidentId(incident) {
    const id = getIncidentId(incident);

    if (id === null || id === undefined || id === "") {
        return "ID unavailable";
    }

    const idString = String(id);

    // Avoid adding INC- to IDs that already have a prefix.
    if (/^INC-/i.test(idString)) {
        return idString.toUpperCase();
    }

    return `INC-${idString.padStart(3, "0")}`;
}

function isOpen(incident) {
    const status = getStatus(incident);

    return ["REPORTED", "ACKNOWLEDGED"].includes(status);
}

function isUnderReview(incident) {
    const status = getStatus(incident);

    return [
        "UNDER REVIEW",
        "ASSIGNED",
        "IN PROGRESS",
        "VERIFICATION PENDING"
    ].includes(status);
}

function isResolved(incident) {
    const status = getStatus(incident);

    return [
        "CLOSED",
        "RESOLVED",
        "COMPLETED"
    ].includes(status);
}

// --------------------------------------------------
// MAIN STUDENT DASHBOARD
// --------------------------------------------------

function StudentDashboard() {
    const navigate = useNavigate();

    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [searchTerm, setSearchTerm] = useState("");

    const currentHour = new Date().getHours();

    const greeting =
        currentHour >= 5 && currentHour < 12
            ? "Good morning"
            : currentHour >= 12 && currentHour < 17
                ? "Good afternoon"
                : "Good evening";

    // --------------------------------------------------
    // FETCH INCIDENTS
    // --------------------------------------------------

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
                        err?.message || "Unable to load your incidents."
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

    // --------------------------------------------------
    // SUMMARY COUNTS
    // --------------------------------------------------

    const counts = useMemo(() => ({
        total: incidents.length,
        open: incidents.filter(isOpen).length,
        underReview: incidents.filter(isUnderReview).length,
        resolved: incidents.filter(isResolved).length
    }), [incidents]);

    // --------------------------------------------------
    // COMPLAINT SEARCH
    // --------------------------------------------------

    const filteredIncidents = useMemo(() => {
        const query = searchTerm.trim().toLowerCase();

        if (!query) return incidents;

        return incidents.filter((incident) => {
            const searchableValues = [
                incident?.category,
                incident?.location,
                incident?.description,
                incident?.status,
                formatIncidentId(incident)
            ];

            return searchableValues
                .filter(Boolean)
                .some((value) =>
                    String(value).toLowerCase().includes(query)
                );
        });
    }, [incidents, searchTerm]);

    // --------------------------------------------------
    // LOGOUT
    // --------------------------------------------------

    function handleLogout() {
        // Confirm this storage key against auth.js.
        localStorage.removeItem("token");
        navigate("/login", { replace: true });
    }

    // --------------------------------------------------
    // RENDER
    // --------------------------------------------------

    const dataAvailable =
        !loading &&
        !error &&
        STUDENT_SCOPE_CONFIRMED;

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
                        className="student-nav-link active"
                        onClick={() => navigate("/student")}
                        type="button"
                    >
                        <span className="nav-icon">⌂</span>
                        Dashboard
                    </button>

                    <button
                        className="student-nav-link"
                        onClick={() => navigate("/my-incidents")}
                        type="button"
                    >
                        <span className="nav-icon">▤</span>
                        My Incidents
                    </button>

                    <button
                        className="student-nav-link"
                        onClick={() => navigate("/report-incident")}
                        type="button"
                    >
                        <span className="nav-icon">＋</span>
                        Report Incident
                    </button>

                    <button
                        className="student-nav-link"
                        onClick={() =>
                            document
                                .getElementById("complaint-checker")
                                ?.scrollIntoView({ behavior: "smooth" })
                        }
                        type="button"
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
                        className="student-logout"
                        onClick={handleLogout}
                        type="button"
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

                    {/* Welcome section */}
                    <section className="student-welcome">
                        <div>
                            <p className="welcome-date">
                                YOUR CAMPUS, YOUR VOICE
                            </p>

                            <h1>{greeting}!</h1>

                            <p>
                                Welcome to your dashboard. Keep track of your
                                reports and stay updated on campus concerns.
                            </p>
                        </div>

                        <button
                            className="student-primary-btn"
                            onClick={() => navigate("/report-incident")}
                            type="button"
                        >
                            <span>＋</span>
                            Report New Incident
                        </button>
                    </section>

                    {/* Summary cards */}
                    <section className="student-summary-grid">
                        <div className="student-summary-card">
                            <div className="summary-icon blue-icon">▤</div>
                            <p>Total Reports</p>
                            <h2>
                                {loading || error || !STUDENT_SCOPE_CONFIRMED
                                    ? "—"
                                    : counts.total}
                            </h2>
                            <span>Incidents you've reported</span>
                        </div>

                        <div className="student-summary-card">
                            <div className="summary-icon orange-icon">◷</div>
                            <p>Open Reports</p>
                            <h2>
                                {loading || error || !STUDENT_SCOPE_CONFIRMED
                                    ? "—"
                                    : counts.open}
                            </h2>
                            <span>Awaiting further action</span>
                        </div>

                        <div className="student-summary-card">
                            <div className="summary-icon purple-icon">⌛</div>
                            <p>Under Review</p>
                            <h2>
                                {loading || error || !STUDENT_SCOPE_CONFIRMED
                                    ? "—"
                                    : counts.underReview}
                            </h2>
                            <span>Currently being addressed</span>
                        </div>

                        <div className="student-summary-card">
                            <div className="summary-icon green-icon">✓</div>
                            <p>Resolved</p>
                            <h2>
                                {loading || error || !STUDENT_SCOPE_CONFIRMED
                                    ? "—"
                                    : counts.resolved}
                            </h2>
                            <span>Successfully closed reports</span>
                        </div>
                    </section>

                    {/* Quick actions */}
                    <section className="student-section">
                        <div className="student-section-heading">
                            <div>
                                <h2>Quick Actions</h2>
                                <p>What would you like to do today?</p>
                            </div>
                        </div>

                        <div className="student-actions-grid">
                            <button
                                className="student-action-card report-action"
                                onClick={() => navigate("/report-incident")}
                                type="button"
                            >
                                <span className="action-icon">＋</span>

                                <span className="action-text">
                                    <strong>Report an Incident</strong>
                                    <small>Submit a new campus concern</small>
                                </span>

                                <span className="action-arrow">→</span>
                            </button>

                            <button
                                className="student-action-card check-action"
                                onClick={() =>
                                    document
                                        .getElementById("complaint-checker")
                                        ?.scrollIntoView({ behavior: "smooth" })
                                }
                                type="button"
                            >
                                <span className="action-icon">⌕</span>

                                <span className="action-text">
                                    <strong>Check Existing Complaints</strong>
                                    <small>Look for reports about a similar issue</small>
                                </span>

                                <span className="action-arrow">→</span>
                            </button>
                        </div>
                    </section>

                    {/* Recent incidents */}
                    <section
                        className="student-section student-panel"
                        id="my-incidents"
                    >
                        <div className="student-section-heading">
                            <div>
                                <h2>My Recent Complaints</h2>
                                <p>
                                    Keep track of the incidents you've submitted.
                                </p>
                            </div>

                            <button
                                className="student-text-btn"
                                onClick={() => navigate("/my-incidents")}
                                type="button"
                            >
                                View all
                            </button>
                        </div>

                        {loading ? (
                            <div className="student-empty-state">
                                Loading your reports...
                            </div>
                        ) : error ? (
                            <div className="student-error">
                                {error}
                            </div>
                        ) : !STUDENT_SCOPE_CONFIRMED ? (
                            <div className="student-empty-state">
                                <div className="empty-icon">🔒</div>
                                <h3>Student data access awaiting confirmation</h3>
                                <p>
                                    Your reports will appear here once the
                                    backend confirms that the incidents service
                                    returns only your own records.
                                </p>
                            </div>
                        ) : incidents.length === 0 ? (
                            <div className="student-empty-state">
                                <div className="empty-icon">▤</div>
                                <h3>No reports yet</h3>
                                <p>
                                    You haven't submitted any incidents.
                                    Your reports will appear here.
                                </p>

                                <button
                                    className="student-primary-btn"
                                    onClick={() => navigate("/report-incident")}
                                    type="button"
                                >
                                    Report Your First Incident
                                </button>
                            </div>
                        ) : (
                            <div className="student-table-wrap">
                                <table className="student-table">
                                    <thead>
                                        <tr>
                                            <th>Incident ID</th>
                                            <th>Category</th>
                                            <th>Location</th>
                                            <th>Date</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {incidents.slice(0, 5).map((incident, index) => (
                                            <tr key={getIncidentId(incident) ?? `incident-${index}`}>
                                                <td className="incident-id">
                                                    {formatIncidentId(incident)}
                                                </td>

                                                <td>{incident?.category || "—"}</td>
                                                <td>{incident?.location || "—"}</td>
                                                <td>{formatDate(getDateValue(incident))}</td>

                                                <td>
                                                    <span className="student-status">
                                                        {getStatus(incident)}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </section>

                    {/* Complaint checker */}
                    <section
                        className="student-section student-panel complaint-checker"
                        id="complaint-checker"
                    >
                        <div className="student-section-heading">
                            <div>
                                <h2>Check Existing Complaints</h2>
                                <p>
                                    Search for a similar issue before submitting
                                    a new report.
                                </p>
                            </div>

                            <span className="privacy-label">
                                🔒 Reporter details hidden
                            </span>
                        </div>

                        <div className="complaint-search">
                            <span className="search-icon">⌕</span>

                            <input
                                type="search"
                                placeholder="Search by category, location or keyword..."
                                value={searchTerm}
                                onChange={(event) =>
                                    setSearchTerm(event.target.value)
                                }
                            />

                            {searchTerm && (
                                <button
                                    onClick={() => setSearchTerm("")}
                                    aria-label="Clear search"
                                    type="button"
                                >
                                    Clear
                                </button>
                            )}
                        </div>

                        <p className="search-note">
                            Search results currently use the incidents returned
                            by your existing API. Campus-wide matching will be
                            enabled once the privacy-safe search endpoint is available.
                        </p>

                        {searchTerm.trim() && (
                            <div className="search-results">
                                <h3>
                                    {dataAvailable
                                        ? `${filteredIncidents.length} matching ${
                                            filteredIncidents.length === 1
                                                ? "report"
                                                : "reports"
                                        }`
                                        : "Search results unavailable"}
                                </h3>

                                {!dataAvailable ? (
                                    <p className="no-matches">
                                        Search will be available once your
                                        student-specific incident access is confirmed.
                                    </p>
                                ) : filteredIncidents.length === 0 ? (
                                    <p className="no-matches">
                                        No matching reports found in the available
                                        results. You can still submit your incident.
                                    </p>
                                ) : (
                                    filteredIncidents.map((incident, index) => (
                                        <div
                                            className="matching-incident"
                                            key={
                                                getIncidentId(incident) ??
                                                `matching-${index}`
                                            }
                                        >
                                            <div>
                                                <strong>
                                                    {formatIncidentId(incident)}
                                                    {" · "}
                                                    {incident?.category || "Uncategorised"}
                                                </strong>

                                                <p>
                                                    {incident?.location || "Location not specified"}
                                                    {" · "}
                                                    {formatDate(getDateValue(incident))}
                                                </p>
                                            </div>

                                            <span className="student-status">
                                                {getStatus(incident)}
                                            </span>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}

                        <div className="checker-footer">
                            <span>Can't find a similar complaint?</span>

                            <button
                                className="student-text-btn"
                                onClick={() => navigate("/report-incident")}
                                type="button"
                            >
                                Report a new incident →
                            </button>
                        </div>
                    </section>

                    <footer className="student-footer">
                        SMART CAMPUS · Making campus life better together
                    </footer>
                </div>
            </main>
        </div>
    );
}

export default StudentDashboard;

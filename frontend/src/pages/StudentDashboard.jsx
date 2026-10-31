import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "./StudentDashboard.css";

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

    useEffect(() => {
        async function loadIncidents() {
            try {
                setLoading(true);
                setError("");

                const data = await getIncidents();
                setIncidents(Array.isArray(data) ? data : []);
            } catch (err) {
                setError(err.message || "Unable to load your incidents.");
            } finally {
                setLoading(false);
            }
        }

        loadIncidents();
    }, []);

    const openReports = incidents.filter((incident) =>
        ["REPORTED", "ACKNOWLEDGED"].includes(incident.status)
    ).length;

    const underReview = incidents.filter((incident) =>
        [
            "UNDER_REVIEW",
            "ASSIGNED",
            "IN_PROGRESS",
            "VERIFICATION_PENDING"
        ].includes(incident.status)
    ).length;

    const resolvedReports = incidents.filter(
        (incident) => incident.status === "CLOSED"
    ).length;

    const filteredIncidents = useMemo(() => {
        const query = searchTerm.trim().toLowerCase();

        if (!query) return incidents;

        return incidents.filter((incident) =>
            [
                incident.category,
                incident.location,
                incident.description,
                incident.status,
                `INC-${String(incident.id).padStart(3, "0")}`
            ]
                .filter(Boolean)
                .some((value) => String(value).toLowerCase().includes(query))
        );
    }, [incidents, searchTerm]);

    function formatStatus(status) {
        return status
            ? status.replaceAll("_", " ")
            : "Unknown";
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
                    >
                        <span className="nav-icon">⌂</span>
                        Dashboard
                    </button>

                    <button
                        className="student-nav-link"
                        onClick={() => navigate("/my-incidents")}
                    >
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

                    <button
                        className="student-nav-link"
                        onClick={() =>
                            document.getElementById("complaint-checker")?.scrollIntoView({
                                behavior: "smooth"
                            })
                        }
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
                    >
                        <span>↪</span>
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main dashboard */}
            <main className="student-main">

                <header className="student-topbar">
                    <div>
                        <p className="topbar-label">STUDENT PORTAL</p>
                        <p className="topbar-brand">SMART CAMPUS</p>
                    </div>

                    <div className="student-avatar">S</div>
                </header>

                <div className="student-content">

                    {/* Greeting */}
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
                            <h2>{incidents.length}</h2>
                            <span>Incidents you've reported</span>
                        </div>

                        <div className="student-summary-card">
                            <div className="summary-icon orange-icon">◷</div>
                            <p>Open Reports</p>
                            <h2>{openReports}</h2>
                            <span>Awaiting further action</span>
                        </div>

                        <div className="student-summary-card">
                            <div className="summary-icon purple-icon">⌛</div>
                            <p>Under Review</p>
                            <h2>{underReview}</h2>
                            <span>Currently being addressed</span>
                        </div>

                        <div className="student-summary-card">
                            <div className="summary-icon green-icon">✓</div>
                            <p>Resolved</p>
                            <h2>{resolvedReports}</h2>
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
                                    document.getElementById("complaint-checker")?.scrollIntoView({
                                        behavior: "smooth"
                                    })
                                }
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
                                <p>Keep track of the incidents you've submitted.</p>
                            </div>

                            <button
                                className="student-text-btn"
                                oonClick={() => navigate("/my-incidents")}
                            >
                                View all
                            </button>
                        </div>

                        {loading ? (
                            <div className="student-empty-state">
                                Loading your reports...
                            </div>
                        ) : error ? (
                            <div className="student-error">{error}</div>
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
                                        {incidents.slice(0, 5).map((incident) => (
                                            <tr key={incident.id}>
                                                <td className="incident-id">
                                                    INC-{String(incident.id).padStart(3, "0")}
                                                </td>
                                                <td>{incident.category || "—"}</td>
                                                <td>{incident.location || "—"}</td>
                                                <td>{formatDate(incident.created_at)}</td>
                                                <td>
                                                    <span className="student-status">
                                                        {formatStatus(incident.status)}
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
                            <span className="privacy-label">🔒 Reporter details hidden</span>
                        </div>

                        <div className="complaint-search">
                            <span className="search-icon">⌕</span>
                            <input
                                type="search"
                                placeholder="Search by category, location or keyword..."
                                value={searchTerm}
                                onChange={(event) => setSearchTerm(event.target.value)}
                            />
                            {searchTerm && (
                                <button
                                    onClick={() => setSearchTerm("")}
                                    aria-label="Clear search"
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
                                    {filteredIncidents.length} matching
                                    {filteredIncidents.length === 1 ? " report" : " reports"}
                                </h3>

                                {filteredIncidents.length === 0 ? (
                                    <p className="no-matches">
                                        No matching reports found in the available results.
                                        You can still submit your incident.
                                    </p>
                                ) : (
                                    filteredIncidents.map((incident) => (
                                        <div
                                            className="matching-incident"
                                            key={incident.id}
                                        >
                                            <div>
                                                <strong>
                                                    INC-{String(incident.id).padStart(3, "0")}
                                                    {" · "}
                                                    {incident.category || "Uncategorised"}
                                                </strong>
                                                <p>
                                                    {incident.location || "Location not specified"}
                                                    {" · "}
                                                    {formatDate(incident.created_at)}
                                                </p>
                                            </div>

                                            <span className="student-status">
                                                {formatStatus(incident.status)}
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

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getIncidents } from "../services/incidents";

import "./StudentDashboard.css";
import "./IncidentDetails.css";

function IncidentDetails() {
    const navigate = useNavigate();
    const { incidentId } = useParams();

    const [incident, setIncident] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [retryCount, setRetryCount] = useState(0);

    useEffect(() => {
        let isActive = true;

        async function loadIncident() {
            try {
                setLoading(true);
                setError("");
                setIncident(null);

                const data = await getIncidents();

                const records = Array.isArray(data)
                    ? data
                    : data?.incidents ||
                      data?.data ||
                      data?.items ||
                      data?.results ||
                      [];

                const selectedIncident = records.find((item) => {
                    const id = item.id ?? item.incident_id ?? item._id;
                    return String(id) === String(incidentId);
                });

                if (isActive) {
                    setIncident(selectedIncident || null);
                }
            } catch (err) {
                if (isActive) {
                    setError(
                        err.message || "Unable to load incident details."
                    );
                }
            } finally {
                if (isActive) {
                    setLoading(false);
                }
            }
        }

        loadIncident();

        return () => {
            isActive = false;
        };
    }, [incidentId, retryCount]);

    function handleLogout() {
        localStorage.removeItem("token");
        navigate("/login");
    }

    function getValue(...values) {
        return values.find(
            (value) =>
                value !== undefined &&
                value !== null &&
                String(value).trim() !== ""
        );
    }

    function formatIncidentId(item) {
        const id = item?.id ?? item?.incident_id ?? item?._id;

        if (id == null) return "—";

        const value = String(id);

        return value.startsWith("INC-")
            ? value
            : `INC-${value.padStart(3, "0")}`;
    }

    function formatStatus(status) {
        if (!status) return "Unknown";

        return String(status)
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) => letter.toUpperCase());
    }

    function getStatusClass(status) {
        const value = String(status || "").toLowerCase();

        if (["closed", "resolved"].includes(value)) {
            return "detail-status-resolved";
        }

        if (["rejected", "cancelled"].includes(value)) {
            return "detail-status-rejected";
        }

        if (
            ["in_progress", "under_review", "assigned"].includes(value)
        ) {
            return "detail-status-progress";
        }

        return "detail-status-pending";
    }

    function formatDate(value) {
        if (!value) return "—";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) return "—";

        return date.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "long",
            year: "numeric"
        });
    }

    function formatDateTime(value) {
        if (!value) return "—";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) return "—";

        return date.toLocaleString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit"
        });
    }

    function formatTime(value) {
        if (!value) return "—";

        // Handle a time-only value such as "14:30".
        if (/^\d{1,2}:\d{2}(:\d{2})?$/.test(String(value))) {
            const [hours, minutes] = String(value).split(":");
            const date = new Date();
            date.setHours(Number(hours), Number(minutes), 0, 0);

            return date.toLocaleTimeString("en-IN", {
                hour: "numeric",
                minute: "2-digit"
            });
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) return "—";

        return date.toLocaleTimeString("en-IN", {
            hour: "numeric",
            minute: "2-digit"
        });
    }

    function getEvidenceItems(item) {
        const rawEvidence = getValue(
            item?.attachments,
            item?.evidence,
            item?.files,
            item?.evidence_url,
            item?.attachment_url
        );

        if (!rawEvidence) return [];

        const entries = Array.isArray(rawEvidence)
            ? rawEvidence
            : [rawEvidence];

        return entries
            .map((entry, index) => {
                if (typeof entry === "string") {
                    return {
                        id: index,
                        name: entry.split("/").pop() || "Attached file",
                        url: entry
                    };
                }

                if (entry && typeof entry === "object") {
                    return {
                        id: entry.id ?? index,
                        name:
                            entry.name ||
                            entry.filename ||
                            entry.file_name ||
                            "Attached file",
                        url:
                            entry.url ||
                            entry.file_url ||
                            entry.download_url ||
                            entry.path ||
                            ""
                    };
                }

                return null;
            })
            .filter(Boolean);
    }

    function isSafeLink(url) {
        return /^https?:\/\//i.test(String(url || ""));
    }

    const status = incident?.status;

    const history = incident
        ? getValue(
              incident.status_history,
              incident.history,
              incident.updates
          )
        : [];

    const historyItems = Array.isArray(history) ? history : [];

    const title = getValue(
        incident?.title,
        incident?.subject,
        incident?.category,
        "Incident Report"
    );

    const description = getValue(
        incident?.description,
        incident?.details,
        incident?.incident_description
    );

    const reportedDate = getValue(
        incident?.created_at,
        incident?.createdAt,
        incident?.reported_at,
        incident?.date
    );

    const reportedTime = getValue(
        incident?.time,
        incident?.incident_time,
        incident?.reported_time,
        incident?.created_at,
        incident?.createdAt,
        incident?.reported_at
    );

    const updatedDate = getValue(
        incident?.updated_at,
        incident?.updatedAt,
        incident?.last_updated
    );

    const department = getValue(
        incident?.assigned_department,
        incident?.department_name,
        incident?.department
    );

    const assignedTo = getValue(
        incident?.assigned_to,
        incident?.assigned_staff,
        incident?.staff_name
    );

    const priority = getValue(incident?.priority);
    const evidenceItems = incident ? getEvidenceItems(incident) : [];

    return (
        <div className="student-dashboard">
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

                    <button
                        className="student-nav-link active"
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

                    <button className="student-logout" onClick={handleLogout}>
                        <span>↪</span>
                        Logout
                    </button>
                </div>
            </aside>

            <main className="student-main">
                <header className="student-topbar">
                    <div>
                        <p className="topbar-label">STUDENT PORTAL</p>
                        <p className="topbar-brand">SMART CAMPUS</p>
                    </div>

                    <div className="student-avatar">S</div>
                </header>

                <div className="student-content incident-details-page">
                    <button
                        className="incident-back-btn"
                        onClick={() => navigate("/my-incidents")}
                    >
                        ← Back to My Incidents
                    </button>

                    {loading ? (
                        <section className="incident-state-card">
                            <div className="incident-state-icon">◷</div>
                            <h2>Loading incident details</h2>
                            <p>
                                Please wait while we retrieve your report.
                            </p>
                        </section>
                    ) : error ? (
                        <section className="incident-state-card incident-state-error">
                            <div className="incident-state-icon">!</div>
                            <h2>Unable to load this incident</h2>
                            <p>{error}</p>

                            <button
                                className="student-primary-btn"
                                onClick={() => setRetryCount((count) => count + 1)}
                            >
                                Try Again
                            </button>
                        </section>
                    ) : !incident ? (
                        <section className="incident-state-card">
                            <div className="incident-state-icon">?</div>
                            <h2>Incident not found</h2>
                            <p>
                                This incident could not be found in your
                                submitted reports.
                            </p>

                            <button
                                className="student-primary-btn"
                                onClick={() => navigate("/my-incidents")}
                            >
                                View My Incidents
                            </button>
                        </section>
                    ) : (
                        <>
                            <section className="incident-detail-header">
                                <div>
                                    <p className="welcome-date">
                                        INCIDENT OVERVIEW
                                    </p>
                                    <h1>{title}</h1>
                                    <p className="incident-detail-id">
                                        {formatIncidentId(incident)}
                                    </p>
                                </div>

                                <span
                                    className={`incident-detail-status ${getStatusClass(status)}`}
                                >
                                    {formatStatus(status)}
                                </span>
                            </section>

                            <section className="incident-detail-grid">
                                <div className="incident-detail-main">
                                    <article className="incident-detail-card">
                                        <div className="incident-card-heading">
                                            <div className="incident-heading-icon">
                                                ▤
                                            </div>
                                            <div>
                                                <h2>Report Information</h2>
                                                <p>
                                                    Details of the incident
                                                    you submitted.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="incident-info-grid">
                                            <div className="incident-info-item">
                                                <span>Category</span>
                                                <strong>
                                                    {incident.category || "—"}
                                                </strong>
                                            </div>

                                            <div className="incident-info-item">
                                                <span>Subcategory</span>
                                                <strong>
                                                    {incident.subcategory || "—"}
                                                </strong>
                                            </div>

                                            <div className="incident-info-item">
                                                <span>Location</span>
                                                <strong>
                                                    {incident.location || "—"}
                                                </strong>
                                            </div>

                                            <div className="incident-info-item">
                                                <span>Priority</span>
                                                <strong>
                                                    {priority
                                                        ? formatStatus(priority)
                                                        : "—"}
                                                </strong>
                                            </div>

                                            <div className="incident-info-item">
                                                <span>Date Reported</span>
                                                <strong>
                                                    {formatDate(reportedDate)}
                                                </strong>
                                            </div>

                                            <div className="incident-info-item">
                                                <span>Time Reported</span>
                                                <strong>
                                                    {formatTime(reportedTime)}
                                                </strong>
                                            </div>

                                            <div className="incident-info-item">
                                                <span>Last Updated</span>
                                                <strong>
                                                    {formatDateTime(updatedDate)}
                                                </strong>
                                            </div>
                                        </div>

                                        <div className="incident-description">
                                            <span>Description</span>
                                            <p>
                                                {description ||
                                                    "No description is available for this report."}
                                            </p>
                                        </div>
                                    </article>

                                    <article className="incident-detail-card">
                                        <div className="incident-card-heading">
                                            <div className="incident-heading-icon">
                                                ◷
                                            </div>
                                            <div>
                                                <h2>Status Updates</h2>
                                                <p>
                                                    Available updates for this
                                                    incident.
                                                </p>
                                            </div>
                                        </div>

                                        {historyItems.length > 0 ? (
                                            <div className="incident-history">
                                                {historyItems.map((item, index) => {
                                                    const updateStatus =
                                                        typeof item === "string"
                                                            ? item
                                                            : getValue(
                                                                  item?.status,
                                                                  item?.title,
                                                                  item?.action,
                                                                  "Update"
                                                              );

                                                    const updateDate =
                                                        typeof item === "object"
                                                            ? getValue(
                                                                  item?.created_at,
                                                                  item?.updated_at,
                                                                  item?.date,
                                                                  item?.timestamp
                                                              )
                                                            : null;

                                                    const updateNote =
                                                        typeof item === "object"
                                                            ? getValue(
                                                                  item?.description,
                                                                  item?.message,
                                                                  item?.remarks
                                                              )
                                                            : null;

                                                    return (
                                                        <div
                                                            className="incident-history-item"
                                                            key={item?.id || index}
                                                        >
                                                            <div className="incident-history-marker">
                                                                ✓
                                                            </div>

                                                            <div>
                                                                <strong>
                                                                    {formatStatus(
                                                                        updateStatus
                                                                    )}
                                                                </strong>

                                                                {updateNote && (
                                                                    <p>{updateNote}</p>
                                                                )}

                                                                {updateDate && (
                                                                    <span>
                                                                        {formatDateTime(
                                                                            updateDate
                                                                        )}
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        ) : (
                                            <div className="incident-history-empty">
                                                <span>◷</span>
                                                <div>
                                                    <strong>
                                                        No status updates available
                                                    </strong>
                                                    <p>
                                                        Updates will appear here
                                                        when they are provided.
                                                    </p>
                                                </div>
                                            </div>
                                        )}
                                    </article>

                                    <article className="incident-detail-card">
                                        <div className="incident-card-heading">
                                            <div className="incident-heading-icon">
                                                📎
                                            </div>
                                            <div>
                                                <h2>Evidence & Attachments</h2>
                                                <p>
                                                    Files submitted with this
                                                    incident report.
                                                </p>
                                            </div>
                                        </div>

                                        {evidenceItems.length > 0 ? (
                                            <div className="incident-evidence-list">
                                                {evidenceItems.map((file) => (
                                                    <div
                                                        className="incident-evidence-item"
                                                        key={file.id}
                                                    >
                                                        <span className="incident-evidence-icon">
                                                            📄
                                                        </span>
                                                        <div className="incident-evidence-info">
                                                            <strong>{file.name}</strong>
                                                            <span>
                                                                {isSafeLink(file.url)
                                                                    ? "Attachment available"
                                                                    : "File link not available"}
                                                            </span>
                                                        </div>

                                                        {isSafeLink(file.url) && (
                                                            <a
                                                                className="incident-evidence-link"
                                                                href={file.url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                            >
                                                                View file ↗
                                                            </a>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="incident-evidence-empty">
                                                <span>📎</span>
                                                <div>
                                                    <strong>
                                                        No evidence details available
                                                    </strong>
                                                    <p>
                                                        Attachment information
                                                        will appear here when it
                                                        is provided with the
                                                        incident record.
                                                    </p>
                                                </div>
                                            </div>
                                        )}
                                    </article>
                                </div>

                                <aside className="incident-detail-side">
                                    <article className="incident-detail-card">
                                        <div className="incident-card-heading">
                                            <div className="incident-heading-icon">
                                                ◉
                                            </div>
                                            <div>
                                                <h2>Assignment</h2>
                                                <p>
                                                    Responsibility information
                                                </p>
                                            </div>
                                        </div>

                                        <div className="incident-assignment-item">
                                            <span>Assigned Department</span>
                                            <strong>
                                                {department || "Not available yet"}
                                            </strong>
                                        </div>

                                        <div className="incident-assignment-item">
                                            <span>Assigned Staff</span>
                                            <strong>
                                                {assignedTo || "Not available yet"}
                                            </strong>
                                        </div>
                                    </article>

                                    <article className="incident-detail-note">
                                        <div className="incident-note-icon">i</div>
                                        <div>
                                            <h3>Need help?</h3>
                                            <p>
                                                If you have questions about
                                                this report, contact your
                                                campus administrator.
                                            </p>
                                        </div>
                                    </article>

                                    <button
                                        className="incident-secondary-btn"
                                        onClick={() => navigate("/my-incidents")}
                                    >
                                        View All My Reports
                                    </button>
                                </aside>
                            </section>
                        </>
                    )}

                    <footer className="student-footer">
                        SMART CAMPUS · Making campus life better together
                    </footer>
                </div>
            </main>
        </div>
    );
}

export default IncidentDetails;

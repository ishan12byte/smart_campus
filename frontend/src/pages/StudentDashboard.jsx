import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getIncidents } from "../services/incidents";
import "../App.css";

function StudentDashboard() {
    const navigate = useNavigate();
    const [incidents, setIncidents] = useState([]);

    useEffect(() => {
        async function loadIncidents() {
            try {
                const data = await getIncidents();
                setIncidents(data);
            } catch (error) {
                console.error("Failed to load incidents:", error);
            }
        }

        loadIncidents();
    }, []);
    return (
        <div className="app-shell">
            <main className="page-container">
                <header className="page-header">
                    <div>
                        <h1>Student Dashboard</h1>
                        <p className="page-subtitle">
                            Track and manage the incidents you have reported.
                        </p>
                    </div>

                    <button
                        className="btn btn-primary"
                        onClick={() => navigate("/report-incident")}
                    >
                        + Report New Incident
                    </button>
                </header>

                <section className="summary-grid">
                    <div className="summary-card">
                        <h3>My Reports</h3>
                        <p className="summary-value">{incidents.length}</p>
                    </div>

                    <div className="summary-card">
                        <h3>Open Reports</h3>
                        <p className="summary-value">
                            {incidents.filter((incident) =>
                                ["REPORTED", "ACKNOWLEDGED"].includes(incident.status)
                            ).length}
                        </p>
                    </div>

                    <div className="summary-card">
                        <h3>Under Review</h3>
                        <p className="summary-value">
                            {incidents.filter((incident) =>
                                [
                                    "UNDER_REVIEW",
                                    "ASSIGNED",
                                    "IN_PROGRESS",
                                    "VERIFICATION_PENDING"
                                ].includes(incident.status)
                            ).length}
                        </p>
                    </div>

                    <div className="summary-card">
                        <h3>Resolved</h3>
                        <p className="summary-value">
                            {incidents.filter(
                                (incident) => incident.status === "CLOSED"
                            ).length}
                        </p>
                    </div>
                </section>

                <section className="content-card">
                    <h2>My Recent Reports</h2>

                    {incidents.length === 0 ? (
                        <div className="empty-state">
                            <p>You haven't reported any incidents yet.</p>
                            <button
                                className="btn btn-primary"
                                onClick={() => navigate("/report-incident")}
                            >
                                Report Your First Incident
                            </button>
                        </div>
                    ) : (
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Incident ID</th>
                                        <th>Category</th>
                                        <th>Location</th>
                                        <th>Date</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {incidents.map((incident) => (
                                        <tr key={incident.id}>
                                            <td>
                                                INC-{String(incident.id).padStart(3, "0")}
                                            </td>
                                            <td>{incident.category}</td>
                                            <td>{incident.location}</td>
                                            <td>
                                                {incident.created_at
                                                    ? new Date(
                                                        incident.created_at
                                                    ).toLocaleDateString()
                                                    : "—"}
                                            </td>
                                            <td>
                                                <span className="status-badge">
                                                    {incident.status.replaceAll("_", " ")}
                                                </span>
                                            </td>
                                            <td>
                                                <button
                                                    className="btn btn-secondary"
                                                    onClick={() =>
                                                        navigate(`/incidents/${incident.id}`)
                                                    }
                                                >
                                                    View Details
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}

export default StudentDashboard;
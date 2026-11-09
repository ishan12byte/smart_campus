
import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import "./AnalyticsDashboard.css";

function AnalyticsDashboard() {
    const [period, setPeriod] = useState("30");
    const location = useLocation();

    const dashboardPath = location.state?.from || "/admin/overview";

    const stats = [
        { label: "Total Incidents", value: "—", note: "Awaiting incident data" },
        { label: "Resolved Incidents", value: "—", note: "Awaiting incident data" },
        { label: "Pending Incidents", value: "—", note: "Awaiting incident data" },
        { label: "Average Resolution Time", value: "—", note: "Awaiting incident data" }
    ];

    return (
        <div className="analytics-page">
            <header className="analytics-header">
                <div>
                    <p className="analytics-eyebrow">SMART CAMPUS</p>
                    <h1>Analytics & AI Insights</h1>
                    <p className="analytics-subtitle">
                        Monitor campus incidents, understand trends, and view
                        intelligent recommendations.
                    </p>
                </div>

                <div className="analytics-header-actions">
                    <NavLink to={dashboardPath} className="analytics-back-link">
                        Back to Dashboard
                    </NavLink>

                    <select
                        value={period}
                        onChange={(e) => setPeriod(e.target.value)}
                        aria-label="Select analytics period"
                    >
                        <option value="7">Last 7 days</option>
                        <option value="30">Last 30 days</option>
                        <option value="90">Last 90 days</option>
                        <option value="365">Last 12 months</option>
                    </select>
                </div>
            </header>

            <section className="analytics-section">
                <div className="analytics-section-heading">
                    <div>
                        <h2>Incident Overview</h2>
                        <p>A summary of campus incident activity.</p>
                    </div>
                </div>

                <div className="analytics-stats-grid">
                    {stats.map((stat) => (
                        <div className="analytics-stat-card" key={stat.label}>
                            <p>{stat.label}</p>
                            <h3>{stat.value}</h3>
                            <span>{stat.note}</span>
                        </div>
                    ))}
                </div>
            </section>

            <section className="analytics-charts-grid">
                <div className="analytics-panel">
                    <div className="analytics-panel-heading">
                        <div>
                            <h2>Incident Trends</h2>
                            <p>Incident activity over the selected period.</p>
                        </div>
                    </div>

                    <div className="analytics-empty-state">
                        <div className="analytics-empty-icon">▥</div>
                        <h3>Trend data will appear here</h3>
                        <p>
                            Incident trend charts will be displayed once
                            incident records are connected.
                        </p>
                    </div>
                </div>

                <div className="analytics-panel">
                    <div className="analytics-panel-heading">
                        <div>
                            <h2>Priority Distribution</h2>
                            <p>Breakdown of incidents by priority.</p>
                        </div>
                    </div>

                    <div className="analytics-priority-list">
                        {["Critical", "High", "Medium", "Low"].map((priority) => (
                            <div className="analytics-priority-row" key={priority}>
                                <span className={`priority-dot ${priority.toLowerCase()}`} />
                                <span>{priority}</span>
                                <strong>—</strong>
                            </div>
                        ))}
                    </div>

                    <p className="analytics-data-note">
                        Priority figures will be populated from incident data.
                    </p>
                </div>
            </section>

            <section className="analytics-panel analytics-department-panel">
                <div className="analytics-panel-heading">
                    <div>
                        <h2>Department-wise Analysis</h2>
                        <p>
                            Compare incident volume and resolution performance
                            across departments.
                        </p>
                    </div>
                </div>

                <div className="analytics-table-wrapper">
                    <table className="analytics-table">
                        <thead>
                            <tr>
                                <th>Department</th>
                                <th>Total Incidents</th>
                                <th>Resolved</th>
                                <th>Pending</th>
                                <th>Resolution Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colSpan="5" className="analytics-table-empty">
                                    Department analytics will appear when
                                    department-wise incident data is available.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section className="analytics-ai-section">
                <div className="analytics-ai-heading">
                    <div className="analytics-ai-icon">✦</div>
                    <div>
                        <p className="analytics-eyebrow">INTELLIGENCE CENTRE</p>
                        <h2>AI Insights & Recommendations</h2>
                        <p>
                            Decision-support insights generated from campus
                            incident data.
                        </p>
                    </div>
                </div>

                <div className="analytics-ai-grid">
                    <div className="analytics-ai-card">
                        <span className="analytics-ai-label">PATTERN DETECTION</span>
                        <h3>Incident Patterns</h3>
                        <p>
                            Identifies recurring incident locations, categories,
                            and time-based patterns.
                        </p>
                        <span className="analytics-coming-soon">Awaiting AI results</span>
                    </div>

                    <div className="analytics-ai-card">
                        <span className="analytics-ai-label">RISK ANALYSIS</span>
                        <h3>Risk Assessment</h3>
                        <p>
                            Highlights potential high-risk areas and incidents
                            requiring attention.
                        </p>
                        <span className="analytics-coming-soon">Awaiting AI results</span>
                    </div>

                    <div className="analytics-ai-card">
                        <span className="analytics-ai-label">DECISION SUPPORT</span>
                        <h3>Smart Recommendations</h3>
                        <p>
                            Presents suggested actions and preventive measures
                            based on available incident information.
                        </p>
                        <span className="analytics-coming-soon">Awaiting AI results</span>
                    </div>
                </div>

                <div className="analytics-ai-footer">
                    <span>✦</span>
                    AI-generated results will be displayed here when provided
                    by the Decision Engine.
                </div>
            </section>

            <footer className="analytics-footer">
                <p>SMART CAMPUS · Analytics & AI Results</p>
                <p>Data and AI insights are subject to backend availability.</p>
            </footer>
        </div>
    );
}

export default AnalyticsDashboard;

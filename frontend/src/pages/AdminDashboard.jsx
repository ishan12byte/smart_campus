function AdminDashboard() {
    return (
        <div>

            {/* Dashboard Header */}
            <div>
                <h1>Super Admin Dashboard</h1>
                <p>Campus-wide incident monitoring and operations.</p>
            </div>

            {/* KPI Cards */}
            <div>
                <div>
                    <h3>Total Incidents</h3>
                    <h2>24</h2>
                    <p>+12% this month</p>
                </div>

                <div>
                    <h3>Open Incidents</h3>
                    <h2>8</h2>
                    <p>3 high priority</p>
                </div>

                <div>
                    <h3>In Progress</h3>
                    <h2>6</h2>
                    <p>2 awaiting action</p>
                </div>

                <div>
                    <h3>Resolved</h3>
                    <h2>10</h2>
                    <p>+18% this month</p>
                </div>
            </div>

            {/* Analytics */}
            <div>
                <div>
                    <h2>Incident Trend</h2>
                    <p>Incident activity over the past week.</p>

                    <div>
                        <p>Mon: 3 incidents</p>
                        <p>Tue: 5 incidents</p>
                        <p>Wed: 2 incidents</p>
                        <p>Thu: 6 incidents</p>
                        <p>Fri: 4 incidents</p>
                        <p>Sat: 2 incidents</p>
                        <p>Sun: 2 incidents</p>
                    </div>
                </div>

                <div>
                    <h2>Status Distribution</h2>
                    <p>Current incident lifecycle status.</p>

                    <div>
                        <p>Open: 8</p>
                        <p>Acknowledged: 2</p>
                        <p>Under Review: 3</p>
                        <p>In Progress: 6</p>
                        <p>Resolved: 5</p>
                    </div>
                </div>
            </div>

            {/* Recent Incidents */}
            <div>
                <div>
                    <h2>Recent Incidents</h2>
                    <button>View All</button>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Incident ID</th>
                            <th>Category</th>
                            <th>Location</th>
                            <th>Priority</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr>
                            <td>INC-024</td>
                            <td>Electrical</td>
                            <td>Block A</td>
                            <td>High</td>
                            <td>Open</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-023</td>
                            <td>Security</td>
                            <td>Main Gate</td>
                            <td>Critical</td>
                            <td>Under Review</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-022</td>
                            <td>Water Supply</td>
                            <td>Block C</td>
                            <td>Medium</td>
                            <td>Resolved</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-021</td>
                            <td>Maintenance</td>
                            <td>Library</td>
                            <td>Low</td>
                            <td>Assigned</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>
    )
}

export default AdminDashboard
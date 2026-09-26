function StaffDashboard() {

    return (
        <div>

            {/* Dashboard Header */}
            <div>
                <h1>Staff Dashboard</h1>
                <p>Welcome back!</p>
            </div>


            {/* Summary Cards */}
            <div>

                <div>
                    <h3>Assigned Incidents</h3>
                    <p>6</p>
                </div>

                <div>
                    <h3>In Progress</h3>
                    <p>3</p>
                </div>

                <div>
                    <h3>Pending Verification</h3>
                    <p>1</p>
                </div>

                <div>
                    <h3>Resolved</h3>
                    <p>2</p>
                </div>

            </div>


            {/* Assigned Incidents */}
            <div>

                <h2>Assigned Incidents</h2>

                <table style={{margin: "0 auto"}}>
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
                            <td>INC-001</td>
                            <td>Electrical</td>
                            <td>Block A</td>
                            <td>High</td>
                            <td>In Progress</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-002</td>
                            <td>Maintenance</td>
                            <td>Library</td>
                            <td>Medium</td>
                            <td>Assigned</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-003</td>
                            <td>Plumbing</td>
                            <td>Block C</td>
                            <td>Low</td>
                            <td>Pending Verification</td>
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

export default StaffDashboard
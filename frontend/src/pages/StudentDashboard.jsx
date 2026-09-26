function StudentDashboard() {

    return (
        <div>

            {/* Student Header */}
            <div>
                <h1>Student Dashboard</h1>
                <p>Track the incidents you have reported.</p>
            </div>


            {/* Student Summary */}
            <div>

                <div>
                    <h3>My Reports</h3>
                    <p>7</p>
                </div>

                <div>
                    <h3>Open Reports</h3>
                    <p>2</p>
                </div>

                <div>
                    <h3>Under Review</h3>
                    <p>1</p>
                </div>

                <div>
                    <h3>Resolved</h3>
                    <p>4</p>
                </div>

            </div>


            {/* Recent Reports */}
            <div>

                <h2>My Recent Reports</h2>

                <table style ={{margin: "0 auto"}}>

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

                        <tr>
                            <td>INC-001</td>
                            <td>Electrical</td>
                            <td>Block A</td>
                            <td>18 Sep 2026</td>
                            <td>Under Review</td>
                            <td>
                                <button>View Details</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-002</td>
                            <td>Maintenance</td>
                            <td>Library</td>
                            <td>16 Sep 2026</td>
                            <td>Open</td>
                            <td>
                                <button>View Details</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-003</td>
                            <td>Water Supply</td>
                            <td>Block C</td>
                            <td>12 Sep 2026</td>
                            <td>Resolved</td>
                            <td>
                                <button>View Details</button>
                            </td>
                        </tr>

                    </tbody>

                </table>

            </div>


            {/* Student Action */}
            <div>
                <h2>Need to report a new issue?</h2>
                <p>Submit an incident report to the campus operations team.</p>
                <button>Report New Incident</button>
            </div>

        </div>
    )
}

export default StudentDashboard
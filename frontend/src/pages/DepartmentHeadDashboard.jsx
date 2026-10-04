function DepartmentHeadDashboard(){
    return(
        <div>
            <h1>Department Head Dashboard</h1>

            <p>Review and manage incidents requiring attention</p>

            <div>
                <h2>Incidents Review Queue</h2>

                <table style={{margin: "0 auto"}}>
                    <thead>
                        <tr>
                            <th>Incident ID</th>
                            <th>Category</th>
                            <th>Location</th>
                            <th>Priority</th>
                            <th>Recommendation</th>
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
                            <td>Assign to Electrical Team</td>
                            <td>Under Review</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-002</td>
                            <td>Water Supply</td>
                            <td>Block C</td>
                            <td>Medium</td>
                            <td>Review Maintenance Team</td>
                            <td>Pending Review</td>
                            <td>
                                <button>View</button>
                            </td>
                        </tr>

                        <tr>
                            <td>INC-003</td>
                            <td>Maintenance</td>
                            <td>Library</td>
                            <td>Low</td>
                            <td>Assign to Maintenance Team</td>
                            <td>Under Review</td>
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
export default DepartmentHeadDashboard
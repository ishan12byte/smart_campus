function ReportIncident() {

    return (
        <div>

            <h1>Report New Incident</h1>

            <p>Submit an issue to the campus operations team.</p>

            <form>

                <div>
                    <label>Description</label>
                    <textarea />
                </div>

                <div>
                    <label>Category</label>
                    <select>
                        <option>Select category</option>
                        <option>Electrical</option>
                        <option>Water Supply</option>
                        <option>Maintenance</option>
                        <option>Security</option>
                    </select>
                </div>

                <div>
                    <label>Subcategory</label>
                    <select>
                        <option>Select subcategory</option>
                        <option>Power Outage</option>
                        <option>Leakage</option>
                        <option>Cleaning</option>
                        <option>Access Issue</option>
                    </select>
                </div>

                <div>
                    <label>Location</label>
                    <input type="text" placeholder="Enter incident location" />
                </div>

                <div>
                    <label>Date</label>
                    <input type="date" />
                </div>

                <div>
                    <label>Time</label>
                    <input type="time" />
                </div>

                <div>
                    <label>Session ID (optional)</label>
                    <input type="text" />
                </div>

                <div>
                    <label>Service Cycle ID (optional)</label>
                    <input type="text" />
                </div>

                <div>
                    <label>Evidence (optional)</label>
                    <input type="file" />
                </div>

                <button type="submit">Submit Incident</button>

            </form>

        </div>
    )
}

export default ReportIncident
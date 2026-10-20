import { useState } from "react";
import { createIncident } from "../services/incidents";
function ReportIncident() {
    const [formData, setFormData] = useState
    ({
    description: "",
    category: "",
    subcategory: "",
    location: "",
    date: "",
    time: "",
    session_id: "",
    service_cycle_id: "",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const handleSubmit = async (e) => 
        {
        e.preventDefault();
        console.log("Submit handler is running");

        setError("");
        setSuccess("");
        setLoading(true);

        try 
        {
        const incidentData = 
        {
        title: `${formData.category} Incident`,
        description: formData.description,
        category: formData.category,
        subcategory: formData.subcategory,
        location: formData.location,
        };

        const result = await createIncident(incidentData);

        setSuccess("Incident reported successfully!");

        setFormData({
        description: "",
        category: "",
        subcategory: "",
        location: "",
        date: "",
        time: "",
        session_id: "",
        service_cycle_id: "",
        });

        console.log("Created incident:", result);
            } 
        catch (err) 
        {
            setError(err.message || "Failed to submit incident.");
        } 
        finally 
        {
        setLoading(false);
        }
        };

    return (
        <div>

            <h1>Report New Incident</h1>

            <p>Submit an issue to the campus operations team.</p>

            <form onSubmit={handleSubmit}>
                {error && <p style={{ color: "red" }}>{error}</p>}
                {success && <p style={{ color: "green" }}>{success}</p>}

                <div>
                    <label>Description</label>
                    <textarea 
                    value={formData.description}
                    onChange={(e)=>
                        setFormData({
                            ...formData,
                            description: e.target.value,
                        })
                    }
                    required
                    />
                </div>

                <div>
                    <label>Category</label>
                    <select
                        value={formData.category}
                        onChange={(e) =>
                            setFormData
                            ({
                                ...formData,
                                category: e.target.value,
                            })
                        }
                    required
                    >
                        <option value="">Select category</option>
                        <option value="Electrical">Electrical</option>
                        <option value="Water Supply">Water Supply</option>
                        <option value="Maintenance">Maintenance</option>
                        <option value="Security">Security</option>
                    </select>


                </div>

                <div>
                    <label>Subcategory</label>
                    <select
                        value={formData.subcategory}
                        onChange={(e) =>
                            setFormData({
                                ...formData,
                                subcategory: e.target.value,
                                })
                            }
                            required
                        >
                            <option value="">Select subcategory</option>
                            <option value="Power Outage">Power Outage</option>
                            <option value="Leakage">Leakage</option>
                            <option value="Cleaning">Cleaning</option>
                            <option value="Access Issue">Access Issue</option>
                    </select>
                </div>

                <div>
                    <label>Location</label>
                    <input type="text" 
                    placeholder="Enter incident location" 
                    value={formData.location}
                    onChange={(e) =>
                    setFormData({
                        ...formData,
                        location: e.target.value,
                        })
                    }
                    required
                    />
                </div>

                <div>
                    <label>Date</label>
                    <input type="date" 
                     value={formData.date}
                    onChange={(e) =>
                    setFormData({
                        ...formData,
                    date: e.target.value,
                        })
                    }
                    required
                    />
                </div>

                <div>
                    <label>Time</label>
                    <input type="time" 
                    value={formData.time}
                    onChange={(e) =>
                        setFormData({
                            ...formData,
                            time: e.target.value,
                        })
                    }
                    required
                    />
                </div>

                <div>
                    <label>Session ID (optional)</label>
                    <input type="text" 
                    value={formData.session_id}
                    onChange={(e) =>
                        setFormData({
                        ...formData,
                        session_id: e.target.value,
                        })
                    }
                    placeholder="Enter session ID (optional)"
                    />
                </div>

                <div>
                    <label>Service Cycle ID (optional)</label>
                    <input type="text" 
                        value={formData.service_cycle_id}
                        onChange={(e) =>
                            setFormData({
                                ...formData,
                                service_cycle_id: e.target.value,
                            })
                        }
                        placeholder="Enter service cycle ID (optional)"
                    />
                </div>

                <div>
                    <label>Evidence (optional)</label>
                    <input type="file" />
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? "Submitting..." : "Submit Incident"}
                </button>

            </form>

        </div>
    )
}

export default ReportIncident
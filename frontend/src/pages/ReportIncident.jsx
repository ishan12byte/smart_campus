
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createIncident } from "../services/incidents";
import "./ReportIncident.css";

const initialFormData = {
  description: "",
  category: "",
  otherCategory: "",
  subcategory: "",
  location: "",
  date: "",
  time: "",
  session_id: "",
  service_cycle_id: "",
};

const categories = [
  "Electrical",
  "Water Supply",
  "Cleaning & Sanitation",
  "Maintenance & Infrastructure",
  "Security & Safety",
  "Classroom & Furniture",
  "Internet & Network",
  "Transport",
  "Other",
];

const subcategoryOptions = {
  Electrical: [
    "Power Outage",
    "Faulty Wiring",
    "Damaged Switch",
    "Lighting Issue",
  ],

  "Water Supply": [
    "Water Leakage",
    "No Water Supply",
    "Low Water Pressure",
    "Drainage Issue",
  ],

  "Cleaning & Sanitation": [
    "Washroom Cleaning",
    "Waste Disposal",
    "Pest Control",
    "Unclean Area",
  ],

  "Maintenance & Infrastructure": [
    "Building Damage",
    "Plumbing Issue",
    "Broken Door",
    "Lift Issue",
  ],

  "Security & Safety": [
    "Theft",
    "Unauthorized Access",
    "Harassment",
    "Safety Hazard",
  ],

  "Classroom & Furniture": [
    "Broken Desk",
    "Damaged Chair",
    "Projector Issue",
    "Board Damage",
  ],

  "Internet & Network": [
    "Wi-Fi Not Working",
    "Slow Internet",
    "Network Outage",
  ],

  Transport: [
    "Bus Delay",
    "Vehicle Breakdown",
    "Route Issue",
  ],

  Other: [
    "Other / Not Listed",
  ],
};

function ReportIncident() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState(initialFormData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((previousData) => {
      if (name === "category") {
        return {
          ...previousData,
          category: value,
          subcategory: "",
          otherCategory:
            value === "Other" ? previousData.otherCategory : "",
        };
      }

      return {
        ...previousData,
        [name]: value,
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (
      formData.category === "Other" &&
      !formData.otherCategory.trim()
    ) {
      setError("Please specify your incident category.");
      return;
    }

    setLoading(true);

    try {
      const selectedCategory =
        formData.category === "Other"
          ? formData.otherCategory.trim()
          : formData.category;

      const finalDescription =
        formData.category === "Other"
          ? `Specified category: ${selectedCategory}\n\n${formData.description}`
          : formData.description;

      const incidentData = {
        title: `${selectedCategory} Incident`,
        description: finalDescription,
        category: formData.category,
        subcategory: formData.subcategory,
        location: formData.location,
      };

      await createIncident(incidentData);

      setSuccess("Your incident has been reported successfully!");
      setFormData(initialFormData);
    } catch (err) {
      setError(
        err.message || "Failed to submit incident. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-page">
      <header className="report-topbar">
        <div className="report-brand">
          <div className="report-brand-icon">SC</div>
          <span>SMART CAMPUS</span>
        </div>

        <button
          type="button"
          className="report-back-button"
          onClick={() => navigate("/student")}
        >
          ← Back to Dashboard
        </button>
      </header>

      <main className="report-main">
        <section className="report-heading">
          <div>
            <p className="report-eyebrow">CAMPUS SUPPORT</p>
            <h1>Report an Incident</h1>
            <p className="report-subtitle">
              Help us keep the campus safe and running smoothly.
              Share the details below and our operations team will look into it.
            </p>
          </div>

          <div className="report-heading-icon" aria-hidden="true">
            <span>!</span>
          </div>
        </section>

        <form className="report-form" onSubmit={handleSubmit}>
          <div className="report-form-intro">
            <div>
              <h2>Incident details</h2>
              <p>Fields marked with * are required.</p>
            </div>
            <span className="report-required-tag">NEW REPORT</span>
          </div>

          {error && (
            <div className="report-alert report-alert-error" role="alert">
              <strong>Unable to submit</strong>
              <p>{error}</p>
            </div>
          )}

          {success && (
            <div className="report-alert report-alert-success" role="status">
              <strong>Report submitted</strong>
              <p>{success}</p>
            </div>
          )}

          {/* SECTION 01: ISSUE INFORMATION */}
          <section className="report-section">
            <div className="report-section-heading">
              <span className="report-section-number">01</span>
              <div>
                <h3>Issue information</h3>
                <p>Tell us what happened.</p>
              </div>
            </div>

            <div className="report-field-grid">
              <div className="report-field">
                <label htmlFor="category">Incident category *</label>

                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select a category</option>

                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              {formData.category === "Other" && (
                <div className="report-field">
                  <label htmlFor="otherCategory">
                    Specify your category *
                  </label>

                  <input
                    id="otherCategory"
                    type="text"
                    name="otherCategory"
                    value={formData.otherCategory}
                    onChange={handleChange}
                    placeholder="Enter your incident category"
                    required
                  />
                </div>
              )}

              <div className="report-field">
                <label htmlFor="subcategory">Subcategory *</label>

                <select
                  id="subcategory"
                  name="subcategory"
                  value={formData.subcategory}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select a subcategory</option>

                  {(subcategoryOptions[formData.category] || []).map(
                    (subcategory) => (
                      <option key={subcategory} value={subcategory}>
                        {subcategory}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div className="report-field report-field-full">
                <label htmlFor="description">Description *</label>

                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Describe the issue in detail. Include anything that could help the team understand and resolve it."
                  rows="5"
                  required
                />

                <span className="report-field-hint">
                  Be as specific as possible.
                </span>
              </div>
            </div>
          </section>

          {/* SECTION 02: LOCATION AND TIME */}
          <section className="report-section">
            <div className="report-section-heading">
              <span className="report-section-number">02</span>
              <div>
                <h3>Location and time</h3>
                <p>Help the team find when and where it happened.</p>
              </div>
            </div>

            <div className="report-field-grid">
              <div className="report-field report-field-full">
                <label htmlFor="location">Incident location *</label>

                <input
                  id="location"
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="e.g. Block A, Room 204, Library"
                  required
                />
              </div>

              <div className="report-field">
                <label htmlFor="date">Date *</label>

                <input
                  id="date"
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="report-field">
                <label htmlFor="time">Time *</label>

                <input
                  id="time"
                  type="time"
                  name="time"
                  value={formData.time}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          </section>

          {/* SECTION 03: ADDITIONAL INFORMATION */}
          <section className="report-section">
            <div className="report-section-heading">
              <span className="report-section-number">03</span>
              <div>
                <h3>Additional information</h3>
                <p>These details are optional.</p>
              </div>
            </div>

            <div className="report-field-grid">
              <div className="report-field">
                <label htmlFor="session_id">Session ID</label>

                <input
                  id="session_id"
                  type="text"
                  name="session_id"
                  value={formData.session_id}
                  onChange={handleChange}
                  placeholder="Enter session ID"
                />
              </div>

              <div className="report-field">
                <label htmlFor="service_cycle_id">Service Cycle ID</label>

                <input
                  id="service_cycle_id"
                  type="text"
                  name="service_cycle_id"
                  value={formData.service_cycle_id}
                  onChange={handleChange}
                  placeholder="Enter service cycle ID"
                />
              </div>

              <div className="report-field report-field-full">
                <label htmlFor="evidence">Evidence attachment</label>

                <input
                  id="evidence"
                  type="file"
                  className="report-file-input"
                  accept="image/*,.pdf"
                />

                <span className="report-field-hint">
                  Optional. File selection is displayed here, but upload is not
                  connected to the API yet.
                </span>
              </div>
            </div>
          </section>

          {/* FORM ACTIONS */}
          <div className="report-form-footer">
            <p>
              Please review your details before submitting your report.
            </p>

            <div className="report-form-actions">
              <button
                type="button"
                className="report-cancel-button"
                onClick={() => navigate("/student")}
                disabled={loading}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="report-submit-button"
                disabled={loading}
              >
                {loading ? "Submitting..." : "Submit Incident →"}
              </button>
            </div>
          </div>
        </form>

        <p className="report-footer-note">
          SMART CAMPUS · Incident Reporting System
        </p>
      </main>
    </div>
  );
}

export default ReportIncident;

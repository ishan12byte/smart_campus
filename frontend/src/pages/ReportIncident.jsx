
import { useRef, useState } from "react";
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

const DESCRIPTION_LIMIT = 1000;

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
    Other: ["Other / Not Listed"],
};

function ReportIncident() {
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const [formData, setFormData] = useState(initialFormData);
    const [selectedFile, setSelectedFile] = useState(null);
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((previous) => {
            if (name === "category") {
                return {
                    ...previous,
                    category: value,
                    subcategory: "",
                    otherCategory:
                        value === "Other" ? previous.otherCategory : "",
                };
            }

            return {
                ...previous,
                [name]: value,
            };
        });

        setErrors((previous) => ({
            ...previous,
            [name]: "",
            ...(name === "category"
                ? { subcategory: "", otherCategory: "" }
                : {}),
        }));

        setError("");
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.category) {
            newErrors.category = "Please select an incident category.";
        }

        if (
            formData.category === "Other" &&
            !formData.otherCategory.trim()
        ) {
            newErrors.otherCategory = "Please specify your category.";
        }

        if (!formData.subcategory) {
            newErrors.subcategory = "Please select a subcategory.";
        }

        if (!formData.description.trim()) {
            newErrors.description = "Please describe the incident.";
        } else if (formData.description.trim().length < 10) {
            newErrors.description =
                "Please provide at least 10 characters.";
        }

        if (!formData.location.trim()) {
            newErrors.location = "Please enter the incident location.";
        }

        if (!formData.date) {
            newErrors.date = "Please select the incident date.";
        }

        if (!formData.time) {
            newErrors.time = "Please select the incident time.";
        }

        setErrors(newErrors);

        return Object.keys(newErrors).length === 0;
    };

    const handleFileChange = (event) => {
        const file = event.target.files?.[0];

        if (!file) return;

        const isAllowedType =
            file.type.startsWith("image/") ||
            file.type === "application/pdf";

        if (!isAllowedType) {
            setError("Please select an image or PDF file.");
            event.target.value = "";
            setSelectedFile(null);
            return;
        }

        setError("");
        setSelectedFile(file);
    };

    const removeFile = () => {
        setSelectedFile(null);

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return `${bytes} bytes`;

        if (bytes < 1024 * 1024) {
            return `${(bytes / 1024).toFixed(1)} KB`;
        }

        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError("");

        if (!validateForm()) {
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
                    ? `Specified category: ${selectedCategory}\n\n${formData.description.trim()}`
                    : formData.description.trim();

            // Send all confirmed fields to the existing JSON API.
            const incidentData = {
                title: `${selectedCategory} Incident`,
                description: finalDescription,
                category: formData.category,
                subcategory: formData.subcategory,
                location: formData.location.trim(),
                date: formData.date,
                time: formData.time,
                session_id: formData.session_id.trim(),
                service_cycle_id: formData.service_cycle_id.trim(),
            };

            await createIncident(incidentData);

            setSubmitted(true);
            setFormData(initialFormData);
            setSelectedFile(null);
            setErrors({});

            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        } catch (err) {
            setError(
                err?.message ||
                "Failed to submit incident. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    const startNewReport = () => {
        setSubmitted(false);
        setError("");
        setErrors({});
        setFormData(initialFormData);
        setSelectedFile(null);

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    if (submitted) {
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
                        Back to Dashboard
                    </button>
                </header>

                <main className="report-main report-success-main">
                    <section className="report-success-card">
                        <div className="report-success-icon">✓</div>

                        <p className="report-eyebrow">
                            CAMPUS SUPPORT
                        </p>

                        <h1>Report Submitted!</h1>

                        <p>
                            Your incident report has been submitted
                            successfully. You can view your submitted
                            reports and follow their progress from
                            the My Incidents section.
                        </p>

                        <div className="report-success-actions">
                            <button
                                type="button"
                                className="report-submit-button"
                                onClick={() => navigate("/my-incidents")}
                            >
                                View My Incidents →
                            </button>

                            <button
                                type="button"
                                className="report-cancel-button"
                                onClick={startNewReport}
                            >
                                Report Another Incident
                            </button>
                        </div>
                    </section>

                    <p className="report-footer-note">
                        SMART CAMPUS · Incident Reporting System
                    </p>
                </main>
            </div>
        );
    }

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
                            Share the details below and our operations team
                            will look into it.
                        </p>
                    </div>

                    <div className="report-heading-icon" aria-hidden="true">
                        <span>!</span>
                    </div>
                </section>

                <form
                    className="report-form"
                    onSubmit={handleSubmit}
                    noValidate
                >
                    <div className="report-form-intro">
                        <div>
                            <h2>Incident details</h2>
                            <p>Fields marked with * are required.</p>
                        </div>

                        <span className="report-required-tag">
                            NEW REPORT
                        </span>
                    </div>

                    {error && (
                        <div
                            className="report-alert report-alert-error"
                            role="alert"
                        >
                            <strong>Unable to submit</strong>
                            <p>{error}</p>
                        </div>
                    )}

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
                                <label htmlFor="category">
                                    Incident category *
                                </label>

                                <select
                                    id="category"
                                    name="category"
                                    value={formData.category}
                                    onChange={handleChange}
                                    className={
                                        errors.category ? "field-invalid" : ""
                                    }
                                >
                                    <option value="">Select a category</option>

                                    {categories.map((category) => (
                                        <option key={category} value={category}>
                                            {category}
                                        </option>
                                    ))}
                                </select>

                                {errors.category && (
                                    <span className="report-error-text">
                                        {errors.category}
                                    </span>
                                )}
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
                                        className={
                                            errors.otherCategory
                                                ? "field-invalid"
                                                : ""
                                        }
                                    />

                                    {errors.otherCategory && (
                                        <span className="report-error-text">
                                            {errors.otherCategory}
                                        </span>
                                    )}
                                </div>
                            )}

                            <div className="report-field">
                                <label htmlFor="subcategory">
                                    Subcategory *
                                </label>

                                <select
                                    id="subcategory"
                                    name="subcategory"
                                    value={formData.subcategory}
                                    onChange={handleChange}
                                    disabled={!formData.category}
                                    className={
                                        errors.subcategory ? "field-invalid" : ""
                                    }
                                >
                                    <option value="">
                                        Select a subcategory
                                    </option>

                                    {(subcategoryOptions[formData.category] || [])
                                        .map((subcategory) => (
                                            <option
                                                key={subcategory}
                                                value={subcategory}
                                            >
                                                {subcategory}
                                            </option>
                                        ))}
                                </select>

                                {errors.subcategory && (
                                    <span className="report-error-text">
                                        {errors.subcategory}
                                    </span>
                                )}
                            </div>

                            <div className="report-field report-field-full">
                                <label htmlFor="description">
                                    Description *
                                </label>

                                <textarea
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    placeholder="Describe the issue in detail. Include anything that could help the team understand and resolve it."
                                    rows="5"
                                    maxLength={DESCRIPTION_LIMIT}
                                    className={
                                        errors.description ? "field-invalid" : ""
                                    }
                                />

                                <div className="report-description-footer">
                                    {errors.description ? (
                                        <span className="report-error-text">
                                            {errors.description}
                                        </span>
                                    ) : (
                                        <span className="report-field-hint">
                                            Be as specific as possible.
                                        </span>
                                    )}

                                    <span className="report-character-count">
                                        {formData.description.length}/
                                        {DESCRIPTION_LIMIT}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="report-section">
                        <div className="report-section-heading">
                            <span className="report-section-number">02</span>
                            <div>
                                <h3>Location and time</h3>
                                <p>
                                    Help the team find when and where it happened.
                                </p>
                            </div>
                        </div>

                        <div className="report-field-grid">
                            <div className="report-field report-field-full">
                                <label htmlFor="location">
                                    Incident location *
                                </label>

                                <input
                                    id="location"
                                    type="text"
                                    name="location"
                                    value={formData.location}
                                    onChange={handleChange}
                                    placeholder="e.g. Block A, Room 204, Library"
                                    className={
                                        errors.location ? "field-invalid" : ""
                                    }
                                />

                                {errors.location && (
                                    <span className="report-error-text">
                                        {errors.location}
                                    </span>
                                )}
                            </div>

                            <div className="report-field">
                                <label htmlFor="date">Date *</label>

                                <input
                                    id="date"
                                    type="date"
                                    name="date"
                                    value={formData.date}
                                    onChange={handleChange}
                                    className={errors.date ? "field-invalid" : ""}
                                />

                                {errors.date && (
                                    <span className="report-error-text">
                                        {errors.date}
                                    </span>
                                )}
                            </div>

                            <div className="report-field">
                                <label htmlFor="time">Time *</label>

                                <input
                                    id="time"
                                    type="time"
                                    name="time"
                                    value={formData.time}
                                    onChange={handleChange}
                                    className={errors.time ? "field-invalid" : ""}
                                />

                                {errors.time && (
                                    <span className="report-error-text">
                                        {errors.time}
                                    </span>
                                )}
                            </div>
                        </div>
                    </section>

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
                                <label htmlFor="service_cycle_id">
                                    Service Cycle ID
                                </label>

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
                                <label htmlFor="evidence">
                                    Evidence attachment
                                </label>

                                <input
                                    ref={fileInputRef}
                                    id="evidence"
                                    type="file"
                                    className="report-file-input"
                                    accept="image/*,.pdf"
                                    onChange={handleFileChange}
                                />

                                <span className="report-field-hint">
                                    Optional. Images and PDF files can be selected.
                                    File upload is not connected to the API yet.
                                </span>

                                {selectedFile && (
                                    <div className="report-file-preview">
                                        <div className="report-file-info">
                                            <span className="report-file-icon">
                                                {selectedFile.type === "application/pdf"
                                                    ? "PDF"
                                                    : "IMG"}
                                            </span>

                                            <div>
                                                <strong>{selectedFile.name}</strong>
                                                <span>
                                                    {formatFileSize(selectedFile.size)}
                                                </span>
                                            </div>
                                        </div>

                                        <button
                                            type="button"
                                            className="report-file-remove"
                                            onClick={removeFile}
                                        >
                                            Remove
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </section>

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

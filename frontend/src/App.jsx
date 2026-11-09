
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login.jsx";
import StudentDashboard from "./pages/StudentDashboard";
import StaffDashboard from "./pages/StaffDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import DepartmentHeadDashboard from "./pages/DepartmentHeadDashboard";
import SuperAdminDashboard from "./pages/SuperAdminDashboard";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import ReportIncident from "./pages/ReportIncident";
import MyIncidents from "./pages/MyIncidents";
import IncidentDetails from "./pages/IncidentDetails";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/login" replace />} />
                <Route path="/login" element={<Login />} />

                <Route path="/student" element={<StudentDashboard />} />
                <Route path="/staff/*" element={<StaffDashboard />} />
                <Route path="/department/*" element={<DepartmentHeadDashboard />} />
                <Route path="/admin/*" element={<AdminDashboard />} />
                <Route path="/super-admin/*" element={<SuperAdminDashboard />} />

                <Route path="/report-incident" element={<ReportIncident />} />
                <Route path="/my-incidents" element={<MyIncidents />} />
                <Route path="/incident/:incidentId" element={<IncidentDetails />} />

                <Route path="/analytics" element={<AnalyticsDashboard />} />

                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;

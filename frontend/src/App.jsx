import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from './pages/Login.jsx'
import StudentDashboard from './pages/StudentDashboard'
import StaffDashboard from './pages/StaffDashboard'
import AdminDashboard from './pages/AdminDashboard'
import DepartmentHeadDashboard from "./pages/DepartmentHeadDashboard";
import ReportIncident from "./pages/ReportIncident"

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />}/>
        <Route path="/student" element={<StudentDashboard/>}/>
        <Route path="/staff" element={<StaffDashboard/>}/>
        <Route path="/admin" element={<AdminDashboard/>}/>
        <Route path="/department" element={<DepartmentHeadDashboard/>}/>
        <Route path="/report" element={<ReportIncident/>}/>
      </Routes>
    </BrowserRouter>
    )
}

export default App

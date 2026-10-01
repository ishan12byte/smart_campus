import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from './pages/Login.jsx'
import StudentDashboard from './pages/StudentDashboard'
import StaffDashboard from './pages/StaffDashboard'
import AdminDashboard from './pages/AdminDashboard'

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />}/>
        <Route path="/student" element={<StudentDashboard/>}/>
        <Route path="/staff" element={<StaffDashboard/>}/>
        <Route path="/admin" element={<AdminDashboard/>}/>
      </Routes>
    </BrowserRouter>
    )
}

export default App

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import StudentDashboard from './pages/StudentDashboard';
import FacultyDashboard from './pages/FacultyDashboard';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);

  const handleLogin = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} />
        
        <Route 
          path="/dashboard" 
          element={
            !user ? <Navigate to="/login" /> : 
            user.role === 'admin' ? <AdminDashboard user={user} onLogout={handleLogout} /> :
            user.role === 'faculty' ? <FacultyDashboard user={user} onLogout={handleLogout} /> :
            <StudentDashboard user={user} onLogout={handleLogout} />
          } 
        />

        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}
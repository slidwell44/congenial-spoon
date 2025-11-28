import { useMemo } from 'react';
import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom';

import Dashboard from './pages/Dashboard';
import EmployeeProfile from './pages/EmployeeProfile';
import SkillsMatrix from './pages/SkillsMatrix';
import OneOnOnes from './pages/OneOnOnes';
import { CurrentUserContext } from './context/CurrentUserContext';
import './App.css';

function App() {
  const currentUser = useMemo(
    () => ({
      uid: '11111111-1111-1111-1111-111111111111',
      role: 'MANAGER',
      name: 'Riley Manager'
    }),
    []
  );

  return (
    <CurrentUserContext.Provider value={currentUser}>
      <BrowserRouter>
        <div className="app-shell">
          <aside className="sidebar">
            <div className="brand">
              <h1>People Tool</h1>
              <p className="user-name">{currentUser.name}</p>
            </div>
            <nav>
              <NavLink to="/" end>
                Dashboard
              </NavLink>
              <NavLink to={`/employees/${currentUser.uid}`}>My Profile</NavLink>
              <NavLink to="/skills-matrix">Skills Matrix</NavLink>
            </nav>
          </aside>
          <main className="content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/employees/:employeeUid" element={<EmployeeProfile />} />
              <Route path="/skills-matrix" element={<SkillsMatrix />} />
              <Route path="/one-on-ones" element={<OneOnOnes />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </CurrentUserContext.Provider>
  );
}

export default App;

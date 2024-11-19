import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css'; // Optional for styling

const Navbar: React.FC = () => {
  const [isDashboardVisible, setDashboardVisible] = useState(false);
  const location = useLocation();

  const toggleDashboard = () => {
    setDashboardVisible(!isDashboardVisible);
  };

  const pageTitles: { [key: string]: string } = {
    '/': 'Dashboard',
    '/manage': 'Manage',
    '/log': 'Log',
    '/detections': 'Detections',
    '/notifications': 'Notifications',
  };

  const currentPageTitle = pageTitles[location.pathname] || 'Page';

  return (
    <div className="navbar">
      <div className="navbar-left">Soney</div>
      <div className="navbar-center">{currentPageTitle}</div>
      <div className="navbar-right">
        <button className="menu-button" onClick={toggleDashboard}>
          ☰
        </button>
      </div>

      {isDashboardVisible && (
        <div className="dashboard-menu">
          <ul>
            <li><Link to="/" onClick={toggleDashboard}>Dashboard</Link></li>
            <li><Link to="/manage" onClick={toggleDashboard}>Manage</Link></li>
            <li><Link to="/log" onClick={toggleDashboard}>Log</Link></li>
            <li><Link to="/detections" onClick={toggleDashboard}>Detections</Link></li>
            <li><Link to="/notifications" onClick={toggleDashboard}>Notifications</Link></li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default Navbar;

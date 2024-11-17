import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/api';
import { useTheme } from '../components/ThemeContext';

interface NavbarProps {
  isAuthenticated: boolean;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ isAuthenticated, setIsAuthenticated }) => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    alert('Logged out successfully');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">Chat</Link>
      </div>
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/profile">Profile</Link></li>
        {isAuthenticated ? (
          <li><Link to="/login" onClick={handleLogout}>Logout</Link></li>
        ) : (
          <li><Link to="/login">Login</Link></li>
        )}
        <li><Link to="/signup">Signup</Link></li>
        <li><Link to="/post">Post</Link></li>
        <li><Link to="/chat">Chat</Link></li>
      </ul>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </nav>
  );
};

export default Navbar;
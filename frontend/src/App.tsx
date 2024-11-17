import React, { useEffect, useState } from 'react';
import { Route, Routes, useNavigate } from 'react-router-dom';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Post from './pages/Post';
import Chat from './pages/Chat';
import { getUserProfile } from './services/api';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import { ThemeProvider, useTheme } from './components/ThemeContext';
import './App.css';

const AppContent: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('authToken'));
  const navigate = useNavigate();
  const { theme } = useTheme();

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        await getUserProfile();
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      }
    };
    fetchUserProfile();
  }, []);

  return (
    <div className={`app ${theme}-theme`}>
      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/profile" element={<PrivateRoute isAuthenticated={isAuthenticated}><Profile /></PrivateRoute>} />
        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/post" element={<PrivateRoute isAuthenticated={isAuthenticated}><Post /></PrivateRoute>} />
        <Route path="/chat" element={<PrivateRoute isAuthenticated={isAuthenticated}><Chat /></PrivateRoute>} />
      </Routes>
    </div>
  );
};

const App: React.FC = () => (
  <ThemeProvider>
    <AppContent />
  </ThemeProvider>
);

export default App;

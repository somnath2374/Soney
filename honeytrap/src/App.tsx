import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Manage from './pages/Manage';
import Log from './pages/Log';
import Detections from './pages/Detections';
import Notifications from './pages/Notifications';
import Honeytraps from './pages/Honeytraps';
const App: React.FC = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/manage" element={<Manage />} />
        <Route path="/log" element={<Log />} />
        <Route path="/detections" element={<Detections />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/honeytraps" element={<Honeytraps />} />
      </Routes>
    </Router>
  );
};

export default App;

import React, { useState } from 'react';
import './Honeytraps.css';

const Honeytraps: React.FC = () => {
  const [showCreateWindow, setShowCreateWindow] = useState(false);

  const handleNewClick = () => {
    setShowCreateWindow(true);
  };

  const handleCloseWindow = () => {
    setShowCreateWindow(false);
  };

  return (
    <div className="honeytraps-page">
      <h1 className="page-heading">Honeytraps</h1>
      
      {/* Placeholder Table */}
      <div className="table-placeholder">
        <p>Table to be implemented</p>
      </div>

      {/* New Button */}
      <button className="new-button" onClick={handleNewClick}>
        New
      </button>

      {/* Create New Honeytrap Window */}
      {showCreateWindow && (
        <div className="create-window">
          <nav className="mini-navbar">
            <span className="window-title">Create Honeytrap</span>
            <button className="close-button" onClick={handleCloseWindow}>
              ✖
            </button>
          </nav>
          <div className="create-content">
            <p>Create New Honeytrap:</p>
            <input type="text" className="input-field" placeholder="Enter details..." />
            <button className="submit-button">Submit</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Honeytraps;

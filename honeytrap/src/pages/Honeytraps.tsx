import React, { useState, useEffect } from 'react';
import { createHoneypot, getHoneypots } from '../services/api'; 
import './Honeytraps.css';

type Honeypot = {
  id: string;
  purpose: string;
  username: string;
  email: string;
  friends: string[];
  friend_requests: string[];
};

const Honeytraps: React.FC = () => {
  const [showCreateWindow, setShowCreateWindow] = useState(false);
  const [purpose, setPurpose] = useState('');
  const [honeypots, setHoneypots] = useState<Honeypot[]>([]);

  useEffect(() => {
    fetchHoneypots();
  }, []);

  const fetchHoneypots = async () => {
    try {
      const data = await getHoneypots();
      setHoneypots(data);
    } catch (error) {
      console.error('Failed to fetch honeypots', error);
    }
  };

  const handleNewClick = () => {
    setShowCreateWindow(true);
  };

  const handleCloseWindow = () => {
    setShowCreateWindow(false);
  };

  const handleSubmit = async () => {
    try {
      await createHoneypot(purpose);
      alert('Honeypot created successfully!');
      setShowCreateWindow(false);
      fetchHoneypots(); // Refresh the list of honeypots
    } catch (error) {
      alert('Failed to create honeypot');
    }
  };

  return (
    <div className="honeytraps-page">
      <h1 className="page-heading">Honeytraps</h1>
      
      <div className="table-placeholder">
        {honeypots.length > 0 ? (
          <table className="honeypots-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Purpose</th>
                <th>Friends</th>
                <th>Friend Requests</th>
              </tr>
            </thead>
            <tbody>
              {honeypots.map((honeypot) => (
                <tr key={honeypot.id}>
                  <td>{honeypot.username}</td>
                  <td>{honeypot.email}</td>
                  <td>{honeypot.purpose}</td>
                  <td>{honeypot.friends.join(', ')}</td>
                  <td>{honeypot.friend_requests.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No honeypots available</p>
        )}
      </div>

      <button className="new-button" onClick={handleNewClick}>
        New
      </button>

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
            <input
              type="text"
              className="input-field"
              placeholder="Purpose"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
            />
            <button className="submit-button" onClick={handleSubmit}>
              Submit
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Honeytraps;
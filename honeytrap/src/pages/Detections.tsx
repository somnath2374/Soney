import React, { useState, useEffect } from 'react';
import { getDetectedUsers } from '../services/api';
import './Detections.css';

type DetectedUser = {
  username: string;
  reasons: string[];
  timestamp: string;
};

const Detections: React.FC = () => {
  const [detectedUsers, setDetectedUsers] = useState<DetectedUser[]>([]);

  useEffect(() => {
    fetchDetectedUsers();
  }, []);

  const fetchDetectedUsers = async () => {
    try {
      const data = await getDetectedUsers();
      setDetectedUsers(data);
    } catch (error) {
      console.error('Failed to fetch detected users', error);
    }
  };

  return (
    <div className="detections-page">
      <h1>Detected Bots/Frauds</h1>
      
      {/* Detected Users Table */}
      <table className="detected-users-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Reasons</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {detectedUsers.length > 0 ? (
            detectedUsers.map((user, index) => (
              <tr key={index}>
                <td>{user.username}</td>
                <td>
                  <ul>
                    {user.reasons.map((reason, reasonIndex) => (
                      <li key={reasonIndex}>{reason}</li>
                    ))}
                  </ul>
                </td>
                <td>{user.timestamp}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={3}>No detected users found.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Detections;

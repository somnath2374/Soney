import React, { useState, useEffect } from 'react';
import { getHoneypots, getHoneytrapLogs } from '../services/api'; 
import './Log.css';

type Honeypot = {
  id: string;
  purpose: string;
  username: string;
  email: string;
  friends: string[];
};

type LogEntry = {
  username: string;
  action: string;
  timestamp: string;
};

const Log: React.FC = () => {
  const [honeytraps, setHoneytraps] = useState<Honeypot[]>([]);
  const [selectedHoneytrap, setSelectedHoneytrap] = useState<Honeypot | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');

  useEffect(() => {
    fetchHoneypots();
  }, []);

  const fetchHoneypots = async () => {
    try {
      const data = await getHoneypots();
      setHoneytraps(data);
    } catch (error) {
      console.error('Failed to fetch honeypots', error);
    }
  };

  const fetchLogs = async (username: string) => {
    try {
      const data = await getHoneytrapLogs(username);
      setLogs(data);
    } catch (error) {
      console.error('Failed to fetch logs', error);
    }
  };

  const handleSearch = () => {
    if (searchTerm) {
      setHoneytraps(honeytraps.filter((honeytrap) => honeytrap.username.includes(searchTerm)));
    } else {
      fetchHoneypots(); // Reset to original list
    }
  };

  const handleRowClick = (honeytrap: Honeypot) => {
    setSelectedHoneytrap(honeytrap);
    fetchLogs(honeytrap.username);
  };

  return (
    <div className="log-page">
      <h1>HoneyTrap Log</h1>
      
      {/* Search Bar */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      
      <div className="log-content">
        {/* Honeytrap List */}
        <div className="honeytrap-list">
          <h2>Honeytraps</h2>
          <ul>
            {honeytraps.map((honeytrap) => (
              <li key={honeytrap.id} onClick={() => handleRowClick(honeytrap)}>
                {honeytrap.username}
              </li>
            ))}
          </ul>
        </div>
        
        {/* Logs Section */}
        <div className="logs-section">
          {selectedHoneytrap ? (
            <>
              <h2>Logs for {selectedHoneytrap.username}</h2>
              <p>Purpose: {selectedHoneytrap.purpose}</p>
              <ul>
                {logs.map((log, index) => (
                  <li key={index}>
                    <p>{log.timestamp}: {log.action}</p>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p>Select a honeytrap to view logs.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Log;

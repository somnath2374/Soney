import React, { useState } from 'react';
import './Log.css';

const Log: React.FC = () => {
  const [honeytrapNames, setHoneytrapNames] = useState<string[]>([
    'Trap 1',
    'Trap 2',
    'Trap 3',
  ]);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');

  const handleSearch = () => {
    if (searchTerm) {
      setHoneytrapNames(honeytrapNames.filter((name) => name.includes(searchTerm)));
    } else {
      setHoneytrapNames(['Trap 1', 'Trap 2', 'Trap 3']); // Reset for demo
    }
  };

  const handleRowClick = (name: string) => {
    setSelectedName(name);
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
      
      {/* Table */}
      <div className="log-table">
        <table>
          <thead>
            <tr>
              <th>HoneyTrap Names</th>
            </tr>
          </thead>
          <tbody>
            {honeytrapNames.map((name, index) => (
              <tr key={index} onClick={() => handleRowClick(name)}>
                <td>{name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Details Section */}
      {selectedName && (
        <div className="details-section">
          <h2>{selectedName}</h2>
          <p>Details about {selectedName} will be displayed here.</p>
        </div>
      )}
    </div>
  );
};

export default Log;

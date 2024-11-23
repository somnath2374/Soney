import React, { useState } from 'react';
import './Detections.css';

const Detections: React.FC = () => {
  const [name, setName] = useState<string>('');
  const [history, setHistory] = useState<string[]>([]);

  const handleAdd = () => {
    if (name) {
      setHistory([name, ...history]);
      setName('');
    }
  };

  return (
    <div className="detections-page">
      <h1>Detected Bots/Frauds</h1>
      
      {/* Input Field */}
      <div className="input-section">
        <input
          type="text"
          placeholder="Enter name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button onClick={handleAdd}>Add</button>
      </div>
      
      {/* History */}
      <div className="history-section">
        <h2>History</h2>
        <ul>
          {history.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Detections;

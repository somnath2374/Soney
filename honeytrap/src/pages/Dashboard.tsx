import React, { useState, useEffect } from 'react';
import SummaryMetrics from '../components/SummaryMetrics';
import { getHoneytrapStatistics } from '../services/api'; // Import the API function
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any[]>([]);

  useEffect(() => {
    fetchHoneytrapStatistics();
  }, []);

  const fetchHoneytrapStatistics = async () => {
    try {
      const data = await getHoneytrapStatistics();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch honeytrap statistics', error);
    }
  };

  return (
    <div className="dashboard">
      <h1 className="dashboard-heading">Honeytrap Statistics</h1>
      <div className="metrics-container">
        {metrics.map((metric, index) => (
          <SummaryMetrics key={index} name={metric.name} value={metric.value} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

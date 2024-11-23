import React from 'react';
import SummaryMetrics from '../components/SummaryMetrics';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const metrics = [
    { name: 'Metric 1', value: 42 },
    { name: 'Metric 2', value: 84 },
    { name: 'Metric 3', value: 126 },
    { name: 'Metric 4', value: 21 },
    { name: 'Metric 5', value: 63 },
    { name: 'Metric 6', value: 105 },
  ];

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

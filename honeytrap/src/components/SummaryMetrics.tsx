import React from 'react';
import './SummaryMetrics.css';

interface SummaryMetricProps {
  name: string;
  value: string | number;
}

const SummaryMetrics: React.FC<SummaryMetricProps> = ({ name, value }) => {
  return (
    <div className="summary-card">
      <h3 className="metric-name">{name}</h3>
      <p className="metric-value">{value}</p>
    </div>
  );
};

export default SummaryMetrics;

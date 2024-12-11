import React from 'react';
import './SummaryMetrics.css';

type SummaryMetricsProps = {
  name: string;
  value: any;
};

const SummaryMetrics: React.FC<SummaryMetricsProps> = ({ name, value }) => {
  return (
    <div className="summary-metrics">
      <h2>{name}</h2>
      <p>{value}</p>
    </div>
  );
};

export default SummaryMetrics;

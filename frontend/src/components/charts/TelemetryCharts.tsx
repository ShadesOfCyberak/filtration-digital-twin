import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export const TelemetryCharts: React.FC = () => {
  const history = useSelector((state: RootState) => state.sensor.history);

  const labels = history.map((h) => h.timestamp);

  const pressureData = {
    labels,
    datasets: [
      {
        label: 'Pressure Drop ΔP (bar)',
        data: history.map((h) => h.dp),
        borderColor: '#0284c7',
        backgroundColor: 'rgba(2, 132, 199, 0.12)',
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const flowData = {
    labels,
    datasets: [
      {
        label: 'Flow Rate Q (L/min)',
        data: history.map((h) => h.flow),
        borderColor: '#059669',
        backgroundColor: 'rgba(5, 150, 105, 0.12)',
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#334155', font: { family: 'Inter', weight: 500 } },
      },
    },
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { color: '#64748b' } },
      y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { color: '#64748b' } },
    },
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
      <div className="glass-panel" style={{ height: '320px' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '12px' }}>
          Pressure Drop ΔP (bar)
        </h3>
        <div style={{ height: '240px' }}>
          <Line data={pressureData} options={chartOptions} />
        </div>
      </div>

      <div className="glass-panel" style={{ height: '320px' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '12px' }}>
          Flow Rate Q (L/min)
        </h3>
        <div style={{ height: '240px' }}>
          <Line data={flowData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
};

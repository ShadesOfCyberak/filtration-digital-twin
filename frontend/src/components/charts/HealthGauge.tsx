import React from 'react';

interface HealthGaugeProps {
  label: string;
  score: number;
  sublabel?: string;
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({ label, score, sublabel }) => {
  const getColor = (s: number) => {
    if (s >= 80) return 'var(--accent-emerald)';
    if (s >= 55) return 'var(--accent-amber)';
    return 'var(--accent-coral)';
  };

  const color = getColor(score);
  const strokeDashoffset = 283 - (283 * Math.min(100, Math.max(0, score))) / 100;

  return (
    <div className="glass-panel" style={{ textAlign: 'center', padding: '24px 16px' }}>
      <h4 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '16px' }}>{label}</h4>
      <div style={{ position: 'relative', width: '120px', height: '120px', margin: '0 auto' }}>
        <svg width="120" height="120" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="rgba(0, 0, 0, 0.08)"
            strokeWidth="8"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeDasharray="283"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
            transform="rotate(-90 50 50)"
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          fontSize: '1.4rem',
          fontWeight: 700,
          color: color
        }}>
          {Math.round(score)}%
        </div>
      </div>
      {sublabel && (
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '12px', fontWeight: 500 }}>
          {sublabel}
        </p>
      )}
    </div>
  );
};

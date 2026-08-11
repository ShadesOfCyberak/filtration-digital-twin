import React from 'react';

export const LoadingSpinner: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
    <div style={{
      width: '36px',
      height: '36px',
      border: '3px solid rgba(0, 240, 255, 0.2)',
      borderTopColor: 'var(--accent-cyan)',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }} />
  </div>
);

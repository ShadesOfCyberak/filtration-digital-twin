import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import { toggleLiveMode } from '../../store/slices/sensorSlice';
import { Activity, RefreshCw, Server } from 'lucide-react';

export const Header: React.FC = () => {
  const dispatch = useDispatch();
  const isLive = useSelector((state: RootState) => state.sensor.isLive);
  const health = useSelector((state: RootState) => state.health.systemHealth);

  const status = health?.status || 'healthy';

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 24px',
      height: '74px',
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-card)',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 1000,
      boxShadow: '0 2px 10px rgba(15, 23, 42, 0.04)',
      boxSizing: 'border-box'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #0284c7 0%, #7c3aed 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          boxShadow: '0 4px 14px rgba(2, 132, 199, 0.25)'
        }}>
          <Activity size={24} strokeWidth={2.5} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Filtration System Digital Twin
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Machine Health Monitoring & Failure Prediction Platform
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Server size={18} color="var(--text-muted)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>System Status:</span>
          <span className={`badge badge-${status === 'healthy' ? 'synchronized' : status === 'degraded' ? 'warning' : 'critical'}`}>
            <span className="pulse-dot" />
            {status}
          </span>
        </div>

        <button
          onClick={() => dispatch(toggleLiveMode())}
          className="btn-primary"
          style={{
            padding: '8px 14px',
            fontSize: '0.85rem',
            background: isLive ? 'linear-gradient(135deg, #059669 0%, #047857 100%)' : '#f1f5f9',
            border: isLive ? 'none' : '1px solid #cbd5e1',
            boxShadow: isLive ? '0 4px 12px rgba(5, 150, 105, 0.25)' : 'none',
            color: isLive ? '#ffffff' : '#475569'
          }}
        >
          <RefreshCw size={16} className={isLive ? 'spin' : ''} />
          {isLive ? 'LIVE Telemetry On' : 'Paused'}
        </button>
      </div>
    </header>
  );
};

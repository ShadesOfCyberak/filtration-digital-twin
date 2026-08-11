import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store';
import { acknowledgeAlert } from '../../store/slices/alertSlice';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export const AlertPanel: React.FC = () => {
  const dispatch = useDispatch();
  const alerts = useSelector((state: RootState) => state.alert.alerts);

  if (!alerts || alerts.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <CheckCircle size={32} color="var(--accent-emerald)" style={{ margin: '0 auto 8px auto' }} />
        <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>No Active System Alerts. All operating parameters normal.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <AlertTriangle size={18} color="var(--accent-amber)" />
        Active System Warnings & Alerts
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '240px', overflowY: 'auto' }}>
        {alerts.map((alert) => (
          <div
            key={alert.id}
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              background: alert.severity === 'critical' ? 'rgba(220, 38, 38, 0.06)' : 'rgba(217, 119, 6, 0.06)',
              borderLeft: `4px solid ${alert.severity === 'critical' ? 'var(--accent-coral)' : 'var(--accent-amber)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{alert.message}</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Recommended Action: {alert.recommended_action}
              </p>
            </div>
            {!alert.acknowledged && (
              <button
                onClick={() => dispatch(acknowledgeAlert(alert.id))}
                style={{
                  background: '#f1f5f9',
                  border: '1px solid #cbd5e1',
                  color: 'var(--text-secondary)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 600
                }}
              >
                Acknowledge
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

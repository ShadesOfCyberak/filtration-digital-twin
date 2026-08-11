import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { HealthGauge } from '../charts/HealthGauge';
import { Clock, BrainCircuit } from 'lucide-react';

export const HealthMetricsPanel: React.FC = () => {
  const health = useSelector((state: RootState) => state.health.systemHealth);
  const ml = useSelector((state: RootState) => state.health.mlPrediction);

  const overall = health?.overall_health_score ?? 88.0;
  const filterH = health?.filter_health_score ?? 84.5;
  const pumpH = health?.pump_health_score ?? 92.0;

  const rul = ml?.rul_hours ?? 38.5;
  const failMode = ml?.predicted_failure_mode ?? 'Normal Operating Mode';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        <HealthGauge label="Overall System Health" score={overall} sublabel={`Status: ${health?.status || 'healthy'}`} />
        <HealthGauge label="Filter Element Health" score={filterH} sublabel={`Clogging Index: ${health?.clogging_index ?? 112.5}`} />
        <HealthGauge label="Pump Component Health" score={pumpH} sublabel="Hydraulic Efficiency Normal" />
      </div>

      <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '10px',
            background: 'rgba(124, 58, 237, 0.1)',
            border: '1px solid rgba(124, 58, 237, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-purple)'
          }}>
            <BrainCircuit size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.95rem', color: 'var(--text-primary)', fontWeight: 600 }}>ML Predictive Failure & RUL Engine</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Predicted Failure Mode: <b style={{ color: 'var(--accent-cyan)' }}>{failMode}</b>
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={20} color="var(--accent-emerald)" />
          <div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>Estimated RUL (Remaining Useful Life)</p>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>{rul.toFixed(1)} Hours</h3>
          </div>
        </div>
      </div>
    </div>
  );
};

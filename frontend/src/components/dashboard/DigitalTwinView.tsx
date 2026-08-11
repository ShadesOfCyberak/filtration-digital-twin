import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { Cpu } from 'lucide-react';

export const DigitalTwinView: React.FC = () => {
  const twin = useSelector((state: RootState) => state.sensor.twinState);

  const syncState = twin?.synchronization_state || 'SYNCHRONIZED';
  const dpAct = twin?.actual_pressure_drop ?? 0.55;
  const dpExp = twin?.expected_pressure_drop ?? 0.52;
  const dpRes = twin?.pressure_residual ?? 0.03;
  const dpDevPct = twin?.pressure_deviation_pct ?? 5.7;

  const flowAct = twin?.actual_flow_rate ?? 76.5;
  const flowExp = twin?.expected_flow_rate ?? 77.2;
  const flowRes = twin?.flow_residual ?? -0.7;

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Cpu size={24} color="var(--accent-cyan)" />
          <div>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>Physics-Based Digital Twin Mirror Engine</h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Darcy's Law Porous Media & Cake Resistance Buildup Model
            </p>
          </div>
        </div>

        <div className={`badge badge-${syncState === 'SYNCHRONIZED' ? 'synchronized' : syncState.includes('MINOR') ? 'warning' : 'critical'}`}>
          <span className="pulse-dot" />
          {syncState}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-card)' }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Pressure Drop ΔP</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', margin: '12px 0 6px 0' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Actual: <b style={{ color: 'var(--text-primary)' }}>{dpAct.toFixed(2)} bar</b></span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Expected: <b style={{ color: 'var(--accent-cyan)' }}>{dpExp.toFixed(2)} bar</b></span>
          </div>
          <div style={{ fontSize: '0.75rem', color: dpDevPct < 15 ? 'var(--accent-emerald)' : 'var(--accent-amber)', fontWeight: 600 }}>
            Residual: <b>{dpRes > 0 ? `+${dpRes.toFixed(2)}` : dpRes.toFixed(2)} bar</b> ({dpDevPct.toFixed(1)}%)
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-card)' }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Flow Rate Q</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', margin: '12px 0 6px 0' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Actual: <b style={{ color: 'var(--text-primary)' }}>{flowAct.toFixed(1)} L/min</b></span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Expected: <b style={{ color: 'var(--accent-cyan)' }}>{flowExp.toFixed(1)} L/min</b></span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
            Residual: <b>{flowRes > 0 ? `+${flowRes.toFixed(1)}` : flowRes.toFixed(1)} L/min</b>
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-card)' }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Physical State Memory</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>
            Accumulated Volume: <b style={{ color: 'var(--text-primary)' }}>{(twin?.accumulated_volume_liters ?? 142.5).toFixed(1)} L</b>
          </p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Operating Time: <b style={{ color: 'var(--text-primary)' }}>{Math.round((twin?.time_since_last_backwash_sec ?? 360) / 60)} min</b>
          </p>
        </div>
      </div>
    </div>
  );
};

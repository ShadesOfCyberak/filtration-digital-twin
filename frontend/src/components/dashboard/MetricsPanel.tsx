import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { Gauge, Wind, Zap, AlertCircle } from 'lucide-react';

export const MetricsPanel: React.FC = () => {
  const telemetry = useSelector((state: RootState) => state.sensor.telemetry);

  const dp = telemetry?.pressure_drop ?? 0.55;
  const flow = telemetry?.flow_rate ?? 76.5;
  const power = telemetry?.pump_power ?? 78.0;
  const ci = telemetry?.clogging_index ?? 112.5;

  const cards = [
    { label: 'Pressure Drop ΔP', value: `${dp.toFixed(2)} bar`, icon: Gauge, color: 'var(--accent-cyan)' },
    { label: 'Flow Rate Q', value: `${flow.toFixed(1)} L/min`, icon: Wind, color: 'var(--accent-emerald)' },
    { label: 'Pump Power P', value: `${power.toFixed(1)} W`, icon: Zap, color: 'var(--accent-amber)' },
    { label: 'Clogging Index CI', value: `${ci.toFixed(1)}`, icon: AlertCircle, color: ci > 160 ? 'var(--accent-coral)' : 'var(--accent-purple)' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              background: `rgba(0,0,0,0.03)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: card.color,
              border: `1px solid ${card.color}30`
            }}>
              <Icon size={24} />
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                {card.label}
              </p>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                {card.value}
              </h3>
            </div>
          </div>
        );
      })}
    </div>
  );
};

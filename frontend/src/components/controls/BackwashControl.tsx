import React, { useState } from 'react';
import { apiService } from '../../services/api';
import { Play, RotateCcw, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const BackwashControl: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleTriggerBackwash = async () => {
    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await apiService.triggerBackwash(30);
      if (res.success) {
        setStatusMsg('Backwash sequence triggered successfully! Relay activated for 30s.');
      } else {
        setStatusMsg('Failed to trigger backwash command.');
      }
    } catch (err: any) {
      setStatusMsg(`Error: ${err?.message || 'Failed to communicate with control API'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    setStatusMsg(null);
    try {
      await apiService.resetTwinState();
      setStatusMsg('Digital twin physical state reset to clean baseline.');
    } catch (err: any) {
      setStatusMsg('Reset failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ShieldAlert size={20} color="var(--accent-cyan)" />
        Filter Backwash & System Control Actions
      </h3>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
        Manually trigger high-pressure reverse flow pulse to clear accumulated filter cake from porous medium.
      </p>

      <div style={{ display: 'flex', gap: '16px' }}>
        <button
          onClick={handleTriggerBackwash}
          disabled={loading}
          className="btn-danger"
        >
          <Play size={18} />
          {loading ? 'Executing Backwash...' : 'Initiate Manual Backwash Cycle (30s)'}
        </button>

        <button
          onClick={handleReset}
          disabled={loading}
          className="btn-secondary"
        >
          <RotateCcw size={18} />
          Reset Digital Twin State
        </button>
      </div>

      {statusMsg && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          borderRadius: '8px',
          background: 'rgba(5, 150, 105, 0.08)',
          border: '1px solid var(--accent-emerald)',
          color: 'var(--accent-emerald)',
          fontSize: '0.85rem',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle2 size={16} />
          {statusMsg}
        </div>
      )}
    </div>
  );
};

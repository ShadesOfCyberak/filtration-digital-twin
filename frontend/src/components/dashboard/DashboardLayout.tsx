import React, { useState } from 'react';
import { Header } from '../common/Header';
import { Sidebar } from '../common/Sidebar';
import { MetricsPanel } from './MetricsPanel';
import { DigitalTwinView } from './DigitalTwinView';
import { TelemetryCharts } from '../charts/TelemetryCharts';
import { HealthMetricsPanel } from './HealthMetricsPanel';
import { AlertPanel } from './AlertPanel';
import { BackwashControl } from '../controls/BackwashControl';
import { useRealTimeData } from '../../hooks/useRealTimeData';

export const DashboardLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  // Trigger continuous real-time data polling hook
  useRealTimeData(1500);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Header />
      <div style={{ display: 'flex', flex: 1, marginTop: '74px', height: 'calc(100vh - 74px)', overflow: 'hidden' }}>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <main style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
          {activeTab === 'dashboard' && (
            <>
              <MetricsPanel />
              <DigitalTwinView />
              <div style={{ marginBottom: '24px' }}>
                <TelemetryCharts />
              </div>
              <HealthMetricsPanel />
              <AlertPanel />
              <div style={{ marginTop: '24px' }}>
                <BackwashControl />
              </div>
            </>
          )}

          {activeTab === 'twin' && (
            <>
              <DigitalTwinView />
              <TelemetryCharts />
            </>
          )}

          {activeTab === 'health' && (
            <>
              <HealthMetricsPanel />
              <AlertPanel />
            </>
          )}

          {activeTab === 'controls' && (
            <BackwashControl />
          )}
        </main>
      </div>
    </div>
  );
};

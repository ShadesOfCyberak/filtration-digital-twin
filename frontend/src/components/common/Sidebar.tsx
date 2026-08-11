import React from 'react';
import { LayoutDashboard, Cpu, ShieldAlert, Sliders } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const items = [
    { id: 'dashboard', label: 'Main Overview', icon: LayoutDashboard },
    { id: 'twin', label: 'Digital Twin Model', icon: Cpu },
    { id: 'health', label: 'Health Analytics', icon: ShieldAlert },
    { id: 'controls', label: 'Backwash Controls', icon: Sliders },
  ];

  return (
    <aside style={{
      width: '240px',
      height: '100%',
      overflowY: 'auto',
      background: 'rgba(255, 255, 255, 0.7)',
      backdropFilter: 'blur(10px)',
      borderRight: '1px solid var(--border-card)',
      padding: '24px 16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      boxSizing: 'border-box'
    }}>
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 16px',
              borderRadius: '10px',
              fontSize: '0.9rem',
              fontWeight: isActive ? 600 : 500,
              color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              background: isActive ? 'rgba(2, 132, 199, 0.08)' : 'transparent',
              border: isActive ? '1px solid rgba(2, 132, 199, 0.25)' : '1px solid transparent',
              boxShadow: isActive ? '0 2px 8px rgba(2, 132, 199, 0.08)' : 'none',
              transition: 'all 0.2s ease',
              textAlign: 'left'
            }}
          >
            <Icon size={18} />
            {item.label}
          </button>
        );
      })}
    </aside>
  );
};

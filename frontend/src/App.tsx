import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { DashboardLayout } from './components/dashboard/DashboardLayout';

export const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ErrorBoundary>
        <DashboardLayout />
      </ErrorBoundary>
    </Provider>
  );
};

export default App;

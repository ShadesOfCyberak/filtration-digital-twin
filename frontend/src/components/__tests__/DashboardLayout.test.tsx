import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../../store';
import { DashboardLayout } from '../dashboard/DashboardLayout';

describe('DashboardLayout Component', () => {
  it('renders dashboard shell without throwing error', () => {
    const { getByText } = render(
      <Provider store={store}>
        <DashboardLayout />
      </Provider>
    );
    expect(getByText(/Filtration System Digital Twin/i)).toBeDefined();
  });
});

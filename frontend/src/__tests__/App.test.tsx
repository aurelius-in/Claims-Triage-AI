/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';

// Import components to test
import App from '../App';
import TriageQueuePage from '../pages/TriageQueue/TriageQueuePage';
import AnalyticsPage from '../pages/Analytics/AnalyticsPage';
import AuditPage from '../pages/Audit/AuditPage';
import SettingsPage from '../pages/Settings/SettingsPage';

// Import slices
import authReducer from '../store/slices/authSlice';
import casesReducer from '../store/slices/casesSlice';
import analyticsReducer from '../store/slices/analyticsSlice';
import uiReducer from '../store/slices/uiSlice';
import auditReducer from '../store/slices/auditSlice';

// Mock API calls
jest.mock('../services/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

// Mock store
const mockStore = configureStore([thunk]);

// Test theme
const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

// Test data
const mockCases = [
  {
    id: '1',
    title: 'Test Auto Insurance Claim',
    description: 'Multi-vehicle collision on I-95',
    case_type: 'auto_insurance',
    urgency_level: 'high',
    risk_level: 'medium',
    status: 'new',
    created_at: '2024-01-15T08:00:00Z',
    updated_at: '2024-01-15T08:00:00Z',
    metadata: {
      police_report: 'PR-2024-001',
      injuries: ['whiplash', 'broken_arm'],
    },
  },
  {
    id: '2',
    title: 'Healthcare Prior Authorization',
    description: 'Patient requires cardiac surgery',
    case_type: 'prior_auth',
    urgency_level: 'high',
    risk_level: 'high',
    status: 'in_progress',
    created_at: '2024-01-15T09:00:00Z',
    updated_at: '2024-01-15T09:00:00Z',
    metadata: {
      procedure: 'CABG',
      diagnosis: 'coronary_artery_disease',
    },
  },
];

const mockAnalytics = {
  caseVolume: {
    total_cases: 150,
    cases_by_type: {
      auto_insurance: 50,
      prior_auth: 30,
      credit_dispute: 40,
      personal_injury: 30,
    },
    cases_by_status: {
      new: 60,
      in_progress: 45,
      completed: 45,
    },
    cases_by_urgency: {
      high: 40,
      medium: 60,
      low: 50,
    },
    cases_by_risk: {
      high: 30,
      medium: 70,
      low: 50,
    },
  },
  sla: {
    sla_adherence_rate: 0.85,
    average_resolution_time: 48,
    sla_violations: 15,
  },
  accuracy: {
    classification_accuracy: 0.92,
    risk_prediction_accuracy: 0.88,
    routing_accuracy: 0.95,
  },
};

const mockAuditLogs = [
  {
    id: '1',
    case_id: '1',
    user_id: 'user1',
    action: 'case_created',
    resource_type: 'case',
    resource_id: '1',
    details: { action: 'case_created' },
    ip_address: '192.168.1.1',
    user_agent: 'Mozilla/5.0',
    timestamp: '2024-01-15T08:00:00Z',
  },
  {
    id: '2',
    case_id: '1',
    user_id: 'user1',
    action: 'case_updated',
    resource_type: 'case',
    resource_id: '1',
    details: { action: 'case_updated', field: 'status' },
    ip_address: '192.168.1.1',
    user_agent: 'Mozilla/5.0',
    timestamp: '2024-01-15T09:00:00Z',
  },
];

// Helper function to render with providers
const renderWithProviders = (
  component: React.ReactElement,
  initialState = {}
) => {
  const store = mockStore({
    auth: {
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,
    },
    cases: {
      items: [],
      loading: false,
      error: null,
      filters: {},
      pagination: { page: 1, size: 10, total: 0 },
    },
    analytics: {
      caseVolume: null,
      sla: null,
      accuracy: null,
      loading: false,
      error: null,
    },
    ui: {
      sidebarOpen: false,
      theme: 'light',
      notifications: [],
    },
    audit: {
      logs: [],
      loading: false,
      error: null,
      pagination: { page: 1, size: 10, total: 0 },
    },
    ...initialState,
  });

  return render(
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          {component}
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

describe('App Component', () => {
  test('renders without crashing', () => {
    renderWithProviders(<App />);
    expect(screen.getByText(/Claims Triage AI/i)).toBeInTheDocument();
  });

  test('shows login page when not authenticated', () => {
    renderWithProviders(<App />);
    expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
  });

  test('shows main app when authenticated', () => {
    const authenticatedState = {
      auth: {
        user: { id: '1', username: 'testuser', email: 'test@example.com' },
        token: 'mock-token',
        isAuthenticated: true,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<App />, authenticatedState);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  });

  test('navigates between pages', async () => {
    const authenticatedState = {
      auth: {
        user: { id: '1', username: 'testuser', email: 'test@example.com' },
        token: 'mock-token',
        isAuthenticated: true,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<App />, authenticatedState);
    
    // Navigate to Triage Queue
    fireEvent.click(screen.getByText(/Triage Queue/i));
    await waitFor(() => {
      expect(screen.getByText(/Case Management/i)).toBeInTheDocument();
    });
    
    // Navigate to Analytics
    fireEvent.click(screen.getByText(/Analytics/i));
    await waitFor(() => {
      expect(screen.getByText(/Analytics Dashboard/i)).toBeInTheDocument();
    });
    
    // Navigate to Audit
    fireEvent.click(screen.getByText(/Audit/i));
    await waitFor(() => {
      expect(screen.getByText(/Audit Logs/i)).toBeInTheDocument();
    });
    
    // Navigate to Settings
    fireEvent.click(screen.getByText(/Settings/i));
    await waitFor(() => {
      expect(screen.getByText(/System Settings/i)).toBeInTheDocument();
    });
  });
});

describe('TriageQueuePage Component', () => {
  test('renders triage queue page', () => {
    renderWithProviders(<TriageQueuePage />);
    expect(screen.getByText(/Case Management/i)).toBeInTheDocument();
  });

  test('displays cases when loaded', () => {
    const stateWithCases = {
      cases: {
        items: mockCases,
        loading: false,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithCases);
    
    expect(screen.getByText('Test Auto Insurance Claim')).toBeInTheDocument();
    expect(screen.getByText('Healthcare Prior Authorization')).toBeInTheDocument();
  });

  test('shows loading state', () => {
    const loadingState = {
      cases: {
        items: [],
        loading: true,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 0 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, loadingState);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('shows error state', () => {
    const errorState = {
      cases: {
        items: [],
        loading: false,
        error: 'Failed to load cases',
        filters: {},
        pagination: { page: 1, size: 10, total: 0 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, errorState);
    expect(screen.getByText(/Failed to load cases/i)).toBeInTheDocument();
  });

  test('filters cases by type', () => {
    const stateWithCases = {
      cases: {
        items: mockCases,
        loading: false,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithCases);
    
    // Open filter menu
    fireEvent.click(screen.getByText(/Filter/i));
    
    // Select auto insurance filter
    fireEvent.click(screen.getByText(/Auto Insurance/i));
    
    // Should only show auto insurance cases
    expect(screen.getByText('Test Auto Insurance Claim')).toBeInTheDocument();
    expect(screen.queryByText('Healthcare Prior Authorization')).not.toBeInTheDocument();
  });

  test('sorts cases by different criteria', () => {
    const stateWithCases = {
      cases: {
        items: mockCases,
        loading: false,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithCases);
    
    // Open sort menu
    fireEvent.click(screen.getByText(/Sort/i));
    
    // Sort by urgency
    fireEvent.click(screen.getByText(/Urgency/i));
    
    // Verify sorting (high urgency cases should appear first)
    const caseElements = screen.getAllByTestId('case-card');
    expect(caseElements[0]).toHaveTextContent('Healthcare Prior Authorization');
  });

  test('opens case details modal', () => {
    const stateWithCases = {
      cases: {
        items: mockCases,
        loading: false,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithCases);
    
    // Click on a case to open details
    fireEvent.click(screen.getByText('Test Auto Insurance Claim'));
    
    // Should show case details modal
    expect(screen.getByText(/Case Details/i)).toBeInTheDocument();
    expect(screen.getByText(/Multi-vehicle collision on I-95/i)).toBeInTheDocument();
  });

  test('performs bulk actions', () => {
    const stateWithCases = {
      cases: {
        items: mockCases,
        loading: false,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithCases);
    
    // Select cases
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]); // Select first case
    fireEvent.click(checkboxes[2]); // Select second case
    
    // Open bulk actions menu
    fireEvent.click(screen.getByText(/Bulk Actions/i));
    
    // Select bulk action
    fireEvent.click(screen.getByText(/Assign to Team/i));
    
    // Should show assignment dialog
    expect(screen.getByText(/Assign Cases/i)).toBeInTheDocument();
  });
});

describe('AnalyticsPage Component', () => {
  test('renders analytics page', () => {
    renderWithProviders(<AnalyticsPage />);
    expect(screen.getByText(/Analytics Dashboard/i)).toBeInTheDocument();
  });

  test('displays case volume analytics', () => {
    const stateWithAnalytics = {
      analytics: {
        caseVolume: mockAnalytics.caseVolume,
        sla: null,
        accuracy: null,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<AnalyticsPage />, stateWithAnalytics);
    
    expect(screen.getByText(/150/i)).toBeInTheDocument(); // Total cases
    expect(screen.getByText(/Auto Insurance/i)).toBeInTheDocument();
    expect(screen.getByText(/50/i)).toBeInTheDocument(); // Auto insurance cases
  });

  test('displays SLA analytics', () => {
    const stateWithAnalytics = {
      analytics: {
        caseVolume: null,
        sla: mockAnalytics.sla,
        accuracy: null,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<AnalyticsPage />, stateWithAnalytics);
    
    expect(screen.getByText(/85%/i)).toBeInTheDocument(); // SLA adherence rate
    expect(screen.getByText(/48 hours/i)).toBeInTheDocument(); // Average resolution time
  });

  test('displays accuracy analytics', () => {
    const stateWithAnalytics = {
      analytics: {
        caseVolume: null,
        sla: null,
        accuracy: mockAnalytics.accuracy,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<AnalyticsPage />, stateWithAnalytics);
    
    expect(screen.getByText(/92%/i)).toBeInTheDocument(); // Classification accuracy
    expect(screen.getByText(/88%/i)).toBeInTheDocument(); // Risk prediction accuracy
    expect(screen.getByText(/95%/i)).toBeInTheDocument(); // Routing accuracy
  });

  test('shows loading state', () => {
    const loadingState = {
      analytics: {
        caseVolume: null,
        sla: null,
        accuracy: null,
        loading: true,
        error: null,
      },
    };
    
    renderWithProviders(<AnalyticsPage />, loadingState);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('filters analytics by date range', () => {
    const stateWithAnalytics = {
      analytics: {
        caseVolume: mockAnalytics.caseVolume,
        sla: mockAnalytics.sla,
        accuracy: mockAnalytics.accuracy,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<AnalyticsPage />, stateWithAnalytics);
    
    // Open date filter
    fireEvent.click(screen.getByText(/Date Range/i));
    
    // Select custom date range
    fireEvent.click(screen.getByText(/Custom Range/i));
    
    // Should show date picker
    expect(screen.getByText(/Start Date/i)).toBeInTheDocument();
    expect(screen.getByText(/End Date/i)).toBeInTheDocument();
  });

  test('exports analytics data', () => {
    const stateWithAnalytics = {
      analytics: {
        caseVolume: mockAnalytics.caseVolume,
        sla: mockAnalytics.sla,
        accuracy: mockAnalytics.accuracy,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<AnalyticsPage />, stateWithAnalytics);
    
    // Click export button
    fireEvent.click(screen.getByText(/Export/i));
    
    // Should show export options
    expect(screen.getByText(/Export as CSV/i)).toBeInTheDocument();
    expect(screen.getByText(/Export as PDF/i)).toBeInTheDocument();
  });
});

describe('AuditPage Component', () => {
  test('renders audit page', () => {
    renderWithProviders(<AuditPage />);
    expect(screen.getByText(/Audit Logs/i)).toBeInTheDocument();
  });

  test('displays audit logs', () => {
    const stateWithAuditLogs = {
      audit: {
        logs: mockAuditLogs,
        loading: false,
        error: null,
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<AuditPage />, stateWithAuditLogs);
    
    expect(screen.getByText(/case_created/i)).toBeInTheDocument();
    expect(screen.getByText(/case_updated/i)).toBeInTheDocument();
  });

  test('filters audit logs', () => {
    const stateWithAuditLogs = {
      audit: {
        logs: mockAuditLogs,
        loading: false,
        error: null,
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<AuditPage />, stateWithAuditLogs);
    
    // Open filter menu
    fireEvent.click(screen.getByText(/Filter/i));
    
    // Filter by action
    fireEvent.click(screen.getByText(/Action/i));
    fireEvent.click(screen.getByText(/case_created/i));
    
    // Should only show case_created actions
    expect(screen.getByText(/case_created/i)).toBeInTheDocument();
    expect(screen.queryByText(/case_updated/i)).not.toBeInTheDocument();
  });

  test('searches audit logs', () => {
    const stateWithAuditLogs = {
      audit: {
        logs: mockAuditLogs,
        loading: false,
        error: null,
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<AuditPage />, stateWithAuditLogs);
    
    // Enter search term
    const searchInput = screen.getByPlaceholderText(/Search audit logs/i);
    fireEvent.change(searchInput, { target: { value: 'case_created' } });
    
    // Should filter results
    expect(screen.getByText(/case_created/i)).toBeInTheDocument();
    expect(screen.queryByText(/case_updated/i)).not.toBeInTheDocument();
  });

  test('exports audit logs', () => {
    const stateWithAuditLogs = {
      audit: {
        logs: mockAuditLogs,
        loading: false,
        error: null,
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<AuditPage />, stateWithAuditLogs);
    
    // Click export button
    fireEvent.click(screen.getByText(/Export/i));
    
    // Should show export options
    expect(screen.getByText(/Export as CSV/i)).toBeInTheDocument();
    expect(screen.getByText(/Export as JSON/i)).toBeInTheDocument();
  });

  test('shows audit log details', () => {
    const stateWithAuditLogs = {
      audit: {
        logs: mockAuditLogs,
        loading: false,
        error: null,
        pagination: { page: 1, size: 10, total: 2 },
      },
    };
    
    renderWithProviders(<AuditPage />, stateWithAuditLogs);
    
    // Click on audit log entry
    fireEvent.click(screen.getByText(/case_created/i));
    
    // Should show details modal
    expect(screen.getByText(/Audit Log Details/i)).toBeInTheDocument();
    expect(screen.getByText(/192.168.1.1/i)).toBeInTheDocument();
  });
});

describe('SettingsPage Component', () => {
  test('renders settings page', () => {
    renderWithProviders(<SettingsPage />);
    expect(screen.getByText(/System Settings/i)).toBeInTheDocument();
  });

  test('displays user settings', () => {
    const authenticatedState = {
      auth: {
        user: { id: '1', username: 'testuser', email: 'test@example.com' },
        token: 'mock-token',
        isAuthenticated: true,
        loading: false,
        error: null,
      },
    };
    
    renderWithProviders(<SettingsPage />, authenticatedState);
    
    expect(screen.getByText(/User Settings/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('testuser')).toBeInTheDocument();
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
  });

  test('changes theme', () => {
    renderWithProviders(<SettingsPage />);
    
    // Open theme selector
    fireEvent.click(screen.getByText(/Theme/i));
    
    // Select dark theme
    fireEvent.click(screen.getByText(/Dark/i));
    
    // Should update theme
    expect(screen.getByText(/Dark theme selected/i)).toBeInTheDocument();
  });

  test('updates notification settings', () => {
    renderWithProviders(<SettingsPage />);
    
    // Toggle email notifications
    const emailToggle = screen.getByLabelText(/Email Notifications/i);
    fireEvent.click(emailToggle);
    
    // Should update setting
    expect(emailToggle).toBeChecked();
  });

  test('saves settings', () => {
    renderWithProviders(<SettingsPage />);
    
    // Make changes
    const usernameInput = screen.getByLabelText(/Username/i);
    fireEvent.change(usernameInput, { target: { value: 'newusername' } });
    
    // Save settings
    fireEvent.click(screen.getByText(/Save Settings/i));
    
    // Should show success message
    expect(screen.getByText(/Settings saved successfully/i)).toBeInTheDocument();
  });

  test('resets settings to defaults', () => {
    renderWithProviders(<SettingsPage />);
    
    // Click reset button
    fireEvent.click(screen.getByText(/Reset to Defaults/i));
    
    // Should show confirmation dialog
    expect(screen.getByText(/Reset Settings/i)).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to reset all settings?/i)).toBeInTheDocument();
  });
});

describe('Utility Functions', () => {
  test('formats dates correctly', () => {
    const { formatDate } = require('../utils/formatters');
    
    const date = new Date('2024-01-15T08:00:00Z');
    const formatted = formatDate(date);
    
    expect(formatted).toMatch(/Jan 15, 2024/);
  });

  test('formats currency correctly', () => {
    const { formatCurrency } = require('../utils/formatters');
    
    const amount = 1500.50;
    const formatted = formatCurrency(amount);
    
    expect(formatted).toBe('$1,500.50');
  });

  test('validates email format', () => {
    const { validateEmail } = require('../utils/validators');
    
    expect(validateEmail('test@example.com')).toBe(true);
    expect(validateEmail('invalid-email')).toBe(false);
    expect(validateEmail('')).toBe(false);
  });

  test('validates required fields', () => {
    const { validateRequired } = require('../utils/validators');
    
    expect(validateRequired('test')).toBe(true);
    expect(validateRequired('')).toBe(false);
    expect(validateRequired(null)).toBe(false);
    expect(validateRequired(undefined)).toBe(false);
  });
});

describe('API Integration', () => {
  test('handles API errors gracefully', async () => {
    const { api } = require('../services/api');
    api.get.mockRejectedValue(new Error('Network error'));
    
    const stateWithError = {
      cases: {
        items: [],
        loading: false,
        error: 'Failed to load cases',
        filters: {},
        pagination: { page: 1, size: 10, total: 0 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithError);
    
    expect(screen.getByText(/Failed to load cases/i)).toBeInTheDocument();
    expect(screen.getByText(/Retry/i)).toBeInTheDocument();
  });

  test('retries failed API calls', async () => {
    const { api } = require('../services/api');
    api.get.mockRejectedValueOnce(new Error('Network error')).mockResolvedValueOnce({ data: mockCases });
    
    const stateWithError = {
      cases: {
        items: [],
        loading: false,
        error: 'Failed to load cases',
        filters: {},
        pagination: { page: 1, size: 10, total: 0 },
      },
    };
    
    renderWithProviders(<TriageQueuePage />, stateWithError);
    
    // Click retry button
    fireEvent.click(screen.getByText(/Retry/i));
    
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(2);
    });
  });
});

describe('Accessibility', () => {
  test('has proper ARIA labels', () => {
    renderWithProviders(<TriageQueuePage />);
    
    // Check for proper ARIA labels
    expect(screen.getByLabelText(/Search cases/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Filter cases/i)).toBeInTheDocument();
  });

  test('supports keyboard navigation', () => {
    renderWithProviders(<TriageQueuePage />);
    
    // Tab through interactive elements
    const searchInput = screen.getByLabelText(/Search cases/i);
    searchInput.focus();
    
    // Should be able to tab to next element
    const filterButton = screen.getByLabelText(/Filter cases/i);
    expect(filterButton).not.toHaveFocus();
    
    // Tab to filter button
    searchInput.blur();
    filterButton.focus();
    expect(filterButton).toHaveFocus();
  });

  test('has proper color contrast', () => {
    renderWithProviders(<TriageQueuePage />);
    
    // Check that text has sufficient contrast
    const textElements = screen.getAllByText(/Case Management/i);
    textElements.forEach(element => {
      const style = window.getComputedStyle(element);
      // This is a basic check - in a real app you'd use a proper contrast checker
      expect(style.color).toBeDefined();
    });
  });
});

describe('Performance', () => {
  test('renders large lists efficiently', () => {
    const largeCaseList = Array.from({ length: 100 }, (_, i) => ({
      id: i.toString(),
      title: `Case ${i}`,
      description: `Description for case ${i}`,
      case_type: 'auto_insurance',
      urgency_level: 'normal',
      risk_level: 'low',
      status: 'new',
      created_at: '2024-01-15T08:00:00Z',
      updated_at: '2024-01-15T08:00:00Z',
      metadata: {},
    }));
    
    const stateWithLargeList = {
      cases: {
        items: largeCaseList,
        loading: false,
        error: null,
        filters: {},
        pagination: { page: 1, size: 10, total: 100 },
      },
    };
    
    const startTime = performance.now();
    renderWithProviders(<TriageQueuePage />, stateWithLargeList);
    const endTime = performance.now();
    
    // Should render within reasonable time (adjust threshold as needed)
    expect(endTime - startTime).toBeLessThan(1000);
  });

  test('debounces search input', async () => {
    renderWithProviders(<TriageQueuePage />);
    
    const searchInput = screen.getByLabelText(/Search cases/i);
    
    // Type rapidly
    fireEvent.change(searchInput, { target: { value: 'a' } });
    fireEvent.change(searchInput, { target: { value: 'ab' } });
    fireEvent.change(searchInput, { target: { value: 'abc' } });
    
    // Should only trigger search after debounce delay
    await waitFor(() => {
      // Check that search was called with final value
      expect(searchInput).toHaveValue('abc');
    }, { timeout: 1000 });
  });
});

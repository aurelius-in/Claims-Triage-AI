import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Analytics {
  total_cases: number;
  pending_cases: number;
  completed_today: number;
  avg_processing_time: string;
  sla_compliance: string;
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}

interface AnalyticsState {
  analytics: Analytics | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  analytics: null,
  loading: false,
  error: null,
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    fetchAnalyticsStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchAnalyticsSuccess: (state, action: PayloadAction<Analytics>) => {
      state.loading = false;
      state.analytics = action.payload;
    },
    fetchAnalyticsFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { fetchAnalyticsStart, fetchAnalyticsSuccess, fetchAnalyticsFailure } = analyticsSlice.actions;
export default analyticsSlice.reducer;

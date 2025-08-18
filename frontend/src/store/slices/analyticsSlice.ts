import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { analyticsAPI } from '@/services/api';
import { AnalyticsSnapshot, TimeSeriesData, RiskDistribution, TeamPerformance } from '@/types';

interface AnalyticsState {
  analytics: AnalyticsSnapshot | null;
  overview: {
    totalCases: number;
    pendingCases: number;
    avgProcessingTime: number;
    escalationRate: number;
    slaComplianceRate: number;
  } | null;
  caseVolume: TimeSeriesData[];
  riskDistribution: RiskDistribution[];
  teamPerformance: TeamPerformance[];
  slaCompliance: TimeSeriesData[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: AnalyticsState = {
  analytics: null,
  overview: null,
  caseVolume: [],
  riskDistribution: [],
  teamPerformance: [],
  slaCompliance: [],
  loading: false,
  error: null,
  lastUpdated: null,
};

export const fetchOverview = createAsyncThunk(
  'analytics/fetchOverview',
  async () => {
    const response = await analyticsAPI.getOverview();
    return response;
  }
);

export const fetchCaseVolume = createAsyncThunk(
  'analytics/fetchCaseVolume',
  async (period: 'day' | 'week' | 'month' = 'week') => {
    const response = await analyticsAPI.getCaseVolume(period);
    return response;
  }
);

export const fetchRiskDistribution = createAsyncThunk(
  'analytics/fetchRiskDistribution',
  async () => {
    const response = await analyticsAPI.getRiskDistribution();
    return response;
  }
);

export const fetchTeamPerformance = createAsyncThunk(
  'analytics/fetchTeamPerformance',
  async () => {
    const response = await analyticsAPI.getTeamPerformance();
    return response;
  }
);

export const fetchSLACompliance = createAsyncThunk(
  'analytics/fetchSLACompliance',
  async (period: 'day' | 'week' | 'month' = 'week') => {
    const response = await analyticsAPI.getSLACompliance(period);
    return response;
  }
);

export const fetchAllAnalytics = createAsyncThunk(
  'analytics/fetchAllAnalytics',
  async (params: { timeRange: string; teamId?: string }) => {
    const response = await analyticsAPI.getAllAnalytics(params);
    return response;
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setLastUpdated: (state, action: PayloadAction<string>) => {
      state.lastUpdated = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch overview
      .addCase(fetchOverview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOverview.fulfilled, (state, action) => {
        state.loading = false;
        state.overview = action.payload;
      })
      .addCase(fetchOverview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch overview';
      })
      // Fetch case volume
      .addCase(fetchCaseVolume.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCaseVolume.fulfilled, (state, action) => {
        state.loading = false;
        state.caseVolume = action.payload;
      })
      .addCase(fetchCaseVolume.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch case volume';
      })
      // Fetch risk distribution
      .addCase(fetchRiskDistribution.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRiskDistribution.fulfilled, (state, action) => {
        state.loading = false;
        state.riskDistribution = action.payload;
      })
      .addCase(fetchRiskDistribution.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch risk distribution';
      })
      // Fetch team performance
      .addCase(fetchTeamPerformance.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTeamPerformance.fulfilled, (state, action) => {
        state.loading = false;
        state.teamPerformance = action.payload;
      })
      .addCase(fetchTeamPerformance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch team performance';
      })
      // Fetch SLA compliance
      .addCase(fetchSLACompliance.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSLACompliance.fulfilled, (state, action) => {
        state.loading = false;
        state.slaCompliance = action.payload;
      })
      .addCase(fetchSLACompliance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch SLA compliance';
      })
      // Fetch all analytics
      .addCase(fetchAllAnalytics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAllAnalytics.fulfilled, (state, action) => {
        state.loading = false;
        state.analytics = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchAllAnalytics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch analytics';
      });
  },
});

export const {
  clearError,
  setLastUpdated,
} = analyticsSlice.actions;

export default analyticsSlice.reducer;

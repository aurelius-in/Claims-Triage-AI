import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { auditAPI } from '@/services/api';
import { AuditLog, AuditFilters, PaginationParams, PaginatedResponse } from '@/types';

interface AuditState {
  auditLogs: AuditLog[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  filters: AuditFilters;
}

const initialState: AuditState = {
  auditLogs: [],
  loading: false,
  error: null,
  totalCount: 0,
  currentPage: 1,
  pageSize: 25,
  filters: {
    action: '',
    resourceType: '',
    userId: '',
    dateFrom: '',
    dateTo: '',
    search: '',
  },
};

export const fetchAuditLogs = createAsyncThunk(
  'audit/fetchAuditLogs',
  async (params: { page: number; size: number; filters: AuditFilters }) => {
    const response = await auditAPI.getAuditLogs(params);
    return response;
  }
);

const auditSlice = createSlice({
  name: 'audit',
  initialState,
  reducers: {
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.currentPage = 1;
    },
    setFilters: (state, action: PayloadAction<Partial<AuditFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.currentPage = 1;
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
      state.currentPage = 1;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAuditLogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAuditLogs.fulfilled, (state, action) => {
        state.loading = false;
        state.auditLogs = action.payload.data;
        state.totalCount = action.payload.total;
      })
      .addCase(fetchAuditLogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch audit logs';
      });
  },
});

export const {
  setCurrentPage,
  setPageSize,
  setFilters,
  clearFilters,
  clearError,
} = auditSlice.actions;

export default auditSlice.reducer;

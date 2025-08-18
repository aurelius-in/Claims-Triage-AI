import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { casesAPI } from '@/services/api';
import { Case, CaseCreate, CaseUpdate, CaseFilters, PaginationParams, PaginatedResponse, TriageResult } from '@/types';

interface CasesState {
  cases: Case[];
  currentCase: Case | null;
  loading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  filters: CaseFilters;
  selectedCases: string[];
  triageLoading: boolean;
  triageError: string | null;
}

const initialState: CasesState = {
  cases: [],
  currentCase: null,
  loading: false,
  error: null,
  totalCount: 0,
  currentPage: 1,
  pageSize: 20,
  filters: {},
  selectedCases: [],
  triageLoading: false,
  triageError: null,
};

export const fetchCases = createAsyncThunk(
  'cases/fetchCases',
  async (params: { page: number; size: number; filters?: CaseFilters }) => {
    const response = await casesAPI.getCases(params);
    return response;
  }
);

export const fetchCase = createAsyncThunk(
  'cases/fetchCase',
  async (id: string) => {
    const response = await casesAPI.getCase(id);
    return response;
  }
);

export const createCase = createAsyncThunk(
  'cases/createCase',
  async (caseData: CaseCreate) => {
    const response = await casesAPI.createCase(caseData);
    return response;
  }
);

export const updateCase = createAsyncThunk(
  'cases/updateCase',
  async ({ id, caseData }: { id: string; caseData: CaseUpdate }) => {
    const response = await casesAPI.updateCase(id, caseData);
    return response;
  }
);

export const deleteCase = createAsyncThunk(
  'cases/deleteCase',
  async (id: string) => {
    await casesAPI.deleteCase(id);
    return id;
  }
);

export const runTriage = createAsyncThunk(
  'cases/runTriage',
  async (id: string) => {
    const response = await casesAPI.runTriage(id);
    return response;
  }
);

const casesSlice = createSlice({
  name: 'cases',
  initialState,
  reducers: {
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
      state.currentPage = 1;
    },
    setFilters: (state, action: PayloadAction<Partial<CaseFilters>>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.currentPage = 1;
    },
    clearFilters: (state) => {
      state.filters = {};
      state.currentPage = 1;
    },
    selectCase: (state, action: PayloadAction<string>) => {
      if (!state.selectedCases.includes(action.payload)) {
        state.selectedCases.push(action.payload);
      }
    },
    deselectCase: (state, action: PayloadAction<string>) => {
      state.selectedCases = state.selectedCases.filter(id => id !== action.payload);
    },
    selectAllCases: (state) => {
      state.selectedCases = state.cases.map(case_ => case_.id);
    },
    deselectAllCases: (state) => {
      state.selectedCases = [];
    },
    clearCurrentCase: (state) => {
      state.currentCase = null;
    },
    clearError: (state) => {
      state.error = null;
      state.triageError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch cases
      .addCase(fetchCases.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCases.fulfilled, (state, action) => {
        state.loading = false;
        state.cases = action.payload.items;
        state.totalCount = action.payload.total;
      })
      .addCase(fetchCases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch cases';
      })
      // Fetch single case
      .addCase(fetchCase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCase.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCase = action.payload;
      })
      .addCase(fetchCase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch case';
      })
      // Create case
      .addCase(createCase.fulfilled, (state, action) => {
        state.cases.unshift(action.payload);
        state.totalCount += 1;
      })
      // Update case
      .addCase(updateCase.fulfilled, (state, action) => {
        const index = state.cases.findIndex(case_ => case_.id === action.payload.id);
        if (index !== -1) {
          state.cases[index] = action.payload;
        }
        if (state.currentCase?.id === action.payload.id) {
          state.currentCase = action.payload;
        }
      })
      // Delete case
      .addCase(deleteCase.fulfilled, (state, action) => {
        state.cases = state.cases.filter(case_ => case_.id !== action.payload);
        state.selectedCases = state.selectedCases.filter(id => id !== action.payload);
        state.totalCount -= 1;
        if (state.currentCase?.id === action.payload) {
          state.currentCase = null;
        }
      })
      // Run triage
      .addCase(runTriage.pending, (state) => {
        state.triageLoading = true;
        state.triageError = null;
      })
      .addCase(runTriage.fulfilled, (state, action) => {
        state.triageLoading = false;
        // Update the case with triage results
        const index = state.cases.findIndex(case_ => case_.id === action.payload.case_id);
        if (index !== -1) {
          state.cases[index].triage_results = state.cases[index].triage_results || [];
          state.cases[index].triage_results.push(action.payload);
        }
        if (state.currentCase?.id === action.payload.case_id) {
          state.currentCase.triage_results = state.currentCase.triage_results || [];
          state.currentCase.triage_results.push(action.payload);
        }
      })
      .addCase(runTriage.rejected, (state, action) => {
        state.triageLoading = false;
        state.triageError = action.error.message || 'Failed to run triage';
      });
  },
});

export const {
  setCurrentPage,
  setPageSize,
  setFilters,
  clearFilters,
  selectCase,
  deselectCase,
  selectAllCases,
  deselectAllCases,
  clearCurrentCase,
  clearError,
} = casesSlice.actions;

export default casesSlice.reducer;

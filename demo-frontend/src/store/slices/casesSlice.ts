import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Case {
  id: string;
  title: string;
  description: string;
  case_type: string;
  urgency: string;
  risk_level: string;
  status: string;
  created_at: string;
  assigned_team: string;
}

interface CasesState {
  cases: Case[];
  loading: boolean;
  error: string | null;
}

const initialState: CasesState = {
  cases: [],
  loading: false,
  error: null,
};

const casesSlice = createSlice({
  name: 'cases',
  initialState,
  reducers: {
    fetchCasesStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchCasesSuccess: (state, action: PayloadAction<Case[]>) => {
      state.loading = false;
      state.cases = action.payload;
    },
    fetchCasesFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
  },
});

export const { fetchCasesStart, fetchCasesSuccess, fetchCasesFailure } = casesSlice.actions;
export default casesSlice.reducer;

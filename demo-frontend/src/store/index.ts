import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import casesReducer from './slices/casesSlice';
import analyticsReducer from './slices/analyticsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    cases: casesReducer,
    analytics: analyticsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

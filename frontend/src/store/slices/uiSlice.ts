import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Notification, ThemeConfig } from '@/types';

interface UIState {
  theme: ThemeConfig;
  sidebarOpen: boolean;
  notifications: Notification[];
  loadingStates: Record<string, boolean>;
  errorStates: Record<string, string | null>;
  drawerOpen: boolean;
  drawerContent: 'case-detail' | 'filters' | 'settings' | null;
  selectedDrawerId: string | null;
}

const initialState: UIState = {
  theme: {
    mode: 'light',
    primaryColor: '#1976d2',
    secondaryColor: '#dc004e',
  },
  sidebarOpen: true,
  notifications: [],
  loadingStates: {},
  errorStates: {},
  drawerOpen: false,
  drawerContent: null,
  selectedDrawerId: null,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<ThemeConfig>) => {
      state.theme = action.payload;
    },
    toggleTheme: (state) => {
      state.theme.mode = state.theme.mode === 'light' ? 'dark' : 'light';
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const id = Date.now().toString();
      state.notifications.push({ ...action.payload, id });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setLoading: (state, action: PayloadAction<{ key: string; loading: boolean }>) => {
      state.loadingStates[action.payload.key] = action.payload.loading;
    },
    setError: (state, action: PayloadAction<{ key: string; error: string | null }>) => {
      state.errorStates[action.payload.key] = action.payload.error;
    },
    clearErrors: (state) => {
      state.errorStates = {};
    },
    openDrawer: (state, action: PayloadAction<{ content: 'case-detail' | 'filters' | 'settings'; id?: string }>) => {
      state.drawerOpen = true;
      state.drawerContent = action.payload.content;
      state.selectedDrawerId = action.payload.id || null;
    },
    closeDrawer: (state) => {
      state.drawerOpen = false;
      state.drawerContent = null;
      state.selectedDrawerId = null;
    },
  },
});

export const {
  setTheme,
  toggleTheme,
  toggleSidebar,
  setSidebarOpen,
  addNotification,
  removeNotification,
  clearNotifications,
  setLoading,
  setError,
  clearErrors,
  openDrawer,
  closeDrawer,
} = uiSlice.actions;

export default uiSlice.reducer;

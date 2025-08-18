import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Box, Container, Typography, Paper } from '@mui/material';
import { RootState } from './store';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CasesPage from './pages/CasesPage';
import AnalyticsPage from './pages/AnalyticsPage';

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);

  // Demo login for testing
  useEffect(() => {
    if (!isAuthenticated) {
      // Auto-login for demo purposes
      dispatch({
        type: 'auth/loginSuccess',
        payload: {
          user: {
            id: 'user-001',
            username: 'admin',
            email: 'admin@demo.com',
            role: 'admin',
            name: 'Demo Administrator'
          },
          token: 'demo-token'
        }
      });
    }
  }, [dispatch, isAuthenticated]);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      <Container maxWidth="xl" sx={{ py: 2 }}>
        <Paper sx={{ p: 3, mb: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Claims Triage AI - Demo
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome, {user?.name} | Role: {user?.role}
          </Typography>
        </Paper>
        
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/cases" element={<CasesPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Routes>
      </Container>
    </Box>
  );
}

export default App;

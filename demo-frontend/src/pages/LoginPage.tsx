import React from 'react';
import { Box, Paper, Typography, Button } from '@mui/material';

const LoginPage: React.FC = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.50',
      }}
    >
      <Paper sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Claims Triage AI
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" gutterBottom>
          Demo Login
        </Typography>
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" align="center">
            Demo credentials: admin / admin123
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default LoginPage;

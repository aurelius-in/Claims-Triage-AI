import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent } from '@mui/material';
import { Assessment, Assignment, TrendingUp, Warning } from '@mui/icons-material';

const DashboardPage: React.FC = () => {
  const stats = [
    { title: 'Total Cases', value: '156', icon: <Assignment />, color: 'primary.main' },
    { title: 'Pending Cases', value: '23', icon: <Warning />, color: 'warning.main' },
    { title: 'Completed Today', value: '12', icon: <TrendingUp />, color: 'success.main' },
    { title: 'SLA Compliance', value: '94.2%', icon: <Assessment />, color: 'info.main' },
  ];

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        Dashboard Overview
      </Typography>
      
      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ color: stat.color, mr: 1 }}>
                    {stat.icon}
                  </Box>
                  <Typography variant="h6" component="div">
                    {stat.title}
                  </Typography>
                </Box>
                <Typography variant="h4" component="div" sx={{ color: stat.color }}>
                  {stat.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Cases
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Auto Insurance Claim - High Priority
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Medical Prior Authorization - Critical
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Property Damage Claim - Medium Priority
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Typography variant="body2" color="success.main">
              ✅ AI Triage Engine: Online
            </Typography>
            <Typography variant="body2" color="success.main">
              ✅ Database: Connected
            </Typography>
            <Typography variant="body2" color="success.main">
              ✅ Analytics: Active
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;

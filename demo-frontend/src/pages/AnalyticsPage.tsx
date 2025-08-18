import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent } from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AnalyticsPage: React.FC = () => {
  const riskData = [
    { name: 'Low', value: 45, color: '#4caf50' },
    { name: 'Medium', value: 67, color: '#ff9800' },
    { name: 'High', value: 32, color: '#f44336' },
    { name: 'Critical', value: 12, color: '#9c27b0' },
  ];

  const caseTypeData = [
    { name: 'Auto Insurance', value: 45 },
    { name: 'Medical Auth', value: 32 },
    { name: 'Property', value: 28 },
    { name: 'Legal', value: 15 },
  ];

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        Analytics Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Risk Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Case Types
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={caseTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Cases
                  </Typography>
                  <Typography variant="h4">
                    156
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Pending Cases
                  </Typography>
                  <Typography variant="h4">
                    23
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Processing Time
                  </Typography>
                  <Typography variant="h4">
                    2.3h
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    SLA Compliance
                  </Typography>
                  <Typography variant="h4">
                    94.2%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsPage;

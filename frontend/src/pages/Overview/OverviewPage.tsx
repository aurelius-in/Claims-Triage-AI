import React, { useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Assignment,
  Warning,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchAllAnalytics } from '@/store/slices/analyticsSlice';
import { fetchCases } from '@/store/slices/casesSlice';
import LoadingSpinner from '@/components/Common/LoadingSpinner';

const OverviewPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { overview, isLoading, error } = useAppSelector((state) => state.analytics);
  const { cases, totalCases } = useAppSelector((state) => state.cases);

  useEffect(() => {
    dispatch(fetchAllAnalytics('week'));
    dispatch(fetchCases({ page: 1, size: 20 }));
  }, [dispatch]);

  if (isLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const pendingCases = cases.filter(case_ => case_.status === 'pending').length;
  const escalatedCases = cases.filter(case_ => case_.status === 'escalated').length;
  const resolvedCases = cases.filter(case_ => case_.status === 'resolved').length;

  const metrics = [
    {
      title: 'Total Cases',
      value: totalCases,
      icon: <Assignment color="primary" />,
      color: 'primary',
    },
    {
      title: 'Pending Cases',
      value: pendingCases,
      icon: <Schedule color="warning" />,
      color: 'warning',
    },
    {
      title: 'Escalated Cases',
      value: escalatedCases,
      icon: <Warning color="error" />,
      color: 'error',
    },
    {
      title: 'Resolved Cases',
      value: resolvedCases,
      icon: <CheckCircle color="success" />,
      color: 'success',
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          Dashboard Overview
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor your case triage performance and system health
        </Typography>
      </Box>

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {metrics.map((metric) => (
          <Grid item xs={12} sm={6} md={3} key={metric.title}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {metric.icon}
                  <Typography variant="h6" sx={{ ml: 1, fontWeight: 'bold' }}>
                    {metric.value}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {metric.title}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Performance Metrics */}
      {overview && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  Performance Metrics
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Avg Processing Time</Typography>
                    <Chip 
                      label={`${overview.avg_processing_time.toFixed(1)}h`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">SLA Compliance</Typography>
                    <Chip 
                      label={`${(overview.sla_compliance_rate * 100).toFixed(1)}%`}
                      color={overview.sla_compliance_rate > 0.9 ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Escalation Rate</Typography>
                    <Chip 
                      label={`${(overview.escalation_rate * 100).toFixed(1)}%`}
                      color={overview.escalation_rate < 0.1 ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<Assignment />}
                    fullWidth
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    View Triage Queue
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<TrendingUp />}
                    fullWidth
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    View Analytics
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Warning />}
                    fullWidth
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    Review Escalations
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Recent Activity */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
            Recent Cases
          </Typography>
          {cases.length > 0 ? (
            <Box>
              {cases.slice(0, 5).map((case_) => (
                <Box
                  key={case_.id}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 1,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    '&:last-child': { borderBottom: 'none' },
                  }}
                >
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {case_.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {case_.external_id} • {case_.case_type.replace('_', ' ')}
                    </Typography>
                  </Box>
                  <Chip
                    label={case_.status}
                    size="small"
                    color={
                      case_.status === 'pending' ? 'warning' :
                      case_.status === 'escalated' ? 'error' :
                      case_.status === 'resolved' ? 'success' : 'default'
                    }
                  />
                </Box>
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No cases found
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default OverviewPage;

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Download,
  Refresh,
  CalendarToday,
  Assessment,
  Speed,
  Warning,
  CheckCircle,
  Schedule,
  Business,
  LocalHospital,
  TrendingUp as FinanceIcon,
  Gavel,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart,
} from 'recharts';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchAllAnalytics } from '@/store/slices/analyticsSlice';
import { addNotification } from '@/store/slices/uiSlice';
import LoadingSpinner from '@/components/Common/LoadingSpinner';
import { AnalyticsSnapshot, CaseType, RiskLevel } from '@/types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AnalyticsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { analytics, loading, error } = useAppSelector((state) => state.analytics);
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedTeam, setSelectedTeam] = useState('all');

  useEffect(() => {
    dispatch(fetchAllAnalytics({ timeRange, teamId: selectedTeam }));
  }, [dispatch, timeRange, selectedTeam]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    dispatch(fetchAllAnalytics({ timeRange, teamId: selectedTeam }));
    dispatch(addNotification({
      id: Date.now().toString(),
      message: 'Analytics refreshed',
      type: 'success',
    }));
  };

  const handleExport = (format: 'csv' | 'json' | 'pdf') => {
    // Implement export functionality
    dispatch(addNotification({
      id: Date.now().toString(),
      message: `Analytics exported as ${format.toUpperCase()}`,
      type: 'success',
    }));
  };

  if (loading) return <LoadingSpinner message="Loading analytics..." />;

  // Mock data for charts (replace with real data from analytics state)
  const caseVolumeData = [
    { date: '2024-01-01', insurance: 45, healthcare: 32, finance: 28, legal: 15 },
    { date: '2024-01-02', insurance: 52, healthcare: 38, finance: 31, legal: 18 },
    { date: '2024-01-03', insurance: 48, healthcare: 35, finance: 29, legal: 16 },
    { date: '2024-01-04', insurance: 55, healthcare: 42, finance: 33, legal: 20 },
    { date: '2024-01-05', insurance: 51, healthcare: 39, finance: 30, legal: 17 },
    { date: '2024-01-06', insurance: 47, healthcare: 36, finance: 27, legal: 14 },
    { date: '2024-01-07', insurance: 53, healthcare: 40, finance: 32, legal: 19 },
  ];

  const riskDistributionData = [
    { name: 'Low Risk', value: 45, color: '#4CAF50' },
    { name: 'Medium Risk', value: 30, color: '#FF9800' },
    { name: 'High Risk', value: 20, color: '#F44336' },
    { name: 'Critical Risk', value: 5, color: '#9C27B0' },
  ];

  const teamPerformanceData = [
    { team: 'Team Alpha', cases: 120, avgTime: 2.5, slaCompliance: 95, escalations: 3 },
    { team: 'Team Beta', cases: 98, avgTime: 3.2, slaCompliance: 88, escalations: 7 },
    { team: 'Team Gamma', cases: 85, avgTime: 2.8, slaCompliance: 92, escalations: 4 },
    { team: 'Team Delta', cases: 110, avgTime: 3.5, slaCompliance: 85, escalations: 9 },
  ];

  const slaComplianceData = [
    { month: 'Jan', target: 95, actual: 92, insurance: 94, healthcare: 89, finance: 96, legal: 91 },
    { month: 'Feb', target: 95, actual: 94, insurance: 96, healthcare: 91, finance: 97, legal: 93 },
    { month: 'Mar', target: 95, actual: 93, insurance: 95, healthcare: 90, finance: 96, legal: 92 },
    { month: 'Apr', target: 95, actual: 95, insurance: 97, healthcare: 93, finance: 98, legal: 94 },
    { month: 'May', target: 95, actual: 94, insurance: 96, healthcare: 92, finance: 97, legal: 93 },
    { month: 'Jun', target: 95, actual: 96, insurance: 98, healthcare: 94, finance: 99, legal: 95 },
  ];

  const processingTimeData = [
    { team: 'Team Alpha', avgTime: 2.5, minTime: 1.2, maxTime: 4.8 },
    { team: 'Team Beta', avgTime: 3.2, minTime: 1.8, maxTime: 5.5 },
    { team: 'Team Gamma', avgTime: 2.8, minTime: 1.5, maxTime: 4.2 },
    { team: 'Team Delta', avgTime: 3.5, minTime: 2.1, maxTime: 6.1 },
  ];

  const escalationTrendData = [
    { week: 'Week 1', escalations: 12, highRisk: 8, criticalRisk: 4 },
    { week: 'Week 2', escalations: 15, highRisk: 10, criticalRisk: 5 },
    { week: 'Week 3', escalations: 11, highRisk: 7, criticalRisk: 4 },
    { week: 'Week 4', escalations: 18, highRisk: 12, criticalRisk: 6 },
    { week: 'Week 5', escalations: 14, highRisk: 9, criticalRisk: 5 },
    { week: 'Week 6', escalations: 16, highRisk: 11, criticalRisk: 5 },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Analytics Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
              <MenuItem value="1y">Last Year</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Team</InputLabel>
            <Select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              label="Team"
            >
              <MenuItem value="all">All Teams</MenuItem>
              <MenuItem value="alpha">Team Alpha</MenuItem>
              <MenuItem value="beta">Team Beta</MenuItem>
              <MenuItem value="gamma">Team Gamma</MenuItem>
              <MenuItem value="delta">Team Delta</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => handleExport('csv')}
          >
            Export
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Cases
                  </Typography>
                  <Typography variant="h4" component="div">
                    {analytics?.overview?.totalCases || 1,247}
                  </Typography>
                  <Typography variant="body2" color="success.main" sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUp sx={{ fontSize: 16, mr: 0.5 }} />
                    +12.5%
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Avg Processing Time
                  </Typography>
                  <Typography variant="h4" component="div">
                    {analytics?.overview?.avgProcessingTime || 2.8}h
                  </Typography>
                  <Typography variant="body2" color="success.main" sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingDown sx={{ fontSize: 16, mr: 0.5 }} />
                    -8.2%
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    SLA Compliance
                  </Typography>
                  <Typography variant="h4" component="div">
                    {analytics?.overview?.slaCompliance || 94.2}%
                  </Typography>
                  <Typography variant="body2" color="success.main" sx={{ display: 'flex', alignItems: 'center' }}>
                    <CheckCircle sx={{ fontSize: 16, mr: 0.5 }} />
                    +2.1%
                  </Typography>
                </Box>
                <Schedule sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Escalation Rate
                  </Typography>
                  <Typography variant="h4" component="div">
                    {analytics?.overview?.escalationRate || 3.8}%
                  </Typography>
                  <Typography variant="body2" color="error.main" sx={{ display: 'flex', alignItems: 'center' }}>
                    <Warning sx={{ fontSize: 16, mr: 0.5 }} />
                    +0.5%
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Analytics Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="analytics tabs">
          <Tab label="Case Volume" />
          <Tab label="Risk Analysis" />
          <Tab label="Team Performance" />
          <Tab label="SLA Compliance" />
          <Tab label="Processing Time" />
          <Tab label="Escalations" />
        </Tabs>
      </Box>

      {/* Case Volume Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Case Volume Trends by Type
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={caseVolumeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="insurance" stroke="#8884d8" name="Insurance" />
                  <Line type="monotone" dataKey="healthcare" stroke="#82ca9d" name="Healthcare" />
                  <Line type="monotone" dataKey="finance" stroke="#ffc658" name="Finance" />
                  <Line type="monotone" dataKey="legal" stroke="#ff7300" name="Legal" />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Risk Analysis Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Risk Trends Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={escalationTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Area type="monotone" dataKey="highRisk" stackId="1" stroke="#ff7300" fill="#ff7300" name="High Risk" />
                  <Area type="monotone" dataKey="criticalRisk" stackId="1" stroke="#9c27b0" fill="#9c27b0" name="Critical Risk" />
                </AreaChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Team Performance Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Team Performance Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <ComposedChart data={teamPerformanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="team" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <RechartsTooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="cases" fill="#8884d8" name="Cases Handled" />
                  <Line yAxisId="right" type="monotone" dataKey="slaCompliance" stroke="#82ca9d" name="SLA %" />
                </ComposedChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Team Performance Table
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Team</TableCell>
                      <TableCell align="right">Cases Handled</TableCell>
                      <TableCell align="right">Avg Time (hours)</TableCell>
                      <TableCell align="right">SLA Compliance (%)</TableCell>
                      <TableCell align="right">Escalations</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {teamPerformanceData.map((row) => (
                      <TableRow key={row.team}>
                        <TableCell component="th" scope="row">
                          {row.team}
                        </TableCell>
                        <TableCell align="right">{row.cases}</TableCell>
                        <TableCell align="right">{row.avgTime}</TableCell>
                        <TableCell align="right">{row.slaCompliance}%</TableCell>
                        <TableCell align="right">{row.escalations}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* SLA Compliance Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                SLA Compliance Trends
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={slaComplianceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="target" stroke="#666" strokeDasharray="5 5" name="Target" />
                  <Line type="monotone" dataKey="actual" stroke="#82ca9d" name="Overall" />
                  <Line type="monotone" dataKey="insurance" stroke="#8884d8" name="Insurance" />
                  <Line type="monotone" dataKey="healthcare" stroke="#ffc658" name="Healthcare" />
                  <Line type="monotone" dataKey="finance" stroke="#ff7300" name="Finance" />
                  <Line type="monotone" dataKey="legal" stroke="#9c27b0" name="Legal" />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Processing Time Tab */}
      <TabPanel value={tabValue} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Processing Time Analysis
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={processingTimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="team" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="avgTime" fill="#8884d8" name="Average Time" />
                  <Bar dataKey="minTime" fill="#82ca9d" name="Minimum Time" />
                  <Bar dataKey="maxTime" fill="#ffc658" name="Maximum Time" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Escalations Tab */}
      <TabPanel value={tabValue} index={5}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Escalation Trends
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={escalationTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Area type="monotone" dataKey="escalations" stroke="#ff7300" fill="#ff7300" name="Total Escalations" />
                  <Area type="monotone" dataKey="highRisk" stroke="#ffc658" fill="#ffc658" name="High Risk" />
                  <Area type="monotone" dataKey="criticalRisk" stroke="#9c27b0" fill="#9c27b0" name="Critical Risk" />
                </AreaChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default AnalyticsPage;

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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Badge,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Switch,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  FilterList,
  Sort,
  PlayArrow,
  Visibility,
  Edit,
  Delete,
  Refresh,
  Download,
  Upload,
  Assignment,
  Warning,
  CheckCircle,
  Schedule,
  ExpandMore,
  Info,
  TrendingUp,
  TrendingDown,
  Security,
  Business,
  LocalHospital,
  Gavel,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchCases, runTriage, selectCase, deselectCase, selectAllCases, deselectAllCases } from '@/store/slices/casesSlice';
import { addNotification } from '@/store/slices/uiSlice';
import LoadingSpinner from '@/components/Common/LoadingSpinner';
import { Case, CaseStatus, CaseType, RiskLevel, UserRole } from '@/types';

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
      id={`triage-tabpanel-${index}`}
      aria-labelledby={`triage-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const TriageQueuePage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { cases, loading, error, selectedCases, currentPage, pageSize, filters } = useAppSelector(
    (state) => state.cases
  );
  const { user } = useAppSelector((state) => state.auth);

  // Local state
  const [tabValue, setTabValue] = useState(0);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [triageDialogOpen, setTriageDialogOpen] = useState(false);
  const [bulkActionDialogOpen, setBulkActionDialogOpen] = useState(false);
  const [bulkAction, setBulkAction] = useState<string>('');
  const [localFilters, setLocalFilters] = useState({
    status: '',
    type: '',
    riskLevel: '',
    assignedTeam: '',
    search: '',
  });
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    dispatch(fetchCases({ page: currentPage, size: pageSize, filters }));
  }, [dispatch, currentPage, pageSize, filters]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCaseClick = (caseItem: Case) => {
    setSelectedCase(caseItem);
    setDrawerOpen(true);
  };

  const handleRunTriage = async (caseId: string) => {
    try {
      await dispatch(runTriage(caseId)).unwrap();
      dispatch(addNotification({
        id: Date.now().toString(),
        message: 'Triage completed successfully',
        type: 'success',
      }));
      dispatch(fetchCases({ page: currentPage, size: pageSize, filters }));
    } catch (error) {
      dispatch(addNotification({
        id: Date.now().toString(),
        message: 'Failed to run triage',
        type: 'error',
      }));
    }
  };

  const handleBulkAction = async () => {
    if (selectedCases.length === 0) return;

    try {
      // Implement bulk actions based on bulkAction value
      switch (bulkAction) {
        case 'run_triage':
          for (const caseId of selectedCases) {
            await dispatch(runTriage(caseId)).unwrap();
          }
          break;
        case 'assign_team':
          // Implement team assignment
          break;
        case 'update_status':
          // Implement status update
          break;
      }

      dispatch(addNotification({
        id: Date.now().toString(),
        message: `Bulk action "${bulkAction}" completed`,
        type: 'success',
      }));
      setBulkActionDialogOpen(false);
      dispatch(deselectAllCases());
    } catch (error) {
      dispatch(addNotification({
        id: Date.now().toString(),
        message: 'Bulk action failed',
        type: 'error',
      }));
    }
  };

  const getStatusColor = (status: CaseStatus) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'in_progress': return 'info';
      case 'resolved': return 'success';
      case 'escalated': return 'error';
      default: return 'default';
    }
  };

  const getRiskColor = (risk: RiskLevel) => {
    switch (risk) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: CaseType) => {
    switch (type) {
      case 'insurance': return <Business />;
      case 'healthcare': return <LocalHospital />;
      case 'finance': return <TrendingUp />;
      case 'legal': return <Gavel />;
      default: return <Assignment />;
    }
  };

  const filteredCases = cases.filter((caseItem) => {
    if (localFilters.status && caseItem.status !== localFilters.status) return false;
    if (localFilters.type && caseItem.case_type !== localFilters.type) return false;
    if (localFilters.riskLevel && caseItem.risk_level !== localFilters.riskLevel) return false;
    if (localFilters.assignedTeam && caseItem.assigned_team_id !== localFilters.assignedTeam) return false;
    if (localFilters.search) {
      const searchLower = localFilters.search.toLowerCase();
      return (
        caseItem.title.toLowerCase().includes(searchLower) ||
        caseItem.description.toLowerCase().includes(searchLower) ||
        caseItem.case_id.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const sortedCases = [...filteredCases].sort((a, b) => {
    const aValue = a[sortBy as keyof Case];
    const bValue = b[sortBy as keyof Case];
    
    if (sortOrder === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  if (loading) return <LoadingSpinner message="Loading triage queue..." />;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Triage Queue
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => dispatch(fetchCases({ page: currentPage, size: pageSize, filters }))}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => setTriageDialogOpen(true)}
            disabled={selectedCases.length === 0}
          >
            Run Triage ({selectedCases.length})
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Filters and Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ mr: 2 }}>
            Filters
          </Typography>
          <IconButton onClick={() => setShowFilters(!showFilters)}>
            <FilterList />
          </IconButton>
        </Box>

        {showFilters && (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search"
                value={localFilters.search}
                onChange={(e) => setLocalFilters({ ...localFilters, search: e.target.value })}
                placeholder="Search cases..."
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={localFilters.status}
                  onChange={(e) => setLocalFilters({ ...localFilters, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="escalated">Escalated</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={localFilters.type}
                  onChange={(e) => setLocalFilters({ ...localFilters, type: e.target.value })}
                  label="Type"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="insurance">Insurance</MenuItem>
                  <MenuItem value="healthcare">Healthcare</MenuItem>
                  <MenuItem value="finance">Finance</MenuItem>
                  <MenuItem value="legal">Legal</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Risk Level</InputLabel>
                <Select
                  value={localFilters.riskLevel}
                  onChange={(e) => setLocalFilters({ ...localFilters, riskLevel: e.target.value })}
                  label="Risk Level"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="triage queue tabs">
          <Tab label={`All Cases (${sortedCases.length})`} />
          <Tab label={`Pending (${sortedCases.filter(c => c.status === 'pending').length})`} />
          <Tab label={`In Progress (${sortedCases.filter(c => c.status === 'in_progress').length})`} />
          <Tab label={`High Risk (${sortedCases.filter(c => c.risk_level === 'high' || c.risk_level === 'critical').length})`} />
        </Tabs>
      </Box>

      {/* Cases Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedCases.length === sortedCases.length && sortedCases.length > 0}
                    indeterminate={selectedCases.length > 0 && selectedCases.length < sortedCases.length}
                    onChange={(e) => {
                      if (e.target.checked) {
                        dispatch(selectAllCases());
                      } else {
                        dispatch(deselectAllCases());
                      }
                    }}
                  />
                </TableCell>
                <TableCell>Case ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Assigned To</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedCases.map((caseItem) => (
                <TableRow
                  key={caseItem.id}
                  hover
                  selected={selectedCases.includes(caseItem.id)}
                  onClick={() => handleCaseClick(caseItem)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedCases.includes(caseItem.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        if (e.target.checked) {
                          dispatch(selectCase(caseItem.id));
                        } else {
                          dispatch(deselectCase(caseItem.id));
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {caseItem.case_id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap>
                      {caseItem.title}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={getTypeIcon(caseItem.case_type)}
                      label={caseItem.case_type}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={caseItem.status}
                      color={getStatusColor(caseItem.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={caseItem.risk_level}
                      color={getRiskColor(caseItem.risk_level) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(caseItem.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {caseItem.assigned_user_id || 'Unassigned'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCaseClick(caseItem);
                          }}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Run Triage">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRunTriage(caseItem.id);
                          }}
                        >
                          <PlayArrow />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Case Detail Drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{ '& .MuiDrawer-paper': { width: 600 } }}
      >
        {selectedCase && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Case Details</Typography>
              <IconButton onClick={() => setDrawerOpen(false)}>
                <Edit />
              </IconButton>
            </Box>

            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Basic Information</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Case ID</Typography>
                    <Typography variant="body1">{selectedCase.case_id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Type</Typography>
                    <Chip
                      icon={getTypeIcon(selectedCase.case_type)}
                      label={selectedCase.case_type}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Title</Typography>
                    <Typography variant="body1">{selectedCase.title}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Description</Typography>
                    <Typography variant="body1">{selectedCase.description}</Typography>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Status & Risk</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Status</Typography>
                    <Chip
                      label={selectedCase.status}
                      color={getStatusColor(selectedCase.status) as any}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Risk Level</Typography>
                    <Chip
                      label={selectedCase.risk_level}
                      color={getRiskColor(selectedCase.risk_level) as any}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Risk Score</Typography>
                    <Typography variant="body1">
                      {(selectedCase.risk_score * 100).toFixed(1)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Priority</Typography>
                    <Typography variant="body1">{selectedCase.priority}</Typography>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Assignment</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Assigned Team</Typography>
                    <Typography variant="body1">
                      {selectedCase.assigned_team_id || 'Unassigned'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Assigned User</Typography>
                    <Typography variant="body1">
                      {selectedCase.assigned_user_id || 'Unassigned'}
                    </Typography>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Timeline</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Created"
                      secondary={new Date(selectedCase.created_at).toLocaleString()}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Last Updated"
                      secondary={new Date(selectedCase.updated_at).toLocaleString()}
                    />
                  </ListItem>
                  {selectedCase.resolved_at && (
                    <ListItem>
                      <ListItemText
                        primary="Resolved"
                        secondary={new Date(selectedCase.resolved_at).toLocaleString()}
                      />
                    </ListItem>
                  )}
                </List>
              </AccordionDetails>
            </Accordion>

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => handleRunTriage(selectedCase.id)}
                fullWidth
              >
                Run Triage
              </Button>
              <Button
                variant="outlined"
                startIcon={<Edit />}
                fullWidth
              >
                Edit Case
              </Button>
            </Box>
          </Box>
        )}
      </Drawer>

      {/* Triage Dialog */}
      <Dialog open={triageDialogOpen} onClose={() => setTriageDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Run Triage Analysis</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            This will run the complete triage pipeline on {selectedCases.length} selected case(s).
            The process includes classification, risk scoring, routing, and decision support.
          </Typography>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Processing... This may take a few moments.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTriageDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              // Handle bulk triage
              setTriageDialogOpen(false);
            }}
          >
            Run Triage
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TriageQueuePage;

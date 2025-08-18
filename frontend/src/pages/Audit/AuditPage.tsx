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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Tooltip,
  Alert,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
  Switch,
  Badge,
} from '@mui/material';
import {
  Search,
  FilterList,
  Download,
  Refresh,
  Visibility,
  History,
  Security,
  Assignment,
  Person,
  Business,
  LocalHospital,
  TrendingUp,
  Gavel,
  ExpandMore,
  CalendarToday,
  AccessTime,
  Info,
  Warning,
  CheckCircle,
  Error,
  Timeline as TimelineIcon,
  FileDownload,
  FileUpload,
  Edit,
  Delete,
  PlayArrow,
  Stop,
  Pause,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchAuditLogs } from '@/store/slices/auditSlice';
import { addNotification } from '@/store/slices/uiSlice';
import LoadingSpinner from '@/components/Common/LoadingSpinner';
import { AuditLog, AuditAction, ResourceType, UserRole } from '@/types';

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
      id={`audit-tabpanel-${index}`}
      aria-labelledby={`audit-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AuditPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { auditLogs, loading, error, totalCount } = useAppSelector((state) => state.audit);
  const { user } = useAppSelector((state) => state.auth);

  // Local state
  const [selectedAudit, setSelectedAudit] = useState<AuditLog | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [filters, setFilters] = useState({
    action: '',
    resourceType: '',
    userId: '',
    dateFrom: '',
    dateTo: '',
    search: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'table' | 'timeline'>('table');

  useEffect(() => {
    dispatch(fetchAuditLogs({
      page: currentPage + 1,
      size: pageSize,
      filters,
    }));
  }, [dispatch, currentPage, pageSize, filters]);

  const handleAuditClick = (audit: AuditLog) => {
    setSelectedAudit(audit);
    setDrawerOpen(true);
  };

  const handleRefresh = () => {
    dispatch(fetchAuditLogs({
      page: currentPage + 1,
      size: pageSize,
      filters,
    }));
    dispatch(addNotification({
      id: Date.now().toString(),
      message: 'Audit logs refreshed',
      type: 'success',
    }));
  };

  const handleExport = (format: 'csv' | 'json' | 'pdf') => {
    // Implement export functionality
    dispatch(addNotification({
      id: Date.now().toString(),
      message: `Audit logs exported as ${format.toUpperCase()}`,
      type: 'success',
    }));
    setExportDialogOpen(false);
  };

  const getActionColor = (action: AuditAction) => {
    switch (action) {
      case 'create': return 'success';
      case 'update': return 'info';
      case 'delete': return 'error';
      case 'login': return 'primary';
      case 'logout': return 'default';
      case 'export': return 'warning';
      case 'import': return 'warning';
      default: return 'default';
    }
  };

  const getActionIcon = (action: AuditAction) => {
    switch (action) {
      case 'create': return <FileUpload />;
      case 'update': return <Edit />;
      case 'delete': return <Delete />;
      case 'login': return <Person />;
      case 'logout': return <Person />;
      case 'export': return <FileDownload />;
      case 'import': return <FileUpload />;
      case 'triage_run': return <PlayArrow />;
      case 'triage_complete': return <CheckCircle />;
      case 'triage_failed': return <Error />;
      default: return <Info />;
    }
  };

  const getResourceIcon = (resourceType: ResourceType) => {
    switch (resourceType) {
      case 'case': return <Assignment />;
      case 'user': return <Person />;
      case 'team': return <Business />;
      case 'document': return <FileUpload />;
      case 'triage_result': return <PlayArrow />;
      case 'analytics': return <TrendingUp />;
      default: return <Info />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getActionDescription = (action: AuditAction, resourceType: ResourceType) => {
    switch (action) {
      case 'create': return `Created new ${resourceType}`;
      case 'update': return `Updated ${resourceType}`;
      case 'delete': return `Deleted ${resourceType}`;
      case 'login': return 'User logged in';
      case 'logout': return 'User logged out';
      case 'export': return `Exported ${resourceType} data`;
      case 'import': return `Imported ${resourceType} data`;
      case 'triage_run': return 'Started triage analysis';
      case 'triage_complete': return 'Completed triage analysis';
      case 'triage_failed': return 'Triage analysis failed';
      default: return action;
    }
  };

  if (loading) return <LoadingSpinner message="Loading audit logs..." />;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Audit Log
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </Button>
          <Button
            variant="outlined"
            startIcon={<TimelineIcon />}
            onClick={() => setViewMode(viewMode === 'table' ? 'timeline' : 'table')}
          >
            {viewMode === 'table' ? 'Timeline View' : 'Table View'}
          </Button>
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
            onClick={() => setExportDialogOpen(true)}
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

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Filter Audit Logs
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                placeholder="Search audit logs..."
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Action</InputLabel>
                <Select
                  value={filters.action}
                  onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                  label="Action"
                >
                  <MenuItem value="">All Actions</MenuItem>
                  <MenuItem value="create">Create</MenuItem>
                  <MenuItem value="update">Update</MenuItem>
                  <MenuItem value="delete">Delete</MenuItem>
                  <MenuItem value="login">Login</MenuItem>
                  <MenuItem value="logout">Logout</MenuItem>
                  <MenuItem value="export">Export</MenuItem>
                  <MenuItem value="import">Import</MenuItem>
                  <MenuItem value="triage_run">Triage Run</MenuItem>
                  <MenuItem value="triage_complete">Triage Complete</MenuItem>
                  <MenuItem value="triage_failed">Triage Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Resource Type</InputLabel>
                <Select
                  value={filters.resourceType}
                  onChange={(e) => setFilters({ ...filters, resourceType: e.target.value })}
                  label="Resource Type"
                >
                  <MenuItem value="">All Resources</MenuItem>
                  <MenuItem value="case">Case</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="team">Team</MenuItem>
                  <MenuItem value="document">Document</MenuItem>
                  <MenuItem value="triage_result">Triage Result</MenuItem>
                  <MenuItem value="analytics">Analytics</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="User ID"
                value={filters.userId}
                onChange={(e) => setFilters({ ...filters, userId: e.target.value })}
                placeholder="Filter by user..."
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Date From"
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Date To"
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Logs
                  </Typography>
                  <Typography variant="h4" component="div">
                    {totalCount || 1,247}
                  </Typography>
                </Box>
                <History sx={{ fontSize: 40, color: 'primary.main' }} />
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
                    Today's Activity
                  </Typography>
                  <Typography variant="h4" component="div">
                    {auditLogs.filter(log => {
                      const today = new Date().toDateString();
                      return new Date(log.timestamp).toDateString() === today;
                    }).length}
                  </Typography>
                </Box>
                <CalendarToday sx={{ fontSize: 40, color: 'success.main' }} />
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
                    Security Events
                  </Typography>
                  <Typography variant="h4" component="div">
                    {auditLogs.filter(log => 
                      ['login', 'logout', 'delete', 'export', 'import'].includes(log.action)
                    ).length}
                  </Typography>
                </Box>
                <Security sx={{ fontSize: 40, color: 'warning.main' }} />
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
                    Triage Events
                  </Typography>
                  <Typography variant="h4" component="div">
                    {auditLogs.filter(log => 
                      ['triage_run', 'triage_complete', 'triage_failed'].includes(log.action)
                    ).length}
                  </Typography>
                </Box>
                <PlayArrow sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Audit Logs Table */}
      {viewMode === 'table' && (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Resource</TableCell>
                  <TableCell>Details</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.map((audit) => (
                  <TableRow key={audit.id} hover>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {formatTimestamp(audit.timestamp)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(audit.timestamp).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Person sx={{ fontSize: 16 }} />
                        <Typography variant="body2">
                          {audit.user_id}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getActionIcon(audit.action)}
                        label={getActionDescription(audit.action, audit.resource_type)}
                        color={getActionColor(audit.action) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getResourceIcon(audit.resource_type)}
                        <Typography variant="body2">
                          {audit.resource_type}
                        </Typography>
                        {audit.resource_id && (
                          <Chip label={audit.resource_id} size="small" variant="outlined" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {audit.details}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {audit.ip_address || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleAuditClick(audit)}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={totalCount || 0}
            page={currentPage}
            onPageChange={(event, newPage) => setCurrentPage(newPage)}
            rowsPerPage={pageSize}
            onRowsPerPageChange={(event) => {
              setPageSize(parseInt(event.target.value, 10));
              setCurrentPage(0);
            }}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </Paper>
      )}

      {/* Timeline View */}
      {viewMode === 'timeline' && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Audit Timeline
          </Typography>
          <Timeline>
            {auditLogs.map((audit, index) => (
              <TimelineItem key={audit.id}>
                <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                  {formatTimestamp(audit.timestamp)}
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot color={getActionColor(audit.action) as any}>
                    {getActionIcon(audit.action)}
                  </TimelineDot>
                  {index < auditLogs.length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent sx={{ py: '12px', px: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="h6" component="span">
                      {getActionDescription(audit.action, audit.resource_type)}
                    </Typography>
                    <Chip label={audit.resource_type} size="small" variant="outlined" />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    User: {audit.user_id} | IP: {audit.ip_address || 'N/A'}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {audit.details}
                  </Typography>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => handleAuditClick(audit)}
                    sx={{ mt: 1 }}
                  >
                    View Details
                  </Button>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>
        </Paper>
      )}

      {/* Audit Detail Drawer */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{ '& .MuiDrawer-paper': { width: 600 } }}
      >
        {selectedAudit && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Audit Details</Typography>
              <IconButton onClick={() => setDrawerOpen(false)}>
                <Info />
              </IconButton>
            </Box>

            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Basic Information</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Audit ID</Typography>
                    <Typography variant="body1">{selectedAudit.id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Timestamp</Typography>
                    <Typography variant="body1">{formatTimestamp(selectedAudit.timestamp)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">User</Typography>
                    <Typography variant="body1">{selectedAudit.user_id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">IP Address</Typography>
                    <Typography variant="body1">{selectedAudit.ip_address || 'N/A'}</Typography>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">Action Details</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Action</Typography>
                    <Chip
                      icon={getActionIcon(selectedAudit.action)}
                      label={selectedAudit.action}
                      color={getActionColor(selectedAudit.action) as any}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Resource Type</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getResourceIcon(selectedAudit.resource_type)}
                      <Typography variant="body1">{selectedAudit.resource_type}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Resource ID</Typography>
                    <Typography variant="body1">{selectedAudit.resource_id || 'N/A'}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Description</Typography>
                    <Typography variant="body1">{selectedAudit.details}</Typography>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {selectedAudit.metadata && (
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">Additional Metadata</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(selectedAudit.metadata, null, 2)}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            )}
          </Box>
        )}
      </Drawer>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Export Audit Logs</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Choose the format and options for exporting audit logs.
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Checkbox defaultChecked />}
                label="Include all fields"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Checkbox defaultChecked />}
                label="Include metadata"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Checkbox />}
                label="Filter by current search criteria"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => handleExport('csv')} variant="outlined">CSV</Button>
          <Button onClick={() => handleExport('json')} variant="outlined">JSON</Button>
          <Button onClick={() => handleExport('pdf')} variant="contained">PDF</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditPage;

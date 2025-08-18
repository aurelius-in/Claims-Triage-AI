import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Chip,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Palette,
  Notifications,
  Security,
  AccountCircle,
  Business,
  Refresh,
  Save,
  Visibility,
  VisibilityOff,
  Edit,
  Delete,
  Add,
  ExpandMore,
  DarkMode,
  LightMode,
  Email,
  Phone,
  Lock,
  Key,
  Storage,
  Speed,
  BugReport,
  Help,
  Info,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { addNotification } from '@/store/slices/uiSlice';
import { setTheme, toggleTheme } from '@/store/slices/uiSlice';
import { User, UserSettings, ThemeConfig } from '@/types';

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
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SettingsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { theme } = useAppSelector((state) => state.ui);

  // Local state
  const [tabValue, setTabValue] = useState(0);
  const [settings, setSettings] = useState<UserSettings>({
    theme: {
      mode: 'light',
      primaryColor: '#1976d2',
      secondaryColor: '#dc004e',
    },
    notifications: {
      email: true,
      push: true,
      sound: true,
    },
    dashboard: {
      defaultView: 'overview',
      refreshInterval: 30,
    },
  });
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [profileData, setProfileData] = useState({
    fullName: user?.full_name || '',
    email: user?.email || '',
    phone: '',
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleThemeChange = (mode: 'light' | 'dark') => {
    dispatch(setTheme({ ...theme, mode }));
    setSettings({
      ...settings,
      theme: { ...settings.theme, mode },
    });
  };

  const handleNotificationChange = (type: keyof typeof settings.notifications) => {
    setSettings({
      ...settings,
      notifications: {
        ...settings.notifications,
        [type]: !settings.notifications[type],
      },
    });
  };

  const handleSaveSettings = () => {
    // Implement settings save
    dispatch(addNotification({
      id: Date.now().toString(),
      message: 'Settings saved successfully',
      type: 'success',
    }));
  };

  const handlePasswordChange = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      dispatch(addNotification({
        id: Date.now().toString(),
        message: 'New passwords do not match',
        type: 'error',
      }));
      return;
    }
    // Implement password change
    dispatch(addNotification({
      id: Date.now().toString(),
      message: 'Password changed successfully',
      type: 'success',
    }));
    setPasswordDialogOpen(false);
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
  };

  const handleProfileUpdate = () => {
    // Implement profile update
    dispatch(addNotification({
      id: Date.now().toString(),
      message: 'Profile updated successfully',
      type: 'success',
    }));
    setProfileDialogOpen(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Settings
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => window.location.reload()}
          >
            Reset
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSaveSettings}
          >
            Save Changes
          </Button>
        </Box>
      </Box>

      {/* Settings Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="settings tabs">
          <Tab label="General" />
          <Tab label="Appearance" />
          <Tab label="Notifications" />
          <Tab label="Account" />
          <Tab label="Security" />
          <Tab label="System" />
        </Tabs>
      </Box>

      {/* General Settings Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Dashboard Settings
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Default View</InputLabel>
                  <Select
                    value={settings.dashboard.defaultView}
                    onChange={(e) => setSettings({
                      ...settings,
                      dashboard: { ...settings.dashboard, defaultView: e.target.value as any }
                    })}
                    label="Default View"
                  >
                    <MenuItem value="overview">Overview</MenuItem>
                    <MenuItem value="triage">Triage Queue</MenuItem>
                    <MenuItem value="analytics">Analytics</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel>Refresh Interval (seconds)</InputLabel>
                  <Select
                    value={settings.dashboard.refreshInterval}
                    onChange={(e) => setSettings({
                      ...settings,
                      dashboard: { ...settings.dashboard, refreshInterval: e.target.value as number }
                    })}
                    label="Refresh Interval (seconds)"
                  >
                    <MenuItem value={15}>15 seconds</MenuItem>
                    <MenuItem value={30}>30 seconds</MenuItem>
                    <MenuItem value={60}>1 minute</MenuItem>
                    <MenuItem value={300}>5 minutes</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  User Information
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ mr: 2, width: 56, height: 56 }}>
                    <AccountCircle />
                  </Avatar>
                  <Box>
                    <Typography variant="h6">{user?.full_name}</Typography>
                    <Typography variant="body2" color="text.secondary">{user?.email}</Typography>
                    <Chip label={user?.role} size="small" sx={{ mt: 1 }} />
                  </Box>
                </Box>
                <Button
                  variant="outlined"
                  startIcon={<Edit />}
                  onClick={() => setProfileDialogOpen(true)}
                  fullWidth
                >
                  Edit Profile
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Appearance Settings Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Theme Settings
                </Typography>
                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.theme.mode === 'dark'}
                        onChange={() => handleThemeChange(settings.theme.mode === 'dark' ? 'light' : 'dark')}
                      />
                    }
                    label="Dark Mode"
                  />
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    {settings.theme.mode === 'dark' ? <DarkMode /> : <LightMode />}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {settings.theme.mode === 'dark' ? 'Dark theme enabled' : 'Light theme enabled'}
                    </Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" gutterBottom>
                  Color Scheme
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Primary Color"
                      type="color"
                      value={settings.theme.primaryColor}
                      onChange={(e) => setSettings({
                        ...settings,
                        theme: { ...settings.theme, primaryColor: e.target.value }
                      })}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Secondary Color"
                      type="color"
                      value={settings.theme.secondaryColor}
                      onChange={(e) => setSettings({
                        ...settings,
                        theme: { ...settings.theme, secondaryColor: e.target.value }
                      })}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Display Options
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Show animations"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Compact mode"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="High contrast mode"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Show tooltips"
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Notifications Settings Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Notification Preferences
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.email}
                      onChange={() => handleNotificationChange('email')}
                    />
                  }
                  label="Email notifications"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.push}
                      onChange={() => handleNotificationChange('push')}
                    />
                  }
                  label="Push notifications"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.sound}
                      onChange={() => handleNotificationChange('sound')}
                    />
                  }
                  label="Sound notifications"
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Notification Types
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="New case assignments"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Triage completions"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="System updates"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="SLA warnings"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Escalation alerts"
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Account Settings Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Account Information
                </Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <AccountCircle />
                    </ListItemIcon>
                    <ListItemText
                      primary="Full Name"
                      secondary={user?.full_name}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Email />
                    </ListItemIcon>
                    <ListItemText
                      primary="Email"
                      secondary={user?.email}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Business />
                    </ListItemIcon>
                    <ListItemText
                      primary="Role"
                      secondary={user?.role}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <AccountCircle />
                    </ListItemIcon>
                    <ListItemText
                      primary="Account Status"
                      secondary={user?.is_active ? 'Active' : 'Inactive'}
                    />
                    <ListItemSecondaryAction>
                      <Chip
                        label={user?.is_active ? 'Active' : 'Inactive'}
                        color={user?.is_active ? 'success' : 'error'}
                        size="small"
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Account Actions
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Edit />}
                  onClick={() => setProfileDialogOpen(true)}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Edit Profile
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Lock />}
                  onClick={() => setPasswordDialogOpen(true)}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Change Password
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Key />}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  API Keys
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Delete />}
                  fullWidth
                >
                  Delete Account
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Security Settings Tab */}
      <TabPanel value={tabValue} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Settings
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Two-factor authentication"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Session timeout"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Login notifications"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Password complexity requirements"
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Session Management
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Current Session"
                      secondary="Active - Last activity: 2 minutes ago"
                    />
                    <ListItemSecondaryAction>
                      <Chip label="Active" color="success" size="small" />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Mobile Device"
                      secondary="iPhone - Last login: 1 hour ago"
                    />
                    <ListItemSecondaryAction>
                      <Button size="small" color="error">
                        Revoke
                      </Button>
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* System Settings Tab */}
      <TabPanel value={tabValue} index={5}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Information
                </Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <Storage />
                    </ListItemIcon>
                    <ListItemText
                      primary="Storage Used"
                      secondary="2.4 GB / 10 GB"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Speed />
                    </ListItemIcon>
                    <ListItemText
                      primary="Performance"
                      secondary="Optimal"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Info />
                    </ListItemIcon>
                    <ListItemText
                      primary="Version"
                      secondary="v1.0.0"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Support & Help
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Help />}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Help Center
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<BugReport />}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Report Bug
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Info />}
                  fullWidth
                >
                  About
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Password Change Dialog */}
      <Dialog open={passwordDialogOpen} onClose={() => setPasswordDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Current Password"
            type={showPassword ? 'text' : 'password'}
            value={passwordData.currentPassword}
            onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
            sx={{ mb: 2, mt: 1 }}
            InputProps={{
              endAdornment: (
                <IconButton onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              ),
            }}
          />
          <TextField
            fullWidth
            label="New Password"
            type={showPassword ? 'text' : 'password'}
            value={passwordData.newPassword}
            onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Confirm New Password"
            type={showPassword ? 'text' : 'password'}
            value={passwordData.confirmPassword}
            onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
            error={passwordData.newPassword !== passwordData.confirmPassword && passwordData.confirmPassword !== ''}
            helperText={passwordData.newPassword !== passwordData.confirmPassword && passwordData.confirmPassword !== '' ? 'Passwords do not match' : ''}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialogOpen(false)}>Cancel</Button>
          <Button onClick={handlePasswordChange} variant="contained">Change Password</Button>
        </DialogActions>
      </Dialog>

      {/* Profile Update Dialog */}
      <Dialog open={profileDialogOpen} onClose={() => setProfileDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Full Name"
            value={profileData.fullName}
            onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
            sx={{ mb: 2, mt: 1 }}
          />
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={profileData.email}
            onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Phone"
            value={profileData.phone}
            onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleProfileUpdate} variant="contained">Update Profile</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SettingsPage;

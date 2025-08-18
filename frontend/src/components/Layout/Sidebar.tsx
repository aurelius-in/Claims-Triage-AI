import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Queue as QueueIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import { useAppSelector } from '@/store/hooks';

interface MenuItem {
  text: string;
  icon: React.ReactNode;
  path: string;
  badge?: string;
  badgeColor?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
}

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { cases } = useAppSelector((state) => state.cases);

  // Get pending cases count for badge
  const pendingCasesCount = cases.filter(case_ => case_.status === 'pending').length;

  const menuItems: MenuItem[] = [
    {
      text: 'Overview',
      icon: <DashboardIcon />,
      path: '/overview',
    },
    {
      text: 'Triage Queue',
      icon: <QueueIcon />,
      path: '/triage',
      badge: pendingCasesCount > 0 ? pendingCasesCount.toString() : undefined,
      badgeColor: 'error',
    },
    {
      text: 'Analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
    },
    {
      text: 'Audit Log',
      icon: <HistoryIcon />,
      path: '/audit',
    },
  ];

  // Admin/Supervisor only items
  if (user?.role === 'admin' || user?.role === 'supervisor') {
    menuItems.push(
      {
        text: 'Team Management',
        icon: <AssignmentIcon />,
        path: '/teams',
      },
      {
        text: 'Settings',
        icon: <SettingsIcon />,
        path: '/settings',
      }
    );
  }

  // Admin only items
  if (user?.role === 'admin') {
    menuItems.push({
      text: 'Security',
      icon: <SecurityIcon />,
      path: '/security',
    });
  }

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <Box sx={{ width: 280, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
          Claims Triage AI
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Agent-Driven Platform
        </Typography>
      </Box>

      {/* Navigation */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ pt: 1 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  mx: 1,
                  borderRadius: 1,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: location.pathname === item.path ? 'inherit' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: location.pathname === item.path ? 600 : 400,
                  }}
                />
                {item.badge && (
                  <Chip
                    label={item.badge}
                    size="small"
                    color={item.badgeColor || 'default'}
                    sx={{ ml: 1 }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary" align="center">
          Version 1.0.0
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          © 2024 Claims Triage AI
        </Typography>
      </Box>
    </Box>
  );
};

export default Sidebar;

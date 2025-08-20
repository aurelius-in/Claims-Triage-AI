import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Drawer, AppBar, Toolbar, IconButton, Typography, useTheme } from '@mui/material';
import { Menu as MenuIcon, AccountCircle, Notifications } from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { toggleSidebar, toggleTheme } from '@/store/slices/uiSlice';
import Sidebar from './Sidebar';
import UserMenu from './UserMenu';

const DRAWER_WIDTH = 280;

const Layout: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { sidebarOpen, theme: appTheme } = useAppSelector((state) => state.ui);
  const { user } = useAppSelector((state) => state.auth);

  const handleDrawerToggle = () => {
    dispatch(toggleSidebar());
  };

  const handleThemeToggle = () => {
    dispatch(toggleTheme());
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
          zIndex: theme.zIndex.drawer + 1,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          boxShadow: 'none',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1,
              background: 'linear-gradient(135deg, #00d4ff, #ff6b6b, #4ecdc4)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              fontWeight: 800,
            }}
          >
            Claims Triage AI
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              size="large"
              aria-label="toggle theme"
              color="inherit"
              onClick={handleThemeToggle}
            >
              {appTheme.mode === 'dark' ? '☀️' : '🌙'}
            </IconButton>
            
            <IconButton
              size="large"
              aria-label="notifications"
              color="inherit"
            >
              <Notifications />
            </IconButton>
            
            <UserMenu user={user} />
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={sidebarOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
        >
          <Sidebar />
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
          open
        >
          <Sidebar />
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 1.5,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: '64px', // AppBar height
          background: '#0a0a0a',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;

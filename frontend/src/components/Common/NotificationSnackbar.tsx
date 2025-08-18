import React, { useEffect } from 'react';
import { Snackbar, Alert, AlertColor } from '@mui/material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { removeNotification } from '@/store/slices/uiSlice';

const NotificationSnackbar: React.FC = () => {
  const dispatch = useAppDispatch();
  const notifications = useAppSelector((state) => state.ui.notifications);

  const handleClose = (id: string) => {
    dispatch(removeNotification(id));
  };

  const currentNotification = notifications[0];

  useEffect(() => {
    if (currentNotification?.duration) {
      const timer = setTimeout(() => {
        dispatch(removeNotification(currentNotification.id));
      }, currentNotification.duration);

      return () => clearTimeout(timer);
    }
  }, [currentNotification, dispatch]);

  if (!currentNotification) {
    return null;
  }

  return (
    <Snackbar
      open={!!currentNotification}
      autoHideDuration={currentNotification.duration || 6000}
      onClose={() => handleClose(currentNotification.id)}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        onClose={() => handleClose(currentNotification.id)}
        severity={currentNotification.type as AlertColor}
        variant="filled"
        sx={{ width: '100%' }}
        action={
          currentNotification.action && (
            <Alert
              color="inherit"
              size="small"
              onClick={currentNotification.action.onClick}
              sx={{ cursor: 'pointer', textDecoration: 'underline' }}
            >
              {currentNotification.action.label}
            </Alert>
          )
        }
      >
        <div>
          <div style={{ fontWeight: 'bold' }}>{currentNotification.title}</div>
          <div>{currentNotification.message}</div>
        </div>
      </Alert>
    </Snackbar>
  );
};

export default NotificationSnackbar;

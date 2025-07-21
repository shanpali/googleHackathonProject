import React, { useState } from 'react';
import { Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Login from './Login';

const theme = createTheme({
  palette: {
    background: {
      default: '#f7f9fb',
    },
  },
});

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {loggedIn ? (
          <>
            <Sidebar />
            <Dashboard />
          </>
        ) : (
          <Login onLogin={() => setLoggedIn(true)} />
        )}
      </Box>
    </ThemeProvider>
  );
}

export default App; 
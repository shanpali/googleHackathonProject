import React, { useState } from 'react';
import { Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Portfolio from './components/Portfolio';
import TaxPlanning from './components/TaxPlanning';
import NomineeSafeguard from './components/NomineeSafeguard';
import Reports from './components/Reports';
import Settings from './components/Settings';
import Login from './Login';
import Goals from './components/Goals';
import PersonalisedNews from './components/PersonalisedNews';

const theme = createTheme({
  palette: {
    background: {
      default: '#f7f9fb',
    },
  },
});

const TABS = [
  'Dashboard',
  'Portfolio',
  'Goals',
  'Tax Planning',
  'Nominee Safeguard',
  'Reports',
  'Settings',
];



function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [selectedTab, setSelectedTab] = useState('Dashboard');
  const [phone, setPhone] = useState('');

  const handleLogin = (loginPhone) => {
    setPhone(loginPhone);
    setLoggedIn(true);
  };

  const renderContent = () => {
    switch (selectedTab) {
      case 'Dashboard':
        return <Dashboard phone={phone} setSelectedTab={setSelectedTab} />;
      case 'Portfolio':
        return <Portfolio phone={phone} />;
      case 'Goals':
        return <Goals />;
      case 'Tax Planning':
        return <TaxPlanning phone={phone} />;
      case 'Nominee Safeguard':
        return <NomineeSafeguard phone={phone} />;
      case 'Reports':
        return <Reports phone={phone} />;
      case 'Settings':
        return <Settings phone={phone} />;
      case 'Personalised News':
        return <PersonalisedNews phone={phone} />;
      default:
        return <Dashboard phone={phone} setSelectedTab={setSelectedTab} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {loggedIn ? (
          <>
            <Sidebar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
            {renderContent()}
          </>
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </Box>
    </ThemeProvider>
  );
}

export default App; 
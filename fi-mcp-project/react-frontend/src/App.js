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
  'Investment Insights',
];



function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [selectedTab, setSelectedTab] = useState('Dashboard');
  const [phone, setPhone] = useState('');
  const [globalRefreshTrigger, setGlobalRefreshTrigger] = useState(0);

  const handleLogin = (loginPhone) => {
    setPhone(loginPhone);
    setLoggedIn(true);
  };

  const globalRefresh = () => {
    setGlobalRefreshTrigger(prev => prev + 1);
  };

  const renderContent = () => {
    switch (selectedTab) {
      case 'Dashboard':
        return <Dashboard phone={phone} setSelectedTab={setSelectedTab} globalRefreshTrigger={globalRefreshTrigger} />;
      case 'Portfolio':
        return <Portfolio phone={phone} />;
      case 'Goals':
        return <Goals onGoalChange={globalRefresh} />;
      case 'Tax Planning':
        return <TaxPlanning phone={phone} />;
      case 'Nominee Safeguard':
        return <NomineeSafeguard phone={phone} />;
      case 'Reports':
        return <Reports phone={phone} />;
      case 'Settings':
        return <Settings phone={phone} />;
      case 'Investment Insights':
        return <PersonalisedNews phone={phone} />;
      default:
        return <Dashboard phone={phone} setSelectedTab={setSelectedTab} globalRefreshTrigger={globalRefreshTrigger} />;
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
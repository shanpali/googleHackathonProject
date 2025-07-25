import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Grid, 
  CircularProgress, 
  Paper, 
  InputBase, 
  IconButton,
  Badge,
  Toolbar,
  Popover,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import NotificationsIcon from '@mui/icons-material/Notifications';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import FinancialOverview from './FinancialOverview';
import AssetAllocation from './AssetAllocation';
import Insights from './Insights';
import HealthScore from './HealthScore';
import NomineeSafeguard from './NomineeSafeguard';
import RecentTransactions from './RecentTransactions';
import PageHeader from './PageHeader';
import axios from 'axios';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Get current date in a readable format
  const getCurrentDate = () => {
    const now = new Date();
    const options = { year: 'numeric', month: 'long' };
    return now.toLocaleDateString('en-US', options);
  };

  useEffect(() => {
    axios.get('/financial-data', { withCredentials: true })
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <Box sx={{ flexGrow: 1, p: 4 }}><CircularProgress /></Box>;
  if (!data) return <Box sx={{ flexGrow: 1, p: 4 }}>No data available.</Box>;

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f7f9fb', minHeight: '100vh' }}>
      <PageHeader title="Dashboard" />

      {/* Dashboard Content */}
      <Box sx={{ p: 4 }}>
        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1f2937', marginBottom: '8px' }}>
          Welcome back, Rahul
        </div>
        <div style={{ color: '#6b7280', marginBottom: '24px' }}>
          Here's your financial overview for {getCurrentDate()}
        </div>
        
        <FinancialOverview data={data} />
  
        <Grid container spacing={3} mt={2}>
          <Grid item xs={12} md={8}>
            <AssetAllocation data={data} />
            <Insights data={data} />
          </Grid>
          <Grid item xs={12} md={4}>
            <HealthScore data={data} />
            <NomineeSafeguard data={data} />
          </Grid>
        </Grid>
        <RecentTransactions data={data} />
      </Box>
    </Box>
  );
} 
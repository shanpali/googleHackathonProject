import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, CircularProgress } from '@mui/material';
import FinancialOverview from './FinancialOverview';
import AssetAllocation from './AssetAllocation';
import Insights from './Insights';
import HealthScore from './HealthScore';
import NomineeSafeguard from './NomineeSafeguard';
import RecentTransactions from './RecentTransactions';
import axios from 'axios';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

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
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Typography variant="h5" fontWeight={700}>Welcome back, Rahul</Typography>
      <Typography color="text.secondary" mb={3}>Here's your financial overview for May 2023</Typography>
      <FinancialOverview data={data} />
      <Grid container spacing={3} columns={12} mt={2}>
        <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 8' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
          <AssetAllocation data={data} />
          <Insights data={data} />
        </Box>
        <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 4' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
          <HealthScore data={data} />
          <NomineeSafeguard data={data} />
        </Box>
      </Grid>
      <RecentTransactions data={data} />
    </Box>
  );
} 
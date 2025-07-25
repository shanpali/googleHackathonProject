import React from 'react';
import { Grid, Card, CardContent, Box } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import ShieldIcon from '@mui/icons-material/Shield';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import UnifiedFinancialOverview from './UnifiedFinancialOverview';

export default function FinancialOverview({ data }) {
  // Extract values from real data
  const netWorth = data.fetch_net_worth?.netWorthResponse?.totalNetWorthValue?.units || '—';
  const investments = data.fetch_net_worth?.netWorthResponse?.assetValues?.find(a => a.netWorthAttribute === 'ASSET_TYPE_MUTUAL_FUND')?.value?.units || '—';
  const savings = data.fetch_bank_transactions?.accounts?.reduce((sum, acc) => sum + (parseFloat(acc.balance) || 0), 0) || '—';
  // If you have insurance data, use it; otherwise, show '—'
  const insurance = data.fetch_insurance?.totalCoverage || '—';

  const cards = [
    { label: 'Total Net Worth', value: `₹${netWorth}`, change: '', icon: <TrendingUpIcon color="primary" fontSize="large" /> },
    { label: 'Investments', value: `₹${investments}`, change: '', icon: <ShowChartIcon color="success" fontSize="large" /> },
    { label: 'Savings', value: `₹${savings}`, change: '', icon: <SavingsIcon color="secondary" fontSize="large" /> },
    { label: 'Insurance Coverage', value: insurance !== '—' ? `₹${insurance}` : '—', change: '', icon: <ShieldIcon color="warning" fontSize="large" /> },
  ];

  return (
    <Grid container spacing={2} mb={2}>
      <UnifiedFinancialOverview/>
      {/* {cards.map((item) => (
        <Grid item xs={12} sm={6} md={3} key={item.label}>
          <Card sx={{ borderRadius: 3, boxShadow: 0 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {item.icon}
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{item.label}</div>
              </Box>
              <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{item.value}</div>
              <div style={{ fontSize: '0.875rem', color: item.change.startsWith('+') ? 'green' : 'red' }}>
                {item.change}
              </div>
            </CardContent>
          </Card>
        </Grid>
      ))} */}
    </Grid>
  );
} 
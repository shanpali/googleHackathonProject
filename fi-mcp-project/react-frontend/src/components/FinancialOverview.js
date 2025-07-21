import React from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import ShieldIcon from '@mui/icons-material/Shield';
import ShowChartIcon from '@mui/icons-material/ShowChart';

export default function FinancialOverview({ data }) {
  // Use real data from props
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
    <Grid container spacing={2} columns={12}>
      {cards.map((item, idx) => (
        <Box key={item.label} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' }, display: 'flex' }}>
          <Card sx={{ borderRadius: 3, boxShadow: 0, flex: 1 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {item.icon}
                <Typography variant="subtitle2" color="text.secondary">{item.label}</Typography>
              </Box>
              <Typography variant="h6" fontWeight={700}>{item.value}</Typography>
              {item.change && (
                <Typography variant="body2" color={item.change.startsWith('+') ? 'green' : 'red'}>
                  {item.change}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      ))}
    </Grid>
  );
} 
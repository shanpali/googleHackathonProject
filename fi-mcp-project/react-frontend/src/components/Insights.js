import React from 'react';
import { Card, CardContent, Typography, Grid, Box, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import InfoIcon from '@mui/icons-material/Info';
import SavingsIcon from '@mui/icons-material/Savings';

const insights = [
  {
    title: 'Tax Optimization Required',
    priority: 'High Priority',
    desc: 'Invest ₹1,50,000 in ELSS by June 15th to save ₹45,000 in taxes this year. Our AI analysis shows you have sufficient funds in your HDFC savings account.',
    action: 'Take Action',
    icon: <ErrorOutlineIcon color="error" />, color: 'error',
    save: 'Save ₹45,000',
  },
  {
    title: 'Portfolio Drift Detected',
    priority: 'Medium Priority',
    desc: 'Your portfolio has drifted from your target allocation. Consider rebalancing to optimize risk/return based on AI analysis. Equity exposure is 8% higher than your risk profile suggests.',
    action: 'View Details',
    icon: <TrendingUpIcon color="warning" />, color: 'warning',
    save: '+2.3% potential',
  },
  {
    title: 'Spending Pattern Analysis',
    priority: 'Informational',
    desc: 'Your discretionary spending increased by 15% this month. The main categories with increases were dining out (+32%) and entertainment (+24%).',
    action: 'See Budget Plan',
    icon: <InfoIcon color="info" />, color: 'info',
    save: '',
  },
  {
    title: 'Capital Gain Opportunity',
    priority: 'Opportunity',
    desc: 'Offset your recent capital gains of ₹1,30,000 from Infosys shares by selling your underperforming SBI Mutual Fund units, potentially saving ₹32,500 in taxes.',
    action: 'Explore Strategy',
    icon: <SavingsIcon color="success" />, color: 'success',
    save: 'Save ₹32,500',
  },
];

export default function Insights() {
  return (
    <Box mt={3}>
      <Typography variant="h6" fontWeight={700} mb={2}>Proactive Insights & Alerts</Typography>
      <Grid container spacing={2}>
        {insights.map((item, idx) => (
          <Grid item xs={12} sm={6} md={6} key={item.title}>
            <Card sx={{ borderLeft: `4px solid`, borderColor: `${item.color}.main`, borderRadius: 3, mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {item.icon}
                  <Typography variant="subtitle1" fontWeight={700}>{item.title}</Typography>
                  <Box flexGrow={1} />
                  {item.save && <Typography color={item.color + ".main"} fontWeight={700}>{item.save}</Typography>}
                </Box>
                <Typography variant="body2" color="text.secondary" mt={1}>{item.desc}</Typography>
                <Button variant="outlined" size="small" sx={{ mt: 2 }}>{item.action}</Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 
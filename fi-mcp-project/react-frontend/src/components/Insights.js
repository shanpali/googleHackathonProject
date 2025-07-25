import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Grid, Box, Button, CircularProgress, Alert, IconButton, Tooltip, Chip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import InfoIcon from '@mui/icons-material/Info';
import SavingsIcon from '@mui/icons-material/Savings';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import axios from 'axios';

const ICON_MAP = {
  tax: <ErrorOutlineIcon color="error" />,
  portfolio: <TrendingUpIcon color="warning" />,
  spending: <InfoIcon color="info" />,
  opportunity: <SavingsIcon color="success" />,
  alert: <WarningAmberIcon color="warning" />,
};

const fallbackInsights = [
  {
    title: 'Tax Optimization Required',
    priority: 'High Priority',
    description: 'Invest ₹1,50,000 in ELSS by June 15th to save ₹45,000 in taxes this year. Our AI analysis shows you have sufficient funds in your HDFC savings account.',
    action: 'Take Action',
    icon: 'tax',
    save: 'Save ₹45,000',
  },
  {
    title: 'Portfolio Drift Detected',
    priority: 'Medium Priority',
    description: 'Your portfolio has drifted from your target allocation. Consider rebalancing to optimize risk/return based on AI analysis. Equity exposure is 8% higher than your risk profile suggests.',
    action: 'View Details',
    icon: 'portfolio',
    save: '+2.3% potential',
  },
  {
    title: 'Spending Pattern Analysis',
    priority: 'Informational',
    description: 'Your discretionary spending increased by 15% this month. The main categories with increases were dining out (+32%) and entertainment (+24%).',
    action: 'See Budget Plan',
    icon: 'spending',
    save: '',
  },
  {
    title: 'Capital Gain Opportunity',
    priority: 'Opportunity',
    description: 'Offset your recent capital gains of ₹1,30,000 from Infosys shares by selling your underperforming SBI Mutual Fund units, potentially saving ₹32,500 in taxes.',
    action: 'Explore Strategy',
    icon: 'opportunity',
    save: 'Save ₹32,500',
  },
];

export default function Insights({ data, customInsights }) {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (customInsights) {
      setInsights(customInsights);
      setLoading(false);
      setError(null);
      return;
    }
    let mounted = true;
    setLoading(true);
    setError(null);
    axios.get('/insights', { withCredentials: true })
      .then(res => {
        if (mounted && res.data && Array.isArray(res.data.insights)) {
          setInsights(res.data.insights);
        } else if (mounted) {
          setError('No insights found.');
          setInsights(fallbackInsights);
        }
      })
      .catch(err => {
        setError('Could not fetch insights. Showing sample insights.');
        setInsights(fallbackInsights);
      })
      .finally(() => setLoading(false));
    return () => { mounted = false; };
    // eslint-disable-next-line
  }, [customInsights]);

  // Refresh handler
  const handleRefresh = () => {
    setRefreshing(true);
    setError(null);
    axios.get('/insights?refresh=true', { withCredentials: true })
      .then(res => {
        if (res.data && Array.isArray(res.data.insights)) {
          setInsights(res.data.insights);
        } else {
          setError('No insights found.');
        }
      })
      .catch(() => {
        setError('Could not refresh insights.');
      })
      .finally(() => setRefreshing(false));
  };

  // Helper to check if insurance data is missing
  const hasInsuranceData = !!(data && data.fetch_insurance && typeof data.fetch_insurance.totalCoverage === 'number' && data.fetch_insurance.totalCoverage > 0);
  // Helper to check if any insight is about insurance
  const hasInsuranceInsight = insights.some(insight =>
    insight.title && insight.title.toLowerCase().includes('insurance')
  );

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, mx: 'auto', p: { xs: 1, md: 3 } }}>
      {/* Highlight generic advice if insurance data is missing and insight is about insurance */}
      {!hasInsuranceData && hasInsuranceInsight && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <b>Note:</b> AI is providing generic insurance advice due to missing insurance data. Connect your insurance account for personalized insights.
        </Alert>
      )}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={700} mr={1}>Proactive Insights & Alerts</Typography>
        {customInsights && <Chip label="Goal-based" color="secondary" size="small" sx={{ ml: 1 }} />}
        <Tooltip title="Refresh insights from Gemini AI">
          <span>
            <IconButton onClick={handleRefresh} disabled={refreshing || loading || !!customInsights} size="small" color="primary">
              <RefreshIcon />
            </IconButton>
          </span>
        </Tooltip>
        {refreshing && <Typography variant="body2" color="primary" ml={1}>Refreshing...</Typography>}
      </Box>
      {loading && <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}><CircularProgress /></Box>}
      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={2}>
        {insights.map((item, idx) => (
          <Grid item xs={12} sm={6} md={6} key={item.title + idx}>
            <Card sx={{ borderLeft: `4px solid`, borderColor: `${item.priority?.toLowerCase().includes('high') ? 'error.main' : item.priority?.toLowerCase().includes('medium') ? 'warning.main' : item.priority?.toLowerCase().includes('opportunity') ? 'success.main' : 'info.main'}`, borderRadius: 3, mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {ICON_MAP[item.icon] || <InfoIcon color="info" />}
                  <Typography variant="subtitle1" fontWeight={700}>{item.title}</Typography>
                  <Box flexGrow={1} />
                  {item.save && <Typography color="success.main" fontWeight={700}>{item.save}</Typography>}
                </Box>
                <Typography variant="body2" color="text.secondary" mt={1}>{item.description}</Typography>
                <Button variant="outlined" size="small" sx={{ mt: 2 }}>{item.action}</Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 
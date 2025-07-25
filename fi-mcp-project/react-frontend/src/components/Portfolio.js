import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import PieChartIcon from '@mui/icons-material/PieChart';
import PageHeader from './PageHeader';

export default function Portfolio() {
  const portfolioData = [
    { name: 'Equity Mutual Funds', value: '₹45,23,450', percentage: 58, color: '#3b82f6', growth: '+12.4%' },
    { name: 'Debt Funds', value: '₹18,67,890', percentage: 24, color: '#10b981', growth: '+5.2%' },
    { name: 'Direct Stocks', value: '₹12,45,670', percentage: 16, color: '#8b5cf6', growth: '+18.7%' },
    { name: 'Gold ETF', value: '₹1,87,450', percentage: 2, color: '#f59e0b', growth: '+3.1%' }
  ];

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f7f9fb', minHeight: '100vh' }}>
      <PageHeader title="Portfolio Overview" />
      
      <Box sx={{ p: 4 }}>
        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight={700} color="#1f2937" mb={1}>
            Portfolio Overview
          </Typography>
          <Typography color="text.secondary" variant="h6">
            Track your investments and asset allocation
          </Typography>
        </Box>

      {/* Portfolio Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: '16px', p: 2, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: '12px', 
                  bgcolor: 'rgba(59, 130, 246, 0.1)',
                  mr: 2 
                }}>
                  <AccountBalanceWalletIcon sx={{ color: '#3b82f6' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Total Portfolio
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                ₹78,24,460
              </Typography>
              <Typography variant="body2" color="#10b981" sx={{ mt: 1 }}>
                +8.4% this month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: '16px', p: 2, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: '12px', 
                  bgcolor: 'rgba(16, 185, 129, 0.1)',
                  mr: 2 
                }}>
                  <TrendingUpIcon sx={{ color: '#10b981' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Total Returns
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                ₹12,45,789
              </Typography>
              <Typography variant="body2" color="#10b981" sx={{ mt: 1 }}>
                18.9% overall return
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: '16px', p: 2, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: '12px', 
                  bgcolor: 'rgba(139, 92, 246, 0.1)',
                  mr: 2 
                }}>
                  <ShowChartIcon sx={{ color: '#8b5cf6' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Active Investments
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                24
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Across 12 categories
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: '16px', p: 2, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: '12px', 
                  bgcolor: 'rgba(245, 158, 11, 0.1)',
                  mr: 2 
                }}>
                  <PieChartIcon sx={{ color: '#f59e0b' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Risk Score
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                7.2
              </Typography>
              <Typography variant="body2" color="#f59e0b" sx={{ mt: 1 }}>
                Moderate Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Asset Allocation Breakdown */}
      <Paper sx={{ borderRadius: '16px', p: 4 }}>
        <Typography variant="h5" fontWeight={600} color="#1f2937" mb={3}>
          Asset Allocation Breakdown
        </Typography>
        
        <Grid container spacing={4}>
          {portfolioData.map((asset, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {asset.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {asset.percentage}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight={700}>
                    {asset.value}
                  </Typography>
                  <Typography variant="body2" color="#10b981">
                    {asset.growth}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={asset.percentage}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: asset.color,
                      borderRadius: 4,
                    }
                  }}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>
      </Box>
    </Box>
  );
}

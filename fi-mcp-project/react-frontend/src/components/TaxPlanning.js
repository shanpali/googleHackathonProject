import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from '@mui/material';
import ReceiptIcon from '@mui/icons-material/Receipt';
import SavingsIcon from '@mui/icons-material/Savings';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import PageHeader from './PageHeader';

export default function TaxPlanning() {
  const taxSavingOptions = [
    { name: 'ELSS Mutual Funds', limit: '₹1,50,000', invested: '₹1,20,000', remaining: '₹30,000', returns: '15-18%' },
    { name: 'PPF', limit: '₹1,50,000', invested: '₹1,50,000', remaining: '₹0', returns: '7.1%' },
    { name: 'NSC', limit: '₹1,50,000', invested: '₹50,000', remaining: '₹1,00,000', returns: '6.8%' },
    { name: 'Tax Saving FD', limit: '₹1,50,000', invested: '₹25,000', remaining: '₹1,25,000', returns: '5.5%' }
  ];

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f7f9fb', minHeight: '100vh' }}>
      <PageHeader title="Tax Planning" />
      
      <Box sx={{ p: 4 }}>
        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight={700} color="#1f2937" mb={1}>
            Tax Planning
          </Typography>
          <Typography color="text.secondary" variant="h6">
            Optimize your tax savings and plan better
          </Typography>
        </Box>

      {/* Tax Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: '16px', p: 2, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: '12px', 
                  bgcolor: 'rgba(239, 68, 68, 0.1)',
                  mr: 2 
                }}>
                  <ReceiptIcon sx={{ color: '#ef4444' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Tax Liability
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                ₹2,45,600
              </Typography>
              <Typography variant="body2" color="#ef4444" sx={{ mt: 1 }}>
                For FY 2023-24
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
                  <SavingsIcon sx={{ color: '#10b981' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Tax Saved
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                ₹1,89,450
              </Typography>
              <Typography variant="body2" color="#10b981" sx={{ mt: 1 }}>
                Through 80C investments
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
                  <TrendingDownIcon sx={{ color: '#f59e0b' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Potential Savings
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                ₹78,650
              </Typography>
              <Typography variant="body2" color="#f59e0b" sx={{ mt: 1 }}>
                Additional opportunities
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
                  bgcolor: 'rgba(59, 130, 246, 0.1)',
                  mr: 2 
                }}>
                  <AccountBalanceIcon sx={{ color: '#3b82f6' }} />
                </Box>
                <Typography variant="h6" color="text.secondary">
                  Effective Tax Rate
                </Typography>
              </Box>
              <Typography variant="h3" fontWeight={700} color="#1f2937">
                18.5%
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                After optimizations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tax Saving Investments */}
      <Paper sx={{ borderRadius: '16px', p: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" fontWeight={600} color="#1f2937">
            Section 80C Investments
          </Typography>
          <Chip 
            label="₹6,00,000 limit" 
            color="primary" 
            variant="outlined"
            sx={{ fontWeight: 600 }}
          />
        </Box>
        
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><Typography fontWeight={600}>Investment Type</Typography></TableCell>
              <TableCell><Typography fontWeight={600}>Annual Limit</Typography></TableCell>
              <TableCell><Typography fontWeight={600}>Invested</Typography></TableCell>
              <TableCell><Typography fontWeight={600}>Remaining</Typography></TableCell>
              <TableCell><Typography fontWeight={600}>Expected Returns</Typography></TableCell>
              <TableCell><Typography fontWeight={600}>Status</Typography></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {taxSavingOptions.map((option, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  <Typography fontWeight={600}>{option.name}</Typography>
                </TableCell>
                <TableCell>{option.limit}</TableCell>
                <TableCell>{option.invested}</TableCell>
                <TableCell>
                  <Typography color={option.remaining === '₹0' ? 'text.secondary' : '#f59e0b'}>
                    {option.remaining}
                  </Typography>
                </TableCell>
                <TableCell>{option.returns}</TableCell>
                <TableCell>
                  <Chip
                    label={option.remaining === '₹0' ? 'Maxed Out' : 'Available'}
                    color={option.remaining === '₹0' ? 'success' : 'warning'}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      {/* Recommendations */}
      <Paper sx={{ borderRadius: '16px', p: 4 }}>
        <Typography variant="h5" fontWeight={600} color="#1f2937" mb={3}>
          Tax Optimization Recommendations
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: '12px', p: 3, bgcolor: 'rgba(16, 185, 129, 0.05)' }}>
              <Typography variant="h6" fontWeight={600} color="#10b981" mb={2}>
                High Priority
              </Typography>
              <Typography variant="body1" mb={2}>
                Invest remaining ₹30,000 in ELSS funds before March 31st
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Potential tax saving: ₹9,300
              </Typography>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: '12px', p: 3, bgcolor: 'rgba(245, 158, 11, 0.05)' }}>
              <Typography variant="h6" fontWeight={600} color="#f59e0b" mb={2}>
                Medium Priority
              </Typography>
              <Typography variant="body1" mb={2}>
                Consider NSC investment for stable returns
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Potential tax saving: ₹31,000
              </Typography>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: '12px', p: 3, bgcolor: 'rgba(59, 130, 246, 0.05)' }}>
              <Typography variant="h6" fontWeight={600} color="#3b82f6" mb={2}>
                Long Term
              </Typography>
              <Typography variant="body1" mb={2}>
                Plan for Section 80D health insurance premium
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Additional deduction up to ₹25,000
              </Typography>
            </Card>
          </Grid>
        </Grid>
      </Paper>
      </Box>
    </Box>
  );
}

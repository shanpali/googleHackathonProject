import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Chip, 
  LinearProgress, 
  List, 
  ListItem, 
  ListItemText, 
  CircularProgress, 
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button
} from '@mui/material';
import ReceiptIcon from '@mui/icons-material/Receipt';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import axios from 'axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tax-tabpanel-${index}`}
      aria-labelledby={`tax-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function TaxPlanning() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/financial-data', { withCredentials: true });
        setData(res.data);
      } catch (err) {
        setError('Could not load tax planning data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;
  if (!data) return <Alert severity="info" sx={{ m: 2 }}>No tax planning data available.</Alert>;

  // Parse net worth data
  const netWorthData = data.fetch_net_worth?.netWorthResponse;
  const netWorth = netWorthData?.totalNetWorthValue?.units || 0;
  
  // Parse mutual fund data
  const mfSchemeAnalytics = data.fetch_net_worth?.mfSchemeAnalytics?.schemeAnalytics || [];
  const mfData = mfSchemeAnalytics.map(scheme => ({
    fundName: scheme.schemeDetail?.nameData?.longName || 'Unknown Fund',
    currentValue: scheme.enrichedAnalytics?.analytics?.schemeDetails?.currentValue?.units || 0,
    investedAmount: scheme.enrichedAnalytics?.analytics?.schemeDetails?.investedValue?.units || 0
  }));
  
  // Parse EPF data
  const epfData = data.fetch_epf_details?.epfDetails || {};
  const bankData = data.fetch_bank_transactions?.bankTransactions || [];

  // Calculate tax-saving opportunities
  const elssInvestments = mfData.filter(fund => fund.fundName?.includes('ELSS') || fund.fundName?.includes('Tax Saver')).reduce((sum, fund) => sum + (fund.currentValue || 0), 0);
  const epfContribution = epfData.employeeContribution || 0;
  const npsContribution = 0; // Assuming no NPS for now
  const hraDeduction = 0; // Would need salary data
  const homeLoanInterest = 0; // Would need loan data
  const medicalInsurance = 0; // Would need insurance data

  const currentDeductions = elssInvestments + epfContribution + npsContribution + hraDeduction + homeLoanInterest + medicalInsurance;
  const maxDeductions = 150000; // Section 80C limit
  const remainingDeductions = Math.max(0, maxDeductions - currentDeductions);

  const taxSlabs = [
    { slab: '0 - 3,00,000', rate: '0%', tax: 0 },
    { slab: '3,00,001 - 6,00,000', rate: '5%', tax: 15000 },
    { slab: '6,00,001 - 9,00,000', rate: '10%', tax: 30000 },
    { slab: '9,00,001 - 12,00,000', rate: '15%', tax: 45000 },
    { slab: '12,00,001 - 15,00,000', rate: '20%', tax: 60000 },
    { slab: 'Above 15,00,000', rate: '30%', tax: 0 }
  ];

  const taxSavingOpportunities = [
    {
      category: 'ELSS Funds',
      current: elssInvestments,
      potential: Math.min(remainingDeductions, 100000),
      description: 'Equity Linked Savings Scheme for tax deduction under Section 80C',
      deadline: 'March 31, 2024',
      status: elssInvestments > 0 ? 'active' : 'inactive'
    },
    {
      category: 'EPF Contribution',
      current: epfContribution,
      potential: 0,
      description: 'Employee Provident Fund contribution (automatic deduction)',
      deadline: 'Ongoing',
      status: 'active'
    },
    {
      category: 'NPS Contribution',
      current: npsContribution,
      potential: Math.min(remainingDeductions, 50000),
      description: 'National Pension System for additional tax deduction',
      deadline: 'March 31, 2024',
      status: 'inactive'
    },
    {
      category: 'Health Insurance',
      current: medicalInsurance,
      potential: 25000,
      description: 'Health insurance premium for self and family',
      deadline: 'March 31, 2024',
      status: 'inactive'
    }
  ];

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Typography variant="h4" fontWeight={700} mb={3} color="primary">
        💰 Tax Planning & Optimization
      </Typography>

      {/* Tax Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Current Deductions</Typography>
              <Typography variant="h4" fontWeight={700}>₹{currentDeductions.toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Section 80C & others</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #388e3c 0%, #66bb6a 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Remaining Limit</Typography>
              <Typography variant="h4" fontWeight={700}>₹{remainingDeductions.toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Available for investment</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #f57c00 0%, #ff9800 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Potential Savings</Typography>
              <Typography variant="h4" fontWeight={700}>₹{(remainingDeductions * 0.3).toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>At 30% tax rate</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #7b1fa2 0%, #ab47bc 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Utilization</Typography>
              <Typography variant="h4" fontWeight={700}>{((currentDeductions / maxDeductions) * 100).toFixed(1)}%</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Of Section 80C limit</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Deduction Progress */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={700} mb={3}>Section 80C Deduction Progress</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="body1" sx={{ flexGrow: 1 }}>Current Deductions</Typography>
            <Typography variant="body1" fontWeight={600}>₹{currentDeductions.toLocaleString()}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
              of ₹{maxDeductions.toLocaleString()}
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(currentDeductions / maxDeductions) * 100} 
            sx={{ height: 12, borderRadius: 6, bgcolor: '#f0f0f0' }}
          />
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">₹0</Typography>
            <Typography variant="caption" color="text.secondary">₹1,50,000</Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Tax Saving Opportunities */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={700} mb={3}>Tax Saving Opportunities</Typography>
          <Grid container spacing={2}>
            {taxSavingOpportunities.map((opportunity, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ 
                  borderRadius: 3, 
                  border: `2px solid ${opportunity.status === 'active' ? '#4caf50' : '#ff9800'}`,
                  bgcolor: opportunity.status === 'active' ? '#f1f8e9' : '#fff3e0'
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {opportunity.status === 'active' ? 
                        <CheckCircleIcon color="success" sx={{ mr: 1 }} /> : 
                        <WarningIcon color="warning" sx={{ mr: 1 }} />
                      }
                      <Typography variant="h6" fontWeight={700}>{opportunity.category}</Typography>
                      <Chip 
                        label={opportunity.status === 'active' ? 'Active' : 'Inactive'} 
                        color={opportunity.status === 'active' ? 'success' : 'warning'} 
                        size="small" 
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {opportunity.description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Current Investment:</Typography>
                      <Typography variant="body2" fontWeight={600}>₹{opportunity.current.toLocaleString()}</Typography>
                    </Box>
                    {opportunity.potential > 0 && (
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Potential Investment:</Typography>
                        <Typography variant="body2" fontWeight={600} color="success.main">₹{opportunity.potential.toLocaleString()}</Typography>
                      </Box>
                    )}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="body2">Deadline:</Typography>
                      <Typography variant="body2" fontWeight={600}>{opportunity.deadline}</Typography>
                    </Box>
                    {opportunity.potential > 0 && (
                      <Button 
                        variant="contained" 
                        color="primary" 
                        size="small" 
                        startIcon={<SavingsIcon />}
                        fullWidth
                      >
                        Invest Now
                      </Button>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Detailed Tabs */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Tax Slabs" />
            <Tab label="Deductions" />
            <Tab label="Tax Calculator" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Income Slab</strong></TableCell>
                    <TableCell><strong>Tax Rate</strong></TableCell>
                    <TableCell><strong>Tax Amount</strong></TableCell>
                    <TableCell><strong>Cumulative Tax</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {taxSlabs.map((slab, index) => (
                    <TableRow key={index}>
                      <TableCell>{slab.slab}</TableCell>
                      <TableCell>{slab.rate}</TableCell>
                      <TableCell>₹{slab.tax.toLocaleString()}</TableCell>
                      <TableCell>₹{taxSlabs.slice(0, index + 1).reduce((sum, s) => sum + s.tax, 0).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Current Deductions</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="ELSS Investments" 
                          secondary={`₹${elssInvestments.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="EPF Contribution" 
                          secondary={`₹${epfContribution.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="NPS Contribution" 
                          secondary={`₹${npsContribution.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="HRA Deduction" 
                          secondary={`₹${hraDeduction.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Home Loan Interest" 
                          secondary={`₹${homeLoanInterest.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Health Insurance" 
                          secondary={`₹${medicalInsurance.toLocaleString()}`}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e8f5e8' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Recommendations</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Invest in ELSS Funds" 
                          secondary={`₹${Math.min(remainingDeductions, 100000).toLocaleString()} more`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Consider NPS" 
                          secondary="Additional ₹50,000 deduction"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Health Insurance" 
                          secondary="₹25,000 premium deduction"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Home Loan" 
                          secondary="₹2,00,000 interest deduction"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Card sx={{ borderRadius: 3, bgcolor: '#f8f9fa' }}>
              <CardContent>
                <Typography variant="h6" fontWeight={700} mb={3}>Tax Calculator</Typography>
                <Typography variant="body1" color="text.secondary" mb={3}>
                  Calculate your tax liability and potential savings based on your current investments and income.
                </Typography>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h5" color="primary" fontWeight={700}>
                    Tax Calculator Coming Soon
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    Interactive tax calculator with real-time calculations
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
} 
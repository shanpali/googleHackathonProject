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
  Paper
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import axios from 'axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`portfolio-tabpanel-${index}`}
      aria-labelledby={`portfolio-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Portfolio() {
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
        setError('Could not load portfolio data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;
  if (!data) return <Alert severity="info" sx={{ m: 2 }}>No portfolio data available.</Alert>;

  // Parse net worth data
  const netWorthData = data.fetch_net_worth?.netWorthResponse;
  const netWorth = Number(netWorthData?.totalNetWorthValue?.units) || 0;
  
  // Parse mutual fund data
  const mfSchemeAnalytics = data.fetch_net_worth?.mfSchemeAnalytics?.schemeAnalytics || [];
  const mfData = mfSchemeAnalytics.map(scheme => ({
    fundName: scheme.schemeDetail?.nameData?.longName || 'Unknown Fund',
    currentValue: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.currentValue?.units) || 0,
    investedAmount: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.investedValue?.units) || 0,
    units: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.units) || 0,
    nav: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.navValue?.units) || 0,
    xirr: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.XIRR) || 0
  }));
  
  // Parse stock data
  const stockData = (data.fetch_stock_transactions?.stockTransactions || []).map(stock => ({
    ...stock,
    currentPrice: Number(stock.currentPrice) || 0,
    averagePrice: Number(stock.averagePrice) || 0,
    currentValue: Number(stock.currentValue) || 0,
    investedAmount: Number(stock.investedAmount) || 0,
    quantity: Number(stock.quantity) || 0
  }));
  
  // Parse EPF data
  const epfData = {
    currentBalance: Number(data.fetch_epf_details?.epfDetails?.currentBalance) || 0,
    employeeContribution: Number(data.fetch_epf_details?.epfDetails?.employeeContribution) || 0,
    employerContribution: Number(data.fetch_epf_details?.epfDetails?.employerContribution) || 0,
    interestEarned: Number(data.fetch_epf_details?.epfDetails?.interestEarned) || 0,
    uanNumber: data.fetch_epf_details?.epfDetails?.uanNumber || 'N/A',
    memberId: data.fetch_epf_details?.epfDetails?.memberId || 'N/A'
  };

  const totalMFValue = mfData.reduce((sum, fund) => sum + (fund.currentValue || 0), 0);
  const totalStockValue = stockData.reduce((sum, stock) => sum + (stock.currentValue || 0), 0);
  const epfValue = epfData.currentBalance || 0;

  const portfolioBreakdown = [
    { name: 'Mutual Funds', value: totalMFValue, percentage: (totalMFValue / netWorth) * 100, color: '#1976d2' },
    { name: 'Stocks & ETFs', value: totalStockValue, percentage: (totalStockValue / netWorth) * 100, color: '#388e3c' },
    { name: 'EPF', value: epfValue, percentage: (epfValue / netWorth) * 100, color: '#f57c00' },
    { name: 'Savings', value: netWorth - totalMFValue - totalStockValue - epfValue, percentage: ((netWorth - totalMFValue - totalStockValue - epfValue) / netWorth) * 100, color: '#7b1fa2' }
  ];

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Typography variant="h4" fontWeight={700} mb={3} color="primary">
        📊 Investment Portfolio
      </Typography>

      {/* Portfolio Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Total Portfolio Value</Typography>
              <Typography variant="h4" fontWeight={700}>₹{netWorth.toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>As of today</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #388e3c 0%, #66bb6a 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Total Investments</Typography>
              <Typography variant="h4" fontWeight={700}>₹{(totalMFValue + totalStockValue + epfValue).toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Mutual Funds + Stocks + EPF</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #f57c00 0%, #ff9800 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Liquid Savings</Typography>
              <Typography variant="h4" fontWeight={700}>₹{(netWorth - totalMFValue - totalStockValue - epfValue).toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Available for emergencies</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Portfolio Breakdown */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={700} mb={3}>Portfolio Allocation</Typography>
          <Grid container spacing={2}>
            {portfolioBreakdown.map((item, index) => (
              <Grid item xs={12} key={index}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: item.color, mr: 2 }} />
                  <Typography variant="body1" sx={{ flexGrow: 1 }}>{item.name}</Typography>
                  <Typography variant="body1" fontWeight={600}>₹{item.value.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    ({item.percentage.toFixed(1)}%)
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={item.percentage} 
                  sx={{ height: 8, borderRadius: 4, bgcolor: '#f0f0f0' }}
                />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Detailed Tabs */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Mutual Funds" />
            <Tab label="Stocks & ETFs" />
            <Tab label="EPF Details" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Fund Name</strong></TableCell>
                    <TableCell><strong>Current Value</strong></TableCell>
                    <TableCell><strong>Units</strong></TableCell>
                    <TableCell><strong>NAV</strong></TableCell>
                    <TableCell><strong>Return</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mfData.map((fund, index) => {
                    const returnPercent = ((fund.currentValue - fund.investedAmount) / fund.investedAmount) * 100;
                    const navValue = Number(fund.nav);
                    const unitsValue = Number(fund.units);
                    return (
                      <TableRow key={index}>
                        <TableCell>{fund.fundName}</TableCell>
                        <TableCell>₹{fund.currentValue?.toLocaleString()}</TableCell>
                        <TableCell>{typeof unitsValue === 'number' && !isNaN(unitsValue) ? unitsValue.toFixed(2) : '—'}</TableCell>
                        <TableCell>₹{typeof navValue === 'number' && !isNaN(navValue) ? navValue.toFixed(2) : '—'}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {returnPercent >= 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />}
                            <Typography color={returnPercent >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                              {isFinite(returnPercent) ? returnPercent.toFixed(2) : '—'}%
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Stock/ETF</strong></TableCell>
                    <TableCell><strong>Quantity</strong></TableCell>
                    <TableCell><strong>Current Price</strong></TableCell>
                    <TableCell><strong>Current Value</strong></TableCell>
                    <TableCell><strong>Return</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stockData.map((stock, index) => {
                    const returnPercent = ((stock.currentPrice - stock.averagePrice) / stock.averagePrice) * 100;
                    return (
                      <TableRow key={index}>
                        <TableCell>{stock.stockName}</TableCell>
                        <TableCell>{stock.quantity}</TableCell>
                        <TableCell>₹{stock.currentPrice?.toFixed(2)}</TableCell>
                        <TableCell>₹{stock.currentValue?.toLocaleString()}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {returnPercent >= 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />}
                            <Typography color={returnPercent >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                              {returnPercent.toFixed(2)}%
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>EPF Summary</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Current Balance" 
                          secondary={`₹${epfData.currentBalance?.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Employee Contribution" 
                          secondary={`₹${epfData.employeeContribution?.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Employer Contribution" 
                          secondary={`₹${epfData.employerContribution?.toLocaleString()}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Interest Earned" 
                          secondary={`₹${epfData.interestEarned?.toLocaleString()}`}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e3f2fd' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>EPF Details</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="UAN Number" 
                          secondary={epfData.uanNumber || 'N/A'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Member ID" 
                          secondary={epfData.memberId || 'N/A'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Establishment Name" 
                          secondary={epfData.establishmentName || 'N/A'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Last Updated" 
                          secondary={epfData.lastUpdated || 'N/A'}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
} 
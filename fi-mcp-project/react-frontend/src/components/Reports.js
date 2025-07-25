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
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import DownloadIcon from '@mui/icons-material/Download';
import PrintIcon from '@mui/icons-material/Print';
import axios from 'axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reports-tabpanel-${index}`}
      aria-labelledby={`reports-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Reports() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [reportPeriod, setReportPeriod] = useState('monthly');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/financial-data', { withCredentials: true });
        setData(res.data);
      } catch (err) {
        setError('Could not load reports data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;
  if (!data) return <Alert severity="info" sx={{ m: 2 }}>No reports data available.</Alert>;

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
  const stockData = data.fetch_stock_transactions?.stockTransactions || [];
  
  // Parse EPF data
  const epfData = data.fetch_epf_details?.epfDetails || {};
  
  // Parse bank data
  const bankData = data.fetch_bank_transactions?.bankTransactions || [];
  
  // Parse credit data
  const creditData = data.fetch_credit_report?.creditReport || {};

  // Calculate performance metrics
  const totalMFValue = mfData.reduce((sum, fund) => sum + (fund.currentValue || 0), 0);
  const totalMFInvested = mfData.reduce((sum, fund) => sum + (fund.investedAmount || 0), 0);
  const mfReturns = totalMFValue - totalMFInvested;
  const mfReturnPercent = totalMFInvested > 0 ? (mfReturns / totalMFInvested) * 100 : 0;

  const totalStockValue = stockData.reduce((sum, stock) => sum + (stock.currentValue || 0), 0);
  const totalStockInvested = stockData.reduce((sum, stock) => sum + (stock.investedAmount || 0), 0);
  const stockReturns = totalStockValue - totalStockInvested;
  const stockReturnPercent = totalStockInvested > 0 ? (stockReturns / totalStockInvested) * 100 : 0;

  // Mock monthly data for trends
  const monthlyData = [
    { month: 'Jan', netWorth: 1150000, investments: 850000, savings: 300000 },
    { month: 'Feb', netWorth: 1180000, investments: 870000, savings: 310000 },
    { month: 'Mar', netWorth: 1220000, investments: 890000, savings: 330000 },
    { month: 'Apr', netWorth: 1250000, investments: 910000, savings: 340000 },
    { month: 'May', netWorth: 1297000, investments: 930000, savings: 367000 },
  ];

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleDownloadReport = (type) => {
    // Mock download functionality
    console.log(`Downloading ${type} report for ${reportPeriod} period`);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={700} color="primary">
          📊 Financial Reports & Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Period</InputLabel>
            <Select
              value={reportPeriod}
              label="Period"
              onChange={(e) => setReportPeriod(e.target.value)}
            >
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
              <MenuItem value="quarterly">Quarterly</MenuItem>
              <MenuItem value="yearly">Yearly</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => handleDownloadReport('comprehensive')}
          >
            Download Report
          </Button>
          <Button
            variant="outlined"
            startIcon={<PrintIcon />}
          >
            Print
          </Button>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Total Net Worth</Typography>
              <Typography variant="h4" fontWeight={700}>₹{(netWorth / 100000).toFixed(1)}L</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Current value</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #388e3c 0%, #66bb6a 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Investment Returns</Typography>
              <Typography variant="h4" fontWeight={700}>₹{(mfReturns + stockReturns).toLocaleString()}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Total gains</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #f57c00 0%, #ff9800 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Return Rate</Typography>
              <Typography variant="h4" fontWeight={700}>{((mfReturnPercent + stockReturnPercent) / 2).toFixed(1)}%</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Average return</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #7b1fa2 0%, #ab47bc 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Credit Score</Typography>
              <Typography variant="h4" fontWeight={700}>{creditData.creditScore || 746}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Experian score</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Summary */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={700} mb={3}>Investment Performance Summary</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                <CardContent>
                  <Typography variant="h6" fontWeight={700} mb={2}>Mutual Funds</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Current Value:</Typography>
                    <Typography variant="body2" fontWeight={600}>₹{totalMFValue.toLocaleString()}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Invested Amount:</Typography>
                    <Typography variant="body2" fontWeight={600}>₹{totalMFInvested.toLocaleString()}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Returns:</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {mfReturns >= 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />}
                      <Typography 
                        variant="body2" 
                        fontWeight={600} 
                        color={mfReturns >= 0 ? 'success.main' : 'error.main'}
                      >
                        ₹{mfReturns.toLocaleString()} ({mfReturnPercent.toFixed(2)}%)
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 3, bgcolor: '#e3f2fd' }}>
                <CardContent>
                  <Typography variant="h6" fontWeight={700} mb={2}>Stocks & ETFs</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Current Value:</Typography>
                    <Typography variant="body2" fontWeight={600}>₹{totalStockValue.toLocaleString()}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Invested Amount:</Typography>
                    <Typography variant="body2" fontWeight={600}>₹{totalStockInvested.toLocaleString()}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Returns:</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {stockReturns >= 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />}
                      <Typography 
                        variant="body2" 
                        fontWeight={600} 
                        color={stockReturns >= 0 ? 'success.main' : 'error.main'}
                      >
                        ₹{stockReturns.toLocaleString()} ({stockReturnPercent.toFixed(2)}%)
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Detailed Tabs */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Performance" />
            <Tab label="Trends" />
            <Tab label="Credit Report" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Investment Type</strong></TableCell>
                    <TableCell><strong>Current Value</strong></TableCell>
                    <TableCell><strong>Invested Amount</strong></TableCell>
                    <TableCell><strong>Returns</strong></TableCell>
                    <TableCell><strong>Return %</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mfData.map((fund, index) => {
                    const returns = (fund.currentValue || 0) - (fund.investedAmount || 0);
                    const returnPercent = fund.investedAmount > 0 ? (returns / fund.investedAmount) * 100 : 0;
                    return (
                      <TableRow key={index}>
                        <TableCell>{fund.fundName}</TableCell>
                        <TableCell>₹{fund.currentValue?.toLocaleString()}</TableCell>
                        <TableCell>₹{fund.investedAmount?.toLocaleString()}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {returns >= 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />}
                            <Typography color={returns >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                              ₹{returns.toLocaleString()}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography color={returnPercent >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                            {returnPercent.toFixed(2)}%
                          </Typography>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                  {stockData.map((stock, index) => {
                    const returns = (stock.currentValue || 0) - (stock.investedAmount || 0);
                    const returnPercent = stock.investedAmount > 0 ? (returns / stock.investedAmount) * 100 : 0;
                    return (
                      <TableRow key={`stock-${index}`}>
                        <TableCell>{stock.stockName}</TableCell>
                        <TableCell>₹{stock.currentValue?.toLocaleString()}</TableCell>
                        <TableCell>₹{stock.investedAmount?.toLocaleString()}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {returns >= 0 ? <TrendingUpIcon color="success" /> : <TrendingDownIcon color="error" />}
                            <Typography color={returns >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                              ₹{returns.toLocaleString()}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography color={returnPercent >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                            {returnPercent.toFixed(2)}%
                          </Typography>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Net Worth Trend</Typography>
                    <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Month</strong></TableCell>
                            <TableCell><strong>Net Worth</strong></TableCell>
                            <TableCell><strong>Growth</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {monthlyData.map((month, index) => {
                            const prevMonth = index > 0 ? monthlyData[index - 1].netWorth : month.netWorth;
                            const growth = ((month.netWorth - prevMonth) / prevMonth) * 100;
                            return (
                              <TableRow key={month.month}>
                                <TableCell>{month.month}</TableCell>
                                <TableCell>₹{(month.netWorth / 100000).toFixed(1)}L</TableCell>
                                <TableCell>
                                  <Typography color={growth >= 0 ? 'success.main' : 'error.main'} fontWeight={600}>
                                    {growth >= 0 ? '+' : ''}{growth.toFixed(1)}%
                                  </Typography>
                                </TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e3f2fd' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Asset Allocation Trend</Typography>
                    <List dense>
                      {monthlyData.slice(-3).map((month, index) => (
                        <ListItem key={month.month}>
                          <ListItemText 
                            primary={month.month} 
                            secondary={`Investments: ₹${(month.investments / 100000).toFixed(1)}L | Savings: ₹${(month.savings / 100000).toFixed(1)}L`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Credit Score Summary</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Experian Score" 
                          secondary={creditData.creditScore || 746}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Score Range" 
                          secondary="Good (700-749)"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Payment History" 
                          secondary="On time payments"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Credit Utilization" 
                          secondary="35% (Good)"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Credit Age" 
                          secondary="8 years (Good)"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e8f5e8' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Credit Recommendations</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="✅ Good Credit Score" 
                          secondary="Your score is in the good range"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="💳 Credit Utilization" 
                          secondary="Keep utilization below 30%"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="📅 Payment History" 
                          secondary="Continue making on-time payments"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="🔍 Credit Mix" 
                          secondary="Consider diversifying credit types"
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
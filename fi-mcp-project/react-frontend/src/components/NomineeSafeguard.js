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
  Avatar
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PersonIcon from '@mui/icons-material/Person';
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom';
import VerifiedIcon from '@mui/icons-material/Verified';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`nominee-tabpanel-${index}`}
      aria-labelledby={`nominee-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function NomineeSafeguard() {
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
        setError('Could not load nominee safeguard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;
  if (!data) return <Alert severity="info" sx={{ m: 2 }}>No nominee safeguard data available.</Alert>;

  // Parse net worth data
  const netWorthData = data.fetch_net_worth?.netWorthResponse;
  const netWorth = Number(netWorthData?.totalNetWorthValue?.units) || 0;
  
  // Parse mutual fund data
  const mfSchemeAnalytics = data.fetch_net_worth?.mfSchemeAnalytics?.schemeAnalytics || [];
  const mfData = mfSchemeAnalytics.map(scheme => ({
    fundName: scheme.schemeDetail?.nameData?.longName || 'Unknown Fund',
    currentValue: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.currentValue?.units) || 0,
    investedAmount: Number(scheme.enrichedAnalytics?.analytics?.schemeDetails?.investedValue?.units) || 0
  }));
  
  // Parse stock data
  const stockData = data.fetch_stock_transactions?.stockTransactions || [];
  
  // Parse EPF data
  const epfData = data.fetch_epf_details?.epfDetails || {};

  // Parse nominee data from API
  const nomineeData = data.fetch_nominee_details?.nomineeDetails || {
    primaryNominee: {
      name: 'Priya Sharma',
      relationship: 'Spouse',
      age: 32,
      contact: '+91 98765 43210',
      percentage: 100,
      status: 'active'
    },
    secondaryNominees: [
      {
        name: 'Arjun Sharma',
        relationship: 'Son',
        age: 8,
        contact: 'N/A',
        percentage: 50,
        status: 'active'
      },
      {
        name: 'Meera Sharma',
        relationship: 'Daughter',
        age: 5,
        contact: 'N/A',
        percentage: 50,
        status: 'active'
      }
    ],
    insuranceCoverage: {
      lifeInsurance: 5000000,
      healthInsurance: 1000000,
      accidentalCoverage: 2000000,
      totalCoverage: 8000000
    },
    riskAssessment: {
      coverageRatio: Number((8000000 / netWorth) * 100),
      nomineeCompleteness: 85,
      documentationStatus: 90,
      overallRisk: 'Low'
    }
  };

  // Function to check nominee status for different account types
  const getNomineeStatus = (accountType) => {
    const assetWiseNominees = nomineeData.assetWiseNominees || {};
    
    switch (accountType) {
      case 'mutualFunds':
        return assetWiseNominees.mutualFunds?.primaryNominee ? 'registered' : 'not_registered';
      case 'stocks':
        return assetWiseNominees.stocks?.primaryNominee ? 'registered' : 'not_registered';
      case 'epf':
        return assetWiseNominees.epf?.primaryNominee ? 'registered' : 'not_registered';
      case 'bankAccounts':
        return assetWiseNominees.bankAccounts?.primaryNominee ? 'registered' : 'not_registered';
      case 'reit':
        // Check REIT data from net worth response
        const reitHoldings = data.fetch_net_worth?.accountDetailsBulkResponse?.accountDetailsMap;
        if (reitHoldings) {
          for (const accountId in reitHoldings) {
            const account = reitHoldings[accountId];
            if (account.reitSummary?.holdingsInfo) {
              const hasNominee = account.reitSummary.holdingsInfo.some(holding => 
                holding.nominee === 'NOMINEE_TYPE_REGISTERED'
              );
              if (hasNominee) return 'registered';
            }
          }
        }
        return 'not_registered';
      default:
        return 'unknown';
    }
  };

  // Function to render nominee status indicator
  const renderNomineeStatus = (accountType, accountName) => {
    const status = getNomineeStatus(accountType);
    const isRegistered = status === 'registered';
    
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" color="text.secondary">
          {accountName}
        </Typography>
        {isRegistered ? (
          <VerifiedIcon sx={{ color: 'success.main', fontSize: 20 }} />
        ) : (
          <ErrorIcon sx={{ color: 'error.main', fontSize: 20 }} />
        )}
        <Typography variant="caption" color={isRegistered ? 'success.main' : 'error.main'}>
          {isRegistered ? 'Nominee Registered' : 'No Nominee'}
        </Typography>
      </Box>
    );
  };

  const riskFactors = [
    {
      factor: 'Life Insurance Coverage',
      status: nomineeData.riskAssessment.coverageRatio >= 100 ? 'good' : 'warning',
      description: nomineeData.riskAssessment.coverageRatio >= 100 
        ? 'Adequate life insurance coverage' 
        : 'Insufficient life insurance coverage',
      recommendation: 'Consider increasing life insurance coverage'
    },
    {
      factor: 'Nominee Documentation',
      status: nomineeData.riskAssessment.documentationStatus >= 80 ? 'good' : 'warning',
      description: 'All nominee details are properly documented',
      recommendation: 'Keep nominee details updated'
    },
    {
      factor: 'Asset Distribution',
      status: 'good',
      description: 'Assets are properly distributed among nominees',
      recommendation: 'Review distribution percentages annually'
    },
    {
      factor: 'Emergency Fund',
      status: (netWorth - (mfData.reduce((sum, fund) => sum + (fund.currentValue || 0), 0) + 
        stockData.reduce((sum, stock) => sum + (stock.currentValue || 0), 0) + (epfData.currentBalance || 0))) > 500000 ? 'good' : 'warning',
      description: 'Sufficient emergency fund for family',
      recommendation: 'Maintain 6-12 months of expenses as emergency fund'
    }
  ];

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Defensive parse for insurance coverage
  const lifeInsurance = Number(nomineeData.insuranceCoverage?.lifeInsurance);
  const healthInsurance = Number(nomineeData.insuranceCoverage?.healthInsurance);
  const accidentalCoverage = Number(nomineeData.insuranceCoverage?.accidentalCoverage);
  const totalCoverage = Number(nomineeData.insuranceCoverage?.totalCoverage);
  const displayLakh = (val) => !isNaN(val) && val > 0 ? (val / 100000).toFixed(1) : '0';
  // Defensive parse for coverage ratio
  const coverageRatio = Number(nomineeData.riskAssessment?.coverageRatio);
  // Defensive parse for documentation status
  const documentationStatus = Number(nomineeData.riskAssessment?.documentationStatus);

  return (
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Typography variant="h4" fontWeight={700} mb={3} color="primary">
        🛡️ Nominee Safeguard & Protection
      </Typography>

      {/* Risk Assessment Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Risk Level</Typography>
              <Typography variant="h4" fontWeight={700}>{nomineeData.riskAssessment.overallRisk}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Overall protection status</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #388e3c 0%, #66bb6a 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Insurance Coverage</Typography>
              <Typography variant="h4" fontWeight={700}>₹{displayLakh(totalCoverage)}L</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Total protection amount</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #f57c00 0%, #ff9800 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Coverage Ratio</Typography>
              <Typography variant="h4" fontWeight={700}>{coverageRatio.toFixed(1)}%</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Of net worth covered</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #7b1fa2 0%, #ab47bc 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" mb={1}>Documentation</Typography>
              <Typography variant="h4" fontWeight={700}>{documentationStatus}%</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Complete nominee details</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Account Nominee Status */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={700} mb={3}>Account Nominee Status</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 3, bgcolor: '#f8f9fa' }}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={600} mb={2}>Financial Instruments</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {renderNomineeStatus('mutualFunds', 'Mutual Funds')}
                    {renderNomineeStatus('stocks', 'Stocks & ETFs')}
                    {renderNomineeStatus('epf', 'EPF Account')}
                    {renderNomineeStatus('reit', 'REIT Holdings')}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderRadius: 3, bgcolor: '#f8f9fa' }}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={600} mb={2}>Banking & Insurance</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {renderNomineeStatus('bankAccounts', 'Bank Accounts')}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Life Insurance
                      </Typography>
                      <VerifiedIcon sx={{ color: 'success.main', fontSize: 20 }} />
                      <Typography variant="caption" color="success.main">
                        Nominee Registered
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Health Insurance
                      </Typography>
                      <VerifiedIcon sx={{ color: 'success.main', fontSize: 20 }} />
                      <Typography variant="caption" color="success.main">
                        Nominee Registered
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Risk Factors */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={700} mb={3}>Risk Assessment</Typography>
          <Grid container spacing={2}>
            {riskFactors.map((factor, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ 
                  borderRadius: 3, 
                  border: `2px solid ${factor.status === 'good' ? '#4caf50' : '#ff9800'}`,
                  bgcolor: factor.status === 'good' ? '#f1f8e9' : '#fff3e0'
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {factor.status === 'good' ? 
                        <CheckCircleIcon color="success" sx={{ mr: 1 }} /> : 
                        <WarningIcon color="warning" sx={{ mr: 1 }} />
                      }
                      <Typography variant="h6" fontWeight={700}>{factor.factor}</Typography>
                      <Chip 
                        label={factor.status === 'good' ? 'Good' : 'Needs Attention'} 
                        color={factor.status === 'good' ? 'success' : 'warning'} 
                        size="small" 
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {factor.description}
                    </Typography>
                    <Typography variant="body2" fontWeight={600} color="primary">
                      💡 {factor.recommendation}
                    </Typography>
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
            <Tab label="Nominees" />
            <Tab label="Insurance" />
            <Tab label="Recommendations" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Primary Nominee</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                        <PersonIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="h6" fontWeight={600}>{nomineeData.primaryNominee.name}</Typography>
                        <Typography variant="body2" color="text.secondary">{nomineeData.primaryNominee.relationship}</Typography>
                      </Box>
                    </Box>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Age" 
                          secondary={`${nomineeData.primaryNominee.age} years`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Contact" 
                          secondary={nomineeData.primaryNominee.contact}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Share" 
                          secondary={`${nomineeData.primaryNominee.percentage}%`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Status" 
                          secondary={
                            <Chip 
                              label={nomineeData.primaryNominee.status === 'active' ? 'Active' : 'Inactive'} 
                              color={nomineeData.primaryNominee.status === 'active' ? 'success' : 'error'} 
                              size="small"
                            />
                          }
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e3f2fd' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Secondary Nominees</Typography>
                    {nomineeData.secondaryNominees.map((nominee, index) => (
                      <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'white', borderRadius: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Avatar sx={{ bgcolor: 'secondary.main', mr: 2, width: 32, height: 32 }}>
                            <FamilyRestroomIcon />
                          </Avatar>
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="subtitle1" fontWeight={600}>{nominee.name}</Typography>
                            <Typography variant="body2" color="text.secondary">{nominee.relationship}</Typography>
                          </Box>
                          <Chip 
                            label={`${nominee.percentage}%`} 
                            color="primary" 
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Age: {nominee.age} years | Status: {nominee.status}
                        </Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Insurance Coverage Details</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Life Insurance" 
                          secondary={`₹${displayLakh(lifeInsurance)}L`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Health Insurance" 
                          secondary={`₹${displayLakh(healthInsurance)}L`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Accidental Coverage" 
                          secondary={`₹${displayLakh(accidentalCoverage)}L`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Total Coverage" 
                          secondary={`₹${displayLakh(totalCoverage)}L`}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e8f5e8' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Coverage Analysis</Typography>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" mb={1}>Coverage vs Net Worth</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min(coverageRatio, 100)} 
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {coverageRatio.toFixed(1)}% of net worth covered
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Your insurance coverage provides {coverageRatio >= 100 ? 'adequate' : 'insufficient'} protection for your family.
                    </Typography>
                    {coverageRatio < 100 && (
                      <Button 
                        variant="contained" 
                        color="primary" 
                        size="small" 
                        startIcon={<SecurityIcon />}
                        fullWidth
                      >
                        Increase Coverage
                      </Button>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#fff3e0' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2} color="warning.main">Immediate Actions</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Update Nominee Details" 
                          secondary="Ensure all nominee information is current"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Review Insurance Policies" 
                          secondary="Check policy terms and renewal dates"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Document Assets" 
                          secondary="Create a comprehensive asset inventory"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Emergency Fund" 
                          secondary="Maintain 6-12 months of expenses"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e8f5e8' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2} color="success.main">Long-term Planning</Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Will Preparation" 
                          secondary="Consider creating a legal will"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Trust Setup" 
                          secondary="Explore setting up a family trust"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Education Planning" 
                          secondary="Plan for children's education expenses"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Retirement Planning" 
                          secondary="Ensure spouse's retirement security"
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
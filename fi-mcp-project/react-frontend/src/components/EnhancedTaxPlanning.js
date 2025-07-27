import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Grid, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Button,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  Divider
} from '@mui/material';
import axios from 'axios';

const TAX_CATEGORIES = {
  'ELSS Funds': { color: '#1976d2', icon: '📈' },
  'EPF Contribution': { color: '#388e3c', icon: '🏦' },
  'NPS Contribution': { color: '#f57c00', icon: '👴' },
  'Health Insurance': { color: '#d32f2f', icon: '🏥' },
  'Home Loan Interest': { color: '#7b1fa2', icon: '🏠' },
  'Education Loan': { color: '#1565c0', icon: '🎓' },
  'Donations': { color: '#2e7d32', icon: '🤝' }
};

const ADK_TAX_ANALYSIS_TYPES = {
  'tax_planning': { icon: '💰', color: '#388e3c', label: 'Tax Optimization' },
  'portfolio_analysis': { icon: '📊', color: '#1976d2', label: 'Portfolio Analysis' },
  'investment_advice': { icon: '📈', color: '#f57c00', label: 'Investment Advice' }
};

export default function EnhancedTaxPlanning({ data }) {
  const [adkAnalysis, setAdkAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [taxData, setTaxData] = useState({
    elssInvestments: 0,
    epfContribution: 0,
    npsContribution: 0,
    medicalInsurance: 0,
    homeLoanInterest: 0,
    educationLoan: 0,
    donations: 0
  });

  // Calculate tax data from financial data
  useEffect(() => {
    if (data) {
      const newTaxData = {
        elssInvestments: calculateELSSInvestments(data),
        epfContribution: calculateEPFContribution(data),
        npsContribution: 0, // Usually not in standard data
        medicalInsurance: 0, // Usually not in standard data
        homeLoanInterest: 0, // Usually not in standard data
        educationLoan: 0, // Usually not in standard data
        donations: 0 // Usually not in standard data
      };
      setTaxData(newTaxData);
    }
  }, [data]);

  const calculateELSSInvestments = (data) => {
    // Calculate ELSS from mutual fund data
    const mfData = data.fetch_mf_transactions;
    if (mfData && mfData.mfTransactionsResponse) {
      return mfData.mfTransactionsResponse.transactions
        .filter(t => t.fundName && t.fundName.toLowerCase().includes('elss'))
        .reduce((sum, t) => sum + parseFloat(t.amount?.units || 0), 0);
    }
    return 0;
  };

  const calculateEPFContribution = (data) => {
    // Calculate EPF from EPF data
    const epfData = data.fetch_epf_details;
    if (epfData && epfData.epfDetailsResponse) {
      return parseFloat(epfData.epfDetailsResponse.balance?.units || 0);
    }
    return 0;
  };

  const getADKTaxAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/chatbot', { 
        message: "Analyze my tax situation and provide optimization recommendations. Include tax-saving opportunities, deductions I can claim, and strategies to reduce my tax liability. Focus on Indian tax laws and Section 80C, 80D, and other relevant sections." 
      }, { withCredentials: true });

      if (response.data && response.data.analysis_type) {
        setAdkAnalysis(response.data);
      } else {
        setError('Unable to get ADK tax analysis');
      }
    } catch (err) {
      setError('Failed to get tax analysis');
      console.error('ADK Tax Analysis Error:', err);
    }
    setLoading(false);
  };

  // Auto-trigger analysis when component mounts (only if user has interacted)
  useEffect(() => {
    // Only trigger ADK analysis if user has shown interest (e.g., clicked on tax planning)
    // For now, we'll disable auto-trigger to prevent unwanted API calls
    // if (Object.values(taxData).some(value => value > 0)) {
    //   getADKTaxAnalysis();
    // }
  }, [taxData]);

  const totalDeductions = Object.values(taxData).reduce((sum, value) => sum + value, 0);
  const maxDeduction = 150000; // Section 80C limit
  const remainingDeduction = Math.max(0, maxDeduction - totalDeductions);
  const utilizationPercentage = (totalDeductions / maxDeduction) * 100;

  const taxSavingOpportunities = [
    {
      category: 'ELSS Funds',
      current: taxData.elssInvestments,
      potential: Math.min(remainingDeduction, 100000),
      description: 'Equity Linked Savings Scheme for tax deduction under Section 80C',
      deadline: 'March 31, 2024',
      status: taxData.elssInvestments > 0 ? 'active' : 'inactive',
      priority: 'high'
    },
    {
      category: 'EPF Contribution',
      current: taxData.epfContribution,
      potential: 0,
      description: 'Employee Provident Fund contribution (automatic deduction)',
      deadline: 'Ongoing',
      status: 'active',
      priority: 'medium'
    },
    {
      category: 'NPS Contribution',
      current: taxData.npsContribution,
      potential: Math.min(remainingDeduction, 50000),
      description: 'National Pension System for additional tax deduction',
      deadline: 'March 31, 2024',
      status: 'inactive',
      priority: 'high'
    },
    {
      category: 'Health Insurance',
      current: taxData.medicalInsurance,
      potential: 25000,
      description: 'Health insurance premium for self and family',
      deadline: 'March 31, 2024',
      status: 'inactive',
      priority: 'medium'
    }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#d32f2f';
      case 'medium': return '#f57c00';
      case 'low': return '#388e3c';
      default: return '#757575';
    }
  };

  const getStatusColor = (status) => {
    return status === 'active' ? '#4caf50' : '#ff9800';
  };

  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={700}>Enhanced Tax Planning</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">Section 80C Utilization:</Typography>
            <Chip 
              label={`${Math.round(utilizationPercentage)}%`}
              size="small"
              sx={{ 
                backgroundColor: utilizationPercentage > 80 ? '#4caf50' : 
                              utilizationPercentage > 50 ? '#ff9800' : '#f44336',
                color: '#fff',
                fontWeight: 600
              }}
            />
            <Button
              variant="outlined"
              size="small"
              onClick={getADKTaxAnalysis}
              disabled={loading}
              sx={{ ml: 1 }}
            >
              {loading ? <CircularProgress size={16} /> : 'Get AI Analysis'}
            </Button>
          </Box>
        </Box>

        {/* ADK Tax Analysis Section */}
        {adkAnalysis && (
          <Alert 
            severity="info" 
            sx={{ mb: 2, borderRadius: 2 }}
            action={
              <Button 
                size="small" 
                onClick={getADKTaxAnalysis}
                disabled={loading}
                sx={{ color: '#388e3c' }}
              >
                {loading ? <CircularProgress size={16} /> : 'Refresh'}
              </Button>
            }
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <span style={{ fontSize: '18px' }}>
                {ADK_TAX_ANALYSIS_TYPES[adkAnalysis.analysis_type]?.icon || '💰'}
              </span>
              <Typography variant="subtitle2" fontWeight={600}>
                {ADK_TAX_ANALYSIS_TYPES[adkAnalysis.analysis_type]?.label || 'ADK Tax Analysis'}
              </Typography>
              <Chip 
                label={`${Math.round(adkAnalysis.confidence * 100)}% Confidence`}
                size="small"
                sx={{ 
                  backgroundColor: adkAnalysis.confidence > 0.7 ? '#4caf50' : '#ff9800',
                  color: '#fff',
                  fontSize: '10px'
                }}
              />
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              {adkAnalysis.response.substring(0, 200)}...
            </Typography>
            {adkAnalysis.recommendations && adkAnalysis.recommendations.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" fontWeight={600} color="#388e3c">
                  Tax Optimization Tips:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                  {adkAnalysis.recommendations.slice(0, 3).map((rec, idx) => (
                    <Chip 
                      key={idx}
                      label={rec.substring(0, 30)} 
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '10px' }}
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Tax Deduction Progress */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" fontWeight={600} mb={2}>
              Section 80C Utilization
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Current Deductions
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  ₹{totalDeductions.toLocaleString()}
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={Math.min(utilizationPercentage, 100)}
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: utilizationPercentage > 80 ? '#4caf50' : 
                                   utilizationPercentage > 50 ? '#ff9800' : '#f44336'
                  }
                }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  ₹0
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  ₹1,50,000
                </Typography>
              </Box>
            </Box>

            {/* Tax Savings Summary */}
            <Box sx={{ p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
              <Typography variant="subtitle2" fontWeight={600} mb={1}>
                Potential Tax Savings
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Current Savings:</Typography>
                <Typography variant="body2" fontWeight={600} color="#4caf50">
                  ₹{(totalDeductions * 0.3).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">Additional Savings:</Typography>
                <Typography variant="body2" fontWeight={600} color="#ff9800">
                  ₹{(remainingDeduction * 0.3).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Tax Saving Opportunities */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" fontWeight={600} mb={2}>
              Tax Saving Opportunities
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {taxSavingOpportunities.map((opportunity, idx) => (
                <Box 
                  key={idx}
                  sx={{ 
                    p: 2, 
                    border: `1px solid ${opportunity.status === 'active' ? '#4caf50' : '#e0e0e0'}`,
                    borderRadius: 2,
                    backgroundColor: opportunity.status === 'active' ? '#f1f8e9' : '#fff'
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <span style={{ fontSize: '16px' }}>
                        {TAX_CATEGORIES[opportunity.category]?.icon || '💰'}
                      </span>
                      <Typography variant="body2" fontWeight={600}>
                        {opportunity.category}
                      </Typography>
                    </Box>
                    <Chip 
                      label={opportunity.status}
                      size="small"
                      sx={{ 
                        backgroundColor: getStatusColor(opportunity.status),
                        color: '#fff',
                        fontSize: '10px'
                      }}
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    {opportunity.description}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" fontWeight={600}>
                      ₹{opportunity.current.toLocaleString()}
                    </Typography>
                    {opportunity.potential > 0 && (
                      <Typography variant="caption" color="#ff9800" fontWeight={600}>
                        +₹{opportunity.potential.toLocaleString()} potential
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    Deadline: {opportunity.deadline}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Grid>
        </Grid>

        {/* ADK Tax Insights */}
        {adkAnalysis && adkAnalysis.insights && adkAnalysis.insights.length > 0 && (
          <Box sx={{ mt: 3, p: 2, backgroundColor: '#f1f8e9', borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight={600} mb={1} color="#2e7d32">
              💰 ADK Tax Insights
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {adkAnalysis.insights.slice(0, 3).map((insight, idx) => (
                <Typography key={idx} variant="body2" sx={{ color: '#2e7d32' }}>
                  • {insight}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {/* Tax Planning Tips */}
        <Box sx={{ mt: 3, p: 2, backgroundColor: '#fff3e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" fontWeight={600} mb={1} color="#f57c00">
            💡 Tax Planning Tips
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ color: '#e65100', mb: 1 }}>
                <strong>Section 80C:</strong> Maximize your ₹1.5L limit with ELSS, EPF, and other eligible investments.
              </Typography>
              <Typography variant="body2" sx={{ color: '#e65100', mb: 1 }}>
                <strong>Section 80D:</strong> Claim up to ₹25,000 for health insurance premiums.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ color: '#e65100', mb: 1 }}>
                <strong>NPS:</strong> Additional ₹50,000 deduction under Section 80CCD(1B).
              </Typography>
              <Typography variant="body2" sx={{ color: '#e65100' }}>
                <strong>Home Loan:</strong> Interest deduction up to ₹2L under Section 24(b).
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
} 
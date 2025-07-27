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
  CircularProgress
} from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import axios from 'axios';

// Enhanced color palette for better visualization
const COLORS = [
  '#1976d2', '#388e3c', '#f57c00', '#d32f2f', 
  '#7b1fa2', '#1565c0', '#2e7d32', '#f57c00'
];

const ADK_ANALYSIS_TYPES = {
  'portfolio_analysis': { icon: '📊', color: '#1976d2', label: 'Portfolio Analysis' },
  'risk_assessment': { icon: '⚠️', color: '#d32f2f', label: 'Risk Assessment' },
  'investment_advice': { icon: '📈', color: '#f57c00', label: 'Investment Advice' },
  'tax_planning': { icon: '💰', color: '#388e3c', label: 'Tax Planning' }
};

export default function EnhancedAssetAllocation({ data }) {
  const [adkAnalysis, setAdkAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Use real allocation breakdown if available
  const allocation = data.fetch_net_worth?.netWorthResponse?.assetValues?.map(a => ({
    label: a.netWorthAttribute.replace('ASSET_TYPE_', '').replace('_', ' '),
    value: parseFloat(a.value?.units) || 0
  })) || [];

  // Calculate total for percentage breakdown
  const total = allocation.reduce((sum, a) => sum + a.value, 0) || 1;
  const allocationWithPercent = allocation.map((a, idx) => ({
    ...a,
    percent: Math.round((a.value / total) * 100),
    color: COLORS[idx % COLORS.length]
  }));

  // Get ADK analysis for portfolio optimization
  const getADKAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/chatbot', { 
        message: "Analyze my portfolio allocation and provide optimization recommendations. Include risk assessment, diversification analysis, and specific improvement suggestions." 
      }, { withCredentials: true });

      if (response.data && response.data.analysis_type) {
        setAdkAnalysis(response.data);
      } else {
        setError('Unable to get ADK analysis');
      }
    } catch (err) {
      setError('Failed to get portfolio analysis');
      console.error('ADK Analysis Error:', err);
    }
    setLoading(false);
  };

  // Auto-trigger analysis when component mounts (only if user has interacted)
  useEffect(() => {
    // Only trigger ADK analysis if user has shown interest (e.g., clicked on portfolio)
    // For now, we'll disable auto-trigger to prevent unwanted API calls
    // getADKAnalysis();
  }, [allocation]);

  const getRiskProfile = () => {
    const equityPercentage = allocationWithPercent.find(a => 
      a.label.toLowerCase().includes('stock') || 
      a.label.toLowerCase().includes('equity')
    )?.percent || 0;

    if (equityPercentage > 70) return { level: 'High', color: '#d32f2f' };
    if (equityPercentage > 50) return { level: 'Moderate-High', color: '#f57c00' };
    if (equityPercentage > 30) return { level: 'Moderate', color: '#ff9800' };
    return { level: 'Conservative', color: '#388e3c' };
  };

  const riskProfile = getRiskProfile();

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: '#fff',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: '#1976d2' }}>
            {payload[0].payload.label}
          </p>
          <p style={{ margin: '0 0 4px 0', color: '#666' }}>
            Amount: <strong>₹{payload[0].value.toLocaleString()}</strong>
          </p>
          <p style={{ margin: '0', color: '#666' }}>
            Percentage: <strong>{payload[0].payload.percent}%</strong>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={700}>Enhanced Asset Allocation</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">Risk Profile:</Typography>
            <Chip 
              label={riskProfile.level} 
              size="small"
              sx={{ 
                backgroundColor: riskProfile.color, 
                color: '#fff',
                fontWeight: 600
              }}
            />
            <Button
              variant="outlined"
              size="small"
              onClick={getADKAnalysis}
              disabled={loading}
              sx={{ ml: 2 }}
            >
              {loading ? <CircularProgress size={16} /> : 'Get AI Analysis'}
            </Button>
          </Box>
        </Box>

        {/* ADK Analysis Section */}
        {adkAnalysis && (
          <Alert 
            severity="info" 
            sx={{ mb: 2, borderRadius: 2 }}
            action={
              <Button 
                size="small" 
                onClick={getADKAnalysis}
                disabled={loading}
                sx={{ color: '#1976d2' }}
              >
                {loading ? <CircularProgress size={16} /> : 'Refresh'}
              </Button>
            }
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <span style={{ fontSize: '18px' }}>
                {ADK_ANALYSIS_TYPES[adkAnalysis.analysis_type]?.icon || '🤖'}
              </span>
              <Typography variant="subtitle2" fontWeight={600}>
                {ADK_ANALYSIS_TYPES[adkAnalysis.analysis_type]?.label || 'ADK Analysis'}
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
                <Typography variant="caption" fontWeight={600} color="#1976d2">
                  Key Recommendations:
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

        <Grid container spacing={2} alignItems="center">
          {/* Enhanced Table */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" mb={1} fontWeight={600}>
              Allocation Breakdown
            </Typography>
            <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Asset Type</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Amount</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Percent</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allocationWithPercent.length > 0 ? allocationWithPercent.map((item) => (
                    <TableRow key={item.label} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <div 
                            style={{ 
                              width: 12, 
                              height: 12, 
                              borderRadius: '50%', 
                              backgroundColor: item.color 
                            }} 
                          />
                          {item.label}
                        </Box>
                      </TableCell>
                      <TableCell align="right">₹{item.value.toLocaleString()}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700 }}>
                        {item.percent}%
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={3} sx={{ textAlign: 'center', color: '#666' }}>
                        No allocation data available
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Portfolio Summary */}
            <Box sx={{ mt: 2, p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
              <Typography variant="subtitle2" fontWeight={600} mb={1}>
                Portfolio Summary
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Total Assets:</Typography>
                <Typography variant="body2" fontWeight={600}>
                  ₹{total.toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Asset Classes:</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {allocation.length}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">Risk Level:</Typography>
                <Typography variant="body2" fontWeight={600} sx={{ color: riskProfile.color }}>
                  {riskProfile.level}
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Enhanced Pie Chart */}
          <Grid item xs={12} md={8} sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', pr: { md: 10, xs: 0 } }}>
            {allocationWithPercent.length > 0 ? (
              <ResponsiveContainer width={600} height={340}>
                <PieChart>
                  <Pie
                    data={allocationWithPercent}
                    dataKey="value"
                    nameKey="label"
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={120}
                    fill="#90caf9"
                    label={({ value, percent }) => `${Math.round(percent * 100)}%`}
                    labelLine={false}
                    paddingAngle={2}
                  >
                    {allocationWithPercent.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                height: 340,
                color: '#666'
              }}>
                <Typography variant="h6" mb={1}>No Data Available</Typography>
                <Typography variant="body2">Connect your accounts to see asset allocation</Typography>
              </Box>
            )}
          </Grid>
        </Grid>

        {/* ADK Insights Section */}
        {adkAnalysis && adkAnalysis.insights && adkAnalysis.insights.length > 0 && (
          <Box sx={{ mt: 3, p: 2, backgroundColor: '#f1f8e9', borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight={600} mb={1} color="#2e7d32">
              🔍 ADK Insights
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
      </CardContent>
    </Card>
  );
} 
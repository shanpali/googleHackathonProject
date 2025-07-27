import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Grid, Box, Button, CircularProgress, Alert, IconButton, Tooltip, Chip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import InfoIcon from '@mui/icons-material/Info';
import SavingsIcon from '@mui/icons-material/Savings';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import axios from 'axios';

const ICON_MAP = {
  tax: <ErrorOutlineIcon color="error" />,
  portfolio: <TrendingUpIcon color="warning" />,
  spending: <InfoIcon color="info" />,
  opportunity: <SavingsIcon color="success" />,
  alert: <WarningAmberIcon color="warning" />,
};

// Sentiment analysis function for insights
function analyzeInsightSentiment(title, description) {
  const text = `${title} ${description}`.toLowerCase();
  
  // Negative keywords for insights
  const negativeKeywords = [
    'decline', 'fall', 'drop', 'loss', 'negative', 'bearish', 'crash', 'plunge', 'downturn',
    'decrease', 'reduction', 'cut', 'slump', 'dip', 'slide', 'tumble', 'sink', 'plummet',
    'bear market', 'recession', 'bankruptcy', 'default', 'delisting', 'penalty', 'fine',
    'investigation', 'scandal', 'fraud', 'corruption', 'lawsuit', 'litigation', 'regulatory',
    'warning', 'risk', 'volatile', 'uncertainty', 'concern', 'worry', 'fear', 'anxiety',
    'drift', 'underperforming', 'deficit', 'shortfall', 'overspending', 'debt', 'liability'
  ];
  
  // Positive keywords for insights
  const positiveKeywords = [
    'rise', 'gain', 'increase', 'growth', 'positive', 'bullish', 'rally', 'surge', 'jump',
    'climb', 'soar', 'boost', 'improve', 'profit', 'earnings', 'revenue', 'dividend',
    'bull market', 'expansion', 'recovery', 'upswing', 'uptrend', 'breakthrough', 'success',
    'approval', 'launch', 'partnership', 'acquisition', 'merger', 'innovation', 'upgrade',
    'optimistic', 'confidence', 'strong', 'robust', 'healthy', 'stable', 'opportunity',
    'save', 'optimization', 'efficiency', 'benefit', 'advantage', 'potential'
  ];
  
  let negativeScore = 0;
  let positiveScore = 0;
  
  negativeKeywords.forEach(keyword => {
    if (text.includes(keyword)) negativeScore++;
  });
  
  positiveKeywords.forEach(keyword => {
    if (text.includes(keyword)) positiveScore++;
  });
  
  // Determine sentiment
  if (negativeScore > positiveScore) return 'negative';
  if (positiveScore > negativeScore) return 'positive';
  return 'neutral';
}

// Get sentiment styling for insights
function getInsightSentimentStyle(sentiment, priority) {
  const baseStyle = {
    borderRadius: 3,
    mb: 2,
    transition: 'all 0.3s ease',
    '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 }
  };
  
  switch (sentiment) {
    case 'positive':
      return {
        ...baseStyle,
        borderLeft: '4px solid #4caf50',
        background: 'linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%)',
        '&:hover': { 
          ...baseStyle['&:hover'],
          boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)' 
        }
      };
    case 'negative':
      return {
        ...baseStyle,
        borderLeft: '4px solid #f44336',
        background: 'linear-gradient(135deg, #ffebee 0%, #ffffff 100%)',
        '&:hover': { 
          ...baseStyle['&:hover'],
          boxShadow: '0 4px 12px rgba(244, 67, 54, 0.3)' 
        }
      };
    default:
      return {
        ...baseStyle,
        borderLeft: `4px solid ${priority?.toLowerCase().includes('high') ? '#f44336' : priority?.toLowerCase().includes('medium') ? '#ff9800' : priority?.toLowerCase().includes('opportunity') ? '#4caf50' : '#2196f3'}`,
        background: 'linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%)',
        '&:hover': { 
          ...baseStyle['&:hover'],
          boxShadow: '0 4px 12px rgba(158, 158, 158, 0.3)' 
        }
      };
  }
}

// Get sentiment icon for insights
function getInsightSentimentIcon(sentiment) {
  switch (sentiment) {
    case 'positive':
      return <TrendingUpIcon sx={{ color: '#4caf50', fontSize: 20 }} />;
    case 'negative':
      return <TrendingDownIcon sx={{ color: '#f44336', fontSize: 20 }} />;
    default:
      return <TrendingFlatIcon sx={{ color: '#9e9e9e', fontSize: 20 }} />;
  }
}

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
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    if (customInsights) {
      // Add sentiment analysis to custom insights
      const insightsWithSentiment = customInsights.map(insight => ({
        ...insight,
        sentiment: analyzeInsightSentiment(insight.title, insight.description)
      }));
      setInsights(insightsWithSentiment);
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
          // Add sentiment analysis to fetched insights
          const insightsWithSentiment = res.data.insights.map(insight => ({
            ...insight,
            sentiment: analyzeInsightSentiment(insight.title, insight.description)
          }));
          setInsights(insightsWithSentiment);
          setLastUpdated(res.data.last_updated);
        } else if (mounted) {
          // No insights found in database
          setInsights([]);
          setError('No insights available. Click refresh to generate personalized insights.');
        }
      })
      .catch(err => {
        if (mounted) {
          setInsights([]);
          setError('Could not fetch insights. Click refresh to try again.');
        }
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
        if (res.data && Array.isArray(res.data.insights) && res.data.insights.length > 0) {
          const insightsWithSentiment = res.data.insights.map(insight => ({
            ...insight,
            sentiment: analyzeInsightSentiment(insight.title, insight.description)
          }));
          setInsights(insightsWithSentiment);
          setLastUpdated(res.data.last_updated);
          setError(null);
        } else {
          setInsights([]);
          setError('No insights generated. Please try again.');
        }
      })
      .catch(() => {
        setInsights([]);
        setError('Could not refresh insights. Please try again.');
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
        {lastUpdated && (
          <Typography variant="body2" color="text.secondary" ml={1}>
            Last updated: {new Date(lastUpdated).toLocaleString('en-IN', { 
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: true
            })}
          </Typography>
        )}
      </Box>
      {loading && (
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          my: 4, 
          gap: 2,
          width: '100%',
          maxWidth: 1200,
          mx: 'auto'
        }}>
          <Typography variant="h6" color="primary" sx={{ textAlign: 'center', mb: 1 }}>
            {(() => {
              const messages = [
                "Mining financial insights...",
                "Consulting the market oracle...",
                "Decoding your money matrix...",
                "Summoning financial wisdom...",
                "Analyzing your wealth patterns...",
                "Consulting with money gurus...",
                "Unlocking financial secrets...",
                "Reading the market tea leaves...",
                "Deciphering your financial DNA...",
                "Connecting the money dots..."
              ];
              return messages[Math.floor(Math.random() * messages.length)];
            })()}
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'primary.main',
              animation: 'pulse 1.4s ease-in-out infinite both',
              animationDelay: '0s'
            }} />
            <Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'primary.main',
              animation: 'pulse 1.4s ease-in-out infinite both',
              animationDelay: '0.2s'
            }} />
            <Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'primary.main',
              animation: 'pulse 1.4s ease-in-out infinite both',
              animationDelay: '0.4s'
            }} />
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center' }}>
            AI is working harder than your financial advisor
          </Typography>
        </Box>
      )}
      {error && <Alert severity="info" sx={{ mb: 2 }}>{error}</Alert>}
      {!loading && !error && insights.length === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          No insights available. Click the refresh button above to generate personalized insights based on your financial data.
        </Alert>
      )}
      <Grid container spacing={2}>
        {insights.map((item, idx) => (
          <Grid item xs={12} sm={6} md={6} key={item.title + idx}>
            <Card sx={getInsightSentimentStyle(item.sentiment, item.priority)}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {getInsightSentimentIcon(item.sentiment)}
                  <Chip 
                    label={item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)} 
                    size="small" 
                    color={item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'error' : 'default'}
                    variant="outlined"
                  />
                </Box>
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
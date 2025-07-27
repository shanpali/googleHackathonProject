import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, CircularProgress, Alert, Grid, Link, Chip } from '@mui/material';
import FeedIcon from '@mui/icons-material/Feed';
import RefreshIcon from '@mui/icons-material/Refresh';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';

function isRecent(dateStr) {
  if (!dateStr) return false;
  const today = new Date();
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return false;
  const diff = (today - date) / (1000 * 60 * 60 * 24);
  return diff >= 0 && diff <= 7;
}

// Sentiment analysis function
function analyzeSentiment(title, summary) {
  const text = `${title} ${summary}`.toLowerCase();
  
  // Negative keywords
  const negativeKeywords = [
    'decline', 'fall', 'drop', 'loss', 'negative', 'bearish', 'crash', 'plunge', 'downturn',
    'decrease', 'reduction', 'cut', 'slump', 'dip', 'slide', 'tumble', 'sink', 'plummet',
    'bear market', 'recession', 'bankruptcy', 'default', 'delisting', 'penalty', 'fine',
    'investigation', 'scandal', 'fraud', 'corruption', 'lawsuit', 'litigation', 'regulatory',
    'warning', 'risk', 'volatile', 'uncertainty', 'concern', 'worry', 'fear', 'anxiety'
  ];
  
  // Positive keywords
  const positiveKeywords = [
    'rise', 'gain', 'increase', 'growth', 'positive', 'bullish', 'rally', 'surge', 'jump',
    'climb', 'soar', 'boost', 'improve', 'profit', 'earnings', 'revenue', 'dividend',
    'bull market', 'expansion', 'recovery', 'upswing', 'uptrend', 'breakthrough', 'success',
    'approval', 'launch', 'partnership', 'acquisition', 'merger', 'innovation', 'upgrade',
    'upgrade', 'optimistic', 'confidence', 'strong', 'robust', 'healthy', 'stable'
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

// Get sentiment styling
function getSentimentStyle(sentiment) {
  switch (sentiment) {
    case 'positive':
      return {
        border: '2px solid #4caf50',
        background: 'linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%)',
        '&:hover': { boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)' }
      };
    case 'negative':
      return {
        border: '2px solid #f44336',
        background: 'linear-gradient(135deg, #ffebee 0%, #ffffff 100%)',
        '&:hover': { boxShadow: '0 4px 12px rgba(244, 67, 54, 0.3)' }
      };
    default:
      return {
        border: '2px solid #9e9e9e',
        background: 'linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%)',
        '&:hover': { boxShadow: '0 4px 12px rgba(158, 158, 158, 0.3)' }
      };
  }
}

// Get sentiment icon
function getSentimentIcon(sentiment) {
  switch (sentiment) {
    case 'positive':
      return <TrendingUpIcon sx={{ color: '#4caf50', fontSize: 20 }} />;
    case 'negative':
      return <TrendingDownIcon sx={{ color: '#f44336', fontSize: 20 }} />;
    default:
      return <TrendingFlatIcon sx={{ color: '#9e9e9e', fontSize: 20 }} />;
  }
}

// Get sentiment chip color
function getSentimentChipColor(sentiment) {
  switch (sentiment) {
    case 'positive':
      return 'success';
    case 'negative':
      return 'error';
    default:
      return 'default';
  }
}

export default function PersonalisedNews({ phone }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchNews = async (refresh = false) => {
    if (refresh) setRefreshing(true); else setLoading(true);
    setError(null);
    try {
      const url = refresh ? '/news?refresh=true' : '/news';
      const res = await fetch(url, { credentials: 'include' });
      const data = await res.json();
      if (res.ok && Array.isArray(data.news)) {
        // Filter for only recent news (last 7 days) and add sentiment analysis
        const filtered = data.news.filter(item => isRecent(item.date)).map(item => ({
          ...item,
          sentiment: analyzeSentiment(item.title, item.summary)
        }));
        setNews(filtered);
        setLastUpdated(data.last_updated);
      } else {
        setError(data.error || 'Could not fetch news.');
      }
    } catch (e) {
      setError('Could not fetch news.');
    } finally {
      if (refresh) setRefreshing(false); else setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  // Group news by holdingName
  const grouped = {};
  news.forEach(item => {
    const key = item.holdingName || 'Other';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(item);
  });

  if (loading) return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '100%',
      minHeight: '60vh',
      gap: 2,
      width: '100%',
      maxWidth: 1100,
      mx: 'auto',
      p: { xs: 1, md: 4 }
    }}>
      <Typography variant="h5" color="primary" sx={{ textAlign: 'center', mb: 1 }}>
        {(() => {
          const messages = [
            "Fetching your personalized news...",
            "Curating financial headlines...",
            "Gathering market insights...",
            "Loading your news feed...",
            "Preparing financial updates...",
            "Collecting market news...",
            "Loading personalized headlines...",
            "Gathering financial insights...",
            "Curating your news feed...",
            "Preparing market updates..."
          ];
          return messages[Math.floor(Math.random() * messages.length)];
        })()}
      </Typography>
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        <Box sx={{ 
          width: 10, 
          height: 10, 
          borderRadius: '50%', 
          bgcolor: 'primary.main',
          animation: 'pulse 1.4s ease-in-out infinite both',
          animationDelay: '0s'
        }} />
        <Box sx={{ 
          width: 10, 
          height: 10, 
          borderRadius: '50%', 
          bgcolor: 'primary.main',
          animation: 'pulse 1.4s ease-in-out infinite both',
          animationDelay: '0.2s'
        }} />
        <Box sx={{ 
          width: 10, 
          height: 10, 
          borderRadius: '50%', 
          bgcolor: 'primary.main',
          animation: 'pulse 1.4s ease-in-out infinite both',
          animationDelay: '0.4s'
        }} />
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
        Your news is loading faster than the market reacts to tweets... almost
      </Typography>
    </Box>
  );

  return (
    <Box sx={{ width: '100%', maxWidth: 1100, mx: 'auto', p: { xs: 1, md: 4 }, minHeight: 600 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <FeedIcon color="primary" sx={{ fontSize: 36, mr: 1 }} />
        <Typography variant="h4" fontWeight={800} color="primary">Investment Insights</Typography>
        {lastUpdated && (
          <Typography variant="body2" color="text.secondary" ml={2}>
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
        <Box sx={{ ml: 2 }}>
          <button
            onClick={() => fetchNews(true)}
            disabled={refreshing || loading}
            style={{
              background: 'none',
              border: 'none',
              cursor: refreshing || loading ? 'not-allowed' : 'pointer',
              padding: 0,
              margin: 0,
              outline: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              fontSize: 20
            }}
            title="Refresh News"
          >
            <RefreshIcon sx={{ fontSize: 32, color: refreshing ? '#90caf9' : '#1976d2', animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            {refreshing && <span style={{ marginLeft: 8, color: '#1976d2', fontWeight: 600 }}>Refreshing...</span>}
          </button>
        </Box>
      </Box>
      <Typography variant="subtitle1" color="text.secondary" mb={3}>
        Stay updated with the latest news and updates related to your investments. Powered by Gemini AI.
      </Typography>
      {loading && <Box sx={{ display: 'flex', justifyContent: 'center', my: 6 }}><CircularProgress size={40} /></Box>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {!loading && !error && Object.keys(grouped).length === 0 && (
        <Alert severity="info">No news found for your investments.</Alert>
      )}
      <Grid container spacing={3}>
        {Object.entries(grouped).map(([holding, items]) => (
          <Grid item xs={12} key={holding}>
            <Typography variant="h6" fontWeight={700} color="secondary" mb={1}>
              {holding}
            </Typography>
            <Grid container spacing={2}>
              {items.map((item, idx) => (
                <Grid item xs={12} sm={6} md={4} key={item.title + idx}>
                  <Card 
                    sx={{ 
                      borderRadius: 3, 
                      boxShadow: 3, 
                      minHeight: 180, 
                      display: 'flex', 
                      flexDirection: 'column', 
                      justifyContent: 'space-between',
                      transition: 'all 0.3s ease',
                      ...getSentimentStyle(item.sentiment)
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        {getSentimentIcon(item.sentiment)}
                        <Chip 
                          label={item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)} 
                          size="small" 
                          color={getSentimentChipColor(item.sentiment)}
                          variant="outlined"
                        />
                      </Box>
                      <Typography variant="subtitle1" fontWeight={700} gutterBottom>{item.title}</Typography>
                      <Typography variant="body2" color="text.secondary" mb={1}>{item.summary}</Typography>
                      {item.date && <Chip label={item.date} size="small" sx={{ mb: 1, mr: 1 }} />}
                      {item.link && <Link href={item.link} target="_blank" rel="noopener" underline="hover">Read more</Link>}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

// Add global style for pulse animation
const pulseStyle = document.createElement('style');
pulseStyle.innerHTML = `
  @keyframes pulse { 
    0%, 80%, 100% { 
      opacity: 0.3; 
      transform: scale(0.8); 
    } 
    40% { 
      opacity: 1; 
      transform: scale(1); 
    } 
  }
`;
document.head.appendChild(pulseStyle); 
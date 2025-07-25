import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, CircularProgress, Alert, Grid, Link, Chip } from '@mui/material';
import FeedIcon from '@mui/icons-material/Feed';

function isRecent(dateStr) {
  if (!dateStr) return false;
  const today = new Date();
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return false;
  const diff = (today - date) / (1000 * 60 * 60 * 24);
  return diff >= 0 && diff <= 7;
}

export default function PersonalisedNews({ phone }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('/news', { credentials: 'include' });
        const data = await res.json();
        if (res.ok && Array.isArray(data.news)) {
          // Filter for only recent news (last 7 days)
          const filtered = data.news.filter(item => isRecent(item.date));
          setNews(filtered);
        } else {
          setError(data.error || 'Could not fetch news.');
        }
      } catch (e) {
        setError('Could not fetch news.');
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, []);

  // Group news by holdingName
  const grouped = {};
  news.forEach(item => {
    const key = item.holdingName || 'Other';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(item);
  });

  return (
    <Box sx={{ width: '100%', maxWidth: 1100, mx: 'auto', p: { xs: 1, md: 4 }, minHeight: 600 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <FeedIcon color="primary" sx={{ fontSize: 36, mr: 1 }} />
        <Typography variant="h4" fontWeight={800} color="primary">Personalised News</Typography>
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
                  <Card sx={{ borderRadius: 3, boxShadow: 3, minHeight: 180, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <CardContent>
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
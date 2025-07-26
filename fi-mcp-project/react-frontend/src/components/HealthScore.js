import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, List, ListItem, ListItemText, CircularProgress, Alert, IconButton } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import axios from 'axios';

export default function HealthScore({ data }) {
  const [score, setScore] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchHealthScore = (refresh = false) => {
    setLoading(true);
    setError(null);
    axios.post('/health-score', { refresh }, { withCredentials: true })
      .then(res => {
        if (res.data && typeof res.data.score === 'number' && Array.isArray(res.data.metrics)) {
          setScore(res.data.score);
          setMetrics(res.data.metrics);
          setLastUpdated(res.data.last_updated);
        } else {
          setError('No health score found.');
        }
      })
      .catch(() => {
        setError('Could not fetch health score.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealthScore();
  }, []);

  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={700}>Financial Health Score</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {lastUpdated && (
              <Typography variant="body2" color="text.secondary">
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
            <IconButton 
              onClick={() => fetchHealthScore(true)} 
              disabled={loading}
              size="small"
              sx={{ color: '#1976d2' }}
            >
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>
        {loading && <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}><CircularProgress /></Box>}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {!loading && !error && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                <svg width={80} height={80}>
                  <circle cx={40} cy={40} r={36} fill="none" stroke="#e0e0e0" strokeWidth={8} />
                  <circle cx={40} cy={40} r={36} fill="none" stroke="#1976d2" strokeWidth={8} strokeDasharray={226} strokeDashoffset={226 - (score || 0) * 2.26} />
                </svg>
                <Typography variant="h4" sx={{ position: 'absolute', top: 22, left: 22 }}>{score ?? '--'}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">out of 100</Typography>
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <List dense>
                {metrics.map((item) => (
                  <ListItem key={item.label} sx={{ py: 0, alignItems: 'flex-start' }}>
                    <ListItemText
                      primary={<span style={{ fontWeight: 700 }}>{item.label}</span>}
                      secondary={<span style={{ color: '#888', fontSize: 13 }}>{item.explanation}</span>}
                    />
                    <Box sx={{ width: 80, mr: 2, mt: 1 }}>
                      <LinearProgress variant="determinate" value={item.value} sx={{ height: 8, borderRadius: 5 }} />
                    </Box>
                    <Typography fontWeight={700}>{item.value}/100</Typography>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
} 
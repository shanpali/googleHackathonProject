import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box, Button, TextField, Chip, Divider, IconButton, CircularProgress, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Fab, Tooltip, List, ListItem, ListItemText } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import axios from 'axios';

const GOAL_TYPES = [
  { label: 'Short Term', value: 'short' },
  { label: 'Long Term', value: 'long' }
];

const ICON_MAP = {
  tax: <ErrorOutlineIcon color="error" />,
  portfolio: <TrendingUpIcon color="warning" />,
  spending: <InfoIcon color="info" />,
  opportunity: <SavingsIcon color="success" />,
  alert: <WarningAmberIcon color="warning" />,
};

export default function Goals({ onGoalChange }) {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [goalType, setGoalType] = useState('short');
  const [goalName, setGoalName] = useState('');
  const [goalAmount, setGoalAmount] = useState('');
  const [goalYear, setGoalYear] = useState('');
  const [filter, setFilter] = useState('all');
  const [addOpen, setAddOpen] = useState(false);
  const [goalInsights, setGoalInsights] = useState(null);
  const [loadingGoalInsights, setLoadingGoalInsights] = useState(false);
  const [errorGoalInsights, setErrorGoalInsights] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [cached, setCached] = useState(false);

  // Load goals and cached insights from database on component mount
  useEffect(() => {
    const loadGoals = async () => {
      try {
        const res = await axios.get('/goals', { withCredentials: true });
        if (res.data && Array.isArray(res.data.goals)) {
          setGoals(res.data.goals);
          // After goals are loaded, fetch cached insights
          await loadCachedGoalInsights(res.data.goals);
        }
      } catch (err) {
        setError('Could not load goals.');
      } finally {
        setLoading(false);
      }
    };
    
    const loadCachedGoalInsights = async (loadedGoals) => {
      try {
        setLoadingGoalInsights(true);
        // Only fetch insights if there are goals
        if (loadedGoals && loadedGoals.length > 0) {
          const res = await axios.post('/insights', { goals: loadedGoals }, { withCredentials: true });
          if (res.data && Array.isArray(res.data.insights) && res.data.insights.length > 0) {
            setGoalInsights(res.data.insights);
            setLastUpdated(res.data.last_updated);
            setCached(res.data.cached || false);
          }
        }
      } catch (e) {
        // Silently fail - no cached insights
      } finally {
        setLoadingGoalInsights(false);
      }
    };
    
    loadGoals();
  }, []);

  const saveGoalsToDB = async (newGoals) => {
    try {
      await axios.post('/goals', { goals: newGoals }, { withCredentials: true });
      // Trigger global refresh when goals change
      if (onGoalChange) {
        onGoalChange();
      }
    } catch (err) {
      setError('Could not save goals.');
    }
  };

  const handleAddGoal = () => {
    if (!goalName || !goalAmount || !goalYear) return;
    const newGoals = [...goals, {
      type: goalType,
      name: goalName,
      amount: parseFloat(goalAmount),
      year: parseInt(goalYear)
    }];
    setGoals(newGoals);
    saveGoalsToDB(newGoals);
    setGoalName('');
    setGoalAmount('');
    setGoalYear('');
    setAddOpen(false);
  };

  const handleDeleteGoal = (idx) => {
    const newGoals = goals.filter((_, i) => i !== idx);
    setGoals(newGoals);
    saveGoalsToDB(newGoals);
  };

  // Fetch goal-based insights (optionally refresh)
  const handleRequestGoalInsights = async (refresh = false) => {
    // Don't proceed if no goals exist
    if (!goals || goals.length === 0) {
      setErrorGoalInsights('Please add some goals first to get personalized insights.');
      return;
    }

    setLoadingGoalInsights(true);
    setErrorGoalInsights(null);
    if (refresh) {
      setGoalInsights(null);
      setLastUpdated(null);
      setCached(false);
    }
    try {
      // Send goals data for proper context, use POST to include goals in request body
      const url = refresh ? '/insights?refresh=true' : '/insights';
      const res = await axios.post(url, { goals }, { withCredentials: true });
      if (res.data && Array.isArray(res.data.insights)) {
        setGoalInsights(res.data.insights);
        setLastUpdated(res.data.last_updated);
        setCached(res.data.cached || false);
      } else {
        setGoalInsights([]);
        setLastUpdated(null);
        setCached(false);
      }
    } catch (e) {
      setGoalInsights(null);
      setLastUpdated(null);
      setCached(false);
      setErrorGoalInsights('Could not fetch goal-based insights.');
    } finally {
      setLoadingGoalInsights(false);
    }
  };

  // Filtered goals
  const filteredGoals = filter === 'all' ? goals : goals.filter(g => g.type === filter);

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, mx: 'auto', p: { xs: 1, md: 3 }, minHeight: 600 }}>
      {/* Header Section */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="primary" mb={0.5}>
            <EmojiEventsIcon sx={{ fontSize: 32, mr: 1, verticalAlign: 'middle' }} />
            Your Financial Goals
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Track, manage, and achieve your short and long-term goals.
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setAddOpen(true)}
          sx={{ borderRadius: 2, fontWeight: 700, px: 3, py: 1.2, fontSize: 18, boxShadow: 2 }}
        >
          Add Goal
        </Button>
      </Box>
      {/* Filter Bar */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 3, mt: 1 }}>
        <Button variant={filter === 'all' ? 'contained' : 'outlined'} onClick={() => setFilter('all')}>All</Button>
        <Button variant={filter === 'short' ? 'contained' : 'outlined'} color="primary" onClick={() => setFilter('short')}>Short Term</Button>
        <Button variant={filter === 'long' ? 'contained' : 'outlined'} color="success" onClick={() => setFilter('long')}>Long Term</Button>
      </Box>
      {/* Goals Grid */}
      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 6, gap: 2 }}>
          <Typography variant="h6" color="primary" sx={{ textAlign: 'center', mb: 1 }}>
            {(() => {
              const messages = [
                "Loading your financial dreams...",
                "Unpacking your money goals...",
                "Assembling your wealth roadmap...",
                "Polishing your financial aspirations...",
                "Charging your goal batteries...",
                "Warming up your ambition engine...",
                "Preparing your success toolkit...",
                "Loading your future self...",
                "Calibrating your money compass...",
                "Setting up your wealth GPS..."
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
            Goals are loading faster than your salary... almost
          </Typography>
        </Box>
      ) : filteredGoals.length === 0 ? (
        <Box sx={{ textAlign: 'center', mt: 8, mb: 6 }}>
          <Typography variant="h6" color="text.secondary" mb={2}>No goals yet. Click <b>Add Goal</b> to get started!</Typography>
        </Box>
      ) : (
        <Grid container spacing={3} mb={4}>
          {filteredGoals.map((goal, idx) => (
            <Grid item xs={12} sm={6} md={4} key={idx}>
              <Card sx={{ borderRadius: 3, boxShadow: 3, bgcolor: goal.type === 'short' ? '#e3f2fd' : '#e8f5e9', position: 'relative', minHeight: 140 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" fontWeight={700}>{goal.name}</Typography>
                    <Chip label={goal.type === 'short' ? 'Short Term' : 'Long Term'} size="small" color={goal.type === 'short' ? 'primary' : 'success'} sx={{ ml: 1 }} />
                    <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteGoal(goals.indexOf(goal))} sx={{ ml: 'auto' }}><DeleteIcon /></IconButton>
                  </Box>
                  <Typography variant="body2" color="text.secondary" mb={1}>Target: <b>₹{goal.amount.toLocaleString()}</b> by <b>{goal.year}</b></Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      {/* Get Goal-Based Insights & Alerts Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', my: 3, gap: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => handleRequestGoalInsights(false)}
          disabled={loadingGoalInsights || goals.length === 0}
          sx={{ fontWeight: 700, px: 4, py: 1.2, fontSize: 16, borderRadius: 2, boxShadow: 1, display: 'flex', alignItems: 'center', gap: 1 }}
        >
          Get Goal-Based Insights & Alerts
          {loadingGoalInsights && (
            <span style={{ display: 'inline-flex', alignItems: 'center', marginLeft: 12 }}>
              <RefreshIcon sx={{ fontSize: 24, color: '#90a4ae', animation: 'spin 1s linear infinite' }} />
              <Typography component="span" sx={{ color: '#1976d2', fontWeight: 500, ml: 1, fontSize: 16 }}>Refreshing...</Typography>
            </span>
          )}
        </Button>
        {goalInsights && Array.isArray(goalInsights) && goalInsights.length > 0 && !loadingGoalInsights && (
          <IconButton
            onClick={() => handleRequestGoalInsights(true)}
            disabled={loadingGoalInsights}
            size="large"
            sx={{ color: '#1976d2' }}
          >
            <RefreshIcon />
          </IconButton>
        )}
      </Box>
      {/* Add Goal Modal */}
      <Dialog open={addOpen} onClose={() => setAddOpen(false)}>
        <DialogTitle>Add a New Goal</DialogTitle>
        <DialogContent>
          <TextField
            label="Goal Name"
            value={goalName}
            onChange={e => setGoalName(e.target.value)}
            size="small"
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Amount (₹)"
            value={goalAmount}
            onChange={e => setGoalAmount(e.target.value.replace(/[^0-9.]/g, ''))}
            size="small"
            fullWidth
            type="number"
            sx={{ mb: 2 }}
          />
          <TextField
            label="Target Year"
            value={goalYear}
            onChange={e => setGoalYear(e.target.value.replace(/[^0-9]/g, ''))}
            size="small"
            fullWidth
            type="number"
            sx={{ mb: 2 }}
          />
          <TextField
            select
            label="Type"
            value={goalType}
            onChange={e => setGoalType(e.target.value)}
            size="small"
            fullWidth
            SelectProps={{ native: true }}
            sx={{ mb: 2 }}
          >
            {GOAL_TYPES.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)}>Cancel</Button>
          <Button onClick={handleAddGoal} variant="contained" disabled={!goalName || !goalAmount || !goalYear}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
      {/* Goal-based insights display */}
      {loadingGoalInsights && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 2, gap: 2 }}>
          <Typography variant="h6" color="secondary" sx={{ textAlign: 'center', mb: 1 }}>
            {(() => {
              const messages = [
                "Consulting the financial crystal ball...",
                "Decoding your money patterns...",
                "Summoning financial wisdom...",
                "Analyzing your wealth potential...",
                "Crunching the numbers...",
                "Consulting with money mentors...",
                "Unlocking financial insights...",
                "Reading your financial tea leaves...",
                "Deciphering your money story...",
                "Connecting the financial dots..."
              ];
              return messages[Math.floor(Math.random() * messages.length)];
            })()}
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'secondary.main',
              animation: 'pulse 1.4s ease-in-out infinite both',
              animationDelay: '0s'
            }} />
            <Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'secondary.main',
              animation: 'pulse 1.4s ease-in-out infinite both',
              animationDelay: '0.2s'
            }} />
            <Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              bgcolor: 'secondary.main',
              animation: 'pulse 1.4s ease-in-out infinite both',
              animationDelay: '0.4s'
            }} />
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center' }}>
            AI is thinking harder than your accountant
          </Typography>
        </Box>
      )}
      {errorGoalInsights && (
        <Alert severity="error" sx={{ mb: 2 }}>{errorGoalInsights}</Alert>
      )}
      {goals.length > 0 && goalInsights && Array.isArray(goalInsights) && goalInsights.length > 0 && (
        <Card sx={{ borderRadius: 3, mb: 3, background: '#f3f7fa' }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" fontWeight={700} color="secondary">
                Goal-Based Insights & Alerts
              </Typography>
              {lastUpdated && (
                <Chip
                  label={`${cached ? 'Cached' : 'Fresh'} • ${new Date(lastUpdated).toLocaleString('en-IN', { 
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true
                  })}`}
                  size="small"
                  variant="outlined"
                  color={cached ? "default" : "success"}
                />
              )}
            </Box>
            <List dense>
              {goalInsights.map((item, idx) => (
                <ListItem key={item.title + idx} alignItems="flex-start">
                  <Box sx={{ mr: 2, mt: 0.5 }}>{ICON_MAP[item.icon] || <InfoIcon color="info" />}</Box>
                  <ListItemText
                    primary={<span style={{ fontWeight: 700 }}>{item.title}</span>}
                    secondary={<>
                      <span>{item.description}</span><br />
                      {item.save && <span style={{ color: '#388e3c', fontWeight: 600 }}>{item.save}</span>}<br />
                      <span style={{ color: '#888' }}>{item.action}</span>
                    </>}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
      {goalInsights && Array.isArray(goalInsights) && goalInsights.length === 0 && !loadingGoalInsights && !errorGoalInsights && (
        <Alert severity="info" sx={{ mb: 2 }}>No goal-based insights found.</Alert>
      )}
    </Box>
  );
}

// Add global style for spin animation and pulse animation
const style = document.createElement('style');
style.innerHTML = `
  @keyframes spin { 
    100% { transform: rotate(360deg); } 
  }
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
document.head.appendChild(style); 
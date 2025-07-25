import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, CircularProgress, Button, Avatar, Fab, Fade, Chip, Tooltip, Modal, IconButton } from '@mui/material';
import FinancialOverview from './FinancialOverview';
import AssetAllocation from './AssetAllocation';
import Insights from './Insights';
import HealthScore from './HealthScore';
import NomineeSafeguard from './NomineeSafeguard';
import RecentTransactions from './RecentTransactions';
import axios from 'axios';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import ChatIcon from '@mui/icons-material/Chat';
import StarIcon from '@mui/icons-material/Star';
import CloseIcon from '@mui/icons-material/Close';
import Chatbot from '../Chatbot';
import Goals from './Goals';
// Add for export
import { useCallback } from 'react';

function downloadJSON(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good Morning';
  if (hour < 18) return 'Good Afternoon';
  return 'Good Evening';
}

export default function Dashboard({ phone, setSelectedTab }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showFab, setShowFab] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [goalInsights, setGoalInsights] = useState(null);
  const [loadingGoalInsights, setLoadingGoalInsights] = useState(false);
  const [errorGoalInsights, setErrorGoalInsights] = useState(null);
  const [proactiveInsights, setProactiveInsights] = useState([]);
  const [goalBasedInsights, setGoalBasedInsights] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loadingExport, setLoadingExport] = useState(false);

  useEffect(() => {
    axios.get('/financial-data', { withCredentials: true })
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
    // Show FAB after mount for animation
    setTimeout(() => setShowFab(true), 800);
    // Fetch all exportable data
    fetchAllExportData();
  }, []);

  // Load cached goal insights on mount
  useEffect(() => {
    const loadCachedGoalInsights = async () => {
      try {
        const res = await axios.post('/insights', {}, { withCredentials: true });
        if (res.data && Array.isArray(res.data.insights) && res.data.insights.length > 0) {
          setGoalInsights(res.data.insights);
        }
      } catch (e) {
        // Silently fail - no cached insights
      }
    };
    loadCachedGoalInsights();
  }, []);

  // Handler to get goal-based insights
  const handleRequestGoalInsights = async (goals, refresh = false) => {
    setLoadingGoalInsights(true);
    setErrorGoalInsights(null);
    if (refresh) {
      setGoalInsights(null);
    }
    try {
      const res = await axios.post('/insights', { goals }, { withCredentials: true });
      if (res.data && Array.isArray(res.data.insights)) {
        setGoalInsights(res.data.insights);
      } else {
        setGoalInsights([]);
      }
    } catch (e) {
      setGoalInsights(null);
      setErrorGoalInsights('Could not fetch goal-based insights.');
    } finally {
      setLoadingGoalInsights(false);
    }
  };

  // Fetch all exportable data
  const fetchAllExportData = useCallback(async () => {
    try {
      // Proactive Insights
      const proactiveRes = await axios.get('/insights', { withCredentials: true });
      setProactiveInsights(Array.isArray(proactiveRes.data?.insights) ? proactiveRes.data.insights : []);
    } catch {
      setProactiveInsights([]);
    }
    try {
      // Goal-Based Insights
      const goalBasedRes = await axios.post('/insights', {}, { withCredentials: true });
      setGoalBasedInsights(Array.isArray(goalBasedRes.data?.insights) ? goalBasedRes.data.insights : []);
    } catch {
      setGoalBasedInsights([]);
    }
    try {
      // Goals
      const goalsRes = await axios.get('/goals', { withCredentials: true });
      setGoals(Array.isArray(goalsRes.data?.goals) ? goalsRes.data.goals : []);
    } catch {
      setGoals([]);
    }
  }, []);

  if (loading) return <Box sx={{ flexGrow: 1, p: 4 }}><CircularProgress /></Box>;
  if (!data) return <Box sx={{ flexGrow: 1, p: 4 }}>No data available.</Box>;

  return (
    <Box
      sx={{
        flexGrow: 1,
        p: { xs: 1, md: 4 },
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #e0e7ff 0%, #f5f7fa 100%)',
        transition: 'background 0.5s',
      }}
    >
      {/* Hero Banner */}
      <Box
        sx={{
          mb: 4,
          p: { xs: 2, md: 4 },
          borderRadius: 5,
          background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)',
          color: 'white',
          boxShadow: 3,
          display: 'flex',
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden',
          minHeight: 160,
        }}
      >
        <Avatar
          src="https://randomuser.me/api/portraits/men/32.jpg"
          sx={{ width: 72, height: 72, mr: 3, border: '3px solid #fff', boxShadow: 2 }}
        />
        <Box>
          <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: 1, mb: 0.5 }}>
            {getGreeting()}, Rahul
            {phone && (
              <Typography component="span" variant="h6" sx={{ ml: 2, fontWeight: 400, color: '#fff', opacity: 0.85 }}>
                ({phone})
              </Typography>
            )}
            <StarIcon sx={{ fontSize: 28, color: '#ffd600', verticalAlign: 'middle', ml: 1 }} />
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.92, fontWeight: 400 }}>
            Your personalized financial dashboard for <b>May 2023</b>
          </Typography>
          <Chip
            icon={<EmojiEventsIcon />}
            label="Gold Member"
            color="warning"
            sx={{ mt: 1, fontWeight: 700, fontSize: 16, px: 2, borderRadius: 2, background: 'rgba(255, 214, 0, 0.15)' }}
          />
        </Box>
        <Box sx={{ flexGrow: 1 }} />
        <Fade in={true} timeout={1200}>
          <Button
            variant="contained"
            color="secondary"
            disabled={loadingExport}
            onClick={async () => {
              setLoadingExport(true);
              await fetchAllExportData();
              const exportData = {
                netWorthAndPortfolio: data,
                proactiveInsights,
                goalBasedInsights,
                goals
              };
              downloadJSON(exportData, 'artha-insights-export.json');
              setLoadingExport(false);
            }}
            sx={{ fontWeight: 700, boxShadow: 2, px: 3, py: 1.2, fontSize: 18, borderRadius: 3, ml: 2 }}
          >
            {loadingExport ? 'Exporting...' : 'Export Insights'}
          </Button>
        </Fade>
        {/* Decorative background shapes */}
        <Box sx={{ position: 'absolute', right: -60, top: -40, opacity: 0.15 }}>
          <svg width="180" height="180"><circle cx="90" cy="90" r="80" fill="#fff" /></svg>
        </Box>
      </Box>

      {/* Main Dashboard Content */}
      <Grid container spacing={3} columns={12} mt={2}>
        <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 8' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FinancialOverview data={data} animate onNetWorthClick={() => setSelectedTab && setSelectedTab('Portfolio')} />
          <AssetAllocation data={data} />
          <Insights data={data} />
        </Box>
        <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 4' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
          <HealthScore data={data} />
          <NomineeSafeguard data={data} />
        </Box>
      </Grid>
      <RecentTransactions data={data} />

      {/* Floating Action Button for Chatbot */}
      <Fade in={showFab} timeout={1200}>
        <Tooltip title="Ask AI (Scenario Simulation)">
          <Fab
            color="primary"
            aria-label="chatbot"
            sx={{
              position: 'fixed',
              bottom: { xs: 24, md: 40 },
              right: { xs: 24, md: 40 },
              boxShadow: 4,
              zIndex: 1200,
              fontWeight: 700,
              fontSize: 20,
            }}
            onClick={() => setChatOpen(true)}
          >
            <ChatIcon fontSize="large" />
          </Fab>
        </Tooltip>
      </Fade>

      {/* Right-side Chatbot Modal */}
      <Modal
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          p: 2
        }}
      >
        <Box
          sx={{
            width: { xs: '100%', sm: 500, md: 600 },
            maxWidth: '90vw',
            height: { xs: '100%', sm: '90vh' },
            maxHeight: '90vh',
            background: 'linear-gradient(135deg, #e3f2fd 0%, #f5f7fa 100%)',
            borderRadius: { xs: 0, sm: '24px 0 0 24px' },
            boxShadow: 8,
            position: 'relative',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <IconButton
            onClick={() => setChatOpen(false)}
            sx={{
              position: 'absolute',
              top: 16,
              right: 16,
              zIndex: 10,
              background: 'rgba(255, 255, 255, 0.9)',
              '&:hover': { background: 'rgba(255, 255, 255, 1)' }
            }}
            aria-label="Close Chatbot"
          >
            <CloseIcon />
          </IconButton>
          <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <Chatbot />
          </Box>
        </Box>
      </Modal>
    </Box>
  );
} 
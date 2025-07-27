import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, CircularProgress, Button, Avatar, Fab, Fade, Chip, Tooltip, Modal, IconButton, Skeleton, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Link } from '@mui/material';
import FinancialOverview from './FinancialOverview';
import AssetAllocation from './AssetAllocation';
import EnhancedAssetAllocation from './EnhancedAssetAllocation';
import Insights from './Insights';
import HealthScore from './HealthScore';
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

export default function Dashboard({ phone, setSelectedTab, globalRefreshTrigger }) {
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
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [localGlobalRefreshTrigger, setLocalGlobalRefreshTrigger] = useState(0);
  const [userProfile, setUserProfile] = useState({ name: 'User' });
  
  // Fi-MCP Authentication states
  const [fiMcpAuthDialog, setFiMcpAuthDialog] = useState(false);
  const [fiMcpLoginUrl, setFiMcpLoginUrl] = useState('');
  const [fiMcpLoading, setFiMcpLoading] = useState(false);
  const [fiMcpStatus, setFiMcpStatus] = useState('');
  
  // Lazy loading states for AI components
  const [insightsLoaded, setInsightsLoaded] = useState(false);
  const [healthScoreLoaded, setHealthScoreLoaded] = useState(false);

  const refreshData = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const globalRefresh = () => {
    setLocalGlobalRefreshTrigger(prev => prev + 1);
    // Also refresh financial data
    axios.get('/financial-data', { withCredentials: true })
      .then(res => {
        setData(res.data);
      })
      .catch(() => {
        // Silently fail
      });
  };

  useEffect(() => {
    axios.get('/financial-data', { withCredentials: true })
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
    
    // Fetch user profile
    axios.get('/profile', { withCredentials: true })
      .then(res => {
        setUserProfile(res.data);
      })
      .catch(() => {
        // Silently fail, use default name
      });
    
    // Show FAB after mount for animation
    setTimeout(() => setShowFab(true), 800);
    // Fetch all exportable data
    fetchAllExportData();
  }, [localGlobalRefreshTrigger, globalRefreshTrigger]); // Add both triggers as dependencies

  // Lazy load Insights component after a delay
  useEffect(() => {
    if (!loading && data) {
      const timer = setTimeout(() => {
        setInsightsLoaded(true);
      }, 1000); // Load after 1 second
      return () => clearTimeout(timer);
    }
  }, [loading, data]);

  // Lazy load HealthScore component after a delay
  useEffect(() => {
    if (!loading && data) {
      const timer = setTimeout(() => {
        setHealthScoreLoaded(true);
      }, 1500); // Load after 1.5 seconds
      return () => clearTimeout(timer);
    }
  }, [loading, data]);

  // Listen for profile updates
  useEffect(() => {
    const handleProfileUpdate = (event) => {
      setUserProfile(event.detail);
    };

    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => {
      window.removeEventListener('profileUpdated', handleProfileUpdate);
    };
  }, []);

  const loadCachedGoalInsights = async () => {
    try {
      setLoadingGoalInsights(true);
      const res = await axios.post('/insights', {}, { withCredentials: true });
      if (res.data && Array.isArray(res.data.insights) && res.data.insights.length > 0) {
        setGoalInsights(res.data.insights);
      }
    } catch (e) {
      // Silently fail - no cached insights
    } finally {
      setLoadingGoalInsights(false);
    }
  };

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

  const fetchAllExportData = async () => {
    try {
      // Fetch proactive insights (generic financial insights)
      const proactiveRes = await axios.get('/insights', { withCredentials: true });
      if (proactiveRes.data && Array.isArray(proactiveRes.data.insights)) {
        setProactiveInsights(proactiveRes.data.insights);
      }

      // Fetch goals
      const goalsRes = await axios.get('/goals', { withCredentials: true });
      let userGoals = [];
      if (goalsRes.data && Array.isArray(goalsRes.data.goals)) {
        userGoals = goalsRes.data.goals;
        setGoals(userGoals);
      }

      // Fetch goal-based insights (only for goals section)
      if (userGoals.length > 0) {
        const goalInsightsRes = await axios.post('/insights', { goals: userGoals }, { withCredentials: true });
        if (goalInsightsRes.data && Array.isArray(goalInsightsRes.data.insights)) {
          setGoalBasedInsights(goalInsightsRes.data.insights);
        }
      }
    } catch (error) {
      console.error('Error fetching export data:', error);
    }
  };

  // Fi-MCP Authentication functions
  const handleFiMcpAuth = async () => {
    try {
      setFiMcpLoading(true);
      setFiMcpStatus('');
      
      const response = await axios.post('/fi-mcp-auth', {}, { withCredentials: true });
      
      if (response.data.status === 'auth_required') {
        setFiMcpLoginUrl(response.data.login_url);
        setFiMcpAuthDialog(true);
        setFiMcpStatus('Please authenticate with fi-mcp server');
      } else if (response.data.status === 'authenticated') {
        setFiMcpStatus('Already authenticated!');
        // Retry fetching data
        await refreshData();
      } else {
        setFiMcpStatus('Authentication failed');
      }
    } catch (err) {
      setFiMcpStatus('Error: ' + (err.response?.data?.message || err.message));
      console.error('Fi-MCP Auth Error:', err);
    } finally {
      setFiMcpLoading(false);
    }
  };

  const handleFiMcpRetry = async () => {
    try {
      setFiMcpLoading(true);
      setFiMcpStatus('');
      
      const response = await axios.post('/fi-mcp-retry', {}, { withCredentials: true });
      
      if (response.data.status === 'success') {
        setData(response.data.data);
        setFiMcpStatus('Successfully loaded real data!');
        setFiMcpAuthDialog(false);
      } else if (response.data.status === 'no_data') {
        const debugInfo = response.data.debug_info;
        const sessionId = debugInfo?.session_id?.substring(0, 20) + '...';
        const loginUrl = debugInfo?.login_url;
        
        setFiMcpStatus(
          `Authentication incomplete. Please ensure you have completed the authentication process in your browser. ` +
          `Session: ${sessionId}`
        );
        
        // Update the login URL in case it changed
        if (loginUrl) {
          setFiMcpLoginUrl(loginUrl);
        }
      } else {
        setFiMcpStatus('No real data available after authentication');
      }
    } catch (err) {
      setFiMcpStatus('Error: ' + (err.response?.data?.message || err.message));
      console.error('Fi-MCP Retry Error:', err);
    } finally {
      setFiMcpLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%',
        minHeight: '60vh',
        gap: 2,
        width: '100%',
        maxWidth: 1200,
        mx: 'auto',
        p: { xs: 1, md: 4 }
      }}>
        <Typography variant="h4" color="primary" sx={{ textAlign: 'center', mb: 1 }}>
          {(() => {
            const messages = [
              "Loading your financial command center...",
              "Preparing your wealth dashboard...",
              "Assembling your financial cockpit...",
              "Building your money headquarters...",
              "Setting up your financial control room...",
              "Loading your wealth management hub...",
              "Preparing your financial mission control...",
              "Building your money operations center...",
              "Setting up your financial dashboard...",
              "Loading your wealth command center..."
            ];
            return messages[Math.floor(Math.random() * messages.length)];
          })()}
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Box sx={{ 
            width: 12, 
            height: 12, 
            borderRadius: '50%', 
            bgcolor: 'primary.main',
            animation: 'pulse 1.4s ease-in-out infinite both',
            animationDelay: '0s'
          }} />
          <Box sx={{ 
            width: 12, 
            height: 12, 
            borderRadius: '50%', 
            bgcolor: 'primary.main',
            animation: 'pulse 1.4s ease-in-out infinite both',
            animationDelay: '0.2s'
          }} />
          <Box sx={{ 
            width: 12, 
            height: 12, 
            borderRadius: '50%', 
            bgcolor: 'primary.main',
            animation: 'pulse 1.4s ease-in-out infinite both',
            animationDelay: '0.4s'
          }} />
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center' }}>
          Your financial dashboard is loading faster than your investments compound... almost
        </Typography>
      </Box>
    );
  }

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
            {getGreeting()}, {userProfile.name}
            {phone && (
              <Typography component="span" variant="h6" sx={{ ml: 2, fontWeight: 400, color: '#fff', opacity: 0.85 }}>
                ({phone})
              </Typography>
            )}
            <StarIcon sx={{ fontSize: 28, color: '#ffd600', verticalAlign: 'middle', ml: 1 }} />
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.92, fontWeight: 400 }}>
            Your personalized financial dashboard for <b>{new Date().toLocaleString('default', { month: 'long', year: 'numeric' })}</b>
          </Typography>
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

      {/* Fi-MCP Authentication Section */}
      <Box sx={{ mb: 3, p: 3, bgcolor: 'background.paper', borderRadius: 3, border: '1px solid #e0e0e0', boxShadow: 1 }}>
        <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          🔐 Connect to Real Financial Data
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
          Click below to authenticate with the fi-mcp server and access your real financial data instead of mock data.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            onClick={handleFiMcpAuth}
            disabled={fiMcpLoading}
            startIcon={fiMcpLoading ? <CircularProgress size={20} /> : null}
            sx={{ fontWeight: 600 }}
          >
            {fiMcpLoading ? 'Connecting...' : 'Connect to Real Data'}
          </Button>
          {fiMcpStatus && (
            <Alert 
              severity={fiMcpStatus.includes('Error') ? 'error' : fiMcpStatus.includes('Success') ? 'success' : 'info'}
              sx={{ flex: 1, minWidth: 200 }}
            >
              {fiMcpStatus}
            </Alert>
          )}
        </Box>
        {fiMcpLoginUrl && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
              🔗 Authentication URL Available
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              Click "Connect to Real Data" to open the authentication dialog and access the login URL.
            </Typography>
          </Box>
        )}
      </Box>

      {/* Main Dashboard Content */}
      <Grid container spacing={3} columns={12}>
        <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 8' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FinancialOverview data={data} animate onNetWorthClick={() => setSelectedTab && setSelectedTab('Portfolio')} onAssetAdded={globalRefresh} />
                          <EnhancedAssetAllocation data={data} />
          
          {/* Lazy-loaded Insights Component */}
          {insightsLoaded ? (
            <Insights data={data} />
          ) : (
            <Box sx={{ 
              background: 'rgba(255, 255, 255, 0.8)', 
              borderRadius: 3, 
              p: 3, 
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(25, 118, 210, 0.1)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight={700} color="primary">
                  Proactive Insights & Alerts
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Box sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s ease-in-out infinite both',
                    animationDelay: '0s'
                  }} />
                  <Box sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s ease-in-out infinite both',
                    animationDelay: '0.2s'
                  }} />
                  <Box sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s ease-in-out infinite both',
                    animationDelay: '0.4s'
                  }} />
                </Box>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 3 }}>
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
            </Box>
          )}
        </Box>
        
        <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 4' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Lazy-loaded HealthScore Component */}
          {healthScoreLoaded ? (
            <HealthScore data={data} />
          ) : (
            <Box sx={{ 
              background: 'rgba(255, 255, 255, 0.8)', 
              borderRadius: 3, 
              p: 3, 
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(25, 118, 210, 0.1)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight={700} color="primary">
                  Financial Health Score
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Box sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s ease-in-out infinite both',
                    animationDelay: '0s'
                  }} />
                  <Box sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s ease-in-out infinite both',
                    animationDelay: '0.2s'
                  }} />
                  <Box sx={{ 
                    width: 6, 
                    height: 6, 
                    borderRadius: '50%', 
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s ease-in-out infinite both',
                    animationDelay: '0.4s'
                  }} />
                </Box>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 3 }}>
                <Typography variant="h6" color="primary" sx={{ textAlign: 'center', mb: 1 }}>
                  {(() => {
                    const messages = [
                      "Analyzing your financial DNA...",
                      "Consulting with Warren Buffett's ghost...",
                      "Counting your virtual money...",
                      "Teaching your wallet to behave...",
                      "Summoning the money gods...",
                      "Converting coffee expenses to investments...",
                      "Calculating your financial karma...",
                      "Negotiating with your bank account...",
                      "Teaching your credit card some manners...",
                      "Convincing your savings to grow..."
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
                  This might take a moment... (or two)
                </Typography>
              </Box>
            </Box>
          )}
          
        </Box>
      </Grid>
      <RecentTransactions data={data} refreshTrigger={refreshTrigger} />

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

      {/* Fi-MCP Authentication Dialog */}
      <Dialog open={fiMcpAuthDialog} onClose={() => setFiMcpAuthDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          🔐 Fi-MCP Authentication Required
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            To access your real financial data, you need to authenticate with the fi-mcp server.
          </Typography>
          <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
            <strong>Step 1:</strong> Click the link below to open the authentication page in a new tab.
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Link 
              href={fiMcpLoginUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              sx={{ 
                display: 'inline-block',
                p: 2, 
                bgcolor: 'primary.main', 
                color: 'white', 
                borderRadius: 1,
                textDecoration: 'none',
                '&:hover': { bgcolor: 'primary.dark' }
              }}
            >
              🔗 Open Authentication Page
            </Link>
          </Box>
          <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
            <strong>Step 2:</strong> On the authentication page, enter your OTP or complete the verification process.
          </Typography>
          <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
            <strong>Step 3:</strong> After completing authentication, return here and click "Retry with Real Data".
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            <strong>Important:</strong> You must complete the authentication in your browser before clicking "Retry".
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFiMcpAuthDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleFiMcpRetry} 
            variant="contained"
            disabled={fiMcpLoading}
            startIcon={fiMcpLoading ? <CircularProgress size={20} /> : null}
          >
            {fiMcpLoading ? 'Loading...' : 'Retry with Real Data'}
          </Button>
        </DialogActions>
      </Dialog>
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
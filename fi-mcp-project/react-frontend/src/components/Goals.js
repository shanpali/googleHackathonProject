import React, { useState, useEffect } from 'react';
import { 
  Grid, Card, CardContent, Typography, Box, Button, TextField, Chip, Divider, 
  IconButton, CircularProgress, Alert, Dialog, DialogTitle, DialogContent, 
  DialogActions, Fab, Tooltip, List, ListItem, ListItemText, Paper,
  Stepper, Step, StepLabel, Avatar, Accordion, AccordionSummary, AccordionDetails,
  RadioGroup, Radio, FormControlLabel, FormControl, FormLabel, Slider
} from '@mui/material';
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
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ChatIcon from '@mui/icons-material/Chat';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
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

const PRIORITY_COLORS = {
  high: 'error',
  medium: 'warning',
  low: 'success'
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

  // Agentic goal creation states
  const [agentMode, setAgentMode] = useState(false);
  const [agentStep, setAgentStep] = useState(0);
  const [agentSuggestions, setAgentSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [selectedGoalType, setSelectedGoalType] = useState('general');
  const [userMessage, setUserMessage] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [customizingGoal, setCustomizingGoal] = useState(false);
  const [savingGoal, setSavingGoal] = useState(false);
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);
  const [lastCreatedGoal, setLastCreatedGoal] = useState(null);

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

  // Agentic goal creation functions
  const startAgentMode = () => {
    setAgentMode(true);
    setAgentStep(0);
    setConversationHistory([
      {
        type: 'agent',
        message: "Hi! I'm your AI financial advisor. I'll help you create realistic and achievable financial goals based on your current financial situation. What type of goals are you thinking about?",
        timestamp: new Date()
      }
    ]);
  };

  const handleAgentMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message to conversation
    const newConversation = [...conversationHistory, {
      type: 'user',
      message: message,
      timestamp: new Date()
    }];
    setConversationHistory(newConversation);

    // Check for goal-specific questions first
    if (customizingGoal && selectedSuggestion) {
      const goalSpecificAnswer = handleGoalSpecificQuestion(message);
      if (goalSpecificAnswer) {
        setConversationHistory([...newConversation, {
          type: 'agent',
          message: goalSpecificAnswer,
          timestamp: new Date()
        }]);
        return;
      }
    }

    setLoadingSuggestions(true);
    try {
      const response = await axios.post('/goal-suggestions', {
        message: message,
        goal_type: selectedGoalType
      }, { withCredentials: true });

      if (response.data.success) {
        // If we're in customization mode, provide goal customization guidance
        if (customizingGoal && selectedSuggestion) {
          const customizationResponse = {
            type: 'agent',
            message: `Perfect! I can help you customize your "${selectedSuggestion.name}" goal. Here's what I suggest:

• **Goal Name**: ${selectedSuggestion.name} (you can modify this)
• **Amount**: ₹${selectedSuggestion.amount.toLocaleString()} (adjust based on your capacity)
• **Target Year**: ${selectedSuggestion.year} (consider your timeline)
• **Monthly Savings**: ₹${selectedSuggestion.monthly_savings_needed.toLocaleString()}

You can modify these values in the form below. Would you like me to help you adjust any of these parameters?`,
            timestamp: new Date()
          };
          setConversationHistory([...newConversation, customizationResponse]);
        } else {
          // Normal goal suggestions flow
          setAgentSuggestions(response.data.suggestions);
          
          // Add agent response to conversation
          const agentResponse = {
            type: 'agent',
            message: response.data.analysis,
            suggestions: response.data.suggestions,
            timestamp: new Date()
          };
          setConversationHistory([...newConversation, agentResponse]);
          
          setAgentStep(1);
        }
      }
    } catch (error) {
      console.error('Error getting goal suggestions:', error);
      
      // Provide fallback response based on context
      let fallbackMessage = "I'm having trouble analyzing your financial profile right now. Let me provide some general goal suggestions.";
      
      if (customizingGoal && selectedSuggestion) {
        fallbackMessage = `I can help you customize your "${selectedSuggestion.name}" goal. You can adjust the amount, timeline, and other parameters in the form below. The suggested monthly savings is ₹${selectedSuggestion.monthly_savings_needed.toLocaleString()}.`;
      }
      
      setConversationHistory([...newConversation, {
        type: 'agent',
        message: fallbackMessage,
        timestamp: new Date()
      }]);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const selectSuggestion = (suggestion) => {
    setSelectedSuggestion(suggestion);
    setCustomizingGoal(true);
    setAgentStep(2);
    
    // Trigger agent interaction to help customize the goal
    const agentMessage = `I've selected the "${suggestion.name}" goal. Can you help me customize this goal? The suggested amount is ₹${suggestion.amount.toLocaleString()} by ${suggestion.year}.`;
    
    // Add user selection to conversation
    setConversationHistory(prev => [...prev, {
      type: 'user',
      message: `I want to create a ${suggestion.name} goal for ₹${suggestion.amount.toLocaleString()} by ${suggestion.year}`,
      timestamp: new Date()
    }]);
    
    // Trigger agent response
    setTimeout(() => {
      handleAgentMessage(agentMessage);
    }, 500);
  };

  const customizeAndSaveGoal = async () => {
    if (!selectedSuggestion) return;
    
    setSavingGoal(true);
    
    try {
      const newGoal = {
        type: selectedSuggestion.type,
        name: selectedSuggestion.name,
        amount: selectedSuggestion.amount,
        year: selectedSuggestion.year
      };
      
      // Add final agent confirmation message
      setConversationHistory(prev => [...prev, {
        type: 'agent',
        message: `Perfect! I'm creating your "${newGoal.name}" goal for ₹${newGoal.amount.toLocaleString()} by ${newGoal.year}. This will require monthly savings of ₹${selectedSuggestion.monthly_savings_needed.toLocaleString()}. I'll also generate personalized insights to help you achieve this goal!`,
        timestamp: new Date()
      }]);
      
      // Small delay to show the confirmation message
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newGoals = [...goals, newGoal];
      setGoals(newGoals);
      await saveGoalsToDB(newGoals);
      
      // Show success message
      setConversationHistory(prev => [...prev, {
        type: 'agent',
        message: `🎉 Success! Your "${newGoal.name}" goal has been created and saved. You can now get personalized insights based on this goal using the "Get Goal-Based Insights & Alerts" button below. I'll help you track your progress and provide recommendations to achieve this goal!`,
        timestamp: new Date()
      }]);
      
      // Show success notification in main area
      setLastCreatedGoal(newGoal);
      setShowSuccessNotification(true);
      
      // Auto-trigger goal-based insights after a short delay
      setTimeout(() => {
        handleRequestGoalInsights(false);
      }, 1000);
      
      // Reset agent mode after showing success message
      setTimeout(() => {
        setAgentMode(false);
        setAgentStep(0);
        setAgentSuggestions([]);
        setSelectedSuggestion(null);
        setCustomizingGoal(false);
        setConversationHistory([]);
        setUserMessage('');
        setSavingGoal(false);
      }, 4000);
    } catch (error) {
      console.error('Error saving goal:', error);
      setConversationHistory(prev => [...prev, {
        type: 'agent',
        message: "Sorry, there was an error saving your goal. Please try again.",
        timestamp: new Date()
      }]);
      setSavingGoal(false);
    }
  };

  // Helper function to handle goal-specific questions
  const handleGoalSpecificQuestion = (message) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('monthly') || lowerMessage.includes('savings')) {
      return `For your "${selectedSuggestion.name}" goal, you'll need to save ₹${selectedSuggestion.monthly_savings_needed.toLocaleString()} per month. This represents about ${((selectedSuggestion.monthly_savings_needed / (selectedSuggestion.amount / selectedSuggestion.year)) * 100).toFixed(1)}% of your goal amount annually.`;
    }
    
    if (lowerMessage.includes('timeline') || lowerMessage.includes('year') || lowerMessage.includes('time')) {
      return `Your goal timeline is ${selectedSuggestion.year} years. This gives you ${selectedSuggestion.year} years to save ₹${selectedSuggestion.amount.toLocaleString()}, which is a realistic timeline for this type of goal.`;
    }
    
    if (lowerMessage.includes('amount') || lowerMessage.includes('cost')) {
      return `The goal amount is ₹${selectedSuggestion.amount.toLocaleString()}. This is based on your financial profile and current savings capacity. You can adjust this amount based on your specific needs.`;
    }
    
    if (lowerMessage.includes('priority') || lowerMessage.includes('important')) {
      return `This goal is marked as ${selectedSuggestion.priority} priority. ${selectedSuggestion.reasoning}`;
    }
    
    return null; // Let the main agent handle other questions
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

  // Agent conversation steps
  const agentSteps = [
    'Tell me about your goals',
    'Choose from suggestions',
    'Customize your goal'
  ];

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
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<SmartToyIcon />}
            onClick={startAgentMode}
            sx={{ borderRadius: 2, fontWeight: 700, px: 3, py: 1.2, fontSize: 16, boxShadow: 2 }}
          >
            AI Goal Assistant
          </Button>
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
      </Box>

      {/* Agent Mode Dialog */}
      <Dialog 
        open={agentMode} 
        onClose={() => setAgentMode(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, minHeight: 600 }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 2, 
          bgcolor: 'primary.main', 
          color: 'white',
          borderRadius: '12px 12px 0 0'
        }}>
          <SmartToyIcon />
          <Box>
            <Typography variant="h6">AI Financial Goal Assistant</Typography>
            <Typography variant="caption">Let me help you create realistic goals</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          {/* Stepper */}
          <Stepper activeStep={agentStep} sx={{ mb: 3 }}>
            {agentSteps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Conversation Area */}
          <Box sx={{ mb: 3, maxHeight: 300, overflowY: 'auto' }}>
            {conversationHistory.map((msg, idx) => (
              <Box key={idx} sx={{ mb: 2, display: 'flex', justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start' }}>
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    bgcolor: msg.type === 'user' ? 'primary.main' : 'grey.100',
                    color: msg.type === 'user' ? 'white' : 'text.primary',
                    borderRadius: 2
                  }}
                >
                  <Typography variant="body1">{msg.message}</Typography>
                  
                  {/* Show suggestions if available */}
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Here are some personalized goal suggestions:
                      </Typography>
                      <Grid container spacing={2}>
                        {msg.suggestions.map((suggestion, sIdx) => (
                          <Grid item xs={12} sm={6} key={sIdx}>
                            <Card 
                              sx={{ 
                                cursor: 'pointer',
                                '&:hover': { boxShadow: 3 },
                                border: '2px solid transparent',
                                '&:hover': { borderColor: 'primary.main' }
                              }}
                              onClick={() => selectSuggestion(suggestion)}
                            >
                              <CardContent>
                                <Typography variant="h6" fontWeight={600}>
                                  {suggestion.name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  ₹{suggestion.amount.toLocaleString()} by {suggestion.year}
                                </Typography>
                                <Chip 
                                  label={suggestion.priority} 
                                  size="small" 
                                  color={PRIORITY_COLORS[suggestion.priority]}
                                  sx={{ mt: 1 }}
                                />
                                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                                  {suggestion.reasoning}
                                </Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  )}
                </Paper>
              </Box>
            ))}
            
            {loadingSuggestions && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body2" color="text.secondary">
                  Analyzing your financial profile...
                </Typography>
              </Box>
            )}
          </Box>

          {/* Input Area */}
          {agentStep < 3 && (
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label={customizingGoal ? "Ask me about customizing your goal..." : "Tell me about your financial goals..."}
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleAgentMessage(userMessage);
                    setUserMessage('');
                  }
                }}
              />
              <Button
                variant="contained"
                onClick={() => {
                  handleAgentMessage(userMessage);
                  setUserMessage('');
                }}
                disabled={!userMessage.trim() || loadingSuggestions}
              >
                Send
              </Button>
            </Box>
          )}

          {/* Goal Customization */}
          {customizingGoal && selectedSuggestion && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Customize Your Goal: {selectedSuggestion.name}
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Goal Name"
                    defaultValue={selectedSuggestion.name}
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Amount (₹)"
                    type="number"
                    defaultValue={selectedSuggestion.amount}
                    sx={{ mb: 2 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Target Year"
                    type="number"
                    defaultValue={selectedSuggestion.year}
                    sx={{ mb: 2 }}
                  />
                  <FormControl fullWidth>
                    <FormLabel>Goal Type</FormLabel>
                    <RadioGroup
                      value={selectedSuggestion.type}
                      row
                    >
                      <FormControlLabel value="short" control={<Radio />} label="Short Term" />
                      <FormControlLabel value="long" control={<Radio />} label="Long Term" />
                    </RadioGroup>
                  </FormControl>
                </Grid>
              </Grid>

              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Monthly Savings Needed: ₹{selectedSuggestion.monthly_savings_needed.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedSuggestion.reasoning}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setAgentMode(false)}>
            Cancel
          </Button>
          {customizingGoal && (
            <Button 
              variant="contained" 
              onClick={customizeAndSaveGoal}
              disabled={savingGoal}
              startIcon={savingGoal ? <CircularProgress size={20} color="inherit" /> : <CheckCircleIcon />}
            >
              {savingGoal ? 'Saving...' : 'Save Goal'}
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Success Notification */}
      {showSuccessNotification && lastCreatedGoal && (
        <Alert 
          severity="success" 
          sx={{ mb: 3 }}
          onClose={() => setShowSuccessNotification(false)}
          action={
            <Button color="inherit" size="small" onClick={() => setShowSuccessNotification(false)}>
              Dismiss
            </Button>
          }
        >
          <Typography variant="subtitle1" fontWeight={600}>
            Goal Created Successfully! 🎉
          </Typography>
          <Typography variant="body2">
            Your "{lastCreatedGoal.name}" goal has been saved. Goal-based insights are being generated...
          </Typography>
        </Alert>
      )}

      {/* Filter Bar */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 3, mt: 1 }}>
        <Button variant={filter === 'all' ? 'contained' : 'outlined'} onClick={() => setFilter('all')}>All</Button>
        <Button variant={filter === 'short' ? 'contained' : 'outlined'} color="primary" onClick={() => setFilter('short')}>Short Term</Button>
        <Button variant={filter === 'long' ? 'contained' : 'outlined'} color="success" onClick={() => setFilter('long')}>Long Term</Button>
      </Box>

      {/* Goals Grid */}
      {loading ? (
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
          <Typography variant="h6" color="text.secondary" mb={2}>
            No goals yet. Try our <b>AI Goal Assistant</b> for personalized suggestions!
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<SmartToyIcon />}
            onClick={startAgentMode}
            sx={{ mt: 2 }}
          >
            Get AI Goal Suggestions
          </Button>
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
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          my: 2, 
          gap: 2,
          width: '100%',
          maxWidth: 1200,
          mx: 'auto'
        }}>
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
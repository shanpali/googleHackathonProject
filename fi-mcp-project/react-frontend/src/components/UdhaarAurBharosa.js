import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Rating,
  IconButton,
  Fab,
  Alert,
  CircularProgress,
  Grid,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Container
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  PlayArrow as PlayIcon,
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Person as PersonIcon,
  Phone as PhoneIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  ExpandMore as ExpandMoreIcon,
  AutoAwesome as AutoAwesomeIcon,
  Psychology as PsychologyIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  Keyboard as KeyboardIcon
} from '@mui/icons-material';
import axios from 'axios';

export default function UdhaarAurBharosa() {
  const [lendings, setLendings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showLendDialog, setShowLendDialog] = useState(false);
  const [showRepayDialog, setShowRepayDialog] = useState(false);
  const [showAnalysisDialog, setShowAnalysisDialog] = useState(false);
  const [selectedLending, setSelectedLending] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState(null);
  const [voiceAnalysis, setVoiceAnalysis] = useState(null);
  const [analyzingVoice, setAnalyzingVoice] = useState(false);
  const [showVoiceSection, setShowVoiceSection] = useState(true);
  const [showPhoneDialog, setShowPhoneDialog] = useState(false);
  const [pendingAnalysis, setPendingAnalysis] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Form states
  const [lendForm, setLendForm] = useState({
    borrower_phone: '',
    borrower_name: '',
    amount: '',
    description: '',
    due_date: ''
  });

  const [repayForm, setRepayForm] = useState({
    trust_level: 'good',
    repayment_notes: ''
  });

  const [analysisForm, setAnalysisForm] = useState({
    borrower_phone: '',
    amount: ''
  });

  const [phoneInput, setPhoneInput] = useState('');

  useEffect(() => {
    fetchLendings();
  }, []);

  // Auto-hide success message after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const fetchLendings = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/udhaar/lendings', { withCredentials: true });
      setLendings(response.data.lendings || []);
    } catch (error) {
      setError('Failed to fetch lendings');
      console.error('Error fetching lendings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLendMoney = async () => {
    if (!lendForm.borrower_phone || !lendForm.amount) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/udhaar/lend', {
        borrower_phone: lendForm.borrower_phone,
        borrower_name: lendForm.borrower_name,
        amount: parseFloat(lendForm.amount),
        description: lendForm.description,
        due_date: lendForm.due_date,
        voice_note_url: audioUrl || '',
        voice_analysis: voiceAnalysis || {}
      }, { withCredentials: true });

      if (response.data.success) {
        setShowLendDialog(false);
        resetLendForm();
        fetchLendings();
        setError(null);
      }
    } catch (error) {
      setError('Failed to record lending transaction');
      console.error('Error lending money:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRepayMoney = async () => {
    if (!selectedLending) return;

    setLoading(true);
    try {
      const response = await axios.post('/udhaar/repay', {
        lending_id: selectedLending.id,
        trust_level: repayForm.trust_level,
        repayment_notes: repayForm.repayment_notes
      }, { withCredentials: true });

      if (response.data.success) {
        setShowRepayDialog(false);
        resetRepayForm();
        fetchLendings();
        setError(null);
      }
    } catch (error) {
      setError('Failed to update repayment status');
      console.error('Error repaying money:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLendingAnalysis = async () => {
    if (!analysisForm.borrower_phone || !analysisForm.amount) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/udhaar/lending-analysis', {
        borrower_phone: analysisForm.borrower_phone,
        amount: parseFloat(analysisForm.amount)
      }, { withCredentials: true });

      if (response.data) {
        // Show analysis results
        console.log('Lending Analysis:', response.data);
        setError(null);
      }
    } catch (error) {
      setError('Failed to analyze lending request');
      console.error('Error analyzing lending:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeVoiceRecording = async (blob) => {
    setAnalyzingVoice(true);
    try {
      const formData = new FormData();
      formData.append('voice_file', blob, 'voice_note.wav');

      const response = await axios.post('/udhaar/voice-analyze', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        const analysis = response.data.analysis;
        setVoiceAnalysis(analysis);
        
        // Auto-fill form with extracted information
        if (analysis.borrower_name) {
          setLendForm(prev => ({ ...prev, borrower_name: analysis.borrower_name }));
        }
        if (analysis.amount) {
          setLendForm(prev => ({ ...prev, amount: analysis.amount.toString() }));
        }
        if (analysis.purpose) {
          setLendForm(prev => ({ ...prev, description: `Purpose: ${analysis.purpose}` }));
        }
        if (analysis.due_date) {
          setLendForm(prev => ({ ...prev, due_date: analysis.due_date }));
        }

        // Auto-create lending entry if we have name and amount
        if (analysis.borrower_name && analysis.amount) {
          // Auto-fill the lending form
          const autoLendForm = {
            borrower_phone: analysis.borrower_phone || '',
            borrower_name: analysis.borrower_name,
            amount: analysis.amount.toString(),
            description: analysis.purpose ? `Purpose: ${analysis.purpose}` : '',
            due_date: analysis.due_date || ''
          };
          
          setLendForm(autoLendForm);
          
          // Show success message
          setError(null);
          
          // Auto-submit if we have name and amount (phone is optional)
          await handleAutoLend(autoLendForm);
        }

        // Auto-trigger lending analysis if we have key information
        if (analysis.borrower_name && analysis.amount) {
          // Check if we have phone number
          if (analysis.borrower_phone) {
            // We have all required info, trigger analysis directly
            setAnalysisForm({
              borrower_phone: analysis.borrower_phone,
              amount: analysis.amount.toString()
            });
            setShowAnalysisDialog(true);
          } else {
            // We need phone number, show dialog to ask for it
            setPendingAnalysis({
              borrower_name: analysis.borrower_name,
              amount: analysis.amount.toString()
            });
            setShowPhoneDialog(true);
          }
        }
      } else {
        // If backend analysis fails, create a basic transcript
        console.log('Backend analysis failed, creating fallback transcript');
        setVoiceAnalysis({
          transcript: 'Voice recorded successfully. Analysis pending...',
          borrower_name: null,
          borrower_phone: null,
          amount: null,
          purpose: null,
          due_date: null,
          confidence: 0.0
        });
      }
    } catch (error) {
      console.error('Error analyzing voice:', error);
      // Create a fallback transcript even if the API call fails
      setVoiceAnalysis({
        transcript: 'Voice recorded successfully. Could not analyze automatically.',
        borrower_name: null,
        borrower_phone: null,
        amount: null,
        purpose: null,
        due_date: null,
        confidence: 0.0
      });
      setError('Voice recorded but analysis failed. You can still use manual entry.');
    } finally {
      setAnalyzingVoice(false);
    }
  };

  const handleAutoLend = async (lendData) => {
    if (!lendData.borrower_name || !lendData.amount) {
      return; // Don't auto-submit if missing name or amount (phone is optional)
    }

    setLoading(true);
    try {
      const response = await axios.post('/udhaar/lend', {
        borrower_phone: lendData.borrower_phone || '', // Phone is optional
        borrower_name: lendData.borrower_name,
        amount: parseFloat(lendData.amount),
        description: lendData.description,
        due_date: lendData.due_date,
        voice_note_url: audioUrl || '',
        voice_analysis: voiceAnalysis || {}
      }, { withCredentials: true });

      if (response.data.success) {
        // Show success message
        setError(null);
        // Refresh lendings list
        fetchLendings();
        
        // Show success notification
        const phoneInfo = lendData.borrower_phone ? ` (${lendData.borrower_phone})` : '';
        setSuccessMessage(`Successfully lent ₹${lendData.amount} to ${lendData.borrower_name}${phoneInfo} via voice command!`);
      }
    } catch (error) {
      console.error('Error in auto-lending:', error);
      // Don't show error for auto-lending, let user handle manually
    } finally {
      setLoading(false);
    }
  };

  const handlePhoneSubmit = () => {
    if (phoneInput && pendingAnalysis) {
      setAnalysisForm({
        borrower_phone: phoneInput,
        amount: pendingAnalysis.amount
      });
      setShowPhoneDialog(false);
      setShowAnalysisDialog(true);
      setPhoneInput('');
      setPendingAnalysis(null);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      // Try browser-based speech recognition first
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-IN';

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          console.log('Browser transcript:', transcript);
          
          // Set basic transcript immediately
          setVoiceAnalysis({
            transcript: transcript,
            borrower_name: null,
            borrower_phone: null,
            amount: null,
            purpose: null,
            due_date: null,
            confidence: 0.5
          });
        };

        recognition.onerror = (event) => {
          console.log('Browser speech recognition error:', event.error);
        };

        recognition.start();
      }

      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        
        // Analyze voice recording with backend
        await analyzeVoiceRecording(blob);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      setError('Failed to start recording. Please allow microphone access.');
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const playRecording = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlaying(false);
      audio.play();
      setIsPlaying(true);
      setAudioElement(audio);
    }
  };

  const stopPlaying = () => {
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const resetLendForm = () => {
    setLendForm({
      borrower_phone: '',
      borrower_name: '',
      amount: '',
      description: '',
      due_date: ''
    });
    setAudioBlob(null);
    setAudioUrl(null);
    setVoiceAnalysis(null);
  };

  const resetRepayForm = () => {
    setRepayForm({
      trust_level: 'good',
      repayment_notes: ''
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'warning';
      case 'repaid': return 'success';
      case 'overdue': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <ScheduleIcon />;
      case 'repaid': return <CheckCircleIcon />;
      case 'overdue': return <WarningIcon />;
      default: return <PersonIcon />;
    }
  };

  const getTrustLevelColor = (level) => {
    switch (level) {
      case 'excellent': return 'success';
      case 'good': return 'primary';
      case 'poor': return 'error';
      default: return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  const formatAmount = (amount) => {
    return `₹${parseFloat(amount).toLocaleString()}`;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={700} color="primary">
          उधार और भरोसा
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Lending & Trust Management
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, bgcolor: 'primary.light', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Active Loans</Typography>
              <Typography variant="h4" fontWeight={700}>
                {lendings.filter(l => l.status === 'active').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, bgcolor: 'success.light', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Total Repaid</Typography>
              <Typography variant="h4" fontWeight={700}>
                {lendings.filter(l => l.status === 'repaid').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, bgcolor: 'warning.light', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Total Amount Lent</Typography>
              <Typography variant="h4" fontWeight={700}>
                ₹{lendings.reduce((sum, l) => sum + parseFloat(l.amount || 0), 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderRadius: 3, bgcolor: 'info.light', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Average Trust Rating</Typography>
              <Typography variant="h4" fontWeight={700}>
                {lendings.filter(l => l.trust_rating).length > 0 
                  ? (lendings.filter(l => l.trust_rating).reduce((sum, l) => sum + l.trust_rating, 0) / lendings.filter(l => l.trust_rating).length).toFixed(1)
                  : 'N/A'
                }
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Voice Recording Section - Main Page */}
      {showVoiceSection && (
        <Card sx={{ borderRadius: 3, mb: 4, bgcolor: 'background.paper' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <RecordVoiceOverIcon color="primary" sx={{ fontSize: 32 }} />
              <Box>
                <Typography variant="h5" fontWeight={700} gutterBottom>
                  Voice Recording for Lending
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Record your lending request and let AI extract the details automatically
                </Typography>
              </Box>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                {/* Voice Recording Controls */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    🎤 Record Your Lending Request
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                    {!isRecording ? (
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<MicIcon />}
                        onClick={startRecording}
                        disabled={loading}
                        sx={{ borderRadius: 2, px: 4 }}
                      >
                        Start Recording
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        color="error"
                        size="large"
                        startIcon={<StopIcon />}
                        onClick={stopRecording}
                        sx={{ borderRadius: 2, px: 4 }}
                      >
                        Stop Recording
                      </Button>
                    )}

                    {audioUrl && (
                      <Button
                        variant="outlined"
                        startIcon={isPlaying ? <StopIcon /> : <PlayIcon />}
                        onClick={isPlaying ? stopPlaying : playRecording}
                        sx={{ borderRadius: 2 }}
                      >
                        {isPlaying ? 'Stop' : 'Play'} Recording
                      </Button>
                    )}

                    {analyzingVoice && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={20} />
                        <Typography variant="body2">Analyzing voice...</Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Test Voice Recognition */}
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        const recognition = new SpeechRecognition();
                        recognition.continuous = false;
                        recognition.interimResults = false;
                        recognition.lang = 'en-IN';

                        recognition.onresult = (event) => {
                          const transcript = event.results[0][0].transcript;
                          console.log('Test transcript:', transcript);
                          setVoiceAnalysis({
                            transcript: transcript,
                            borrower_name: null,
                            borrower_phone: null,
                            amount: null,
                            purpose: null,
                            due_date: null,
                            confidence: 0.5
                          });
                        };

                        recognition.onerror = (event) => {
                          console.log('Test speech recognition error:', event.error);
                          setError(`Speech recognition error: ${event.error}`);
                        };

                        recognition.start();
                      } else {
                        setError('Speech recognition not supported in this browser');
                      }
                    }}
                    sx={{ borderRadius: 2, mb: 2 }}
                  >
                    Test Voice Recognition
                  </Button>

                  <Typography variant="body2" color="text.secondary">
                    <strong>Example:</strong> "I need to borrow 5000 rupees from Rahul Kumar for medical emergency"
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Or:</strong> "Can I lend 10000 to Priya at 9876543210 for education?"
                  </Typography>
                </Box>

                {/* Converted Text Display */}
                {voiceAnalysis && (
                  <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2, border: '1px solid', borderColor: 'grey.200' }}>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom color="primary">
                      📝 Converted Text
                    </Typography>
                    <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                      "{voiceAnalysis.transcript}"
                    </Typography>
                    {voiceAnalysis.confidence > 0 && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        Confidence: {(voiceAnalysis.confidence * 100).toFixed(1)}%
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Debug Info */}
                {isRecording && (
                  <Box sx={{ mt: 2, p: 1, bgcolor: 'info.light', borderRadius: 1 }}>
                    <Typography variant="caption" color="white">
                      🎤 Recording in progress... Speak clearly
                    </Typography>
                  </Box>
                )}
              </Grid>

              <Grid item xs={12} md={6}>
                {/* Voice Analysis Results */}
                {voiceAnalysis ? (
                  <Box>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      <AutoAwesomeIcon color="primary" sx={{ mr: 1 }} />
                      AI Analysis Results
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {voiceAnalysis.borrower_name && (
                        <Typography variant="body2">
                          <strong>Borrower Name:</strong> {voiceAnalysis.borrower_name}
                        </Typography>
                      )}
                      {voiceAnalysis.borrower_phone && (
                        <Typography variant="body2">
                          <strong>Phone Number:</strong> {voiceAnalysis.borrower_phone}
                        </Typography>
                      )}
                      {voiceAnalysis.amount && (
                        <Typography variant="body2">
                          <strong>Amount:</strong> ₹{voiceAnalysis.amount.toLocaleString()}
                        </Typography>
                      )}
                      {voiceAnalysis.purpose && (
                        <Typography variant="body2">
                          <strong>Purpose:</strong> {voiceAnalysis.purpose}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        <strong>Confidence:</strong> {(voiceAnalysis.confidence * 100).toFixed(1)}%
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                      <Button
                        variant="contained"
                        onClick={() => setShowLendDialog(true)}
                        sx={{ borderRadius: 2 }}
                        startIcon={<AddIcon />}
                      >
                        Use This Data to Lend Money
                      </Button>
                      {voiceAnalysis.borrower_name && voiceAnalysis.amount && (
                        <Button
                          variant="outlined"
                          onClick={() => {
                            if (voiceAnalysis.borrower_phone) {
                              setAnalysisForm({
                                borrower_phone: voiceAnalysis.borrower_phone,
                                amount: voiceAnalysis.amount.toString()
                              });
                              setShowAnalysisDialog(true);
                            } else {
                              setPendingAnalysis({
                                borrower_name: voiceAnalysis.borrower_name,
                                amount: voiceAnalysis.amount.toString()
                              });
                              setShowPhoneDialog(true);
                            }
                          }}
                          sx={{ borderRadius: 2 }}
                          startIcon={<PsychologyIcon />}
                        >
                          Analyze Lending Request
                        </Button>
                      )}
                    </Box>
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
                    <RecordVoiceOverIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="body2" color="text.secondary" align="center">
                      Record your voice to see AI analysis here
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />
            
            {/* Alternative Options */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="outlined"
                startIcon={<KeyboardIcon />}
                onClick={() => setShowLendDialog(true)}
                sx={{ borderRadius: 2 }}
              >
                Manual Entry Instead
              </Button>
              <Button
                variant="outlined"
                startIcon={<PsychologyIcon />}
                onClick={() => setShowAnalysisDialog(true)}
                sx={{ borderRadius: 2 }}
              >
                Analyze Lending Request
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowLendDialog(true)}
          sx={{ borderRadius: 2 }}
        >
          Manual Lend Money
        </Button>
        <Button
          variant="outlined"
          startIcon={<PsychologyIcon />}
          onClick={() => setShowAnalysisDialog(true)}
          sx={{ borderRadius: 2 }}
        >
          Analyze Lending Request
        </Button>
        <Button
          variant="outlined"
          onClick={() => setShowVoiceSection(!showVoiceSection)}
          sx={{ borderRadius: 2 }}
        >
          {showVoiceSection ? 'Hide' : 'Show'} Voice Recording
        </Button>
      </Box>

      {/* Lendings Table */}
      <Card sx={{ borderRadius: 3, mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight={700}>Lending History</Typography>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{ boxShadow: 0 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>BORROWER</TableCell>
                    <TableCell>AMOUNT</TableCell>
                    <TableCell>DESCRIPTION</TableCell>
                    <TableCell>DUE DATE</TableCell>
                    <TableCell>STATUS</TableCell>
                    <TableCell>TRUST RATING</TableCell>
                    <TableCell>ACTIONS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {lendings.length > 0 ? lendings.map((lending) => (
                    <TableRow key={lending.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            <PhoneIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>
                              {lending.borrower_name || lending.borrower_phone}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {lending.borrower_phone}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={700} color="primary">
                          {formatAmount(lending.amount)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                          {lending.description || 'No description'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(lending.due_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(lending.status)}
                          label={lending.status.toUpperCase()}
                          color={getStatusColor(lending.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {lending.trust_level ? (
                          <Chip
                            label={lending.trust_level.toUpperCase()}
                            color={getTrustLevelColor(lending.trust_level)}
                            size="small"
                          />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Pending
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {lending.status === 'active' && (
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => {
                              setSelectedLending(lending);
                              setShowRepayDialog(true);
                            }}
                          >
                            Mark Repaid
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography variant="body2" color="text.secondary">
                          No lending transactions yet
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Phone Number Input Dialog */}
      <Dialog open={showPhoneDialog} onClose={() => setShowPhoneDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={700}>Enter Borrower Phone Number</Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Alert severity="info">
              <Typography variant="body2">
                We extracted {pendingAnalysis?.borrower_name} and ₹{pendingAnalysis?.amount} from your voice recording. 
                Please enter the borrower's phone number to analyze the lending request.
              </Typography>
            </Alert>
            
            <TextField
              label="Borrower Phone Number"
              value={phoneInput}
              onChange={(e) => setPhoneInput(e.target.value)}
              fullWidth
              required
              placeholder="9876543210"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPhoneDialog(false)}>Cancel</Button>
          <Button
            onClick={handlePhoneSubmit}
            variant="contained"
            disabled={!phoneInput}
          >
            Analyze Lending Request
          </Button>
        </DialogActions>
      </Dialog>

      {/* Lend Money Dialog */}
      <Dialog open={showLendDialog} onClose={() => setShowLendDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={700}>Lend Money</Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Borrower Phone Number"
              value={lendForm.borrower_phone}
              onChange={(e) => setLendForm({ ...lendForm, borrower_phone: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Borrower Name"
              value={lendForm.borrower_name}
              onChange={(e) => setLendForm({ ...lendForm, borrower_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Amount (₹)"
              type="number"
              value={lendForm.amount}
              onChange={(e) => setLendForm({ ...lendForm, amount: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={lendForm.description}
              onChange={(e) => setLendForm({ ...lendForm, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
            <TextField
              label="Due Date"
              type="date"
              value={lendForm.due_date}
              onChange={(e) => setLendForm({ ...lendForm, due_date: e.target.value })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />

            {/* Voice Recording Section in Dialog */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Voice Note with AI Analysis (Optional)
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                {!isRecording ? (
                  <Button
                    variant="outlined"
                    startIcon={<MicIcon />}
                    onClick={startRecording}
                    disabled={loading}
                  >
                    Start Recording
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<StopIcon />}
                    onClick={stopRecording}
                  >
                    Stop Recording
                  </Button>
                )}

                {audioUrl && (
                  <Button
                    variant="outlined"
                    startIcon={isPlaying ? <StopIcon /> : <PlayIcon />}
                    onClick={isPlaying ? stopPlaying : playRecording}
                  >
                    {isPlaying ? 'Stop' : 'Play'} Recording
                  </Button>
                )}

                {analyzingVoice && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={20} />
                    <Typography variant="body2">Analyzing voice...</Typography>
                  </Box>
                )}
              </Box>

              {/* Voice Analysis Results */}
              {voiceAnalysis && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AutoAwesomeIcon color="primary" />
                      <Typography variant="subtitle2">AI Voice Analysis Results</Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Typography variant="body2">
                        <strong>Transcript:</strong> {voiceAnalysis.transcript}
                      </Typography>
                      {voiceAnalysis.borrower_name && (
                        <Typography variant="body2">
                          <strong>Borrower Name:</strong> {voiceAnalysis.borrower_name}
                        </Typography>
                      )}
                      {voiceAnalysis.borrower_phone && (
                        <Typography variant="body2">
                          <strong>Phone Number:</strong> {voiceAnalysis.borrower_phone}
                        </Typography>
                      )}
                      {voiceAnalysis.amount && (
                        <Typography variant="body2">
                          <strong>Amount:</strong> ₹{voiceAnalysis.amount.toLocaleString()}
                        </Typography>
                      )}
                      {voiceAnalysis.purpose && (
                        <Typography variant="body2">
                          <strong>Purpose:</strong> {voiceAnalysis.purpose}
                        </Typography>
                      )}
                      <Typography variant="body2">
                        <strong>Confidence:</strong> {(voiceAnalysis.confidence * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowLendDialog(false)}>Cancel</Button>
          <Button
            onClick={handleLendMoney}
            variant="contained"
            disabled={loading || !lendForm.borrower_phone || !lendForm.amount}
          >
            {loading ? <CircularProgress size={20} /> : 'Lend Money'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Repay Money Dialog */}
      <Dialog open={showRepayDialog} onClose={() => setShowRepayDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={700}>Mark as Repaid</Typography>
        </DialogTitle>
        <DialogContent>
          {selectedLending && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <Alert severity="info">
                <Typography variant="body2">
                  Marking repayment for ₹{formatAmount(selectedLending.amount)} to {selectedLending.borrower_name || selectedLending.borrower_phone}
                </Typography>
              </Alert>

              <Box>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Trust Rating
                </Typography>
                <FormControl fullWidth>
                  <InputLabel>Trust Level</InputLabel>
                  <Select
                    value={repayForm.trust_level}
                    onChange={(e) => setRepayForm({ ...repayForm, trust_level: e.target.value })}
                    label="Trust Level"
                  >
                    <MenuItem value="excellent">Excellent - Very trustworthy</MenuItem>
                    <MenuItem value="good">Good - Generally reliable</MenuItem>
                    <MenuItem value="poor">Poor - Not recommended</MenuItem>
                  </Select>
                </FormControl>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Rate how trustworthy this borrower was during repayment
                </Typography>
              </Box>

              <TextField
                label="Repayment Notes"
                value={repayForm.repayment_notes}
                onChange={(e) => setRepayForm({ ...repayForm, repayment_notes: e.target.value })}
                fullWidth
                multiline
                rows={3}
                placeholder="Any notes about the repayment..."
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRepayDialog(false)}>Cancel</Button>
          <Button
            onClick={handleRepayMoney}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Mark Repaid'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Lending Analysis Dialog */}
      <Dialog open={showAnalysisDialog} onClose={() => setShowAnalysisDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6" fontWeight={700}>Analyze Lending Request</Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Get AI-powered analysis of whether you should lend money based on your financial position and borrower's trust rating.
            </Typography>
            
            <TextField
              label="Borrower Phone Number"
              value={analysisForm.borrower_phone}
              onChange={(e) => setAnalysisForm({ ...analysisForm, borrower_phone: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Requested Amount (₹)"
              type="number"
              value={analysisForm.amount}
              onChange={(e) => setAnalysisForm({ ...analysisForm, amount: e.target.value })}
              fullWidth
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAnalysisDialog(false)}>Cancel</Button>
          <Button
            onClick={handleLendingAnalysis}
            variant="contained"
            disabled={loading || !analysisForm.borrower_phone || !analysisForm.amount}
          >
            {loading ? <CircularProgress size={20} /> : 'Analyze Request'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="lend money"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setShowLendDialog(true)}
      >
        <MoneyIcon />
      </Fab>
    </Container>
  );
} 
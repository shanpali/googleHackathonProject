import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Collapse,
  IconButton
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import RefreshIcon from '@mui/icons-material/Refresh';
import axios from 'axios';

export default function HealthScore({ data }) {
  const [score, setScore] = useState(null);
  const [category, setCategory] = useState(null);
  const [breakdown, setBreakdown] = useState({});
  const [strengths, setStrengths] = useState([]);
  const [weaknesses, setWeaknesses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [overallAnalysis, setOverallAnalysis] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [cached, setCached] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    strengths: false,
    weaknesses: false,
    recommendations: false
  });

  const fetchHealthScore = (refresh = false) => {
    setLoading(true);
    setError(null);
    
    const url = refresh ? '/health-score?refresh=true' : '/health-score';
    
    axios.get(url, { withCredentials: true })
      .then(res => {
        if (res.data && typeof res.data.score === 'number') {
          setScore(res.data.score);
          setCategory(res.data.category);
          setBreakdown(res.data.breakdown || {});
          setStrengths(res.data.strengths || []);
          setWeaknesses(res.data.weaknesses || []);
          setRecommendations(res.data.recommendations || []);
          setOverallAnalysis(res.data.overall_analysis || '');
          setLastUpdated(res.data.last_updated);
          setCached(res.data.cached || false);
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

  const getScoreColor = (score) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getCategoryColor = (category) => {
    if (category === 'Excellent') return '#4caf50';
    if (category === 'Good') return '#2196f3';
    if (category === 'Fair') return '#ff9800';
    return '#f44336';
  };

  const handleSectionToggle = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <Card sx={{ borderRadius: 3, mb: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" fontWeight={700} color="primary">
            Financial Health Score
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
            <IconButton 
              onClick={() => fetchHealthScore(true)} 
              disabled={loading}
              size="small"
              sx={{ 
                color: '#1976d2',
                '&:hover': { backgroundColor: 'rgba(25, 118, 210, 0.1)' }
              }}
            >
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4, gap: 2 }}>
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
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!loading && !error && (
          <Grid container spacing={3}>
            {/* Score and Category Breakdown */}
            <Grid item xs={12} md={4}>
              <Card sx={{ 
                borderRadius: 2, 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                textAlign: 'center',
                p: 3,
                height: 'fit-content'
              }}>
                <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                  <svg width={120} height={120}>
                    <circle 
                      cx={60} cy={60} r={54} 
                      fill="none" 
                      stroke="rgba(255,255,255,0.3)" 
                      strokeWidth={8} 
                    />
                    <circle 
                      cx={60} cy={60} r={54} 
                      fill="none" 
                      stroke="white" 
                      strokeWidth={8} 
                      strokeDasharray={339.3} 
                      strokeDashoffset={339.3 - (score || 0) * 3.393}
                      strokeLinecap="round"
                    />
                  </svg>
                  <Typography 
                    variant="h3" 
                    sx={{ 
                      position: 'absolute', 
                      top: '50%', 
                      left: '50%', 
                      transform: 'translate(-50%, -50%)',
                      fontWeight: 700
                    }}
                  >
                    {score ?? '--'}
                  </Typography>
                </Box>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                  out of 100
                </Typography>
                {category && (
                  <Chip
                    label={category}
                    sx={{
                      backgroundColor: getCategoryColor(category),
                      color: 'white',
                      fontWeight: 600,
                      fontSize: '0.9rem'
                    }}
                  />
                )}
              </Card>
            </Grid>

            {/* Category Breakdown */}
            <Grid item xs={12} md={8}>
              <Card sx={{ borderRadius: 2, p: 2, height: 'fit-content' }}>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2, color: 'text.primary' }}>
                  Category Breakdown
                </Typography>
                {Object.keys(breakdown).length > 0 && (
                  <List dense>
                    {Object.entries(breakdown).map(([key, value]) => (
                      <ListItem key={key} sx={{ py: 1, px: 0 }}>
                        <ListItemText
                          primary={
                            <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>
                              {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </Typography>
                          }
                        />
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, minWidth: 120 }}>
                          <Box sx={{ width: 80 }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={value} 
                              sx={{ 
                                height: 8, 
                                borderRadius: 5,
                                backgroundColor: 'rgba(0,0,0,0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: getScoreColor(value)
                                }
                              }} 
                            />
                          </Box>
                          <Typography 
                            variant="body2" 
                            fontWeight={700}
                            color={getScoreColor(value)}
                          >
                            {value}/100
                          </Typography>
                        </Box>
                      </ListItem>
                    ))}
                  </List>
                )}
              </Card>
            </Grid>

            {/* Strengths Card */}
            {strengths.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card sx={{ 
                  borderRadius: 2, 
                  border: '2px solid #e8f5e8',
                  background: 'linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%)',
                  height: 'fit-content'
                }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      mb: 2,
                      cursor: 'pointer'
                    }}
                    onClick={() => handleSectionToggle('strengths')}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <CheckCircle sx={{ color: '#4caf50', mr: 1, fontSize: 24 }} />
                        <Typography variant="h6" fontWeight={600} color="#4caf50">
                          Strengths ({strengths.length})
                        </Typography>
                      </Box>
                      <IconButton size="small" sx={{ color: '#4caf50' }}>
                        {expandedSections.strengths ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </Box>
                    <Collapse in={expandedSections.strengths}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        {strengths.map((strength, index) => (
                          <Box key={index} sx={{ 
                            p: 1.5, 
                            backgroundColor: 'rgba(76, 175, 80, 0.1)', 
                            borderRadius: 1.5,
                            border: '1px solid rgba(76, 175, 80, 0.2)'
                          }}>
                            <Typography variant="body2" sx={{ 
                              fontSize: '0.875rem', 
                              lineHeight: 1.4,
                              fontWeight: 500,
                              color: '#2e7d32'
                            }}>
                              {typeof strength === 'string' ? strength : (strength.description || strength.title || JSON.stringify(strength))}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    </Collapse>
                    {!expandedSections.strengths && strengths.length > 0 && (
                      <Box sx={{ 
                        p: 1.5, 
                        backgroundColor: 'rgba(76, 175, 80, 0.1)', 
                        borderRadius: 1.5,
                        border: '1px solid rgba(76, 175, 80, 0.2)'
                      }}>
                        <Typography variant="body2" sx={{ 
                          fontSize: '0.875rem', 
                          lineHeight: 1.4,
                          fontWeight: 500,
                          color: '#2e7d32'
                        }}>
                          {typeof strengths[0] === 'string' ? strengths[0] : (strengths[0].description || strengths[0].title || JSON.stringify(strengths[0]))}
                        </Typography>
                        {strengths.length > 1 && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
                            +{strengths.length - 1} more strengths (click to expand)
                          </Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Areas to Improve Card */}
            {weaknesses.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card sx={{ 
                  borderRadius: 2, 
                  border: '2px solid #ffebee',
                  background: 'linear-gradient(135deg, #fff8f8 0%, #ffebee 100%)',
                  height: 'fit-content'
                }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      mb: 2,
                      cursor: 'pointer'
                    }}
                    onClick={() => handleSectionToggle('weaknesses')}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Warning sx={{ color: '#f44336', mr: 1, fontSize: 24 }} />
                        <Typography variant="h6" fontWeight={600} color="#f44336">
                          Areas to Improve ({weaknesses.length})
                        </Typography>
                      </Box>
                      <IconButton size="small" sx={{ color: '#f44336' }}>
                        {expandedSections.weaknesses ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </Box>
                    <Collapse in={expandedSections.weaknesses}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        {weaknesses.map((weakness, index) => (
                          <Box key={index} sx={{ 
                            p: 1.5, 
                            backgroundColor: 'rgba(244, 67, 54, 0.1)', 
                            borderRadius: 1.5,
                            border: '1px solid rgba(244, 67, 54, 0.2)'
                          }}>
                            <Typography variant="body2" sx={{ 
                              fontSize: '0.875rem', 
                              lineHeight: 1.4,
                              fontWeight: 500,
                              color: '#d32f2f'
                            }}>
                              {typeof weakness === 'string' ? weakness : (weakness.description || weakness.title || JSON.stringify(weakness))}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    </Collapse>
                    {!expandedSections.weaknesses && weaknesses.length > 0 && (
                      <Box sx={{ 
                        p: 1.5, 
                        backgroundColor: 'rgba(244, 67, 54, 0.1)', 
                        borderRadius: 1.5,
                        border: '1px solid rgba(244, 67, 54, 0.2)'
                      }}>
                        <Typography variant="body2" sx={{ 
                          fontSize: '0.875rem', 
                          lineHeight: 1.4,
                          fontWeight: 500,
                          color: '#d32f2f'
                        }}>
                          {typeof weaknesses[0] === 'string' ? weaknesses[0] : (weaknesses[0].description || weaknesses[0].title || JSON.stringify(weaknesses[0]))}
                        </Typography>
                        {weaknesses.length > 1 && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
                            +{weaknesses.length - 1} more areas to improve (click to expand)
                          </Typography>
                        )}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Recommendations Card */}
            {recommendations.length > 0 && (
              <Grid item xs={12}>
                <Card sx={{ 
                  borderRadius: 2, 
                  border: '2px solid #e3f2fd',
                  background: 'linear-gradient(135deg, #f8fbff 0%, #e3f2fd 100%)'
                }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      mb: 2,
                      cursor: 'pointer'
                    }}
                    onClick={() => handleSectionToggle('recommendations')}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <TrendingUp sx={{ color: '#2196f3', mr: 1, fontSize: 24 }} />
                        <Typography variant="h6" fontWeight={600} color="#2196f3">
                          Recommendations ({recommendations.length})
                        </Typography>
                      </Box>
                      <IconButton size="small" sx={{ color: '#2196f3' }}>
                        {expandedSections.recommendations ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </Box>
                    <Collapse in={expandedSections.recommendations}>
                      <Grid container spacing={2}>
                        {recommendations.map((recommendation, index) => (
                          <Grid item xs={12} sm={6} key={index}>
                            <Box sx={{ 
                              p: 2, 
                              backgroundColor: 'rgba(33, 150, 243, 0.1)', 
                              borderRadius: 2,
                              border: '1px solid rgba(33, 150, 243, 0.2)',
                              height: '100%'
                            }}>
                              <Typography variant="body2" sx={{ 
                                fontSize: '0.875rem', 
                                lineHeight: 1.4,
                                fontWeight: 500,
                                color: '#1976d2'
                              }}>
                                {typeof recommendation === 'string' ? recommendation : (recommendation.description || recommendation.title || JSON.stringify(recommendation))}
                              </Typography>
                            </Box>
                          </Grid>
                        ))}
                      </Grid>
                    </Collapse>
                    {!expandedSections.recommendations && recommendations.length > 0 && (
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Box sx={{ 
                            p: 2, 
                            backgroundColor: 'rgba(33, 150, 243, 0.1)', 
                            borderRadius: 2,
                            border: '1px solid rgba(33, 150, 243, 0.2)',
                            height: '100%'
                          }}>
                            <Typography variant="body2" sx={{ 
                              fontSize: '0.875rem', 
                              lineHeight: 1.4,
                              fontWeight: 500,
                              color: '#1976d2'
                            }}>
                              {typeof recommendations[0] === 'string' ? recommendations[0] : (recommendations[0].description || recommendations[0].title || JSON.stringify(recommendations[0]))}
                            </Typography>
                          </Box>
                        </Grid>
                        {recommendations.length > 1 && (
                          <Grid item xs={12} sm={6}>
                            <Box sx={{ 
                              p: 2, 
                              backgroundColor: 'rgba(33, 150, 243, 0.1)', 
                              borderRadius: 2,
                              border: '1px solid rgba(33, 150, 243, 0.2)',
                              height: '100%'
                            }}>
                              <Typography variant="body2" sx={{ 
                                fontSize: '0.875rem', 
                                lineHeight: 1.4,
                                fontWeight: 500,
                                color: '#1976d2'
                              }}>
                                {typeof recommendations[1] === 'string' ? recommendations[1] : (recommendations[1].description || recommendations[1].title || JSON.stringify(recommendations[1]))}
                              </Typography>
                            </Box>
                          </Grid>
                        )}
                        {recommendations.length > 2 && (
                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', fontStyle: 'italic', display: 'block' }}>
                              +{recommendations.length - 2} more recommendations (click to expand)
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}
      </CardContent>
    </Card>
  );
} 
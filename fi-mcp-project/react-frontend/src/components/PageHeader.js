import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Paper,
  Toolbar,
  Typography,
  Box,
  InputBase,
  IconButton,
  Badge,
  Popover,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import NotificationsIcon from '@mui/icons-material/Notifications';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

// Dummy search data
const searchData = [
  { id: 1, title: 'Portfolio Overview', description: 'View your complete investment portfolio', category: 'Portfolio', url: '/portfolio' },
  { id: 2, title: 'Mutual Fund Returns', description: 'Check your mutual fund performance', category: 'Investments', url: '/portfolio' },
  { id: 3, title: 'Tax Planning', description: 'Optimize your tax-saving investments', category: 'Tax', url: '/tax-planning' },
  { id: 4, title: 'Insurance Coverage', description: 'Review your insurance policies', category: 'Insurance', url: '/portfolio' },
  { id: 5, title: 'Savings Account', description: 'Check your savings account balance', category: 'Banking', url: '/portfolio' },
  { id: 6, title: 'Investment Growth', description: 'Track your investment growth over time', category: 'Analytics', url: '/reports' },
  { id: 7, title: 'Nominee Details', description: 'Update nominee information', category: 'Safeguard', url: '/nominee-safeguard' },
  { id: 8, title: 'ELSS Funds', description: 'Equity Linked Savings Scheme options', category: 'Tax', url: '/tax-planning' },
  { id: 9, title: 'Fixed Deposits', description: 'View your fixed deposit investments', category: 'Banking', url: '/portfolio' },
  { id: 10, title: 'Monthly Reports', description: 'Generate monthly financial reports', category: 'Reports', url: '/reports' }
];

export default function PageHeader({ title }) {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Search functionality state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchAnchor, setSearchAnchor] = useState(null);
  const [showSearchResults, setShowSearchResults] = useState(false);

  // Fetch notifications from JSON file
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        // In a real app, this would be an API endpoint
        // For now, we'll simulate fetching from a local JSON file
        const response = await axios.get('/data/notifications.json');
        setNotifications(response.data.notifications);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch notifications:', err);
        setError('Failed to load notifications');
        // Fallback to default notifications
        setNotifications([
          {
            id: 1,
            type: 'warning',
            title: 'Tax Planning Reminder',
            message: 'Your tax-saving investments are due soon. Consider ELSS funds.',
            timestamp: '2 hours ago',
            read: false
          },
          {
            id: 2,
            type: 'success',
            title: 'Portfolio Update',
            message: 'Your mutual fund portfolio gained ₹5,230 this month.',
            timestamp: '1 day ago',
            read: false
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const handleNotificationClick = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationAnchor(null);
  };

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  };

  const handleNotificationAction = (notification) => {
    if (notification.actionUrl) {
      navigate(notification.actionUrl);
      handleNotificationClose();
    }
    markAsRead(notification.id);
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'warning': return <WarningIcon sx={{ color: '#f59e0b' }} />;
      case 'success': return <CheckCircleIcon sx={{ color: '#10b981' }} />;
      case 'error': return <ErrorIcon sx={{ color: '#ef4444' }} />;
      default: return <InfoIcon sx={{ color: '#3b82f6' }} />;
    }
  };

  // Search functionality
  const handleSearchChange = (event) => {
    const query = event.target.value;
    setSearchQuery(query);
    
    if (query.trim().length >= 3) {
      const filtered = searchData.filter(item =>
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.description.toLowerCase().includes(query.toLowerCase()) ||
        item.category.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(filtered);
      setShowSearchResults(true);
    } else {
      setSearchResults([]);
      setShowSearchResults(false);
    }
  };

  const handleSearchFocus = (event) => {
    setSearchAnchor(event.currentTarget);
    if (searchQuery.trim().length >= 3) {
      setShowSearchResults(true);
    }
  };

  const handleSearchBlur = () => {
    // Delay hiding to allow clicking on results
    setTimeout(() => {
      setShowSearchResults(false);
      setSearchAnchor(null);
    }, 200);
  };

  const handleSearchResultClick = (result) => {
    setSearchQuery(result.title);
    setShowSearchResults(false);
    setSearchAnchor(null);
    if (result.url) {
      navigate(result.url);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        bgcolor: 'white', 
        borderBottom: '1px solid #e8eaed',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: 4, py: 2 }}>
        <Typography variant="h5" fontWeight={600} color="#1f2937">
          {title}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Search Bar */}
          <Paper
            component="form"
            sx={{
              p: '4px 16px',
              display: 'flex',
              alignItems: 'center',
              width: 320,
              bgcolor: '#f8fafc',
              borderRadius: '12px',
              border: '1px solid #e8eaed',
              position: 'relative',
              '&:hover': {
                bgcolor: '#f1f5f9',
                border: '1px solid #cbd5e1'
              }
            }}
            onSubmit={(e) => e.preventDefault()}
          >
            <SearchIcon sx={{ color: '#6b7280', mr: 1 }} />
            <InputBase
              sx={{ ml: 1, flex: 1, fontSize: '14px' }}
              placeholder="Ask me anything about your finances..."
              inputProps={{ 'aria-label': 'search finances' }}
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={handleSearchFocus}
              onBlur={handleSearchBlur}
            />
            {searchQuery && (
              <IconButton 
                size="small" 
                onClick={clearSearch}
                sx={{ p: 0.5 }}
              >
                <Typography sx={{ fontSize: '18px', color: '#6b7280' }}>×</Typography>
              </IconButton>
            )}
          </Paper>

          {/* Search Results Popover */}
          <Popover
            open={showSearchResults && searchResults.length > 0}
            anchorEl={searchAnchor}
            onClose={() => setShowSearchResults(false)}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'left',
            }}
            PaperProps={{
              sx: {
                width: 320,
                maxHeight: 400,
                mt: 1,
                borderRadius: '12px',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)'
              }
            }}
          >
            <Box sx={{ p: 2 }}>
              <Typography variant="subtitle2" fontWeight={600} color="#6b7280" mb={1}>
                Search Results ({searchResults.length})
              </Typography>
            </Box>
            <Divider />
            <List sx={{ p: 0, maxHeight: 300, overflow: 'auto' }}>
              {searchResults.slice(0, 8).map((result) => (
                <ListItem
                  key={result.id}
                  sx={{
                    py: 1.5,
                    px: 2,
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'rgba(59, 130, 246, 0.05)'
                    }
                  }}
                  onClick={() => handleSearchResultClick(result)}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <SearchIcon sx={{ color: '#6b7280', fontSize: 18 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {result.title}
                        </Typography>
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            bgcolor: '#f0f9ff',
                            color: '#2563eb',
                            px: 1,
                            py: 0.25,
                            borderRadius: 1,
                            fontSize: '10px'
                          }}
                        >
                          {result.category}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {result.description}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
              {searchResults.length > 8 && (
                <ListItem sx={{ py: 1, px: 2, textAlign: 'center' }}>
                  <ListItemText>
                    <Typography variant="caption" color="text.secondary">
                      {searchResults.length - 8} more results available
                    </Typography>
                  </ListItemText>
                </ListItem>
              )}
            </List>
          </Popover>
          
          {/* Notifications */}
          <IconButton 
            onClick={handleNotificationClick}
            sx={{ 
              bgcolor: '#f8fafc',
              border: '1px solid #e8eaed',
              borderRadius: '12px',
              width: 44,
              height: 44,
              '&:hover': {
                bgcolor: '#f1f5f9'
              }
            }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon sx={{ color: '#6b7280' }} />
            </Badge>
          </IconButton>

          {/* Notification Popover */}
          <Popover
            open={Boolean(notificationAnchor)}
            anchorEl={notificationAnchor}
            onClose={handleNotificationClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                width: 380,
                maxHeight: 400,
                mt: 1,
                borderRadius: '12px',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)'
              }
            }}
          >
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" fontWeight={600} mb={1}>
                Notifications
              </Typography>
              {loading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    Loading notifications...
                  </Typography>
                </Box>
              ) : error ? (
                <Typography variant="body2" color="error" mb={2}>
                  {error}
                </Typography>
              ) : unreadCount > 0 ? (
                <Typography variant="body2" color="text.secondary" mb={2}>
                  You have {unreadCount} unread notification{unreadCount > 1 ? 's' : ''}
                </Typography>
              ) : (
                <Typography variant="body2" color="text.secondary" mb={2}>
                  All caught up! No new notifications.
                </Typography>
              )}
            </Box>
            <Divider />
            <List sx={{ p: 0 }}>
              {loading ? (
                <ListItem sx={{ justifyContent: 'center', py: 4 }}>
                  <CircularProgress size={24} />
                </ListItem>
              ) : notifications.length === 0 ? (
                <ListItem sx={{ justifyContent: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No notifications available
                  </Typography>
                </ListItem>
              ) : (
                notifications.map((notification) => (
                  <ListItem
                    key={notification.id}
                    sx={{
                      bgcolor: notification.read ? 'transparent' : 'rgba(59, 130, 246, 0.05)',
                      borderLeft: !notification.read ? '3px solid #3b82f6' : 'none',
                      py: 2,
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: 'rgba(0, 0, 0, 0.04)'
                      }
                    }}
                    onClick={() => handleNotificationAction(notification)}
                  >
                    <ListItemIcon>
                      {getNotificationIcon(notification.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Typography variant="subtitle2" fontWeight={600}>
                            {notification.title}
                          </Typography>
                          {notification.category && (
                            <Typography 
                              variant="caption" 
                              sx={{ 
                                bgcolor: notification.priority === 'high' ? '#fef2f2' : 
                                         notification.priority === 'medium' ? '#fef3c7' : '#f0f9ff',
                                color: notification.priority === 'high' ? '#dc2626' : 
                                       notification.priority === 'medium' ? '#d97706' : '#2563eb',
                                px: 1,
                                py: 0.25,
                                borderRadius: 1,
                                fontSize: '10px'
                              }}
                            >
                              {notification.category}
                            </Typography>
                          )}
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                            {notification.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            {notification.timestamp}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                ))
              )}
            </List>
            <Divider />
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Button variant="text" size="small" color="primary">
                View All Notifications
              </Button>
            </Box>
          </Popover>
        </Box>
      </Toolbar>
    </Paper>
  );
}

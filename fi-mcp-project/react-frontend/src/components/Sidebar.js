import React, { useState, useEffect } from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Typography, Box, Avatar, Divider } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import FeedIcon from '@mui/icons-material/Feed';
import PersonIcon from '@mui/icons-material/Person';
import HandshakeIcon from '@mui/icons-material/Handshake';
import axios from 'axios';

const mainMenu = [
  { text: 'Dashboard', icon: <DashboardIcon /> },
  { text: 'Portfolio', icon: <AccountBalanceWalletIcon /> },
  { text: 'Goals', icon: <EmojiEventsIcon /> },
  { text: 'Tax Planning', icon: <ReceiptIcon /> },
  { text: 'Nominee Safeguard', icon: <AssignmentIndIcon /> },
  { text: 'Udhaar Aur Bharosa', icon: <HandshakeIcon /> },
  { text: 'Reports', icon: <AssessmentIcon /> },
  { text: 'Investment Insights', icon: <FeedIcon /> },
];
const settingsMenu = [
  { text: 'Settings', icon: <SettingsIcon /> },
];

export default function Sidebar({ selectedTab, setSelectedTab }) {
  const [userProfile, setUserProfile] = useState({ name: 'User' });

  useEffect(() => {
    // Fetch user profile
    axios.get('/profile', { withCredentials: true })
      .then(res => {
        setUserProfile(res.data);
      })
      .catch(() => {
        // Silently fail, use default name
      });
  }, []);

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

  // Logout handler
  const handleLogout = async () => {
    try {
      await axios.post('/logout', {}, { withCredentials: true });
    } catch (e) {}
    window.location.reload();
  };

  return (
    <Drawer variant="permanent" sx={{ width: 240, flexShrink: 0, [`& .MuiDrawer-paper`]: { width: 240, boxSizing: 'border-box', bgcolor: '#fff', borderRight: '1px solid #e0e0e0' } }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <img src="https://mui.com/static/logo.png" alt="logo" width={32} height={32} />
          <Typography variant="h6" noWrap fontWeight={700} color="primary">ArthaSetu AI</Typography>
        </Box>
      </Toolbar>
      
      {/* User Profile Section */}
      <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <PersonIcon />
          </Avatar>
          <Box>
            <Typography variant="subtitle1" fontWeight={600} color="text.primary">
              {userProfile.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {userProfile.occupation || 'User'}
            </Typography>
          </Box>
        </Box>
      </Box>
      
      <List>
        {mainMenu.map((item) => (
          <ListItem
            button
            key={item.text}
            selected={selectedTab === item.text}
            onClick={() => setSelectedTab(item.text)}
            sx={{ 
              my: 0.5, 
              mx: 1,
              borderRadius: 2, 
              bgcolor: selectedTab === item.text ? '#e3f2fd' : 'transparent',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                bgcolor: selectedTab === item.text ? '#bbdefb' : '#f5f5f5',
                transform: 'translateX(4px)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              },
              '&.Mui-selected': {
                bgcolor: '#e3f2fd',
                borderLeft: '4px solid #1976d2',
                '&:hover': {
                  bgcolor: '#bbdefb',
                }
              },
              '& .MuiListItemIcon-root': {
                color: selectedTab === item.text ? '#1976d2' : '#666',
                transition: 'color 0.2s ease-in-out',
              },
              '& .MuiListItemText-primary': {
                fontWeight: selectedTab === item.text ? 600 : 400,
                color: selectedTab === item.text ? '#1976d2' : '#333',
                transition: 'all 0.2s ease-in-out',
              }
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Box sx={{ flexGrow: 1 }} />
      <Divider sx={{ my: 2 }} />
      <List>
        {settingsMenu.map((item) => (
          <ListItem
            button
            key={item.text}
            selected={selectedTab === item.text}
            onClick={() => setSelectedTab(item.text)}
            sx={{
              my: 0.5,
              mx: 1,
              borderRadius: 2,
              bgcolor: selectedTab === item.text ? '#e3f2fd' : 'transparent',
              '&:hover': {
                bgcolor: selectedTab === item.text ? '#bbdefb' : '#f5f5f5',
              },
              '& .MuiListItemIcon-root': {
                color: selectedTab === item.text ? '#1976d2' : '#666',
              },
              '& .MuiListItemText-primary': {
                fontWeight: selectedTab === item.text ? 600 : 400,
                color: selectedTab === item.text ? '#1976d2' : '#333',
              }
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Box sx={{ px: 2, pb: 3, width: '100%' }}>
        <button
          onClick={handleLogout}
          style={{
            width: '100%',
            padding: '10px 0',
            border: '2px solid #d32f2f',
            borderRadius: 8,
            background: 'white',
            color: '#d32f2f',
            fontWeight: 700,
            fontSize: 16,
            cursor: 'pointer',
            marginTop: 8,
            transition: 'background 0.2s, color 0.2s',
          }}
          onMouseOver={e => {
            e.target.style.background = '#ffeaea';
          }}
          onMouseOut={e => {
            e.target.style.background = 'white';
          }}
        >
          Logout
        </button>
      </Box>
    </Drawer>
  );
} 
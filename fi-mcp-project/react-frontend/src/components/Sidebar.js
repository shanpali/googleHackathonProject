import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Typography, Box, Divider, Button } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';

const menu = [
  { text: 'Dashboard', icon: <DashboardIcon />, route: '/dashboard' },
  { text: 'Portfolio', icon: <AccountBalanceWalletIcon />, route: '/portfolio' },
  { text: 'Tax Planning', icon: <ReceiptIcon />, route: '/tax-planning' },
  { text: 'Nominee Safeguard', icon: <AssignmentIndIcon />, route: '/nominee-safeguard' },
  { text: 'Reports', icon: <AssessmentIcon />, route: '/reports' },
  { text: 'Settings', icon: <SettingsIcon />, route: '/settings' },
];

export default function Sidebar({ onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (route) => {
    navigate(route);
  };

  return (
    <Drawer variant="permanent" sx={{ 
      width: 240, 
      flexShrink: 0, 
      [`& .MuiDrawer-paper`]: { 
        width: 240, 
        boxSizing: 'border-box', 
        bgcolor: '#ffffff', 
        borderRight: '1px solid #e8eaed',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
      } 
    }}>
      <Toolbar sx={{ px: 3, py: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box sx={{ 
            width: 40, 
            height: 40, 
            bgcolor: '#1565c0',
            background: 'linear-gradient(135deg, #1565c0 0%, #1976d2 100%)',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: 'white',
            fontSize: '16px',
            fontWeight: 700,
            boxShadow: '0 4px 12px rgba(21, 101, 192, 0.3)'
          }}>
            ₹
          </Box>
          <Box>
            <Typography variant="h6" noWrap fontWeight={700} color="#1f2937" sx={{ fontSize: '18px', lineHeight: 1.2 }}>
              ArthaSetu AI
            </Typography>
            <Typography variant="caption" color="#6b7280" sx={{ fontSize: '12px', lineHeight: 1 }}>
              Financial Guardian
            </Typography>
          </Box>
        </Box>
      </Toolbar>
      <List sx={{ pl: 2, pr: 0, py: 1 }}>
        {menu.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            onClick={() => handleNavigation(item.route)}
            sx={{ 
              mb: 0.5,
              pl: 2,
              pr: 0,
              py: 1.5,
              borderRadius: '8px 0 0 8px',
              backgroundColor: location.pathname === item.route ? '#f0f4ff' : 'transparent',
              border: location.pathname === item.route ? '1px solid #e3f2fd' : '1px solid transparent',
              '&:hover': {
                backgroundColor: location.pathname === item.route ? '#f0f4ff' : '#f8fafc'
              }
            }}
          >
            <ListItemIcon 
              sx={{ 
                color: location.pathname === item.route ? '#1976d2' : '#6b7280',
                minWidth: '36px'
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text}
              sx={{ 
                '& .MuiListItemText-primary': {
                  color: location.pathname === item.route ? '#1976d2' : '#374151',
                  fontWeight: location.pathname === item.route ? 600 : 500,
                  fontSize: '14px'
                }
              }}
            />
          </ListItem>
        ))}
      </List>
      
      {/* Logout Section */}
      <Box sx={{ mt: 'auto', p: 2 }}>
        <Divider sx={{ mb: 2 }} />
        <Button
          fullWidth
          variant="outlined"
          color="error"
          startIcon={<LogoutIcon />}
          onClick={onLogout}
          sx={{
            py: 1.5,
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 500,
            '&:hover': {
              backgroundColor: '#fef2f2',
              borderColor: '#dc2626'
            }
          }}
        >
          Logout
        </Button>
      </Box>
    </Drawer>
  );
} 
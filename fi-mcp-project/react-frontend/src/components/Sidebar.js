import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Typography, Box } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';

const menu = [
  { text: 'Dashboard', icon: <DashboardIcon /> },
  { text: 'Portfolio', icon: <AccountBalanceWalletIcon /> },
  { text: 'Tax Planning', icon: <ReceiptIcon /> },
  { text: 'Nominee Safeguard', icon: <AssignmentIndIcon /> },
  { text: 'Reports', icon: <AssessmentIcon /> },
  { text: 'Settings', icon: <SettingsIcon /> },
];

export default function Sidebar() {
  return (
    <Drawer variant="permanent" sx={{ width: 240, flexShrink: 0, [`& .MuiDrawer-paper`]: { width: 240, boxSizing: 'border-box', bgcolor: '#fff', borderRight: '1px solid #e0e0e0' } }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <img src="https://mui.com/static/logo.png" alt="logo" width={32} height={32} />
          <Typography variant="h6" noWrap fontWeight={700} color="primary">ArthaSetu AI</Typography>
        </Box>
      </Toolbar>
      <List>
        {menu.map((item) => (
          <ListItem button key={item.text} sx={{ my: 0.5, borderRadius: 2 }}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
} 
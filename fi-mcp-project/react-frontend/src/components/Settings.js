import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  Switch, 
  FormControlLabel, 
  Button, 
  TextField,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import PaletteIcon from '@mui/icons-material/Palette';
import PageHeader from './PageHeader';

export default function Settings() {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    weekly: true,
    monthly: true
  });

  const [profile, setProfile] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+91 9876543210'
  });

  const handleNotificationChange = (setting) => {
    setNotifications(prev => ({
      ...prev,
      [setting]: !prev[setting]
    }));
  };

  const handleProfileChange = (field) => (event) => {
    setProfile(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f7f9fb', minHeight: '100vh' }}>
      <PageHeader title="Settings" />
      
      <Box sx={{ p: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight={700} color="#1f2937" mb={1}>
            Settings
          </Typography>
          <Typography color="text.secondary" variant="h6" mb={2}>
            Manage your account preferences and security settings
          </Typography>
        </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} lg={8}>
          {/* Profile Settings */}
          <Card sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <PersonIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Profile Information
                </Typography>
              </Box>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    value={profile.name}
                    onChange={handleProfileChange('name')}
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    value={profile.email}
                    onChange={handleProfileChange('email')}
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    value={profile.phone}
                    onChange={handleProfileChange('phone')}
                    variant="outlined"
                  />
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button variant="contained" size="small">
                  Save Changes
                </Button>
                <Button variant="outlined" size="small">
                  Cancel
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <NotificationsIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Notification Preferences
                </Typography>
              </Box>
              
              <List>
                <ListItem>
                  <ListItemText 
                    primary="Email Notifications"
                    secondary="Receive important updates via email"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={notifications.email}
                      onChange={() => handleNotificationChange('email')}
                      color="primary"
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Push Notifications"
                    secondary="Get instant alerts on your device"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={notifications.push}
                      onChange={() => handleNotificationChange('push')}
                      color="primary"
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Weekly Reports"
                    secondary="Receive weekly portfolio summaries"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={notifications.weekly}
                      onChange={() => handleNotificationChange('weekly')}
                      color="primary"
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Monthly Reports"
                    secondary="Get detailed monthly analysis"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={notifications.monthly}
                      onChange={() => handleNotificationChange('monthly')}
                      color="primary"
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <SecurityIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Security & Privacy
                </Typography>
              </Box>
              
              <List>
                <ListItem>
                  <ListItemText 
                    primary="Two-Factor Authentication"
                    secondary="Add an extra layer of security to your account"
                  />
                  <ListItemSecondaryAction>
                    <Chip label="Enabled" color="success" size="small" />
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText 
                    primary="Change Password"
                    secondary="Update your account password"
                  />
                  <ListItemSecondaryAction>
                    <Button size="small" variant="outlined">
                      Change
                    </Button>
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText 
                    primary="Login History"
                    secondary="View recent account activity"
                  />
                  <ListItemSecondaryAction>
                    <Button size="small" variant="outlined">
                      View
                    </Button>
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <PaletteIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Appearance
                </Typography>
              </Box>
              
              <Typography variant="body2" color="text.secondary" mb={2}>
                Customize your dashboard appearance
              </Typography>
              
              <Button variant="outlined" size="small" fullWidth>
                Theme Settings
              </Button>
            </CardContent>
          </Card>

          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Account Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button variant="outlined" size="small">
                  Export Data
                </Button>
                <Button variant="outlined" size="small">
                  Download Reports
                </Button>
                <Button variant="outlined" color="error" size="small">
                  Deactivate Account
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      </Box>
    </Box>
  );
}

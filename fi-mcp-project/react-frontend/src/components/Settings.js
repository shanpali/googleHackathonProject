import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Switch,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  TextField,
  Button,
  Avatar,
  Divider,
  FormControlLabel,
  Chip
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import LockIcon from '@mui/icons-material/Lock';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import axios from 'axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Settings() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Settings state
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      sms: false,
      push: true,
      insights: true,
      marketUpdates: false,
      goalReminders: true
    },
    privacy: {
      dataSharing: false,
      analytics: true,
      marketing: false
    },
    security: {
      twoFactor: false,
      biometric: true,
      sessionTimeout: 30
    }
  });

  const [profile, setProfile] = useState({
    name: 'Rahul Sharma',
    email: 'rahul.sharma@email.com',
    phone: '+91 98765 43210',
    address: 'Mumbai, Maharashtra',
    occupation: 'Software Engineer',
    company: 'Tech Solutions Ltd.'
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/financial-data', { withCredentials: true });
        setData(res.data);
      } catch (err) {
        setError('Could not load settings data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSettingChange = (category, setting) => (event) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: event.target.checked
      }
    }));
  };

  const handleProfileChange = (field) => (event) => {
    setProfile(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>;

  return (
    <Box sx={{ flexGrow: 1, p: 4 }}>
      <Typography variant="h4" fontWeight={700} mb={3} color="primary">
        ⚙️ Settings & Preferences
      </Typography>

      {/* Profile Overview */}
      <Card sx={{ borderRadius: 3, mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main' }}>
              <PersonIcon sx={{ fontSize: 40 }} />
            </Avatar>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h5" fontWeight={700}>{profile.name}</Typography>
              <Typography variant="body1" color="text.secondary">{profile.occupation} at {profile.company}</Typography>
              <Typography variant="body2" color="text.secondary">{profile.email}</Typography>
            </Box>
            <Chip label="Gold Member" color="warning" sx={{ fontWeight: 700 }} />
          </Box>
        </CardContent>
      </Card>

      {/* Settings Tabs */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Profile" />
            <Tab label="Notifications" />
            <Tab label="Privacy & Security" />
            <Tab label="Preferences" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={700} mb={3}>Personal Information</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      value={profile.name}
                      onChange={handleProfileChange('name')}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Email"
                      value={profile.email}
                      onChange={handleProfileChange('email')}
                      variant="outlined"
                      type="email"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Phone Number"
                      value={profile.phone}
                      onChange={handleProfileChange('phone')}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      value={profile.address}
                      onChange={handleProfileChange('address')}
                      variant="outlined"
                      multiline
                      rows={2}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Occupation"
                      value={profile.occupation}
                      onChange={handleProfileChange('occupation')}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Company"
                      value={profile.company}
                      onChange={handleProfileChange('company')}
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 3 }}>
                  <Button variant="contained" color="primary" sx={{ mr: 2 }}>
                    Save Changes
                  </Button>
                  <Button variant="outlined">
                    Cancel
                  </Button>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={700} mb={3}>Account Security</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <LockIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Change Password" 
                      secondary="Last changed 3 months ago"
                    />
                    <Button variant="outlined" size="small">
                      Update
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <SecurityIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Two-Factor Authentication" 
                      secondary="Add an extra layer of security"
                    />
                    <Switch 
                      checked={settings.security.twoFactor}
                      onChange={handleSettingChange('security', 'twoFactor')}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <PersonIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Biometric Login" 
                      secondary="Use fingerprint or face ID"
                    />
                    <Switch 
                      checked={settings.security.biometric}
                      onChange={handleSettingChange('security', 'biometric')}
                    />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Typography variant="h6" fontWeight={700} mb={3}>Notification Preferences</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Communication Channels</Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <EmailIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Email Notifications" 
                          secondary="Receive updates via email"
                        />
                        <Switch 
                          checked={settings.notifications.email}
                          onChange={handleSettingChange('notifications', 'email')}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <PhoneIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="SMS Notifications" 
                          secondary="Receive updates via SMS"
                        />
                        <Switch 
                          checked={settings.notifications.sms}
                          onChange={handleSettingChange('notifications', 'sms')}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <NotificationsIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary="Push Notifications" 
                          secondary="Receive app notifications"
                        />
                        <Switch 
                          checked={settings.notifications.push}
                          onChange={handleSettingChange('notifications', 'push')}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e3f2fd' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Notification Types</Typography>
                    <List>
                      <ListItem>
                        <ListItemText 
                          primary="Financial Insights" 
                          secondary="AI-powered financial recommendations"
                        />
                        <Switch 
                          checked={settings.notifications.insights}
                          onChange={handleSettingChange('notifications', 'insights')}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Market Updates" 
                          secondary="Stock market and investment updates"
                        />
                        <Switch 
                          checked={settings.notifications.marketUpdates}
                          onChange={handleSettingChange('notifications', 'marketUpdates')}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Goal Reminders" 
                          secondary="Reminders for financial goals"
                        />
                        <Switch 
                          checked={settings.notifications.goalReminders}
                          onChange={handleSettingChange('notifications', 'goalReminders')}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" fontWeight={700} mb={3}>Privacy & Security Settings</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#fff3e0' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2} color="warning.main">Privacy Settings</Typography>
                    <List>
                      <ListItem>
                        <ListItemText 
                          primary="Data Sharing" 
                          secondary="Allow data sharing for better insights"
                        />
                        <Switch 
                          checked={settings.privacy.dataSharing}
                          onChange={handleSettingChange('privacy', 'dataSharing')}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Analytics" 
                          secondary="Help improve the app with analytics"
                        />
                        <Switch 
                          checked={settings.privacy.analytics}
                          onChange={handleSettingChange('privacy', 'analytics')}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Marketing Communications" 
                          secondary="Receive promotional content"
                        />
                        <Switch 
                          checked={settings.privacy.marketing}
                          onChange={handleSettingChange('privacy', 'marketing')}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e8f5e8' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2} color="success.main">Security Settings</Typography>
                    <List>
                      <ListItem>
                        <ListItemText 
                          primary="Session Timeout" 
                          secondary={`${settings.security.sessionTimeout} minutes`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Login History" 
                          secondary="View recent login activity"
                        />
                        <Button variant="outlined" size="small">
                          View
                        </Button>
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Device Management" 
                          secondary="Manage connected devices"
                        />
                        <Button variant="outlined" size="small">
                          Manage
                        </Button>
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Typography variant="h6" fontWeight={700} mb={3}>App Preferences</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Display Settings</Typography>
                    <List>
                      <ListItem>
                        <ListItemText 
                          primary="Dark Mode" 
                          secondary="Switch to dark theme"
                        />
                        <Switch />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Currency" 
                          secondary="Indian Rupee (₹)"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Language" 
                          secondary="English"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Time Zone" 
                          secondary="IST (UTC +5:30)"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card sx={{ borderRadius: 3, bgcolor: '#e3f2fd' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>Data & Storage</Typography>
                    <List>
                      <ListItem>
                        <ListItemText 
                          primary="Cache Size" 
                          secondary="45.2 MB"
                        />
                        <Button variant="outlined" size="small">
                          Clear
                        </Button>
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Data Export" 
                          secondary="Export your financial data"
                        />
                        <Button variant="outlined" size="small">
                          Export
                        </Button>
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Account Deletion" 
                          secondary="Permanently delete your account"
                        />
                        <Button variant="outlined" color="error" size="small">
                          Delete
                        </Button>
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
} 
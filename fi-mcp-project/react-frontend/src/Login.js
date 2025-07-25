import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  Container,
  InputAdornment
} from '@mui/material';
import PhoneIcon from '@mui/icons-material/Phone';
import LoginIcon from '@mui/icons-material/Login';

function Login({ onLogin }) {
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Validate phone number
    if (phone.length !== 10 || !/^\d{10}$/.test(phone)) {
      setError('Please enter a valid 10-digit phone number.');
      setLoading(false);
      return;
    }
    
    try {
      await axios.post('/login', { phone });
      onLogin();
    } catch {
      setError('Login failed. Please check your phone number and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePhoneChange = (e) => {
    const value = e.target.value;
    // Only allow numeric input and limit to 10 digits
    if (/^\d*$/.test(value) && value.length <= 10) {
      setPhone(value);
      setError(''); // Clear error when user starts typing
    }
  };

  return (
    <Container maxWidth="sm" sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      bgcolor: '#f5f5f5'
    }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          width: '100%', 
          maxWidth: 400,
          borderRadius: 3,
          bgcolor: '#fff'
        }}
      >
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>
            ArthaSetu AI
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome back! Please sign in to continue.
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            label="Phone Number"
            value={phone}
            onChange={handlePhoneChange}
            placeholder="Enter your 10-digit phone number"
            required
            sx={{ mb: 2 }}
            inputProps={{
              maxLength: 10,
              inputMode: 'numeric',
              pattern: '[0-9]*'
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <PhoneIcon color="primary" />
                </InputAdornment>
              ),
            }}
            helperText={`${phone.length}/10 digits`}
          />

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading}
            startIcon={<LoginIcon />}
            sx={{
              mt: 1,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontSize: '1.1rem',
              fontWeight: 600
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default Login;
import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, TextField, Button, InputAdornment } from '@mui/material';
import PhoneIcon from '@mui/icons-material/Phone';
import axios from 'axios';

function Login({ onLogin }) {
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/login', { phone }, { withCredentials: true });
      onLogin(phone);
    } catch (err) {
      setError('Login failed');
      console.error('Login error:', err);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', width: '100vw', bgcolor: '#f5f8fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Card sx={{ minWidth: 350, maxWidth: 400, borderRadius: 4, boxShadow: 3, mx: 'auto' }}>
        <CardContent>
          <Typography variant="h4" fontWeight={700} color="primary" align="center" mb={1}>
            ArthaSetu AI
          </Typography>
          <Typography align="center" color="text.secondary" mb={3}>
            Welcome back! Please sign in to continue.
          </Typography>
          <form onSubmit={handleSubmit}>
            <Typography variant="subtitle2" mb={0.5}>Phone Number *</Typography>
            <TextField
              fullWidth
              required
              placeholder="Enter your phone number"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PhoneIcon color="primary" />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2, mt: 0.5, bgcolor: '#fff', borderRadius: 2 }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              sx={{ py: 1.5, fontWeight: 700, fontSize: 18, mt: 1 }}
              startIcon={<i className="fas fa-sign-in-alt" />}
            >
              Sign In
            </Button>
            {error && <Typography color="error" align="center" mt={2}>{error}</Typography>}
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Login; 
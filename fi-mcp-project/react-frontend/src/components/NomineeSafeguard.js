import React from 'react';
import { Card, CardContent, Box, List, ListItem, ListItemText, Button, Grid } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import SecurityIcon from '@mui/icons-material/Security';
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom';
import PageHeader from './PageHeader';

const risks = [
  { label: 'HDFC Mutual Fund', action: 'Update', status: 'critical' },
  { label: 'ICICI Bank Fixed Deposit', action: 'Update', status: 'critical' },
  { label: 'LIC Policy', action: 'Update', status: 'warning' },
  { label: 'Axis Bank Savings', action: 'Verify', status: 'warning' },
  { label: 'Kotak Securities Demat', action: 'Verify', status: 'warning' },
];

export default function NomineeSafeguard() {
  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f7f9fb', minHeight: '100vh' }}>
      <PageHeader title="Nominee Safeguard" />
      
      <Box sx={{ p: 4 }}>
        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#1f2937', marginBottom: '8px' }}>
            Nominee Safeguard
          </div>
          <div style={{ color: '#6b7280', fontSize: '1.25rem', marginBottom: '16px' }}>
            Secure your family's financial future with proper nominee management
          </div>
        </Box>

      <Grid container spacing={3}>
        {/* Main Status Card */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <WarningAmberIcon color="warning" sx={{ fontSize: 28 }} />
                <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>Nominee Safeguard Status</div>
                <Box flexGrow={1} />
                <Button size="small" variant="contained" color="warning">Action Required</Button>
              </Box>
              <div style={{ fontSize: '1rem', color: '#6b7280', marginBottom: '24px' }}>
                Your nominee details are incomplete across several financial instruments. This could lead to difficulties for your family in accessing your assets in case of an emergency.
              </div>
              
              <div style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '16px' }}>Potential Unclaimed Assets Risk</div>
              <List>
                {risks.map((item) => (
                  <ListItem key={item.label} sx={{ py: 1, borderBottom: '1px solid #f1f5f9' }}>
                    <ListItemText 
                      primary={item.label}
                      secondary={`Status: ${item.status === 'critical' ? 'Critical' : 'Needs attention'}`}
                    />
                    <Button 
                      size="small" 
                      variant="outlined"
                      color={item.status === 'critical' ? 'error' : 'warning'}
                    >
                      {item.action}
                    </Button>
                  </ListItem>
                ))}
              </List>
              
              <Box sx={{ mt: 3, p: 2, bgcolor: '#fef3c7', borderRadius: 2 }}>
                <div style={{ fontSize: '0.875rem', color: '#92400e', fontWeight: 500 }}>
                  📊 Did you know? Over ₹2 lakh crore in unclaimed assets exist in India due to missing nominee details
                </div>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Side Panel */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <SecurityIcon color="primary" />
                <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>
                  Quick Actions
                </div>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button variant="contained" size="small" fullWidth>
                  Update All Nominees
                </Button>
                <Button variant="outlined" size="small" fullWidth>
                  Download Checklist
                </Button>
                <Button variant="outlined" size="small" fullWidth>
                  Schedule Review
                </Button>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <FamilyRestroomIcon color="primary" />
                <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>
                  Family Protection
                </div>
              </Box>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '16px' }}>
                Ensure your family can access your financial assets without legal complications.
              </div>
              <Button variant="outlined" size="small" fullWidth>
                Learn More
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      </Box>
    </Box>
  );
} 
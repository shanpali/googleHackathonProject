import React from 'react';
import { Card, CardContent, Typography, Box, List, ListItem, ListItemText, Button } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

const risks = [
  { label: 'HDFC Mutual Fund', action: 'Update' },
  { label: 'ICICI Bank Fixed Deposit', action: 'Update' },
  { label: 'LIC Policy', action: 'Update' },
  { label: 'Axis Bank Savings', action: 'Verify' },
  { label: 'Kotak Securities Demat', action: 'Verify' },
];

export default function NomineeSafeguard() {
  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <WarningAmberIcon color="warning" />
          <Typography variant="h6" fontWeight={700}>Nominee Safeguard Status</Typography>
          <Box flexGrow={1} />
          <Button size="small" variant="contained" color="warning">Action Required</Button>
        </Box>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Your nominee details are incomplete across several financial instruments. This could lead to difficulties for your family in accessing your assets in case of an emergency.
        </Typography>
        <Typography variant="subtitle2" mb={1}>Potential Unclaimed Assets Risk</Typography>
        <List dense>
          {risks.map((item) => (
            <ListItem key={item.label} sx={{ py: 0 }}>
              <ListItemText primary={item.label} />
              <Button size="small" variant="text">{item.action}</Button>
            </ListItem>
          ))}
        </List>
        <Typography variant="caption" color="text.secondary" mt={2}>
          Did you know? Over ₹2 lakh crore in unclaimed assets exist in India due to missing nominee details
        </Typography>
      </CardContent>
    </Card>
  );
} 
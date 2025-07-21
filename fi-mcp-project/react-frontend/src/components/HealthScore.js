import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, List, ListItem, ListItemText } from '@mui/material';

const metrics = [
  { label: 'Emergency Fund', value: 95 },
  { label: 'Debt Management', value: 90 },
  { label: 'Retirement Planning', value: 75 },
  { label: 'Insurance Coverage', value: 70 },
  { label: 'Tax Efficiency', value: 60 },
];

export default function HealthScore() {
  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Typography variant="h6" fontWeight={700} mb={2}>Financial Health Score</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ textAlign: 'center' }}>
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <svg width={80} height={80}>
                <circle cx={40} cy={40} r={36} fill="none" stroke="#e0e0e0" strokeWidth={8} />
                <circle cx={40} cy={40} r={36} fill="none" stroke="#1976d2" strokeWidth={8} strokeDasharray={226} strokeDashoffset={36} />
              </svg>
              <Typography variant="h4" sx={{ position: 'absolute', top: 22, left: 22 }}>85</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">out of 100</Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <List dense>
              {metrics.map((item) => (
                <ListItem key={item.label} sx={{ py: 0 }}>
                  <ListItemText primary={item.label} />
                  <Box sx={{ width: 80, mr: 2 }}>
                    <LinearProgress variant="determinate" value={item.value} sx={{ height: 8, borderRadius: 5 }} />
                  </Box>
                  <Typography fontWeight={700}>{item.value}/100</Typography>
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
} 
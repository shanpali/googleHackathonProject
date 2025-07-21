import React from 'react';
import { Card, CardContent, Typography, Box, Grid, List, ListItem, ListItemText } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AssetAllocation({ data }) {
  // Use real net worth history if available
  const history = data.fetch_net_worth?.history || [];

  // Use real allocation breakdown if available
  const allocation = data.fetch_net_worth?.netWorthResponse?.assetValues?.map(a => ({
    label: a.netWorthAttribute.replace('ASSET_TYPE_', '').replace('_', ' '),
    value: parseFloat(a.value?.units) || 0
  })) || [];

  // Calculate total for percentage breakdown
  const total = allocation.reduce((sum, a) => sum + a.value, 0) || 1;
  const allocationWithPercent = allocation.map(a => ({ ...a, percent: Math.round((a.value / total) * 100) }));

  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight={700}>Asset Allocation</Typography>
          <Typography variant="body2" color="text.secondary">Last 12 months</Typography>
        </Box>
        <Grid container spacing={2} columns={12} mt={1}>
          <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 8' }, display: 'flex' }}>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={history}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#1976d2" name="Total Portfolio" />
              </LineChart>
            </ResponsiveContainer>
          </Box>
          <Box sx={{ gridColumn: { xs: 'span 12', md: 'span 4' }, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="subtitle2" mb={1}>Allocation Breakdown</Typography>
            <List dense>
              {allocationWithPercent.length > 0 ? allocationWithPercent.map((item) => (
                <ListItem key={item.label} sx={{ py: 0 }}>
                  <ListItemText primary={item.label} />
                  <Typography fontWeight={700}>{item.percent}%</Typography>
                </ListItem>
              )) : <ListItem><ListItemText primary="No data" /></ListItem>}
            </List>
            <Typography variant="body2" color="text.secondary" mt={2}>Risk Profile: <b>Moderate</b></Typography>
          </Box>
        </Grid>
      </CardContent>
    </Card>
  );
} 
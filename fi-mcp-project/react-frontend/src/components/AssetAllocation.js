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
          <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>Asset Allocation</div>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Last 12 months</div>
        </Box>
        <Grid container spacing={2} mt={1}>
          <Grid item xs={12} md={8}>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={history}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#1976d2" name="Total Portfolio" />
              </LineChart>
            </ResponsiveContainer>
          </Grid>
          <Grid item xs={12} md={4}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '8px' }}>Allocation Breakdown</div>
            <List dense>
              {allocationWithPercent.length > 0 ? allocationWithPercent.map((item) => (
                <ListItem key={item.label} sx={{ py: 0 }}>
                  <ListItemText primary={item.label} />
                  <div style={{ fontWeight: 700 }}>{item.percent}%</div>
                </ListItem>
              )) : <ListItem><ListItemText primary="No data" /></ListItem>}
            </List>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '16px' }}>Risk Profile: <b>Moderate</b></div>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
} 
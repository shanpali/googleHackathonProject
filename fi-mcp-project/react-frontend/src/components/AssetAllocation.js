import React from 'react';
import { Card, CardContent, Typography, Box, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

// Softer pastel color palette
const COLORS = ['#90caf9', '#a5d6a7', '#ffe082', '#ffab91', '#ce93d8', '#80cbc4', '#fff59d', '#b0bec5'];

export default function AssetAllocation({ data }) {
  // Use real allocation breakdown if available
  const allocation = data.fetch_net_worth?.netWorthResponse?.assetValues?.map(a => ({
    label: a.netWorthAttribute.replace('ASSET_TYPE_', '').replace('_', ' '),
    value: parseFloat(a.value?.units) || 0
  })) || [];

  // Calculate total for percentage breakdown
  const total = allocation.reduce((sum, a) => sum + a.value, 0) || 1;
  // For the table, add percent as integer; for the pie, use raw value
  const allocationWithPercent = allocation.map((a, idx) => ({
    ...a,
    percent: Math.round((a.value / total) * 100), // for table only
    color: COLORS[idx % COLORS.length]
  }));

  return (
    <Card sx={{ borderRadius: 3, mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={700}>Asset Allocation</Typography>
          <Typography variant="body2" color="text.secondary">Last 12 months</Typography>
        </Box>
        <Grid container spacing={2} alignItems="center">
          {/* Table on the left (narrower) */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" mb={1}>Allocation Breakdown</Typography>
            <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Asset Type</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Amount</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Percent</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {allocationWithPercent.length > 0 ? allocationWithPercent.map((item) => (
                    <TableRow key={item.label}>
                      <TableCell>{item.label}</TableCell>
                      <TableCell align="right">₹{item.value.toLocaleString()}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700 }}>{item.percent}%</TableCell>
                    </TableRow>
                  )) : (
                    <TableRow><TableCell colSpan={3}>No data</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <Typography variant="body2" color="text.secondary" mt={2}>Risk Profile: <b>Moderate</b></Typography>
          </Grid>
          {/* Pie chart on the right (wider) */}
          <Grid item xs={12} md={8} sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', pr: { md: 10, xs: 0 } }}>
            {allocationWithPercent.length > 0 && (
              <ResponsiveContainer width={600} height={340}>
                <PieChart>
                  <Pie
                    data={allocationWithPercent}
                    dataKey="value"
                    nameKey="label"
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={120}
                    fill="#90caf9"
                    label={({ value, percent }) => `${Math.round(percent * 100)}%`}
                    labelLine={false}
                    paddingAngle={2}
                  >
                    {allocationWithPercent.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
} 
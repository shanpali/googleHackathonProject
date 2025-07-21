import React from 'react';
import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Box } from '@mui/material';

// Helper to get recent transactions from real data
function getRecentTransactions(data) {
  // Try to extract from bank transactions or use empty array
  return data.fetch_bank_transactions?.transactions || [];
}

export default function RecentTransactions({ data }) {
  const txns = getRecentTransactions(data);
  return (
    <Card sx={{ borderRadius: 3, mt: 4 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={700}>Recent Transactions</Typography>
          <Typography variant="body2" color="primary" sx={{ cursor: 'pointer' }}>View all transactions →</Typography>
        </Box>
        <TableContainer component={Paper} sx={{ boxShadow: 0 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>DATE</TableCell>
                <TableCell>DESCRIPTION</TableCell>
                <TableCell>CATEGORY</TableCell>
                <TableCell>ACCOUNT</TableCell>
                <TableCell align="right">AMOUNT</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {txns.length > 0 ? txns.map((row, idx) => (
                <TableRow key={idx}>
                  <TableCell>{row.date}</TableCell>
                  <TableCell>{row.description}</TableCell>
                  <TableCell>{row.category}</TableCell>
                  <TableCell>{row.account}</TableCell>
                  <TableCell align="right" style={{ color: row.amount < 0 ? 'red' : 'green', fontWeight: 700 }}>
                    {row.amount < 0 ? '-' : '+'}₹{Math.abs(row.amount).toLocaleString()}
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">No transactions available</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
} 
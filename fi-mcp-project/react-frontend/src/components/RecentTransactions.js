import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Box } from '@mui/material';
import axios from 'axios';

// Helper to get recent transactions from real data
function getRecentTransactions(data, cashAssets) {
  // Extract and flatten all transactions from all banks
  const banks = data.fetch_bank_transactions?.bankTransactions || [];
  let allTxns = [];
  banks.forEach(bank => {
    (bank.txns || []).forEach(txn => {
      // Handle the new transaction structure
      allTxns.push({
        amount: txn.amount || 0,
        description: txn.narration || '',
        date: txn.date || '',
        txnType: txn.type || '',
        category: txn.category || getCategoryFromNarration(txn.narration || '', txn.type || '', ''),
        account: bank.bankName || bank.accountNumber || '',
        balance: bank.currentBalance || 0
      });
    });
  });
  // Add cash asset additions as credit transactions
  if (Array.isArray(cashAssets)) {
    cashAssets.forEach(asset => {
      allTxns.push({
        amount: asset.amount,
        description: asset.description || 'Extra Asset Added',
        date: asset.timestamp ? new Date(asset.timestamp).toISOString().slice(0, 10) : '',
        txnType: 1,
        category: 'Credit',
        account: 'Extra Asset',
        balance: asset.amount
      });
    });
  }
  // Sort by date descending
  allTxns.sort((a, b) => new Date(b.date) - new Date(a.date));
  // Return the 10 most recent
  return allTxns.slice(0, 10);
}

function getCategoryFromNarration(narration, txnType, mode) {
  // Simple heuristics for demo
  if (/salary/i.test(narration)) return 'Salary';
  if (/rent/i.test(narration)) return 'Rent';
  if (/sip|fund|mf/i.test(narration)) return 'Investment';
  if (/credit card/i.test(narration)) return 'Credit Card';
  if (/fuel|petrol|oil/i.test(narration)) return 'Fuel';
  if (/grocery|grocer/i.test(narration)) return 'Groceries';
  if (/interest/i.test(narration)) return 'Interest';
  if (/debit|auto/i.test(narration)) return 'Auto Debit';
  if (/td booking|fd/i.test(narration)) return 'Fixed Deposit';
  if (/upi/i.test(mode)) return 'UPI';
  if (txnType === 1) return 'Credit';
  if (txnType === 2) return 'Debit';
  return 'Other';
}

export default function RecentTransactions({ data, refreshTrigger }) {
  const [cashAssets, setCashAssets] = useState([]);

  useEffect(() => {
    axios.get('/cash-asset', { withCredentials: true }).then(res => {
      setCashAssets(res.data.assets || []);
    }).catch(() => setCashAssets([]));
  }, [refreshTrigger]); // Add refreshTrigger to dependency array

  const txns = getRecentTransactions(data, cashAssets);
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
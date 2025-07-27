import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Box, Modal, IconButton, Chip } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';

// Helper to get all transactions from real data
function getAllTransactions(data, cashAssets) {
  // Extract and flatten all transactions from all banks
  const banks = data.fetch_bank_transactions?.bankTransactions || [];
  let allTxns = [];
  
  banks.forEach(bank => {
    (bank.txns || []).forEach(txn => {
      // Handle both old array format and new object format
      let transaction = {};
      
      if (Array.isArray(txn)) {
        // Old format: [amount, narration, date, type, mode, balance]
        transaction = {
          amount: parseFloat(txn[0]) || 0,
          description: txn[1] || '',
          date: txn[2] || '',
          txnType: txn[3] || '',
          mode: txn[4] || '',
          balance: parseFloat(txn[5]) || 0,
          category: getCategoryFromNarration(txn[1] || '', txn[3] || '', txn[4] || ''),
          account: bank.bankName || bank.bank || bank.accountNumber || 'Bank Account'
        };
      } else {
        // New format: object with properties
        transaction = {
          amount: parseFloat(txn.amount) || 0,
          description: txn.narration || txn.description || '',
        date: txn.date || '',
          txnType: txn.type || txn.txnType || '',
          mode: txn.mode || txn.transactionMode || '',
          balance: parseFloat(txn.balance) || 0,
          category: txn.category || getCategoryFromNarration(txn.narration || '', txn.type || '', txn.mode || ''),
          account: bank.bankName || bank.bank || bank.accountNumber || 'Bank Account'
        };
      }
      
      allTxns.push(transaction);
    });
  });
  
  // Add cash asset additions as credit transactions
  if (Array.isArray(cashAssets)) {
    cashAssets.forEach(asset => {
      allTxns.push({
        amount: parseFloat(asset.amount) || 0,
        description: asset.description || 'Extra Asset Added',
        date: asset.timestamp ? new Date(asset.timestamp).toISOString().slice(0, 10) : '',
        txnType: 1,
        category: 'Credit',
        account: 'Extra Asset',
        balance: parseFloat(asset.amount) || 0,
        mode: 'CASH'
      });
    });
  }
  
  // Sort by date descending
  allTxns.sort((a, b) => new Date(b.date) - new Date(a.date));
  return allTxns;
}

// Helper to get recent transactions (first 10)
function getRecentTransactions(data, cashAssets) {
  return getAllTransactions(data, cashAssets).slice(0, 10);
}

function getCategoryFromNarration(narration, txnType, mode) {
  // Simple heuristics for demo
  if (/salary/i.test(narration)) return 'Salary';
  if (/rent/i.test(narration)) return 'Rent';
  if (/sip|fund|mf|investment/i.test(narration)) return 'Investment';
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
  const [showAllTransactions, setShowAllTransactions] = useState(false);

  useEffect(() => {
    axios.get('/cash-asset', { withCredentials: true }).then(res => {
      setCashAssets(res.data.assets || []);
    }).catch(() => setCashAssets([]));
  }, [refreshTrigger]);

  const txns = getRecentTransactions(data, cashAssets);
  const allTxns = getAllTransactions(data, cashAssets);

  const handleViewAllTransactions = () => {
    setShowAllTransactions(true);
  };

  const handleCloseModal = () => {
    setShowAllTransactions(false);
  };

  return (
    <>
    <Card sx={{ borderRadius: 3, mt: 4 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={700}>Recent Transactions</Typography>
            <Typography 
              variant="body2" 
              color="primary" 
              sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
              onClick={handleViewAllTransactions}
            >
              View all transactions →
            </Typography>
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
                    <TableCell>
                      <Chip 
                        label={row.category} 
                        size="small" 
                        color={row.category === 'Credit' ? 'success' : row.category === 'Debit' ? 'error' : 'default'}
                        variant="outlined"
                      />
                    </TableCell>
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

      {/* All Transactions Modal */}
      <Modal
        open={showAllTransactions}
        onClose={handleCloseModal}
        aria-labelledby="all-transactions-modal"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2
        }}
      >
        <Box sx={{
          bgcolor: 'background.paper',
          borderRadius: 3,
          boxShadow: 24,
          p: 3,
          maxWidth: '90vw',
          maxHeight: '90vh',
          overflow: 'auto',
          position: 'relative'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" fontWeight={700}>All Transactions</Typography>
            <IconButton onClick={handleCloseModal} size="large">
              <CloseIcon />
            </IconButton>
          </Box>
          
          <TableContainer component={Paper} sx={{ boxShadow: 0 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>DATE</TableCell>
                  <TableCell>DESCRIPTION</TableCell>
                  <TableCell>CATEGORY</TableCell>
                  <TableCell>ACCOUNT</TableCell>
                  <TableCell>MODE</TableCell>
                  <TableCell align="right">AMOUNT</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {allTxns.length > 0 ? allTxns.map((row, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{row.date}</TableCell>
                    <TableCell>{row.description}</TableCell>
                    <TableCell>
                      <Chip 
                        label={row.category} 
                        size="small" 
                        color={row.category === 'Credit' ? 'success' : row.category === 'Debit' ? 'error' : 'default'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{row.account}</TableCell>
                    <TableCell>{row.mode}</TableCell>
                    <TableCell align="right" style={{ color: row.amount < 0 ? 'red' : 'green', fontWeight: 700 }}>
                      {row.amount < 0 ? '-' : '+'}₹{Math.abs(row.amount).toLocaleString()}
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">No transactions available</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Total Transactions: {allTxns.length}
            </Typography>
          </Box>
        </Box>
      </Modal>
    </>
  );
} 
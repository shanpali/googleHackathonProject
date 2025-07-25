import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box, Button, TextField, IconButton, List, ListItem, ListItemText, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, Tooltip } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import ShieldIcon from '@mui/icons-material/Shield';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

export default function FinancialOverview({ data, onNetWorthClick }) {
  const [cashAssets, setCashAssets] = useState([]);
  const [loadingCash, setLoadingCash] = useState(true);
  const [addOpen, setAddOpen] = useState(false);
  const [cashAmount, setCashAmount] = useState('');
  const [cashDesc, setCashDesc] = useState('');
  const [adding, setAdding] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchCashAssets();
  }, []);

  const fetchCashAssets = async () => {
    setLoadingCash(true);
    try {
      const res = await axios.get('/cash-asset', { withCredentials: true });
      setCashAssets(res.data.assets || []);
    } catch {
      setCashAssets([]);
    } finally {
      setLoadingCash(false);
    }
  };

  const handleAddCash = async () => {
    if (!cashAmount || isNaN(Number(cashAmount)) || Number(cashAmount) <= 0) return;
    setAdding(true);
    try {
      await axios.post('/cash-asset', { amount: Number(cashAmount), description: cashDesc }, { withCredentials: true });
      setAddOpen(false);
      setCashAmount('');
      setCashDesc('');
      fetchCashAssets();
    } finally {
      setAdding(false);
    }
  };

  const handleDeleteCash = async (id) => {
    setDeletingId(id);
    try {
      await axios.delete('/cash-asset', { data: { id }, withCredentials: true });
      fetchCashAssets();
    } finally {
      setDeletingId(null);
    }
  };

  // Use real data from props
  const netWorth = Number(data.fetch_net_worth?.netWorthResponse?.totalNetWorthValue?.units) + cashAssets.reduce((sum, a) => sum + (Number(a.amount) || 0), 0);
  const investments = Number(data.fetch_net_worth?.netWorthResponse?.assetValues?.find(a => a.netWorthAttribute === 'ASSET_TYPE_MUTUAL_FUND')?.value?.units);
  // Calculate total savings from bank accounts
  const bankAccounts = data.fetch_bank_transactions?.bankTransactions || [];
  const savings = bankAccounts.reduce((sum, bank) => sum + (Number(bank.currentBalance) || 0), 0);
  // If you have insurance data, use it; otherwise, show 0
  const insurance = Number(data.fetch_insurance?.totalCoverage);
  const insuranceDisplay = !isNaN(insurance) && insurance > 0 ? `₹${insurance}` : '₹0';

  const cards = [
    { label: 'Total Net Worth', value: `₹${netWorth}`, change: '', icon: <TrendingUpIcon color="primary" fontSize="large" /> },
    { label: 'Investments', value: `₹${investments}`, change: '', icon: <ShowChartIcon color="success" fontSize="large" /> },
    { label: 'Savings', value: `₹${savings}`, change: '', icon: <SavingsIcon color="secondary" fontSize="large" /> },
    { label: 'Insurance Coverage', value: insuranceDisplay, change: '', icon: <ShieldIcon color="warning" fontSize="large" /> },
  ];

  return (
    <>
      <Grid container spacing={2} columns={12} alignItems="center">
        {cards.map((item, idx) => {
          const isNetWorth = item.label === 'Total Net Worth';
          return (
            <Box key={item.label} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' }, display: 'flex' }}>
              <Card
                sx={{
                  borderRadius: 3,
                  boxShadow: 0,
                  flex: 1,
                  cursor: isNetWorth && onNetWorthClick ? 'pointer' : 'default',
                  transition: 'box-shadow 0.2s',
                  '&:hover': isNetWorth && onNetWorthClick ? { boxShadow: 6, background: '#e3f2fd' } : {},
                }}
                onClick={isNetWorth && onNetWorthClick ? onNetWorthClick : undefined}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {item.icon}
                    <Typography variant="subtitle2" color="text.secondary">{item.label}</Typography>
                  </Box>
                  <Typography variant="h6" fontWeight={700}>{item.value}</Typography>
                  {item.change && (
                    <Typography variant="body2" color={item.change.startsWith('+') ? 'green' : 'red'}>
                      {item.change}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Box>
          );
        })}
        <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 3' }, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 120 }}>
          <Tooltip title="Add Cash Asset">
            <Button variant="outlined" startIcon={<AddIcon />} onClick={() => setAddOpen(true)} sx={{ fontWeight: 700, borderRadius: 2 }}>
              Add Cash
            </Button>
          </Tooltip>
        </Box>
      </Grid>
      <Dialog open={addOpen} onClose={() => setAddOpen(false)}>
        <DialogTitle>Add Cash Asset</DialogTitle>
        <DialogContent>
          <TextField
            label="Amount"
            type="number"
            value={cashAmount}
            onChange={e => setCashAmount(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Description"
            value={cashDesc}
            onChange={e => setCashDesc(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)}>Cancel</Button>
          <Button onClick={handleAddCash} variant="contained" disabled={adding || !cashAmount || Number(cashAmount) <= 0}>
            {adding ? <CircularProgress size={20} /> : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1" fontWeight={700} mb={1}>Cash Assets</Typography>
        {loadingCash ? <CircularProgress size={24} /> : (
          <List dense>
            {cashAssets.length === 0 && <ListItem><ListItemText primary="No cash assets added." /></ListItem>}
            {cashAssets.map(asset => (
              <ListItem key={asset.id} secondaryAction={
                <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteCash(asset.id)} disabled={deletingId === asset.id}>
                  {deletingId === asset.id ? <CircularProgress size={20} /> : <DeleteIcon />}
                </IconButton>
              }>
                <ListItemText
                  primary={<>
                    <b>₹{Number(asset.amount).toLocaleString()}</b> <span style={{ color: '#888', marginLeft: 8 }}>{asset.description}</span>
                  </>}
                  secondary={new Date(asset.timestamp).toLocaleString()}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    </>
  );
} 
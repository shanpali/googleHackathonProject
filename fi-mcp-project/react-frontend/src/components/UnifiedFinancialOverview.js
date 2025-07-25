import React from 'react';
import { Grid, Card, CardContent, Box, Button } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import SavingsIcon from '@mui/icons-material/Savings';
import ShieldIcon from '@mui/icons-material/Shield';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

export default function UnifiedFinancialOverview() {
  const financialCards = [
    {
      title: 'Total Net Worth',
      value: '₹1,24,56,789',
      change: '+3.2%',
      subtitle: 'vs previous month',
      icon: <TrendingUpIcon sx={{ fontSize: 24, color: '#3b82f6' }} />,
      bgColor: '#eff6ff',
      iconBg: '#dbeafe'
    },
    {
      title: 'Investments',
      value: '₹78,45,230',
      change: '+5.7%',
      subtitle: 'across 12 instruments',
      icon: <ShowChartIcon sx={{ fontSize: 24, color: '#10b981' }} />,
      bgColor: '#f0fdf4',
      iconBg: '#dcfce7'
    },
    {
      title: 'Savings',
      value: '₹15,78,450',
      change: '+1.2%',
      subtitle: 'across 4 accounts',
      icon: <SavingsIcon sx={{ fontSize: 24, color: '#8b5cf6' }} />,
      bgColor: '#faf5ff',
      iconBg: '#f3e8ff'
    },
    {
      title: 'Insurance Coverage',
      value: '₹2,50,00,000',
      change: '',
      subtitle: 'across 3 policies',
      icon: <ShieldIcon sx={{ fontSize: 24, color: '#f59e0b' }} />,
      bgColor: '#fffbeb',
      iconBg: '#fef3c7'
    }
  ];

  return (
    <Box sx={{
      background: '#fff',
      borderRadius: 3,
      boxShadow: '0 1px 3px 0 rgba(0,0,0,0.06)',
      p: 3,
      mb: 4
    }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#1f2937' }}>
          Unified Financial Overview
        </div>
        <Button
          variant="text"
          endIcon={<ArrowForwardIcon />}
          sx={{
            color: '#3b82f6',
            fontWeight: 600,
            fontSize: '0.875rem',
            textTransform: 'none',
            '&:hover': {
              backgroundColor: '#f0f9ff'
            }
          }}
        >
          18 sources connected
        </Button>
      </Box>

      {/* Financial Cards Grid */}
      <Grid container spacing={3}>
        {financialCards.map((card, index) => (
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <Card
              sx={{
                borderRadius: 3,
                border: '1px solid #f1f5f9',
                boxShadow: 'none',
                background: card.bgColor,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  boxShadow: '0 4px 12px 0 rgba(0,0,0,0.08)',
                  transform: 'translateY(-2px)'
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                {/* Icon and Title */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      backgroundColor: card.iconBg,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {card.icon}
                  </Box>
                  <div style={{
                    fontSize: '0.95rem',
                    fontWeight: 500,
                    color: '#6b7280',
                    lineHeight: 1.2
                  }}>
                    {card.title}
                  </div>
                </Box>

                {/* Value */}
                <div style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: '#1f2937',
                  marginBottom: '8px',
                  lineHeight: 1
                }}>
                  {card.value}
                  {card.change && (
                    <span style={{
                      fontSize: '1rem',
                      fontWeight: 600,
                      color: '#10b981',
                      marginLeft: 8
                    }}>
                      {card.change}
                    </span>
                  )}
                </div>

                {/* Subtitle */}
                <div style={{
                  fontSize: '0.95rem',
                  color: '#6b7280'
                }}>
                  {card.subtitle}
                </div>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
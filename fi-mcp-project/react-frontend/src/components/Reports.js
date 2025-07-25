import React from 'react';
import { Box, Typography, Card, CardContent, Grid, Button } from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PieChartIcon from '@mui/icons-material/PieChart';
import DescriptionIcon from '@mui/icons-material/Description';
import PageHeader from './PageHeader';

const reportTypes = [
  {
    title: 'Portfolio Performance',
    description: 'Detailed analysis of your investment returns and performance metrics',
    icon: <TrendingUpIcon color="primary" />,
    status: 'Available'
  },
  {
    title: 'Asset Allocation Report',
    description: 'Comprehensive breakdown of your asset distribution across categories',
    icon: <PieChartIcon color="primary" />,
    status: 'Available'
  },
  {
    title: 'Tax Optimization Report',
    description: 'Analysis of tax-saving opportunities and recommendations',
    icon: <AssessmentIcon color="primary" />,
    status: 'Coming Soon'
  },
  {
    title: 'Risk Assessment Report',
    description: 'Detailed evaluation of your portfolio risk profile and suggestions',
    icon: <DescriptionIcon color="primary" />,
    status: 'Coming Soon'
  }
];

export default function Reports() {
  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f7f9fb', minHeight: '100vh' }}>
      <PageHeader title="Financial Reports" />
      
      <Box sx={{ p: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight={700} color="#1f2937" mb={1}>
            Financial Reports
          </Typography>
          <Typography color="text.secondary" variant="h6" mb={2}>
            Detailed analysis and insights into your financial portfolio
          </Typography>
        </Box>

      <Grid container spacing={3}>
        {reportTypes.map((report, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: 2, 
                    bgcolor: 'primary.light', 
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {report.icon}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" fontWeight={600} mb={1}>
                      {report.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {report.description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography 
                        variant="caption" 
                        color={report.status === 'Available' ? 'success.main' : 'text.secondary'}
                        fontWeight={500}
                      >
                        {report.status}
                      </Typography>
                      <Button 
                        size="small" 
                        variant="outlined"
                        disabled={report.status !== 'Available'}
                      >
                        {report.status === 'Available' ? 'Generate Report' : 'Coming Soon'}
                      </Button>
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Report Schedule
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Configure automatic report generation and delivery preferences
            </Typography>
            <Button variant="contained" size="small">
              Setup Automated Reports
            </Button>
          </CardContent>
        </Card>
      </Box>
      </Box>
    </Box>
  );
}

import React from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';

const CasesPage: React.FC = () => {
  const cases = [
    {
      id: 'case-001',
      title: 'Auto Insurance Claim',
      description: 'Vehicle damage from collision',
      case_type: 'auto_insurance',
      urgency: 'high',
      risk_level: 'medium',
      status: 'pending',
      assigned_team: 'Auto Claims'
    },
    {
      id: 'case-002',
      title: 'Medical Prior Authorization',
      description: 'Cardiac surgery approval needed',
      case_type: 'healthcare_prior_auth',
      urgency: 'critical',
      risk_level: 'high',
      status: 'in_review',
      assigned_team: 'Medical Review'
    },
    {
      id: 'case-003',
      title: 'Property Damage Claim',
      description: 'Home damage from storm',
      case_type: 'property_insurance',
      urgency: 'medium',
      risk_level: 'low',
      status: 'new',
      assigned_team: 'Property Claims'
    }
  ];

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom>
        Cases Management
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Case ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Urgency</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Assigned Team</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {cases.map((caseItem) => (
              <TableRow key={caseItem.id}>
                <TableCell>{caseItem.id}</TableCell>
                <TableCell>{caseItem.title}</TableCell>
                <TableCell>{caseItem.case_type.replace('_', ' ')}</TableCell>
                <TableCell>
                  <Chip 
                    label={caseItem.urgency} 
                    color={getUrgencyColor(caseItem.urgency) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={caseItem.risk_level} 
                    color={getRiskColor(caseItem.risk_level) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{caseItem.status}</TableCell>
                <TableCell>{caseItem.assigned_team}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default CasesPage;

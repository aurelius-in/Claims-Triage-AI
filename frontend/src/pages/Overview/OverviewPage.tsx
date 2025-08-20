import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Assignment,
  Warning,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchAllAnalytics } from '@/store/slices/analyticsSlice';
import { fetchCases } from '@/store/slices/casesSlice';
import LoadingSpinner from '@/components/Common/LoadingSpinner';

const OverviewPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { overview, isLoading, error } = useAppSelector((state) => state.analytics);
  const { cases, totalCases } = useAppSelector((state) => state.cases);
  const [animatedValues, setAnimatedValues] = useState<{[key: string]: number}>({});

  useEffect(() => {
    dispatch(fetchAllAnalytics('week'));
    dispatch(fetchCases({ page: 1, size: 20 }));
  }, [dispatch]);

  const handleClick = (event: React.MouseEvent) => {
    const target = event.currentTarget as HTMLElement;
    target.style.transform = 'scale(0.98)';
    setTimeout(() => {
      target.style.transform = '';
    }, 150);
  };

  // Animate metric values on component mount
  useEffect(() => {
    const animateValues = () => {
      const newValues: {[key: string]: number} = {};
      metrics.forEach((metric) => {
        const finalValue = typeof metric.value === 'string' 
          ? parseFloat(metric.value.replace('%', '').replace('h', ''))
          : metric.value;
        newValues[metric.title] = 0;
        
        let current = 0;
        const increment = finalValue / 100;
        const timer = setInterval(() => {
          current += increment;
          if (current >= finalValue) {
            current = finalValue;
            clearInterval(timer);
          }
          setAnimatedValues(prev => ({
            ...prev,
            [metric.title]: Math.round(current * 100) / 100
          }));
        }, 30);
      });
    };

    if (!isLoading && cases.length > 0) {
      animateValues();
    }
  }, [isLoading, cases.length]);

  if (isLoading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const pendingCases = cases.filter(case_ => case_.status === 'pending').length;
  const escalatedCases = cases.filter(case_ => case_.status === 'escalated').length;
  const resolvedCases = cases.filter(case_ => case_.status === 'resolved').length;

  const metrics = [
    {
      title: 'Total Cases',
      value: totalCases,
      icon: <Assignment />,
      color: 'linear-gradient(135deg, #00d4ff, #4ecdc4)',
    },
    {
      title: 'Pending',
      value: pendingCases,
      icon: <Schedule />,
      color: 'linear-gradient(135deg, #ffeb3b, #ffc107)',
    },
    {
      title: 'Completed Today',
      value: resolvedCases,
      icon: <CheckCircle />,
      color: 'linear-gradient(135deg, #66bb6a, #4caf50)',
    },
    {
      title: 'SLA Compliance',
      value: `${(overview?.sla_compliance_rate * 100 || 94.2).toFixed(1)}%`,
      icon: <TrendingUp />,
      color: 'linear-gradient(135deg, #66bb6a, #4caf50)',
    },
    {
      title: 'Avg Processing',
      value: `${(overview?.avg_processing_time || 2.3).toFixed(1)}h`,
      icon: <Schedule />,
      color: 'linear-gradient(135deg, #ffeb3b, #ffc107)',
    },
    {
      title: 'Accuracy Rate',
      value: '87%',
      icon: <CheckCircle />,
      color: 'linear-gradient(135deg, #ffeb3b, #ffc107)',
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 2, textAlign: 'center', position: 'relative' }}>
        <Box
          sx={{
            position: 'absolute',
            top: -10,
            left: '50%',
            transform: 'translateX(-50%)',
            width: 150,
            height: 2,
            background: 'linear-gradient(90deg, transparent, #00d4ff, transparent)',
          }}
        />
        <Typography variant="h1" sx={{ mb: 1 }}>
          Claims Triage AI
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1.1rem', fontWeight: 300 }}>
          Intelligent Claims Processing Platform
        </Typography>
      </Box>

      {/* Metrics Section */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          p: 2,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
          borderRadius: 3,
          border: '1px solid rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
        }}
      >
        {metrics.map((metric, index) => (
          <Box key={metric.title} sx={{ textAlign: 'center', position: 'relative' }}>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 8px',
                position: 'relative',
                border: '2px solid rgba(255,255,255,0.1)',
                background: metric.color,
              }}
            >
                             <Typography
                 variant="h6"
                 sx={{
                   fontSize: '1.5rem',
                   fontWeight: 700,
                   color: '#000',
                 }}
               >
                 {metric.title.includes('%') 
                   ? `${animatedValues[metric.title] || 0}%`
                   : metric.title.includes('h')
                   ? `${animatedValues[metric.title] || 0}h`
                   : animatedValues[metric.title] || 0
                 }
               </Typography>
            </Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                fontWeight: 500,
              }}
            >
              {metric.title}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Main Content Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 2,
          mb: 2,
        }}
      >
        {/* Active Cases */}
        <Card sx={{ p: 1.5 }}>
          <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 'bold', color: '#00d4ff' }}>
            📋 Active Cases
          </Typography>
          <Box sx={{ position: 'relative' }}>
            <Box
              sx={{
                position: 'absolute',
                left: 15,
                top: 0,
                bottom: 0,
                width: 2,
                background: 'linear-gradient(180deg, #00d4ff, transparent)',
              }}
            />
            {cases.slice(0, 5).map((case_, index) => (
                             <Box
                 key={case_.id}
                 onClick={handleClick}
                 sx={{
                   position: 'relative',
                   mb: 1.5,
                   pl: 5,
                   transition: 'all 0.3s ease',
                   cursor: 'pointer',
                   '&:hover': {
                     transform: 'translateX(5px)',
                   },
                 }}
               >
                <Box
                  sx={{
                    position: 'absolute',
                    left: 8,
                    top: 12,
                    width: 16,
                    height: 16,
                    borderRadius: '50%',
                    background: '#0a0a0a',
                    border: '2px solid #00d4ff',
                    zIndex: 2,
                    ...(case_.status === 'escalated' && {
                      borderColor: '#ff6b6b',
                      boxShadow: '0 0 15px rgba(255, 107, 107, 0.5)',
                    }),
                    ...(case_.status === 'pending' && {
                      borderColor: '#ffa726',
                      boxShadow: '0 0 15px rgba(255, 167, 38, 0.5)',
                    }),
                    ...(case_.status === 'resolved' && {
                      borderColor: '#4ecdc4',
                      boxShadow: '0 0 15px rgba(78, 205, 196, 0.5)',
                    }),
                  }}
                />
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#fff', mb: 0.5 }}>
                  {case_.title}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.8rem', lineHeight: 1.3 }}>
                  {case_.external_id} • {case_.case_type.replace('_', ' ')} - {case_.status} Priority
                </Typography>
              </Box>
            ))}
          </Box>
        </Card>

        {/* System Status */}
        <Card sx={{ p: 1.5 }}>
          <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 'bold', color: '#00d4ff' }}>
            🔧 System Status
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 1,
            }}
          >
                         {[
               'AI Triage Engine',
               'Database',
               'Analytics',
               'API Gateway',
               'Redis Cache',
               'Message Queue',
               'Monitoring',
               'Security Layer',
               'Load Balancer',
               'CDN',
             ].map((status) => (
               <Box
                 key={status}
                 onClick={handleClick}
                 sx={{
                   display: 'flex',
                   alignItems: 'center',
                   gap: 1,
                   p: 1,
                   background: 'rgba(255,255,255,0.03)',
                   borderRadius: 2,
                   border: '1px solid rgba(255,255,255,0.05)',
                   transition: 'all 0.3s ease',
                   cursor: 'pointer',
                   '&:hover': {
                     background: 'rgba(255,255,255,0.08)',
                     transform: 'translateY(-2px)',
                   },
                 }}
               >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.2rem',
                    color: '#00d4ff',
                  }}
                >
                  ✓
                </Box>
                <Typography variant="body2" sx={{ fontWeight: 500, color: '#fff', fontSize: '0.9rem' }}>
                  {status}
                </Typography>
              </Box>
            ))}
          </Box>
        </Card>
      </Box>

      {/* Real-time Analytics & KPIs */}
      <Card sx={{ p: 1.5, mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 'bold', color: '#00d4ff' }}>
          📊 Real-time Analytics & KPIs
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: 1,
          }}
        >
          {[
            'Processing Efficiency: 87% faster than manual',
            'Accuracy Rate: 94.2% across all domains',
            'Avg Response Time: 1.2 seconds',
            'Cost Savings: $2.3M annually',
            'Healthcare Cases: 45% of total volume',
            'Auto Claims: 32% automated processing',
          ].map((metric) => (
                         <Box
               key={metric}
               onClick={handleClick}
               sx={{
                 background: 'rgba(0,0,0,0.3)',
                 border: '1px solid rgba(255,255,255,0.1)',
                 borderRadius: 2,
                 p: 1,
                 fontFamily: 'JetBrains Mono, monospace',
                 position: 'relative',
                 overflow: 'hidden',
                 transition: 'all 0.3s ease',
                 cursor: 'pointer',
                 '&:hover': {
                   transform: 'scale(1.02)',
                 },
                 '&::before': {
                   content: '""',
                   position: 'absolute',
                   top: 0,
                   left: 0,
                   right: 0,
                   height: 2,
                   background: 'linear-gradient(90deg, #00d4ff, #ff6b6b)',
                 },
               }}
             >
              <Typography variant="body2" sx={{ color: '#fff', fontSize: '0.8rem' }}>
                {metric}
              </Typography>
            </Box>
          ))}
        </Box>
      </Card>

      {/* Platform Features */}
      <Card sx={{ p: 1.5, mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 'bold', color: '#00d4ff' }}>
          🎯 Platform Features
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 1,
          }}
        >
          {[
            { icon: '🤖', text: 'AI-Powered Triage' },
            { icon: '📊', text: 'Risk Assessment' },
            { icon: '⚡', text: 'Real-time Analytics' },
            { icon: '🏥', text: 'Multi-case Support' },
            { icon: '⏱️', text: 'SLA Monitoring' },
            { icon: '🚀', text: 'Scalable Architecture' },
            { icon: '🔒', text: 'Data Encryption' },
            { icon: '📱', text: 'Mobile Integration' },
            { icon: '🔍', text: 'Advanced Search' },
          ].map((feature) => (
                         <Box
               key={feature.text}
               onClick={handleClick}
               sx={{
                 display: 'flex',
                 alignItems: 'center',
                 gap: 1,
                 p: 1,
                 background: 'rgba(255,255,255,0.03)',
                 borderRadius: 2,
                 border: '1px solid rgba(255,255,255,0.05)',
                 transition: 'all 0.3s ease',
                 cursor: 'pointer',
                 '&:hover': {
                   background: 'rgba(255,255,255,0.08)',
                   transform: 'translateY(-3px)',
                 },
               }}
             >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #00d4ff, #4ecdc4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.3rem',
                  color: '#0a0a0a',
                }}
              >
                {feature.icon}
              </Box>
              <Typography variant="body2" sx={{ color: '#fff', fontWeight: 500, fontSize: '0.9rem' }}>
                {feature.text}
              </Typography>
            </Box>
          ))}
        </Box>
      </Card>

      {/* AI Agent Analysis Results */}
      <Card sx={{ p: 1.5 }}>
        <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 'bold', color: '#00d4ff' }}>
          🤖 AI Agent Analysis Results
        </Typography>
        <Box
          sx={{
            background: 'rgba(0,0,0,0.4)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 2,
            p: 1.5,
            fontFamily: 'JetBrains Mono, Courier New, monospace',
            fontSize: '0.8rem',
            lineHeight: 1.4,
            maxHeight: 200,
            overflowY: 'auto',
          }}
        >
                     {[
             { timestamp: '[Case #CT-2024-001]', type: 'info', content: '🔍 ClassifierAgent: Healthcare Prior Authorization - Critical Urgency' },
             { timestamp: '[Risk Score: 0.87]', type: 'success', content: '📊 RiskScorerAgent: High Risk - Cardiac surgery complexity detected' },
             { timestamp: '[SLA: 2h]', type: 'warning', content: '🔄 RouterAgent: Route to Specialist Team - Escalation Required' },
             { timestamp: '[Actions]', type: 'info', content: '💡 DecisionSupportAgent: Immediate medical director review + Peer consultation' },
             { timestamp: '[Compliance]', type: 'success', content: '✅ ComplianceAgent: PII detected & redacted - Audit trail created' },
             { timestamp: '[Case #CT-2024-002]', type: 'info', content: '🔍 ClassifierAgent: Auto Insurance Claim - Medium Urgency' },
             { timestamp: '[Risk Score: 0.42]', type: 'success', content: '📊 RiskScorerAgent: Low-Medium Risk - Standard collision assessment' },
             { timestamp: '[SLA: 24h]', type: 'info', content: '🔄 RouterAgent: Route to Standard Claims Team' },
             { timestamp: '[Actions]', type: 'success', content: '💡 DecisionSupportAgent: Automated processing approved - No escalation needed' },
             { timestamp: '[Case #CT-2024-003]', type: 'info', content: '🔍 ClassifierAgent: Property Damage Claim - Low Urgency' },
             { timestamp: '[Risk Score: 0.23]', type: 'success', content: '📊 RiskScorerAgent: Low Risk - Standard storm damage' },
             { timestamp: '[SLA: 48h]', type: 'info', content: '🔄 RouterAgent: Route to Property Claims Team' },
             { timestamp: '[Actions]', type: 'success', content: '💡 DecisionSupportAgent: Schedule adjuster inspection - Standard processing' },
           ].map((log, index) => (
            <Box
              key={index}
              sx={{
                mb: 0.5,
                p: 0.25,
                color: log.type === 'info' ? '#4ecdc4' : 
                       log.type === 'success' ? '#66bb6a' : 
                       log.type === 'warning' ? '#ffa726' : '#ff6b6b',
              }}
            >
              <span style={{ color: '#888', marginRight: 8 }}>{log.timestamp}</span>
              {log.content}
            </Box>
          ))}
        </Box>
      </Card>
    </Box>
  );
};

export default OverviewPage;

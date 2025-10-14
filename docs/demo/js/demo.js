// Claims Triage AI - Demo JavaScript
class ClaimsTriageDemo {
  constructor() {
    this.currentTab = 'overview';
    this.mockData = this.generateMockData();
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.animateMetrics();
    this.startRealTimeUpdates();
    this.loadMockData();
  }

  setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // Case selection
    document.querySelectorAll('.case-row').forEach(row => {
      row.addEventListener('click', () => {
        this.selectCase(row.dataset.caseId);
      });
    });

    // Filter controls
    document.querySelectorAll('.filter-select').forEach(select => {
      select.addEventListener('change', () => {
        this.applyFilters();
      });
    });

    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(() => {
        this.applyFilters();
      }, 300));
    }

    // Bulk actions
    document.querySelectorAll('.bulk-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.performBulkAction(e.target.dataset.action);
      });
    });

    // Refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.refreshData();
      });
    }
  }

  switchTab(tabName) {
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Show/hide content
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.querySelector(`#${tabName}-content`).classList.add('active');

    this.currentTab = tabName;
    
    // Load tab-specific data
    this.loadTabData(tabName);
  }

  loadTabData(tabName) {
    switch (tabName) {
      case 'overview':
        this.loadOverviewData();
        break;
      case 'triage':
        this.loadTriageData();
        break;
      case 'analytics':
        this.loadAnalyticsData();
        break;
      case 'audit':
        this.loadAuditData();
        break;
      case 'investment':
        this.loadInvestmentData();
        break;
        case 'pricing':
            this.loadPricingData();
            break;
        case 'documentation':
            this.loadDocumentationData();
            break;
    }
  }

  loadOverviewData() {
    // Update metrics with animated values
    this.animateMetrics();
    
    // Update active cases
    this.updateActiveCases();
    
    // Update system status
    this.updateSystemStatus();
    
    // Update AI log
    this.updateAILog();
  }

  loadTriageData() {
    // Load cases table
    this.renderCasesTable();
    
    // Update filters
    this.updateFilterCounts();
  }

  loadAnalyticsData() {
    // Load analytics charts and metrics
    this.renderAnalyticsCharts();
  }

  loadAuditData() {
    // Load audit trail
    this.renderAuditTrail();
  }

  animateMetrics() {
    const metrics = [
      { selector: '.metric-total-cases', value: 1247 },
      { selector: '.metric-pending', value: 89 },
      { selector: '.metric-completed', value: 156 },
      { selector: '.metric-sla-compliance', value: 94.2 },
      { selector: '.metric-avg-processing', value: 2.3 },
      { selector: '.metric-accuracy', value: 87 }
    ];

    metrics.forEach(metric => {
      const element = document.querySelector(metric.selector);
      if (element) {
        this.animateNumber(element, metric.value, metric.value > 100 ? 0 : 1);
      }
    });
  }

  animateNumber(element, targetValue, decimals = 0) {
    const startValue = 0;
    const duration = 2000;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const currentValue = startValue + (targetValue - startValue) * this.easeOutCubic(progress);
      
      if (decimals === 0) {
        element.textContent = Math.round(currentValue);
      } else {
        element.textContent = currentValue.toFixed(decimals);
      }

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  updateActiveCases() {
    const activeCasesContainer = document.querySelector('.active-cases');
    if (!activeCasesContainer) return;

    const recentCases = this.mockData.cases.slice(0, 5);
    activeCasesContainer.innerHTML = '';

    recentCases.forEach(caseItem => {
      const caseElement = document.createElement('div');
      caseElement.className = 'case-item';
      caseElement.innerHTML = `
        <div class="case-status-indicator ${caseItem.status}"></div>
        <div class="case-content">
          <div class="case-title">${caseItem.title}</div>
          <div class="case-meta">${caseItem.case_id} • ${caseItem.type} • ${caseItem.priority} Priority</div>
        </div>
      `;
      activeCasesContainer.appendChild(caseElement);
    });
  }

  updateSystemStatus() {
    const systemStatus = [
      { name: 'AI Triage Engine', status: 'operational' },
      { name: 'Database', status: 'operational' },
      { name: 'Analytics', status: 'operational' },
      { name: 'API Gateway', status: 'operational' },
      { name: 'Redis Cache', status: 'operational' },
      { name: 'Message Queue', status: 'operational' },
      { name: 'Monitoring', status: 'operational' },
      { name: 'Security Layer', status: 'operational' },
      { name: 'Load Balancer', status: 'operational' },
      { name: 'CDN', status: 'operational' }
    ];

    const statusContainer = document.querySelector('.system-status');
    if (!statusContainer) return;

    statusContainer.innerHTML = '';

    systemStatus.forEach(item => {
      const statusElement = document.createElement('div');
      statusElement.className = 'status-item';
      statusElement.innerHTML = `
        <div class="status-indicator-icon">✓</div>
        <div class="status-item-name">${item.name}</div>
      `;
      statusContainer.appendChild(statusElement);
    });
  }

  updateAILog() {
    const aiLogContainer = document.querySelector('.ai-log');
    if (!aiLogContainer) return;

    const logEntries = [
      { timestamp: '[Case #CT-2024-001]', type: 'info', content: '🔍 ClassifierAgent: Healthcare Prior Authorization - Critical Urgency' },
      { timestamp: '[Risk Score: 0.87]', type: 'success', content: '📊 RiskScorerAgent: High Risk - Cardiac surgery complexity detected' },
      { timestamp: '[SLA: 2h]', type: 'warning', content: '🔄 RouterAgent: Route to Specialist Team - Escalation Required' },
      { timestamp: '[Actions]', type: 'info', content: '💡 DecisionSupportAgent: Immediate medical director review + Peer consultation' },
      { timestamp: '[Compliance]', type: 'success', content: '✅ ComplianceAgent: PII detected & redacted - Audit trail created' },
      { timestamp: '[Case #CT-2024-002]', type: 'info', content: '🔍 ClassifierAgent: Auto Insurance Claim - Medium Urgency' },
      { timestamp: '[Risk Score: 0.42]', type: 'success', content: '📊 RiskScorerAgent: Low-Medium Risk - Standard collision assessment' },
      { timestamp: '[SLA: 24h]', type: 'info', content: '🔄 RouterAgent: Route to Standard Claims Team' },
      { timestamp: '[Actions]', type: 'success', content: '💡 DecisionSupportAgent: Automated processing approved - No escalation needed' }
    ];

    aiLogContainer.innerHTML = '';

    logEntries.forEach(entry => {
      const logElement = document.createElement('div');
      logElement.className = `ai-log-entry log-${entry.type}`;
      logElement.innerHTML = `
        <span class="log-timestamp">${entry.timestamp}</span>
        ${entry.content}
      `;
      aiLogContainer.appendChild(logElement);
    });
  }

  renderCasesTable() {
    const tableBody = document.querySelector('.cases-table tbody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    this.mockData.cases.forEach(caseItem => {
      const row = document.createElement('tr');
      row.className = 'case-row';
      row.dataset.caseId = caseItem.id;
      row.innerHTML = `
        <td>
          <input type="checkbox" class="case-checkbox" data-case-id="${caseItem.id}">
        </td>
        <td><strong>${caseItem.case_id}</strong></td>
        <td>${caseItem.title}</td>
        <td><span class="case-type"><span class="case-type-icon">${this.getCaseTypeIcon(caseItem.type)}</span>${caseItem.type}</span></td>
        <td><span class="status-indicator status-${caseItem.status}"><span class="status-dot"></span>${caseItem.status}</span></td>
        <td><span class="status-indicator risk-${caseItem.risk_level}">${caseItem.risk_level}</span></td>
        <td>${new Date(caseItem.created_at).toLocaleDateString()}</td>
        <td>${caseItem.assigned_user || 'Unassigned'}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="demo.viewCase('${caseItem.id}')">View</button>
          <button class="btn btn-primary btn-sm" onclick="demo.runTriage('${caseItem.id}')">Triage</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  }

  getCaseTypeIcon(type) {
    const icons = {
      'insurance': '🏢',
      'healthcare': '🏥',
      'finance': '💰',
      'legal': '⚖️'
    };
    return icons[type] || '📋';
  }

  selectCase(caseId) {
    // Remove previous selection
    document.querySelectorAll('.case-row').forEach(row => {
      row.classList.remove('selected');
    });

    // Add selection to clicked row
    const selectedRow = document.querySelector(`[data-case-id="${caseId}"]`);
    if (selectedRow) {
      selectedRow.classList.add('selected');
    }

    // Show case details
    this.showCaseDetails(caseId);
  }

  showCaseDetails(caseId) {
    const caseItem = this.mockData.cases.find(c => c.id === caseId);
    if (!caseItem) return;

    // Update case details modal or sidebar
    const detailsModal = document.querySelector('.case-details-modal');
    if (detailsModal) {
      detailsModal.innerHTML = `
        <div class="case-details-header">
          <h3>Case Details - ${caseItem.case_id}</h3>
          <button class="btn-close" onclick="demo.closeCaseDetails()">×</button>
        </div>
        <div class="case-details-content">
          <div class="detail-section">
            <h4>Basic Information</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Case ID:</label>
                <span>${caseItem.case_id}</span>
              </div>
              <div class="detail-item">
                <label>Type:</label>
                <span class="case-type"><span class="case-type-icon">${this.getCaseTypeIcon(caseItem.type)}</span>${caseItem.type}</span>
              </div>
              <div class="detail-item">
                <label>Title:</label>
                <span>${caseItem.title}</span>
              </div>
              <div class="detail-item">
                <label>Description:</label>
                <span>${caseItem.description}</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <h4>Status & Risk</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Status:</label>
                <span class="status-indicator status-${caseItem.status}"><span class="status-dot"></span>${caseItem.status}</span>
              </div>
              <div class="detail-item">
                <label>Risk Level:</label>
                <span class="status-indicator risk-${caseItem.risk_level}">${caseItem.risk_level}</span>
              </div>
              <div class="detail-item">
                <label>Risk Score:</label>
                <span>${(caseItem.risk_score * 100).toFixed(1)}%</span>
              </div>
              <div class="detail-item">
                <label>Priority:</label>
                <span>${caseItem.priority}</span>
              </div>
            </div>
          </div>
        </div>
      `;
      detailsModal.classList.add('show');
    }
  }

  closeCaseDetails() {
    const detailsModal = document.querySelector('.case-details-modal');
    if (detailsModal) {
      detailsModal.classList.remove('show');
    }
  }

  runTriage(caseId) {
    // Show loading state
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Processing...';
    button.disabled = true;

    // Simulate triage processing
    setTimeout(() => {
      button.textContent = 'Completed';
      button.classList.add('btn-success');
      
      // Show success notification
      this.showNotification('Triage completed successfully', 'success');
      
      // Reset button after delay
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
        button.classList.remove('btn-success');
      }, 2000);
    }, 2000);
  }

  viewCase(caseId) {
    this.selectCase(caseId);
    this.showCaseDetails(caseId);
  }

  applyFilters() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('status-filter')?.value || '';
    const typeFilter = document.getElementById('type-filter')?.value || '';
    const riskFilter = document.getElementById('risk-filter')?.value || '';

    const filteredCases = this.mockData.cases.filter(caseItem => {
      const matchesSearch = !searchTerm || 
        caseItem.title.toLowerCase().includes(searchTerm) ||
        caseItem.description.toLowerCase().includes(searchTerm) ||
        caseItem.case_id.toLowerCase().includes(searchTerm);
      
      const matchesStatus = !statusFilter || caseItem.status === statusFilter;
      const matchesType = !typeFilter || caseItem.type === typeFilter;
      const matchesRisk = !riskFilter || caseItem.risk_level === riskFilter;

      return matchesSearch && matchesStatus && matchesType && matchesRisk;
    });

    this.renderFilteredCases(filteredCases);
  }

  renderFilteredCases(cases) {
    const tableBody = document.querySelector('.cases-table tbody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    cases.forEach(caseItem => {
      const row = document.createElement('tr');
      row.className = 'case-row';
      row.dataset.caseId = caseItem.id;
      row.innerHTML = `
        <td>
          <input type="checkbox" class="case-checkbox" data-case-id="${caseItem.id}">
        </td>
        <td><strong>${caseItem.case_id}</strong></td>
        <td>${caseItem.title}</td>
        <td><span class="case-type"><span class="case-type-icon">${this.getCaseTypeIcon(caseItem.type)}</span>${caseItem.type}</span></td>
        <td><span class="status-indicator status-${caseItem.status}"><span class="status-dot"></span>${caseItem.status}</span></td>
        <td><span class="status-indicator risk-${caseItem.risk_level}">${caseItem.risk_level}</span></td>
        <td>${new Date(caseItem.created_at).toLocaleDateString()}</td>
        <td>${caseItem.assigned_user || 'Unassigned'}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="demo.viewCase('${caseItem.id}')">View</button>
          <button class="btn btn-primary btn-sm" onclick="demo.runTriage('${caseItem.id}')">Triage</button>
        </td>
      `;
      tableBody.appendChild(row);
    });

    // Update tab counts
    this.updateFilterCounts(cases);
  }

  updateFilterCounts(cases = this.mockData.cases) {
    const pendingCount = cases.filter(c => c.status === 'pending').length;
    const inProgressCount = cases.filter(c => c.status === 'in_progress').length;
    const highRiskCount = cases.filter(c => c.risk_level === 'high' || c.risk_level === 'critical').length;

    document.querySelector('.tab-pending .tab-count')?.textContent = pendingCount;
    document.querySelector('.tab-in-progress .tab-count')?.textContent = inProgressCount;
    document.querySelector('.tab-high-risk .tab-count')?.textContent = highRiskCount;
  }

  performBulkAction(action) {
    const selectedCases = Array.from(document.querySelectorAll('.case-checkbox:checked'))
      .map(checkbox => checkbox.dataset.caseId);

    if (selectedCases.length === 0) {
      this.showNotification('Please select cases to perform bulk action', 'warning');
      return;
    }

    this.showNotification(`Performing ${action} on ${selectedCases.length} cases...`, 'info');

    // Simulate bulk action processing
    setTimeout(() => {
      this.showNotification(`${action} completed successfully on ${selectedCases.length} cases`, 'success');
      this.refreshData();
    }, 2000);
  }

  refreshData() {
    // Show loading state
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.innerHTML = '<span class="loading"></span> Refreshing...';
      refreshBtn.disabled = true;
    }

    // Simulate data refresh
    setTimeout(() => {
      this.loadMockData();
      
      if (refreshBtn) {
        refreshBtn.innerHTML = '🔄 Refresh';
        refreshBtn.disabled = false;
      }

      this.showNotification('Data refreshed successfully', 'success');
    }, 1500);
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }

  startRealTimeUpdates() {
    // Simulate real-time updates every 30 seconds
    setInterval(() => {
      this.updateRealTimeData();
    }, 30000);
  }

  updateRealTimeData() {
    // Update metrics with small random changes
    const metrics = document.querySelectorAll('.metric-value');
    metrics.forEach(metric => {
      const currentValue = parseFloat(metric.textContent);
      const change = (Math.random() - 0.5) * 0.1; // ±5% change
      const newValue = Math.max(0, currentValue + change);
      
      if (metric.textContent.includes('%')) {
        metric.textContent = newValue.toFixed(1) + '%';
      } else if (metric.textContent.includes('h')) {
        metric.textContent = newValue.toFixed(1) + 'h';
      } else {
        metric.textContent = Math.round(newValue);
      }
    });

    // Add new AI log entry occasionally
    if (Math.random() > 0.7) {
      this.addNewAILogEntry();
    }
  }

  addNewAILogEntry() {
    const aiLogContainer = document.querySelector('.ai-log');
    if (!aiLogContainer) return;

    const newEntries = [
      { timestamp: '[Case #CT-2024-003]', type: 'info', content: '🔍 ClassifierAgent: Property Damage Claim - Low Urgency' },
      { timestamp: '[Risk Score: 0.23]', type: 'success', content: '📊 RiskScorerAgent: Low Risk - Standard storm damage' },
      { timestamp: '[SLA: 48h]', type: 'info', content: '🔄 RouterAgent: Route to Property Claims Team' },
      { timestamp: '[Actions]', type: 'success', content: '💡 DecisionSupportAgent: Schedule adjuster inspection - Standard processing' }
    ];

    const randomEntry = newEntries[Math.floor(Math.random() * newEntries.length)];
    
    const logElement = document.createElement('div');
    logElement.className = `ai-log-entry log-${randomEntry.type}`;
    logElement.innerHTML = `
      <span class="log-timestamp">${randomEntry.timestamp}</span>
      ${randomEntry.content}
    `;

    aiLogContainer.insertBefore(logElement, aiLogContainer.firstChild);

    // Remove old entries if too many
    const entries = aiLogContainer.querySelectorAll('.ai-log-entry');
    if (entries.length > 15) {
      entries[entries.length - 1].remove();
    }
  }

  loadMockData() {
    // This would typically load data from an API
    // For demo purposes, we'll use the generated mock data
    this.renderCasesTable();
    this.updateFilterCounts();
  }

  generateMockData() {
    const caseTypes = ['insurance', 'healthcare', 'finance', 'legal'];
    const statuses = ['pending', 'in_progress', 'resolved', 'escalated'];
    const riskLevels = ['low', 'medium', 'high', 'critical'];
    const priorities = ['Low', 'Medium', 'High', 'Critical'];
    const assignedUsers = ['John Smith', 'Sarah Johnson', 'Mike Chen', 'Lisa Rodriguez', null];

    const sampleCases = [
      {
        id: '1',
        case_id: 'CT-2024-001',
        title: 'Healthcare Prior Authorization Request',
        description: 'Complex cardiac surgery requiring prior authorization with multiple specialists involved.',
        type: 'healthcare',
        status: 'escalated',
        risk_level: 'high',
        risk_score: 0.87,
        priority: 'Critical',
        assigned_user: 'Dr. Sarah Johnson',
        created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '2',
        case_id: 'CT-2024-002',
        title: 'Auto Insurance Collision Claim',
        description: 'Standard vehicle collision claim with minor injuries and property damage.',
        type: 'insurance',
        status: 'in_progress',
        risk_level: 'medium',
        risk_score: 0.42,
        priority: 'Medium',
        assigned_user: 'Mike Chen',
        created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
      },
      {
        id: '3',
        case_id: 'CT-2024-003',
        title: 'Property Damage Storm Claim',
        description: 'Residential property damage from severe weather event.',
        type: 'insurance',
        status: 'pending',
        risk_level: 'low',
        risk_score: 0.23,
        priority: 'Low',
        assigned_user: null,
        created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '4',
        case_id: 'CT-2024-004',
        title: 'Financial Dispute Resolution',
        description: 'Credit card dispute involving unauthorized transactions.',
        type: 'finance',
        status: 'resolved',
        risk_level: 'medium',
        risk_score: 0.56,
        priority: 'Medium',
        assigned_user: 'Lisa Rodriguez',
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: '5',
        case_id: 'CT-2024-005',
        title: 'Legal Document Review',
        description: 'Contract review and compliance assessment for new vendor agreement.',
        type: 'legal',
        status: 'in_progress',
        risk_level: 'high',
        risk_score: 0.74,
        priority: 'High',
        assigned_user: 'John Smith',
        created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
      }
    ];

    // Generate additional mock cases
    for (let i = 6; i <= 20; i++) {
      const caseType = caseTypes[Math.floor(Math.random() * caseTypes.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      const riskLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)];
      const priority = priorities[Math.floor(Math.random() * priorities.length)];
      const assignedUser = assignedUsers[Math.floor(Math.random() * assignedUsers.length)];

      sampleCases.push({
        id: i.toString(),
        case_id: `CT-2024-${i.toString().padStart(3, '0')}`,
        title: `${caseType.charAt(0).toUpperCase() + caseType.slice(1)} Case ${i}`,
        description: `Sample ${caseType} case description with various complexity levels.`,
        type: caseType,
        status: status,
        risk_level: riskLevel,
        risk_score: Math.random(),
        priority: priority,
        assigned_user: assignedUser,
        created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
      });
    }

    return {
      cases: sampleCases,
      metrics: {
        totalCases: sampleCases.length,
        pendingCases: sampleCases.filter(c => c.status === 'pending').length,
        resolvedCases: sampleCases.filter(c => c.status === 'resolved').length,
        escalatedCases: sampleCases.filter(c => c.status === 'escalated').length,
        avgProcessingTime: 2.3,
        slaCompliance: 94.2,
        accuracyRate: 87
      }
    };
  }

  renderAnalyticsCharts() {
    // This would integrate with a charting library like Chart.js or D3.js
    // For demo purposes, we'll create simple visual representations
    console.log('Rendering analytics charts...');
  }

  renderAuditTrail() {
    // Render audit trail data
    console.log('Rendering audit trail...');
  }

  loadInvestmentData() {
    // Load investment-specific data and charts
    this.animateRevenueProjections();
    this.updateMarketMetrics();
  }

        loadPricingData() {
            // Load pricing data and initialize ROI calculator
            this.initializeROICalculator();
            this.updatePricingComparison();
        }

        loadDocumentationData() {
            // Load documentation viewer functionality
            this.initializeDocumentViewer();
            this.setupDocumentNavigation();
            this.setupSearchFilters();
        }

  animateRevenueProjections() {
    // Animate the revenue projection bars
    const bars = document.querySelectorAll('.projection-chart .bar');
    bars.forEach((bar, index) => {
      setTimeout(() => {
        bar.style.transform = 'scaleY(1)';
      }, index * 200);
    });
  }

  updateMarketMetrics() {
    // Update market metrics with real-time data
    const metrics = [
      { selector: '.metric-value', values: ['$47.2B', '$8.7B', '$1.2B'] },
    ];

    metrics.forEach(metric => {
      const elements = document.querySelectorAll(metric.selector);
      elements.forEach((element, index) => {
        if (metric.values[index]) {
          this.animateNumber(element, parseFloat(metric.values[index].replace('$', '').replace('B', '')), 1);
        }
      });
    });
  }

  initializeROICalculator() {
    const monthlyCasesInput = document.getElementById('monthly-cases');
    const currentCostInput = document.getElementById('current-cost');
    const currentTimeInput = document.getElementById('current-time');

    if (monthlyCasesInput && currentCostInput && currentTimeInput) {
      [monthlyCasesInput, currentCostInput, currentTimeInput].forEach(input => {
        input.addEventListener('input', () => {
          this.calculateROI();
        });
      });

      // Initial calculation
      this.calculateROI();
    }
  }

  calculateROI() {
    const monthlyCases = parseFloat(document.getElementById('monthly-cases')?.value) || 25000;
    const currentCost = parseFloat(document.getElementById('current-cost')?.value) || 15.50;
    const currentTime = parseFloat(document.getElementById('current-time')?.value) || 2.5;

    // Calculate current annual cost
    const currentAnnual = monthlyCases * currentCost * 12;
    
    // Our pricing (Professional tier for this calculation)
    const ourAnnual = 90000; // $7,500/month * 12
    
    // Calculate savings
    const annualSavings = currentAnnual - ourAnnual;
    
    // Calculate ROI
    const roi = ourAnnual > 0 ? ((annualSavings / ourAnnual) * 100) : 0;

    // Update display
    this.updateElement('current-annual', `$${currentAnnual.toLocaleString()}`);
    this.updateElement('new-annual', `$${ourAnnual.toLocaleString()}`);
    this.updateElement('annual-savings', `$${annualSavings.toLocaleString()}`);
    this.updateElement('roi', `${Math.round(roi)}%`);
  }

  updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value;
    }
  }

  updatePricingComparison() {
    // Update pricing comparison data
    const comparisonData = [
      { platform: 'UiPath', monthly: 12500, annual: 150000 },
      { platform: 'Automation Anywhere', monthly: 15000, annual: 180000 },
      { platform: 'Blue Prism', monthly: 18750, annual: 225000 }
    ];

    // This would update the comparison table with real-time data
    console.log('Updated pricing comparison data');
  }

  loadDocumentationData() {
    // Load documentation viewer functionality
    this.initializeDocumentViewer();
    this.setupDocumentNavigation();
    this.setupSearchFilters();
  }

  initializeDocumentViewer() {
    // Initialize the enterprise document viewer
    this.setupDocumentToolbar();
    this.loadDocumentContent('investor-deck');
    this.setupViewModes();
  }

  setupDocumentNavigation() {
    // Setup document navigation and selection
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        // Remove active class from all items
        navItems.forEach(nav => nav.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Load document content
        const docId = item.getAttribute('data-doc');
        this.loadDocumentContent(docId);
        
        // Update breadcrumb
        this.updateBreadcrumb(item);
      });
    });
  }

  setupSearchFilters() {
    // Setup search and filter functionality
    const searchInput = document.getElementById('docs-search');
    const categoryFilter = document.getElementById('filter-category');
    const typeFilter = document.getElementById('filter-type');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterDocuments(e.target.value);
      });
    }

    if (categoryFilter) {
      categoryFilter.addEventListener('change', (e) => {
        this.filterDocumentsByCategory(e.target.value);
      });
    }

    if (typeFilter) {
      typeFilter.addEventListener('change', (e) => {
        this.filterDocumentsByType(e.target.value);
      });
    }
  }

  setupDocumentToolbar() {
    // Setup document toolbar functionality
    const exportPdfBtn = document.getElementById('export-pdf');
    const exportExcelBtn = document.getElementById('export-excel');
    const shareDocBtn = document.getElementById('share-doc');
    const fullscreenBtn = document.getElementById('fullscreen');

    if (exportPdfBtn) {
      exportPdfBtn.addEventListener('click', () => {
        this.showNotification('Exporting document to PDF...', 'info');
      });
    }

    if (exportExcelBtn) {
      exportExcelBtn.addEventListener('click', () => {
        this.showNotification('Exporting data to Excel...', 'info');
      });
    }

    if (shareDocBtn) {
      shareDocBtn.addEventListener('click', () => {
        this.showShareModal();
      });
    }

    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => {
        this.toggleFullscreen();
      });
    }
  }

  setupViewModes() {
    // Setup document view modes (Read, Present, Annotate)
    const viewBtns = document.querySelectorAll('.view-btn');
    viewBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        viewBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const viewMode = btn.getAttribute('data-view');
        this.switchViewMode(viewMode);
      });
    });
  }

  loadDocumentContent(docId) {
    // Load document content based on ID
    const docsContent = document.getElementById('docs-content');
    if (!docsContent) return;

    // Show loading state
    this.showDocumentLoading();

    // Simulate document loading
    setTimeout(() => {
      this.hideDocumentLoading();
      this.showDocumentPreview(docId);
    }, 1000);
  }

  showDocumentLoading() {
    const placeholder = document.querySelector('.document-placeholder');
    if (placeholder) {
      placeholder.innerHTML = `
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p>Loading enterprise document...</p>
        </div>
      `;
    }
  }

  hideDocumentLoading() {
    const placeholder = document.querySelector('.document-placeholder');
    if (placeholder) {
      placeholder.style.display = 'none';
    }
  }

  showDocumentPreview(docId) {
    const docsContent = document.getElementById('docs-content');
    if (!docsContent) return;

    // Create document preview content
    const previewContent = this.generateDocumentPreview(docId);
    
    // Replace placeholder with actual content
    const placeholder = docsContent.querySelector('.document-placeholder');
    if (placeholder) {
      placeholder.innerHTML = previewContent;
      placeholder.style.display = 'block';
    }
  }

  generateDocumentPreview(docId) {
    const previews = {
      'investor-deck': `
        <div class="placeholder-icon">📊</div>
        <h3>Executive Investor Presentation</h3>
        <p>Comprehensive 45-slide presentation covering market opportunity, financial projections, competitive positioning, and growth strategy.</p>
        <div class="document-stats">
          <div class="stat-item">
            <span class="stat-number">45</span>
            <span class="stat-label">Slides</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">$47.2B</span>
            <span class="stat-label">TAM</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">300%+</span>
            <span class="stat-label">ROI</span>
          </div>
        </div>
      `,
      'financial-model': `
        <div class="placeholder-icon">💰</div>
        <h3>Financial Model & Projections</h3>
        <p>Detailed 5-year financial model with scenario analysis, unit economics, and revenue projections across multiple market segments.</p>
        <div class="document-stats">
          <div class="stat-item">
            <span class="stat-number">87</span>
            <span class="stat-label">Sheets</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">5-Year</span>
            <span class="stat-label">Projections</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">3</span>
            <span class="stat-label">Scenarios</span>
          </div>
        </div>
      `,
      'competitive-analysis': `
        <div class="placeholder-icon">⚔️</div>
        <h3>Comprehensive Competitive Analysis</h3>
        <p>In-depth analysis of 15+ competitors including feature comparison, market positioning, and strategic advantages.</p>
        <div class="document-stats">
          <div class="stat-item">
            <span class="stat-number">156</span>
            <span class="stat-label">Pages</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">15+</span>
            <span class="stat-label">Competitors</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">87%</span>
            <span class="stat-label">Faster</span>
          </div>
        </div>
      `
    };

    return previews[docId] || `
      <div class="placeholder-icon">📄</div>
      <h3>Professional Document</h3>
      <p>Enterprise-grade documentation with institutional standards and comprehensive analysis.</p>
    `;
  }

  filterDocuments(searchTerm) {
    // Filter documents based on search term
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      const title = item.querySelector('.doc-title')?.textContent.toLowerCase() || '';
      const meta = item.querySelector('.doc-meta')?.textContent.toLowerCase() || '';
      
      if (title.includes(searchTerm.toLowerCase()) || meta.includes(searchTerm.toLowerCase())) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  }

  filterDocumentsByCategory(category) {
    // Filter documents by category
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      if (category === 'all') {
        item.style.display = 'block';
      } else {
        // Logic to filter by category based on data attributes
        item.style.display = 'block';
      }
    });
  }

  filterDocumentsByType(type) {
    // Filter documents by type
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      if (type === 'all') {
        item.style.display = 'block';
      } else {
        // Logic to filter by type
        item.style.display = 'block';
      }
    });
  }

  updateBreadcrumb(navItem) {
    // Update breadcrumb navigation
    const breadcrumbActive = document.querySelector('.breadcrumb-item.active');
    const docTitle = navItem.querySelector('.doc-title')?.textContent || 'Document';
    
    if (breadcrumbActive) {
      breadcrumbActive.textContent = docTitle;
    }
  }

  switchViewMode(mode) {
    // Switch document view mode
    const docsContent = document.getElementById('docs-content');
    if (!docsContent) return;

    // Add view mode class for styling
    docsContent.className = docsContent.className.replace(/view-\w+/g, '');
    docsContent.classList.add(`view-${mode}`);

    this.showNotification(`Switched to ${mode} mode`, 'info');
  }

  showShareModal() {
    // Show share document modal
    this.showNotification('Document sharing functionality available in full version', 'info');
  }

  toggleFullscreen() {
    // Toggle fullscreen mode
    const container = document.querySelector('.docs-container');
    if (container) {
      if (container.classList.contains('fullscreen')) {
        container.classList.remove('fullscreen');
        this.showNotification('Exited fullscreen mode', 'info');
      } else {
        container.classList.add('fullscreen');
        this.showNotification('Entered fullscreen mode', 'info');
      }
    }
  }

  showNotification(message, type = 'info') {
    // Show notification to user
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--bg-secondary);
      color: var(--text-primary);
      padding: 1rem 1.5rem;
      border-radius: 8px;
      border: 1px solid var(--border-primary);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      z-index: 1000;
      animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}

// Utility function for debouncing
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Initialize demo when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.demo = new ClaimsTriageDemo();
});

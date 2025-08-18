# Claims Triage AI Documentation

Welcome to the comprehensive documentation for Claims Triage AI, a next-generation agent-driven case triage platform.

##  Quick Start

Get up and running in minutes:

```bash
git clone https://github.com/yourusername/Claims-Triage-AI.git
cd Claims-Triage-AI
make setup
make up
```

Access the platform:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)

##  Documentation Sections

###  Architecture
- [System Overview](architecture/overview.md) - High-level system design
- [Agent Architecture](architecture/agents.md) - AI agent system design
- [Data Architecture](architecture/data.md) - Database and storage design
- [Security Architecture](architecture/security.md) - Security and compliance

###  API Reference
- [Authentication](api/authentication.md) - User authentication and authorization
- [Cases](api/cases.md) - Case management endpoints
- [Triage](api/triage.md) - Triage pipeline endpoints
- [Analytics](api/analytics.md) - Analytics and reporting endpoints
- [Audit](api/audit.md) - Audit and compliance endpoints

###  User Guides
- [Dashboard](user-guides/dashboard.md) - Platform dashboard usage
- [Case Management](user-guides/case-management.md) - Managing cases
- [Analytics](user-guides/analytics.md) - Using analytics and reports
- [Settings](user-guides/settings.md) - Platform configuration

###  Developer Guides
- [Setup](developer/setup.md) - Development environment setup
- [Agent Development](developer/agents.md) - Building custom agents
- [API Development](developer/api.md) - Extending the API
- [Frontend Development](developer/frontend.md) - Frontend development
- [Testing](developer/testing.md) - Testing strategies

###  Deployment
- [Local Development](deployment/local.md) - Local development setup
- [Staging](deployment/staging.md) - Staging environment deployment
- [Production](deployment/production.md) - Production deployment
- [Kubernetes](deployment/kubernetes.md) - Kubernetes deployment
- [Monitoring](deployment/monitoring.md) - Monitoring and observability

##  Key Features

###  Agent-Driven Architecture
- **5 Specialized AI Agents** working in orchestrated harmony
- **ClassifierAgent**: Zero-shot LLM + ML fallback for case classification
- **RiskScorerAgent**: XGBoost + SHAP explanations for risk assessment
- **RouterAgent**: OPA policy-based intelligent routing
- **DecisionSupportAgent**: RAG-powered decision support and next actions
- **ComplianceAgent**: PII detection, audit logging, and compliance monitoring

###  Production-Ready Infrastructure
- **FastAPI** backend with comprehensive API design
- **PostgreSQL** + **Redis** for data persistence and caching
- **Open Policy Agent (OPA)** for policy-as-code
- **ChromaDB** vector store for RAG capabilities
- **Prometheus** + **Grafana** for observability
- **Docker Compose** for easy deployment

###  Modern Frontend
- **React + TypeScript** with Material-UI
- **Real-time dashboards** with Recharts
- **Dark theme** with keyboard shortcuts
- **Responsive design** for all devices

###  Enterprise Security & Compliance
- **JWT authentication** with role-based access control
- **PII detection and redaction** on all inputs/outputs
- **Comprehensive audit trails** with integrity hashing
- **Data retention policies** and compliance monitoring

##  Development

### Running Tests
```bash
make test              # All tests
make test-unit         # Unit tests only
make test-api          # API tests only
make test-integration  # Integration tests
```

### Code Quality
```bash
make lint              # Run all linters
make format            # Format code
make type-check        # Type checking
```

### ML Pipeline
```bash
make train             # Train models
make eval              # Evaluate models
make ml-pipeline       # Complete pipeline
```

### Monitoring
```bash
make health            # System health
make metrics           # Current metrics
make grafana           # Open Grafana
```

##  Contributing

We welcome contributions! Please see our [Contributing Guide](contributing/workflow.md) for details.

### Development Setup
```bash
make quickstart    # Complete development setup
make dev           # Start development servers
```

##  Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Claims-Triage-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Claims-Triage-AI/discussions)
- **Email**: support@claimstriage.ai

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with  for intelligent case processing**
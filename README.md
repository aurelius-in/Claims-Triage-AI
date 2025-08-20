# Claims Triage AI 🚀

> **Next-Generation Agent-Driven Case Triage Platform**

Transform your case processing with AI-powered agents that work across insurance, healthcare, finance, and legal domains. This platform combines cutting-edge machine learning, policy-based routing, and comprehensive compliance to deliver intelligent, scalable case triage.

![Claims Triage AI Demo](docs/images/claims_demo.gif)

## 🎯 What Makes This Special

### 🤖 **Agent-Driven Architecture**
- **5 Specialized AI Agents** working in orchestrated harmony
- **ClassifierAgent**: Zero-shot LLM + ML fallback for case classification
- **RiskScorerAgent**: XGBoost + SHAP explanations for risk assessment
- **RouterAgent**: OPA policy-based intelligent routing
- **DecisionSupportAgent**: RAG-powered decision support and next actions
- **ComplianceAgent**: PII detection, audit logging, and compliance monitoring

### 🏗️ **Production-Ready Infrastructure**
- **FastAPI** backend with comprehensive API design
- **PostgreSQL** + **Redis** for data persistence and caching
- **Open Policy Agent (OPA)** for policy-as-code
- **ChromaDB** vector store for RAG capabilities
- **Prometheus** + **Grafana** for observability
- **Docker Compose** for easy deployment

### 🎨 **Modern Frontend**
- **React + TypeScript** with Material-UI
- **Real-time dashboards** with Recharts
- **Dark theme** with keyboard shortcuts
- **Responsive design** for all devices

### 🔒 **Enterprise Security & Compliance**
- **JWT authentication** with role-based access control
- **PII detection and redaction** on all inputs/outputs
- **Comprehensive audit trails** with integrity hashing
- **Data retention policies** and compliance monitoring

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/Claims-Triage-AI.git
cd Claims-Triage-AI
make setup
```

### 2. Start Services
```bash
make up
```

### 3. Access the Platform
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## 🏛️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (React/TS)    │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent         │    │   Redis         │    │   ChromaDB      │
│   Orchestrator  │◄──►│   Cache/Queue   │◄──►│   Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OPA           │    │   Prometheus    │    │   Grafana       │
│   Policies      │    │   Metrics       │    │   Dashboards    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🤖 Agent Pipeline

### 1. **ClassifierAgent**
```python
# Zero-shot classification with LLM fallback
result = await classifier.classify({
    "title": "Medical claim for emergency surgery",
    "description": "Patient requires immediate cardiac procedure",
    "amount": 50000
})
# Output: {"case_type": "healthcare_prior_auth", "urgency": "critical"}
```

### 2. **RiskScorerAgent**
```python
# ML-based risk scoring with SHAP explanations
risk_result = await risk_scorer.score_risk(case_data, classification_result)
# Output: {"risk_score": 0.85, "risk_level": "high", "top_features": [...]}
```

### 3. **RouterAgent**
```python
# Policy-based routing using OPA
route_result = await router.route_case(case_data, classification_result, risk_result)
# Output: {"team": "Specialist", "sla_hours": 4, "escalation": true}
```

### 4. **DecisionSupportAgent**
```python
# RAG-powered decision support
support_result = await decision_support.provide_support(
    case_data, classification_result, risk_result, route_result
)
# Output: {"actions": [...], "template_response": "...", "checklist": [...]}
```

### 5. **ComplianceAgent**
```python
# PII detection and audit logging
compliance_result = await compliance.process_compliance(case_data, agent_results)
# Output: {"pii_detected": true, "audit_log": {...}, "compliance_issues": [...]}
```

## 📊 Key Features

### 🎯 **Multi-Domain Support**
- **Insurance Claims**: Auto, health, property, liability
- **Healthcare**: Prior authorizations, medical necessity reviews
- **Banking**: Dispute resolution, fraud detection
- **Legal**: Case intake, document review, compliance

### 📈 **Analytics & Monitoring**
- **Real-time dashboards** with KPIs and trends
- **SLA monitoring** with breach alerts
- **Risk distribution** analysis
- **Team performance** metrics
- **Agent confidence** tracking

### 🔧 **Developer Experience**
- **Comprehensive API** with OpenAPI documentation
- **Type-safe** TypeScript frontend
- **Automated testing** with pytest
- **CI/CD ready** with GitHub Actions
- **Development tools** with hot reloading

### 🚀 **Scalability**
- **Horizontal scaling** with container orchestration
- **Load balancing** with nginx
- **Background processing** with Celery
- **Caching** with Redis
- **Database optimization** with connection pooling

## 🛠️ Development

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

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed system design
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Agent Guide](docs/AGENTS.md)** - Agent development guide
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Security Guide](docs/SECURITY.md)** - Security and compliance

## 🎬 Demo & Examples

### Sample Case Processing
```bash
# Create a new case
curl -X POST "http://localhost:8000/api/v1/cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Emergency Medical Claim",
    "description": "Patient requires immediate cardiac surgery",
    "case_type": "healthcare_prior_auth",
    "amount": 75000,
    "priority": "critical"
  }'

# Run triage
curl -X POST "http://localhost:8000/api/v1/triage/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_id": "case-uuid", "force_reprocess": false}'
```

### Expected Output
```json
{
  "case_id": "case-uuid",
  "triage_id": "triage-uuid",
  "case_type": "healthcare_prior_auth",
  "urgency": "critical",
  "risk_level": "high",
  "risk_score": 0.87,
  "recommended_team": "Specialist",
  "sla_target_hours": 2,
  "escalation_flag": true,
  "suggested_actions": [
    "Immediate medical director review",
    "Schedule peer review",
    "Notify provider of urgent decision"
  ],
  "agent_results": [...],
  "processing_time_ms": 1250
}
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
make quickstart    # Complete development setup
make dev           # Start development servers
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **Hugging Face** for transformers
- **FastAPI** for the excellent web framework
- **Material-UI** for the beautiful components
- **Open Policy Agent** for policy management

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Claims-Triage-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Claims-Triage-AI/discussions)
- **Email**: support@claimstriage.ai

---

**Built with ❤️ for intelligent case processing**


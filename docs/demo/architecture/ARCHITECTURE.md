# Claims Triage AI - Architecture Guide

## System Overview

Claims Triage AI is a next-generation, agent-driven case triage platform designed to handle complex case processing across multiple domains including insurance, healthcare, finance, and legal sectors.

## High-Level Architecture

```

                        Frontend Layer                          

  React + TypeScript + Material-UI                              
   Real-time dashboards                                        
   Case management interface                                   
   Analytics and reporting                                     
   User management and settings                                

                                
                                

                        API Gateway Layer                       

  FastAPI + Nginx                                               
   RESTful API endpoints                                       
   Authentication & Authorization                              
   Rate limiting & security                                    
   Request/Response validation                                 

                                
                                

                      Agent Orchestration Layer                 

  Agent Orchestrator                                            
   Workflow coordination                                       
   Agent communication                                         
   Error handling & retry logic                                
   Performance monitoring                                      

                                
                                

                        Agent Layer                             

      
  Classifier    Risk Scorer   Router        Decision      
  Agent         Agent         Agent         Support       
                                            Agent         
      
   
                      Compliance Agent                          
   

                                
                                

                      Data Layer                                

  PostgreSQL  Redis  ChromaDB  OPA Policies  File Storage  
   Cases      Cache  Vectors  Rules        Documents   
   Users      Queue  RAG      Routing      Reports     
   Audit      Sessions  KB     Compliance  Exports     

                                
                                

                    Observability Layer                         

  Prometheus  Grafana  OpenTelemetry  Logging  Alerting     
   Metrics    Dashboards  Tracing     Structured  SLA    
   Collection  Visualization  Spans     Centralized  Health
   Storage    Reports     Correlation  Analysis   Events 

```

## Agent Architecture

### Agent Communication Flow

```
Case Input  Classifier  Risk Scorer  Router  Decision Support  Compliance  Output
                                                                
                                                                
  Validation  Classification Risk Assessment Routing Decision Compliance Audit
```

### Agent Responsibilities

#### 1. Classifier Agent
- **Purpose**: Determine case type and urgency
- **Technologies**: Zero-shot LLM + ML fallback
- **Input**: Case title, description, metadata
- **Output**: Case type, urgency level, confidence score

#### 2. Risk Scorer Agent
- **Purpose**: Assess case risk and complexity
- **Technologies**: XGBoost + SHAP explanations
- **Input**: Case data + classification results
- **Output**: Risk score, risk level, feature importance

#### 3. Router Agent
- **Purpose**: Determine optimal routing and SLA
- **Technologies**: OPA policy engine
- **Input**: Case data + classification + risk results
- **Output**: Target team, SLA hours, escalation flags

#### 4. Decision Support Agent
- **Purpose**: Provide actionable recommendations
- **Technologies**: RAG + ChromaDB
- **Input**: All previous agent results
- **Output**: Suggested actions, templates, checklists

#### 5. Compliance Agent
- **Purpose**: Ensure compliance and audit requirements
- **Technologies**: PII detection + audit logging
- **Input**: All case data and agent results
- **Output**: Compliance status, audit trail, PII flags

## Data Architecture

### Database Schema

#### Core Entities
- **Cases**: Main case records with metadata
- **Users**: System users and authentication
- **Teams**: Organizational units for routing
- **Audit Logs**: Complete audit trail
- **Triage Results**: Agent processing results

#### Relationships
```
Users (1)  (N) Cases
Teams (1)  (N) Cases
Cases (1)  (N) Triage Results
Cases (1)  (N) Audit Logs
```

### Caching Strategy

#### Redis Usage
- **Session Management**: User sessions and tokens
- **Agent Results**: Cached triage results
- **Rate Limiting**: API rate limiting
- **Queue Management**: Background job queues

### Vector Store

#### ChromaDB Collections
- **Knowledge Base**: Domain-specific knowledge
- **Case Templates**: Response templates
- **Policy Documents**: Regulatory requirements
- **Best Practices**: Historical case patterns

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Role-Based Access**: Granular permissions
- **API Keys**: Service-to-service communication
- **Session Management**: Secure session handling

### Data Protection
- **PII Detection**: Automatic sensitive data identification
- **Data Redaction**: Automatic data masking
- **Encryption**: Data at rest and in transit
- **Audit Logging**: Complete activity tracking

### Compliance
- **GDPR Compliance**: Data privacy requirements
- **HIPAA Compliance**: Healthcare data protection
- **SOC 2**: Security and availability controls
- **Data Retention**: Automated data lifecycle management

## Scalability Architecture

### Horizontal Scaling
- **Load Balancing**: Nginx reverse proxy
- **Container Orchestration**: Docker Compose/Kubernetes
- **Database Scaling**: Read replicas and connection pooling
- **Cache Distribution**: Redis cluster support

### Performance Optimization
- **Async Processing**: Non-blocking operations
- **Background Jobs**: Celery task queues
- **Connection Pooling**: Database optimization
- **CDN Integration**: Static asset delivery

## Monitoring & Observability

### Metrics Collection
- **Application Metrics**: Custom business metrics
- **Infrastructure Metrics**: System resource usage
- **Agent Performance**: Processing times and accuracy
- **Business KPIs**: SLA adherence and throughput

### Logging Strategy
- **Structured Logging**: JSON-formatted logs
- **Log Aggregation**: Centralized log collection
- **Log Levels**: Appropriate verbosity levels
- **Log Retention**: Automated log lifecycle

### Alerting
- **SLA Breaches**: Automated alerting
- **System Health**: Infrastructure monitoring
- **Security Events**: Security incident alerts
- **Performance Degradation**: Performance monitoring

## Deployment Architecture

### Environment Strategy
- **Development**: Local development environment
- **Staging**: Pre-production testing
- **Production**: Live production environment
- **DR/Backup**: Disaster recovery setup

### Infrastructure
- **Containerization**: Docker-based deployment
- **Orchestration**: Docker Compose/Kubernetes
- **CI/CD**: Automated deployment pipeline
- **Monitoring**: Comprehensive observability stack
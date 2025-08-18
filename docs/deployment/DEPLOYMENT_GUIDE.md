# Claims Triage AI - Deployment Guide

## Overview

This guide covers deploying Claims Triage AI in various environments, from local development to production.

## Prerequisites

### System Requirements

- **CPU**: 4+ cores (8+ for production)
- **RAM**: 8GB+ (16GB+ for production)
- **Storage**: 50GB+ available space
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **Make**: For automation scripts

### Network Requirements

- **Ports**: 80, 443, 3000, 8000, 5432, 6379, 8181, 6333, 9090, 3001
- **SSL Certificate**: For production HTTPS
- **Domain**: For production deployment

## Local Development Deployment

### Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/Claims-Triage-AI.git
   cd Claims-Triage-AI
   ```

2. **Setup Environment**
   ```bash
   # Install dependencies
   make install
   
   # Setup database and seed data
   make setup
   
   # Start all services
   make up
   ```

3. **Verify Deployment**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001 (admin/admin)

### Development Configuration

#### Environment Variables

Create `.env` file in the root directory:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/triage_ai
POSTGRES_DB=triage_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
OPA_URL=http://localhost:8181
VECTOR_STORE_URL=http://localhost:6333

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Application
DEBUG=true
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["http://localhost:3000"]
```

#### Docker Compose Configuration

The `docker-compose.yml` file includes all necessary services:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/triage_ai
      - REDIS_URL=redis://redis:6379
      - DEBUG=true
    depends_on:
      - postgres
      - redis
      - opa
      - chroma

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=triage_ai
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  opa:
    image: openpolicyagent/opa:latest
    command: run --server --addr :8181 --cors
    ports:
      - "8181:8181"
    volumes:
      - ./policies:/policies

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "6333:6333"
    volumes:
      - chroma_data:/chroma/chroma

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  chroma_data:
  prometheus_data:
  grafana_data:
```

## Staging Deployment

### Staging Environment Setup

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   ```

2. **Application Deployment**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/Claims-Triage-AI.git
   cd Claims-Triage-AI
   
   # Create staging environment file
   cp .env.example .env.staging
   
   # Edit environment variables
   nano .env.staging
   
   # Start staging services
   docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
   ```

3. **SSL Configuration**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Obtain SSL certificate
   sudo certbot --nginx -d staging.claimstriage.ai
   
   # Configure auto-renewal
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Staging Configuration

#### Environment Variables (Staging)

```bash
# Application
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=staging

# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/triage_ai_staging

# Security
SECRET_KEY=staging-secret-key
JWT_SECRET_KEY=staging-jwt-secret

# External Services
OPA_URL=http://opa:8181
VECTOR_STORE_URL=http://chroma:6333

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# URLs
FRONTEND_URL=https://staging.claimstriage.ai
API_URL=https://staging.claimstriage.ai/api
ALLOWED_ORIGINS=["https://staging.claimstriage.ai"]
```

#### Nginx Configuration (Staging)

```nginx
# /etc/nginx/sites-available/staging.claimstriage.ai
server {
    listen 80;
    server_name staging.claimstriage.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name staging.claimstriage.ai;

    ssl_certificate /etc/letsencrypt/live/staging.claimstriage.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.claimstriage.ai/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Monitoring
    location /grafana/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Production Deployment

### Production Environment Setup

1. **Server Requirements**
   - **CPU**: 8+ cores
   - **RAM**: 32GB+
   - **Storage**: 500GB+ SSD
   - **Network**: High bandwidth, low latency
   - **Backup**: Automated backup solution

2. **Security Hardening**
   ```bash
   # Configure firewall
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   
   # Install fail2ban
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   
   # Configure automatic security updates
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Application Deployment**
   ```bash
   # Create production directory
   sudo mkdir -p /opt/claimstriage
   sudo chown $USER:$USER /opt/claimstriage
   cd /opt/claimstriage
   
   # Clone repository
   git clone https://github.com/yourusername/Claims-Triage-AI.git .
   
   # Create production environment
   cp .env.example .env.production
   nano .env.production
   
   # Build and start production services
   docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
   ```

### Production Configuration

#### Environment Variables (Production)

```bash
# Application
DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://postgres:strong-password@postgres:5432/triage_ai_prod

# Security
SECRET_KEY=very-long-random-secret-key
JWT_SECRET_KEY=very-long-random-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# External Services
OPA_URL=http://opa:8181
VECTOR_STORE_URL=http://chroma:6333

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# URLs
FRONTEND_URL=https://claimstriage.ai
API_URL=https://claimstriage.ai/api
ALLOWED_ORIGINS=["https://claimstriage.ai"]

# Performance
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
CONNECTION_TIMEOUT=30

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30
```

#### Production Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - WORKER_PROCESSES=4
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=triage_ai_prod
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=strong-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '2'
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  backup:
    image: postgres:15-alpine
    restart: "no"
    environment:
      - POSTGRES_DB=triage_ai_prod
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=strong-password
    volumes:
      - ./backups:/backups
      - postgres_data:/var/lib/postgresql/data
    command: |
      sh -c '
        pg_dump -h postgres -U postgres triage_ai_prod > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql
        find /backups -name "backup_*.sql" -mtime +30 -delete
      '

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

#### Production Nginx Configuration

```nginx
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream servers
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    upstream frontend {
        server frontend:3000;
        keepalive 32;
    }

    # Main server
    server {
        listen 80;
        server_name claimstriage.ai www.claimstriage.ai;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name claimstriage.ai www.claimstriage.ai;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## Kubernetes Deployment

### Kubernetes Cluster Setup

1. **Create Cluster**
   ```bash
   # Using kind for local development
   kind create cluster --name claimstriage
   
   # Using minikube
   minikube start --cpus 4 --memory 8192
   
   # Using cloud provider (AWS EKS example)
   eksctl create cluster --name claimstriage --region us-west-2 --nodegroup-name workers --node-type t3.large --nodes 3
   ```

2. **Install Helm**
   ```bash
   curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
   sudo mv linux-amd64/helm /usr/local/bin/helm
   ```

3. **Deploy with Helm**
   ```bash
   # Create namespace
   kubectl create namespace claimstriage
   
   # Install dependencies
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm install postgres bitnami/postgresql -n claimstriage
   helm install redis bitnami/redis -n claimstriage
   
   # Deploy application
   helm install claimstriage ./helm-chart -n claimstriage
   ```

### Helm Chart Structure

```
helm-chart/
 Chart.yaml
 values.yaml
 templates/
    deployment.yaml
    service.yaml
    ingress.yaml
    configmap.yaml
    secret.yaml
    hpa.yaml
 charts/
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'claimstriage-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'claimstriage-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboards

1. **Application Dashboard**
   - Request rate and response times
   - Error rates and status codes
   - Database connection pool usage
   - Redis cache hit rates

2. **Infrastructure Dashboard**
   - CPU and memory usage
   - Disk I/O and network traffic
   - Container resource usage
   - System load and uptime

3. **Business Dashboard**
   - Case processing volume
   - SLA compliance rates
   - Agent performance metrics
   - User activity and engagement

### Alerting Rules

```yaml
# monitoring/prometheus/rules/alerts.yml
groups:
  - name: claimstriage
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionHigh
        expr: pg_stat_database_numbackends > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database has {{ $value }} active connections"
```

## Backup and Recovery

### Automated Backups

1. **Database Backup Script**
   ```bash
   #!/bin/bash
   # backup.sh
   
   BACKUP_DIR="/opt/claimstriage/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   DB_NAME="triage_ai_prod"
   
   # Create backup
   docker-compose exec -T postgres pg_dump -U postgres $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
   
   # Compress backup
   gzip $BACKUP_DIR/backup_$DATE.sql
   
   # Remove old backups (keep 30 days)
   find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
   
   # Upload to cloud storage (optional)
   aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://claimstriage-backups/
   ```

2. **Cron Job Setup**
   ```bash
   # Add to crontab
   crontab -e
   
   # Daily backup at 2 AM
   0 2 * * * /opt/claimstriage/backup.sh
   ```

### Recovery Procedures

1. **Database Recovery**
   ```bash
   # Stop application
   docker-compose down
   
   # Restore database
   gunzip -c backup_20240101_020000.sql.gz | docker-compose exec -T postgres psql -U postgres triage_ai_prod
   
   # Start application
   docker-compose up -d
   ```

2. **Full System Recovery**
   ```bash
   # Clone fresh repository
   git clone https://github.com/yourusername/Claims-Triage-AI.git /opt/claimstriage-new
   cd /opt/claimstriage-new
   
   # Restore configuration
   cp /opt/claimstriage/.env.production .env.production
   
   # Restore data
   cp -r /opt/claimstriage/backups ./backups
   gunzip -c backups/backup_latest.sql.gz | docker-compose exec -T postgres psql -U postgres triage_ai_prod
   
   # Switch to new deployment
   cd /opt
   mv claimstriage claimstriage-old
   mv claimstriage-new claimstriage
   cd claimstriage
   
   # Start services
   docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
   ```

## Security Considerations

### SSL/TLS Configuration

1. **Certificate Management**
   ```bash
   # Obtain certificate
   sudo certbot --nginx -d claimstriage.ai
   
   # Auto-renewal
   sudo crontab -e
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

2. **Security Headers**
   ```nginx
   # Add to nginx configuration
   add_header X-Frame-Options DENY;
   add_header X-Content-Type-Options nosniff;
   add_header X-XSS-Protection "1; mode=block";
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
   ```

### Access Control

1. **Firewall Configuration**
   ```bash
   # Configure UFW
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **SSH Hardening**
   ```bash
   # Edit SSH configuration
   sudo nano /etc/ssh/sshd_config
   
   # Add/modify these lines:
   Port 2222
   PermitRootLogin no
   PasswordAuthentication no
   PubkeyAuthentication yes
   MaxAuthTries 3
   ```

## Performance Optimization

### Database Optimization

1. **PostgreSQL Tuning**
   ```sql
   -- Increase shared buffers
   ALTER SYSTEM SET shared_buffers = '2GB';
   
   -- Optimize work memory
   ALTER SYSTEM SET work_mem = '64MB';
   
   -- Enable connection pooling
   ALTER SYSTEM SET max_connections = 200;
   
   -- Reload configuration
   SELECT pg_reload_conf();
   ```

2. **Index Optimization**
   ```sql
   -- Create indexes for common queries
   CREATE INDEX idx_cases_status ON cases(status);
   CREATE INDEX idx_cases_created_at ON cases(created_at);
   CREATE INDEX idx_cases_type_urgency ON cases(case_type, urgency_level);
   ```

### Application Optimization

1. **Connection Pooling**
   ```python
   # Database connection pooling
   DATABASE_URL = "postgresql://user:pass@host:port/db?pool_size=20&max_overflow=30"
   ```

2. **Caching Strategy**
   ```python
   # Redis caching
   CACHE_TTL = 3600  # 1 hour
   CACHE_PREFIX = "claimstriage:"
   ```

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose logs backend
   docker-compose logs frontend
   
   # Check resource usage
   docker stats
   
   # Restart services
   docker-compose restart
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U postgres
   
   # Check connection pool
   docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   docker system df
   
   # Clean up Docker
   docker system prune -a
   ```

### Performance Monitoring

1. **Resource Monitoring**
   ```bash
   # System resources
   htop
   iotop
   nethogs
   
   # Docker resources
   docker stats
   ```

2. **Application Monitoring**
   ```bash
   # Check application metrics
   curl http://localhost:8000/metrics
   
   # Check health endpoints
   curl http://localhost:8000/health
   curl http://localhost:3000/health
   ```

## Maintenance

### Regular Maintenance Tasks

1. **Daily Tasks**
   - Monitor system health
   - Check backup completion
   - Review error logs
   - Monitor performance metrics

2. **Weekly Tasks**
   - Update system packages
   - Review security logs
   - Analyze performance trends
   - Clean up old logs

3. **Monthly Tasks**
   - Update application dependencies
   - Review and rotate secrets
   - Analyze resource usage trends
   - Plan capacity upgrades

### Update Procedures

1. **Application Updates**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Build new images
   docker-compose build --no-cache
   
   # Deploy with zero downtime
   docker-compose up -d --no-deps backend
   docker-compose up -d --no-deps frontend
   ```

2. **System Updates**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Update Docker
   sudo apt install docker-ce docker-ce-cli containerd.io
   
   # Restart services
   sudo systemctl restart docker
   docker-compose up -d
   ```

## Support and Resources

### Documentation
- [Architecture Guide](docs/architecture/ARCHITECTURE.md)
- [API Documentation](docs/api/API.md)
- [Developer Guide](docs/developer/DEVELOPER_GUIDE.md)
- [User Guide](docs/user-guides/USER_GUIDE.md)

### Community Support
- [GitHub Issues](https://github.com/yourusername/Claims-Triage-AI/issues)
- [GitHub Discussions](https://github.com/yourusername/Claims-Triage-AI/discussions)
- [Discord Server](https://discord.gg/claimstriage)
- [Email Support](mailto:deployment-support@claimstriage.ai)

### External Resources
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
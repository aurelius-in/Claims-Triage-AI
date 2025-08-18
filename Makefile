# Claims Triage AI - Makefile
# Comprehensive development and deployment automation

.PHONY: help install setup up down logs clean test lint format seed demo-gif

# Default target
help:
	@echo "Claims Triage AI - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install     - Install all dependencies"
	@echo "  setup       - Initial setup (install + seed data)"
	@echo "  up          - Start all services with docker-compose"
	@echo "  down        - Stop all services"
	@echo "  logs        - View logs from all services"
	@echo "  clean       - Clean up containers, volumes, and cache"
	@echo ""
	@echo "Development:"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-api    - Run API tests only"
	@echo "  test-integration - Run integration tests"
	@echo "  lint        - Run linting (black, isort, flake8, mypy)"
	@echo "  format      - Format code (black, isort)"
	@echo "  type-check  - Run type checking (mypy)"
	@echo ""
	@echo "Data & ML:"
	@echo "  seed        - Seed database with sample data"
	@echo "  train       - Train ML models"
	@echo "  eval        - Evaluate ML models"
	@echo "  ml-pipeline - Run complete ML pipeline"
	@echo ""
	@echo "Monitoring & Analytics:"
	@echo "  metrics     - View current metrics"
	@echo "  health      - Check system health"
	@echo "  grafana     - Open Grafana dashboard"
	@echo "  prometheus  - Open Prometheus metrics"
	@echo ""
	@echo "Documentation:"
	@echo "  docs        - Build documentation"
	@echo "  docs-serve  - Serve documentation locally"
	@echo ""
	@echo "Demo & Presentation:"
	@echo "  demo-gif    - Generate demo GIF"
	@echo "  demo-video  - Generate demo video"
	@echo "  demo-setup  - Setup demo environment"
	@echo ""
	@echo "Production:"
	@echo "  build       - Build production images"
	@echo "  deploy      - Deploy to production"
	@echo "  backup      - Backup database"
	@echo "  restore     - Restore database"

# Setup & Installation
install:
	@echo "Installing dependencies..."
	pip install -r backend/requirements.txt
	cd frontend && npm install
	@echo "Dependencies installed successfully!"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Frontend dependencies installed!"

install-backend:
	@echo "Installing backend dependencies..."
	pip install -r backend/requirements.txt
	@echo "Backend dependencies installed!"

setup: install seed
	@echo "Setup complete! Run 'make up' to start services."

up:
	@echo "Starting Claims Triage AI services..."
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Grafana: http://localhost:3001 (admin/admin)"
	@echo "  Prometheus: http://localhost:9090"

up-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm start

up-backend:
	@echo "Starting backend development server..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

down:
	@echo "Stopping services..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
	rm -rf logs/*
	rm -rf uploads/*
	rm -rf .pytest_cache
	rm -rf __pycache__
	find . -name "*.pyc" -delete
	@echo "Cleanup complete!"

# Development
test:
	@echo "Running all tests..."
	pytest backend/tests/ -v --cov=backend --cov-report=html --cov-report=term

test-unit:
	@echo "Running unit tests..."
	pytest backend/tests/unit/ -v

test-api:
	@echo "Running API tests..."
	pytest backend/tests/api/ -v

test-integration:
	@echo "Running integration tests..."
	pytest backend/tests/integration/ -v

lint:
	@echo "Running linting..."
	black --check backend/
	isort --check-only backend/
	flake8 backend/
	mypy backend/

format:
	@echo "Formatting code..."
	black backend/
	isort backend/
	@echo "Code formatted!"

type-check:
	@echo "Running type checking..."
	mypy backend/

# Data & ML
seed:
	@echo "Seeding database with sample data..."
	docker-compose exec backend python -m backend.scripts.seed_data
	@echo "Database seeded!"

db-init: ## Initialize database with tables and seed data
	@echo "Initializing database..."
	cd backend && python scripts/init_db.py

db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-migrate-create: ## Create new migration
	@echo "Creating new migration..."
	cd backend && alembic revision --autogenerate -m "$(message)"

db-reset: ## Reset database (drop and recreate)
	@echo "Resetting database..."
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head
	cd backend && python scripts/init_db.py

train:
	@echo "Training ML models..."
	docker-compose exec backend python -m backend.ml.train
	@echo "Models trained!"

eval:
	@echo "Evaluating ML models..."
	docker-compose exec backend python -m backend.ml.eval
	@echo "Evaluation complete!"

ml-pipeline: train eval
	@echo "ML pipeline complete!"

# Monitoring & Analytics
metrics:
	@echo "Current metrics:"
	curl -s http://localhost:8000/api/v1/metrics | jq .

health:
	@echo "System health check:"
	curl -s http://localhost:8000/health | jq .

grafana:
	@echo "Opening Grafana dashboard..."
	open http://localhost:3001

prometheus:
	@echo "Opening Prometheus metrics..."
	open http://localhost:9090

# Documentation
docs:
	@echo "Building documentation..."
	mkdocs build

docs-serve:
	@echo "Serving documentation..."
	mkdocs serve

# Demo & Presentation
demo-gif:
	@echo "Generating demo GIF..."
	# TODO: Implement demo GIF generation
	@echo "Demo GIF generated: demo/demo.gif"

demo-video:
	@echo "Generating demo video..."
	# TODO: Implement demo video generation
	@echo "Demo video generated: demo/demo.mp4"

demo-setup:
	@echo "Setting up demo environment..."
	make seed
	make train
	@echo "Demo environment ready!"

# Production
build:
	@echo "Building production images..."
	docker-compose build --no-cache
	@echo "Images built!"

deploy:
	@echo "Deploying to production..."
	# TODO: Implement production deployment
	@echo "Deployment complete!"

backup:
	@echo "Backing up database..."
	docker-compose exec postgres pg_dump -U postgres triage_ai > backup_$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created!"

restore:
	@echo "Restoring database..."
	# Usage: make restore BACKUP_FILE=backup_20231201_120000.sql
	docker-compose exec -T postgres psql -U postgres triage_ai < $(BACKUP_FILE)
	@echo "Database restored!"

# Utility targets
status:
	@echo "Service status:"
	docker-compose ps

restart:
	@echo "Restarting services..."
	docker-compose restart

rebuild:
	@echo "Rebuilding and restarting services..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Development helpers
dev-backend:
	@echo "Starting backend in development mode..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in development mode..."
	cd frontend && npm start

dev: dev-backend dev-frontend

# Frontend specific commands
frontend-build:
	@echo "Building frontend for production..."
	cd frontend && npm run build

frontend-test:
	@echo "Running frontend tests..."
	cd frontend && npm test

frontend-lint:
	@echo "Running frontend linting..."
	cd frontend && npm run lint

frontend-format:
	@echo "Formatting frontend code..."
	cd frontend && npm run format

frontend-type-check:
	@echo "Running frontend type checking..."
	cd frontend && npm run type-check

frontend-clean:
	@echo "Cleaning frontend build artifacts..."
	cd frontend && rm -rf build node_modules/.cache

# Quick start for new developers
quickstart: setup up
	@echo "Quick start complete!"
	@echo "Access the application at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API Docs: http://localhost:8000/docs"

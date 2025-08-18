# Claims Triage AI - Developer Guide

## Development Setup

### Prerequisites

- **Python 3.11+**: Core backend development
- **Node.js 18+**: Frontend development
- **Docker & Docker Compose**: Containerized development
- **Git**: Version control
- **PostgreSQL 15+**: Database (optional, Docker provides this)
- **Redis 7+**: Caching and queues (optional, Docker provides this)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Claims-Triage-AI.git
   cd Claims-Triage-AI
   ```

2. **Setup Development Environment**
   ```bash
   # Install dependencies
   make install
   
   # Setup database and seed data
   make setup
   
   # Start all services
   make up
   ```

3. **Verify Installation**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001 (admin/admin)

### Development Workflow

#### Backend Development

1. **Start Backend Services**
   ```bash
   # Start only backend services
   docker-compose up postgres redis opa chroma -d
   
   # Start backend in development mode
   make dev-backend
   ```

2. **Run Tests**
   ```bash
   # All tests
   make test
   
   # Unit tests only
   make test-unit
   
   # API tests only
   make test-api
   
   # Integration tests
   make test-integration
   ```

3. **Code Quality**
   ```bash
   # Format code
   make format
   
   # Lint code
   make lint
   
   # Type checking
   make type-check
   ```

#### Frontend Development

1. **Start Frontend**
   ```bash
   # Start frontend development server
   make dev-frontend
   ```

2. **Run Tests**
   ```bash
   # Frontend tests
   make frontend-test
   
   # Lint frontend
   make frontend-lint
   ```

## Project Structure

### Backend Structure

```
backend/
 agents/                 # AI Agent implementations
    classifier.py      # Case classification agent
    risk_scorer.py     # Risk assessment agent
    router.py          # Routing agent
    decision_support.py # Decision support agent
    compliance.py      # Compliance agent
    orchestrator.py    # Agent orchestration
 core/                  # Core functionality
    config.py         # Configuration management
    security.py       # Security and authentication
    telemetry.py      # Observability setup
    redis.py          # Redis client
    vector_store.py   # Vector store client
    opa.py            # OPA client
 ml/                   # Machine learning components
    models/           # ML model definitions
    training/         # Training scripts
    evaluation/       # Evaluation scripts
    features/         # Feature engineering
 rag/                  # RAG components
    knowledge_base.py # Knowledge base management
    embeddings.py     # Embedding generation
    retrieval.py      # Document retrieval
 tests/                # Test suite
    unit/            # Unit tests
    integration/     # Integration tests
    api/             # API tests
    performance/     # Performance tests
 scripts/              # Utility scripts
    seed_data.py     # Data seeding
    init_db.py       # Database initialization
 main.py              # FastAPI application entry point
 requirements.txt     # Python dependencies
 Dockerfile          # Backend container definition
```

### Frontend Structure

```
frontend/
 src/
    components/       # React components
       Charts/      # Chart components
       Common/      # Common UI components
       Layout/      # Layout components
    pages/           # Page components
       Analytics/   # Analytics pages
       Auth/        # Authentication pages
       TriageQueue/ # Case management pages
       Settings/    # Settings pages
    store/           # Redux store
       slices/      # Redux slices
       hooks.ts     # Redux hooks
    services/        # API services
    types/           # TypeScript type definitions
    utils/           # Utility functions
 public/              # Static assets
 package.json         # Node.js dependencies
 Dockerfile          # Frontend container definition
```

## Agent Development

### Agent Architecture

Each agent follows a consistent pattern:

```python
class AgentName:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.model = self._load_model()
    
    async def process(self, input_data: Dict) -> AgentResult:
        """Main processing method"""
        try:
            # 1. Validate input
            validated_data = self._validate_input(input_data)
            
            # 2. Process with model
            result = await self._process_with_model(validated_data)
            
            # 3. Post-process results
            processed_result = self._post_process(result)
            
            # 4. Return structured result
            return AgentResult(
                success=True,
                data=processed_result,
                metadata=self._get_metadata()
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata=self._get_metadata()
            )
    
    def _validate_input(self, data: Dict) -> Dict:
        """Validate input data"""
        pass
    
    async def _process_with_model(self, data: Dict) -> Dict:
        """Process with underlying model"""
        pass
    
    def _post_process(self, result: Dict) -> Dict:
        """Post-process model results"""
        pass
```

### Creating a New Agent

1. **Create Agent File**
   ```python
   # backend/agents/new_agent.py
   from typing import Dict, Optional
   from pydantic import BaseModel
   
   class NewAgentConfig(BaseModel):
       model_path: str
       threshold: float = 0.5
   
   class NewAgentResult(BaseModel):
       result: str
       confidence: float
       metadata: Dict
   
   class NewAgent:
       def __init__(self, config: NewAgentConfig):
           self.config = config
           self.model = self._load_model()
       
       async def process(self, input_data: Dict) -> NewAgentResult:
           # Implementation here
           pass
   ```

2. **Add to Orchestrator**
   ```python
   # backend/agents/orchestrator.py
   from .new_agent import NewAgent, NewAgentConfig
   
   class AgentOrchestrator:
       def __init__(self):
           self.new_agent = NewAgent(NewAgentConfig(...))
       
       async def run_pipeline(self, case_data: Dict):
           # Add new agent to pipeline
           new_result = await self.new_agent.process(case_data)
           # Continue pipeline
   ```

3. **Add Tests**
   ```python
   # backend/tests/test_new_agent.py
   import pytest
   from backend.agents.new_agent import NewAgent, NewAgentConfig
   
   class TestNewAgent:
       @pytest.fixture
       def agent(self):
           config = NewAgentConfig(model_path="test_model")
           return NewAgent(config)
       
       async def test_process(self, agent):
           result = await agent.process({"test": "data"})
           assert result.success
           assert result.data is not None
   ```

## API Development

### Adding New Endpoints

1. **Create Route Module**
   ```python
   # backend/api/routes/new_feature.py
   from fastapi import APIRouter, Depends, HTTPException
   from typing import List
   
   router = APIRouter(prefix="/api/v1/new-feature", tags=["new-feature"])
   
   @router.get("/")
   async def get_items(
       current_user: User = Depends(get_current_user)
   ) -> List[Item]:
       """Get all items"""
       return await get_items_service()
   
   @router.post("/")
   async def create_item(
       item: ItemCreate,
       current_user: User = Depends(get_current_user)
   ) -> Item:
       """Create new item"""
       return await create_item_service(item, current_user)
   ```

2. **Register in Main App**
   ```python
   # backend/main.py
   from api.routes import new_feature
   
   app.include_router(new_feature.router)
   ```

3. **Add Tests**
   ```python
   # backend/tests/api/test_new_feature.py
   import pytest
   from httpx import AsyncClient
   
   class TestNewFeatureAPI:
       async def test_get_items(self, client: AsyncClient, auth_headers):
           response = await client.get("/api/v1/new-feature/", headers=auth_headers)
           assert response.status_code == 200
           data = response.json()
           assert isinstance(data, list)
   ```

### Database Models

1. **Create Model**
   ```python
   # backend/models/new_model.py
   from sqlalchemy import Column, Integer, String, DateTime
   from sqlalchemy.sql import func
   from database import Base
   
   class NewModel(Base):
       __tablename__ = "new_models"
       
       id = Column(Integer, primary_key=True, index=True)
       name = Column(String, nullable=False)
       description = Column(String)
       created_at = Column(DateTime(timezone=True), server_default=func.now())
       updated_at = Column(DateTime(timezone=True), onupdate=func.now())
   ```

2. **Create Migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add new model"
   alembic upgrade head
   ```

3. **Add Repository**
   ```python
   # backend/repositories/new_model_repository.py
   from typing import List, Optional
   from sqlalchemy.orm import Session
   from models.new_model import NewModel
   
   class NewModelRepository:
       def __init__(self, db: Session):
           self.db = db
       
       def create(self, new_model: NewModel) -> NewModel:
           self.db.add(new_model)
           self.db.commit()
           self.db.refresh(new_model)
           return new_model
       
       def get_by_id(self, id: int) -> Optional[NewModel]:
           return self.db.query(NewModel).filter(NewModel.id == id).first()
   ```

## Frontend Development

### Component Development

1. **Create Component**
   ```typescript
   // frontend/src/components/NewComponent/NewComponent.tsx
   import React from 'react';
   import { Box, Typography } from '@mui/material';
   
   interface NewComponentProps {
     title: string;
     data: any[];
   }
   
   export const NewComponent: React.FC<NewComponentProps> = ({ title, data }) => {
     return (
       <Box>
         <Typography variant="h6">{title}</Typography>
         {/* Component content */}
       </Box>
     );
   };
   ```

2. **Add to Page**
   ```typescript
   // frontend/src/pages/NewPage/NewPage.tsx
   import React from 'react';
   import { NewComponent } from '../../components/NewComponent/NewComponent';
   
   export const NewPage: React.FC = () => {
     return (
       <div>
         <NewComponent title="New Feature" data={[]} />
       </div>
     );
   };
   ```

3. **Add Route**
   ```typescript
   // frontend/src/App.tsx
   import { NewPage } from './pages/NewPage/NewPage';
   
   // In your router configuration
   <Route path="/new-feature" element={<NewPage />} />
   ```

### State Management

1. **Create Slice**
   ```typescript
   // frontend/src/store/slices/newFeatureSlice.ts
   import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
   
   interface NewFeatureState {
     items: any[];
     loading: boolean;
     error: string | null;
   }
   
   const initialState: NewFeatureState = {
     items: [],
     loading: false,
     error: null,
   };
   
   export const fetchItems = createAsyncThunk(
     'newFeature/fetchItems',
     async () => {
       const response = await api.get('/api/v1/new-feature/');
       return response.data;
     }
   );
   
   const newFeatureSlice = createSlice({
     name: 'newFeature',
     initialState,
     reducers: {},
     extraReducers: (builder) => {
       builder
         .addCase(fetchItems.pending, (state) => {
           state.loading = true;
         })
         .addCase(fetchItems.fulfilled, (state, action) => {
           state.loading = false;
           state.items = action.payload;
         })
         .addCase(fetchItems.rejected, (state, action) => {
           state.loading = false;
           state.error = action.error.message || 'Failed to fetch items';
         });
     },
   });
   
   export default newFeatureSlice.reducer;
   ```

2. **Add to Store**
   ```typescript
   // frontend/src/store/index.ts
   import newFeatureReducer from './slices/newFeatureSlice';
   
   export const store = configureStore({
     reducer: {
       // ... other reducers
       newFeature: newFeatureReducer,
     },
   });
   ```

## Testing

### Backend Testing

1. **Unit Tests**
   ```python
   # backend/tests/unit/test_new_feature.py
   import pytest
   from unittest.mock import Mock, patch
   
   class TestNewFeature:
       def test_some_function(self):
           # Arrange
           input_data = {"test": "data"}
           
           # Act
           result = some_function(input_data)
           
           # Assert
           assert result is not None
           assert result["status"] == "success"
   ```

2. **Integration Tests**
   ```python
   # backend/tests/integration/test_new_feature_integration.py
   import pytest
   from httpx import AsyncClient
   
   class TestNewFeatureIntegration:
       async def test_end_to_end_flow(self, client: AsyncClient):
           # Test complete workflow
           response = await client.post("/api/v1/new-feature/", json={...})
           assert response.status_code == 201
           
           # Verify result
           result = response.json()
           assert result["id"] is not None
   ```

3. **Performance Tests**
   ```python
   # backend/tests/performance/test_new_feature_performance.py
   import pytest
   import time
   
   class TestNewFeaturePerformance:
       async def test_response_time(self, client: AsyncClient):
           start_time = time.time()
           response = await client.get("/api/v1/new-feature/")
           end_time = time.time()
           
           assert response.status_code == 200
           assert (end_time - start_time) < 1.0  # Should respond within 1 second
   ```

### Frontend Testing

1. **Component Tests**
   ```typescript
   // frontend/src/components/NewComponent/__tests__/NewComponent.test.tsx
   import React from 'react';
   import { render, screen } from '@testing-library/react';
   import { NewComponent } from '../NewComponent';
   
   describe('NewComponent', () => {
     test('renders title correctly', () => {
       render(<NewComponent title="Test Title" data={[]} />);
       expect(screen.getByText('Test Title')).toBeInTheDocument();
     });
   });
   ```

2. **Integration Tests**
   ```typescript
   // frontend/src/pages/NewPage/__tests__/NewPage.test.tsx
   import React from 'react';
   import { render, screen, fireEvent } from '@testing-library/react';
   import { Provider } from 'react-redux';
   import { store } from '../../../store';
   import { NewPage } from '../NewPage';
   
   describe('NewPage', () => {
     test('loads and displays data', async () => {
       render(
         <Provider store={store}>
           <NewPage />
         </Provider>
       );
       
       // Wait for data to load
       await screen.findByText('Loaded Data');
     });
   });
   ```

## Deployment

### Local Development

1. **Development Mode**
   ```bash
   # Start all services in development mode
   make dev
   
   # Or start individually
   make dev-backend
   make dev-frontend
   ```

2. **Hot Reloading**
   - Backend: Uses uvicorn with `--reload` flag
   - Frontend: Uses React development server
   - Changes are automatically reflected

### Production Deployment

1. **Build Images**
   ```bash
   # Build production images
   make build
   
   # Or build individually
   docker-compose build backend
   docker-compose build frontend
   ```

2. **Deploy**
   ```bash
   # Deploy to production
   make deploy
   
   # Or use Docker Compose
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Contributing

### Code Standards

1. **Python Standards**
   - Follow PEP 8 style guide
   - Use type hints
   - Write docstrings for all functions
   - Maximum line length: 127 characters

2. **TypeScript Standards**
   - Use strict TypeScript configuration
   - Follow ESLint rules
   - Use Prettier for formatting
   - Write JSDoc comments

3. **Testing Standards**
   - Maintain >80% code coverage
   - Write unit tests for all functions
   - Write integration tests for APIs
   - Write E2E tests for critical flows

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**
   - Write code following standards
   - Add tests for new functionality
   - Update documentation

3. **Run Tests**
   ```bash
   make test
   make lint
   make type-check
   ```

4. **Submit PR**
   - Create pull request
   - Add description of changes
   - Link related issues
   - Request code review

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # Reset database
   make db-reset
   ```

2. **Redis Connection Issues**
   ```bash
   # Check Redis status
   docker-compose ps redis
   
   # Flush Redis cache
   make redis-flush
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear node modules
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Test Failures**
   ```bash
   # Run tests with verbose output
   pytest -v backend/tests/
   
   # Run specific test
   pytest backend/tests/test_specific.py::test_function -v
   ```

### Performance Optimization

1. **Database Optimization**
   - Use database indexes
   - Optimize queries
   - Use connection pooling
   - Monitor slow queries

2. **Caching Strategy**
   - Cache frequently accessed data
   - Use Redis for session storage
   - Implement cache invalidation
   - Monitor cache hit rates

3. **API Optimization**
   - Use pagination for large datasets
   - Implement request compression
   - Use async processing
   - Monitor response times

## Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Material-UI Documentation](https://mui.com/)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Insomnia](https://insomnia.rest/) - API client
- [DBeaver](https://dbeaver.io/) - Database client
- [Redis Commander](https://github.com/joeferner/redis-commander) - Redis client

### Community
- [GitHub Issues](https://github.com/yourusername/Claims-Triage-AI/issues)
- [GitHub Discussions](https://github.com/yourusername/Claims-Triage-AI/discussions)
- [Discord Server](https://discord.gg/claimstriage)
- [Email Support](mailto:dev-support@claimstriage.ai)
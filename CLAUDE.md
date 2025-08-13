# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

Dify is a full-stack LLM application development platform with a Python Flask API backend and Next.js React frontend. The architecture consists of:

- **API Backend** (`api/`): Flask-based REST API with SQLAlchemy ORM, Celery for background tasks
- **Web Frontend** (`web/`): Next.js 15 with TypeScript, TailwindCSS, and React 19
- **Core Engine** (`api/core/`): Business logic including workflow engine, RAG pipeline, agent framework, and model management
- **Docker Setup** (`docker/`): Production deployment with middleware services (Redis, PostgreSQL, etc.)

## Development Commands

### API (Python) Development
```bash
# Start API server for development
./dev/start-api

# Start background worker
./dev/start-worker

# Run all tests
pytest api/tests/unit_tests/

# Run specific test categories
./dev/pytest/pytest_unit_tests.sh
./dev/pytest/pytest_workflow.sh
./dev/pytest/pytest_tools.sh

# Code formatting and linting
./dev/reformat

# Type checking
./dev/mypy-check

# Update dependencies
./dev/update-uv
./dev/sync-uv
```

### Web (Next.js) Development
```bash
# Start development server
cd web && pnpm dev

# Build for production
cd web && pnpm build

# Run linting
cd web && pnpm lint

# Fix linting issues
cd web && pnpm eslint-fix

# Run tests
cd web && pnpm test
```

### Docker Development
```bash
# Start full stack
cd docker && docker-compose up -d

# Build Docker images
make build-all
make build-api
make build-web
```

## Key Components

### Core Workflow Engine (`api/core/workflow/`)
- **Graph Engine**: DAG-based workflow execution engine with node-by-node processing
- **Node Types**: LLM, Code, Tool, Knowledge Retrieval, HTTP Request, Condition, Loop, etc.
- **Variable System**: Dynamic variable passing between nodes with type validation
- **Stream Processing**: Real-time workflow execution with WebSocket streaming

### RAG System (`api/core/rag/`)
- **Vector Stores**: Support for 20+ vector databases (Qdrant, Weaviate, Chroma, etc.)
- **Embeddings**: Multi-provider embedding support with caching
- **Retrievers**: Keyword, semantic, and hybrid retrieval strategies
- **Document Processing**: PDF, DOCX, Markdown extractors with chunking strategies

### Agent Framework (`api/core/agent/`)
- **Agent Types**: Function Calling and ReAct agents
- **Tool Integration**: 50+ built-in tools + custom tool support
- **Plugin System**: Extensible plugin architecture for tools and models

### Model Management (`api/core/model_runtime/`)
- **Provider Support**: 100+ LLM providers (OpenAI, Anthropic, local models, etc.)
- **Load Balancing**: Multi-provider failover and load distribution
- **Token Management**: Usage tracking and quota management

## Testing Strategy

### API Testing
- **Unit Tests**: Located in `api/tests/unit_tests/`
- **Integration Tests**: Located in `api/tests/integration_tests/`
- **Test Containers**: Database testing with TestContainers
- **Mock Configuration**: Test environment setup in `api/pytest.ini`

### Web Testing
- **Jest**: Unit testing framework with React Testing Library
- **Component Tests**: Located in `__tests__/` directories
- **E2E Tests**: Browser-based testing for critical workflows

## Configuration Management

### Environment Variables
- **API Configuration**: See `docker/.env.example` for all available options
- **Database**: PostgreSQL with SQLAlchemy migrations
- **Redis**: Session storage and Celery task queue
- **Storage**: Multiple providers (S3, Azure Blob, Local, etc.)

### Development Environment
- **Python**: 3.11-3.12 with uv package manager
- **Node.js**: >= 22.11.0 with pnpm package manager
- **Dependencies**: Managed via `pyproject.toml` and `package.json`

## Code Quality Standards

### Python
- **Formatter**: Ruff formatter
- **Linter**: Ruff with custom configuration
- **Type Checking**: MyPy with strict settings
- **Import Organization**: Alphabetical ordering required

### TypeScript/React
- **Linter**: ESLint with Next.js configuration
- **Formatter**: Built into linting process
- **Type Safety**: Strict TypeScript configuration
- **Component Patterns**: Functional components with hooks

## Database Migrations

```bash
# Generate new migration
cd api && flask db migrate -m "description"

# Apply migrations
cd api && flask db upgrade

# Migration files located in api/migrations/versions/
```

## Plugin Development

### Custom Tools
- Implement in `api/core/tools/custom_tool/`
- Follow provider pattern with YAML configuration
- Support OAuth authentication for external APIs

### Workflow Nodes
- Extend base classes in `api/core/workflow/nodes/`
- Implement node execution logic with proper error handling
- Add corresponding frontend components in `web/app/components/workflow/`

## Security Considerations

- **Authentication**: JWT-based with refresh token rotation
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Pydantic models for API validation
- **XSS Protection**: DOMPurify for frontend content sanitization
- **SSRF Protection**: Built-in proxy for external requests

## Performance Optimization

### API
- **Caching**: Redis-based caching for embeddings and model responses
- **Background Tasks**: Celery for heavy computations
- **Connection Pooling**: PostgreSQL and Redis connection pools
- **Monitoring**: OpenTelemetry tracing support

### Frontend
- **Code Splitting**: Next.js automatic code splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: `pnpm analyze` command available
- **Lazy Loading**: Component-level lazy loading for large features
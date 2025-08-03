# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## User Request ##
Always reply in korean

## Common Development Commands

### Local Development
```bash
# Run the FastAPI server locally
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 --reload

# Run with Docker
docker-compose -f docker-compose.dev.yml up -d --build

# Restart server
make restart-server
```

### Code Quality Tools
```bash
# Format code with Black
poetry run black app/ data/ aws_lambda/ test/

# Sort imports with isort
poetry run isort app/ data/ aws_lambda/ test/

# Type checking with mypy
poetry run mypy app data dependencies tests

# Linting with flake8
poetry run flake8 app/ data/ aws_lambda/ test/
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest test/app/module/asset/services/test_asset_service.py

# Run tests matching a pattern
poetry run pytest -k "test_asset"

# Run with coverage
poetry run pytest --cov=app --cov-report=html
```

### Database Operations
```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

### AWS Lambda Deployment
```bash
# Deploy all Lambda functions
cd aws_lambda && make deploy-all

# Deploy specific Lambda function
cd aws_lambda && make deploy-handlers-bigquery-export-user-profile-daily
```

## High-Level Architecture

### Core Application Structure

The project follows a modular architecture with clear separation of concerns:

1. **API Layer** (`app/api/`)
   - FastAPI routers organized by domain and version
   - `asset/v1/`: Handles salary statistics and job-related endpoints
   - `auth/v1/`: Manages user registration and consent

2. **Business Logic** (`app/module/`)
   - Domain-specific modules containing services, repositories, and models
   - Services orchestrate business logic and coordinate between repositories
   - Repositories handle data persistence using SQLAlchemy async sessions
   - Each module has its own error definitions and logging configuration

3. **Data Collection** (`app/data/`)
   - External data scraping from Wanted and wage centers
   - Uses Selenium for web scraping with proper session management

4. **Common Components** (`app/common/`)
   - Shared utilities, middleware, and base classes
   - Custom exception handlers registered globally
   - Logging middleware with structured logging
   - Redis repository for caching operations

### Database Architecture

- Uses MySQL 8.0 with SQLAlchemy async engine
- Connection pooling configured with size=5, max_overflow=10
- Alembic for database migrations
- Models use SQLModel for Pydantic integration
- Slow query logging for queries > 200ms

### AWS Lambda Functions

Lambda functions are organized by purpose with shared dependencies:

1. **BigQuery Export** (`aws_lambda/handlers/bigquery/`)
   - Exports user profile data to BigQuery daily
   - Uses Google Cloud BigQuery client

2. **Email Services** (`aws_lambda/handlers/email/`)
   - Onboarding emails with HTML templates
   - Trigger system using SNS for email campaigns

3. **Shared Layer** (`aws_lambda/shared/`)
   - Common database models and configurations
   - Deployed as Lambda layer for code reuse

### Infrastructure

- **Local Development**: Docker Compose with FastAPI, MySQL, Redis, and Nginx
- **Production**: Configured for CORS with https://www.olass.co.kr
- **BigQuery**: Terraform-managed infrastructure in `infra/bigquery/`

### Key Design Patterns

1. **Repository Pattern**: All data access goes through repository classes
2. **Service Layer**: Business logic isolated in service classes
3. **Dependency Injection**: FastAPI's dependency system for database sessions
4. **Error Handling**: Custom exceptions with global handlers
5. **Async/Await**: Fully async architecture for better performance

### Environment Configuration

- Uses python-dotenv for environment variables
- Environment-specific configurations (dev/prod)
- Required environment variables:
  - `ENVIRONMENT`: dev/prod
  - Database connection details
  - AWS credentials for Lambda functions
  - Redis connection settings

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

## Infrastructure Directory (`infra/`)

인프라스트럭처 코드는 Terraform으로 관리되며 다음과 같이 구성됩니다:

### 1. **BigQuery** (`infra/bigquery/`)
- BigQuery 데이터셋 및 테이블 정의
- 개발/프로덕션 환경별 tfvars 파일
- 주요 파일:
  - `datasets.tf`: 데이터셋 구성
  - `tables.tf`: 테이블 스키마 정의
  - `terraform.dev.tfvars`, `terraform.prod.tfvars`: 환경별 설정

### 2. **CloudWatch Alarms** (`infra/cloudwatch-alarms/`)
- AWS CloudWatch 알람 구성
- Discord 연동을 위한 Lambda 함수
- 주요 파일:
  - `alarms_critical.tf`: 중요 알람 정의
  - `alarms_warning.tf`: 경고 알람 정의
  - `lambda_discord.tf`: Discord 알림 Lambda
  - `sns.tf`: SNS 토픽 구성

### 3. **Infrastructure** (`infra/infrastructure/`)
- 핵심 AWS 인프라 구성
- 주요 리소스:
  - `elastic_beanstalk.tf`: EB 애플리케이션 설정
  - `elasticache.tf`: Redis 캐시 구성
  - `rds.tf`: MySQL 데이터베이스 설정
  - `s3.tf`: S3 버킷 구성
  - `cloudwatch_logs.tf`: 로그 그룹 설정

### Terraform 명령어
```bash
# 인프라 계획 확인
cd infra/{module} && make plan-dev

# 인프라 배포
cd infra/{module} && make apply-dev

# 상태 확인
cd infra/{module} && terraform show
```

## Test Directory (`test/`)

테스트는 load test와 unit test로 구분되어 있습니다:

### 1. **Load Test** (`test/load_test/`)
- Locust를 사용한 부하 테스트
- 주요 파일:
  - `locustfile.py`: 부하 테스트 시나리오 정의
  - `report.html`: 테스트 결과 리포트
  - `Makefile`: 테스트 실행 명령어

### Load Test 명령어
```bash
# 부하 테스트 실행
cd test/load_test && make run

# 분산 부하 테스트
cd test/load_test && make run-distributed
```

### 2. **Unit Test** (`test/unit_test/`)

#### 테스트 구조
- `app/`: 애플리케이션 모듈 테스트
  - `module/asset/services/`: 자산 서비스 테스트
  - `module/user/services/`: 사용자 서비스 테스트
- `aws_lambda/`: Lambda 함수 테스트
  - `handlers/bigquery/`: BigQuery export 테스트
  - `handlers/email/`: 이메일 트리거 테스트

#### Fixture 구성 (`test/unit_test/fixtures/`)
- `base.py`: 기본 픽스처 클래스
- `asset_fixture.py`, `asset_mock_fixture.py`: 자산 관련 픽스처
- `auth_fixture.py`, `auth_mock_fixture.py`: 인증 관련 픽스처
- `lambda_mock_fixture.py`: Lambda 테스트용 모킹
- `full_fixture.py`: 통합 테스트용 전체 픽스처

#### Test Conftest (`test/unit_test/test_conftest/`)
- 픽스처 동작 검증을 위한 테스트
- `test_database_fixtures.py`: DB 픽스처 테스트
- `test_http_client_fixtures.py`: HTTP 클라이언트 테스트
- `test_integration_fixtures.py`: 통합 픽스처 테스트
- `test_redis_fixtures.py`: Redis 픽스처 테스트

### Unit Test 명령어
```bash
# 전체 테스트 실행
poetry run pytest test/unit_test/

# 특정 모듈 테스트
poetry run pytest test/unit_test/app/module/asset/

# 픽스처 테스트
poetry run pytest test/unit_test/test_conftest/

# 커버리지 포함 실행
poetry run pytest test/unit_test/ --cov=app --cov-report=html
```

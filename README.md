# PeerWorth Backend

급여 정보 및 자산 관리 서비스를 위한 FastAPI 기반 백엔드 애플리케이션

## 📁 프로젝트 구조

```
backend/
├── app/                    # 메인 애플리케이션
│   ├── api/               # API 라우터 (도메인별, 버전별 구성)
│   │   ├── asset/v1/     # 자산 관련 API
│   │   └── auth/v1/      # 인증 관련 API
│   ├── module/           # 비즈니스 로직
│   │   └── asset/        # 자산 도메인
│   │       ├── services/  # 서비스 레이어
│   │       └── repositories/ # 데이터 액세스 레이어
│   ├── common/           # 공통 컴포넌트
│   │   ├── middleware/   # 미들웨어
│   │   └── redis_repository/ # Redis 캐시
│   └── data/             # 외부 데이터 수집
├── aws_lambda/           # AWS Lambda 함수
│   ├── handlers/         # Lambda 핸들러
│   └── shared/          # 공유 라이브러리
├── database/            # 데이터베이스 설정
├── test/               # 테스트 코드 (소스와 동일한 구조)
│   ├── test_conftest/  # conftest fixture 테스트
│   ├── app/           # app 폴더 테스트
│   └── aws_lambda/    # Lambda 함수 테스트
└── infra/             # 인프라 코드 (Terraform)
```

## 🚀 빠른 시작

### 환경 설정

```bash
# Python 3.12+ 필요
poetry install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 설정값 입력
```

### 로컬 개발

```bash
# FastAPI 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 --reload

# Docker로 실행
docker-compose -f docker-compose.dev.yml up -d --build

# 서버 재시작
make restart-server
```

### 데이터베이스 관리

```bash
# 마이그레이션 생성
poetry run alembic revision --autogenerate -m "마이그레이션 설명"

# 마이그레이션 적용
poetry run alembic upgrade head

# 마이그레이션 롤백
poetry run alembic downgrade -1
```

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트 실행
poetry run pytest

# 특정 모듈 테스트
poetry run pytest test/app/module/asset/

# 커버리지 포함 테스트
poetry run pytest --cov=app --cov-report=html

# 테스트 패턴으로 실행
poetry run pytest -k "test_asset"
```

### 테스트 구조

- **Given-When-Then** 패턴 준수
- 소스 코드와 동일한 디렉토리 구조
- fixture를 활용한 테스트 데이터 관리

## 🛠️ 코드 품질

### 린팅 및 포맷팅

```bash
# 코드 포맷팅
poetry run black app/ data/ aws_lambda/ test/

# Import 정렬
poetry run isort app/ data/ aws_lambda/ test/

# 타입 체킹
poetry run mypy app data dependencies tests

# 린팅
poetry run flake8 app/ data/ aws_lambda/ test/
```

## 🏗️ 아키텍처

### 핵심 설계 패턴

- **Repository 패턴**: 데이터 액세스 추상화
- **Service 레이어**: 비즈니스 로직 분리
- **의존성 주입**: FastAPI 의존성 시스템 활용
- **비동기 처리**: 전체 아키텍처에서 async/await 사용

### 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, SQLModel
- **데이터베이스**: MySQL 8.0
- **캐시**: Redis
- **테스트**: pytest, pytest-asyncio
- **배포**: AWS Lambda, Docker
- **데이터 분석**: BigQuery

### 인프라

- **로컬 개발**: Docker Compose (FastAPI, MySQL, Redis, Nginx)
- **프로덕션**: AWS Lambda + RDS + ElastiCache
- **CI/CD**: GitHub Actions
- **모니터링**: CloudWatch, BigQuery

## 📊 AWS Lambda 함수

### BigQuery 데이터 내보내기

```bash
cd aws_lambda && make deploy-handlers-bigquery-export-user-profile-daily
```

### 이메일 서비스

- 온보딩 이메일 발송
- SNS 트리거 기반 이메일 캠페인

### 전체 Lambda 배포

```bash
cd aws_lambda && make deploy-all
```

# SQLAlchemy 쿼리 최적화 가이드

## 개요
이 문서는 SQLAlchemy ORM을 사용한 쿼리 최적화 방법과 실행계획 분석 도구 사용법을 설명합니다.

## 모니터링 시스템 구성

### 1. 자동 쿼리 모니터링
- **위치**: `app.common.monitoring.query_monitor`
- **기능**: 모든 쿼리 실행시간 추적, 슬로우 쿼리 감지
- **임계값**: 기본 0.2초 (설정 가능)

### 2. API별 쿼리 분석 미들웨어
- **위치**: `app.common.middleware.query_monitoring_middleware`
- **기능**: API 요청별 쿼리 통계, HTTP 헤더에 통계 정보 추가
- **헤더**: `X-Query-Count`, `X-Query-Time`, `X-Slow-Query-Count`

### 3. 디버그 API 엔드포인트
개발환경에서만 활성화되는 쿼리 분석 API:

```bash
# 전체 쿼리 통계
GET /api/asset/debug/query-stats

# 슬로우 쿼리 목록
GET /api/asset/debug/slow-queries?limit=10

# Jobs API 쿼리 분석
GET /api/asset/debug/analyze-jobs

# Profile API 쿼리 분석
GET /api/asset/debug/analyze-profile/{unique_id}?save_rate=50

# 특정 쿼리 실행계획 분석
POST /api/asset/debug/explain-query
{
  "sql": "SELECT * FROM user_salary WHERE job_id = :job_id",
  "params": {"job_id": 1}
}
```

## 사용법

### 1. 개발 서버 실행
```bash
# 개발환경으로 실행 (쿼리 모니터링 활성화)
ENVIRONMENT=dev uvicorn main:app --reload
```

### 2. API 호출 후 쿼리 분석
```bash
# API 호출
curl -H "Accept: application/json" http://localhost:8000/api/asset/v1/jobs

# 응답 헤더에서 쿼리 통계 확인
# X-Query-Count: 2
# X-Query-Time: 0.045
# X-Slow-Query-Count: 0
```

### 3. 상세 쿼리 분석
```bash
# Jobs API 분석
curl http://localhost:8000/api/asset/debug/analyze-jobs

# 응답 예시
{
  "api": "get_jobs",
  "result_count": 15,
  "queries_executed": 2,
  "query_details": [
    {
      "sql": "SELECT job.id, job.name FROM job WHERE job.is_deleted = false",
      "execution_time": "0.023s",
      "is_slow": false
    }
  ]
}
```

## 최적화 가이드

### 1. N+1 쿼리 문제 해결
```python
# 🚫 잘못된 예 (N+1 문제)
jobs = await session.execute(select(Job))
for job in jobs:
    job_group = await session.execute(select(JobGroup).where(JobGroup.id == job.group_id))

# ✅ 올바른 예 (JOIN 사용)
stmt = select(Job).join(JobGroup).options(selectinload(Job.group))
jobs = await session.execute(stmt)
```

### 2. 인덱스 활용 확인
```bash
# 실행계획 분석
curl -X POST http://localhost:8000/api/asset/debug/explain-query \\
  -H "Content-Type: application/json" \\
  -d '{
    "sql": "SELECT * FROM user_salary WHERE job_id = :job_id AND experience = :exp",
    "params": {"job_id": 1, "exp": 3}
  }'

# 분석 결과에서 확인할 항목:
# - access_type: "ref" (좋음) vs "ALL" (나쁨)
# - key: 사용된 인덱스명
# - rows_examined_per_scan: 검사된 행 수
```

### 3. 복합 인덱스 최적화
```sql
-- 자주 함께 사용되는 컬럼에 복합 인덱스 생성
CREATE INDEX idx_user_salary_job_exp ON user_salary(job_id, experience);

-- WHERE 절의 컬럼 순서와 인덱스 컬럼 순서 일치시키기
SELECT * FROM user_salary WHERE job_id = 1 AND experience = 3;
```

### 4. 쿼리 최적화 체크리스트

#### 슬로우 쿼리 발견 시:
1. **실행계획 확인**: `EXPLAIN` 사용
2. **인덱스 여부**: `access_type`이 `ALL`인지 확인
3. **SELECT 절 최적화**: 필요한 컬럼만 조회
4. **JOIN 최적화**: 적절한 JOIN 타입 사용
5. **WHERE 절 최적화**: 인덱스 활용 가능한 조건 사용

#### 인덱스 추가가 필요한 경우:
```python
# Alembic 마이그레이션으로 인덱스 추가
def upgrade():
    op.create_index('idx_user_salary_lookup', 'user_salary', ['job_id', 'experience'])

def downgrade():
    op.drop_index('idx_user_salary_lookup', 'user_salary')
```

## 주의사항

### 1. 프로덕션 환경
- 쿼리 모니터링 미들웨어는 개발환경에서만 사용
- 디버그 API는 프로덕션에서 자동 비활성화

### 2. 성능 영향
- 모니터링 시스템 자체의 오버헤드 최소화
- 슬로우 쿼리만 상세 로깅

### 3. 보안
- 디버그 API는 내부 네트워크에서만 접근 가능하도록 설정
- 쿼리 파라미터에 민감한 정보 로깅 주의

## 모니터링 대시보드 (향후 계획)

```python
# Grafana/Prometheus 연동을 위한 메트릭 수집
from prometheus_client import Counter, Histogram

query_duration = Histogram('sqlalchemy_query_duration_seconds', 'Query duration')
slow_query_counter = Counter('sqlalchemy_slow_queries_total', 'Slow query count')
```

이 시스템을 통해 각 API별 쿼리 성능을 실시간으로 모니터링하고 최적화할 수 있습니다.

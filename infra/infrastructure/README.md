# AWS Infrastructure as Code

Elastic Beanstalk, RDS MySQL, ElastiCache Redis를 관리하는 Terraform 코드입니다.

## 📁 파일 구조

```
infra/infrastructure/
├── main.tf                   # Provider 및 데이터 소스 설정
├── variables.tf              # 변수 정의
├── elastic_beanstalk.tf      # Elastic Beanstalk 리소스
├── rds.tf                   # RDS MySQL 리소스
├── elasticache.tf           # ElastiCache Redis 리소스
├── outputs.tf               # 출력 값 정의
├── terraform.dev.tfvars     # 개발 환경 설정
├── terraform.prod.tfvars    # 운영 환경 설정
├── Makefile                 # 배포 자동화 스크립트
└── README.md                # 이 파일
```

## 🏗️ 아키텍처

### 개발 환경 (dev)
- **Elastic Beanstalk**: t3.micro, 단일 인스턴스
- **RDS MySQL**: db.t3.micro, 20GB, 백업 1일
- **ElastiCache Redis**: cache.t3.micro, 스냅샷 1일

### 프로덕션 환경 (prod)
- **Elastic Beanstalk**: t3.small, Auto Scaling (1-3 인스턴스)
- **RDS MySQL**: db.t3.small, 100GB, 백업 7일, Enhanced Monitoring
- **ElastiCache Redis**: cache.t3.small, 스냅샷 5일

## 🚀 사용 방법

### 1. 사전 준비

```bash
# 1. 디렉토리 이동
cd infra/infrastructure

# 2. AWS CLI 설정 확인
aws configure list

# 3. 환경별 설정 파일 수정
# terraform.dev.tfvars에서 db_password 등 중요 정보 수정
```

### 2. 개발 환경 배포

```bash
# 전체 파이프라인 실행
make dev-deploy

# 또는 단계별 실행
make init
make plan-dev
make apply-dev
```

### 3. 프로덕션 환경 배포

```bash
# 계획 확인 (신중히!)
make prod-plan

# 배포 (수동 승인 필요)
make apply-prod
```

## 📊 모니터링 연동

### monitoring-alarms와 연결

이 인프라는 `../monitoring-alarms/` 폴더의 CloudWatch 알람과 연동됩니다:

```bash
# 1. 인프라 배포 후 리소스 정보 확인
cd infra/infrastructure
make output

# 2. 출력된 정보로 monitoring-alarms 설정 업데이트
cd ../monitoring-alarms
# terraform.dev.tfvars에서 다음 값들 업데이트:
# - db_instance_identifier
# - elasticache_cluster_id
# - alb_name (EB에서 생성된 ALB 이름)

# 3. 알람 배포
make apply-dev
```

### 환경 변수 자동 설정

Elastic Beanstalk 환경에 다음 변수들이 자동으로 설정됩니다:

- `ENVIRONMENT`: dev/prod
- `DB_HOST`: RDS 엔드포인트
- `DB_NAME`: 데이터베이스 이름
- `DB_USER`: 데이터베이스 사용자
- `DB_PASSWORD`: 데이터베이스 비밀번호
- `REDIS_HOST`: Redis 엔드포인트
- `REDIS_PORT`: Redis 포트

## ⚙️ 설정 커스터마이징

### 인스턴스 크기 변경

`terraform.dev.tfvars` 또는 `terraform.prod.tfvars`에서:

```hcl
# Elastic Beanstalk 인스턴스 타입
eb_instance_type = "t3.small"

# RDS 인스턴스 클래스
db_instance_class = "db.t3.small"

# Redis 노드 타입
redis_node_type = "cache.t3.small"
```

### 보안 설정

```hcl
# 특정 IP만 접근 허용 (프로덕션 권장)
allowed_cidr_blocks = ["203.0.113.0/24", "198.51.100.0/24"]

# 데이터베이스 암호화 (프로덕션에서 자동 활성화)
# RDS에서 storage_encrypted = true로 설정됨
```

## 📋 운영 가이드

### 상태 확인

```bash
# 전체 리소스 상태
make full-status

# 개별 서비스 상태
make eb-status    # Elastic Beanstalk
make rds-status   # RDS
make redis-status # ElastiCache
```

### 로그 확인

```bash
# Elastic Beanstalk 로그 그룹 확인
make logs-eb

# 애플리케이션 로그 (CloudWatch에서)
aws logs tail /aws/elasticbeanstalk/olass-dev-env/var/log/eb-docker/containers/eb-current-app
```

### 백업 및 복구

```bash
# RDS 스냅샷 생성
aws rds create-db-snapshot \
  --db-instance-identifier $(terraform output -raw rds_identifier) \
  --db-snapshot-identifier manual-backup-$(date +%Y%m%d)

# Redis 스냅샷 생성
aws elasticache create-snapshot \
  --cache-cluster-id $(terraform output -raw redis_cluster_id) \
  --snapshot-name manual-backup-$(date +%Y%m%d)
```

## 🔧 트러블슈팅

### 자주 발생하는 문제

**1. Elastic Beanstalk 배포 실패**

```bash
# 환경 이벤트 확인
aws elasticbeanstalk describe-events \
  --environment-name $(terraform output -raw eb_environment_name)
```

**2. RDS 연결 실패**

```bash
# 보안 그룹 규칙 확인
aws ec2 describe-security-groups \
  --group-ids $(terraform output -raw rds_security_group_id)
```

**3. Redis 연결 실패**

```bash
# 클러스터 노드 정보 확인
aws elasticache describe-cache-clusters \
  --cache-cluster-id $(terraform output -raw redis_cluster_id) \
  --show-cache-node-info
```

## 💰 비용 최적화

### 개발 환경
- 모든 리소스 t3.micro/cache.t3.micro 사용
- RDS 백업 1일, Redis 스냅샷 1일
- Enhanced Monitoring 비활성화

### 프로덕션 환경
- 필요에 따라 인스턴스 크기 조정
- 자동 스케일링으로 비용 효율성 확보
- 스냅샷 보존 기간 최적화

## 🔗 관련 문서

- [모니터링 알람 설정](../monitoring-alarms/README.md)
- [BigQuery 연동](../bigquery/README.md)
- [AWS Elastic Beanstalk 문서](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

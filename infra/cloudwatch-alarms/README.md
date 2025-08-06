# CloudWatch Monitoring Infrastructure

AWS CloudWatch 알람 및 모니터링을 위한 Terraform 코드입니다.

## 📁 파일 구조

```
infra/monitoring-alarms/
├── main.tf                   # Provider 및 데이터 소스 설정
├── variables.tf              # 변수 정의
├── sns.tf                   # SNS 토픽 및 구독 설정
├── alarms_critical.tf       # Critical 알람 (5개)
├── alarms_warning.tf        # Warning 알람 (5개)
├── outputs.tf               # 출력 값 정의
├── terraform.dev.tfvars     # 개발 환경 설정
├── terraform.prod.tfvars    # 운영 환경 설정
├── Makefile                 # 배포 자동화 스크립트
└── README.md                # 이 파일
```

## 🚨 알람 구성

### Critical 알람 (즉시 대응)

| 알람명                   | 서비스 | 메트릭              | 임계값 | 평가 기간 |
| ------------------------ | ------ | ------------------- | ------ | --------- |
| RDS-ConnectionSaturation | RDS    | DatabaseConnections | > 40   | 2회/10분  |
| RDS-LowStorage           | RDS    | FreeStorageSpace    | < 1GB  | 1회/5분   |
| ALB-NoHealthyTargets     | ALB    | HealthyHostCount    | < 1    | 1회/5분   |
| EC2-StatusCheckFailed    | EC2    | StatusCheckFailed   | > 0    | 1회/5분   |
| Redis-Evictions          | Redis  | Evictions           | > 0    | 1회/5분   |

### Warning 알람 (15분 내 확인)

| 알람명            | 서비스 | 메트릭                        | 임계값  | 평가 기간 |
| ----------------- | ------ | ----------------------------- | ------- | --------- |
| ALB-High5xxErrors | ALB    | HTTPCode_Target_5XX_Count     | > 10    | 2회/10분  |
| RDS-HighCPU       | RDS    | CPUUtilization                | > 75%   | 3회/15분  |
| Redis-HighMemory  | Redis  | DatabaseMemoryUsagePercentage | > 85%   | 2회/10분  |
| ALB-SlowResponse  | ALB    | TargetResponseTime            | > 1.0초 | 3회/15분  |
| EC2-HighCPU       | EC2    | CPUUtilization                | > 80%   | 2회/10분  |

**무료 티어 최적화를 위해 제거된 알람들:**
- RDS-LowMemory (RDS-HighCPU로 간접 감지)
- RDS-HighReadLatency (RDS-HighCPU와 중복)
- Redis-HighEngineCPU (Redis-HighMemory가 더 중요)
- ALB-UnhealthyTargets (Critical의 NoHealthyTargets로 충분)
- ALB-High4xxErrors (클라이언트 에러, 우선순위 낮음)

## 🚀 사용 방법

### 1. 사전 준비

```bash
# 1. 디렉토리 이동
cd infra/monitoring-alarms

# 2. 환경 변수 파일 수정
# terraform.dev.tfvars 또는 terraform.prod.tfvars에서
# 실제 리소스 ID로 수정:
# - db_instance_identifier
# - elasticache_cluster_id
# - alb_name
# - alert_email
```

### 2. 개발 환경 배포

```bash
# 초기화
make init

# 계획 확인
make plan-dev

# 배포
make apply-dev

# 알람 상태 확인
make list-alarms ENV=dev
```

### 3. 운영 환경 배포

```bash
# 계획 확인 (신중히!)
make plan-prod

# 배포 (수동 승인 필요)
make apply-prod

# 상태 확인
make alarm-state ENV=prod
```

## ⚙️ 설정 커스터마이징

### 임계값 변경

`terraform.dev.tfvars` 또는 `terraform.prod.tfvars`에서 수정:

```hcl
# 예시: RDS 연결 수 임계값 변경
rds_connection_threshold = 50  # 기본값: 40

# 예시: ALB 응답 시간 임계값 변경
alb_response_time_threshold = 0.5  # 기본값: 1.0초
```

### 알림 방식 추가

```hcl
# Discord 웹훅 추가
discord_webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

## 📊 모니터링 대시보드

AWS Console에서 **Automatic Dashboard** 활용:

1. CloudWatch → Dashboards → Automatic dashboards
2. EC2, RDS, ElastiCache, Application ELB 각각 확인

## 🔔 알림 테스트

```bash
# SNS 토픽으로 테스트 메시지 발송
make test-alarm TOPIC_ARN=arn:aws:sns:ap-northeast-2:123456789012:olass-dev-critical-alerts
```

## 📋 운영 체크리스트

### 배포 전

- [ ] 리소스 ID가 올바른지 확인
- [ ] 이메일 주소가 정확한지 확인
- [ ] 임계값이 환경에 적합한지 확인

### 배포 후

- [ ] 이메일 구독 확인 (받은 편지함 확인)
- [ ] 알람 상태 확인: `make alarm-state`
- [ ] 테스트 알림 발송: `make test-alarm`

### 일상 운영

- [ ] 주간 알람 상태 리뷰
- [ ] 월간 임계값 적정성 검토
- [ ] 분기별 알람 효과성 분석

## 🔧 트러블슈팅

### 자주 발생하는 문제

**1. 리소스를 찾을 수 없음**

```bash
# 문제: Error: No matching EC2 instances found
# 해결: EC2 인스턴스에 Environment 태그 추가
aws ec2 create-tags --resources i-1234567890abcdef0 --tags Key=Environment,Value=dev
```

**2. SNS 구독이 확인되지 않음**

```bash
# 이메일 받은 편지함 확인 후 "Confirm subscription" 클릭
# 또는 CLI로 확인:
aws sns list-subscriptions-by-topic --topic-arn <topic-arn>
```

**3. 너무 많은 알람 생성**

```bash
# 현재 알람 수 확인
make output | grep total_alarm_count

# 10개 초과 시 비용 발생하므로 불필요한 알람 제거
```

## 💰 비용 관리

- **무료 한도**: 알람 10개까지 무료
- **예상 비용**: 10개 초과 시 알람당 $0.10/월
- **최적화**: Critical 5개 + Warning 5개 = 총 10개로 무료 운영

## 📚 추가 자료

- [AWS CloudWatch 알람 문서](https://docs.aws.amazon.com/cloudwatch/latest/monitoring/AlarmThatSendsEmail.html)
- [Terraform AWS Provider 문서](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [프로젝트 모니터링 전략 문서](../../docs/monitoring_strategy_confluence.md)

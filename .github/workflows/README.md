# GitHub Actions 환경변수 설정 가이드

## 필요한 GitHub Secrets

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 시크릿들을 추가해야 합니다:

### 1. AWS 인증 정보 (필수)
- `AWS_ACCESS_KEY_ID`: AWS IAM 사용자의 액세스 키 ID
- `AWS_SECRET_ACCESS_KEY`: AWS IAM 사용자의 시크릿 액세스 키
- `AWS_REGION`: AWS 리전 (예: ap-northeast-2)

### 2. GitHub Personal Access Token (필수)
- `GH_PAT`: 태그 생성 권한이 있는 GitHub Personal Access Token
  - Settings > Developer settings > Personal access tokens에서 생성
  - 필요 권한: `repo` (전체)

### 3. Elastic Beanstalk 설정 (필수)
- `DEV_EB_APPLICATION_NAME`: 개발 환경 EB 애플리케이션 이름
- `DEV_EB_ENV_NAME`: 개발 환경 EB 환경 이름
- `DEV_EB_BUCKET`: 개발 환경 EB 배포용 S3 버킷 이름
- `EB_APPLICATION_NAME`: 프로덕션 환경 EB 애플리케이션 이름 (main 브랜치용)
- `EB_ENV_NAME`: 프로덕션 환경 EB 환경 이름 (main 브랜치용)
- `EB_BUCKET`: 프로덕션 환경 EB 배포용 S3 버킷 이름 (main 브랜치용)

### 4. 환경 파일 (필수)
- `DEV_ENV_CONTENTS`: 개발 환경 .env 파일 전체 내용
- `BACKEND_ENV_CONTENTS`: 프로덕션 환경 .env 파일 전체 내용 (main 브랜치용)

### 5. 선택적 시크릿 (필요시 추가)
- `SLACK_WEBHOOK_URL`: 배포 알림을 위한 Slack 웹훅 URL
- `SENTRY_DSN`: 에러 모니터링을 위한 Sentry DSN
- `NEW_RELIC_LICENSE_KEY`: New Relic 모니터링 라이센스 키

## GitHub Environment 설정

Settings > Environments에서 환경별 설정을 추가할 수 있습니다:

### dev 환경
1. Environment name: `dev`
2. Environment secrets:
   - 개발 환경 전용 시크릿 추가 가능
3. Protection rules:
   - Required reviewers: 선택사항
   - Wait timer: 선택사항

### prod 환경 (추후 생성)
1. Environment name: `prod`
2. Environment secrets:
   - 프로덕션 전용 시크릿
3. Protection rules:
   - Required reviewers: 2명 이상 권장
   - Restrict deployment branches: main 브랜치만
   - Wait timer: 5분 권장

## IAM 권한 요구사항

GitHub Actions에서 사용할 IAM 사용자는 다음 권한이 필요합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "elasticbeanstalk:*",
        "s3:*",
        "ec2:*",
        "elasticloadbalancing:*",
        "autoscaling:*",
        "cloudwatch:*",
        "logs:*",
        "rds:*",
        "elasticache:*",
        "iam:*",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateServiceLinkedRole"
      ],
      "Resource": "arn:aws:iam::*:role/aws-service-role/*"
    }
  ]
}
```

## Terraform State 관리

원격 상태 저장소를 사용하는 경우:

1. S3 백엔드 설정 (terraform/backend.tf):
```hcl
terraform {
  backend "s3" {
    bucket = "olass-terraform-state"
    key    = "dev/terraform.tfstate"
    region = "ap-northeast-2"
    encrypt = true
  }
}
```

2. 추가 필요 권한:
- S3 버킷 읽기/쓰기 권한
- DynamoDB 테이블 권한 (상태 잠금용)

## 워크플로우 트리거

- `dev` 브랜치에 push 시 자동 배포
- `dev` 브랜치로 PR이 merge될 때 자동 배포
- 수동 트리거도 가능 (workflow_dispatch 추가 시)

## 로컬 테스트

GitHub Actions 실행 전 로컬에서 테스트:

```bash
# AWS 자격 증명 설정
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# Terraform 테스트
cd infra/infrastructure
terraform plan -var-file=terraform.dev.tfvars

# 배포 스크립트 테스트
./deploy-eb.sh dev
```

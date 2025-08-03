# Terraform Infrastructure Management Makefile

.PHONY: help init plan-dev plan-prod apply-dev apply-prod destroy-dev destroy-prod validate format clean status

# 기본 변수
ENV ?= dev
TF_VAR_FILE = terraform.$(ENV).tfvars

help: ## 사용 가능한 명령어 목록
	@echo "Infrastructure Management Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Terraform 초기화
	terraform init

validate: ## Terraform 구성 검증
	terraform validate

format: ## Terraform 코드 포맷팅
	terraform fmt -recursive

plan-dev: ## 개발 환경 배포 계획 확인
	terraform plan -var-file=terraform.dev.tfvars

plan-prod: ## 프로덕션 환경 배포 계획 확인 (신중히!)
	terraform plan -var-file=terraform.prod.tfvars

apply-dev: ## 개발 환경 배포
	terraform apply -var-file=terraform.dev.tfvars

apply-prod: ## 프로덕션 환경 배포 (수동 승인 필요)
	terraform apply -var-file=terraform.prod.tfvars

destroy-dev: ## 개발 환경 삭제
	terraform destroy -var-file=terraform.dev.tfvars

destroy-prod: ## 프로덕션 환경 삭제 (주의!)
	@echo "⚠️  프로덕션 환경 삭제는 매우 위험합니다!"
	@echo "정말로 삭제하시겠습니까? [y/N]"
	@read -r response && [ "$$response" = "y" ] || exit 1
	terraform destroy -var-file=terraform.prod.tfvars

status: ## 현재 인프라 상태 확인
	@echo "=== Terraform State ==="
	terraform show -json | jq -r '.values.root_module.resources[] | select(.type == "aws_elastic_beanstalk_environment" or .type == "aws_db_instance" or .type == "aws_elasticache_cluster") | "\(.type): \(.values.name // .values.identifier // .values.cluster_id)"'

output: ## 배포된 리소스 정보 출력
	terraform output

eb-status: ## Elastic Beanstalk 환경 상태 확인
	@EB_ENV=$$(terraform output -raw eb_environment_name 2>/dev/null) && \
	if [ -n "$$EB_ENV" ]; then \
		ENV_STATUS=$$(aws elasticbeanstalk describe-environments --environment-names $$EB_ENV --query "Environments[0].Status" --output text 2>/dev/null || echo "NOT_FOUND") && \
		if [ "$$ENV_STATUS" != "NOT_FOUND" ] && [ "$$ENV_STATUS" != "None" ]; then \
			aws elasticbeanstalk describe-environment-health --environment-name $$EB_ENV --attribute-names All; \
		else \
			echo "Elastic Beanstalk 환경이 아직 생성되지 않았습니다. GitHub Actions를 통해 첫 배포를 진행하세요."; \
		fi \
	else \
		echo "Elastic Beanstalk 환경 이름이 설정되지 않았습니다."; \
	fi

rds-status: ## RDS 상태 확인
	@RDS_ID=$$(terraform output -raw rds_identifier 2>/dev/null) && \
	if [ -n "$$RDS_ID" ]; then \
		aws rds describe-db-instances --db-instance-identifier $$RDS_ID --query 'DBInstances[0].{Status:DBInstanceStatus,Engine:Engine,Class:DBInstanceClass,Storage:AllocatedStorage}'; \
	else \
		echo "RDS 인스턴스가 배포되지 않았습니다."; \
	fi

redis-status: ## Valkey 클러스터 상태 확인
	@REDIS_ID=$$(terraform output -raw redis_cluster_id 2>/dev/null) && \
	if [ -n "$$REDIS_ID" ]; then \
		aws elasticache describe-replication-groups --replication-group-id $$REDIS_ID --query 'ReplicationGroups[0].{Status:Status,NodeType:CacheNodeType,Engine:Engine}'; \
	else \
		echo "Valkey 클러스터가 배포되지 않았습니다."; \
	fi

logs-eb: ## Elastic Beanstalk 로그 확인
	@EB_ENV=$$(terraform output -raw eb_environment_name 2>/dev/null) && \
	if [ -n "$$EB_ENV" ]; then \
		aws logs describe-log-groups --log-group-name-prefix "/aws/elasticbeanstalk/$$EB_ENV"; \
	else \
		echo "Elastic Beanstalk 환경이 배포되지 않았습니다."; \
	fi

clean: ## Terraform 임시 파일 정리
	rm -rf .terraform/
	rm -f terraform.tfstate.backup
	rm -f .terraform.lock.hcl

# 개발 환경 빠른 배포
dev-deploy: init validate format plan-dev apply-dev ## 개발 환경 전체 배포 파이프라인

# 프로덕션 환경 빠른 배포 (계획만)
prod-plan: init validate format plan-prod ## 프로덕션 환경 배포 계획만 실행

# 전체 상태 확인
full-status: status eb-status rds-status redis-status ## 모든 리소스 상태 종합 확인

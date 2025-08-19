TERRAFORM_DIR := $(CURDIR)
TFVARS ?= terraform.dev.tfvars

# 환경별 로컬 state 파일 설정
DEV_STATE := terraform.dev.tfstate
PROD_STATE := terraform.prod.tfstate

# 환경별 state 초기화 (로컬 state 사용)
init-dev:
	cd $(TERRAFORM_DIR) && terraform init -reconfigure

init-prod:
	cd $(TERRAFORM_DIR) && terraform init -reconfigure

# 기본 명령어들
plan:
	cd $(TERRAFORM_DIR) && terraform plan -var-file=$(TFVARS)

apply:
	cd $(TERRAFORM_DIR) && terraform apply -var-file=$(TFVARS)

destroy:
	cd $(TERRAFORM_DIR) && terraform destroy -var-file=$(TFVARS)

# Dev 환경 명령어
dev-plan:
	@echo "Using dev environment..."
	@cd $(TERRAFORM_DIR) && \
	terraform plan -var-file=terraform.dev.tfvars -state=$(DEV_STATE)

dev-apply:
	@echo "Using dev environment..."
	@cd $(TERRAFORM_DIR) && \
	terraform apply -var-file=terraform.dev.tfvars -state=$(DEV_STATE)

dev-destroy:
	@echo "Using dev environment..."
	@cd $(TERRAFORM_DIR) && \
	terraform destroy -var-file=terraform.dev.tfvars -state=$(DEV_STATE)

# Prod 환경 명령어
prod-plan:
	@echo "Using prod environment..."
	@cd $(TERRAFORM_DIR) && \
	terraform plan -var-file=terraform.prod.tfvars -state=$(PROD_STATE)

prod-apply:
	@echo "Using prod environment..."
	@cd $(TERRAFORM_DIR) && \
	terraform apply -var-file=terraform.prod.tfvars -state=$(PROD_STATE)

prod-destroy:
	@echo "Using prod environment..."
	@cd $(TERRAFORM_DIR) && \
	terraform destroy -var-file=terraform.prod.tfvars -state=$(PROD_STATE)

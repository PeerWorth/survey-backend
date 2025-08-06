# CloudWatch Monitoring Infrastructure Makefile

.PHONY: help init plan apply destroy clean validate format

# Default environment
ENV ?= dev

help: ## Show this help message
	@echo "CloudWatch Monitoring Infrastructure Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
init: ## Initialize Terraform
	terraform init

validate: ## Validate Terraform configuration
	terraform validate

format: ## Format Terraform files
	terraform fmt -recursive

plan-dev: ## Plan for development environment
	terraform plan -var-file="terraform.dev.tfvars" -out=terraform-dev.plan

apply-dev: ## Apply for development environment
	terraform apply -var-file="terraform.dev.tfvars" -auto-approve

destroy-dev: ## Destroy development environment
	terraform destroy -var-file="terraform.dev.tfvars" -auto-approve

##@ Production
plan-prod: ## Plan for production environment
	terraform plan -var-file="terraform.prod.tfvars" -out=terraform-prod.plan

apply-prod: ## Apply for production environment (requires manual approval)
	terraform apply -var-file="terraform.prod.tfvars"

destroy-prod: ## Destroy production environment (requires manual approval)
	terraform destroy -var-file="terraform.prod.tfvars"

##@ General Commands
plan: ## Plan for specified environment (make plan ENV=dev)
	terraform plan -var-file="terraform.$(ENV).tfvars" -out=terraform-$(ENV).plan

apply: ## Apply for specified environment (make apply ENV=dev)
	terraform apply -var-file="terraform.$(ENV).tfvars" $(if $(filter prod,$(ENV)),,-auto-approve)

destroy: ## Destroy specified environment (make destroy ENV=dev)
	terraform destroy -var-file="terraform.$(ENV).tfvars" $(if $(filter prod,$(ENV)),,-auto-approve)

show: ## Show current state
	terraform show

output: ## Show outputs
	terraform output

state-list: ## List resources in state
	terraform state list

##@ Cleanup
clean: ## Clean temporary files
	rm -f terraform*.plan
	rm -f .terraform.lock.hcl

clean-all: ## Clean all Terraform files (DANGEROUS)
	rm -rf .terraform/
	rm -f terraform*.plan
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate*

##@ Alarm Management
list-alarms: ## List all CloudWatch alarms
	aws cloudwatch describe-alarms --query 'MetricAlarms[?starts_with(AlarmName, `olass-$(ENV)`)].AlarmName' --output table

alarm-state: ## Show alarm states
	aws cloudwatch describe-alarms --query 'MetricAlarms[?starts_with(AlarmName, `olass-$(ENV)`)].{Name:AlarmName,State:StateValue,Reason:StateReason}' --output table

test-alarm: ## Test SNS notification (specify TOPIC_ARN)
	@if [ -z "$(TOPIC_ARN)" ]; then echo "Usage: make test-alarm TOPIC_ARN=<sns-topic-arn>"; exit 1; fi
	aws sns publish --topic-arn $(TOPIC_ARN) --message "Test alarm notification from $(ENV) environment"

##@ Documentation
docs: ## Generate documentation
	@echo "# CloudWatch Alarms Documentation" > ALARMS.md
	@echo "" >> ALARMS.md
	@echo "## Critical Alarms" >> ALARMS.md
	@terraform output critical_alarms >> ALARMS.md
	@echo "" >> ALARMS.md
	@echo "## Warning Alarms" >> ALARMS.md
	@terraform output warning_alarms >> ALARMS.md
	@echo "" >> ALARMS.md
	@echo "Total Alarms: " >> ALARMS.md
	@terraform output total_alarm_count >> ALARMS.md

##@ Examples
example-usage: ## Show example usage
	@echo "Example usage:"
	@echo ""
	@echo "1. Initialize and plan for dev:"
	@echo "   make init"
	@echo "   make plan-dev"
	@echo ""
	@echo "2. Apply to dev environment:"
	@echo "   make apply-dev"
	@echo ""
	@echo "3. Check alarm status:"
	@echo "   make list-alarms ENV=dev"
	@echo ""
	@echo "4. Apply to production:"
	@echo "   make plan-prod"
	@echo "   make apply-prod"
	@echo ""
	@echo "5. Test notifications:"
	@echo "   make test-alarm TOPIC_ARN=arn:aws:sns:region:account:topic"

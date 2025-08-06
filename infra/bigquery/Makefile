TERRAFORM_DIR := $(CURDIR)
TFVARS ?= terraform.dev.tfvars

init:
	cd $(TERRAFORM_DIR) && terraform init

plan:
	cd $(TERRAFORM_DIR) && terraform plan -var-file=$(TFVARS)

apply:
	cd $(TERRAFORM_DIR) && terraform apply -var-file=$(TFVARS)

destroy:
	cd $(TERRAFORM_DIR) && terraform destroy -var-file=$(TFVARS)

dev-plan:
	make plan TFVARS=terraform.dev.tfvars

prod-plan:
	make plan TFVARS=terraform.prod.tfvars

dev-apply:
	make apply TFVARS=terraform.dev.tfvars

prod-apply:
	make apply TFVARS=terraform.prod.tfvars

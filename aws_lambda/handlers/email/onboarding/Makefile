# 기본 설정
ENV_FILE ?= $(abspath $(dir $(lastword $(MAKEFILE_LIST)))../../../.env)
include $(ENV_FILE)

PYTHON=python3.12
REGION=ap-northeast-2
LAMBDA_NAME=olass-onboarding-email
ROLE_ARN=arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(AWS_LAMBDA_ROLE_NAME)

# === LAYER ===
LAYER_DIR=$(abspath $(dir $(lastword $(MAKEFILE_LIST)))../../../layers/base)
LAYER_ZIP=layer.zip
LAYER_NAME=olass-base-layer
LAYER_REQ=$(LAYER_DIR)/requirements.txt

# === HANDLER ===
HANDLER_DIR=$(abspath $(dir $(lastword $(MAKEFILE_LIST))))
HANDLER_ZIP=function.zip
SHARED_DIR=$(abspath $(HANDLER_DIR)/../../../shared)

.PHONY: all clean build-layer zip-layer deploy-layer zip-handler create update deploy

all: deploy

clean:
	rm -rf python __pycache__ $(HANDLER_DIR)/$(LAYER_ZIP) $(HANDLER_DIR)/$(HANDLER_ZIP)

# 1. Layer 빌드 및 배포
build-layer:
	$(PYTHON) -m pip install -r $(LAYER_REQ) -t python/

zip-layer: build-layer
	cd python && zip -r ../$(LAYER_ZIP) .

deploy-layer: zip-layer
	aws lambda publish-layer-version \
		--layer-name $(LAYER_NAME) \
		--zip-file fileb://$(LAYER_ZIP) \
		--compatible-runtimes python3.11 \
		--region $(REGION)

# 2. Handler 빌드
zip-handler:
	zip -r $(HANDLER_ZIP) \
		handler.py \
		service.py \
		repository.py \
		constant.py \
		template.html \
		../../../shared/base.html \
		../../../shared/db_config.py \
		../../../shared/auth_model.py


# 3. Lambda 배포
LAYER_VERSION := $(shell aws lambda list-layer-versions \
	--layer-name $(LAYER_NAME) \
	--region $(REGION) \
	--query 'LayerVersions[0].Version' \
	--output text)

create: zip-handler
	aws lambda create-function \
		--function-name $(LAMBDA_NAME) \
		--runtime python3.11 \
		--role $(ROLE_ARN) \
		--handler handler.lambda_handler \
		--zip-file fileb://$(HANDLER_ZIP) \
		--timeout 10 \
		--memory-size 128 \
		--region $(REGION) \
		--layers arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(LAYER_NAME):$(LAYER_VERSION)

update: zip-handler
	aws lambda update-function-configuration \
		--function-name $(LAMBDA_NAME) \
		--layers arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(LAYER_NAME):$(LAYER_VERSION) \
		--region $(REGION)

	aws lambda update-function-code \
		--function-name $(LAMBDA_NAME) \
		--zip-file fileb://$(HANDLER_ZIP) \
		--region $(REGION)

deploy:
	@echo "Attempting to update existing Lambda..."
	@make update || (echo "Function not found. Creating instead..." && make create)

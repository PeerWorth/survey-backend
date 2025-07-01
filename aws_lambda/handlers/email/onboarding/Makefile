# 기본 설정
ENV_FILE ?= ../../.env
include $(ENV_FILE)

PYTHON=python3.12
REGION=ap-northeast-2
LAMBDA_NAME=olass-onboarding-email
ROLE_ARN=arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(AWS_LAMBDA_ROLE_NAME)

# === LAYER ===
LAYER_DIR=layers/base
LAYER_ZIP=layer.zip
LAYER_NAME=olass-base-layer
LAYER_REQ=$(LAYER_DIR)/requirements.txt

# === HANDLER ===
HANDLER_ZIP=function.zip
HANDLER_PATH=handlers/email/onboarding
HANDLER_HANDLER=handler.lambda_handler

.PHONY: all clean build-layer build-handler zip-handler zip-layer deploy-layer create update deploy

all: deploy

clean:
	rm -rf python __pycache__ $(LAYER_ZIP) $(HANDLER_ZIP)

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

# 2. Handler zip
zip-handler:
	zip -j $(HANDLER_ZIP) \
		$(HANDLER_PATH)/handler.py \
		$(HANDLER_PATH)/service.py \
		$(HANDLER_PATH)/repository.py \
		$(HANDLER_PATH)/constant.py \
		$(HANDLER_PATH)/template.html \
		shared/base.html \
		shared/db_config.py \
		shared/auth_model.py


# 3. Lambda 배포
create: zip-handler
	aws lambda create-function \
		--function-name $(LAMBDA_NAME) \
		--runtime python3.11 \
		--role $(ROLE_ARN) \
		--handler $(HANDLER_HANDLER) \
		--zip-file fileb://$(HANDLER_ZIP) \
		--timeout 10 \
		--memory-size 128 \
		--region $(REGION) \
		--layers arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(LAYER_NAME):1

update: zip-handler
	aws lambda update-function-code \
		--function-name $(LAMBDA_NAME) \
		--zip-file fileb://$(HANDLER_ZIP) \
		--region $(REGION)

deploy:
	@echo "Attempting to update existing Lambda..."
	@make update || (echo "Function not found. Creating instead..." && make create)

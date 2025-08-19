include ../../../../../.env

LAMBDA_NAME=olass-export-prod-user-profile-daily
ROLE_ARN=arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(AWS_LAMBDA_ROLE_NAME)

SHARED_LAYER_NAME=olass-shared-layer
BASE_LAYER_NAME=olass-base-layer

HANDLER_ZIP=function.zip

LAYER_SHARED_VERSION := $(shell aws lambda list-layer-versions \
	--layer-name $(SHARED_LAYER_NAME) \
	--region $(REGION) \
	--query 'LayerVersions[0].Version' \
	--output text)

LAYER_BASE_VERSION := $(shell aws lambda list-layer-versions \
	--layer-name $(BASE_LAYER_NAME) \
	--region $(REGION) \
	--query 'LayerVersions[0].Version' \
	--output text)

.PHONY: zip create update deploy

zip:
	cd ../../ && rm -f $(HANDLER_ZIP)
	cd ../../ && zip -r $(HANDLER_ZIP) . -x "deploy/*"
	mv ../../$(HANDLER_ZIP) .

create: zip
	aws lambda create-function \
		--function-name $(LAMBDA_NAME) \
		--runtime $(PYTHON) \
		--role $(ROLE_ARN) \
		--handler handler.lambda_handler \
		--zip-file fileb://$(HANDLER_ZIP) \
		--timeout 100 \
		--memory-size 128 \
		--region $(REGION) \
		--architectures arm64 \
		--environment Variables='{ENVIRONMENT=prod}' \
		--layers \
			arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(BASE_LAYER_NAME):$(LAYER_BASE_VERSION) \
			arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(SHARED_LAYER_NAME):$(LAYER_SHARED_VERSION)

update: zip
	aws lambda update-function-configuration \
		--function-name $(LAMBDA_NAME) \
		--environment Variables='{ENVIRONMENT=prod}' \
		--layers \
			arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(BASE_LAYER_NAME):$(LAYER_BASE_VERSION) \
			arn:aws:lambda:$(REGION):$(AWS_ACCOUNT_ID):layer:$(SHARED_LAYER_NAME):$(LAYER_SHARED_VERSION) \
		--region $(REGION)

	sleep 10

	aws lambda update-function-code \
		--function-name $(LAMBDA_NAME) \
		--zip-file fileb://$(HANDLER_ZIP) \
		--region $(REGION)

deploy:
	@make update || make create

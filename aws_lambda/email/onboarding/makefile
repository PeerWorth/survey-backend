PYTHON=python3.11
LAMBDA_NAME=olass-onboarding-email
ZIP_FILE=function.zip
REQ=requirements.txt
ROLE_ARN=arn:aws:iam::590184068466:role/LambdaExecutionRole
REGION=ap-northeast-2
HANDLER=handler.lambda_handler

.PHONY: clean build zip create update deploy

clean:
	rm -rf python __pycache__ $(ZIP_FILE)

build:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(REQ) -t python/

zip: clean build
	cd python && zip -r ../$(ZIP_FILE) . && cd ..

	cp ../shared/base.html .
	zip -g $(ZIP_FILE) handler.py service.py template.html base.html
	rm base.html

create: zip
	aws lambda create-function \
		--function-name $(LAMBDA_NAME) \
		--runtime python3.11 \
		--role $(ROLE_ARN) \
		--handler $(HANDLER) \
		--zip-file fileb://$(ZIP_FILE) \
		--timeout 10 \
		--memory-size 128 \
		--region $(REGION)

update: zip
	aws lambda update-function-code \
		--function-name $(LAMBDA_NAME) \
		--zip-file fileb://$(ZIP_FILE) \
		--region $(REGION)

deploy:
	@echo "Attempting to update existing Lambda..."
	@make update || (echo "Function not found. Creating instead..." && make create)

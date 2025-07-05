include ../../.env

LAYER_NAME=olass-base-layer

.PHONY: build zip deploy clean

build:
	docker build -t lambda-base-builder .

zip: build
	docker create --name temp lambda-base-builder
	docker cp temp:/var/task/layer.zip layer.zip
	docker rm temp

deploy: zip
	aws lambda publish-layer-version \
	  --layer-name $(LAYER_NAME) \
	  --zip-file fileb://layer.zip \
	  --compatible-runtimes python3.11 \
	  --region $(REGION)

clean:
	rm -rf python layer.zip

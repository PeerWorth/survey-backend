include ../.env
LAYER_NAME=olass-shared-layer

build:
	rm -rf python
	mkdir -p python/shared
	cp *.py python/shared/
	cp __init__.py python/shared/

zip:
	rm -f layer.zip
	(cd . && zip -r layer.zip python)


deploy: build zip
	aws lambda publish-layer-version \
	  --layer-name $(LAYER_NAME) \
	  --zip-file fileb://layer.zip \
	  --compatible-runtimes python3.11 \
	  --region $(REGION)

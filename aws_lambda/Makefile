.PHONY: all deploy-onboarding deploy-onboarding-layer

include .env

deploy-onboarding:
	$(MAKE) -C handlers/email/onboarding deploy

deploy-onboarding-layer:
	$(MAKE) -C handlers/email/onboarding deploy-layer

clean-onboarding:
	$(MAKE) -C handlers/email/onboarding clean

all: deploy-onboarding-layer deploy-onboarding

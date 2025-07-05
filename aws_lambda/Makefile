.PHONY: deploy-shared deploy-dependencies-base deploy-handlers-email-onboarding deploy-all

deploy-shared:
	$(MAKE) -C shared deploy

deploy-dependencies-base:
	$(MAKE) -C dependencies/base deploy

deploy-handlers-email-onboarding:
	$(MAKE) -C handlers/email/onboarding deploy

deploy-all: deploy-shared deploy-dependencies-base deploy-handlers-email-onboarding

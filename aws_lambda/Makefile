.PHONY: deploy-shared deploy-dependencies-base deploy-handlers-email-onboarding deploy-all

deploy-shared:
	$(MAKE) -C shared deploy

deploy-dependencies-base:
	$(MAKE) -C dependencies/base deploy

deploy-handlers-email-trigger:
	$(MAKE) -C handlers/email/trigger deploy

deploy-handlers-email-onboarding:
	$(MAKE) -C handlers/email/onboarding deploy

deploy-handlers-bigquery-export-user-profile-daily:
	$(MAKE) -C handlers/bigquery/export_user_profile_daily deploy


deploy-all: deploy-shared deploy-dependencies-base deploy-handlers-email-onboarding deploy-handlers-email-trigger deploy-handlers-bigquery-export-user-profile-daily

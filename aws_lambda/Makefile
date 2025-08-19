.PHONY: deploy-shared deploy-dependencies-base deploy-handlers-email-onboarding deploy-all

deploy-shared:
	$(MAKE) -C shared deploy

deploy-dependencies-base:
	$(MAKE) -C dependencies/base deploy

deploy-handlers-email-trigger:
	$(MAKE) -C handlers/email/trigger deploy

deploy-handlers-email-onboarding:
	$(MAKE) -C handlers/email/onboarding deploy

deploy-handlers-bigquery-export-dev-user-profile-daily:
	$(MAKE) -C handlers/bigquery/export_user_profile_daily/deploy/dev deploy

deploy-handlers-bigquery-export-prod-user-profile-daily:
	$(MAKE) -C handlers/bigquery/export_user_profile_daily/deploy/prod deploy


deploy-all: deploy-shared deploy-dependencies-base deploy-handlers-email-onboarding deploy-handlers-email-trigger deploy-handlers-bigquery-export-dev-user-profile-daily deploy-handlers-bigquery-export-prod-user-profile-daily

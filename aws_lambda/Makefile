.PHONY: deploy-shared deploy-dependencies-base deploy-dev-all deploy-prod-all deploy-all

export AWS_PAGER=

# 공통 의존성
deploy-shared:
	$(MAKE) -C shared deploy

deploy-dependencies-base:
	$(MAKE) -C dependencies/base deploy

# Dev 환경 Lambda 함수들
deploy-handlers-bigquery-export-dev-user-profile-daily:
	$(MAKE) -C handlers/bigquery/export_user_profile_daily/deploy/dev deploy

deploy-handlers-bigquery-export-dev-user-journey-daily:
	$(MAKE) -C handlers/bigquery/export_user_journey_daily/deploy/dev deploy

# Prod 환경 Lambda 함수들
deploy-handlers-bigquery-export-prod-user-profile-daily:
	$(MAKE) -C handlers/bigquery/export_user_profile_daily/deploy/prod deploy

deploy-handlers-bigquery-export-prod-user-journey-daily:
	$(MAKE) -C handlers/bigquery/export_user_journey_daily/deploy/prod deploy

# 개발 중인 기능들 (주석 처리)
# deploy-handlers-email-trigger:
#	$(MAKE) -C handlers/email/trigger deploy
# deploy-handlers-email-onboarding:
#	$(MAKE) -C handlers/email/onboarding deploy

deploy-dev-all: deploy-shared deploy-dependencies-base deploy-handlers-bigquery-export-dev-user-profile-daily deploy-handlers-bigquery-export-dev-user-journey-daily
deploy-prod-all: deploy-shared deploy-dependencies-base deploy-handlers-bigquery-export-prod-user-profile-daily deploy-handlers-bigquery-export-prod-user-journey-daily
deploy-all: deploy-dev-all deploy-prod-all

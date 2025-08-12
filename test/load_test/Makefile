# 기본 설정
HOST ?= http://olass-dev-env.eba-ngrf8aht.ap-northeast-2.elasticbeanstalk.com # Example [terraform apply-dev 후 load test 용 호스트 붙여넣기]
USERS ?= 500
SPAWN_RATE ?= 1
RUN_TIME ?= 6m

.PHONY: ui test clean

ui-test:
	locust -f locustfile.py --host $(HOST)

test:
	locust -f locustfile.py \
		--host $(HOST) \
		--users $(USERS) \
		--spawn-rate $(SPAWN_RATE) \
		--run-time $(RUN_TIME) \
		--headless \
		--html report.html

clean:
	rm -f report.html

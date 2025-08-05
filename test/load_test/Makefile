# 기본 설정
HOST ?= http://olass-dev-env.eba-hxef44pn.ap-northeast-2.elasticbeanstalk.com # terraform apply-dev 후 load test 용 호스트 붙여넣기
USERS ?= 2
SPAWN_RATE ?= 2
RUN_TIME ?= 10m

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

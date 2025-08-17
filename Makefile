.PHONY: restart-server, stop-server, start-server, clean, restart-server-clean

restart-server:
	docker-compose -f docker-compose.dev.single.yml down
	docker-compose -f docker-compose.dev.single.yml rm -f
	docker-compose -f docker-compose.dev.single.yml up -d --build --force-recreate

stop-server:
	docker-compose -f docker-compose.dev.single.yml down

start-server:
	docker-compose -f docker-compose.dev.single.yml up -d --build

restart-server-clean:
	docker-compose -f docker-compose.dev.single.yml down -v
	docker-compose -f docker-compose.dev.single.yml rm -f
	docker-compose -f docker-compose.dev.single.yml up -d --build --force-recreate

clean:
	docker-compose -f docker-compose.dev.single.yml down -v --rmi all --remove-orphans

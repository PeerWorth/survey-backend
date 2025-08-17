.PHONY: restart-server, stop-server, start-server, clean

restart-server:
	docker-compose -f docker-compose.dev.single.yml down -v
	docker-compose -f docker-compose.dev.single.yml rm -f
	docker-compose -f docker-compose.dev.single.yml up -d --build --force-recreate

stop-server:
	docker-compose -f docker-compose.dev.single.yml down -v


start-server:
	docker-compose -f docker-compose.dev.single.yml up -d --build


clean:
	docker-compose -f docker-compose.dev.single.yml down -v --rmi all --remove-orphans

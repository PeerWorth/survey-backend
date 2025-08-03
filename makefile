restart-server:
	docker-compose -f docker-compose.dev.single.yml down
	docker-compose -f docker-compose.dev.single.yml up -d --build

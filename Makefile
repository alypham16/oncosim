PORT ?= 8050
NAME ?= "alypham16/oncosim:0.1.0"

filter:
	docker ps --filter "expose=${PORT}"  --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"

build:
	docker build -t ${NAME} .

run: build
	docker run -d -p 8050:8050 ${NAME}

stop:
	docker stop $(shell docker ps -q)

all: stop build run

compose-up:
	docker compose up --build -d 

compose-down:
	docker compose down
	
compose: compose-down compose-up

compose-up-staging:
	docker compose -f docker-compose-staging.yml up --build -d

compose-down-staging:
	docker compose -f docker-compose-staging.yml down

compose-staging: compose-down-staging compose-up-staging
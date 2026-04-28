PORT ?= 8050
NAME ?= alypham16/oncosim:0.1.0

build:
	docker build -t ${NAME} .

run: build
	docker run -d -p ${PORT}:8050 ${NAME}

stop:
	docker stop $(shell docker ps -q)

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

compose-restart:
	docker compose down
	docker compose up --build -d
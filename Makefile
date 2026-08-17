build:
	docker build -t flight-api "./phase 2"
	docker build -t flight-frontend "./phase 3"

run:
	docker network create flight-network
	docker run -d --name flight-api-container --network flight-network -p 8000:8000 -e WANDB_API_KEY="$(WANDB_API_KEY)" -e DB_PASSWORD="$(DB_PASSWORD)" flight-api
	docker run -d --name flight-frontend-container --network flight-network -p 8501:8501 -p 8502:8502 -e API_URL="http://flight-api-container:8000" -e DB_PASSWORD="$(DB_PASSWORD)" flight-frontend

clean:
	docker rm -f flight-api-container
	docker rm -f flight-frontend-container
	docker network rm flight-network
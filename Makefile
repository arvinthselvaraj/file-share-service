# Project variables
APP_NAME=file-share-service
BUCKET_NAME=file-share-bucket
TABLE_NAME=FileMetadata
LOCALSTACK_URL=http://localhost:4566
REGION=us-east-1

.PHONY: up down logs init test lint

# Build and start app + LocalStack
up:
	docker-compose up --build -d

# Stop and clean containers
down:
	docker-compose down

# Follow logs (app + localstack)
logs:
	docker-compose logs -f

# Initialize resources in LocalStack (S3 bucket + DynamoDB table)
init:
	aws --endpoint-url=$(LOCALSTACK_URL) s3 mb s3://$(BUCKET_NAME) || true
	aws --endpoint-url=$(LOCALSTACK_URL) dynamodb create-table \
	  --table-name $(TABLE_NAME) \
	  --attribute-definitions AttributeName=fileId,AttributeType=S \
	  --key-schema AttributeName=fileId,KeyType=HASH \
	  --billing-mode PAY_PER_REQUEST \
	  --region $(REGION) || true

# Run unit tests with pytest
test:
	pytest -q

# Run linter (flake8 or black)
lint:
	black .

# File Share Service (FastAPI + S3 + DynamoDB + LocalStack)

A lightweight file-sharing API built with FastAPI.
S3 (LocalStack) -> stores files
DynamoDB (LocalStack) -> stores metadata
FastAPI -> provides REST endpoints for upload, download, and listing

The repo contains source code for running and testing the app locally.
At the end of this document are Assumptions, design decisions, enterprise-grade scale and future extensions.

## Features
- `POST /files` -> Upload a file (max 20MB)
- `GET /files/{id}` -> Download file by ID
- `GET /files` -> List all uploaded files (metadata only)
- File metadata includes: id, filename, size, contentType, uploadedAt, sha256
- Runs locally with `LocalStack` (no AWS account needed)
- `Makefile` for ease of testing and running locally

## High-level Design (Current, basic version)
![basic_design.png](docs/images/basic_design.png)

## Run locally quickly
1. Pre-requisite
- Install python 3.11 or above.
Verify after install:
```bash
    python --version
```
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
Verify after install:
```bash
    docker --version
    docker compose version
```

2. Clone repository
```bash
    git clone https://github.com/arvinthselvaraj/file-share-service.git
    cd file-share-service
```

3. Install dependencies:
MacOS/Linux
```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

4. Start application and initialize AWS resources in LocalStack
```bash
make up

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

make init
```
This will:
- Start app + LocalStack
- Create S3 bucket -> file-share-bucket
- Create DynamoDB table -> FileMetadata (partition key = fileId)

NOTE: Use aws credentials while connecting to real AWS account.

5. Test API
Interactive API Docs (default FastAPI swagger UI params):
- Swagger UI is available at: http://localhost:8000/docs

Screenshots of Swagger UI with all endpoints:
- [All endpoints](docs/images/swagger_ui_all_endpoints.png)
- [Upload file](docs/images/swagger_ui_upload_file_success.png)
- [Upload file too large](docs/images/swagger_ui_upload_file_too_large.png)
- [List all files](docs/images/swagger_ui_list_all_files.png)
- [Download file](docs/images/swagger_ui_download_file_by_id.png)

6. Running Tests
```bash
make test
```

View test coverage:

```bash
pytest --cov=app --cov-report=term-missing tests/
```

## Project Structure
```bash
app/
 ├── main.py            # FastAPI entrypoint
 ├── config.py          # App configuration
 ├── dependencies.py    # AWS clients (S3, DynamoDB)
 ├── routes/            # API routes
 ├── services/          # File business logic
 ├── models/            # Pydantic models
 └── utils/             # Helpers (hashing)
tests/                  # Unit tests
docker-compose.yml      # App + LocalStack
Dockerfile              # Build and run container
Makefile                # Helper commands
```


## Useful Make Commands
```bash
make up     # start app + localstack
make init   # create S3 bucket + DynamoDB table
make logs   # view logs
make test   # run tests
make down   # stop everything
```

## API Design

#### POST /files
- Request: multipart/form-data with field file.
- Response (201): ```{ "id": "<uuid>", "filename": "orig.pdf", "size": 12345 }```
- Errors: 
  - 413 File Too Large -> when upload exceeds 20MB.
  - 400 Bad Request -> missing filename.
  - 500 Internal Server Error -> unexpected.

#### GET /files/{id}
- Request: file_id
- Response (200): Returns file bytes (Content-Disposition: attachment; filename="orig.pdf")
- Errors:
  - 404 File not found
  - 500 Internal Server Error -> unexpected.

#### GET /files
- Request: None
- Response (200): Returns list of metadata (no file content): 
```[{ "fileId": "<uuid>", "filename": "orig.pdf", "uploadedAt": "2025-09-25T12:34:56Z" }, "sizeBytes": 123]```
- Errors:
  - 404 File not found
  - 500 Internal Server Error -> unexpected.


# Assumptions & Design Decisions
- No authentication required (per exercise requirements).
- Max file size: 20MB (per exercise requirements).
  - zero size file allowed.
- File names sanitized to prevent unsafe characters.
- Metadata stored in DynamoDB (or local JSON).
- Storage in S3 or local disk depending on environment.
- API errors:
  - `413 Payload Too Large` → File exceeds 20MB
  - `404 Not Found` → File ID does not exist
  - `500 Internal Server Error` → Unexpected server error
- LocalStack usage for rapid local testing without AWS dependency.

# Scaling to Production and Future Extensions
Design evolves for enterprise-grade scale (e.g., millions of files, compliance):
## Upload Flow
- Replace API proxy upload with S3 pre-signed URLs -> clients upload directly to S3, avoiding app bottlenecks.
- Trigger S3 events -> Lambda for virus scanning, metadata extraction, and audit logging.
## Storage & Metadata
- S3 -> production bucket with versioning, encryption (KMS), lifecycle policies (cold storage like S3 Glacier for long-term storage, deletion).
- DynamoDB -> on-demand mode with Global Secondary Indexes (GSI) to support user-level queries.
- Global Tables -> multi-region replication for Disaster Recovery (DR).
## Security & Compliance
- Authentication/Authorization -> AWS Cognito or enterprise OIDC (JWT-based).
- Encryption -> TLS in transit, KMS-managed keys at rest.
- Access Control -> IAM roles, fine-grained bucket policies, per-user RBAC.
- Audit Logging -> CloudTrail + immutable logs 
- Compliance -> Immutable data, retention policies (S3 object-lock, dynamodb TTL).
## Availability & Reliability
- API behind API Gateway + Lambda (serverless, auto-scaling).
- Use CloudFront CDN for file downloads (low latency, global distribution).
- Multi-AZ deployments with automated failover.
## Observability
- Metrics (CloudWatch / Datadog) -> request counts, error rates, upload latency.
- Request tracing (X-Ray).
- Alerts on error spikes, DynamoDB throttling, or S3 event failures.
## Cost Optimization
- S3 lifecycle -> move stale files to S3 Glacier Deep Archive.
- DynamoDB TTL -> automatically expire old metadata.
- Minimize egress with signed URLs and CloudFront caching.
## API enhancements
- Version API path with v1, v2 ... for ease of API evolution with low customer impact.
- Response pagination for list files endpoint.
- Validate for safe file types (Currently, any file type is allowed e.g., .exe, .sh)
## CI/CD
- Pipeline for app build and deployment
- Gated deployment: Automated tests (unit, integration, perf etc.), static code analysis & test coverage (sonar), governance checks etc.
- Tagged releases (in case of app rollback)
- Change management process

## Alternate Design
![alt_design.png](docs/images/alt_design.png)
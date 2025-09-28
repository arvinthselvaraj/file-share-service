import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET_NAME = os.getenv("BUCKET_NAME", "file-share-bucket")
TABLE_NAME = os.getenv("TABLE_NAME", "FileMetadata")
MAX_BYTES = 20 * 1024 * 1024  # 20 MB limit

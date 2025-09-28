import os, boto3
from app import config

endpoint_url = os.getenv("AWS_ENDPOINT_URL")

s3 = boto3.client("s3", region_name=config.AWS_REGION, endpoint_url=endpoint_url)
dynamodb = boto3.resource(
    "dynamodb", region_name=config.AWS_REGION, endpoint_url=endpoint_url
)
table = dynamodb.Table(config.TABLE_NAME)

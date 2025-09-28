import os
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3
from app.main import app
from app import config


@pytest.fixture(scope="function")
def aws_setup():
    # Set dummy credentials
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

    with mock_aws():
        # Mock S3 + DynamoDB
        s3 = boto3.client("s3", region_name=config.AWS_REGION)
        dynamodb = boto3.client("dynamodb", region_name=config.AWS_REGION)

        # Create test bucket
        s3.create_bucket(Bucket=config.BUCKET_NAME)

        # Create DynamoDB table
        dynamodb.create_table(
            TableName=config.TABLE_NAME,
            KeySchema=[{"AttributeName": "fileId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "fileId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        yield


@pytest.fixture()
def client(aws_setup):
    return TestClient(app)
